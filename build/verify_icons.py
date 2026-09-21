"""Contact sheets of the drawings, for the one check no script can make: cover the
caption and name the group.

    python3 verify_icons.py forms           every FORM's drawing (one tile per form in use)
    python3 verify_icons.py own [k] [n]     per-taxon silhouettes, page k of n
    -> build/verify/icons_<what>.png
"""
import html, json, os, shutil, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biota
from biota_forms import FORMS, chain
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VERIFY = os.path.join(HERE, "verify")
CSS = ("body{background:#0d131a;color:#cfd9e6;font:10px -apple-system,Helvetica,sans-serif;margin:8px}"
       ".g{display:flex;flex-wrap:wrap;gap:6px}.c{width:104px}"
       ".i{--ko:#161d25;width:100px;height:64px;border-radius:6px;background:rgba(150,190,120,.13);"
       "border:1px solid #2a3644;color:#c2debb;display:flex;align-items:center;justify-content:center}"
       ".i svg{width:92px;height:58px;fill:currentColor;stroke-linecap:round;stroke-linejoin:round}"
       ".n{font-size:9.5px;line-height:1.2;margin-top:2px;color:#eed6a6}.h{font-size:8.5px;color:#8fa0b3}"
       ".parent .i{border-color:#e0764a}")


def shoot(page, out, w, h):
    tmp = tempfile.mkdtemp(prefix="teicons")
    t_html, t_png = os.path.join(tmp, "c.html"), os.path.join(tmp, "c.png")
    open(t_html, "w").write(page)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                             f"--user-data-dir={tmp}/prof", "--no-first-run",
                             f"--window-size={w},{h}", f"--screenshot={t_png}", "file://" + t_html],
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
    print(out if os.path.exists(out) else "NO SCREENSHOT")


def main(argv):
    what = argv[0] if argv else "forms"
    os.makedirs(VERIFY, exist_ok=True)
    icons = json.load(open(os.path.join(HERE, "life_icons.json")))
    reg = biota.load()["taxa"]
    tiles = []
    if what == "forms":
        used = {}
        for e in reg.values():
            used.setdefault(e["form"], []).append(e["n"])
        for form in sorted(used, key=lambda k: (FORMS[k]["kind"], list(FORMS).index(k))):
            key, how = None, "form"
            for i, f in enumerate(chain(form)):
                k = FORMS[f]["icon"] or f
                if k in icons:
                    key, how = k, ("form" if i == 0 else "parent")
                    break
            eg = ", ".join(used[form][:2])
            tiles.append((key, form, f"{how}:{key} · {len(used[form])} taxa · {eg}", how))
    else:
        k, n = (int(argv[1]), int(argv[2])) if len(argv) > 2 else (1, 1)
        own = []
        for name in sorted(reg):
            ic, how = biota.icon_for(name, icons)
            if how in ("own", "rep"):
                own.append((ic, name, f"{how} · form {reg[name]['form']}", how))
        per = (len(own) + n - 1) // n
        tiles = own[(k - 1) * per: k * per]
        what = f"own{k}"
    cells = "".join(
        f"<div class='c {how}'><div class=i><svg viewBox='0 0 64 40'>{icons.get(key or '', '')}</svg></div>"
        f"<div class=n>{html.escape(name)}</div><div class=h>{html.escape(sub)}</div></div>"
        for key, name, sub, how in tiles)
    cols = 16
    rows = (len(tiles) + cols - 1) // cols
    page = f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=g>{cells}</div>"
    shoot(page, os.path.join(VERIFY, f"icons_{what}.png"), 16 + cols * 110, 20 + rows * 112)


if __name__ == "__main__":
    main(sys.argv[1:])
