# Handoff — the Atlas port (2026-09-07)

Paste this whole file as the first message of a new session. It supersedes nothing: `HANDOFF-WP10.md`
and `HANDOFF-M1-DEPLOY.md` still describe the mountain roadmap and the M1 runbook; this file
describes what the port of 2026-09-07 changed and how it was measured.

---

## What you are working on

**Tectonic Earth** — the deep-time paleogeography app, 1000 Ma → +250 Myr, globe and map.

- Repo: `/Users/augustgweon/Tectonic Plate Model` (never under `~/Desktop` or `~/Documents`: macOS TCC)
- Live: https://augustg97.github.io/tectonic-earth/ (GitHub Pages serves `main:/docs`)
- **Read `README.md` first**: §2 the working rules, §5.7 the clouds, §5.8 the broker, §5.11 the port,
  §6 build and deploy, §7 the traps.

## What the port did

Three things came over from Tectonic Atlas (donor commit `cb57e9f`, the bundle at
`~/Downloads/claude-tectonic-earth-handoff`), selectively — its lighter renderer, its field subset
and its mesh caps did not, and the terrain shaders are byte-for-byte unchanged:

1. **Loading and timeline correctness.** `web/loader.js` is the request broker (dedupe, priorities,
   cancel-behind-a-seek, missing ≠ unavailable) and the pure time policy (`frameAt` binary search
   with an exact keyframe alone, the weather clock rules, the graph maths). `build/test_loader.mjs`
   (`node build/test_loader.mjs`, 10 tests) is its contract against the shipped timeline.
2. **Coherent seeks.** `bindTextures()` keeps an explicit account of what the picture shows against
   what the age asks for (`APP.surface()`), the time preview atlas draws the requested age at once,
   the readout says *Loading terrain* / *Refining detail*, the era rows seek.
3. **The clouds.** NASA's Blue Marble cloud field (`web/imagery/`, credited in the About panel, the
   README and `nasa-clouds.json`) in coherent motion over the paused globe and map, adapted to the
   era by the terrain's own elevation/rainfall pair; a paused-time layer with its own clock; the
   ground cache so the weather is not paid for by re-shading the planet.
4. **The temperature graph** under the conditions readout.

Every one is switchable for comparison: `?noclouds` (no image; the noise fallback), the *Cloud cover*
and *Animate weather* switches, `?nopreview`, `?groundcache=0`, `?lite=0`, and the frozen old page
`web/_old.html` (gitignored, with `_app_old.js`, `_shaders_old.js`, `_style_old.css`) which the
driver takes with `?app=_old.html`.

## The measurement harness, and what it measured

All of it is `build/verify_run.py JOBS.json` driving `web/_verify.html` headless on the M1's own GPU
(`--use-angle=metal`), one job at a time, waiting on each job's output files by name, with
`build/verify_diff.py` for frame comparisons. The job lists used are in the session scratchpad;
the modes are documented at the top of `_verify.html`. The old page ran through the same driver
with `?app=_old.html`, back to back with the new one, on a machine that was also running another
session's headless Chromes (so absolute frame times are an upper bound; the ratios hold).

| what | old page | new page |
|---|---|---|
| cold seek to full detail, 1000 → 0 / 300 / −250 / 700 Ma, warm localhost | 6.56 / 8.76 / 5.95 / 3.38 s, the previous world shown throughout | 0.56 / 0.24 / 0.24 / 0.24 s; the preview shows in 74 / 20 / 21 / 21 ms |
| the same with a 600 ms delay on every field fetch | 6.55 / 7.10 / 5.71 / 6.11 s | 0.83 / 0.90 / 0.94 / 0.93 s |
| fast-scrub release to render | 730 ms | 10 ms |
| keyframe-crossing storm gate (max synchronous uploads) | 2 | 2 (`audit_perf` unchanged) |
| playback coherence, 20 s at 18 Myr/s (uWarp/uMat live) | 100 % | 100 % |
| playback on the sheet path, 10 Myr/s, 600 ms sheet delay, 8 s | 0 holds, 0 path flips | 5 held frames of 2760, 0 flips |
| working set over 90 s of far jumps (four passes) | 949 MB cache, 460 pinned, 71 GL textures, flat | 949 / 461 / 65–70, flat, +139 MB imagery (preview 64, clouds 75) |
| frame p50 at 2560 × 1440, orbital, clouds on | 355 ms | 344 ms direct; **56 ms** paused with the ground cache |
| frame p50, orbital, clouds off | 343 ms | 328–346 ms (unchanged) |
| frame p50, Himalaya at zoom 1.35 / Andes tilted 55° | 352 / 316 ms | 350 / 307 ms direct; **29 / 30 ms** with the cache |
| cloud-off frames, old against new, orbital 0 / 300 / 720 / −250 Ma | — | 0.06 / 0.07 / 0.18 / 0.00 of 255 mean |
| cloud-off frames, map 0 / 300 / 720 Ma | — | 0.00 (bit-identical) |
| cloud-off close frames at 2.5 Ma (inside an interval): Himalaya / erg / plains | — | 0.00 / 0.03 / 0.00 |
| cloud-off close frames at exactly 0 Ma: Himalaya / Zagros / plains / erg / Hawaii / Mid-Atlantic | — | 12.8 / 8.2 / 10.5 / 12.9 / 1.2 / 2.2 — see below |
| cloud motion, fixed camera, two frames: present Globe 20 s / 300 Ma Map 15 s / +250 Myr Globe 15 s | — | 25.6 / 19.7 / 20.5 of 255 mean in the crop; the same fronts displaced (`build/verify/cmp_weather_ab.png`) |
| compile and link of all six materials on the M1 | 5 programs | 6 programs, all linked; 16 texture units, 16384 max texture |

**The one material difference is the exact-keyframe binding, and it is the requested one.** At an
age that is exactly a keyframe the old scan bound (the next younger keyframe, this one, t = 1), so
the present day was drawn with `fut_0005`'s plate slots, rotation table, fold fabric and foreland;
the new `frameAt` binds keyframe 50's own. The per-pixel procedural detail rides the material
coordinates, so its *instances* move while its statistics do not — the same class of change as the
noise-lattice swap of July 2026. Inside an interval (2.5 Ma) old and new are bit-identical, which is
what proves the rendering path untouched.

## Round 2 (the same evening): clouds through playback, continents that drift

The owner's two screenshots at 608 Ma asked for two things: a cloud layer that lives through
playback and evolves (masses forming, merging, dissolving, arranged by each era's likely climate),
and an end to the wide view's "unfinished frame" look and to continents that jump while time runs.

- **Clouds.** `cloudsVisible` no longer depends on `playing`. The shader gained a slow synoptic gate
  (two octaves of the lattice noise drifting through the weather clock, ~a minute from clear to
  overcast at a point, moved gently by the era), a soft zonal climatology (ITCZ, storm tracks,
  subtropical highs, as gains of 0.8–1.35) and a snowball damping (`uSnowball`, shared). Over 60 s
  at 300 Ma with a fixed camera the deck reorganises rather than translating
  (`build/verify/cmp_evolve_60s.png`; 19.4 of 255 mean in the crop).
- **The wide view** was the 2048 sheet set at 1.75× magnification on the stepped-down render
  scale. The app now ships a **4096 set** (`web/sheets/`, 238 MB, baked on the M1 from the frozen
  page `web/_bakeapp.html` in about 45 minutes), keeps the 2048 set in `web/sheets2048/` for the
  ambient page and constrained devices, holds six 4096 sheets, and engages the sheets from a
  quarter texel per pixel once the governor has stepped down. At 608 Ma, zoom 3.9, the sheet path
  and the live shader now differ by 2.2–3.0 of 255 (`cmp_wide608_sheets_vs_live.png`).
- **The jumps** were time advancing into a pair whose fields had not landed. `coreKinds` (elevation,
  rainfall, lakes, surface process, ocean structure of both keyframes; displacement and plate slots
  of the younger) now gates the switch from the preview, and **playback waits** for the next pair's
  core on both paths (capped at `HOLD_MS` = 3 s — 1.5 s let a loaded machine advance into a
  still; the preview gives up waiting after 6 s and binds
  progressively). The first cut waited on the terrain path only; at 10 Myr/s on the sheet path
  four frames in five were stills and the clouds flickered with them.
- **No frame moves time by more than 1.5 Myr** (`MAX_STEP_MYR`): the slider stays honest against the
  wall clock at the default speed (the half-second `dtT` cap already held 3 Myr/s to 1.5 Myr a
  frame), and fast playback on slow frames slows smoothly instead of leaping 3 Myr in one frame.
- **Shipped 4096 sheets upload in strips** (sixteen a sheet; two a frame while the picture has its sheets, up to eight by the frame's
  length while it waits for one — scaling by the frame's length alone fed on itself; the mip chain once at
  the end), since uploading one whole at its first draw cost the crossing frame ~70 ms; the sheet
  path warms every kind at one upload a frame — warming only the two it samples was tried and moved
  eight uploads into the crossing frame (355 ms), since the terrain material binds on every path.
- **The crossing hitch was the label raster.** `elevField` drew the keyframe's full 4096 × 2048
  bitmap into its 256 × 128 canvas on the spot — a 33 MB GPU-to-CPU read-back on the main thread,
  once per keyframe, 316–387 ms in the storm test with no uploads in the frame, and one sheet-path
  playback frame in twenty was that size. It now builds off the main thread from a resized decode
  of the same bytes; readers get null until it lands (a label rides its plate for a moment).
- **A shipped sheet is never baked.** A sheet whose fetch or strip failed used to fall through to
  the in-app bake while its retry waited (four strips of an 8-megapixel terrain render a frame:
  1.8-second frames in the first playback test); `_shippedSheet` now answers "on its way" through
  the retry, and `APP.sheets.status().bakes` counts bakes, which a shipped site keeps at zero.
- Seeks now reach a full core in 0.6–1.5 s (elevation alone was 0.24–0.56 s); the preview still
  shows within 26–107 ms. Memory stayed flat over four passes of far jumps (`__MEM().sheetsMB`
  now counts the sheets). Smoke test 32/32.

| what (round 2) | old page | new page |
|---|---|---|
| sheet-path playback, 3 / 10 Myr/s, 20 / 15 s | 21.2 fps, 50 ms (2048 sheets, no clouds) | 12.8 / 10.7 fps, 67 / 67 ms median; 0 jumps, 0 snaps, 0 flips, 2 / 12 held frames; clouds on every frame, weather clock +16.8 s of 20 |
| playback at zoom 1.6, 3 / 10 Myr/s | 0.7 fps, 1.55 s a frame, terrain throughout | 2.5 / 3.1 fps, sheets 3 frames in 4 after the governor stepped down; 0 jumps, 0 snaps, 1 / 3 holds |
| the same, 600 ms field delay | — | 2.7 fps, 0 jumps, 0 snaps, 5 holds |
| wide view 608 Ma, quality auto | — | 12.1 fps, 83 ms, 0 jumps / snaps / flips, 2 holds |
| most time moved in one frame at 10 Myr/s | 5 Myr | 1.5 Myr |
| forced frame p50, sheet path: playing clouds off / on; paused cache off; zoom 1.6 playing | 50 ms | 25.7 / 29.1 / 24.7 / 18.7 ms |
| crossing frame (storm), three crossings | ≤ 2 uploads | 2.5 / 2.6 / 5.6 ms, 0 uploads (was 316–387 ms with 0 uploads; 355 ms with 8 before the warm rule was reverted) |
| in-app bakes during playback | — | 0 in every run |
| smoke | 32/32 | 32/32 |

Left: the rAF interval of sheet-path playback (67–83 ms median on the loaded machine, 25–29 ms forced) is playback's per-frame work — the terrain material's warm uploads, two strips a frame, decode insertions; one frame in twenty is 250–300 ms. Lazy binding of the terrain material while the sheets draw is the lever.

## Round 3 (2026-09-08): the ambient page, and one update log

- **The two update logs are one.** `build/updatelog.json` is the only source; its `_note` says how
  the numbering was reconciled (August 2.3–3.0 had never shipped; September became 3.1–3.3; this
  round is 3.4). `web/updatelog.json` is exactly what `build_webdata.build_updatelog` writes. The
  smoke test now checks the newest release from the data instead of a hard-coded number.
- **The ambient page carries the app's clouds.** Its shaders moved to `web/shaders/ambient__*.glsl`
  (validated and cross-checked against `ambient.html` by `check_shader.py`, which also emits
  `CN_NEW` into `shaders.js` for the page, and now catches a material that names its shader as
  `SHADERS.NAME` — the preview shader had never been cross-checked). `ambient__ACFRAG` is
  `index__CFRAG` with the land and wetness read from the sheets' own colours (blue water, green
  wet land, tan dry land, white ice, through a coarse mip level), no shadow pass and no map. The
  page copies `bakeNoiseLUT` from app.js and `build_site.py` refuses drift.
- **Its frames no longer hitch.** Sheets and the cloud image upload in strips (two a frame, eight
  while waiting); and the 30 fps cap's `dt` was the interval since the previous *tick*, not the
  previous *draw*, so time ran at half the slider and stuttered — now frames are due on a grid with
  a millisecond of tolerance and dt is the time since the last draw.
- `_verify.html?ambient=NAME&app=ambient.html|_ambient_old.html&secs=&speed=&age=&clouds=0` measures
  the page (draw cadence from the age samples, holds, the page's own frame statistics, a PNG).

| ambient page (20 s at 2 Myr/s from 300 Ma) | old page | new page |
|---|---|---|
| draw cadence median / p95 / max | 48.5 / 50.1 / 51.9 ms, 23.6 a second | 33.3 / 35.1 / 35.4 ms, 30.6 a second |
| time advanced on a 2 Myr/s setting | 0.79 Myr/s | 2.04 Myr/s |
| draws over 60 ms / holds | 0 / 0 | 0 / 4 of 855 |
| clouds | — | on, weather clock +28.5 s, no errors; `?clouds=0` 33.3 / 35.2 ms |
| 10 Myr/s from 600 Ma, 15 s | — | 33.3 / 50 / 50.1 ms (one draw in twenty a tick late while eight strips a frame feed a waiting sheet), 10.2 Myr/s |

## Round 4 (2026-09-08, later): one ambient view

- The in-app ambient mode (`state.ambient`, `#ambientExit`, the Lite link, the in-app full-screen
  button, Escape handling) is gone. `#ambientBtn` → `openAmbient()`: an `#ambientHost` frame over
  the window running `ambient.html?embedded=1&age=&paused=`, the app's loop idling beneath
  (`_ambientFrame`); the page's Close (or Escape) posts `{tectonic:'ambient',action:'close',age,
  playing}` and `closeAmbient()` takes the age and play state up. The app's key handler yields
  while the frame is up.
- `ambient.html` chrome: `#tl` Close + Full screen (the document's, through `allowfullscreen`),
  `#tr` Pause/Play (time only) + era chips built from `eras.json` (`era` field, grouped, oldest
  first; a chip jumps to the era's oldest edge, `state.dir=-1`, playing or paused; the readout and
  the lit chip follow the DRAWN frame, so a jump shows the old picture until the new sheets are
  in). `?ui=0` hides it all. `stamp_data_version.py` stamps the page (its `eras.json` fetch).
- Smoke test: open → the page boots inside the frame → its own Close button → the frame is gone
  and the app holds the age it sent. `_verify.html?ambient=…&jump=ERA&paused=1` probes the chips.

| probe (`_verify.html`, headless M1) | result |
|---|---|
| smoke: Ambient opens the frame → the page boots inside it → its own Close → frame gone, app at the sent age | 3 of 3 steps, 33 of 33 overall |
| ambient page 12 s at 2 Myr/s with the chrome | 30.9 draws a second, 33.3 / 35.0 / 35.3 ms, clouds on, five era chips, no errors |
| `?paused=1` for 8 s | age held at 300, weather clock +16.4 s |
| Cenozoic chip while playing | 271 → 66 Ma and running (59.4 after 3.5 s), 99 frames drawn after, the chip lit |
| Neoproterozoic chip while paused | 300 → 1000 Ma, 102 frames drawn after (the picture follows a jump while paused), the chip lit |

## State right now

- Deployed: see the last commit on `main`; the live `DATA_V` is printed by
  `curl -s https://augustg97.github.io/tectonic-earth/ | grep -o "DATA_V='[0-9-]*'"`.
- The two update logs were reconciled on 2026-09-08: `build/updatelog.json` is the only source (its
  August 5–9 releases 2.3–3.0 had never reached the site; the September releases are 3.1–3.3 after
  them), and `web/updatelog.json` is exactly what `build_webdata.py` writes from it.
- The old page copies (`web/_old.html`, `_app_old.js`, `_shaders_old.js`, `_style_old.css`) are the
  frozen pre-port control; delete them when the next round freezes its own.

## Traps this round found

- **A hidden Browser pane has a 0 × 0 viewport, so the map draws nothing there** (`layoutMap()` reads
  `innerWidth`); the map verifies only through the headless driver, whose iframe has a size.
- **The app's own frames starve the driver's timers.** With the terrain shader at 350 ms a frame,
  `await sleep(2000)` in `_verify.html` takes eleven seconds; a 20-second weather test needed a
  400 s job timeout before the ground cache made frames cheap. Give a job time, then read its
  `secs` field to see how long the wait really was.
- **The cloud fade is not instant.** A shot taken right after a jump catches the layer mid-fade
  (1.4 s at 24 fps, longer when frames are slow); the weather test now waits for `fade` and `blend`
  to reach 1 before its first shot.
- **Only the render call changed for the ground cache, but three things had to move with it:** the
  cloud meshes on their own layer, the camera's layer mask restored after every pass, and the sheet
  bake's ortho camera re-enabled for all layers (it renders through the same scene).

Plus the standing ones in `HANDOFF-M1-DEPLOY.md` and README §7.

## The work queue

1. **Look at the close tilted views with the clouds on.** They keep 55 % opacity at the closest zoom
   (the brief asked for Atlas's attenuation instead of the old retirement); over Tibet at zoom 1.4
   and 60° tilt the deck is heavy. If the owner prefers the mountains, lower the close-view floor
   (`cf=(1.0-0.45*near)` in `loop()`) or retire below some zoom; the switch turns them off meanwhile.
2. ~~Reconcile the two update logs~~ — done 2026-09-08 (round 3).
3. **The five held frames on the sheet path at 10 Myr/s with a 600 ms sheet delay** (old: none, with
   the whole timeline warmed): raise the sheet priority above the pair's refinement kinds or widen
   `_sheetWanted` by one if it shows in use.
4. The mountain round (`HANDOFF-WP10.md`, "What the ribs need") is untouched by this port.

## Commands

```bash
cd "/Users/augustgweon/Tectonic Plate Model"
node build/test_loader.mjs                              # the broker and policy contracts
cd build && ../venv/bin/python check_shader.py          # validates all seven shaders, writes web/shaders.js
../venv/bin/python build_timeline_preview.py --check    # the preview atlas against the shipped sheets
../venv/bin/python serve.py 8899 &  ../venv/bin/python verify_server.py &
../venv/bin/python verify_run.py JOBS.json              # headless jobs on the real GPU
../venv/bin/python verify_diff.py A.png B.png           # two frames
../venv/bin/python build_site.py                        # validators, stamp, docs/
```
