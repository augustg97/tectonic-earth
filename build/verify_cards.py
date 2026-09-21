"""Render real biota cards, side by side, to one PNG -- without booting the globe.

A card is not verified when life.json contains the right names. It is verified
when it has been drawn and looked at: the icon binding, the realm tint, the
Fauna/Flora sub-headings and the note all happen in the page, and a wrong
drawing is only ever visible as a drawing.

Booting the whole app under headless Chrome costs ten minutes of software
WebGL to reach a DOM panel, so this does the opposite: it lifts the app's OWN
card functions out of web/app.js by name, verbatim -- lifeSection, lifeHTML,
cardAt, groupTitle and the helpers they call -- and runs them against the real
life.json and labels.json with the real style.css. What is photographed is the
source text the app ships, not a re-implementation of it; if a function is
renamed or removed the extraction fails loudly rather than drifting.

    python3 verify_cards.py tag "Patagonian Desert@1" "North America@50" ...
    python3 verify_cards.py tag --file list.txt        (one Label@age per line)
    -> build/verify/cards_<tag>.png
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
VERIFY = os.path.join(HERE, "verify")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

FUNCS = ["esc", "lifeAt", "taxonNow", "sizeStr", "lifeHTML", "cardAt", "sparseAt",
         "groupTitle", "lifeSection", "lifeGroupsHTML", "fmtAge", "regionalAt"]


def lift(src, name):
    """The full source text of top-level `function name(...)`.

    app.js writes every top-level function either on ONE line or closed by a
    bare `}` in column 0, so the end is found by layout rather than by matching
    braces -- a brace matcher has to understand template literals and regex
    literals to get `esc()` right, and the first one written here did not.
    """
    lines = src.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("function %s(" % name):
            if ln.rstrip().endswith("}") and ln.count("{") == ln.count("}"):
                return ln
            for j in range(i + 1, len(lines)):
                if lines[j] == "}":
                    return "\n".join(lines[i: j + 1])
            break
    raise SystemExit(f"app.js no longer defines a top-level function {name}() -- "
                     f"update verify_cards.FUNCS")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    tag = argv[0]
    if argv[1] == "--file":
        cards = [l.strip() for l in open(argv[2]) if l.strip()]
    else:
        cards = argv[1:]
    os.makedirs(VERIFY, exist_ok=True)
    src = open(os.path.join(WEB, "app.js")).read()
    # Template literals contain braces and backticks; a naive matcher is thrown by
    # `${...}` inside a string, so strings are skipped but `${` is not special --
    # the functions lifted here keep their braces balanced inside templates.
    code = "\n".join(lift(src, f) for f in FUNCS)
    css = open(os.path.join(WEB, "style.css")).read()
    life = open(os.path.join(WEB, "life.json")).read()
    labels = open(os.path.join(WEB, "labels.json")).read()
    jobs = []
    for c in cards:
        i = c.rindex("@")
        jobs.append({"n": c[:i], "a": float(c[i + 1:])})
    cols = min(len(jobs), 6)
    page = f"""<!doctype html><meta charset=utf-8><style>{css}
html,body{{background:#0a0f15!important;overflow:visible!important;height:auto!important}}
#grid{{display:flex;flex-wrap:wrap;gap:12px;padding:12px;align-items:flex-start}}
.cell{{width:290px;background:rgba(18,26,36,.96);border:1px solid #26323f;border-radius:12px;
padding:14px;color:#dbe4ee;font-size:11px}}
.cell h3{{font-size:14px;margin:0 0 2px;font-weight:600;color:#fff}}
.cell .tg{{font-size:9px;letter-spacing:.14em;color:#e2b25a;text-transform:uppercase;margin-bottom:2px}}
</style><div id=grid></div><script>
const DATA={{life:{life},labels:{labels}}};
const state={{age:0}};
const MARINE_T=new Set(['ocean','sea']);
{code}
const jobs={json.dumps(jobs)};
const g=document.getElementById('grid');
for(const j of jobs){{
  const c=document.createElement('div');c.className='cell';
  const ls=DATA.labels.filter(x=>x.n===j.n);
  const l=ls.find(x=>j.a>=Math.min(x.a0,x.a1)-1&&j.a<=Math.max(x.a0,x.a1)+1)||ls[0];
  state.age=j.a;
  let h='';
  try{{h=l?lifeSection(l):'<i>no such label</i>';}}catch(e){{h='<b style="color:#e0764a">'+e+'</b>';}}
  c.innerHTML='<div class=tg>'+(l?l.t:'?')+' · '+fmtAge(j.a)+'</div><h3>'+j.n+'</h3>'+(h||'<i>(no biota section)</i>');
  g.appendChild(c);
}}
</script>"""
    html = os.path.join(VERIFY, f"cards_{tag}.html")
    with open(html, "w") as f:
        f.write(page)
    out = os.path.join(VERIFY, f"cards_{tag}.png")
    if os.path.exists(out):
        os.remove(out)
    rows = (len(jobs) + cols - 1) // cols
    w, h = 24 + cols * 302, 60 + rows * 1000
    # Two things learned the slow way. Chrome mangles a file:// URL with a space
    # in it, and this project's path has three, so the page and the PNG live in a
    # space-free temp dir and the PNG is copied back. And `--headless=new` does
    # not exit after --screenshot on this machine: wait for the file, then kill
    # the process by the PID this script launched -- never by a pattern.
    import shutil, tempfile, time
    tmp = tempfile.mkdtemp(prefix="tecards")
    t_html, t_png = os.path.join(tmp, "c.html"), os.path.join(tmp, "c.png")
    shutil.copy(html, t_html)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                             f"--user-data-dir={tmp}/prof", "--no-first-run",
                             f"--window-size={w},{h}", f"--screenshot={t_png}",
                             "file://" + t_html],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        if os.path.exists(t_png) and os.path.getsize(t_png) > 0:
            time.sleep(0.6)
            break
        time.sleep(0.5)
    proc.kill()
    if os.path.exists(t_png):
        shutil.copy(t_png, out)
    shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.exists(out):
        print("NO SCREENSHOT WRITTEN")
        return 1
    print(out, os.path.getsize(out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
