# Handoff — Tectonic Earth sea-floor work

Paste this whole file as the first message of a new session.

---

## What you are working on

**Tectonic Earth** — interactive deep-time paleogeography app, 1000 Ma → +250 Myr, globe + Mollweide map.

- Repo: `/Users/augustgweon/Tectonic Plate Model` (do NOT move it back to `~/Desktop` — macOS TCC blocks builds there)
- Live: https://augustg97.github.io/tectonic-earth/ (GitHub Pages serves `main:/docs`)
- **Read `README.md` first.** It documents goals, all six standing working rules, every subsystem, the traps that have cost time (§7 — now eight of them), and §10 "where the ocean model stands", which carries this round's before/after table.

## The current task

Bring the ocean floor to reference quality. **This is a LOOP the user set explicitly:**

> "keep going and making improvements to improve the ocean floor until we reach Google-Earth-level quality, based on the screenshots in the Google Earth Examples folder inside Deep Time Maps and Resources. After making updates, visually compare with Google Earth, and then assess whether we've reached equivalent fidelity and detail. If yes, deploy and launch; if no, continue to make updates to improve detail and fidelity and repeat."

So: change → rebuild → screenshot → compare against the reference images → assess honestly → repeat. **Deploy only when equivalent.** This overrides the standing "always deploy every round" rule for this item.

### Reference material

`/Users/augustgweon/Tectonic Plate Model/Deep Time Maps and Resources/`

- `Google Earth Examples/` — 5 screenshots. **These define "done."** `Screenshot 2026-07-24 at 5.42.56 PM.png` (South Atlantic) is the most useful: it is the most zoomed-in, at **~1.6 km/px**, so it shows the texture band the argument is about.
- `pitch-continental-shelf-slope-way-transition-region.webp` — margin anatomy; canyons are a DENSE DENDRITIC comb across the whole slope.
- Other `.webp` process diagrams: subduction, back-arc basins, slab pull, atoll formation, supercontinent cycle, oceanic crust age pattern.
- ~76 `.jpg` deep-time paleogeographic maps with Ma dates (Scotese / DeepTimeMaps). The user wants these audited against our reconstruction **later** — not this round.
- Esri "Ocean Basemap" (GEBCO-based) — https://www.arcgis.com/apps/mapviewer/index.html?webmap=67ab7f7c535c4687b6518e6d2343e8a2 — did not render in the browser pane.

## Measure, don't eyeball — the harness

The comparison is only meaningful at **matched pixel scale**, and getting there took a while, so reuse this rather than rebuilding it:

- `APP.state.zoom = 1.35` gives **1.58 km/px** at view centre — the reference's scale. `tilt` is the centre latitude in radians; `lon_centre = -degrees(rot) - 89.1`.
- The browser-pane screenshot tool downsamples to 800 px, which destroys exactly the band this work is about. Instead: run a tiny receiver (`scratchpad/shotsrv.py`, port 8898) and POST `canvas.toDataURL()` to it. `APP.step()` drives a frame by hand; when the pane is hidden the canvas collapses to 0×0, so call `renderer.setPixelRatio(1); renderer.setSize(1400,900,false)` before every capture.
- `scratchpad/cmp.py` and `bands.py` print the numbers that decide it: ocean R/B and G/B, saturation, and the radial spectrum split into <12 / 12–30 / 30–80 / 80–250 / >250 km bands, plus **local** grain coherence (structure tensor in 24 px blocks — a single tensor over a whole tile reports ~0 whenever the grain's direction rotates across it, and scored the reference's own fabric at 0.09).
- The shader carries a temporary `uDbg` vec4 uniform wired to the fabric terms (x = noise fabric, y = fault sets, z = fracture-zone corrugation, w = the dequantisation). Toggling it from the console is how every one of this round's attributions was actually made. **Remove it before shipping.**

## The second round (resolution round)

The user asked for the three remaining items to be closed: the synthetic grain, the seamount cones, and the resolution. All three were done, and two of them turned out not to be what they looked like.

- **Seamount cones were the CANYON system, not quantisation.** The rings are finer than a texel, which no 8-bit terrace can be. The canyon gate was "tilted ground between 200 m and 3.5 km" — which every seamount flank satisfies — and the canyon domain subtracts DEPTH as its potential, so on a cone it drew the depth contours. Gated on whether there is a shelf above the slope (the four wide taps give it free) plus prominence. Its probe was also stepping a fixed ANGLE rather than a fraction of a noise cell, so at the tributary frequency `k1` and `k0` were 2.5 cells apart — decorrelated samples, not a slope — and `abs(gully)*1.15` could exceed 1, driving the colour negative. That was the hard black band on every margin, blamed for two rounds on the elevation staircase.
- **Resolution doubled to 2048×4096**, which is the 6-arc-minute source DEM's own resolution, at q=94. About fifteen constants had to move with it; see README §7.6, which is the trap worth reading before touching it again. The counter-intuitive one: the gradient baseline must NOT follow the grid.
- **The grain** now has its aspect, spectrum and coherence measured against the reference rather than guessed, three power-law orders, and — the part that reads as "not synthetic" — spreading rate driving hill SPACING as well as amplitude, plus fabric strength tied to the baked field's own roughness so provinces differ.
- **The shade ceiling was clipping every lit face.** Flat ground sits at 1.09 against a 1.18 ceiling and a 0.70 floor, so hills could darken by 0.39 and brighten by 0.09: the fabric rendered as dark marks on a light ground rather than as relief. 1.34 at sea (land still needs 1.18, its base colours are too bright).

## State right now

- Last live deploy: **`DATA_V=20260726-0223`** (commit `d3436b7`) — far behind the working tree.
- Committed and not deployed: `a1116d1`, `e296c96`.
- **Everything since is uncommitted**: `web/index.html`, `build/build_fields.py` (ELEV_H/W 1024×2048 → 2048×4096, ELEV_Q 92 → 94), `build/render.py` (`smooth_bathymetry`), `build/seafloor.py` (every filter radius doubled), README §7/§10, this file.
- Two full reskins were run, the second at the new resolution. `web/fields` is **145 MB** against 94 before, of which `_e` is **57.4 MB** against 18.4. Verified across 0 / 300 / 700 Ma and +150 Myr, globe and map, with no console errors; frame time 57 ms close and 72 ms globe against ~67 for the committed shader.
- **Not deployed**, deliberately, per the loop's own rule.

## Do not change the pipeline without re-running the reskin

`build_fields.ELEV_H/W/Q`, `render.smooth_bathymetry` and every filter in `seafloor.py` are baked into the shipped `_e`. The shader is not — it can be iterated freely against whatever fields are on disk, which is what makes the loop tractable: start the reskin, then tune the shader while it runs.

## What this round found (all measured, none guessed)

The headline: **almost none of the gap was in the abyssal-hill fabric**, which is where the previous rounds had been looking.

1. **The maze was the elevation field's quantisation contours.** 75% of adjacent abyssal cells are identical; only 27 of 256 levels are used below 3.5 km. The hillshade was drawing terrace level-sets. Dithering at encode does **not** survive lossy WebP (measured, all of white/blue/TPDF). The fix is shrinkage against an exactly-known noise bound — see README §7.2.
2. **The pale speckle over the open ocean was sun glint driven by the sea-FLOOR normal.** 892 blobs in one frame. A sea surface is flat regardless of the bathymetry under it.
3. **The bright dots were seamount summits painted as shelf.** The old ramp lightened anything within 850 m of the surface; bottom return is exponential and a basalt summit under 200 m of clear water returns nothing.
4. **The ocean's colour model was wrong in kind, not degree.** The reference is one hue shaded, not a hue ramp — its R/B holds at 0.37–0.41 from the 1st to the 75th percentile.
5. **The fault set's wavelength drifts** from 21 km at the axis to 190 km at twenty degrees out, because it is keyed to a companded coordinate. Past a few degrees it was not a fault set at all.
6. **The sea floor was being shaded at 59× vertical exaggeration** — right for land, far too much for water.

## Traps that have each cost real time

1. **Run `python check_shader.py` before every shader edit.** A backtick anywhere in shader source (even in a comment) closes the JS template literal → black globe.
2. A distance transform is not a shape until band-limited.
3. Never treat categorical IDs as a continuous field.
4. Anisotropy by domain-stretch is impossible on a sphere. Elongation must come from a scalar that varies across the axis, or from smearing (`licGrad`).
5. Never ring-average at the poles.
6. **Two systems texturing one surface** — now three instances, tabulated in README §7.4. The lesson has sharpened: fade by *the variable that says whose band it is*, not by whichever variable happens to correlate.
7. **A coordinate-keyed periodic term drifts in wavelength** (README §7.5).
8. **Vertical exaggeration is not one number** (README §7.6).
9. `pygplates` does not refuse negative times — it extrapolates and returns confident nonsense.

## The work queue

Ranked by how much of the remaining visible gap each closes:

1. **12–30 km energy is still short** — 20–28% against the reference's 32–41%. This is the band the fabric owns, so it is a fabric question, not a data one.
2. **The fabric does not break at fracture zones.** A real chart's abyssal-hill provinces are bounded by them and change character across each; ours is continuous. `_o` carries no fracture-zone channel to key on — R is age, G/B direction. Adding one means finding a spare channel or a fourth field.
3. **Coastlines and shelf breaks stay jagged at texel scale.** Verified as a source-data limit rather than a shader one: globally the abyss now measures a median slope of 0.00° and p95 of 1.08°, entirely physical, and the remaining stipple sits on genuinely steep margins where the PaleoDEM itself is coarse. Google Earth's near-shore bathymetry is 15 arc-seconds — twenty times finer than anything available here.
4. **Deep time renders much flatter and greener than the present.** At 300 Ma the fabric is nearly absent (old crust everywhere, no surveyed age, low `aniso`) and `uSeaTint` pulls the hue well toward the ancient green sea. Both are deliberate, and neither has a reference to check against — but it does mean the calibration only holds at the modern end.
5. Then: remove `uDbg`, `check_shader.py && build_site.py` → commit → push → verify live `DATA_V`.

Known-unfinished beyond this round (README §10): plume positions are hashed rather than from a real hotspot catalogue; aseismic ridges and marginal basins are absent or generic; 27 labels sit on the wrong medium for >⅓ of their span.

## Commands

```bash
cd "/Users/augustgweon/Tectonic Plate Model/build"
../venv/bin/python check_shader.py                    # ALWAYS before shipping a shader edit
ONLY_AGE=300 ../venv/bin/python reskin_seafloor.py    # one Phanerozoic keyframe, quick check
../venv/bin/python reskin_seafloor.py                 # all 251 (~55 min warm, ~3 h cold)
../venv/bin/python build_site.py                      # stamps DATA_V, copies web/ -> docs/
```

A local server is usually already running on **:8899** serving the repo. Drive it from the browser pane with `APP.jumpTo(<Ma>)`, `APP.state.rot` / `.tilt` / `.zoom`, `APP.state.view='map'|'globe'`, and `APP.step()` to force a frame.

## How the user wants this done

Read the six rules in README §2 — each came from a specific failure. The two that mattered most this round:

- **Measure before tuning.** Every real cause this round was invisible to inspection and obvious to a histogram, a spectrum or a term-by-term A/B. Two full rounds of fabric tuning had been spent on a problem that was not in the fabric.
- **Prefer structural over cosmetic.** The changes that moved the image were: a model of the encoder's error, a model of bottom return, a model of what a sea surface is, and a model of what sets abyssal roughness. The parameter tweaks in between moved almost nothing.

And: **visually verify everything**, **address every item raised**, and **be honest in the assessment** — the user has asked for a truthful yes/no against the reference, not an optimistic one.
