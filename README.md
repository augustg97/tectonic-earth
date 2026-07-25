# Tectonic Earth

An interactive reconstruction of Earth's surface across 1.25 billion years — from the supercontinent **Rodinia** at 1000 Ma, through **Pangaea**, to the projected **Pangaea Proxima** 250 Myr ahead — as a globe and as an equal-area map.

**Live:** https://augustg97.github.io/tectonic-earth/
**Contact:** August Gweon · augustgweon@gmail.com · august@anthropic.com

---

## 1. What this is trying to be

A **model**, not a slideshow. The app ships physical *fields* per keyframe and assembles the world in a GPU shader at render time. Nothing is a pre-rendered picture of an era.

That choice is the whole architecture, and everything below follows from it:

- A coastline **migrates** between keyframes because the elevation field interpolates, instead of one image dissolving into another.
- Relief is shaded **per pixel**, so terrain keeps its bite at any zoom.
- Detail finer than any field the app could ship — abyssal hills a few kilometres across, gullies on a continental slope — is **grown per pixel from the process that makes it**, so zooming reveals structure rather than running out of it.
- Every layer is derived from the same underlying data, so the layers cannot disagree with each other.

### Goals

1. **Scientific veracity first.** Where the published record says something, follow it. Where it does not, model the mechanism and say plainly that it is modelled.
2. **Coherence.** One world, internally consistent. Boundaries agree with motion; climate agrees with geography; biota agree with the interval and the region.
3. **Detail that survives zoom.** The interesting scales are often below the shipped grid. Those must be synthesised from a mechanism, not faked with noise.
4. **Honesty about uncertainty.** Deep time and deep future are interpretive. The UI says so, and the model degrades gracefully rather than inventing confident detail.

---

## 2. Working rules

These are standing constraints on how work is done here, not suggestions.

### 2.1 Always visually verify

An update is not done when the field contains the value. It is done when it has been **rendered and looked at**. Render the frame, read the image, confirm the change is on screen and is correct.

*Why:* this project has twice had work reported as complete based on field statistics while the feature was invisible on screen.

### 2.2 Fix the system, not the instance

When correcting an error, make the change at the level that fixes the whole **class** across the timeline. If a fossil appears on the wrong plateau, the bug is the region-tagging system, not that one card.

*Why:* this is a coherent world. A patched instance leaves the same bug at every other age and place.

### 2.3 Prefer structural, model-based changes over cosmetic ones

When fidelity is short, build or extend a **model** of the thing — a network, a mechanism, a physical process — rather than tuning noise, amplitudes or colours to imitate the look.

*Why:* several rounds of sea-floor work were spent adjusting procedural texture when the real deficits were structural (a colour ramp that collapsed every depth into one tone; a ridge "system" that was a dozen disconnected arcs with distance interpolated between them). Each cosmetic pass produced a "modest improvement" and never closed the gap. The structural ones did.

*How to apply:* ask what the real-world **object or process** is — a connected spreading network segmented by transforms, normal faulting producing tilted blocks, turbidity currents cutting canyons — and model that. Let the appearance fall out of it.

### 2.4 Measure before tuning

Before adjusting an appearance, measure what the field actually contains. Two of the longest-standing sea-floor defects were invisible to inspection and obvious to a histogram:

- the elevation quantum is **105 m at abyssal depth**, and it feeds a normal of `(-gE, gN, 300)` — a **19° tilt per level** on a plain that is genuinely flat;
- half of all adjacent abyssal cells differed by exactly zero. The "texture" down there *was* the quantisation staircase.

### 2.5 Track every request; never silently drop one

Keep a running list of each round's items and address all of them. If something genuinely cannot be done, **say so explicitly and say why** — do not omit it.

### 2.6 Always deploy

Every round ends with `build_site.py` → commit → push to `main`, and a check of the live `DATA_V` stamp. Local-only changes are invisible to review and read as "not done".

---

## 3. Repository layout

```
build/          49 Python modules, ~15k lines — the offline pipeline
web/            the app: index.html (~4k lines, incl. the GLSL shaders) + data
web/fields/     1,506 field textures (6 kinds × 251 keyframes), plus a second
                present-day lake field without the geologically young lakes
docs/           the built static site; GitHub Pages serves main:/docs
data/           source DEMs, rotation files, catalogues (not in git)
```

Keyframes are every **5 Myr** from 1000 Ma to +250 Myr — 251 of them.

Build scripts use relative paths (`../web`, `../docs`), so the project directory can move. It has: it lives at `~/Tectonic Plate Model` because macOS TCC gates `~/Desktop` and `~/Documents` and blocked the build mid-session. Do not move it back.

---

## 4. The shipped fields

Six textures per keyframe. All are WebP; all are decoded and interpolated between the two bracketing keyframes in the shader.

| suffix | field | resolution | contents |
|---|---|---|---|
| `_e` | elevation | 2048×1024 | signed-sqrt encoded, so precision concentrates near sea level — the coastline is the one contour that must interpolate cleanly |
| `_r` | rainfall | 1536×768 | smooth, so it costs little |
| `_m` | plate motion | 128×64 | R = east, G = north, B = confidence |
| `_w` | lake depth | 2048×1024 | baked standing water, sqrt-encoded metres |
| `_d` | surface process | 2048×1024 | drainage, substrate, fetch |
| `_o` | ocean structure | 2048×1024 | R = companded across-ridge coordinate, G/B = spreading direction with confidence in its length |

Temperature is **not** shipped: it is a closed form of latitude, elevation and the era anomaly, so the shader recomputes it for free.

---

## 5. Subsystems

### 5.1 Plate motion and boundaries

Two independent routes, used where each is sound.

**Deep time** (`build_plates_gplates.py`, `plates_time.py`) — the **Merdith et al. (2021)** full-plate rotation model, resolved with pyGPlates into continuously-closing plate topologies per 5-Myr age, with boundaries classified as ridge / trench / transform. Stored in `web/plates_time.json` as `{"c": "ridge"|"trench"|"transform", "p": [[lon,lat],…]}`.

Boundaries are derived by **segmenting the surface into plates first and taking the edges afterwards**. An earlier version thresholded a strain field and thinned it, which can only ever give fragments — a threshold crossing is a patch, and thinning a patch gives a broken crest. Real boundaries are not features in their own right; they are the edges between plates, so they are continuous and closed by construction.

**Measured motion** (`motion.py`) — two elevation keyframes are the same crust some millions of years apart, so block-matching one against the next recovers how far each patch of surface travelled. Matching uses a ±15 Myr half-baseline — a 30 Myr window — because over a single 5 Myr step a plate moves well under one grid cell, which integer block-matching cannot resolve at all.

Where there is no structure to match — bare abyssal plain — **no motion is claimed** rather than invented. This matters downstream: an early attempt to find ridges by thresholding this field's divergence marked scattered noise as ridges, precisely because the field is silent by design over the open ocean.

### 5.2 Paleogeography

Three eras, three sources (`build_fields.py`):

- **Phanerozoic 0–540 Ma** — Scotese & Wright PALEOMAP PaleoDEMs, 6-arc-minute, straight through.
- **Future 0 → +250 Myr** — the *present* DEM rigidly rotated by plate group. At age 0 every rotation is the identity, so the future series begins as an exact copy of the present frame, inherits its full detail, and leaves no seam.
- **Precambrian 540–1000 Ma** — generated cratons (`precambrian.py`), blended onto the real 540 Ma DEM across the youngest 60 Myr so the handoff is continuous rather than popping.

Precambrian coastlines are **generated, not copied**. An earlier version cut cratons out of the modern DEM with lon/lat bounding boxes, which read as rectangles — jittering the edge of a rectangle still leaves a rectangle. Nothing about a 900 Ma coastline is known well enough to trace, so each craton's radius is modulated by three octaves of 3D noise in the craton's own rotating frame.

`epeiric.py` floods the epicontinental seas the 20 km global grid cannot resolve (the Trans-Saharan Seaway, the Cannonball Sea), because otherwise a label describes a sea the map does not show.

### 5.3 The ocean floor

The largest subsystem, and the one under most active development. Split between `build/seafloor.py` (baked structure) and the fragment shader (per-pixel fabric).

**Baked, per keyframe:**

- **Age-graded depth** from half-space cooling, `depth = 2600 + 350·√(age_Myr)`, with a half-spreading rate of 30 km/Myr and crust older than 190 Myr treated as subducted.
- **A synthesised spreading network.** The reconstruction resolves only a dozen or so ridge arcs in deep time — far too coarse to read as a spreading system, and interpolating distance to that sparse set can only ever give broad smooth swells with no axis you can trace. So `_ridge_network()` joins arcs whose endpoints nearly meet into continuous chains, then offsets each chain at **four self-similar orders**:

  | order | segment | offset | breaks? | what it is |
  |---|---|---|---|---|
  | 1st | 7.0° | ±1.25° | yes | ridge–transform; the fracture-zone makers |
  | 2nd | 2.0° | ±0.40° | yes | overlapping spreading centres |
  | 3rd | 0.65° | ±0.115° | no | non-transform offsets — the axis bends, not steps |
  | 4th | 0.22° | ±0.038° | no | axial crenulation |

  Offset is held at ~0.18 of segment length at every order, which is what makes the axis genuinely self-similar over 1.5 decades. 13 arcs become 269 segments at 300 Ma, mean 1.6° ≈ 180 km — real fracture-zone spacing.

  Offsets come from a **positional hash**, not a RNG, so a chain that persists between keyframes does not re-roll its network and the fracture zones do not shimmer.

- **Segment-scale axial structure.** Melt is delivered to the middle of a segment and starved at its ends, so the crest shoals toward the centre and drops into a **nodal basin** ~1 km deeper at each transform.
- **Fracture zones** as the boundary of the nearest-segment partition — literally the boundary between crust made by one segment and crust made by the next.
- **Trenches** with the outer rise the plate flexes into before it bends down; **seamount chains** smeared along plate motion; **sediment** blanketing near margins; **oceanic plateaus** (Kerguelen, Ontong Java, the Seychelles, Mauritia, Argoland …) back-advected on plate rotations with elevation curves that carry them from emergent island through drowned bank to deep plateau.

**Per pixel, in the shader:**

- **Abyssal hills as tilted fault blocks** — three self-similar fault sets keyed to the shipped across-ridge coordinate, spaced from ~24 km down to ~3.6 km at the axis, with power-law throw and en-echelon breakup. Abyssal hills are not noise: they are blocks cut by normal faults at the axis and carried outward unchanged, which is why real fabric combs in long parallel lines rather than dappling.
- **Pelagic mantling** as a band-limit: sediment buries short wavelengths first, so young crust is sharp and an old plain against a margin is nearly featureless.
- **Submarine canyons** on the continental slope, cut downslope — the opposite anisotropy to the abyssal fabric.

### 5.4 Climate

`render.py`, `climate.py`. Biomes are not painted on by latitude; each frame runs a small climate model.

- Prevailing winds by latitude — tropical easterlies, mid-latitude westerlies, polar easterlies.
- Moisture advected downwind: air recharges over ocean and dries across land, so **continental interiors go arid on their own** and Pangaea grows a genuine desert heart with monsoonal windward margins.
- **Orographic rainfall** and rain shadow — the Atacama and Patagonia fall out of the model, not out of a lookup table.
- Vegetation from rainfall against evaporative demand, so cold dry Siberia is taiga while a subtropical plain on the same rainfall is desert.

Era state (temperature anomaly, ice lines, vegetation, aridity) is literature-informed. **The ice lines are not decoration**: `render.glaciation()` turns the equatorward line into the temperature threshold the shader glaciates at, so each line is a claim about how much of the world was under ice — and `ice_audit.py` checks that claim against the area the app actually draws. Six were corrected the first time that audit ran.

### 5.5 Surface processes

`build_surface.py`. The app knew where the ground was and how much rain fell on it, and nothing about what the water then did. This derives drainage from the topographic lows of the reconstructed terrain weighted by rainfall: narrow incised lows render as channels, broad wet flats as marsh, the same at a coastline as delta plain. Plus substrate (a billion-year-bare shield is not a filling basin) and fetch.

Ancient river courses are not known, so none are drawn from a map. As a check, the same method on the present-day DEM places channels in the real Himalayan valleys draining to the Bay of Bengal.

Lakes are baked separately (`bake_lakes.py`, `bake_present_lakes.py`) and the geologically young ones are handled explicitly: the Great Lakes are ~14 ka old, and interpolating them out of the present frame left them sitting there in the Pliocene, 4 Myr either side of today. A second present-day lake field *without* them is swapped in outside the window they actually occupy.

### 5.6 Events, features and life

- `paleo_tracks.py` — impacts and large igneous provinces are catalogued where we find them *today*, and the crust has travelled. These are reconstructed along **real plate rotations**. The previous approach advected them on the block-matched motion grid, which freezes over featureless ocean and has a poleward bias past 250 Ma, so an ocean crater sat still while its plate moved out from under it.
- `features.py` — volcanic provinces and era labels with age windows. A flood basalt is an eruption for a moment and a **landform** for far longer, so each province stays on the map as long as it stood as high ground. The Deccan still holds up the Western Ghats; CAMP, the largest of them all, was buried in its own rift basins almost as it erupted and is a landform essentially nowhere.
- `life.py`, `add_*_life.py`, `add_present_biota.py` — biomes and the regional fossil record, with terms chosen to suit the period: no grassland before the Cenozoic, and before land plants the terrestrial world is microbial crust and bare regolith.
- `audit_labels_full.py` — systematic label audit across terrain, debut age and drift, because a label must track the *same feature* as it evolves rather than merely sit at fixed coordinates.

### 5.7 Rendering

`web/index.html` holds four GLSL shaders as JS template literals: `VERT`/`FRAG` (globe and map) and `CVERT`/`CFRAG` (clouds). The fragment shader decodes and interpolates the fields, then recomputes temperature, relief, biome colour, water, ice, sky and the ocean fabric per pixel.

---

## 6. Build and deploy

```bash
cd build
python check_shader.py && python build_site.py
```

then commit and push to `main`. GitHub Pages serves `main:/docs`.

Common targeted rebuilds:

```bash
ONLY_AGE=300 python reskin_seafloor.py     # one keyframe, quick visual check
python reskin_seafloor.py                  # _e and _o for all 251 (~40 min)
python build_webdata.py                    # labels, timeline, boundaries, life
```

`stamp_data_version.py` bumps `DATA_V` **before** `index.html` is copied. This is not optional: Pages serves the JSON with `max-age=600` and an ETag, and a returning viewer can sit on a cached copy well past that window. The failure is silent — the app runs perfectly and shows yesterday's data. It has happened three times, on `labels.json`, `plates_time.json` and `life.json`, and each time it looked like the deploy had never landed.

Verify the live `DATA_V` after every push.

---

## 7. Traps

### 7.1 Shader traps — the black globe

Run `check_shader.py` before any shader edit ships. It catches every failure mode that has actually occurred here, all of which present identically: the page loads, the panels and labels render, the console says nothing useful, and the globe is simply black.

- **A backtick anywhere in shader source**, including inside a comment. It closes the JS template literal. This has happened three times.
- **GLSL reserved words as variable names** — `patch`, `flat`, `sample`. The compiler says `'flat' : syntax error` and nothing else.
- **Use before declaration** inside `main()`.
- **Duplicate declaration at the same scope**, and unbalanced comments or braces.

Chain it: `python check_shader.py && <rebuild>`, so a bad shader blocks the build.

### 7.2 Quantisation

An 8-bit channel whose quantisation step is coarser than a texel does not read as a slightly rough field — it reads as a **staircase of flat terraces**, and anything periodic keyed to it draws the terrace *contours*. This produced a right-angled circuit-board maze across the ocean.

Two lessons, both learned the expensive way:

- **Never treat categorical IDs as a continuous field.** Blurring a segment-ID raster and taking its gradient scales the signal by the arbitrary difference in *label number*: a 1↔2 boundary comes out 40× fainter than a 1↔41 one.
- **A distance transform is not a shape until it is band-limited.** Raw EDT level sets follow the pixel lattice, so they draw right angles. Smooth before using them as geometry.

### 7.3 The precision budget

Extra precision beyond 8 bits forces `_o` to lossless WebP, because every scheme's extra channel is a sawtooth and lossy compression destroys it. Measured over 251 keyframes at 2048×1024:

| encoding | total |
|---|---|
| hi/lo 16-bit split, lossless RGBA | 320 MB |
| long-period sawtooth (4°), lossless RGBA | 224 MB |
| lossless RGB, *no* extra precision at all | 124 MB |
| **what ships today (lossy RGB)** | **23 MB** |

All six field types together are 94 MB. **Do not re-attempt the 16-bit ship without new information.**

The answer instead is **companding**: ship `log(1 + d/2.5)` rather than `d/75`. Free, and it moves the quantisation step from a flat 0.29° to 0.034° at the ridge axis — five times finer than a texel — widening to ~1° far out. That gradient is the physics, not a compromise: fabric is cut at the axis and buried by sediment with age.

Corollary that governs the shader: **key every periodic term to the companded coordinate, never the decoded distance.** A quantisation level then advances the phase by a fixed fraction of a cycle everywhere. Only terms that must match a true spatial rate use decoded degrees, and those must be faded out past ~30° where a level spans several noise periods.

### 7.4 Two systems texturing one surface

When detail looks *wrong* rather than *absent* — "mottled", "busy", "not quite combed" — check whether two systems are texturing the same surface. `elevDetail()` was laying isotropic 24 km blobs on the abyss **in the elevation**, where they drive the primary normal, so they beat the anisotropic fabric that only perturbs the normal afterwards. No parameter tuning could have fixed it.

Give each system a band of scales and fade the others out of it.

### 7.5 Anisotropy on a sphere

Elongating noise by compressing the domain along a tangent direction **does not work on a sphere, at any amplitude**. Compressing along `t` means subtracting `t·dot(P·F, t)`, and `dot(P, t)` is identically zero because a tangent is perpendicular to the radius — and its derivative is zero too, since moving along `t` tilts `t` inward at exactly the rate that restores the term. That curvature identity is why an early attempt at domain-stretched lineation came out as isotropic crumple.

Elongation has to come from a scalar field that genuinely varies across the axis (the shipped coordinate), or from smearing along the axis. Both are used, each where it is the better tool.

### 7.6 Never ring-average at the poles

Clamping the sampling radius near the pole makes every pixel poleward of ~88° share one ring value — a uniform disc — and where that ring crosses land it paints polar *ocean* as land. Pole handling is instead: an on-sphere disc filter inside the cap, plain tangent-frame differences outside, both in the east/north basis, with the field band-limited per row in the pipeline (`polar_lowpass`).

---

## 8. Sources

| role | source |
|---|---|
| Plate model | Merdith, A. S. et al. (2021), *Earth-Science Reviews* 214, 103477 · Zenodo 4485738 · CC-BY 4.0 |
| Paleo-DEMs | Scotese, C. R. & Wright, N. (2018), PALEOMAP PaleoDEMs · Zenodo 5460860 · CC-BY 4.0 |
| Present plate motions | NNR-MORVEL56 (Argus, Gordon & DeMets, 2011) |
| Present boundaries | Bird, P. (2003), PB2002 · *G³* 4(3) |
| Sea-floor depth | Parsons & Sclater half-space cooling; von Kármán roughness model for abyssal hills |
| Future climate | Farnsworth, A. et al. (2024), *Nature Geoscience* 17, 1109–1116 |
| Solar model | Gough, D. O. (1981), *Solar Physics* 74, 21–34 |
| Impacts | Impact Earth database (Osinski et al.) and Schmieder & Kring (2020) |
| Intervals | ICS chart v2024/12 |
| Illustrations | PhyloPic — CC0, Public Domain Mark or CC-BY only; contributors credited individually |
| Software | pyGPlates / GPlates; three.js + GLSL |

---

## 9. Known limits

- **Deep time and deep future are interpretive.** Pre-540 Ma and future frames are authored reconstructions — real cratons rotated into supercontinent fits. Treat this as a visualisation of the published record, not a precise map.
- **The synthesised spreading network is plausible, not surveyed.** The pattern is real; the particular line is not. Same standing as the modelled rivers.
- **27 tracked labels** still sit on the wrong medium for more than a third of their span. Root cause is a Merdith-vs-Scotese frame mismatch; the fix needs per-region rather than global-rigid frame correction.
- **Hotspot chains are generic**, smeared along plate motion, rather than modelled per plume with an explicit island-formation-and-subsidence history.
- **Present-day biota** have their own regional cards for 49 of 148 labels; the rest fall back to broader assemblages.
