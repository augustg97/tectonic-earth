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

**Two rotation models are in use, and that is deliberate.** Boundaries need resolved topologies, which only Merdith provides. *Feature tracks* — labels, craters, LIPs, the epeiric seas and the hotspot chains — instead ride **Scotese's PALEOMAP rotations** (`paleo_tracks.py`), because that is the frame the PaleoDEM terrain is drawn in, and tracking in anyone else's places a name on one Earth and draws it on another. Until July 2026 the tracks were Merdith's and the gap was patched with a rigid global longitude shift per age (`frame_offset.py`, now deleted — with one frame there is nothing left to correct and applying it would inject the error it used to remove).

Four independent measurements of that switch:

| | before | after |
|---|---|---|
| land-today points landing on abyssal plain (53 points × 10 ages) | 20% | **5%** |
| labels disagreeing with the terrain under them, ≥⅓ of their span | 62 | **41** |
| labels moving more than 15° in one 5 Myr step — impossible for crust | 12 | **6** |
| per-feature medium score, mean over the 124 features the build tracks | 0.819 | **0.971** |

The last is the one that matters, because an average can hide a tail. `Deep Research/modeling/regression_gate.py` scores **every** tracked feature on **its own** age window under both frames and reports the individual outcome: 54 improved, 67 unchanged, 3 down by ≤0.08, **none** a true regression. That harness is the general instrument, not a one-off — §7.10.

Boundaries are derived by **segmenting the surface into plates first and taking the edges afterwards**. An earlier version thresholded a strain field and thinned it, which can only ever give fragments — a threshold crossing is a patch, and thinning a patch gives a broken crest. Real boundaries are not features in their own right; they are the edges between plates, so they are continuous and closed by construction.

**Measured motion** (`motion.py`) — two elevation keyframes are the same crust some millions of years apart, so block-matching one against the next recovers how far each patch of surface travelled. Matching uses a ±15 Myr half-baseline — a 30 Myr window — because over a single 5 Myr step a plate moves well under one grid cell, which integer block-matching cannot resolve at all.

Where there is no structure to match — bare abyssal plain — **no motion is claimed** rather than invented. This matters downstream: an early attempt to find ridges by thresholding this field's divergence marked scattered noise as ridges, precisely because the field is silent by design over the open ocean.

### 5.1b The future series

The present DEM carried by rigid per-group rotations toward `GROUP_TARGET`. Two things about it are worth stating because both were wrong until July 2026.

**The targets are packed, not authored-raw.** `future_grid` resolved two groups landing on the same ground with `out = np.maximum(out, z)` — high ground wins — so the lower of the two was deleted, and what got deleted was coastal plain, shelf and continental interior. Measured: land **148 → 93 Mkm²** across 250 Myr, a 37% loss, against 5.5% for a rotation that conserves area by construction; ground below 1 km fell 45% while land above 2 km stayed flat. Instrumenting the claim masks pinned it: at +250 Myr **53.3 Mkm² of land sat on top of other land** against a total deficit of 58.0, so 92% of the loss was groups interpenetrating and nothing else.

No collision rule fixes that — whichever cell you keep, the other has nowhere to go. `_packed_targets` instead treats each group as a disc of its own land radius and relaxes the *authored* targets until they only touch, mass-weighted (so a small block docks against a large one rather than shoving it aside) and sprung back toward the authored arrangement (so what changes is the packing, not the reconstruction). Raw land now runs **150.5 → 133.1 Mkm², −11.6%** against a 5.5% rasterisation floor, land above 1 km is flat at 29.9 → 29.4, and mean land elevation rises 56 m instead of 212.

The same relaxation fixes the separate finding that the assembly ended too tight: **r90 60° → 76.6°**, against PALEOMAP's own 76°.

### 5.2 Paleogeography

Three eras, three sources (`build_fields.py`):

- **Phanerozoic 0–540 Ma** — Scotese & Wright PALEOMAP PaleoDEMs, 6-arc-minute, straight through.
- **Future 0 → +250 Myr** — the *present* DEM rigidly rotated by plate group. At age 0 every rotation is the identity, so the future series begins as an exact copy of the present frame, inherits its full detail, and leaves no seam.
- **Precambrian 540–1000 Ma** — generated cratons (`precambrian.py`), blended onto the real 540 Ma DEM across the youngest 60 Myr so the handoff is continuous rather than popping.

Precambrian coastlines are **generated, not copied**. An earlier version cut cratons out of the modern DEM with lon/lat bounding boxes, which read as rectangles — jittering the edge of a rectangle still leaves a rectangle. Nothing about a 900 Ma coastline is known well enough to trace, so each craton's radius is modulated by three octaves of 3D noise in the craton's own rotating frame.

`epeiric.py` floods the epicontinental seas the 20 km global grid cannot resolve, because otherwise a label describes a sea the map does not show. **The climate solve sees the carved terrain, not the raw DEM** — it did not until July 2026, so every seeded sea changed the coastline without making the air over it any wetter. Feeding it in raises rainfall on land that is still land by 17% at 240 Ma, the deep Pangaean interior by 11%, and the ground within a few cells of the new coast by 13%. Global mean rainfall *falls*, which is not a contradiction: 6% of the grid moved from land, where this model reports rainfall, to sea, where it reports almost none. It carried two — the Trans-Saharan Seaway and the Cannonball Sea — and therefore reached 50–105 Ma and nothing else, which left the interval where the reconstruction is *worst* for shelf sea with no seeded water at all.

**Measured against Deep Time Maps (Blakey), an independent reconstruction, at 240 Ma we drew 1.8% shallow sea against his 8.0%, and 93% of everything he draws as shelf sea was dry land in ours.** That was also the whole of the +5 to +9 pp land *excess* at 150–240 Ma: never extra continent, always missing sea. Two mechanisms close it.

- **Eight named Triassic–Jurassic basins**, each with stratigraphic control and its own transgression curve: the Germanic (Muschelkalk), Zechstein, Sverdrup, West Siberian, Sundance, Russian Platform, Neuquén and the Alpine Tethyan platforms. An Arabian carbonate platform and an Australian northwest shelf were entered here first and taken out again the same day — they are *margins*, not flooded interiors, so they duplicated the shelf mechanism below and over-flooded 220 Ma by 3.3 points. **What belongs in this table is water standing on continental interior.**
- **A Pangaean shelf**, which is the other two-thirds. A shelf break sits 130–200 m down and tens to a couple of hundred km offshore, so a 20 km grid samples it in one or two cells and the coastline lands on the slope.

**The shelf's target comes from our own data, not from Blakey.** Measured on the raw PaleoDEMs the shelf fraction jumps 8.6% → 4.5% → 3.0% → 6.3% → 1.6% → 8.2% → 13.8% across 170, 180, 200, 220, 240, 250 and 260 Ma, while eustatic sea level slides smoothly from 83 m to 0. Shelf area does not do that: a seven-point swing between two adjacent frames is how the source grids were authored. So each frame is judged against the **median of its own ±70 Myr neighbourhood**, and the mechanism supplies only the shortfall. Blakey is then used to *score* that target, never to set it — mean absolute error 0.68 pp over 150–250 Ma.

Two things the solver had to learn, both from measurement:

- **The weight sets which ground floods, not how deep.** Blending toward a shelf depth in proportion to a weight shaves two metres off everything near the coast at weight 0.02, so any land already within two metres of sea level becomes "shelf" — the response was a staircase, stepping 6.3% → 11.2% in one increment. The weight is now an elevation ceiling, and area grows smoothly with it.
- **Flood only if it helps.** On some frames the smallest expressible flood still overshoots: the 220 Ma grid carries ~5% of the globe as coastal land within *fourteen metres* of sea level. Where flooding would land further from the target than leaving it alone, the frame keeps what it has — which is right anyway, because land that close to sea level is the grid being vague about a coastline, not a shelf waiting to be revealed.

| shelf sea vs Blakey | before | after |
|---|---|---|
| 150 Ma | −2.6 pp | **−0.7** |
| 180 Ma | −3.6 | **−0.7** |
| 200 Ma | −5.0 | **−0.9** |
| 240 Ma | −6.4 | **−0.4** |
| **mean over 150–250 Ma** | **2.80 pp** | **0.70 pp** |

No age was made worse, and the 0 Ma control is untouched at 9.0%. The Palaeozoic runs the *other* way — we draw 3–11 pp more shelf than Blakey from 260 Ma back — and is deliberately left alone: that is an open disagreement between two published reconstructions, not a defect to tune out.

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

- `paleo_tracks.py` — impacts, large igneous provinces, labels, the epeiric seas and the plume chains are catalogued where we find them *today*, and the crust has travelled. These are reconstructed along **real plate rotations** — Scotese's PALEOMAP, the frame the terrain itself is drawn in (§5.1). The previous approach advected them on the block-matched motion grid, which freezes over featureless ocean and has a poleward bias past 250 Ma, so an ocean crater sat still while its plate moved out from under it.
- `provinces.py` — the biogeographic province each label sat in, at every age it is drawn, emitted as runs. What stopped 235 of 336 cards showing one global list; see §9.
- `hotspots_cat.py` — the 53-plume catalogue and the subsidence law that turns it into islands, atolls and guyots; see §10. Both this and `provinces.py` are two-line bridges to `Deep Research/modeling/`, which is stdlib-only on purpose so `build/` can import it rather than keep a second copy that drifts.
- `features.py` — volcanic provinces and era labels with age windows. A flood basalt is an eruption for a moment and a **landform** for far longer, so each province stays on the map as long as it stood as high ground. The Deccan still holds up the Western Ghats; CAMP, the largest of them all, was buried in its own rift basins almost as it erupted and is a landform essentially nowhere.
- `life.py`, `add_*_life.py`, `add_present_biota.py` — biomes and the regional fossil record, with terms chosen to suit the period: no grassland before the Cenozoic, and before land plants the terrestrial world is microbial crust and bare regolith.
- `audit_labels_full.py` — systematic label audit across terrain, debut age and drift, because a label must track the *same feature* as it evolves rather than merely sit at fixed coordinates.

### 5.7 Rendering

`web/index.html` holds four GLSL shaders as JS template literals: `VERT`/`FRAG` (globe and map) and `CVERT`/`CFRAG` (clouds). The fragment shader decodes and interpolates the fields, then recomputes temperature, relief, biome colour, water, ice, sky and the ocean fabric per pixel.

---

## 5.8 Loading

Fields are fetched **when they are wanted**, not up front. The loader used to await all 1,506 of them — six fields at each of 251 keyframes — before the globe appeared: measured, **148.8 MB and 17.9 s on localhost with a warm cache**, which is fetch and decode alone, before a byte crosses a network. What the opening frame needs is the keyframes it interpolates between: 12 files, about a megabyte. Time to a usable Earth went **17.9 s → 0.37 s**, and the render is bit-identical (same SHA-1 on a pinned-`uTime` capture).

Three things already in the architecture made that a loader change rather than a rewrite, and they are worth preserving:

- `bindTextures()` is written `if(ea) … if(eb||ea)`, so a keyframe that has not arrived keeps the previously bound texture instead of binding null.
- `getTex()` creates GPU textures lazily behind an LRU cap, so residency was never tied to how many images were in memory.
- every CPU-side reader of the elevation raster goes through `elevField()`, which returns null for a frame it does not have — and every caller already handled that, because a `_w` or `_o` file has always been allowed to be missing.

The background fill re-centres on every completion: it asks each time for the nearest keyframe to wherever the viewer is **now**, so scrubbing re-aims the queue instead of waiting out a plan made before they moved. Four concurrent — enough to saturate a connection, few enough that a frame someone is waiting for is not stuck behind speculative ones. A cold jump to an unfetched age costs about 0.8 s locally, during which the previous age stays on screen.

`FIELD_V` (bumped by hand, unlike `DATA_V`) busts the texture cache when the fields change but keep their names — as they did when the elevation grid doubled.

## 6. Build and deploy

```bash
cd build
python check_shader.py && python build_site.py
```

then commit and push to `main`. GitHub Pages serves `main:/docs`.

`build_site.py` now **runs the validators first and refuses to publish if one moved backwards**. They are read-only and take a few seconds:

```bash
python audit_all.py           # all of them
python audit_all.py --quick   # skip the pyGPlates ones (~2 min)
```

| check | baseline | what it catches |
|---|---|---|
| `audit_cards` HIGH / MED | 0 / 0 | factual errors, unhedged contested claims, date drift, coverage gaps, anachronistic vocabulary |
| `audit_label_windows` | 2 | a label drawn when the entity it names did not exist |
| `audit_curated_biota` | 10 exceptions, 0 conflicts | a curated locality the province model would overwrite, or one whose flag disagrees with what it is |
| `climate_audit` | 1 (an INFO check that PASSES) | the GMST/CO₂/O₂ table against PhanDA and Krause |
| `ice_audit` | 0 of 23 outside range | drawn ice area against the literature, per keyframe |
| `regression_gate` | 0 true regressions | a feature the frame switch made worse |

The baselines are not all zero and should not be — two label windows are genuine open disagreements about when Gondwana and Kazakhstania become identifiable. The rule is that **none of them may move backwards**; when one legitimately improves, tighten the baseline in the same commit, so the ratchet turns one way only. `SKIP_AUDIT=1` overrides, deliberately awkwardly.

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

### 7.10 A guard inside a bare `except` is not a guard

`regression_gate.py` mirrors the build's own rule for which labels get plate-tracked, including "the coordinate must be land today". It was written as:

```python
try:
    z = present(lon, lat)
    if z is None or z < 0:
        return False
except Exception:
    pass
```

`build_webdata._present_elevation()` takes **no arguments** — it returns the raster, and the lookup is a separate function. So every call raised `TypeError` straight into `except: pass`, the guard passed everything, and the gate scored 35 labels the build never tracks. That is what produced the headline "7 true regressions": five of the seven — Gulf of California, Red Sea Rift, Newark Rift Valleys, West Antarctic Rift, Kerguelen — are authored at coordinates that are *water today*, so the build leaves them to `snapLabel` under **both** frames. A frame switch cannot regress a feature it never touches.

With the guard actually working: 124 features scored, 54 improved, 67 unchanged, **3 down by ≤0.08, none true**.

Two rules out of it, and the second is the general one:

- **A `try/except` around a guard inverts it.** The failure mode of a check that throws is *silence*, and silence reads as "passed". If the guard cannot run, that is a reason to stop, not to continue — the gate now raises rather than reporting numbers it cannot stand behind.
- **When an audit disagrees with the app, check the audit first.** Seven times out of seven in this project the error has been in the measuring instrument. Two of the seven were found by the audits' own selftests; this one needed the app's answer and the audit's answer to be put side by side.

### 7.11 Two ways a long build silently does not run

Both cost time in July 2026, on the same afternoon, and both look identical from outside: the command returns, nothing is obviously wrong, and the files never change.

- **A process backgrounded with `&` dies when its shell call ends** — `nohup` does not save it. A 50-keyframe rebuild launched this way printed its first line and was gone; the same command in a properly detached background task ran for two hours. The tell is a log that stops after one line.
- **Waiting on a pattern matches the waiter.** `pgrep -f build_fields.py` matching itself is the known form, and bracketing the first character (`[b]uild_fields.py`) fixes exactly that one case and no other: a *second* waiter watching the same string still matches the first. `until ! ps -eo command | grep -q "[r]eskin_seafloor.py"` can therefore never exit, because its own command line contains the pattern. **Wait on a PID** — `until ! kill -0 "$PID"` — which cannot match anything but the process itself.
- **A chained waiter must run the next job in its own foreground.** A waiter that ends `… & echo $!` loses the child the moment the waiter's shell exits, so the second job never starts and nothing says so.
- **Two full-resolution rebuilds in parallel is slower than one after the other.** They write disjoint files and use disjoint `oceanage` cache entries, so nothing collides and it looks free. It is not: one pass holds ~1 GB and the future builder ~2.2, which pinned swap at 3.5 GB of 4 and took throughput from 20 s a keyframe to 60. **Check `sysctl vm.swapusage` and RSS, not just file collisions.**

All four fail the same way — the command returns, nothing errors, the files never change. On any long build, confirm the job is alive and producing output before leaving it, and prefer serial-and-verified to parallel-and-assumed.

### 7.12 A rule with two branches has a blind spot where they meet

`build_labels()` decides what to do with a coordinate by asking one question: **is it land today?** Land means a present-day position, so plate-track it. Water means the coordinate was authored in its own era's reconstruction frame — Gondwana at 30E 40S, Avalonia in the South Atlantic — so leave it where it is. Both branches are right, and §9 lists the four labels the water branch correctly declines to track.

The blind spot is the case the question cannot see: **a palaeo coordinate that happens to fall on modern land.** It takes the present-day branch and is tracked, silently, on whatever continent now occupies that spot. Nothing errors. The label still draws, still moves, still looks entirely plausible — it is simply riding the wrong continent, and no amount of staring at the globe will show you which one.

Found by machine, eleven of them, after the Newark Rift Valleys had been found by hand:

- **All four of Sloss's cratonic sequences** — the Sauk, Tippecanoe, Kaskaskia and Absaroka seas, the great floodings of *Laurentia* — were authored in the Caribbean and at the mouth of the Amazon. All four rode South America and were carried to 67°S while the continent they flooded sat on the equator.
- **Laurentia** itself, at its Ordovician equatorial position, lands in Guyana. The label for North America's craton rode South America.
- **Catskill Delta** → Brazil · **Variscan Belt** → the Sahara · **Caledonides** → Western Sahara · **Muschelkalk Sea** → Libya · **Sveconorwegian Belt** → Algeria.

The general lesson: when a rule branches on a property that is only a *proxy* for what you actually mean, enumerate the cases where the proxy and the meaning come apart, and write a check for them. Here the check is `build/audit_label_plate.py` — it cross-references every tracked label's plate id against the continents its own name and description commit it to, with fourteen genuinely trans-continental features (Laurasia, Beringia, Wallacea, the Central Pangaean Mountains) listed as exemptions with a reason each. It is registered in `audit_all.py`, so the class stays closed rather than being closed once.

### 7.13 The artefact was in the codec, not the model

A stair-step pattern crossed the sea floor at zoom, worst on smooth abyssal plain and along shelf edges. Four rounds of sea-floor work had already gone into procedural fabric, the depth law and the dequantisation window, so the reflex was to look there again. It was none of them.

**WebP's lossy path transforms in 4x4 blocks and quantises each block's DC level on its own.** The abyss is smooth, low-contrast, and uses only ~27 of the 256 encoded levels below 3.5 km, so neighbouring blocks land on DIFFERENT levels and the decoded field carries a four-pixel grid of one-level steps that was never in the data. The shader then DIFFERENTIATES elevation to light it, and one level at abyssal depth is a 19-degree normal tilt (section 2.4) -- so every block edge is drawn as a facet.

Measured as excess gradient energy at exactly the four-pixel period, on the float array before it is ever saved:

| | Precambrian | present day |
|---|---|---|
| the array itself | 0.4x | 0.0x |
| WebP q94, what we shipped | **29.5x** | **37.8x** |
| AVIF q90 | 2.3x | 15.8x |
| WebP lossless | 0.4x | 0.0x |

Elevation ships as **AVIF** now. AV1's larger transforms and better prediction of smooth gradients cut the artefact 2.4-13x, the files come out *smaller* (0.95x overall), mean error drops, and it decodes at the same speed -- 3.3 ms against WebP's 3.6 on a 4096x2048 frame, measured in the browser, so fetch-on-demand scrubbing is unaffected. Lossless WebP takes it to zero but costs 3.7x the bytes. On the shipped set the block-edge excess step fell from **9.3 m to 3.0 m**, under the ~89 m quantisation level the shader already shrinks away.

Three hypotheses were tested and disproved first -- crustal-age quantisation, the new GDH1 depth law, and dithering before quantisation -- and two A/B runs were invalid because they re-encoded an ALREADY-DAMAGED file, which faithfully reproduces the artefact and looks like a null result. When A/B-ing a codec, always start from the array, never from the shipped file.

### 7.14 A rank statistic is shaped like the stencil it is computed on

`shelfHi = hi2`, the second highest of four elevation taps, decides whether there is a shelf above this slope. The four taps sat due N/S/E/W at a fixed 16-texel radius -- and **the contours of a rank statistic take the shape of the stencil**. So a margin running diagonally was drawn as a flight of stairs with square 90-degree corners, one tap-radius (about 1.4 degrees) on a side.

It is the stencil, not the data. Reproduced offline on the shipped field: at a 16-texel radius the gate boundary is all right angles; at 4 texels the same boundary on the same field is smoothly curved. Note that this is a SEPARATE artefact from 7.13 -- that one is four pixels and comes from the codec, this one is tens of pixels and comes from the shader. Fixing the first did not touch the second.

The fix is to spin the cross by a smoothly varying angle (a value noise at about two tap radii) and rotate the measured gradient back into the north/east frame, which is exact. Each fragment still takes FOUR taps at ONE radius, so the seamount rejection the second-highest was introduced for is untouched -- verified on synthetics: an isolated seamount leaves the gate at 0% either way, a broad shelf fires it over half the frame either way. Neighbouring fragments simply no longer agree about which way is "along", so no contour can follow a texel row.

Measured: the wide gradient keeps its strength (873 -> 844 m mean), the change correlates with the rotation field at only +0.105, and band power at the rotation wavelength goes DOWN -- so it does not trade a staircase for mottling, which is the obvious way to get this wrong. An eight-tap ring was tried and rejected: it trades square steps for octagonal ones.

### 7.15 One control for two quantities means neither can be right

`handoff_blend` cross-fades the real 540 Ma DEM into the generated Precambrian world, and a single `wq` drove both what the ground looks like and how much of it is land. Those want opposite ramps:

- The 540 Ma DEM is a snapshot of one instant. Held at two-thirds weight 20 Myr away, it put **-3640 m of ocean** under Siberia's label, which by then had moved with its plate -- so a continent appeared to swim across the sea and its name swam with it. That wants a SHORT ramp.
- Land fraction wants a LONG one. Shortening the single ramp to 20 Myr sent land 18.5% -> 28.6% -> back to 24.1%, which is the same "continents flood then a continent arises" artefact this function was written to kill, running backwards.

Split them: geometry on 20 Myr, land fraction on 110 Myr, with the re-levelling shim now running at `wq >= 1` too (returning `B` early is what made the land curve step). Both come right at once -- land rises 18.5 -> 24.4% monotonically and both labels sit on land at every age.

Two related traps came out of the same hunt. **A label's track is not linear in time**: Siberia barely moves 540->560 and then sweeps 60 degrees by 600, so pinning the ends of the handoff window left the interpolation 23 degrees ahead of it in the middle -- more than the craton's own radius. Pinning the ends of a window says nothing about its middle. And a verification that RE-DERIVES geometry can repeat the very error it is checking for: the first "on land at every age" result was produced by a broadcasting bug and was wrong. Sample the shipped texture instead.

## 8. Sources

| role | source |
|---|---|
| Plate topologies | Merdith, A. S. et al. (2021), *Earth-Science Reviews* 214, 103477 · Zenodo 4485738 · CC-BY 4.0 |
| Feature-track rotations | Scotese, C. R. (2016), PALEOMAP Global Plate Model `m15g60_v2d3` · in `Scotese_PaleoAtlas_v3` · CC-BY 4.0 — the PaleoDEMs' own frame |
| Paleo-DEMs | Scotese, C. R. & Wright, N. (2018), PALEOMAP PaleoDEMs · Zenodo 5460860 · CC-BY 4.0 |
| Present plate motions | NNR-MORVEL56 (Argus, Gordon & DeMets, 2011) |
| Present boundaries | Bird, P. (2003), PB2002 · *G³* 4(3) |
| Sea-floor depth | GDH1 plate model (Stein, C. A. & Stein, S., 1992, *Nature* 359, 123–129); von Kármán roughness model for abyssal hills |
| Future climate | Farnsworth, A. et al. (2024), *Nature Geoscience* 17, 1109–1116 |
| Solar model | Gough, D. O. (1981), *Solar Physics* 74, 21–34 |
| Impacts | Impact Earth database (Osinski et al.) and Schmieder & Kring (2020) |
| Intervals | ICS chart v2024/12 |
| Illustrations | PhyloPic — CC0, Public Domain Mark or CC-BY only; contributors credited individually |
| Software | pyGPlates / GPlates; three.js + GLSL |

---

## 9. Known limits

- **Deep time and deep future are interpretive.** Pre-540 Ma and future frames are authored reconstructions — real cratons rotated into supercontinent fits. Treat this as a visualisation of the published record, not a precise map.

- **Palaeozoic longitude is a choice, not a measurement, and a residual against another reconstruction is EXPECTED.** Palaeomagnetism fixes palaeolatitude and orientation and says nothing about longitude, so before ~175 Ma — where the oldest sea floor and its magnetic stripes run out — every published model picks its own. Measured against Deep Time Maps (Blakey), an independent reconstruction: 5° mean |Δlon| over 0–100 Ma, 12° over 100–260 Ma, and **73° over 260–525 Ma, reaching 146° at 500 Ma**. Scotese's own model moved by up to **60°** between its ~2000 and 2016 editions. Latitude agrees throughout — land-versus-latitude correlation 0.87–0.97 across 400–525 Ma — which is the signature of a one-dimensional uncertainty. Chasing the residual to zero is the wrong goal; part of it can also be a true-polar-wander correction present in one model and absent in another.
- **The synthesised spreading network is plausible, not surveyed.** The pattern is real; the particular line is not. Same standing as the modelled rivers.
- **41 tracked labels** still sit on the wrong medium for more than a third of their span, down from 62 before the frame switch. The old root cause — a Merdith-vs-Scotese frame mismatch patched with a rigid global longitude shift — is gone; tracks now use Scotese's own rotations, so the mismatch is zero by construction. What remains is a different and smaller set of causes: about a third of them are submarine **plateaus** (Ontong Java, Manihiki, Agulhas, Broken Ridge, Mascarene, Kerguelen) where "wrong medium" means the audit expected land and the feature is genuinely a drowned plateau, and most of the rest are terranes below what a 20 km grid resolves.

- **A small block in a shredded region is below the grid, in any frame.** The Rhodope Massif is the worked example: nine anchors *inside the same massif*, all assigned the same plate, score anywhere from 0.15 to 0.92 on the medium test under **either** rotation model. The spread is the measurement — the answer depends on which texel you land in, not on the reconstruction — so its residual is recorded rather than tuned away.

- **Four labels are authored at coordinates that are water today**, and so are never plate-tracked in any frame: **Gulf of California**, **Red Sea Rift** (both rifts that have already opened into sea), **West Antarctic Rift** (below sea level under ice) and **Kerguelen Microcontinent** (a drowned plateau). `coord_is_present_day()` routes them to `snapLabel`'s terrain search by design — a track follows crust, and a point in open water has no crust to follow. They are correct as authored; the build lists them under "labels left untracked" every run.
- **The oldest ocean crust is capped at 190 Myr, and one basin is probably older than that.** `MAX_CRUST_AGE = 190` is right for the world's ocean floor: everything older has been subducted, which is why the Pacific has no Jurassic floor left. The exception is the deep **eastern Mediterranean** — the Ionian and Herodotus basins may be surviving **Palaeozoic Tethyan floor, 270–340 Ma**, trapped behind the closing of Tethys rather than consumed with it. If so it is by a wide margin the oldest ocean crust on Earth, and this model draws it at 190 Myr like everything else, so it comes out a few hundred metres too shallow and with the wrong fabric age. The dating is contested and the basins are buried under kilometres of Messinian salt, which is part of why. Recorded rather than special-cased: one basin's disputed age is not worth a branch in the depth law.

- **The late Ediacaran draws too little land ice, and that is the price of one reference frame.** `ice_audit` wants 2-10% of land under ice at 570 Ma, for the cool interval after the Gaskiers glaciation; the model draws **0.3%**. It is not the ice model. Pinning the generated Precambrian world to PALEOMAP at the handoff -- so that Siberia and Laurentia stop drifting away from their own names (section 7.14) -- also adopts PALEOMAP's Ediacaran latitudes, and they are tropical: at 570 Ma **60% of all land lies within 30 degrees of the equator and only 7% above 60**, against 46%/16% at 545 and 42%/16% at 650. There is barely any high-latitude land to freeze. The literature figure assumes continents further poleward than this frame puts them. Warming the ice threshold until the number matched would be a compensating error hiding a geography disagreement, so it is recorded instead, and `audit_all` allows exactly this one finding.

- **Hotspot chains are generic**, smeared along plate motion, rather than modelled per plume with an explicit island-formation-and-subsidence history.
- **The biota panel now has three tiers, and the residue is 21 labels.** It used to have two: a curated list for 101 of 336 labels, and one *global interval list* for everything else — the same four organisms on two hundred cards, and 133 labels (every mountain belt, basin, rift, desert and plateau) got no panel at all. `provinces.py` puts a named biogeographic province on **315 of 336** labels at every age they are drawn, so the order is now exception-curated → province assemblage → labelled global list, with the heading saying which one the reader is looking at. The 21 that still fall through are future-only names (Pangaea Proxima, Amasia, Neo-Himalaya) and the Antarctic Ice Sheet.

- **Ten curated localities are flagged `exception`** and the province model must never speak over them — Solnhofen, the Zechstein, Muschelkalk and Nama seas, the Messinian salt basin, the Paratethys, Lake Pannon, the Mid-Atlantic Ridge and East Pacific Rise vent faunas, and the Beringian steppe-tundra. Being atypical for their province is the entire point of each. `audit_curated_biota.py` checks the flag against a reading of the name, so a new curated entry has to declare itself.

- **We and Blakey agree about how much continent there was, and disagree about how much of it was dry.** This is the honest shape of the two largest remaining disagreements with an independent reconstruction, and they turn out to be one disagreement. At 525 Ma our land is 10.1 points below his — the biggest single-age gap in the whole audit — but **land plus shelf agrees to 1.0 point** (31.7% against 32.7%). Same continents, different shoreline. From 360 Ma back the same thing shows as us drawing 3–11 points *more* shelf sea than he does. Our own Cambrian series is smooth and tracks our eustatic curve (18.6% land at 540 Ma → 16.6% at 525 → 17.2% at 500), while his drops eleven points in 25 Myr against his own neighbours — so where the two differ at 525 Ma, the anomaly is not on our side. Recorded rather than tuned: this is two published reconstructions disagreeing about flooding, not a defect.

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

**Fixed in July 2026: the plumes were in the wrong places, and it was not a texture problem.**

`seamounts.field()` placed its 34 plumes by **hashing a seed** — `_h(seed, p, 11)` for the latitude. The mechanism was right (a chain is the locus of volcanoes born at a stationary plume and carried off on the plate) and every location was invented, so the single most *organised* feature of a real ocean was the one thing the map put in the wrong place. Hawaii, Louisville, Ninetyeast, Walvis, the Emperor seamounts: all absent, and a scatter of imaginary chains instead.

The fix is a catalogue, not a noise function. `hotspots_cat.py` bridges the 53-plume table in `Deep Research/modeling/hotspots.py` into the seeder, and one line of physics does the rest:

```
summit_depth = (ridge_depth − edifice_height) + 0.350·√(edifice age in Myr)
```

An edifice's summit sits at an **absolute** depth set by its own age, so its height above the floor is whatever the difference happens to be — which is why a young Hawaiian volcano on 90 Myr crust comes out 7 km tall and an Emperor guyot on the same crust comes out with its top 2 km down. Islands drown at ~16 Myr. Measured on the shipped field at 0 Ma:

| | drawn | what it should be |
|---|---|---|
| Midway (~28 Ma edifice) | **−77 m** | an atoll — it is one |
| Meiji (~85 Ma, Emperor) | **−2,111 m** | a deep guyot |
| Ninetyeast Ridge | **−1,255 to −2,587 m** | a submarine ridge, crest 1.5–2.5 km |
| Carnegie / Nazca / Cocos ridges | −458 / −768 / −36 m | shallow aseismic ridges |
| Iceland · Réunion · Azores · Cape Verde · Samoa · Society · Marquesas · St Helena | **emergent** | volcanic islands |
| two open-abyss controls | unchanged | unchanged |

Measured over 300 open-abyss points on the rendered globe afterwards: R/B **0.42**, G/B **0.52**, saturation **0.574**. The colour ramp was not touched and has not moved. **The spectral-band and grain-coherence rows of the table above were NOT re-measured** — their reference framing is a set of Google Earth screenshots at a fixed zoom and sun angle, which is not reproducible from a scripted render, so quoting a number against them would be false precision. The direct evidence that the abyss is untouched is that the chains occupy 2% of ocean cells and the open-abyss controls read identically before and after.

Three things follow from the catalogue rather than needing new machinery. **Guyots and atolls** are the same line at different ages. **Ten named aseismic ridges** are entered from their surveyed present-day trace and carried back on their own plate — necessary because several were written on a plate the plume no longer touches (India has taken the Ninetyeast Ridge 5,000 km from Kerguelen, and every plate within 8° of the plume now shares Antarctica's rotation). And the **anti-breach cap** — which existed to stop procedural noise painting turquoise flecks across the abyss — now splits on *do we know its name*: a named volcano's summit comes from its own age, everything procedural stays 1.3 km down. New land is **0.012% of the globe**, and it is Hawaii, the Azores, Bouvet, the Marquesas, Juan Fernández and the Cook–Australs.

**Where the catalogue stops, the model carries on and says so.** The oldest dated trail is ~135 Ma; Earth plainly had plumes at 300 Ma and we do not know where, so the hashed population survives as the top-up beyond the catalogue's reach.

**Not fixed, and known.**

- **Deep-time sea floor cannot be made accurate**, only structurally correct. That crust was subducted; there is no record. The isochron model correlates 0.41 with the surveyed grid where both exist, which is why the surveyed grid is preferred wherever it survives.
- **The axial valley and nodal basins still key off the ridge network**, not age — deliberately, because they describe where the ridge is *now*.
- **Marginal basins are still generic.** The aseismic ridges are now catalogued, but the Philippine Sea and the western Pacific's scatter of back-arc basins are not modelled by slab roll-back; the mechanism is on the Sea of Japan card and not in the geometry.
- **A plume's mirror trail is over-drawn at the short end.** Where a plume sits on a spreading axis it feeds both flanks — Tristan writes Walvis on the African plate and the Rio Grande Rise on the South American — and the catalogue does not record which flank each age span belongs to, so the union is applied to both. The Rio Grande Rise therefore runs a little younger than it should.
- **The Emperor limb is short.** PALEOMAP's Pacific rotation carries the chain to (158°E, 37°N) at 80 Ma where the real Meiji seamount is at (165°E, 53°N). That is the published model's own answer, and the ridge itself is drawn from its surveyed trace rather than from the rotation for exactly this reason.
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
