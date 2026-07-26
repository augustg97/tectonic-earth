# Handoff — Tectonic Earth sea-floor work

Paste this whole file as the first message of a new session.

---

## What you are working on

**Tectonic Earth** — interactive deep-time paleogeography app, 1000 Ma → +250 Myr, globe + Mollweide map.

- Repo: `/Users/augustgweon/Tectonic Plate Model` (do NOT move it back to `~/Desktop` — macOS TCC blocks builds there)
- Live: https://augustg97.github.io/tectonic-earth/ (GitHub Pages serves `main:/docs`)
- **Read `README.md` first.** It documents goals, all six standing working rules, every subsystem, the traps that have cost time, and a "where the ocean model stands" section listing what is knowingly unfinished.

## The current task

Bring the ocean floor to reference quality. **This is a LOOP the user set explicitly:**

> "keep going and making improvements to improve the ocean floor until we reach Google-Earth-level quality, based on the screenshots in the Google Earth Examples folder inside Deep Time Maps and Resources. After making updates, visually compare with Google Earth, and then assess whether we've reached equivalent fidelity and detail. If yes, deploy and launch; if no, continue to make updates to improve detail and fidelity and repeat."

So: change → rebuild → screenshot → compare against the reference images → assess honestly → repeat. **Deploy only when equivalent.** This overrides the standing "always deploy every round" rule for this item.

### Reference material (study before changing anything)

`/Users/augustgweon/Tectonic Plate Model/Deep Time Maps and Resources/`

- `Google Earth Examples/` — 5 screenshots. **These define "done."** The SW Pacific one (`Screenshot 2026-07-24 at 5.42.12 PM.png`) is the most informative.
- `pitch-continental-shelf-slope-way-transition-region.webp` — margin anatomy; canyons are a DENSE DENDRITIC comb across the whole slope.
- Other `.webp` process diagrams: subduction, back-arc basins, slab pull, atoll formation, supercontinent cycle, oceanic crust age pattern.
- ~76 `.jpg` deep-time paleogeographic maps with Ma dates (Scotese / DeepTimeMaps). The user wants these audited against our reconstruction **later** — not this round.
- Also given this session: https://www.arcgis.com/apps/mapviewer/index.html?webmap=67ab7f7c535c4687b6518e6d2343e8a2 — resolves to **Esri "Ocean Basemap"** (GEBCO-based). It did not render in the browser pane; the tab title was the only thing that loaded. Treat as a second reference alongside Google Earth.

### What the references actually show (this corrected a wrong assumption — don't re-make it)

Below the shelf break, Google Earth's ocean carries **almost no colour variation** — the whole abyss is one blue-violet and *every bit of visible detail is hillshade*: fine dense engraving, fracture zones as long thin scratches, chains as strings of tiny bumps, trenches as sharp dark curves. An earlier round concluded "we need more contrast" and that was **wrong**. The direction is: flatten ocean colour, put everything into fine relief.

## State right now

- Last live deploy: **`DATA_V=20260726-0223`** (commit `d3436b7`)
- Committed since then and **NOT deployed**: `a1116d1`
- **Only 2 of 251 keyframes (0 and 60 Ma) carry the newest seamounts.** The rest are from the `d3436b7` build. Do not deploy until a full reskin has run.
- Working tree should be clean; `build/cache/` (~380 MB) and `data/` are gitignored.

## Architecture you need to know

The sea floor is keyed to **crustal age**, not distance-to-present-ridge (that change is done and is the foundation of everything else):

- `build/crustage.py` — isochron model from the Merdith 2021 rotation model via pyGPlates. Also `plume_track()`, which places hotspot volcanoes correctly (see below). Cached to `build/cache/age/`, 201 keyframes, ~13 min to rebuild.
- `build/realage.py` — the surveyed Müller et al. 2019 age grid (`data/Muller2019_PresentDay_AgeGrid.nc`, 25 MB, already downloaded) carried backwards.
- `build/oceanage.py` — fuses the two in the **gradient domain**, and derives isochron azimuth + fracture zones. Cached to `build/cache/ocean/`.
- `build/sediment.py` — thickness competing against the relief it buries.
- `build/seamounts.py` — the three seamount populations.
- `build/seafloor.py` — assembles it all into the shipped `_e` and `_o` fields.
- `web/index.html` — the GLSL shaders (per-pixel fabric, canyons, colour).

## Measured facts — do NOT re-derive these

| Fact | Value |
|---|---|
| 16-bit `_o` coordinate | **Unaffordable.** Lossless forced; 320 MB (hi/lo split), 224 MB (sawtooth), 124 MB (lossless, no extra precision) vs 23 MB now. Solved by log companding instead. |
| Companding | `log(1+d/2.5)`, full scale **52°** of spreading (190 Myr × 30 km/Myr). `CO_K=3.0819` must match in `seafloor.py` and the shader. Step at axis 0.030° = 3.4 km. |
| Isochron model vs surveyed grid | correlation **0.41**, median error 33 Myr. Hence the hybrid. |
| Surveyed coverage | 0 Ma 55% of globe · 40 Ma 38% · 80 Ma 21% · 150 Ma 4% · 180 Ma 0.7%. Past ~180 Ma no ocean crust survives. |
| Isochron coverage (within 5°) | 0 Ma 99% · 150 Ma 93% · 300 Ma 86% · 500 Ma 81% |
| Sediment calibration | mean 451 m, plains 17%, hills 72% (targets ~450 m, ~20%) |
| Elevation quantum at abyssal depth | **105 m** = a 19° normal tilt. Half of adjacent abyssal cells differ by exactly zero. |
| Hawaii plume track | 76 mm/yr at present, 46 at 40 Ma (real Pacific 70–100) — validates `plume_track` |
| Marbling threshold | perturbation gradient exceeds carrier at **13°** from the axis |

## Traps that have each cost real time

1. **Run `python check_shader.py` before every shader edit.** A backtick anywhere in shader source (even in a comment) closes the JS template literal → black globe. Has happened three times. Also catches GLSL reserved words, use-before-declaration, brace/comment imbalance.
2. **A distance transform is not a shape until band-limited** — raw EDT level sets follow the pixel lattice and draw right angles.
3. **Never treat categorical IDs as a continuous field.**
4. **Anisotropy by domain-stretch is impossible on a sphere** — `dot(P,t)≡0` for a tangent, and its derivative is zero too. Elongation must come from a scalar that varies across the axis, or from smearing.
5. **Never ring-average at the poles.**
6. **Two systems texturing one surface** — when detail looks *wrong* rather than *absent*, check whether something else is writing to the same scale band. `elevDetail`'s isotropic blobs were beating the anisotropic fabric because they were in the elevation.
7. **Smoothing fixes can erase the features they sit next to** — the 2.9-texel deep-water gradient baseline (added to kill the quantisation staircase) was erasing fracture zones, which are 430 m deep and two texels wide. Capped at 0.6.
8. **`pygplates` does not refuse negative times** — it extrapolates and returns confident nonsense. The future path is handled explicitly in `oceanage._future`.

## The work queue

1. **Texture fineness** — the biggest remaining gap. Ours reads clumpy; the reference is a fine dense engraving. Look at the shader fabric frequencies and `abyssLod`.
2. **Shelf colour** — ours is saturated cyan, the reference is muted pale blue. In the shelf-grading block after the `bio` mix in `web/index.html`.
3. **Residual tonal patchiness** — better but not uniform enough.
4. **Reduce/naturalise seamount count further** — user said still slightly too many, and wants more natural spatial patterning.
5. **Full reskin** (`python reskin_seafloor.py`, ~50 min, 251 keyframes) — required before any deploy.
6. **Re-compare and assess.** If not equivalent, loop back to 1.
7. Then deploy: `check_shader.py && build_site.py` → commit → push → verify live `DATA_V`.

Known-unfinished beyond this round (in README §10): seamount chains are modelled but plume positions are hashed rather than taken from a real hotspot catalogue; aseismic ridges and marginal basins (Ninetyeast, Walvis, Philippine Sea) are absent or generic; 27 labels sit on the wrong medium for >⅓ of their span.

## Commands

```bash
cd "/Users/augustgweon/Tectonic Plate Model/build"
../venv/bin/python check_shader.py                    # ALWAYS before shipping a shader edit
ONLY_AGE=300 ../venv/bin/python reskin_seafloor.py    # one Phanerozoic keyframe, quick check
../venv/bin/python reskin_seafloor.py                 # all 251 (~50 min)
../venv/bin/python build_site.py                      # stamps DATA_V, copies web/ -> docs/
```

A local server is usually already running on **:8899** serving the repo; `http://localhost:8899/index.html` is the app. Drive it from the browser pane with `APP.jumpTo(<Ma>)`, `APP.state.rot` / `.tilt` (radians, tilt clamped ±1.3) / `.zoom` (~1.5 close, ~2.5 far), `APP.state.view='map'|'globe'`.

## How the user wants this done

Read the six rules in README §2 — they are not boilerplate, each came from a specific failure. The two that matter most here:

- **Measure before tuning.** Two of the longest-standing defects were invisible to inspection and obvious to a histogram.
- **Prefer structural over cosmetic.** Several rounds of texture tuning each produced "a modest improvement" and never closed the gap; the structural changes did. Ask what the real-world object or process is and model that.

And: **visually verify everything** (render it and look), **address every item raised** (say explicitly if something can't be done), and **be honest in the assessment** — the user has asked for a truthful yes/no against the reference, not an optimistic one.
