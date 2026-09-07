"""The timeline preview atlas (the Atlas port, 2026-09-07).

    ../venv/bin/python build_timeline_preview.py           # rebuild web/imagery/timeline-preview.{webp,json}
    ../venv/bin/python build_timeline_preview.py --check   # is the shipped atlas built from THESE sheets?

While a seek's full-resolution fields are still arriving, the app draws the
requested age from a 4096x2048 atlas of 256x128 thumbnails of all 251 shipped
world sheets (web/sheets/), sixteen to a row in timeline order. The thumbnails
are the sheets' own RGB, Lanczos-reduced, no alpha compositing, no gamma or
ICC change; the metadata records the SHA-256 of every source sheet and of the
timeline and manifest it was built from, which is what --check compares.
build_site.py runs --check and refuses to publish a preview whose sources have
moved: a stale thumbnail shows one keyframe's world under another's age.

Adapted from Tectonic Atlas's scripts/build-timeline-preview.py (commit
cb57e9f) to this repository's paths. Needs Pillow with AVIF decoding
(pillow-avif-plugin, in the venv).
"""
import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
IMAGERY = os.path.join(WEB, "imagery")
SHEETS = os.path.join(WEB, "sheets")
COLS = ROWS = 16
CW, CH = 256, 128
W, H = COLS * CW, ROWS * CH


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(quiet=False):
    """0 when the shipped atlas matches the current timeline, manifest and
    sheets; 1 when it does not (or is absent); 2 when there are no shipped
    sheets to check against (nothing to say)."""
    meta_path = os.path.join(IMAGERY, "timeline-preview.json")
    webp_path = os.path.join(IMAGERY, "timeline-preview.webp")
    manifest = os.path.join(SHEETS, "manifest.json")
    if not os.path.exists(manifest):
        if not quiet:
            print("timeline preview: no shipped sheets here, nothing to check against (2)")
        return 2
    if not (os.path.exists(meta_path) and os.path.exists(webp_path)):
        print("timeline preview: MISSING -- run build_timeline_preview.py")
        return 1
    meta = json.load(open(meta_path))
    problems = []
    if meta.get("sha256") != sha(webp_path):
        problems.append("the atlas bytes do not match its metadata")
    if meta.get("timelineSHA256") != sha(os.path.join(WEB, "timeline.json")):
        problems.append("the timeline has changed")
    if meta.get("sourceManifestSHA256") != sha(manifest):
        problems.append("the sheet manifest has changed")
    frames = meta.get("frames") or []
    timeline = json.load(open(os.path.join(WEB, "timeline.json")))
    if len(frames) != len(timeline):
        problems.append(f"{len(frames)} cells for {len(timeline)} keyframes")
    moved = 0
    for fr in frames:
        p = os.path.join(SHEETS, fr["source"])
        if not os.path.exists(p) or sha(p) != fr["sourceSHA256"]:
            moved += 1
    if moved:
        problems.append(f"{moved} source sheet(s) changed since the atlas was built")
    if problems:
        print("timeline preview: STALE -- " + "; ".join(problems) + ". Run build_timeline_preview.py")
        return 1
    if not quiet:
        print(f"timeline preview: current ({len(frames)} cells, sheets, manifest and timeline unchanged)")
    return 0


def build():
    from PIL import Image
    try:
        import pillow_avif  # noqa: F401  -- registers the AVIF decoder
    except ImportError:
        pass
    timeline = json.load(open(os.path.join(WEB, "timeline.json")))
    sheets = json.load(open(os.path.join(SHEETS, "manifest.json")))
    ages = [f["age"] for f in timeline]
    assert len(ages) == 251 and ages == sorted(ages) and len(set(ages)) == 251, "the timeline is not the 251 ascending keyframes"
    assert COLS * ROWS >= len(ages)
    os.makedirs(IMAGERY, exist_ok=True)
    t0 = time.monotonic()

    def prepare(item):
        index, frame = item
        source = os.path.join(SHEETS, sheets["files"][str(frame["age"])])
        payload = open(source, "rb").read()
        with Image.open(source) as image:
            assert image.size == (sheets["w"], sheets["h"]), source
            # Discard the ocean-mask alpha without compositing or changing the RGB.
            rgb = image.convert("RGB").resize((CW, CH), Image.Resampling.LANCZOS)
        col, row = index % COLS, index // COLS
        entry = {"index": index, "ageMa": frame["age"], "column": col, "row": row,
                 "source": os.path.basename(source), "sourceSHA256": hashlib.sha256(payload).hexdigest(),
                 "pixelRect": [col * CW, row * CH, CW, CH],
                 "imageUVRect": [col / COLS, row / ROWS, 1 / COLS, 1 / ROWS],
                 "flippedUVRect": [col / COLS, 1 - (row + 1) / ROWS, 1 / COLS, 1 / ROWS],
                 "flippedUVCenters": [(col * CW + 0.5) / W, 1 - ((row + 1) * CH - 0.5) / H,
                                      ((col + 1) * CW - 0.5) / W, 1 - (row * CH + 0.5) / H]}
        return index, rgb, entry

    atlas = Image.new("RGB", (W, H), (5, 19, 40))
    entries = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for index, rgb, entry in pool.map(prepare, enumerate(timeline)):
            atlas.paste(rgb, (index % COLS * CW, index // COLS * CH))
            entries.append(entry)
            rgb.close()
    filename = "timeline-preview.webp"
    path = os.path.join(IMAGERY, filename)
    atlas.save(path, "WEBP", quality=88, method=6, exact=True)
    payload = open(path, "rb").read()
    with Image.open(path) as chk:
        assert chk.size == (W, H) and chk.mode == "RGB"
    meta = {"file": filename, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
            "width": W, "height": H, "columns": COLS, "rows": ROWS, "cellWidth": CW, "cellHeight": CH,
            "frameCount": len(entries), "gutterPixels": 0, "unusedCells": list(range(len(entries), COLS * ROWS)),
            "order": "Timeline array index; ascending age in Ma, from -250 to 1000. Columns left to right, then rows top to bottom.",
            "encoding": {"format": "WebP", "quality": 88, "method": 6, "mode": "RGB", "downsample": "Lanczos",
                         "colorHandling": "Source RGB retained without alpha compositing, gamma adjustment, or ICC conversion."},
            "texture": {"flipY": True, "mipmaps": False, "minFilter": "LinearFilter", "magFilter": "LinearFilter",
                        "halfTexel": [0.5 / W, 0.5 / H],
                        "sampling": "flippedUVRect assumes createImageBitmap(imageOrientation=flipY), texture.flipY=false. Clamp local sheet UV to its texel centers to avoid neighboring frames."},
            "timelineSHA256": sha(os.path.join(WEB, "timeline.json")),
            "sourceManifestSHA256": sha(os.path.join(SHEETS, "manifest.json")),
            "frames": entries}
    with open(os.path.join(IMAGERY, "timeline-preview.json"), "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
    print(json.dumps({"file": path, "bytes": len(payload), "sha256": meta["sha256"], "frames": len(entries),
                      "dimensions": [W, H], "elapsedSeconds": round(time.monotonic() - t0, 1)}))
    print("bump IMAGERY_V in web/app.js: the bytes changed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify the shipped atlas against the current sheets; exit 1 if stale")
    a = ap.parse_args()
    if a.check:
        return check()
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
