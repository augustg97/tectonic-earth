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
| `_e` | elevation | 4096×2048 | signed-sqrt encoded, so precision concentrates near sea level — the coastline is the one contour that must interpolate cleanly. Matches the 6-arc-minute source DEM, so more pixels would only interpolate |
| `_r` | rainfall | 1536×768 | smooth, so it costs little |
| `_m` | plate motion | 128×64 | R = east, G = north, B = confidence |
| `_w` | lake depth | 2048×1024 | baked standing water, sqrt-encoded metres |
| `_d` | surface process | 2048×1024 | drainage, substrate, fetch |
| `_o` | ocean structure | 2048×1024 | R = **crustal age**, log-companded over 0–52° of spreading (190 Myr, the oldest surviving ocean crust); G/B = spreading direction from the age gradient, with confidence in its length |

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

The largest subsystem. It is built on **crustal age**, and the reason that matters is worth stating plainly, because the model it replaced was wrong in a way no amount of tuning could reach.

The old model asked: *how far is this point from the nearest spreading ridge right now?* Nature asks nothing of the sort. Every parcel of ocean crust was created at a ridge at a particular moment and has been carried away ever since, and what it carries is a frozen record of the ridge **as it was**. Three things followed from getting that wrong, and all three were visible on screen:

- **Fabric orientation was wrong away from the axis.** Abyssal hills lie parallel to the *isochron*. Keyed to the present ridge they swept round it in arcs, where a real chart combs dead straight.
- **Fracture zones could not persist.** The scars that cross a whole basin on a real chart are *material lines* — one transform's entire history, frozen into the plate. Ours were Voronoi boundaries of the *present* segmentation, rebuilt from nothing every keyframe, so they could never be older than the frame they were drawn in.
- **The coordinate's gradient collapsed with range**, which marbled the far field into contour loops and then left it blank once that was capped. Real abyssal hills stay ~5 km apart from the axis to the trench; only their *amplitude* decays, as sediment buries them. Distance conflates spacing with amplitude. Age does not — its gradient is 1/(spreading rate) and does not decay.

**Two sources of age** (`crustage.py`, `realage.py`), fused in the gradient domain (`oceanage.py`):

| | |
|---|---|
| `crustage.py` | Isochron model. Crust at time T with age A sat on a ridge at T+A, so carrying that ridge forward to T on each flank's own plate *is* the isochron of age A. Matched per plate — a global nearest-isochron search puts a 180 Myr line beside a 20 Myr one and tears the field. |
| `realage.py` | The surveyed grid (Müller et al. 2019) carried backwards. A cell whose age today is A0 existed at T iff A0 > T. |

Measured against the surveyed grid the isochron model correlates only **0.41** (median error 33 Myr) — Merdith is built to get *continents* right across a billion years, and its Cenozoic ocean detail is coarser than a model made for the purpose. So real data is used where real data exists, and the division is forced by the geology rather than chosen:

| T | surveyed | | T | surveyed |
|---|---|---|---|---|
| 0 Ma | 55% of globe | | 100 Ma | 17% |
| 40 Ma | 38% | | 150 Ma | 4% |
| 80 Ma | 21% | | 180 Ma | 0.7% |

Past ~180 Ma essentially no ocean crust survives, so there is nothing left to reconstruct and the model carries it alone. The two are blended by spreading the *difference* rather than the values — preferring one where it exists would put a step of tens of Myr along the edge, and since depth goes as √age that step would draw itself on the sea floor as a wall.

**The future** is not extrapolated. Asked for a negative time pyGPlates does not refuse — it runs Merdith up to 250 Myr past the end of the model and returns a complete, plausible-looking field in which every number is invented. Instead the future carries today's age field on the same rigid per-group rotations the future *terrain* already uses, plus elapsed time; unclaimed ground is new ocean, young.

**What falls out of age:**

- **Depth** — half-space cooling on real age, so basins sit at the depths their crust has earned.
- **Fabric orientation** — the isochron tangent, correct everywhere.
- **Fracture zones** — an age offset measured *along* the isochron, over a finite baseline (the tangential component of a gradient is identically zero; the first version of this returned nothing at all for exactly that reason).
- **Sediment** (`sediment.py`) — pelagic accumulation is rate(latitude) × age, which could not be computed at all before. Against the turbidite wedge off the margins, and against the 50–300 m of relief it has to bury. Where accumulation wins, the floor is a plain. Calibrated to published thickness grids: mean 451 m, plains 17%, hills the majority. Verified by the Bengal and Indus Fans appearing unprompted either side of India.
- **Seamounts** (`seamounts.py`) — a population of discrete cones, power-law heights, born at ridges, subsiding with their plate, planed into guyots where they reached the surface. ~6,300 above the 1.2 km this grid can resolve.

**Still baked from the ridge network**, and correctly so — these describe where the ridge is *now*: the axial valley, the along-strike segment structure (inflated centres, nodal basins at segment ends), trenches with their outer rise, and oceanic plateaus.

**Per pixel, in the shader:** abyssal hills as three self-similar sets of **tilted fault blocks** keyed to the companded age coordinate, with power-law throw and en-echelon breakup; submarine canyons cut downslope on the continental slope.

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

The same thing happens to the **elevation** field, and for longer it was blamed on the fabric. Measured on the shipped `_e`: only 27 of 256 levels are used below 3.5 km and **75% of adjacent abyssal cells are identical**, so the abyss is a staircase of terraces averaging four texels wide, and the hillshade draws their *contours* — closed loops following the level sets of a smooth field. That is the "marbling" several rounds of fabric tuning chased, and no fabric parameter could have reached it.

**Dithering at encode does not work**: measured, WebP's lossy path destroys ±½-LSB noise of every kind (white, blue, TPDF) and re-terraces on decode, at identical file size.

What does work is that the artefact is **exactly characterised**, so it can be undone at read time. Quantisation error is bounded by half a level per sample, hence one level per *difference*, and one level here is a known function of depth (`dz/dlevel = 2·|d|·Z_RANGE·2/255`, about 89 m at 4 km and 109 m at 6 km). Soft-threshold the residual between a narrow and a wide gradient at one level — the standard shrinkage rule, but with an exact noise bound rather than an estimated one — and the staircase goes completely.

The corollary matters more than the fix: **shrinkage lets the smoothing window get wider, not narrower.** The old mitigation blended 40% of a 2.9-texel gradient and was capped there because widening it erased fracture zones. Under shrinkage the test is amplitude, not scale, so an 8-texel window is safe — and *better*, because a wider window makes a terrace's contribution to the regional slope smaller, so the residual at a terrace edge lands closer to exactly one level and is removed more completely, while a fracture zone (a symmetric trough the wide window reads as no slope at all) keeps nearly its whole sharp gradient.

### 7.3 The precision budget

Extra precision beyond 8 bits forces `_o` to lossless WebP, because every scheme's extra channel is a sawtooth and lossy compression destroys it. Measured over 251 keyframes at 2048×1024:

| encoding | total |
|---|---|
| hi/lo 16-bit split, lossless RGBA | 320 MB |
| long-period sawtooth (4°), lossless RGBA | 224 MB |
| lossless RGB, *no* extra precision at all | 124 MB |
| **what ships today (lossy RGB)** | **23 MB** |

All six field types together are 94 MB. **Do not re-attempt the 16-bit ship without new information.**

The answer instead is **companding**: ship `log(1 + d/2.5)` rather than a linear ramp. Free, and it moves the quantisation step to **0.030° at the ridge axis — 3.4 km, which is abyssal-hill spacing** — widening to ~1° far out. That gradient is the physics, not a compromise: fabric is cut at the axis and buried by sediment with age.

Full scale is **52° of spreading**, not 75. That was the right number when the coordinate was distance (the far side of Panthalassa); it is wrong now it is age, because ocean crust does not survive past ~190 Myr and 190 Myr at 30 km/Myr is 51.3°. Two other constants were pinned to the old range — the `crustAge` normalisation and `ACR`, the radians-to-coordinate factor both domain stretches are built on — and would have silently rescaled the entire fabric.

Corollary that governs the shader: **key every periodic term to the companded coordinate, never the decoded distance.** A quantisation level then advances the phase by a fixed fraction of a cycle everywhere. Only terms that must match a true spatial rate use decoded degrees, and those must be faded out past ~30° where a level spans several noise periods.

### 7.4 Two systems texturing one surface

When detail looks *wrong* rather than *absent* — "mottled", "busy", "not quite combed" — check whether two systems are texturing the same surface. `elevDetail()` was laying isotropic 24 km blobs on the abyss **in the elevation**, where they drive the primary normal, so they beat the anisotropic fabric that only perturbs the normal afterwards. No parameter tuning could have fixed it.

It has now happened three times, and the pattern in the *fix* is as instructive as the pattern in the fault:

| the two systems | the tell | why the first fade was wrong |
|---|---|---|
| `elevDetail`'s 24 km octave vs the abyssal fabric | mottling across the combing | faded on **depth** (1800–3400 m), so it stood at full strength on ridge flanks and upper slopes — 15% of the sea floor and the most conspicuous 15%. The reason to fade was never depth: it is that below the shelf break the ocean-structure system *owns* the 5–30 km band. Fade on the shelf break. |
| the sea surface's sun glint vs the sea floor | pale blue-white speckle over open ocean (measured: 892 blobs above L=115 in one frame, at exactly base + spec + glint) | the specular normal was built from `nrm`, which by that point carries the whole abyssal-hill fabric — so a ridge four kilometres down lit a highlight on the water above it. **A sea surface is flat no matter what the bathymetry does under it.** |
| the surface's own brightness ripple (11 km) vs the fabric | fine grit over the abyss | full strength everywhere; now a quarter of it over deep water, where there is most sea floor to see and least reason to look at the water |

**Give each system a band, and fade the others out of it by the variable that says whose band it is** — not by whichever variable happens to correlate.

### 7.5 A coordinate-keyed periodic term drifts in wavelength

Keying the fault set to the companded age coordinate solves terracing and creates a worse problem, because the companding is by construction non-linear. `phA = crustCo·40` has a spacing of `40/((D0+d)·K)` cycles per degree — **21 km at the axis, 90 km at ten degrees out, 190 km at twenty**. Abyssal hills are 2–8 km. Past a few degrees this had stopped being a fault set and become a system of enormous wandering ridges, and *that* — isolated by switching it off at globe zoom — is the squiggle maze read as "marbling" for several rounds. It is not a modulation-index problem out there; the carrier itself is wrong by an order of magnitude.

The shipped coordinate cannot carry a uniform fine fabric to the far field, and no cap fixes that: keyed to the companded coordinate the wavelength drifts, keyed to true distance one 8-bit level is 0.66° out there — nearly four wavelengths — and it terraces. So the far field's fabric has to come from **position**, whose scale is whatever we choose, uniformly, everywhere; all the shipped field supplies is the *direction*, which is smooth and well-resolved and exactly what it is good at. Periodic sets are kept only where the coordinate genuinely resolves them, within a few degrees of the axis, which is also the only place real scarps are unmantled and sharp.

### 7.6 A resolution change is not one constant

Doubling the elevation grid to 2048×4096 in July 2026 touched about fifteen constants across three files, and the failure mode is that most of them look fine when you skip them.

**Filter radii are in cells, so they encode either a width in the WORLD or a limit of the RASTER, and only you know which.** Every filter in `seafloor.py` is the first kind — a fracture zone is 0.26°, a turbidite apron 5°, a continent more than 3° across — so all of them had to double. `render.smooth_bathymetry` is the second kind, band-limiting to what the grid can hold, so it correctly stays put and its footprint halves in angle (5 cells is 49 km at 9.8 km cells against 137 km at 19.5 — and the 90 km of bathymetry that buys back is the point of the exercise).

**The gradient baseline should NOT follow the grid**, which is the counter-intuitive one. The tempting move is to halve `da` and "use" the new resolution; measured, it makes the sea floor worse. Quantisation error is bounded per *sample*, so it does not shrink when the baseline does, while the true relief across the baseline does: abyssal slopes run 2–5 m/km, so over 35 km a real difference is 75–180 m against an 89 m quantum, and over 23 km it is 50–120 m — which the shrinkage then discards as encoding noise. The rendered abyss went flat while the field itself carried *more* at every band (10–30 km: 61 m against 41; 30–80 km: 154 against 87).

**And `gE` is metres, not a slope.** The effective vertical exaggeration is `(2·da in metres)/vex`, so `da` and `vex` are only meaningful together — as are every other constant compared against a gradient (the shrinkage's steep-slope guard, the fabric's flat-ground gate, the canyon's tilt gate). Change one, change all five.

The models that write *into* the grid are a separate question and were deliberately left: `_ridge_geometry` at 1024×2048 and `oceanage` at 512×1024 are smooth fields that get upsampled, and raising `oceanage` costs 64 s a keyframe against 0.5 (it scales badly), which is 4½ hours for structure that is smooth between its samples anyway.

### 7.7 Vertical exaggeration is not one number

`nrm = normalize(vec3(-gE, gN, 300))` with `gE` in metres over a 1.8-texel baseline is a **59× vertical exaggeration**. On land that is right and always has been — it is what gives a mountain belt its bite at global zoom. Under water it is far too much, and measurably so: simulating that gradient on the shipped field gives a median submarine tilt of **27.6°** and a p90 of **53.5°** on ground whose true slopes are a fraction of a degree. Every under-resolved one-texel step becomes a hard facet, and together they are the granular black hatch that outlined every rise, arc and margin.

Two things follow. First, the sea floor takes its own scale (780, about 23×) — trenches stay legible at 78° while texel-scale noise drops from 27° to 11°. Second, **60% of that content is not quantisation**: it survives shrinkage because a 20 km grid genuinely cannot describe a continental slope, and delivers it as a staircase. Where the *wide* gradient is already large, the regional slope is the trustworthy description and the texel-scale departure from it is sampling noise; where the wide gradient is small, a large residual is a real narrow feature. Scaling the residual by the wide gradient separates the two cases without a global flattening.

### 7.8 Anisotropy on a sphere

Elongating noise by compressing the domain along a tangent direction **does not work on a sphere, at any amplitude**. Compressing along `t` means subtracting `t·dot(P·F, t)`, and `dot(P, t)` is identically zero because a tangent is perpendicular to the radius — and its derivative is zero too, since moving along `t` tilts `t` inward at exactly the rate that restores the term. That curvature identity is why an early attempt at domain-stretched lineation came out as isotropic crumple.

Elongation has to come from a scalar field that genuinely varies across the axis (the shipped coordinate), or from smearing along the axis. Both are used, each where it is the better tool.

### 7.9 Never ring-average at the poles

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

---

## 10. Where the ocean model stands

The sea floor was rebuilt onto crustal age in July 2026. What that fixed, and what it did not:

**Fixed.** Fabric orientation everywhere (isochron tangent rather than present-ridge distance). Fracture zones that persist, because an age offset travels with the crust. Depth by basin, from real age. Abyssal plains with sharp edges, from a sediment thickness that competes against the relief it buries. A seamount population instead of smeared streaks. Far-field marbling, which was a modulation index above 1 — the perturbation's gradient exceeding the carrier's, crossing over at 13° from the axis.

**Fixed in the July 2026 reference round** — the round measured against the Google Earth frames rather than tuned by eye. The measurements are in §7.2, §7.4, §7.5 and §7.6; the outcomes:

| | before | after | reference |
|---|---|---|---|
| ocean RGB | 22 · 58 · 84 | **37 · 46 · 95** | 37 · 46 · 95 |
| R/B · G/B | 0.27 · 0.70 | **0.39 · 0.48** | 0.39 · 0.48 |
| saturation | 0.741 | **0.608** | 0.617 |
| mean luminance | 54.8 | **59.2** | 59.4 |
| energy below 12 km | 12–24% | **2.9–3.3%** | 2.4–5.7% |
| energy 12–30 km | 13–27% | **16–27%** | 32–41% |
| local grain coherence | 0.32–0.39 | **0.49–0.55** | 0.40–0.50 |
| spurious bright blobs, one frame | 892 | **3** | — |
| elevation grid | 1024×2048 | **2048×4096** | — |
| `_e` across 251 keyframes | 18.4 MB | **57.4 MB** | — |
| all fields | 94 MB | **145 MB** | — |

Frame time is unchanged (67.7 ms against 66.6–67.3 for the previous shader, at 1400×900 and 1.6 km/px, measured on an idle machine — earlier readings taken while a reskin was running are not comparable). The abyssal fractal dropped from five octaves to three, which paid for the third grain order: its 15 km and 7 km terms had weights of 0.07 and 0.02 because `licGrad` owns that band now, and they cost six noise evaluations per fragment to contribute almost nothing.

The colour change is the one worth restating, because it was a wrong *model* rather than a wrong value. The old ramp interpolated between three different hues with depth. Binning the reference's ocean by luminance shows it does nothing of the sort: from the 1st to the 75th percentile its R/B holds at 0.37–0.41 and G/B at 0.46–0.52 while brightness rises 40%. It is **one colour, shaded** — which is also the physics, since below the photic zone nothing reflects off the floor and all you see is the water column's own attenuation. A hue ramp with depth is a cartographic convention, not an appearance.

The same argument fixed the shelf: bright shallow water needs a bright *floor* as well as a shallow one, and bottom return is exponential in depth, not a smoothstep from 850 m. Under the old ramp every seamount summit within half a kilometre of the surface was painted shelf-blue — 228 of them in the open ocean at 0 Ma.

Being exponential, though, it then has to be fed a depth the grid can support: `exp(z/70)` changes seventeenfold between 100 and 300 m, and the shipped field carries 206–303 m rms of texel-scale content in exactly that band. So neighbouring shelf pixels landed on wildly different parts of the ramp, and the palette drew a dark speckle inside pale blue around every margin. The colour now follows the **regional** depth (this pixel against the four taps eight texels out, already fetched for the dequantisation) and fades back to the true value above 40 m, where the surf zone and the reef flats want the ramp sharp. Relief still comes from the hillshade — this only stops the palette reporting detail the data does not have.

**A fifth instance, and the one that finally explained the seamounts.** The concentric rings on every cone were never quantisation — they are finer than a texel, which no 8-bit terrace can be. They were the **submarine-canyon system**, whose gate was "tilted ground between 200 m and 3.5 km" and therefore fired on every seamount flank; and because the canyon domain subtracts DEPTH as its potential, on a cone — where iso-depth lines are circles — it drew the depth contours. A canyon is cut by turbidity currents carrying sediment off a continental shelf, so the test is whether there *is* a shelf above the slope, and the four wide taps answer it directly. Its probe was also stepping a fixed angle rather than a fraction of a noise cell, so `k1` and `k0` were decorrelated samples and `abs(gully)*1.15` could exceed 1 — driving the colour negative and printing the hard black band along every margin.

And a fourth instance of §7.4, found by checking the Cryogenian: **the sea-floor normal was shading pack ice**, so at the snowball peaks the whole world was embossed with the abyssal fabric of the ocean beneath it. Pack ice is a raft; the visible surface owns its own normal. Grounded ice over shallow bedrock — most of Antarctica — still takes the relief under it, because there the relief *is* the surface.

**Fracture zones, and the channel that was not needed.** A real chart's abyssal-hill provinces are bounded by fracture zones and change character across each one; ours ran continuously across every scar, which was most of why the ocean read as one uniform field rather than a set of terrains. The obvious fix is a fourth channel on `_o`, and it is the wrong one: **the signal is already in the R channel**, because a fracture zone *is* an age offset. Stepping along the isochron and differencing the age spikes on a scar and is near zero elsewhere — the same computation `oceanage._derive` does in the pipeline, for eight texture reads and no extra bytes.

Two corrections were needed, both found by painting the detector's own output over a region with textbook scars:

- Scaling against the *assumed* spreading rate lit up every continental margin and almost no scars, because the analytic rate presumes 30 km/Myr everywhere and anywhere spreading was slower the ordinary gradient exceeds it. Measure the real denominator.
- It then traced the ridge axis, because the denominator is a symmetric difference across the isochron and at the axis age is a minimum — the samples come back equal and the ratio diverges. Floor it, and fade the detector in past a couple of degrees, where a fracture zone stops being an active transform and becomes the frozen trace this is for.

**But the limit was the age grid, not the channel.** Rendering the fracture-zone field over the equatorial Atlantic at 512×1024 against 768×1536 settles it: the coarse grid shows the ridge trace and essentially nothing else, the fine one shows the Romanche–Chain–Vema family as the long continuous parallel scars a chart has. A fracture zone is a step a few tens of km wide, and a 39 km cell smooths it away before anything downstream can see it. `seafloor.py` now asks `oceanage` for 768×1536 — 4.8 s a keyframe once the one-time pyGPlates load is paid — which sharpens the baked troughs as well as the shader's test for where the fabric should break.

**Not fixed, and known.**

- **Seamounts are not clustered along plume tracks.** They are seeded by crustal age, so they scatter where a real ocean shows chains — Hawaii, Louisville, the Cook–Australs. The `hotspot` input to `seamounts.field()` exists and is not wired up.
- **Deep-time sea floor cannot be made accurate**, only structurally correct. That crust was subducted; there is no record. The isochron model correlates 0.41 with the surveyed grid where both exist, which is why the surveyed grid is preferred wherever it survives.
- **The axial valley and nodal basins still key off the ridge network**, not age — deliberately, because they describe where the ridge is *now*.
- **Aseismic ridges and marginal basins** (Ninetyeast, Walvis, the Philippine Sea) are absent or generic.
- **The fabric is a synthesised grain, not surveyed hills.** Its aspect, spectrum and coherence are measured against the reference rather than guessed, and it varies with spreading rate, sediment burial, the baked field's own roughness and — since the fracture-zone work below — with the province it sits in. What it still is not is a survey.
- **Coastlines and shelf breaks stay jagged at texel scale.** At 9.8 km the grid matches the source PaleoDEMs exactly, so there is nothing further to extract: Google Earth's near-shore bathymetry is 15 arc-seconds, some twenty times finer. This is a data limit, not a shader one, and it is where the remaining visible difference lives.

---

## 11. Reference material

`Deep Time Maps and Resources/` (not in git — large images) is the standard this work is measured against.

- **`Google Earth Examples/`** — five screenshots that define "done" for the sea floor. The key finding from them: below the shelf break Google Earth's ocean carries almost **no colour variation**; the whole abyss is one blue-violet and every bit of visible detail is hillshade. An earlier round concluded the opposite ("we need more contrast") and was wrong.
- **Esri Ocean Basemap** — https://www.arcgis.com/apps/mapviewer/index.html?webmap=67ab7f7c535c4687b6518e6d2343e8a2 · GEBCO-based, a second reference alongside Google Earth.
- **Process diagrams** (`.webp`) — continental-margin anatomy, subduction, back-arc basins, slab pull, atoll formation, the supercontinent cycle, the oceanic crust age pattern. The margin diagram is why the canyons are dendritic.
- **~76 deep-time paleogeographic maps** with Ma dates (Scotese / DeepTimeMaps). **Not yet audited against our reconstruction** — the user has asked for a full audit of these as separate work.

`HANDOFF.md` carries the live state, the measured facts, and the work queue for continuing the sea-floor loop in a fresh session.
