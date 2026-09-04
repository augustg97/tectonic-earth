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

All of it is on branch `claude/tectonic-earth-wp10-handoff-uie4hu` (fast-forwarded from
`claude/tectonic-earth-review-nze22g`, which it contains), not on `main`. Nothing has been
deployed. Deploying is `cd build && python check_shader.py && python
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
- **Round 3 (2026-09-03, a review environment: software GL, no display).** The register
  entry has every number. **B5, the erg half**: the dune lineation is keyed to the resultant
  wind line of the Coriolis-turned zonal bands (NE–SW north of the equator, NW–SE south),
  a corridor octave and a ridged dune octave smeared along it, as tone and normal
  (`?erg=`); verified on the Grand Erg (coherence 0.168 → 0.190 at unchanged band energy).
  The Rub' al Khali is untouched because the round-G6 sand-sea mask is zero there
  (`?show=1` draws it) — that mask is the open erg item. **The belt type**: `build_arc.py`
  bakes 1 − arc into the alpha of `_t` from the shipped trenches, land and ocean-crust
  masks (no source data); the shader takes the fold relief down by 0.9·arc (`?arc=`).
  Verified on the Andes: the Western Cordillera and the Altiplano lose the fold ridges
  (directional energy −37 % and −49 %), the Eastern Cordillera keeps them (0.24/255).
  **Item 3**: a DEM-driven plateau envelope on `rug` was built and measured out — on a
  plateau the 62 km slope is texel-scale speckle (`?show=4`) and multiplying the ridges by
  it re-textures them; it ships off (`?plat=1` to try) and `basinEnv()` remains the model.
  **Found under it**: the fold-axis compression of the detail noise was still combing the
  40 % of `det` left under the atlas; it now fades with the belt gate (README §7.4), which
  raised coherence in every belt measured and left the Zagros regression frame at
  0.54/255. Harness: `_verify.html` forwards every knob, `?quick=1`, `?show=N`, a frozen
  `_old.html` for old-against-new pairs (README §7.16).

## The review on the M1, and then the deploy (decided 2026-09-03)

Nothing is deployed: the atlas amplitude was calibrated by metrics on software GL and you
chose to look first. History stays as it is for now. The branch
`claude/tectonic-earth-review-nze22g` is 27 commits ahead of `main` with no divergence.

**Review.** `cd build && python3 serve.py`, then at zoom 1.35–2:
- the Zagros (51°E 32°N), the Himalaya (86.9°E 28.2°N), the Andes (−68° −18°), Pangaea at
  300 Ma (−5° 8°), each beside `?noatlas=1`; `?atlasN=1.6` and `2.4` bracket the default.
- Tibet with `?basin=0` beside the default (the plateau envelope).
- the Great Plains (−98° 42°) and the Deccan (78° 18°) at zoom 1 or closer with
  `?plainsK=2` beside `?nodrain=1` (the second form is invisible at 2.5 km/px).
- `ambient.html?age=150` — the 2048 sheet set is in `web/sheets/`, gitignored.
- Round 3: the Andes (−68° −18°) with `?arc=0` beside the default (the Western Cordillera
  should lose its folds, the Eastern keep them); the Grand Erg Oriental (8°E 31°N) at 1.35
  with `?erg=0` beside the default and `?erg=2` for the bracket; Tibet with `?plat=1` to see
  the retired envelope for yourself; `?show=1` over Arabia for the sand-sea mask.

**Then one of three deploys**, all from the M1 where the validators run in full:
1. self-contained: `git checkout main && git merge --ff-only claude/tectonic-earth-review-nze22g
   && cd build && python3 check_shader.py && python3 build_site.py && cd .. && git add docs
   && git commit -m "Deploy WP-10 rounds 1-2" && git push` — adds ~160 MB (`_q` 37, `_x` 60,
   sheets 63) to docs/ and history.
2. lean: `python3 build/publish_assets.py --release fields-20260903`, then
   `build_site.py --field-base https://github.com/augustg97/tectonic-earth/releases/download/fields-20260903
   --sheet-base <same>` — docs/ carries manifests only. Check the browser console once for
   CORS on the first field fetch.
3. lean plus history rewrite (D4): `git filter-repo --path docs/fields --path docs/sheets
   --invert-paths` on a fresh clone, force-push, every clone re-clones. Your call, later.

## The display review (M1, 2026-09-03) and what shipped

Looked at in Chrome at zoom 1.35 with the knobs flipped live (`APP.mat.uniforms`), after the
texture-unit fix (README 7.17) let the round-3 shader link at all. Verdicts, verbatim in
substance:

- **Zagros, Himalaya**: the fold ridges "still look like ribbed fabric and unnatural",
  "symmetrical unnatural ribs on top of mountains"; useful for reading elevation, not as
  mountains. Keep only if they can be made natural and varied. The Ganges plain is fine.
- **Andes**: fine zoomed out; up close a faint ridged fabric remains on the Pacific side.
- **Pangaea 300 Ma**: the old belt reads better than the young ones; the ribs still do not.
- **Tibet**: `?basin=0` makes no noticeable difference; fainter ribs in the basins show
  depth but do not look good.
- **Great Plains / Deccan**: a mild improvement at `?plainsK=2`. **Grand Erg**: a mild
  improvement at `?erg=2`. **Arabia** `?show=1`: black, as expected.

**Decision: ship with the ridges off.** `uFoldK` (`?fold=`, default 0) gates the whole belt
relief through `atlasGate()`; `?fold=1` restores this round's look. Plains and erg are baked
at twice the first cut and are the new `1`. The belt-type bake, the fold and drainage
coordinates, the atlas and the knobs all ship, dormant where the gate is 0, so the next
mountain round starts from this state instead of rebuilding it.

**What the ribs need** (the next mountain round, before 4b/4c): the patches are periodic
erosion surfaces sampled at (phi, psi) with one spacing, one asymmetry and one erosion stage
per belt, so every belt reads as the same comb. Vary them along strike (patch mixing by a
low-frequency field, or several patches per cell at different stages), give the ridges the
asymmetry of thrust sheets (steep forelimb, gentle backlimb), and let the stage follow the
belt's age -- the reviewer preferred Pangaea's eroded belt to the young ones. Judge it on the
display first this time (`?fold=1` beside `?fold=0`), numbers second.

## What to do next, in order

0. **Before anything else on the M1** (round 3 changed shipped fields and the shader):
   `cd build && python3 build_arc.py` writes the belt-type alpha into all 251 `_t` files
   (~1 s each; the RGB is untouched, verified byte-for-byte; `--stats 0` lists what it
   flags). `build_foldphase.py -j` and `build_drainphase.py -j` are unchanged. Then
   `check_shader.py` (clean here), and the sheets are stale again — re-bake and bump
   `SHEET_V`.
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
4. **B5 second form is in** (`_x`, tilted patches, `dissectRelief()` steering) and is
   invisible at continental zoom by construction (register, round 2): under 1 % of pixels
   move between the steered and the lattice forms at 2.5 km/px. Judge it at close zoom
   with `?plainsK=2` beside `?nodrain=1`; the plains normal term (1.6) and tone (0.16)
   are still the first cut. **The erg lineation is done** (round 3); what is not is the
   sand-sea mask under it: `ergBody` is a crust-locked noise, zero over Arabia. A body
   from something physical — a closed basin with a sand supply, the drainage and
   substrate fields already say most of it — is the next erg item.
4b. **The arcs want their volcanoes.** The belt type only takes the fold ridges away; a
   cone patch in the atlas (point-source uplift under the erosion model, 30–80 km
   spacing) sampled where `gArc` is high is the next mountain model.
4c. **A plateau's basins need a bake.** Neither `rug` nor prominence at 100 km separates
   the Tibetan interior's ranges from its basins in the PaleoDEM (register, round 3); if
   the corduroy still reads wrong on the display after `?basin=`, the answer is a smoothed
   regional field, not a per-pixel gate.
5. **D4/D5 are done** except the decision: `publish_assets.py` + `build_site.py
   --field-base/--sheet-base` host the textures elsewhere; whether to rewrite history so
   the old copies leave the repository is yours. The page is split; edit shaders in
   `web/shaders/*.glsl` and run `check_shader.py` (README §6).

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
- **At an exact keyframe age the interval kinds bind from the younger neighbour** (age 0
  reads `fut_0005`'s `_t`); a field baked for one keyframe is not the one the shader reads
  there (README §7.16). The first belt-type A/B was null for this.
- **A box statistic is not a spatial pattern.** `rug` on a plateau had the right
  distribution for an envelope and was texel-scale speckle on screen; draw a gate as a
  mask (`?show=N`) before multiplying anything by it.
- **A background waiter can outlive its stated timeout.** One launched the render chain a
  second time an hour after it should have died; two Chromes on one profile directory,
  one of which died at once and skipped a load. Chain launchers want a lock file, and
  anything that must outlive a turn wants `setsid nohup`.
- **The stripe metric is orientation-blind.** Band-pass σ did not move when the comb
  came off because compression reorients noise without changing its energy; the
  structure tensor's eigenvalue difference (directional energy) is what sees a corduroy.
- **The review box had 32 texture units; the M1 has 16.** Rounds 2-3 added five samplers on
  SwiftShader and the shader linked there and failed on real hardware at the first framing of
  the deploy (2026-09-03): a black globe with one console line. The four small per-keyframe
  fields now share one texture (`stackFill`, README 7.17 and §5.8) and `check_shader.py` counts
  the units. Write down what the harness differs from the hardware in, and check it in the build.

## Verification harness (unchanged, plus)

`build/serve.py 8899`, `build/verify_server.py` (8901), `_verify.html?shots=` and the
`APP.lookAt / APP.snap` recipe as before. New: `_verify.html?bake=i0-i1&sheet=W` bakes
sheets; `APP.sheets.status() / bake(i) / png(i)`; `?lite=1|0`, `?sheet=N`,
`?bakefull=1`, `?noshipped=1`, `?noatlas=1`; `ambient.html` exposes `AMB.status()` and
`AMB.snap()`.
