# Handoff — from the round-3 branch to the live site (M1 runbook)

For a Claude Code session running LOCALLY on the M1, in the repository, or for
the user at the terminal. Nothing here works from a remote session: the steps
need the GPU (sheets), the local field sets, a display (the review) and the
user's push to main. Read `README.md` §2 (the working rules) and §6 (build and
deploy) first, then `HANDOFF-WP10.md` for what the branch contains and why.

Two decisions are the user's and the session must STOP for them: the display
review verdicts (step 3) and the deploy choice (step 5). Do not push to main
until the user says so.

Python: the repo's venv (`source venv/bin/activate` at the repo root, or
`../venv/bin/python3` from `build/`). The system python has no numpy, PIL or
scipy and every script below needs them.

## 0. The branch

```bash
cd "/Users/augustgweon/Tectonic Plate Model"      # never under ~/Desktop (macOS TCC blocks builds there)
git status                                         # clean; commit or stash anything left from round 2
git fetch origin
git checkout claude/tectonic-earth-wp10-handoff-uie4hu
git log --oneline main..HEAD | wc -l               # 40 or so
source venv/bin/activate
```

## 1. Bake the field round 3 changed (~5 min)

```bash
cd build
python3 build_arc.py                               # the belt-type alpha into all 251 _t files
python3 build_arc.py --stats 0
python3 -c "from PIL import Image; print(Image.open('../web/fields/phan_0000_t.webp').mode)"
ls ../web/fields/*_q.webp | wc -l; ls ../web/fields/*_x.webp | wc -l
```

Checks: the stats show the Andes W Cordillera at 0.55 (65% above 0.5), the
Eastern Cordillera 0.00, the Himalaya and Tibet 0.00; the mode prints `RGBA`;
both counts are 251. If `_q` or `_x` are short, `python3 build_foldphase.py -j`
(~2 min) and `python3 build_drainphase.py -j` (~5 min).

## 2. Validate the shader

```bash
python3 check_shader.py                            # must end "shader source clean"
```

It also prints the texture units each shader reads; the FRAG line must say
`16 texture units read` (the hardware limit -- README 7.17 is the sampler
stack that made the round-3 shader fit on the M1).

## 3. The display review (the user looks; the session drives)

```bash
python3 serve.py 8899                              # leave running; "address in use" means one is already up -- use it
```

Open `http://127.0.0.1:8899/index.html?lite=0` in Chrome (`lite=0` forces the
live shader at every zoom). Frame from the console with
`APP.lookAt(lon, lat, {age, zoom})` and confirm the returned `ok` is true. A
knob is a URL parameter: reload with it, then the same `lookAt`. Zoom clamps
at 1.35.

| view | lookAt | beside |
|---|---|---|
| Zagros | `APP.lookAt(51, 32, {age:0, zoom:1.35})` | `?noatlas=1`, `?atlasN=1.6`, `?atlasN=2.4` |
| Himalaya | `APP.lookAt(86.9, 28.2, {age:0, zoom:1.35})` | the same three |
| Andes | `APP.lookAt(-68, -18, {age:0, zoom:1.35})` | `?arc=0` |
| Pangaea | `APP.lookAt(-5, 8, {age:300, zoom:1.6})` | `?noatlas=1` |
| Tibet | `APP.lookAt(88, 33, {age:0, zoom:1.6})` | `?basin=0`, then `?plat=1` |
| Great Plains / Deccan | `APP.lookAt(-98, 42, {age:0, zoom:1.35})` / `APP.lookAt(78, 18, {age:0, zoom:1.35})` | `?plainsK=2` beside `?nodrain=1` |
| Grand Erg Oriental | `APP.lookAt(8, 31, {age:0, zoom:1.35})` | `?erg=0`, `?erg=2` |
| sand-sea mask | `APP.lookAt(50, 22, {age:0, zoom:2.5})` | `?show=1` (white = sand sea; Arabia is black, a known open item) |

While looking: at age 0 the tectonic field bound is the -5 Ma keyframe's
(README 7.16), which carries the belt type after step 1. A verdict is a
multiplier; to bake it in, edit the constant in
`web/shaders/index__FRAG.frag.glsl`, run `check_shader.py`, reload:

    atlas normal   ampA=ga*8.0          atlas tone   ar.x*0.55        atlas height  ar.x*520.0
    plains normal  gd*1.6               plains tone  dr.x*0.16
    erg corridor   (vc-0.5)*3.0         erg crest    (crest-0.5)*0.5  erg normal    ampE=gErg*2.2
    basin trough   0.25+0.75*smoothstep in basinEnv()                 arc           1.0-0.9*gArc in atlasGate()

Done 2026-09-03: the ridges were judged ribbed fabric in every belt and ship
OFF (`uFoldK`, `?fold=1` to see them); plains and erg were baked at twice the
first cut. The verdicts are in `HANDOFF-WP10.md` ("The display review").

Every shader edit must be finished before step 4: an edit after the sheets
are baked means baking them again.

## 4. Sheets (~1 min GPU + 10-20 min encode)

`web/sheets/manifest.json` carries ONE width and both pages read it, so ship
the 2048 set (the ambient build's budget); a 4096 run would replace it.

```bash
pip show pillow-avif-plugin >/dev/null || pip install pillow-avif-plugin
python3 bake_sheets.py --width 2048
python3 -c "import json; m=json.load(open('../web/sheets/manifest.json')); print(m['w'], len(m['files']))"   # 2048 251
```

Then bump `SHEET_V` in `web/app.js` and `web/ambient.html` to today's date,
and check `http://127.0.0.1:8899/ambient.html?age=150` draws with
`AMB.status()` reporting nothing pending or missing.

## 5. Build and deploy (the user chooses which)

`build_site.py` runs the validators first (`audit_all.py --quick`) and refuses
if a baseline moved backwards; if one legitimately changed, tighten it in
`audit_all.py` in the same commit and say why. `SKIP_AUDIT=1` should not be
needed.

Lean (manifests only in `docs/`, textures on a GitHub release; needs `gh`
installed and logged in -- `brew install gh && gh auth login`):

```bash
python3 publish_assets.py --release fields-20260903
python3 build_site.py \
  --field-base https://github.com/augustg97/tectonic-earth/releases/download/fields-20260903 \
  --sheet-base https://github.com/augustg97/tectonic-earth/releases/download/fields-20260903
cd ..
git add -A docs web/app.js web/ambient.html
git commit -m "Deploy WP-10 rounds 1-3 (assets on release fields-20260903)"
git checkout main && git merge --ff-only claude/tectonic-earth-wp10-handoff-uie4hu && git push
```

Self-contained (about 160 MB more in `docs/` and history):

```bash
python3 build_site.py
cd ..
git add -A docs web/app.js web/ambient.html
git commit -m "Deploy WP-10 rounds 1-3"
git checkout main && git merge --ff-only claude/tectonic-earth-wp10-handoff-uie4hu && git push
```

If the fast-forward is refused, main has moved: `git merge` without
`--ff-only` and resolve.

## 6. Verify the live site

```bash
sleep 120
curl -s https://augustg97.github.io/tectonic-earth/ | grep -o "DATA_V='[0-9-]*'"
grep -o "DATA_V='[0-9-]*'" web/app.js
```

The two stamps must match (if the live one is stale, wait for Pages and
re-check; do not redeploy). Open the live site, hard-reload, frame the Zagros
and the Andes; for the lean deploy open the console once -- a CORS error on the
first field fetch means the release did not answer with the allow-origin
header, and the self-contained deploy is the fallback. Open the live
`ambient.html?age=150`.

## Errors that are expected, and their fixes

- `ModuleNotFoundError: No module named 'numpy'` (or PIL, scipy): the venv is
  not active. `source venv/bin/activate`, or `../venv/bin/python3 script.py`.
- `error: pathspec '...' did not match any file(s) known to git`: `git fetch
  origin` first, then checkout.
- `Your local changes to the following files would be overwritten by
  checkout`: `git stash` (or commit) and retry.
- `OSError: [Errno 48] Address already in use` from `serve.py`: a server from
  round 2 is still up on 8899; use it as is.
- `bake_sheets: pip install pillow-avif-plugin`: do exactly that, inside the
  venv.
- `gh: command not found` or not logged in: install and `gh auth login`, or
  take the self-contained deploy.
- `build_site: <audit> failed`: read which check moved and why before anything
  else; a moved baseline is a finding, not an obstacle.
- `FRAGMENT shader texture image units count exceeds MAX_TEXTURE_IMAGE_UNITS(16)`
  in the console and a black globe: the shader reads more samplers than the
  GPU has units (software GL allows 32, the M1 16). `check_shader.py` now
  refuses this; README 7.17.
- A tab Chrome considers hidden (behind another window) gets no animation
  frames: the age does not advance, decodes stall and a capture returns the
  previous frame. Bring the window to the front, or drive frames by hand with
  `APP.step()` and capture with `APP.shoot(name, px)` (the harness path,
  `verify_server.py` on 8901).
- `Operation not permitted` on reads under the repository: the repo has been
  moved under `~/Desktop` or `~/Documents`; move it back out.
