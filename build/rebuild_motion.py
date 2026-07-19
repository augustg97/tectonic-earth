"""Recompute motion and boundary textures from the elevation textures on disk.

The elevation fields are the expensive part of the pipeline (paleoDEM reads,
the wind solve, craton generation). Motion is derived purely from those fields,
so re-deriving it does not require regenerating anything — this reads the
exported elevation textures back and rewrites only `_m` (motion) and `_b`
(boundary class) per keyframe.
"""
import os, json
import numpy as np
from PIL import Image

import motion as MO
from fieldpack import dec_elev

OUT = "../web/fields"


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    man.sort(key=lambda m: m["age"])

    # decode every elevation texture down to the motion grid
    coarse = {}
    for rec in man:
        img = np.asarray(Image.open(os.path.join(OUT, rec["e"])).convert("RGB"))[..., 0] / 255.0
        coarse[rec["age"]] = MO.coarsen(dec_elev(img))
    ages = sorted(coarse)
    print(f"decoded {len(ages)} elevation fields")

    speeds = []
    total = 0
    lines = {}
    for rec in man:
        a = rec["age"]
        older = min(ages, key=lambda x: abs(x - (a + MO.BASE_MYR)))
        younger = min(ages, key=lambda x: abs(x - (a - MO.BASE_MYR)))
        dt = max(5.0, older - younger)
        vx, vy, cf = MO.displacement(coarse[older], coarse[younger], dt)
        vx, vy = MO.remove_net_rotation(vx, vy, cf)

        p = os.path.join(OUT, rec["m"])
        MO.encode(vx, vy, cf).save(p, "WEBP", quality=94, method=6)
        total += os.path.getsize(p)

        lines[str(rec["age"])] = MO.boundary_lines(vx, vy, cf)
        rec.pop("b", None)

        m = cf > 0.3
        if m.any():
            speeds.append(float(np.median(np.hypot(vx, vy)[m])))

    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), separators=(",", ":"))
    bpath = "../web/boundaries_time.json"
    json.dump(lines, open(bpath, "w"), separators=(",", ":"))
    nseg = sum(len(v) for f in lines.values() for v in f.values())
    print(f"boundary lines: {nseg} segments, {os.path.getsize(bpath)/1e6:.2f} MB")
    print(f"motion + boundaries: {len(man)} keyframes, {total/1e6:.2f} MB")
    print(f"median plate speed across the record: {np.median(speeds):.0f} mm/yr "
          f"(p10 {np.percentile(speeds,10):.0f}, p90 {np.percentile(speeds,90):.0f})")


if __name__ == "__main__":
    main()
