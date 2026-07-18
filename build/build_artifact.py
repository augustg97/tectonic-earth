"""Inline everything into one self-contained artifact HTML (body-only, as the
Artifact publish flow wraps it in <!doctype><head></head><body>)."""
import base64, json, os, re

WEB = "../web"
SRC = os.path.join(WEB, "index.html")
OUT = os.path.join(WEB, "artifact.html")

html = open(SRC, encoding="utf-8").read()

# 1) JSON data
jsons = {}
for name in ["timeline", "boundaries", "plates", "hotspots", "labels"]:
    jsons[name] = json.load(open(os.path.join(WEB, name + ".json")))

# 2) field textures (elevation + rainfall) as data URIs
fields = {}
tl = jsons["timeline"]
for fr in tl:
    for key in ("e", "r"):
        name = fr[key]
        p = os.path.join(WEB, "fields", name)
        # Prefer the lighter elevation encoding here: this build is inlined as
        # base64 (which inflates ~33%) and has to clear a 16 MB ceiling. The
        # self-hosted site serves the full-quality textures instead.
        lite = p.replace(".webp", "_lite.webp")
        if key == "e" and os.path.exists(lite):
            p = lite
        b = base64.b64encode(open(p, "rb").read()).decode()
        fields[name] = "data:image/webp;base64," + b

inline_js = ("window.INLINE_JSON=" + json.dumps(jsons, separators=(",", ":")) + ";\n"
             + "window.INLINE_FIELDS=" + json.dumps(fields, separators=(",", ":")) + ";\n")

# 3) three.js inline
three = open(os.path.join(WEB, "three.min.js"), encoding="utf-8").read()
assert "</script" not in three.lower(), "three.js contains </script>"

# ---- assemble body-only content ----
# strip document scaffolding
for tag in [r"<!DOCTYPE html>", r"<html[^>]*>", r"</html>", r"<head>", r"</head>",
            r"<body>", r"</body>", r'<meta[^>]*>']:
    html = re.sub(tag, "", html, flags=re.IGNORECASE)

# replace three.js external script with inline + inject INLINE data just before it
html = html.replace(
    '<script src="three.min.js"></script>',
    '<script>/*INLINE_DATA*/</script>\n<script>/*THREE*/</script>'
)
html = html.replace('<script>/*INLINE_DATA*/</script>', '<script>' + inline_js + '</script>')
html = html.replace('<script>/*THREE*/</script>', '<script>' + three + '</script>')

html = '<meta charset="utf-8">\n' + html.strip()
open(OUT, "w", encoding="utf-8").write(html)
mb = os.path.getsize(OUT) / 1e6
print(f"wrote {OUT}  {mb:.2f} MB")
print(f"field textures inlined: {len(fields)}")
