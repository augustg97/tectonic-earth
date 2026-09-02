# Handoff — the WP-10 roadmap (mountains, frame cost, ambient build)

Paste this file as the first message of a new session. It supersedes `HANDOFF.md`
(the sea-floor loop) for the roadmap work; that file still documents the sea floor.

## What this is

**Tectonic Earth** — deep-time paleogeography app, 1000 Ma → +250 Myr, globe + map.
Repo at `/Users/augustgweon/Tectonic Plate Model`; live site is `main:/docs` on
GitHub Pages. **Read `README.md` §2 (the working rules) and §5.9 (world sheets) first,**
then `Deep Research/research reports/WP-10-review-and-roadmap.md` — the review that
set this roadmap, with goals G1–G5 and plans A–D — and the two `WP-10 — IMPLEMENTATION`
entries at the end of `Deep Research/MODEL-GAPS.md`, which log what shipped and the
numbers that say it did.

All of it is on branch `claude/tectonic-earth-review-nze22g`, not on `main`. Nothing
has been deployed. Deploying is `cd build && python check_shader.py && python
build_site.py`, then merge to `main` and push (README §6).

## What is done (in roadmap order)

- **D1** foreland moat no longer drowns dry plains (shader floor + `audit_foreland` check)
- **D2** `check_shader.py` regenerates `web/shaders/*.glsl`; **D3** `site/` junk removed;
  **D6** README field tables true
- **A5** real-time pace (`dtT`), idle throttle (5 fps when nothing moves), prefetch gated
  on hidden tabs / battery / metered links
- **B1** the three per-pixel mountain constructions retired (tone band, sine grating,
  ridged transform) with the 2π scale-convention note in the shader
- **A1–A4** world sheets: equirect bake mode in FRAG (`uMapProj 2`, ocean mask in alpha
  at 0.5), the lite material, strip bakes with an LRU pool, shipped sheets from
  `build/bake_sheets.py`, auto LOD by pixel footprint, Full quality pins the live path
- **C1/C3** `web/ambient.html` (sheets + `_v` only) and the "Lite view" link in Ambient
- **B2** `build/build_orogen_atlas.py` — stream-power erosion under fold-belt uplift on
  periodic patches → `web/atlas.webp`; **B3** `build/build_foldphase.py` bakes the fold
  coordinates `_q` (two potentials per keyframe, conjugate gradients preconditioned by
  an exact FFT Laplacian solve, 1.3 s a keyframe — the lsqr first cut never converged
  and a plain FFT projection lost most of ψ) and `atlasRelief()` samples the belt
  patches at (φ, ψ) — verified in emulation and on the Zagros render; **B4** the height
  floor of `atlasGate()` lowered to 100–400 m (deep-time belts sit at 150–700 m);
  **B5** (first form)
  `dissectRelief()` lays the plateau/lowland patches on hard flat uplands, untuned
- **Round 2 (2026-09-02, afternoon).** Live knobs for the atlas amplitudes (`?atlasN=`
  `?atlasT=` `?atlasH=` `?plainsK=`, `uAtlasK`) and the plateau basin envelope
  (`basinEnv()`, `?basin=0`); **B5 second form**: `build_drainphase.py` bakes drainage
  coordinates `_x` (χ across the regional flow, ω along it) from the PaleoDEM smoothed to
  120 km, `build_orogen_atlas.py` erodes four plains patches on a wrap-aware regional tilt
  (cells 12–15), and `dissectRelief()` samples them at (χ, −ω) where the flow is trusted
  (`?nodrain=1` for A/B); **D4** `FIELD_BASE`/`SHEET_BASE` in both pages,
  `build_site.py --field-base/--sheet-base`, `publish_assets.py`; **D5** the page is
  split: `index.html` markup, `style.css`, `app.js`, `web/shaders/*.glsl` as the shader
  sources with `check_shader.py` packing `shaders.js` and `build_site.py` inlining the
  deployed page. `check_shader.py` now also flags a function called above its definition.

## What to do next, in order

1. **Sheets.** A 2048-wide set is baked here on software GL at the end of round 2
   (`web/sheets/`, gitignored; `build_site.py` ships it) — check `web/sheets/manifest.json`
   has 251 entries before deploying. The 4096 set still wants the M1:
   `cd build && python3 bake_sheets.py` (~1 min GPU + 10–20 min encode). Every shader
   edit invalidates shipped sheets: re-run and bump `SHEET_V` in `web/app.js` and
   `web/ambient.html`.
2. **Amplitudes on a real display.** The normal term is calibrated by sweep (register,
   round 2): default 8.0 (2.0× the first cut), energy-neutral bracket 1.6–2.7×, no
   saturation up to 2.4×. `?atlasN=` `?atlasT=` `?atlasH=` `?plainsK=` scale the four
   terms live; `?basin=0` removes the plateau envelope. The two questions the numbers
   could not settle: the envelope's trough depth on Tibet (0.25 now; the x2.4 frame still
   combs the plateau), and the Andes drawing fold-belt ridges — a belt-type channel in
   `_t` (arc vs fold belt), not an amplitude.
3. **B4 is done** (floor lowered to 100–400 m on the field statistics, controls
   unchanged; register entry of 2026-09-02). What the numbers point at next: the gate
   opens on 94 % of the Tibetan interior and 98 % of the Altiplano at more than half
   strength, so plateau interiors read as corduroy — carry more of the amplitude on
   `rug` (now 0.6–1.0) or on a basin/plateau-interior term; and eroded old belts
   (Appalachians 0.10, Urals 0.02 shortening) sit below the age-relative gate, which is
   correct for what the gate means and a separate decision.
4. **B5** plains, second form: the first form lays isotropic dissection on hard flat
   uplands; steering it by a drainage-azimuth field from `build_surface.py`'s D8
   receivers (a third potential, like φ/ψ) and adding erg lineation from fetch are
   the next steps if the plains still read as unorganised.
5. **D4/D5** move `docs/fields` and `docs/sheets` out of git history; split `index.html`.

## Traps this round found (add to README §7 when they recur)

- **A masked target is not a weighted fit.** Solving the plain Laplacian with the gate
  moved into the right-hand side is exact and instant and wrong: the masked along-strike
  field has curl along both sides of every belt, and the projection onto gradient fields
  threw away three quarters of ψ. Keep the weights in the operator; use the FFT solve as
  the preconditioner (`build_foldphase.py`).
- **Pick the test framing by the effect, not by the population.** The 150 Ma window with
  the most cells in the 150–700 m band sat at 272 m and 0.18 shortening, where neither
  floor opens the gate; the two renders differed in 0.7 % of pixels and said nothing.
  Choose the window by the gate difference itself.
- **Lossless WebP zeroes RGB under alpha 0 unless told not to.** The low byte of ψ rides in
  alpha; `exact=True` in the encoder, and check the roundtrip byte-for-byte.
- **An empty framebuffer from `APP.snap` can be a one-off** under software GL contention
  (one of thirteen renders this round); re-run before reading anything into it.

- **A canvas premultiplies.** Anything read back through a 2-D canvas loses its colour
  under alpha 0. The sheet mask is alpha 0.5 for exactly this reason.
- **`pkill -f` matches the shell that runs it** when the pattern is in your own command
  line; kill by exact PID from `ps -eo pid,args`. The same self-match bit `pgrep -f "node shoot.js"` inside a background script: the harness wrapper's own argv carries the whole command text, so the wait loop never ended. Wait on a marker file or an exact PID, never on a pattern that appears in your own script.
- **Software GL saturates the box.** A SwiftShader render pins every core; Python work
  run beside it looks hung. Serialise them.
- **Uphill receivers make cycles.** A steepest-descent receiver must be strictly lower or
  the level walk never ends (`_receivers` in the atlas baker).
- The stale `web/shaders/*.glsl` copies were 500 lines behind the page; never read them
  as the shader unless `check_shader.py` has just written them.

## Verification harness (unchanged, plus)

`build/serve.py 8899`, `build/verify_server.py` (8901), `_verify.html?shots=` and the
`APP.lookAt / APP.snap` recipe as before. New: `_verify.html?bake=i0-i1&sheet=W` bakes
sheets; `APP.sheets.status() / bake(i) / png(i)`; `?lite=1|0`, `?sheet=N`,
`?bakefull=1`, `?noshipped=1`, `?noatlas=1`; `ambient.html` exposes `AMB.status()` and
`AMB.snap()`.
