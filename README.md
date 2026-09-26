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
build/          52 Python modules, ~16k lines — the offline pipeline
web/            the app, split (WP-10 D5): index.html is the markup, style.css
                the styles, loader.js the request broker and the pure time
                policy (Node-testable, build/test_loader.mjs), app.js the
                application (~4.5k lines), and web/shaders/*.glsl the seven
                shaders, which check_shader.py validates and packs into
                shaders.js (generated). build_site.py inlines all of it back
                into one deployed docs/index.html
web/imagery/    the NASA cloud field and the timeline preview atlas, each with
                its provenance/metadata JSON (§5.7, §5.11); shipped to docs/imagery
web/fields/     ~2,960 field textures (12 kinds × 251 keyframes, some kinds
                absent on a few keyframes), plus a second present-day lake field
                without the geologically young lakes. Gitignored: docs/fields
                holds the deployed copy (or an asset host does, §6)
docs/           the built static site; GitHub Pages serves main:/docs
data/           source DEMs, rotation files, catalogues (not in git)
```

Keyframes are every **5 Myr** from 1000 Ma to +250 Myr — 251 of them.

Build scripts use relative paths (`../web`, `../docs`), so the project directory can move. It has: it lives at `~/Tectonic Plate Model` because macOS TCC gates `~/Desktop` and `~/Documents` and blocked the build mid-session. Do not move it back.

---

## 4. The shipped fields

Ten textures per keyframe (138 MB for the timeline). Elevation is AVIF (§7.13); the rest are WebP. All are decoded and interpolated between the two bracketing keyframes in the shader, the interval ones (`_v`, `_p`) from the younger keyframe of the pair.

| suffix | field | resolution | contents |
|---|---|---|---|
| `_e` | elevation | 4096×2048 | signed-sqrt encoded, so precision concentrates near sea level — the coastline is the one contour that must interpolate cleanly. Matches the 6-arc-minute source DEM, so more pixels would only interpolate |
| `_r` | rainfall | 1536×768 | smooth, so it costs little |
| `_m` | plate motion | 128×64 | R = east, G = north, B = confidence |
| `_w` | lake depth | 2048×1024 | baked standing water, sqrt-encoded metres; G marks a desiccated basin |
| `_d` | surface process | 2048×1024 | drainage, substrate, fetch |
| `_o` | ocean structure | 2048×1024 | R = **crustal age**, log-companded over 0–52° of spreading (190 Myr, the oldest surviving ocean crust); G/B = spreading direction from the age gradient, with confidence in its length |
| `_v` | displacement | 1024×512 | how far the crust under each pixel moves to the next keyframe, east/north in degrees of great circle, B = divergence (`build_displacement.py`) |
| `_p` | plate slot | 1024×512 | index into the per-keyframe rotation table in `platerot.json`, giving each pixel a material coordinate so procedural texture rides its plate (`build_platefield.py`) |
| `_t` | tectonic fabric | 512×256 | R shortening, G/B the fold axis as a double angle (`build_tectonic.py`); A the **belt type**, 1 − arc: a magmatic arc (the overriding plate 150–300 km behind a trench with ocean crust going down) against a fold-and-thrust belt (`build_arc.py`, §5.10) |
| `_f` | foreland flexure | 1024×512 | R the moat in front of a mountain belt (0–620 m), G the forebulge beyond it (0–90 m) (`build_foreland.py`); B the **relief deficit**, 0–1: how much of the ridge-and-valley relief a real belt of that height carries the source never drew there, which the shader's erosion relief fills (`relief_deficit.py`, §5.10) |
| `_x` | drainage coordinates | 512×256 | two potentials fitted to the downhill direction of the PaleoDEM smoothed to ~120 km, χ across the regional flow and ω along it (increasing upstream), one unit per 256 km, gated on plains with a regional slope of 0.2–1 m/km; the tilted plains patches of the atlas are sampled at (χ, ω) (`build_drainphase.py`, §5.10) |
| `_q` | fold coordinates | 512×256 | two potentials fitted to the strike field, φ across strike and ψ along it, one unit per 256 km, 16-bit byte pairs in a lossless WebP; the orogen atlas is sampled at (φ, ψ) (`build_foldphase.py`, §5.10) |

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

**The collision zone is a landform (2026-09).** Where two groups' footprints interpenetrate, the overlap *is* the collision zone -- its width is the shortening -- and until this round its uplift was `gaussian_filter(overlap, 3°)²`: a dome over every patch, in the shape of the overlap rather than of an orogen. Measured on the shipped +250 Myr field it was what the user called clumps: more land above 2 km than today (12.1 Mkm² against 8.7) and almost none above 4 km (0.37 against 2.69), the summit 4.9 km. `_zone_orogen()` now builds the zone's own geometry: a **plateau** that rises across the zone's margin and is flat inside, the way Tibet's is; a **main range** along the zone's medial axis (`skimage.morphology.medial_axis`), as wide as the zone is, present only where the zone is wide enough to carry one and pruned to the axis's spine so a roundish zone does not grow a starfish (§7.32); a broad **swell** round the zone outside its plateau; and along-strike **segmentation** keyed to the crust's own present-day position, so massifs and saddles ride their plates. Calibrated on the 2048-row field that ships, the uplands stay where the user signed them off and the high tail moves into chains:

| +250 Myr, Mkm² | >1 km | >2 km | >3 km | >4 km | >5 km | max |
|---|---|---|---|---|---|---|
| today (0 Ma) | 30.2 | 8.7 | 4.3 | 2.7 | -- | 6.7 km |
| domes (until 3.11) | 27.1 | 12.1 | 3.8 | 0.37 | -- | 4.9 km |
| zone orogen | 26.1 | 13.0 | 4.7 | 2.5 | 1.0 | 6.5 km |

The shader's erosion relief (§5.10) then cuts them into ranges; the relief deficit on the future's smooth belts runs from 0.07 at +50 Myr to 0.70 at +250.

**The future's names are placed on the future (3.15).** Future labels used to be present-day names carried forward on their plates, and several ended up on the wrong ground or on nothing: an "Amasia" over a world where the Americas never reach Asia, a Pan-Asian Rift nothing draws, the Pangaea Proxima Inland Sea named while it was still open ocean. `build_webdata.future_label_pass` now places every name that reaches into the future against the future terrain itself, keyframe by keyframe (`FUTURE_LABELS` in `features.py` says how): a collision belt at the top quartile of the zone where two groups' main bodies meet (`belt`), a crust point carried on its group (`ride`), the largest landmass and its most arid interior (`landmass`, `interior`, the pole of inaccessibility among ground under 0.2 of rainfall), an ocean held between named coasts (`between`) or a sea only once it is enclosed (`enclosed`). A name is shown only over the longest run of keyframes where its feature exists (a continuing name must hold from +5), and one that never validates is dropped rather than drawn on the wrong thing -- the Trans-Atlantic Belt, since this drawing's Americas stop ~1,000 km short of Africa. Cards and phases for the future's oceans and continents say what this drawing does and where it differs from Scotese's 2018 atlas (the Atlantic narrows but stays open; the East African Rift is the older projection) and Farnsworth et al. (2023).

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

**Sand seas** (WP-10 B5, the erg half). An erg is a corduroy, and its lineation follows the resultant wind. The climate model's winds are zonal by latitude band (`fetch` above), and a surface wind is turned by the Coriolis force, so the trades blow from the north-east and the westerlies from the south-west: the *line* is NE–SW everywhere north of the equator and NW–SE south of it, which is the trend of the Rub' al Khali's uruq and of the Kalahari's and the Simpson's dunes. The shader smears value noise along that line at two scales — 11 km cells for the dune-field corridors that survive at continental zoom, and 5.8 km cells over ±5 cells for the dunes themselves, ridged into sharp crests and faded in by the pixel footprint — as tone (crests light, interdune corridors dark) and as slope in the shading normal. The direction comes from the present latitude, the pattern is welded to the crust, and the erg mask (dry, still, flat, and a sand-sea body) is unchanged — which is the open item: the body is a crust-locked noise, and drawn as a mask (`?show=1`) it is zero over the whole Arabian peninsula and, on Tibet, on only in the Tarim. `?erg=0` switches the lineation off, `?erg=K` scales it.

Lakes are baked separately (`bake_lakes.py`, `bake_present_lakes.py`) and the geologically young ones are handled explicitly: the Great Lakes are ~14 ka old, and interpolating them out of the present frame left them sitting there in the Pliocene, 4 Myr either side of today. A second present-day lake field *without* them is swapped in outside the window they actually occupy.

**Three rules decide which basins keep water (3.15).** *An overflowing basin is breached*: a keyframe is millions of years, and an outlet that carries a continental river cuts down, so a basin whose budget supports more lake than lies below its spill, and at least `BREACH_Q` = 600 cells of it, keeps only its deep tectonic core. Filling them to the lip had put 845,000 km² of shallow lake in the Congo and 419,000 in the Amazon at 5 Ma and the blotchy lowland lakes of the future; the breach is set by discharge, not overflow alone, so a rift lake's modest overflow (Tanganyika 160 cells, the soda lakes 265) does not trip it. *A deep floor needs a wet catchment*: the permanent fill of deep basins scales with the catchment's humidity index up to `HUM_DEEP` = 0.30, so a 130 m desert basin is no longer flooded to a tenth of its depth. *The record outranks the sky where it names a lake*: within a `lake` label's window, the basin under its plate-tracked position keeps its full deep floor, is not breached and keeps bodies of any size (the climate solve runs dry over interiors, the trade that keeps Pangaea a desert). Water under the record's own lake labels went 29 → 25 → 28 label-keyframes with that rule, Pebas at 10 Ma newly wet; Uinta at 50 Ma, Baikal at 30 and Tanganyika at 10 keep small lakes at the edges of their windows. The rule authors nothing -- a basin the DEM lacks holds nothing -- and it reads the tracks from `web/labels.json`, so labels are built before lakes. Shores are measured against the σ-1 surface, not the 8-bit one, so a lowland lake's edge follows a contour instead of the terrace outline. Lake cover roughly halves at most ages (+250 Myr 0.41 → 0.17% of cells, 150 Ma 1.02 → 0.30%).

### 5.6 Events, features and life

- `paleo_tracks.py` — impacts, large igneous provinces, labels, the epeiric seas and the plume chains are catalogued where we find them *today*, and the crust has travelled. These are reconstructed along **real plate rotations** — Scotese's PALEOMAP, the frame the terrain itself is drawn in (§5.1). The previous approach advected them on the block-matched motion grid, which freezes over featureless ocean and has a poleward bias past 250 Ma, so an ocean crater sat still while its plate moved out from under it.
- `provinces.py` — the biogeographic province each label sat in, at every age it is drawn, emitted as runs. What stopped 235 of 336 cards showing one global list; see §9.
- `hotspots_cat.py` — the 53-plume catalogue and the subsidence law that turns it into islands, atolls and guyots; see §10. Both this and `provinces.py` are two-line bridges to `Deep Research/modeling/`, which is stdlib-only on purpose so `build/` can import it rather than keep a second copy that drifts.
- `features.py` — volcanic provinces and era labels with age windows. A flood basalt is an eruption for a moment and a **landform** for far longer, so each province stays on the map as long as it stood as high ground. The Deccan still holds up the Western Ghats; CAMP, the largest of them all, was buried in its own rift basins almost as it erupted and is a landform essentially nowhere.
- `life.py`, `add_*_life.py`, `add_present_biota.py` — biomes and the curated regional fossil record (`life_data.json`), with terms chosen to suit the period: no grassland before the Cenozoic, and before land plants the terrestrial world is microbial crust and bare regolith.
- **The taxon registry and the card composer** (2026-09) — `build/taxa/*.json`, `biota.py`, `biota_forms.py`. Every organism the app can show is declared ONCE: what it is (a body `form`, which alone decides its drawing), when it lived (`fad`/`lad`), and where (`range`, in present-day CRUST codes, optionally sliced by time). A fossil lies in the crust its animal lived on and a label's crust has a present-day address, so "did it live here" is a comparison of present-day codes and does not depend on the plate model. `biota.compose()` builds each label's card per whole-Myr age from three sources in order — the label's curated list (authority over place, none over time), its province's markers, then whatever else the registry places on this crust now — filtered by age, crust, habitat, palaeolatitude and the taxon's own range within the region, and balanced on purpose into Fauna / Flora / the rest. It ships as run-length-encoded `cards` in `life.json`. The contract for authors is `build/taxa/SCHEMA.md`; new organisms are written as compact batches in `build/taxa_src/`.
  - **Finer than a region code.** The codes are continent-sized (`na-w` is Alaska to Baja), so a narrow endemic carries a `box` in present-day lon/lat and a label carries a footprint (`biota.label_point` + `label_reach`, anisotropic for long ranges). Continents and whole oceans ignore boxes; everything local obeys them. `avoid` names labels outright where a point and a reach cannot separate neighbours. `build/taxa_src/ranges_within_regions.py` holds all of these refinements in one reviewable table.
  - **The label's SETTING is dated.** `SUBMERGED` makes sea cards of labels typed for their tectonics whose surface is water (oceanic plateaus; the Red Sea from 20 Ma, the Gulf of California from 7, Mauritius before its volcano at 8). `LABEL_HOME` may be time-sliced: a microcontinent is its parent's crust until it leaves and an ocean island after. `HABITAT_SINCE` gives blocks and basins the climate they have had only recently (the Tarim Block is desert since ~5 Ma). Ice-age ground poleward of 70° is tundra and ice whatever the type says.
  - **Three rules about "everywhere".** A land taxon ranged `cosmo` does not reach a home that is ocean basin only; after 34 Ma nothing reaches Antarctica unless its author named `an`; polar cards take no taxon on trust. See SCHEMA.md.
  - **The placement review.** `audit_biota.py --placements <age>` prints every composer-chosen taxon → the labels it lands on at that age. Read by eye at 0, 3, 20, 50, 100, 150, 250, 300 and 400 Ma it found what no rule could: endemics leaking across a continent-sized code, lineages shown before they reached a continent, lowland forms on the ice. Run it after any large registry change.
  - **Curated lists that cross a realm.** Overlapping curated spans are merged (`curated_at`). A curated land or air taxon on a sea card (Archaeopteryx at Solnhofen) shows under "On its shores and in the air above it"; a curated sea taxon on a land card after 385 Ma (Basilosaurus in the Fayum) under "In the seas across it". The model never invents either.
- `taxa_src/fetch_evidence.py` — attaches the PBDB's record (classification, robust dates, occurrence regions) to every entry lacking one, so `biota.py --check` cross-examines a new batch and not only itself. The batch writer preserves what it attaches. `taxa_src/recode_regions.py` re-bins that evidence under the current region table from the cache, offline, so a split code is checked by the record the same day. `taxa_src/upgrade_curated.py` replaces the class-level names in the curated spans (`life_data.json`) with the registry's genera of that group that were alive and at home on the label, by the composer's own place rules; the curated prose stays with the first genus.
- `pbdb.py` — a cached Paleobiology Database client: classification, first/last appearance (4th–96th percentile of occurrence midpoints; the raw extremes are outliers and coarse bins) and occurrence regions for every registry name, used by `biota.review()` to cross-check form, range and place.
- `audit_biota.py` — replays every card the app can show (38,036 label-ages) from the SHIPPED `life.json` against the registry, plus a present-day DEM check that no label drawn under deep water lists land life. Wired into `audit_all.py` (§6). `--ledger` and `--sheets` write review documents to `build/verify/`.
- `verify_cards.py`, `verify_icons.py` — render real cards and icon contact sheets to PNG under headless Chrome by lifting the app's OWN card functions out of `app.js` verbatim, so the check is of the shipped source text without a ten-minute software-WebGL boot.
- `build_silhouettes.py forms|registry`, `fix_form_icons.py` — PhyloPic silhouettes per body form and per taxon (CC0/PDM/CC-BY only, genus-matched), pinned picks and hand-drawn icons where PhyloPic has nothing that passes "cover the caption, name the group".
- `audit_labels_full.py` — systematic label audit across terrain, debut age and drift, because a label must track the *same feature* as it evolves rather than merely sit at fixed coordinates.

### 5.7 Rendering

`web/shaders/` holds the GLSL: `VERT`/`FRAG` (globe and map), `LFRAG` (the sheet path, §5.9), `CVERT`/`CFRAG` (clouds) and `PVERT`/`PFRAG` (the time preview, §5.11); `check_shader.py` packs them into `shaders.js`. The fragment shader decodes and interpolates the fields, then recomputes temperature, relief, biome colour, water, ice, sky and the ocean fabric per pixel.

**The clouds (since the Atlas port, September 2026)** are NASA's *Blue Marble: Clouds* — a multi-day composite by Reto Stöckli (NASA/GSFC), reduced to a 4096 × 2048 cloud-density scalar in `web/imagery/`, provenance in `nasa-clouds.json` — sampled as one continuous field in coherent transport (0.004 rad per weather second, a bounded latitude shear, gently varying deformation, never accumulated strain and never a crossfade between phases). The selected era adapts it, not the other way round: the shader reads the same elevation and rainfall pair the terrain is drawn from (the terrain material's own uniform objects) for a land mask and a broad land-normalised wetness that modulates optical depth gently, and `uEra` shifts the arrangement. Rainfall is land-only, so an ocean zero is never read as dryness. Three meshes share one texture and one weather clock: the shell at 1.014 over the globe, a shadow shell at 1.0085 (between the highest displaced peak at full exaggeration and the clouds; both ride the exaggeration lift), and a plane over the flat map. Since the port's second round the deck rides the running timeline too: its transport is on the weather clock, its arrangement follows the era's land, rain and ice as the continents move, and a slow synoptic gate — a three-dimensional lattice noise drifting through the weather clock, about a minute from clear to overcast at a point, moved gently by the era as well — thickens, merges and dissolves cloud masses while the satellite structure inside them keeps its fronts and spirals. A soft zonal climatology underneath (the tropical convergence band, the mid-latitude storm tracks, the clear subtropical highs, the three bands the old procedural clouds were built from) sets where the deck is likely, as gains and never as masks; a snowball world loses most of it. Playback waits for a pair's core before advancing (§5.11), so the clouds never see a half-arrived world. Clouds thin to 55% at the closest zoom instead of retiring. Across ancient and future eras it is satellite-derived visual structure with illustrative climate adaptation, not reconstructed weather for any date.

---

## 5.8 Loading

Fields are fetched **when they are wanted**, not up front. The loader used to await all 1,506 of them — six fields at each of 251 keyframes — before the globe appeared: measured, **148.8 MB and 17.9 s on localhost with a warm cache**, which is fetch and decode alone, before a byte crosses a network. What the opening frame needs is the keyframes it interpolates between: 12 files, about a megabyte. Time to a usable Earth went **17.9 s → 0.37 s**, and the render is bit-identical (same SHA-1 on a pinned-`uTime` capture).

Three things already in the architecture made that a loader change rather than a rewrite, and they are worth preserving:

- `bindTextures()` is written `if(ea) … if(eb||ea)`, so a keyframe that has not arrived keeps the previously bound texture instead of binding null.
- `getTex()` creates GPU textures lazily behind an LRU cap, so residency was never tied to how many images were in memory.
- every CPU-side reader of the elevation raster goes through `elevField()`, which returns null for a frame it does not have — and every caller already handled that, because a `_w` or `_o` file has always been allowed to be missing.

The background fill re-centres on every completion: it asks each time for the nearest wanted keyframe to wherever the viewer is **now**, so scrubbing re-aims the queue instead of waiting out a plan made before they moved. Four concurrent — enough to saturate a connection, few enough that a frame someone is waiting for is not stuck behind speculative ones.

**The broker (since the Atlas port, September 2026; `web/loader.js`, tests in `build/test_loader.mjs`).** Every field, sheet and imagery fetch goes through one bounded queue: the same URL is one request however many callers want it, the keyframes the viewer is at outrank everything, and a seek cancels queued *and in-flight* requests for keyframes it left behind (`retargetLoads()` in `loop()`), so a run of jumps starts on the new pair at once instead of behind the tail of the old one. The pump's neighbourhood is bounded everywhere now — paused, three keyframes each way; playing, as many keyframes ahead as the speed covers in a *measured* fetch, a *measured* decode and two seconds of slack (3 at 3 Myr/s, 5 at 10 on a fast link, never more than 8), one behind; two on a metered link or a battery — rather than the whole timeline on mains power. Only an HTTP 404/410 marks a field absent at a keyframe; a timeout, abort, 5xx or network failure is retried after three seconds, and a superseded request is no outcome at all (the old loader recorded every settled fetch as tried, so one dropped packet made a field permanently missing until reload). An exact keyframe age now binds that keyframe alone (`frameAt`, binary search): the old scan answered the next younger keyframe and t = 1, so a marker jump bound the neighbour's interval fields (§7.16). And a cold seek no longer leaves the previous world on screen: §5.11.

`FIELD_V` (bumped by hand, unlike `DATA_V`) busts the texture cache when the fields change but keep their names — as they did when the elevation grid doubled.

### 5.9 World sheets and the lite path

Since WP-10 (September 2026) the terrain shader no longer has to run per pixel per frame.
A **world sheet** is one keyframe's whole shaded world: the same fragment shader rendered
once into an equirect render target (`uMapProj = 2`) with the ocean mask written into
alpha. A second, ~80-line **lite material** then draws the globe and the map from two
sheets per frame — each carried toward the other on the displacement warp exactly as the
keyframe fields are, blended by `mixf`, with the interpolated height deciding which sheet's
colour a shoreline pixel takes, so the coastline still migrates instead of dissolving — and
adds only the terminator, the limb and the schematic tint on top. Measured against the live
shader at the zoom where it engages, the difference is 1.2/255 mean; the cost is a few
texture reads a pixel.

- **A bake waits for every field kind of its keyframe, and a kind the timeline declares
  absent counts as settled** (`_sheetKindsResident`, fixed 2026-09-25): the oldest keyframe
  has no `_v`, and until then the 1000 Ma sheet waited out its in-page timeout and
  `bake_sheets.py` its whole deadline after that, for a file that was never going to come.
- Sheets are **baked in the app** in sixteen strips across frames (never one hitch), for
  the current pair and the next keyframe in the playback direction, from a small pool of
  render targets. Or they are **shipped**: `build/bake_sheets.py` drives the app headless
  on a real GPU, bakes all 251, encodes them to AVIF (alpha kept) in `web/sheets/` with a
  manifest, and the app loads those instead of baking. A shader change invalidates the set:
  re-run the script (a minute of GPU, ten to twenty of encode) and bump `SHEET_V`. **Two
  sets ship since the port's second round (2026-09-07):** `sheets/` is 4096 wide, what the
  app draws from on a desktop (a 4096 sheet is 76 MB of bitmap and mipmapped texture, so it
  holds six of them instead of eight), and `sheets2048/` is the lean set the ambient page
  keeps and a constrained device takes; `bake_sheets.py --width 2048` refreshes the latter
  into `web/sheets/`, to be moved aside by hand. The preview atlas (§5.11) is built from the
  4096 set and `build_site.py` refuses to ship it stale.
- The path switches on **automatically** once a screen pixel covers about half a sheet
  texel (`?lite=1|0` forces it, `?sheet=N` sets the bake width, default 4096, 2048 on
  low-memory devices, `?bakefull=1` bakes a sheet in one frame, `?noshipped=1` ignores the
  manifest). A scrub keeps the live path. `?perf=1` shows which path is drawing. **Eager on a
  slow GPU** (round 2): once the governor has stepped the render scale down, or the quality
  is pinned below Full, the sheets engage from a quarter of a texel per pixel: a pre-shaded
  4096 sheet magnified up to four times is sharper than the live shader at half resolution
  and a tenth of its cost, which is what makes wide-zoom playback smooth on the M1's 5K
  display. The wide view the owner reported as "unfinished" was the 2048 set at 1.75×
  magnification on the stepped-down scale.
- Not carried by a sheet, by design: climate uniforms dissolve across an interval rather
  than interpolate; the Messinian drawdown is held off (a basin drained for two frames must
  not fade over ten); the sea-surface sheen is frozen; keyframe 0 carries the Holocene lakes.

**`ambient.html`** is the background build: a slowly turning Earth with time running,
drawn from the shipped sheets and `_v` only — no terrain shader, no field decoding, ~50 MB
for the whole timeline at 2048 wide, a few per cent of a laptop GPU. `?speed=` (Myr/s,
default 2), `?spin=`, `?fps=` (default 30; 10 under `prefers-reduced-motion`), `?age=`,
`?ui=0`, `?clouds=0`, `?weather=0`, `?paused=1`. It runs as a tab, a screensaver (any WebView screensaver pointing at the URL) or a
wallpaper. **Since 2026-09-08 it is the only ambient view:** the app's Ambient button opens it in
a frame over the app's window at the current age and play state (the app's loop idles beneath),
and its chrome is four small things — Close (back to the app, carrying the age and play state it
reached; Escape does the same) and Full screen at the top left, Pause/Play (time only: the globe
keeps turning and the weather moving) and the geological eras from `eras.json` at the top right,
each a jump to the start of that era, playing or paused, with the current era lit. `?ui=0` hides
the chrome and the readout for a screensaver. The former in-app ambient mode (this view with
its chrome hidden) is gone. **It carries the app's clouds:** its shaders live in `web/shaders/ambient__*.glsl`
(validated with the app's by `check_shader.py`, which emits the noise reader into `shaders.js`
for it), and `ambient__ACFRAG` is `index__CFRAG` with the land and wetness read from the sheets'
own colours — blue water, green wet land, tan dry land, white ice, through a coarse mip level —
since the page ships no fields (an illustrative arrangement, registered in MODEL-GAPS.md); the
same transport, zonal climatology, synoptic gate and snowball damping, on the page's own weather
clock, no shadow pass. Its sheets and the cloud image upload in strips, two a frame and eight
while the picture waits, so a keyframe crossing no longer hitches; and its frame cap now advances
time by the interval since the previous *draw* — the old cap used the previous *tick*, so time
ran at half the slider and rotation and age stuttered whenever the skip pattern broke.
**Measured** (the M1, `build/verify_run.py` driving `_verify.html?ambient=`, 20 s at the default
2 Myr/s from 300 Ma, the frozen old page through the same driver):

| | old page | new page |
|---|---|---|
| draw cadence at the 30 fps cap: median / p95 / max | 48.5 / 50.1 / 51.9 ms (23.6 draws a second) | 33.3 / 35.1 / 35.4 ms (30.6 a second) |
| time actually advanced on a 2 Myr/s setting | 15.9 Myr in 20 s (0.79 Myr/s) | 40.8 Myr in 20 s (2.04 Myr/s) |
| draws over 60 ms; frames held for a sheet | 0; 0 | 0; 4 of 855 |
| clouds | none | up from the first sheets, weather clock +28.5 s in 20 s, no shader errors |
| the same with `?clouds=0` | — | 33.3 / 35.2 / 35.4 ms, 0 slow draws |
| at 10 Myr/s from 600 Ma (15 s) | — | 33.3 / 50 / 50.1 ms: one draw in twenty is a tick late while eight strips a frame feed a waiting sheet; 4 holds; 10.2 Myr/s |
| at the present, still, and at 100 Ma, still | — | 33.3 / 35.2 ms; `build/verify/amb_present.png`, `amb2_land.png` | Recipes that
need no packaging work: on macOS, WebViewScreenSaver (`brew install --cask webviewscreensaver`)
with the page URL plus `?ui=0` as its address, or Plash for a live wallpaper; on Windows,
Lively Wallpaper's "URL" source. All three show the page as-is, so `?speed=` and `?fps=`
tune the pace and cost from the address bar.

**Playback on the sheet path (2026-09-03).** Three things the M1 Mini review found. The sheets
of the next keyframes are requested ahead by speed — about two seconds' worth, two keyframes at
3 Myr/s and four at 10 — where one keyframe ahead was 0.28 s of slack at the old 18 Myr/s, less
than a fetch, a decode and a mipmapped upload. When the next pair's sheet is still late, time
**waits** for it (`_liteHolds`, capped at `HOLD_MS` — 3 s since the port's second round — so a sheet
that never comes cannot stop the clock; the terrain path waits the same way for the next pair's
core, `_fieldHolds`) instead of the path dropping to the terrain shader at full pixel ratio for the wide view,
which was the "smooth, then a burst of lag" on the Mini; ambient.html always did this. And
shipped sheets are bounded at `SHEET_KEEP` like the bake slots — they used to accumulate for
every keyframe visited, 11 MB of GPU texture each. `_verify.html?playtest=NAME&speed=10&secs=8
&sheetdelay=600` is the measurement: from localhost a sheet lands in tens of milliseconds and
nothing is ever late, so the delay stands in for a CDN round trip. Before: 69 of 437 frames on
the terrain shader, two path flips. After: 2507 frames, none, no holds needed; starved at
40 Myr/s and 1.5 s latency, still none, 66 held frames and playback continuing. Note the LOD
rule: with the 2048 set a screen at pixel ratio 2 reaches the sheets only near the widest zoom
(a texel must cover no more than about two device pixels), so on a Retina laptop the sheet path
is nearly dormant and the terrain shader is the picture; the 4096 set would engage it from
about zoom 2.

### 5.10 Mountains: the baked relief, the erosion relief, the orogen atlas and the fold coordinates

**The baked relief (the mountain round, second pass, 2026-09; `relief.py`, `lem.py`, `lem.c`).** The first pass (below) dissected the schematic envelopes per pixel and could not reshape them: the belts still read as symmetric tents at the zoom a globe is looked at, the future's as lumps -- and its 96 km octave drew valleys up to 1.4 km deep, several times what real terrain carries at that scale, which is most of what "clumpy" was. The relief now goes into the elevation field itself, for every upland older than 55–70 Ma and for the future's smooth belts (the deficit decides there), in three steps:

1. **The wedge.** Each belt's crest moves up to ~80 km toward its foreland (the side `build_foreland.polarity` chooses: lower, and not ocean), tapering to nothing at the belt's foot. The footprint and height stay the source's; the foreland flank steepens and the hinterland lengthens -- the critical-taper shape of real orogens. A symmetric tent is an authoring artefact.
2. **The drainage.** The belt at erosional steady state under uplift (`lem.steady`: stream power with n = 1 solved on the receiver tree, Braun & Willett 2013; a priority flood over depressions, Barnes et al. 2014; a threshold slope; the keyframe's own rainfall weighting the drainage area). The uplift-to-erodibility field is the belt's regional height, broad rather than tent-shaped, varied along the belt (massifs and saddles), skewed toward the thrust front and divided by a lithology noise plus the **thrust sheets** (below; in 3.13 rock bands keyed to the envelope's contours, retired); each cycle rescales it per connected belt so the eroded belt's regional mean stays the source's. This decides where valleys, divides, spurs and basins are.
3. **The amplitude.** The eroded surface is split into three bands (up to ~250 km) and each band's amplitude AND distribution are matched to real belts at the same regional height and regional slope, measured on the PaleoDEMs built on modern topography (0–30 Ma): standardised over a ~400 km window, mapped by quantiles onto the real distribution (heavy-tailed: kurtosis 18 in the finest band, where a steady-state network is near-Gaussian), rescaled to the real local rms. Tables `REAL_BANDS`, `REAL_Q`; `relief.py --calib`. A soft ceiling compresses anything above 6 km toward 7.2 (no 10 km cell on today's Earth stands much above 6.7), and closed hollows the synthesis made are filled so the lake bake does not scatter lakes through the ranges -- at the field's resolution and again at the half resolution and 8-bit encoding the lake bake reads (§7.37).

Every perturbation -- the seed roughness, the massifs, the lithology -- is a noise of the crust's own 0 Ma position (`_p` + `platerot.json`), so the same rock grows the same valleys at every keyframe with no chain between them, and a rebuild of one keyframe reproduces it exactly: consecutive keyframes' valleys correlate 0.46 after the warp, against 0.19 for the source's own. **Validated by a control**: today's belts blurred to an envelope and re-grown, beside the real ones in the app (Himalaya, Alps, Andes). What the control changed: a 60 km normalisation window (real relief is patchy; 400 km), tables conditioned on slope as well as height (at one height a plateau carries half a flank's relief), the full tails of the distribution, and no noise stripes along strike (they drew worms; bands keyed to the envelope's contours replaced them). **Under an ice sheet** the shader keeps only the regional slope (the ±137 km macro difference) and drops the bed's relief, fading to the bed at the margin: a sheet a kilometre thick low-passes its bed, and without this the Cryogenian snowball drew its baked ranges as dark ridges through the ice. Today's sheets are drawn by their DEM surface and are unchanged. After the bake the deficit in every baked belt is 0, so the shader's coarse octaves (below) stand down there and only its sub-grid octaves (12 km and finer) draw. Applied in `build_fields.export` and `reskin_seafloor.save_eo`, so any rebuild path carries it; about 30 s a keyframe.

**Thrust sheets and the range scale (the mountain round, third pass, release 3.14).** The ranges
still read as blotches rather than lines, and the control said where: orientation coherence in
the 1–2, 2–4 and 4–8 px bands 0.36/0.32/0.36 even with working sheets, against real belts'
0.38/0.44/0.53 -- right in the fine bands, short at the range scale. Three things changed, all in `relief.py`:

- **The strike potential** `u` (km across strike, rising toward the foreland; `strike_potential`):
  the belt envelope's across-strike axis, sign-made-consistent and fitted by least squares
  (`build_foldphase._solve`), cubic-upsampled. Sheets come in where the envelope has a strike
  (coherence 0.15–0.45) and, per family, not at a vortex's eye, not where they would alias, and not
  where the contours curl tighter than about one spacing at that family's scale (`family_gate`).
- **Three families of sheets on u** (`_sheet_family`): each sheet a gentle back climbing toward the
  foreland and a steep front, and each its OWN strength along strike -- a noise drawn per sheet
  index -- so ridges rise, run and pinch out en échelon (the Zagros' whalebacks) instead of running
  the length of the belt. Minor sheets 45 km apart in ~150 km lenses and major ranges 140 km apart in
  ~450 km lenses go into the landscape model's uplift and erodibility; sub-belts 300 km apart in
  ~1000 km lenses are structure. The first version divided u by a varying spacing and drew moiré
  and whorls (§7.31); the phase drifts are now a fraction of a cycle, added (§7.40).
- **The range scale is structure** (§7.42). The 2–4 px band mixes the major ranges into the model's
  own (`STRUCT_B2`, variance kept) and a fourth band, σ 4–8 px (~250–500 km), is laid from the
  sub-belts and calibrated to real belts -- local rms by regional height and slope (`STRUCT_BANDS`,
  by the method of `REAL_BANDS`, which it reproduces), distribution `REAL_Q3` -- in quadrature with
  what the envelope already carries there. Control after: 0.43/0.44/0.51.

The noise the relief uses is now evaluated in each plate's own 0 Ma frame and blended by value
(`Material`, §7.40); blending the coordinates had drawn sub-pixel stripes down every suture.
**Belt lakes**: the relief's own check reads the lake bake's view (8-bit, half resolution,
σ 1 smoothing), fills against the ocean as the lake bake does, and raises a new hollow to its spill
level; the lake bake keeps only basins the 8-bit field resolves (§7.39). Belt lake bodies at
300/400/700 Ma went 13/24/15 → 0/3/1; the survivors are the source's own deep basins (lakes made
by the relief: ≤0.007% of belt area). The future's belt lakes (1.3–1.4%) are the future terrain's
own basins, which the relief reduces by a fifth. **The shader**: a land hillshade by scale (the
regional tilt soft-compressed, `?hsC=`; a ±1-texel band above the quantisation level, `?hsF=`),
the erosion relief's fine octaves steered by that same fine gradient (`?eroS=`), `rug` as relief
rather than slope (§7.41), laterite only on low ground, and dune fields only in basins below
~1.5–2.6 km -- flat, dry, undrained crests had come out orange sand seas.

**The erosion relief (the mountain round, 2026-09).** The Palaeozoic and Precambrian ranges read as symmetric triangular prisms and the future's as smooth clumps, and the fields said why before the renderer did. Inside mountain belts the relief finer than ~60–90 km -- the band a range is made of: transverse valleys, spurs, massifs and passes -- measures, as a local rms at the same regional elevation, 84 m at 1 km and 176 m at 2.2 km in the present-day PaleoDEM; ~40 m at 100–200 Ma; 16–44 m at 300–400 Ma; 11 m in the generated Precambrian; ~23 m at every elevation on the +250 Myr belts. Scotese drew the older belts as smooth envelopes (where a range stood and how high), the future's were gaussians, and the hillshade lit each smooth envelope as two faces and a crest.

- **The deficit** (`relief_deficit.py`, the blue of `_f`): how much of the relief a real belt of that height carries -- `R_L1`, the mean absolute band value, measured on 0–30 Ma; an RMS read a schematic crest's one sharp line as rough ground (§7.34) -- the source never drew, below the real terrain's own lower quartile (0.55 of the median), so the present day and the modern-topography Cenozoic frames keep their own valleys (median 0 across 0–50 Ma), and it evens the source's own authoring noise (5, 15 and 25 Ma carry half the relief of 0, 10 and 20). Median over belts: 0.3–0.45 in parts of the Mesozoic, ~0.65–0.7 across 250–540 Ma, 0.75 in the Precambrian, 0.07 → 0.70 through the future. Tablelands score a deficit too (the Kalahari, the High Plains) -- relief alone cannot tell them from a schematic belt -- and are sorted out in the shader by how much relief there is to cut.
- **The relief** (`eroRelief` in FRAG): the erosion filter (Clay John 2018, Felix Westin 2023, Rune Skovbo Johansen 2026, written here from the published description). Each octave is a field of stripes running DOWNHILL, grown from jittered pivots blended as a phase vector; the next octave is steered by the slope of the terrain cut so far, so the finer gullies run down the walls of the coarser ones and meet them at an angle -- branching falls out of the steering. Eight octaves, 96 km to 0.75 km: the 96 km octave's transverse ridges are the massifs and passes along a crest, the 48 km octave the transverse drainage (outlets spaced about half a belt's half-width, Hovius 1996). Since the baked relief, only the 96, 48 and 24 km octaves are "coarse" (scaled by the deficit, so off wherever the field carries real or baked relief) and 12 km and finer are always drawn, steered by the field's own valley walls. Walls are planar (a rounded triangle wave), each pivot has its own spacing, weight and heading, and the depth varies along strike over ~450 km. Welded to the crust through the material direction, triplanar, so a valley rides its plate through playback (checked across an interval at mixf 0–1). The four coarse octaves are scaled by the deficit; the four finer ones exist in no field at any age and are grown everywhere mountains are. The depth is a share of the local relief (the envelope's rise over 60 km, or a crest's height above its surroundings), so a tableland is barely cut and a flank deeply; the steering is by the belt's own smooth slope, falling back to across-strike from `_t` on a crest line.
- **Handed to the normal once per pixel** with an analytic slope, because the hillshade stencil is blind in this band (iteration 62). Shaded at a gain that falls as the square root of the wavelength (`?eroN=`, default 100 at 96 km), and where the synthetic dissection carries a flank the envelope's own tilt is soft-compressed toward ~32° -- without that a smooth flank facing away from the sun is shade clamped at zero and no valley can show on it (§7.30). The relief's height goes into z (the snowline and bare rock follow the spurs), its height also into the albedo as tone (floors darker, crests lighter), it fades under land ice, and it may never carve new water.
- **What it replaced**: the isotropic grain in the normal fades to 30% under it (one system per band, §7.4), and the fold-axis compression of the detail noise is retired while it is on -- that compression was drawing fingerprint whorls round every high point in deep time (§7.31).
- **Cost** at 2560×1440 on the M1, live path, term on against `?ero=0`: within run-to-run noise. A first run read +0.4 ms (present-day Himalaya), +0.6 ms (300 Ma belt) and +2.4 ms (400 Ma belt); the final shader, measured while a rebuild loaded the CPU, read −0.4, −0.1 and −2.4 ms. Call it ±2 ms: the term replaces work it retires (the fold compression, most of the grain) about as fast as it adds its own. Knobs: `?ero=0` switches the whole term off (and brings the compression back), `?ero=`, `?eroN=`, `?eroF=`; `?show=10` the deficit, `11` the gate, `12` the height, `13` its hillshade alone, `14` the albedo alone, `15` the lighting alone.

The three per-pixel constructions that used to make the mountains (a ridged fBm in the
height, a `sin²(fBm)` tone band and a sine grating in the normal) are retired (WP-10 B1);
the register's iterations 51–77 had already measured that no orientation of noise produces
the organisation a range has. Ridge-and-valley now comes from a **model**, twice over:

- **The orogen atlas** (`build_orogen_atlas.py` → `web/atlas.webp`, 1.1 MB): twelve 256 km
  periodic patches eroded to steady state by a stream-power + hillslope model — six fold
  belts under striped uplift (ridge spacing 10–18 km, relief 1.0–1.6 km, phase drift and
  pinch-and-swell along strike), three dissected plateaus, three lowlands — stored as
  height and slope at 1 km per texel.
- **The fold coordinates** (`build_foldphase.py` → `_q`): the shader does not rotate a patch
  to the local strike — a patch rotated about a cell centre cannot follow a belt that bends,
  and cells meet as a quilt (measured in a numpy emulation of the first cut). Instead two
  potentials per keyframe, φ across strike and ψ along it, are fitted by least squares to
  the strike field of `_t`, and the belt patch is sampled at (φ, ψ). That is the land
  equivalent of keying the abyssal fabric to the companded crustal age: continuous by
  construction, so the ridges run along the belt and bend with it, with no seams.

In the shader the patch's height goes into the elevation (zero-mean, so snow lines, bare
rock and treelines see the ridges), its slopes into the shading normal (the hillshade
stencil is blind at 47 km), and its height into the albedo as tone (a lit ridge narrower
than a pixel averages away, a dark valley floor does not). All of it gated by the
age-relative shortening from `topo_fabric` and a 100–400 m floor. `?noatlas=1` switches it
off. Amplitudes were set on software GL at 960×600 and are the first thing to look at on a
real display.

Two things the gate alone gets wrong, and their model (WP-10 round 3):

- **A plateau's ranges are not in the DEM, and the comb was.** The belt gate opens on 94 %
  of the Tibetan interior. A DEM-driven envelope on `rug` (`reliefEnv()`, `?plat=1`) was built
  and measured out: box statistics said the 62 km slope separates interiors (0.55–0.77) from
  fronts (1.00), but drawn as a mask (`?show=4`) it is texel-scale speckle on a plateau, and
  multiplying the ridges by it re-textures them without quieting the basins; prominence at
  100 km says the Tibetan interior is a ±200 m undulation in a 6-arc-minute DEM. It ships off;
  the synthetic `basinEnv()` (`?basin=0`) remains the plateau model. What did move the plateau
  numbers was under the atlas: the fold-axis compression of the detail noise, retired
  nowhere in B1, was still combing the 40 % of `det` left under the eroded ridges. It now
  fades with the belt gate (§7.4: one system per band), which leaves band energy where it
  was and raises coherence in every belt measured.
- **An arc is not a fold belt.** `_t` carries shortening, and the Andes' Western Cordillera
  shortens as much as the Eastern, so both drew fold ridges; the western one is a chain of
  volcanoes on an ignimbrite plateau. `build_arc.py` bakes the belt type into the alpha of
  `_t` from what is already shipped — the trench segments of `plates_time.json`, the land
  mask of `_e` and the ocean-crust mask of `_o` — as the band 150–300 km behind a trench on
  the overriding side, where the point 400 km beyond the trench carries a spreading vector
  (the Nazca plate does; India, Arabia and the Persian Gulf do not, so the Himalaya and the
  Zagros stay fold belts). Where it says arc, the fold relief comes down by 0.9 and the
  dissection patches take the upland. The cones themselves want a volcanic patch in the
  atlas, which is the next model. `?arc=0` switches it off. `build_tectonic.py` and
  `rebuild_future.py` write the channel on every rebake; a `_t` without it decodes as 0.
- **The small-field stack (§7.17).** The terrain shader has 16 texture units on real hardware,
  and the per-keyframe fields had come to 20. `_t`, `_f`, `_q` and `_x` therefore share one
  1024×1024 RGBA texture per keyframe: `_f` in rows 0–511 at full width, `_t` in rows 512–767
  twice side by side (the read sits in the right-hand copy, so the dateline neighbours are the
  left copy and the wrap), `_q` at (0, 768) and `_x` at (512, 768). `stackFill()` composes it on
  the GPU as the bitmaps land — `texSubImage2D` through `copyTextureToTexture`, no canvas, so
  nothing is premultiplied and the 16-bit byte pairs survive — and it lives in `TEXCACHE` as
  `'s'+i` (4 MB, no bitmap) under the same budget and eviction as a field. A band one keyframe
  of the pair lacks is read from the other through `uStkSel`/`uStkSelB`, which is the per-field
  fallback the separate samplers had (frame 49 has no `_f`; age 0 reads frame 50's). The
  16-bit fields are read at exact texel centres, which the linear filter returns unblended.
  The warm-ahead pump composes the bands of the next keyframes' stacks the way it uploads
  the other fields, because the crossing-storm gate (`audit_perf.py`) counts every GL upload
  the crossing frame pays: a stack composed at bind time paid seven and failed the build.
- **The fold ridges ship OFF (the display review of 2026-09-03).** Looked at on the M1 at
  zoom 1.35, the belt patches read as symmetrical ribs laid over the ranges — in the Zagros
  and the Himalaya, in Tibet's basins (where `basinEnv()` made no visible difference), and
  faintly on the Andes' Pacific side even under the arc suppression; Pangaea's old belt read
  better than the young ones, which points at the erosion stage of the patches. That is a
  verdict on the model, not an amplitude, so `uFoldK` (`?fold=`, default 0) multiplies the
  whole belt relief through `atlasGate()` — ridges, tone, height and the noise fades under
  them — and `foldAt()` is skipped at 0. `?fold=1` is the round-3 look for the next mountain
  round to compare against. The plains dissection and the erg lineation were judged mild
  improvements at twice their first cut and ship at that: `gd*3.2` / `dr.x*0.32`, corridor
  `*6.0`, crest `*1.0`, `ampE=gErg*4.4`.

### 5.11 The Atlas port: the time preview, the ground cache, the temperature graph

Three things came over from Tectonic Atlas (September 2026), selectively — its lighter renderer, field subset and mesh caps did not, and the terrain shaders are untouched.

- **The time preview.** A seek to an age whose fields are not resident used to leave the previous world on screen under the new age until the pair arrived. Now `bindTextures()` keeps an explicit account of what the picture shows against what the age asks for (`APP.surface()`: `full`, `sheets`, `still`, `preview`, `stale`) and draws the requested age at once from a 4096 × 2048 atlas of 256 × 128 thumbnails of all 251 shipped sheets (`web/imagery/timeline-preview.webp`, built by `build/build_timeline_preview.py` from `web/sheets/` and hash-checked against them at every build). Within two keyframes a resident neighbour is the better stand-in (the scrub stepping of July 2026, now also for short jumps); where the pair's sheets are already resident and the footprint allows them, they are (their colour is the requested keyframes; the stale height can at worst turn a coastline pixel into a plain blend). The readout says *Loading terrain* while a preview or a still shows and *Refining detail* while a bound pair's other fields land. The preview has no height, no warp and no detail; it is loading feedback and is never the settled picture. **The core of a pair** (round 2): the switch from the preview to the terrain shader waits for elevation, rainfall, lakes, surface process and ocean structure of both keyframes and the interval's displacement and plate slots (`coreKinds`), not for elevation alone, which had put a new coastline over the previous age's lakes, drainage and abyssal fabric for the next second — the "unfinished frame". And **playback waits** for the next pair's core the way it waits for a late sheet (capped at 1.5 s, the decodes asked for at essential priority), so continents drift instead of snapping to a still and back.
- **The ground cache.** Paused with the weather moving, the terrain shader was being run over every pixel 24 times a second to redraw a ground that had not moved. `drawScene()` renders everything but the cloud layer into a render target of the canvas's own size whenever anything that draws it changes (`groundSig()`: age, camera, view, path, every bound sampler and uniform, overlays, quality, viewport), refreshes it one strip in sixteen per weather frame so the sea sheen keeps moving, and composites the clouds over it. Nothing is drawn at a lower resolution; with the clouds off or anything else in motion the cache stands down and the frame is rendered exactly as before, which is what keeps the cloud-off picture identical (`build/verify_diff.py`). Bounded at 96 MB of render target; `?groundcache=0` disables it.
- **The temperature graph.** The Conditions readout carries the timeline's `gmst` column across the whole span — 1000 Ma at the left, the present 80 % across, +250 Myr at the right — as a polyline through the 251 records (never a spline, which would invent overshoot) on a fixed −50…+40 °C scale that widens rather than clips. The marker, the value and the accessible description move with the age, and only then; the values are the inherited model's, the readout's caveats stand. Built once as a sibling *after* `#env`, which `updateReadout()` replaces many times a second.

- **Round 2 (the same evening): time that waits, and a sheet set the wide view can use.** The owner's screenshots at 608 Ma showed the wide view as an unfinished frame beside the close view, and continents that jumped while time ran. The wide view was the 2048 sheet set drawn at 1.75× magnification on the stepped-down render scale; the app now ships the 4096 set (§5.9) and engages the sheets eagerly once the governor has stepped down or the quality is pinned below Full. The jumps were time advancing into a pair whose fields had not landed: `coreKinds` (elevation, rainfall, lakes, surface process and ocean structure of both keyframes, the interval's displacement and plate slots) gates the switch from the preview, and playback **waits for the next pair's core on both paths** (`_fieldHolds`, capped at `HOLD_MS` = 3 s the way `_liteHolds` waits for a late sheet — 1.5 s let a loaded machine advance into a still; the preview gives up after 6 s and binds progressively). No frame moves time by more than 1.5 Myr (`MAX_STEP_MYR`, 0.3 of an interval): at the default 3 Myr/s the half-second cap on `dtT` already held it there, so only fast playback on slow frames now runs below the slider, smoothly, where a 300 ms frame at 10 Myr/s used to leap 3 Myr. Shipped 4096 sheets upload in sixteen strips — two a frame while the picture has its sheets, up to eight by the frame's length while it is waiting for one — the mip chain once at the end; a rule that scaled with the frame's length alone fed on itself, a slow frame allowing five strips that kept it slow. A shipped sheet whose fetch failed is retried and never baked in the app: falling through to the bake cost 1.8-second frames (four strips of an 8-megapixel terrain render each) in the first playback test, and `APP.sheets.status().bakes` now counts bakes, which a shipped site keeps at zero. And the crossing hitch playback had always carried went with this round: the 256 × 128 CPU elevation raster the labels snap to was drawn from the keyframe's full 4096 × 2048 bitmap on the spot, a 33 MB GPU-to-CPU read-back on the main thread once per keyframe (a crossing with no uploads at all cost 316–387 ms in the storm test, and one sheet-path playback frame in twenty was that size); `elevField` now builds it off the main thread from a resized decode of the same bytes, and readers get null until it lands, as they did while the elevation was in flight. The clouds ride the running timeline and evolve (§5.7).

**What it measured** (the M1, `build/verify_run.py` driving `web/_verify.html` on the real GPU, the frozen pre-port page through the same driver back to back; another session's headless Chromes shared the machine, so absolute frame times are an upper bound and the ratios are the result):

| | before | after |
|---|---|---|
| cold seek to full detail, 1000 → 0 / 300 / −250 / 700 Ma, warm localhost | 6.6 / 8.8 / 6.0 / 3.4 s, the previous world shown throughout | 0.56 / 0.24 / 0.24 / 0.24 s, the preview within 20–74 ms |
| the same with a 600 ms delay on every field fetch | 6.6 / 7.1 / 5.7 / 6.1 s | 0.83 / 0.90 / 0.94 / 0.93 s |
| fast-scrub release to render | 730 ms | 10 ms |
| keyframe-crossing storm gate | ≤ 2 uploads | ≤ 2 uploads |
| playback coherence at 18 Myr/s (`uWarp`/`uMat` live) | 100 % | 100 % |
| sheet-path playback, 10 Myr/s, 600 ms sheet delay | 0 held frames | 5 of 2760 |
| working set over 90 s of far jumps | 949 MB cache, ~460 pinned, flat | the same, plus 139 MB of imagery (preview 64, clouds 75) |
| frame p50 at 2560 × 1440, orbital, clouds on / off | 355 / 343 ms | 344 / 328–346 ms direct; **56 ms** paused with the ground cache |
| frame p50, Himalaya at 1.35 / Andes tilted 55° | 352 / 316 ms | 350 / 307 ms direct; **29 / 30 ms** with the cache |
| cloud-off frames old against new: orbital, map, close at 2.5 Ma | — | 0.06–0.18, **0.00**, **0.00–0.03** of 255 mean |
| cloud-off close frames at exactly 0 Ma | — | 1.2–12.9 of 255: the exact-keyframe binding (§7.16), not the renderer |
| cloud motion, fixed camera: present Globe 20 s / 300 Ma Map 15 s / +250 Myr Globe 15 s | — | 25.6 / 19.7 / 20.5 of 255 mean in the crop (Atlas's own reference pair: 23.7 over 23 s) |
| round 2: the wide view at 608 Ma, zoom 3.9, sheet path against the live shader | 2048 sheets at 1.75× magnification on the stepped-down scale | 4096 sheets: 2.2–3.0 of 255 mean |
| round 2: cloud evolution, fixed camera 60 s at 300 Ma | — | 19.4 of 255 mean; masses reorganise, not translate |
| round 2: cold seek to a full core (all seven kinds) 1000 → 0 / 300 / −250 / 700 Ma | elevation alone in 0.24–0.56 s | 1.42 / 0.58 / 1.20 / 1.47 s, preview within 26–107 ms |
| round 2: playback on the sheet path, 3 / 10 Myr/s, 20 / 15 s | 21.2 fps, 50 ms a frame at 3 Myr/s (2048 sheets, no clouds) | 12.8 / 10.7 fps, 67 / 67 ms median (4096 sheets, clouds on every frame); 0 pair jumps, 0 mix-fraction snaps, 0 path flips, 2 / 12 held frames; the weather clock advanced 16.8 s of 20 |
| round 2: playback at zoom 1.6, the terrain path's zoom, 3 / 10 Myr/s | 0.7 fps at 1.55 s a frame, the terrain shader throughout | 2.5 / 3.1 fps, the sheets three frames in four once the governor stepped down; 0 jumps, 0 snaps, 1 / 3 held frames |
| round 2: the same with a 600 ms delay on every field fetch | — | 2.7 fps, 0 jumps, 0 snaps, 5 held frames |
| round 2: the wide view at 608 Ma, quality auto, 3 Myr/s | — | 12.1 fps, 83 ms median, 0 jumps, 0 snaps, 0 flips, 2 held frames |
| round 2: the most one frame moved time at 10 Myr/s | 5 Myr, a whole interval | 1.5 Myr |
| round 2: forced frame p50 at 2560 × 1440 on the sheet path — playing, clouds off / on; paused, cache off, clouds on; zoom 1.6 playing | 50 ms (2048 sheets, no clouds) | 25.7 / 29.1 / 24.7 / 18.7 ms |
| round 2: the keyframe-crossing frame (storm gate), three crossings | ≤ 2 uploads, time not recorded | 2.5 / 2.6 / 5.6 ms, 0 uploads (316–387 ms with 0 uploads before the raster fix; 355 ms with 8 before the warm rule was reverted) |
| round 2: in-app sheet bakes during playback on the shipped site | — | 0 in every run (the first cut baked a retrying sheet: 1.8 s frames) |
| round 2: smoke test | 32 / 32 | 32 / 32 |

The rAF frame interval of sheet-path playback (67–83 ms median here, against 25–29 ms for the forced frame) is the per-frame work of playback — the warm uploads for the terrain material, which binds on every path, two sheet strips a frame and the decodes' insertions — on a machine another session's Chromes were also using; one frame in twenty is 250–300 ms. Lazy binding of the terrain material while the sheets draw is the lever left.

### 5.12 Close zoom and colour (3.15)

At zoom 1.35 a pixel is ~0.85 km and a texel of the elevation field 8–11 pixels, so close zoom is whatever the shader invents below the grid. Drawn with the colour taken out (`?show=15`), the land was covered in soft 5–50 km clouds of light and shade -- the Po plain as thickly as the Alps -- with whole patches clamped flat at the shade floor. Four things made them, and none was a slope of any surface:

1. **The detail's slope was a difference of noise.** The land gradient differences base AND procedural detail over ±23.5 km; for the base that is a gradient, for the detail's octaves finer than the baseline it is two unrelated samples of noise. As the footprint shrinks (`gNearW`, 1 below a ~2.5 km footprint, 0 past 6; `?near=` `?nearK=` `?nearA=` `?nearB=`) the far taps read the base only and the detail joins through its own forward difference over ~0.7 of a pixel, at 0.35 of the base's exaggeration. Both latitude branches; set inside one, everything above 63° kept the clouds (§7.46).
2. **The grain was random tilts.** The land grain perturbs the normal with independent value noise at 44, 16 and 6 km: a pixel-wide texture at globe zoom, 20–50 px clouds at close zoom. The two coarse octaves stand down with `gNearW` and the 6 km one halves (`?ngC=` `?ngF=`).
3. **A shadowed flank was one tone.** `hs` clamps at zero, so every face turned more than ~51° from the light shaded exactly the floor. Land keeps 0.3 of the cosine below zero (`?shF=`), measured against the smooth normal the erosion relief is cut into (`nrmS`), so a smooth flank in shadow keeps its old floor and only the walls cut into it vary around it. Measured against zero, east Baffin went darker as a slab (dark pixels 0.1 → 4%).
4. **The relief below the grid was a fifth of real.** The erosion relief halved its amplitude per octave all the way down, which left the 6 km octave at ±60 m in the Alps where real relief inside a 10 km cell is ±400; the snowline, bare rock and treeline followed smooth contours. The sub-grid octaves now have their own spectrum: 12 km at 1.5× the old, 0.78 per finer octave (`?eroB=` `?eroR=`). The anti-alias ramp stays at 2.2–4.5 footprints (`?eroFa=` `?eroFb=`): 1.8–3.6 draws the 3 km octave at the closest zoom, and cost +3.5 ms a frame at 2560×1440 on the M5 Ultra (14.7 → 18.3 ms, median of three) for a finer grain on each wall. With the old ramp the new close-zoom frame measured the same as 3.14's (14.8 against 14.7 ms); mid and globe zoom draw from the sheets and are untouched.

**Colour.** The blocks on the Canadian prairie were the elevation codec (§7.44): AVIF transform-block edges carry ~1 code (0.96 against 0.31 inside a block, 3.1× at 16 texels), `rug` read them, and at the prairie's 350 m aridity-lowered treeline its bare-rock gate painted alpine scree in rectangles. Decisions by relief read `rugC` (1.5 codes allowed); the hillshade and the detail's amplitude keep `rug` (half a code), which plateaus need. And the band between the cold treeline and the one drought lowered now asks for a range's relief (`rugC` 0.30–0.60) -- past a cold treeline a hill is alpine, past a dry one only a mountain range is; a dry plain is steppe, and the biome colour already says so. The dry Andes keep their bare cordillera. **Arid basin floors are pale** (`?floor=`): flat dry ground standing below the mean of the four ±137 km taps takes a pale alluvium, paler toward a playa, under the ergs and hamada and off the high plateaus (2.2–3.4 km fade). The local-low test for marsh and rivers allows 1.25 codes for the same reason as `rugC`.

**What the renderer cannot fix.** BC's ranges draw brown where they are forested to the treeline, the Ganges plain orange, and Tibet's snow sits on the plateau instead of the Himalayan crest: the present-day rain field reads 0.024 over the Columbia Mountains (real ~0.30), 0.03–0.12 on the Ganges plain and 0.000 on the Himalayan crest against 0.005 on the plateau, so the ELA's aridity term is maxed on both and latitude alone puts the snowline lower on the plateau. That is the climate solve's highland dry bias (§9), and the lever that would fix it globally is the one that keeps Pangaea dry.

## 6. Build and deploy

```bash
cd build
python check_shader.py && python build_site.py
```

then commit and push to `main`. GitHub Pages serves `main:/docs`.

**Editing the page.** The shaders are edited in `web/shaders/*.glsl`; `check_shader.py` validates them, counts the texture units each shader reads (16 is the hardware limit, §7.17) and writes `web/shaders.js`, which `index.html` loads in development and `build_site.py` inlines for the site — so a shader edit is `edit the .glsl → python check_shader.py → reload`. The two noise variants (`VN_OLD/VN_NEW`, `CN_OLD/CN_NEW`) live in `app.js` and are spliced in at run time where the sources carry `/*@vnoise*/` and `/*@cnoise*/`. The application is `web/app.js`, the styles `web/style.css`; `index.html` is markup only.

**Hosting the textures off the repository** (WP-10, D4). `docs/fields` and `docs/sheets` are the repository's weight. `publish_assets.py --release TAG` uploads them to a GitHub release (or `--dir PATH` copies them into another Pages repository), and `build_site.py --field-base URL --sheet-base URL` publishes a site that fetches them from there, keeping only the manifests in `docs/`. Each base is the directory the files sit in; `?fieldbase=` and `?sheetbase=` on the page override them for a test. Whether to rewrite history so the old copies leave the repository is a separate decision.

`build_site.py` now **runs the validators first and refuses to publish if one moved backwards**. They are read-only and take a few seconds:

```bash
python audit_all.py           # all of them
python audit_all.py --quick   # skip the pyGPlates ones (~2 min)
```

| check | baseline | what it catches |
|---|---|---|
| `audit_cards` HIGH / MED | 0 / 0 | factual errors, unhedged contested claims, date drift, coverage gaps, anachronistic vocabulary |
| `audit_label_windows` | 2 | a label drawn when the entity it names did not exist |
| `audit_curated_biota` | 11 exceptions, 0 conflicts | a curated locality the province model would overwrite, or one whose flag disagrees with what it is |
| `audit_biota` — 14 hard checks | 0 each | per card-age: an organism outside its lifetime, off its crust, outside its own range within a region, under a drawing its classification contradicts, unregistered, or undrawn; a land card with fauna and no flora or the reverse; fewer than four organisms without a stated reason; a label with no home crust; a card missing; land life on ground the DEM draws as deep sea |
| `audit_biota` — parent-form drawings | 0, may only fall | a taxon drawn with its parent form's icon because its own has nothing to trace: 33 in 3.5, 0 since the last seventeen forms were drawn by hand (`fix_form_icons.HAND`) |
| `audit_label_plate` | 0 | a plate-tracked label whose coordinate is on a different continent from the one its text names — or, since 3.7, from the home crust the biota registry gives it (`biota.LABEL_HOME`), which needs no text: six palaeo-frame labels on modern land were riding the wrong continent |
| `build_site` fetch targets | refuses | every file the pages fetch by name, every script tag, and every per-keyframe field the app derives from the timeline (2,258 names), unless the entry declares it absent (`timeline[i].no`) |
| `climate_audit` | 1 (an INFO check that PASSES) | the GMST/CO₂/O₂ table against PhanDA and Krause |
| `ice_audit` | 0 of 23 outside range | drawn ice area against the literature, per keyframe |
| `regression_gate` | 0 true regressions | a feature the frame switch made worse |

The baselines are not all zero and should not be — two label windows are genuine open disagreements about when Gondwana and Kazakhstania become identifiable. The rule is that **none of them may move backwards**; when one legitimately improves, tighten the baseline in the same commit, so the ratchet turns one way only. `SKIP_AUDIT=1` overrides, deliberately awkwardly.

**Adding or correcting an organism.** Edit or add a batch in `build/taxa_src/` (one `E(...)` line per taxon; existing names are skipped, never overwritten), run it, then `python taxa_src/ranges_within_regions.py`, then:

```bash
python biota.py --check                       # schema, form-vs-classification, range-vs-PBDB
python biota.py --card "Lake Titicaca" 0 3    # compose one label at some ages, no rebuild
python build_silhouettes.py registry          # own silhouettes for new genus/species (network)
python -c "import build_webdata as b; b.build_life()"
python audit_biota.py -v                      # the gate, with detail
python verify_cards.py tag "Label@age" ...    # look at the cards -> build/verify/cards_tag.png
```

Common targeted rebuilds:

```bash
ONLY_AGE=300 python reskin_seafloor.py     # one keyframe, quick visual check
python reskin_seafloor.py                  # _e and _o for all 251 (~40 min)
python relief_deficit.py -j 4              # the relief deficit into B of every _f (~2 min); --stats, --calib
python bake_relief.py                      # the mountain relief into _e/_o, 55-1000 Ma + future (~25 min, 12 workers)
python rederive_fields.py                  # then everything derived from _e, with a census (~15 min)
python rebuild_future.py                   # the 50 future keyframes (~45 min); then their _d, _w, _f, _q, _x
python build_webdata.py                    # labels, timeline, boundaries, life
python build_foldphase.py -j               # fold coordinates for all 251 (~2 min on three cores)
python build_drainphase.py -j              # drainage coordinates for all 251 (~5 min on three cores)
python build_arc.py                        # the belt-type alpha of _t for all 251 (~1 s each); --stats 0 lists what it flags
python build_orogen_atlas.py               # the sixteen atlas patches (~1 h) and web/atlas.webp
python emulate_fold.py 0 44 58 26 36 z.png  # draw the atlas at (φ, ψ) over a window, no browser
python bake_sheets.py                      # world sheets for all 251 (needs a GPU; §5.9)
python bake_sheets.py --width 2048         # the lean set the ambient build runs on
```

`stamp_data_version.py` bumps `DATA_V` in `app.js` **before** the page is assembled. This is not optional: Pages serves the JSON with `max-age=600` and an ETag, and a returning viewer can sit on a cached copy well past that window. The failure is silent — the app runs perfectly and shows yesterday's data. It has happened three times, on `labels.json`, `plates_time.json` and `life.json`, and each time it looked like the deploy had never landed.

Verify the live `DATA_V` after every push.

---

## 7. Traps

### 7.1 Shader traps — the black globe

Run `check_shader.py` before any shader edit ships. It catches every failure mode that has actually occurred here, all of which present identically: the page loads, the panels and labels render, the console says nothing useful, and the globe is simply black.

- **A backtick anywhere in shader source**, including inside a comment. It closes the JS template literal. This has happened three times.
- **GLSL reserved words as variable names** — `patch`, `flat`, `sample`. The compiler says `'flat' : syntax error` and nothing else.
- **Use before declaration** inside `main()`.
- **A function called above its definition.** GLSL has no hoisting; `basinEnv()` calling `vnoise3()` from above the injected definition cost a full render sweep (2026-09-02). The check knows where the noise variants land.
- **Duplicate declaration at the same scope**, and unbalanced comments or braces.

Chain it: `python check_shader.py && <rebuild>`, so a bad shader blocks the build.


**Occurrence five, 2026-07-28.** Writing `` `rwt` `` -- prose backticks around an identifier -- inside a shader comment. Ten of them in one comment block. `check_shader.py` caught it immediately and named it; without that the globe goes black and the cause is three edits back. The rule has no exceptions: **no backtick ever appears between the FRAG backticks**, not even quoting a variable name.
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

`shelfHi` and `prom` decided whether there is a shelf above this slope, and how high the ground stands against its surroundings. Both were RANK statistics -- second highest and second lowest -- over four elevation taps due N/S/E/W at a fixed 16-texel radius.

A rank statistic is **not a smooth function of position**: it switches which sample it is reading. Its contours therefore take the shape of the stencil, and with the taps on a cross that shape is a cross -- so a margin running diagonally came out as a flight of stairs with square 90-degree corners a tap-radius (about 1.4 degrees) on a side, and the same steps appeared in the abyssal shading through `prom`.

It is the stencil, not the data. Two offline checks settle that: thresholding the shipped field directly gives a smooth curved coastline and shelf contour, and dropping the tap radius from 16 texels to 4 turns the same boundary on the same field from right angles back into curves. Note this is a SEPARATE artefact from 7.13 -- that one is four pixels wide and comes from the codec, this is tens of pixels and comes from the shader. Fixing the first did not touch the second, and it is worth measuring the step size before assuming one cause.

**Two plausible fixes were tried and both failed**, which is the part worth keeping:

- **Spinning the cross** by a smooth noise field, so no contour can follow a texel row. It replaces the staircase with a RAGGED edge. Randomising a stencil does not smooth it -- it makes the boundary wander at random, and on the continental slope that read as visibly jagged. Shipped briefly and reverted.
- **A rank statistic over eight taps** instead of four. It trades square steps for octagonal ones, which is exactly what it should do and is not what was wanted.

What works is to **stop ranking**. Eight taps on a ring, combined by one step of iteratively-reweighted least squares: take the plain mean, re-weight each tap by `1/(1+((t-m)/900)^2)`, take the weighted mean. That is smooth in all eight inputs, so its contours are smooth, while a lone outlier still loses its vote -- a seamount 3.5 km above the plain around it keeps about a sixteenth. Verified on synthetics against the old cross: an isolated seamount leaves the shelf gate at **0.0%** under both and a broad margin fires it over **50.0%** under both, so the four-dot fix this replaces is fully preserved.

`shelfHi` is that robust mean **plus 900 m**, and the offset is calibrated rather than guessed: a mean sits lower than a second-highest, and +900 is what makes the gate fire over the same 7.7% of sea floor it did before, measured on the shipped field. That is what keeps the shelf and canyon detail as broad as it was. `prom` keeps its distribution too -- standard deviation 298.4 m before, 298.3 after.

The wide gradient stays on the two cardinal pairs: a central difference is a smooth linear operator and never had this problem.

### 7.15 One control for two quantities means neither can be right

`handoff_blend` cross-fades the real 540 Ma DEM into the generated Precambrian world, and a single `wq` drove both what the ground looks like and how much of it is land. Those want opposite ramps:

- The 540 Ma DEM is a snapshot of one instant. Held at two-thirds weight 20 Myr away, it put **-3640 m of ocean** under Siberia's label, which by then had moved with its plate -- so a continent appeared to swim across the sea and its name swam with it. That wants a SHORT ramp.
- Land fraction wants a LONG one. Shortening the single ramp to 20 Myr sent land 18.5% -> 28.6% -> back to 24.1%, which is the same "continents flood then a continent arises" artefact this function was written to kill, running backwards.

Split them: geometry on 20 Myr, land fraction on 110 Myr, with the re-levelling shim now running at `wq >= 1` too (returning `B` early is what made the land curve step). Both come right at once -- land rises 18.5 -> 24.4% monotonically and both labels sit on land at every age.

Two related traps came out of the same hunt. **A label's track is not linear in time**: Siberia barely moves 540->560 and then sweeps 60 degrees by 600, so pinning the ends of the handoff window left the interpolation 23 degrees ahead of it in the middle -- more than the craton's own radius. Pinning the ends of a window says nothing about its middle. And a verification that RE-DERIVES geometry can repeat the very error it is checking for: the first "on land at every age" result was produced by a broadcasting bug and was wrong. Sample the shipped texture instead.

### 7.16 The harness on software GL

Every render in WP-10 rounds 1–3 was taken headless on SwiftShader, which is pixel-faithful
and slow in ways that look like hangs. The rules that came out of it, each after it cost time:

- **A page load is seven minutes of compile and a framing two to three** — and *anything else
  running on the machine doubles both*. A numpy bake beside Chrome took a framing from three
  minutes to eight (2026-09-03). Serialise: bake, then render, then measure.
- **Wait on a PID or a marker file, never on a process pattern.** `pgrep -f "node shoot.js"`
  and `pkill -f` both match the shell that runs them when the pattern is in their own command
  line, so the wait never ends (§7.11). The round-3 runner waits on the expected PNGs by name and
  kills Chrome by the PID it launched.
- **Freeze the page for an A/B.** A knob sweep is several page loads, and any shader edit
  between them changes what "baseline" means. Copy `index.html`, `app.js` and `shaders.js` to
  `_old.html` / `_app_old.js` / `_shaders_old.js` (gitignored) and point the driver at it with
  `?app=_old.html`; the new page and the frozen one then render the same fields through their
  own shaders, in any order.
- **The driver forwards every query key it does not consume**, so `?erg=0`, `?plat=0`, `?arc=0`,
  `?basin=0`, `?atlasN=` and the rest run through `_verify.html?shots=` unchanged; and
  `?quick=1` skips the camera-still loop (the camera is derived from the state, there is no tween
  to wait for) and waits on field residency instead — two renders a framing instead of six.
- **Two renders of the same page differ** by up to 0.85/255 mean under contention (round 2), so
  an A/B number under about 1/255 is inside the harness unless the pair was taken back to back.
- **An empty framebuffer from `APP.snap` can be a one-off** under contention; re-run before
  reading anything into it.
- **At an exact keyframe age the bound pair WAS (the next younger keyframe, this one).** Age 0
  interpolated frames 49 and 50 at t = 1, and the interval kinds (`_t`, `_f`, `_v`, `_p`) bound
  from frame 49 — `fut_0005`. A field baked for "age 0" alone was therefore not the one the
  shader read at age 0: the first belt-type A/B (round 3) came back null for exactly this
  reason. Since the Atlas port (September 2026) `frameAt` is a binary search and an exact
  keyframe is itself alone ({i, j: i, t: 0}), so age 0 binds frame 50 (`phan_0000`) with no
  warp and no interval. An age strictly inside an interval still binds the interval kinds from
  its younger keyframe.

### 7.17 Sixteen texture units

A fragment shader gets `MAX_TEXTURE_IMAGE_UNITS` samplers: 16 on Apple silicon (ANGLE over
Metal), on most desktop GL, and as the WebGL2 minimum. The SwiftShader the WP-10 rounds were
reviewed on (§7.16) reports 32, so the five samplers rounds 2 and 3 added — the fold and
drainage coordinate pairs and the atlas — took the terrain shader from 15 units to 20, linked
there, and failed on the M1 at the first framing of the deploy review: one console line,
`FRAGMENT shader texture image units count exceeds MAX_TEXTURE_IMAGE_UNITS(16)`, and a black
globe under a page that otherwise worked (2026-09-03).

The fix is structural (§5.8): the four small per-keyframe fields — `_t`, `_f`, `_q`, `_x` —
share one 1024×1024 texture per keyframe, packed on the GPU from the decoded bitmaps
(`stackFill()` in app.js; `stkTect()`, `stkFore()` and `foldTaps()` in the shader), which
returned the shader to 16 units with the atlas and the noise lattice kept. `check_shader.py`
now counts the samplers each shader reads and refuses above 16, so a shader that would fail on
real hardware cannot pass the build again; `?show=8` and `?show=9` draw the packed fold and
drainage coordinates as sawtooth ramps, which read as clean bands when the 16-bit decode is
exact and as speckle when a tap has blended bytes.

The lesson is the one §7.12 and §7.16 already carry: a review environment is a proxy, and every
limit it does not share with the hardware is a blind spot. Units, precision, extensions,
maximum texture size — the list of what the harness differs in wants writing down and checking
in the build, not discovering per deploy.

### 7.18 A fallback that always succeeds hides every omission

The old icon binder matched name substrings and, failing that, drew any land organism as a small
reptile and any sea organism as a fish. It never failed, so nothing ever reported that *Ursus*
had matched a coyote, that *Megatherium* and the South American hoofed mammals had matched
nothing and fallen through to a rodent-like default, or that kelp was a fish. The same shape
produced the misplacements: a province's marker list had no time and no place on it, so there
was nothing to check Bison-at-60-Ma against. **A value with no declared lifetime, place or form
cannot be wrong in any way a script can see.** The registry makes each of those a field, the
binder has no fallback (an undrawable taxon fails the build), and the approximations that remain
are declared and counted. When adding a default, make it loud and make it countable.

### 7.19 "Everywhere" is three different claims

`cosmo` on a land taxon was read literally and put ants, termites and dragonflies on Kerguelen,
frogs and water lilies on the Antarctic ice sheet, and bony fishes on the Seychelles. A
world-wide range means the inhabited continents; it does not mean mid-ocean crust, ice sheets or
polar desert, and a generous wildcard is exactly where a generous default does its damage
(§7.18). The three rules in `biota.at_home` and `is_polar` each have a date on them, because
each was false before it was true: Antarctica was forest, the High Arctic was forest, and
Mauritia was part of Madagascar.

### 7.20 A point is not a footprint, and a box has corners

Region codes turned out continent-sized, so endemics leaked across them; the first fix — a
lon/lat `box` per taxon against the label's point — leaked at the corners: a rectangle round
Amazonia contains Lake Titicaca. What worked was three things together: an anisotropic reach per
label (the Himalaya is 2,400 km by 200), habitat that knows altitude (a lake at 3,800 m is
`alpine`, not a lowland wetland), and an explicit `avoid` for neighbours two degrees apart.
**Review the output listing, not the rule**: every round of this was found by printing
"taxon → labels it lands on" for the present day and reading it, never by reasoning about the
filter.

### 7.21 Evidence databases have homonyms and coarse bins

The PBDB resolved *Acanthostega* to a bryozoan, *Knightia* to a gastropod, *Mauritia* to a
cowrie and *Archaea* to a spider; PhyloPic does the same for silhouettes. Raw first/last
appearances are set by single outliers and by occurrences binned to a whole period, so robust
dates are the 4th–96th percentile of occurrence midpoints. It files most non-mammalian synapsids
under class "Osteichthyes". Treat a database as a witness to cross-examine: match on
classification as well as name, and let an authored `cls` replace the record outright.

### 7.22 A note written for one card is shown on every card

A registry note is displayed wherever the composer places the taxon, so "a fanged fish of the
interior sea", "the likely source of the Red Sea's name" and "primate hands begin here" each
turned up on the wrong ocean or continent. Registry notes are place-neutral by contract; the
sentence about a taxon at a place lives in that label's curated list, and the app applies it
only in the runs where the taxon is curated there (`run[6]`).

### 7.23 Headless Chrome for DOM proof

`file://` URLs containing a space are mangled (this project's path has three): render from a
space-free temp dir. `--headless=new --screenshot` does not exit on this machine: wait for the
file, then kill the PID you launched, never a pattern. Booting the whole WebGL app to reach a
DOM panel costs ten minutes of software GL; lifting the app's own functions out of `app.js`
by name and running them against the real JSON and CSS proves the same source text in seconds
(`verify_cards.py`).

### 7.24 A palaeo coordinate on modern land is tracked on the wrong continent

`build_labels` plate-tracks any coordinate that is land today. A label authored where its
feature sat in its own era — the Gilboa Forest at its Devonian position, which is Brazil now —
passes that test and rides South America to 85°S. Nothing complains: the label draws, moves,
and looks plausible. `audit_label_plate.py` caught eleven by reading continent names out of the
descriptions; eight more had descriptions that named no continent. The second detector needs no
text: the biota registry already records each palaeo-frame label's present-day home crust
(`biota.LABEL_HOME`), and a tracked coordinate outside its own home is the defect. **Two
independent statements of the same fact, kept for different reasons, are a check on each other.**

### 7.25 Two provinces with one name are one province

`provinces.py` keys provinces by name. The Late Palaeozoic and Mesozoic marine schemes both
produced a "Tethyan Realm", and whichever was registered first supplied the paragraph for both:
the Pennsylvanian Absaroka Sea was headed with Cretaceous rudist reefs. A name that is a key must
be unique across every scheme that can emit it.

### 7.26 A batch writer that regenerates its file throws away what tools attached

`taxa_src/*.py` write their registry file from scratch, which is what makes them the source of
truth — and what silently discarded the PBDB evidence, the reviewer's `pbdb_ok`/`place_ok`
verdicts and every hand edit on the next run. The writer now carries a whitelist of
tool-attached keys forward from the previous file, and every authored change goes back into the
batch source, never into the JSON alone.

### 7.27 A coordinate on the right crust can still ride the wrong plate

The Tethyan Himalaya label sat at (88, 29): Indian rock by every description, and `pbdb.region_of`
agreed, so §7.24's detector passed it. But plate polygons have edges, and that point is 30 km
north of the Yarlung suture in the rotation model's static polygons — on the Lhasa terrane. At
110 Ma the card stood at 12°N showing India's fauna while India was at 43°S. The present-day
check cannot see it; the plate id can. The third detector in `audit_label_plate.py` maps each
label's home codes to a continent and holds the tracked point's plate block against it. **A
present-day test of a present-day fact says nothing about the track; test the thing that moves.**

### 7.28 A name resolved by nearest neighbour drifts with the neighbour

The province model keys its best provinces on the BLOCK a label stands on, matched by exact name
first and nearest reconstructed anchor second. "Amuria" is not the model's "Amuria / Mongolia",
so it fell to nearest-anchor; the label at 122°E tracks with North China in the rotation model,
and North China's anchor was nearer at 265 Ma than Mongolia's. The card's banner read *Cathaysian
Province* over an Angaran list. `provinces.LABEL_BLOCK` names the block for the fifteen labels
whose names differ from the model's. **When two systems name the same thing differently, write
the alias table; a fallback to "nearest" is a guess that changes with the age.**

### 7.29 A repeated key in a dict literal keeps only the last entry

`taxa_src/ranges_within_regions.py` grew round by round as one `PATCH = {...}` literal, and a
name refined in two rounds was written twice. Python keeps the last: Quercus lost its
present-day box the round it was given a time-sliced range, Streptelasma its latitude band when
it got a range. Nothing warned; the earlier field was simply gone from the next regenerated
file. Fifty-one names were affected. The table is now read from its own source with `ast` and
duplicates are merged field by field, later over earlier. **A literal that is appended to is a
log, and a log needs a merge rule; a language that silently discards the earlier entry will not
supply one.**

### 7.30 A dark face can be clamped shade, not colour

The Palaeozoic "prisms" looked like a two-tone albedo -- one flank dark brown, one tan -- and
the first erosion relief changed the dark face by nothing. `?show=14` (the albedo alone) and
`?show=15` (the lighting alone) split it in one render: the belt's colour was one uniform
grey-brown, and the dark face was the hillshade CLAMPED AT ZERO. The base lights its 47 km
stencil at ~156x, so any smooth flank steeper than about half a per cent that faces away from the
sun is tilted past the sun's 39 degrees and is uniformly black, and nothing added on top can turn
a facet back into the light. **When a surface does not respond to a change in its normal, look at
the lighting alone before the colour: a saturated multiplier hides everything under it.**

### 7.31 Rescaling an absolute coordinate by a varying direction makes whorls

The fold-fabric compression in `elevDetail` stretched the noise along strike by rewriting the
ABSOLUTE material position, `d - gFold*(dot(d,gFold)*k)`. Where the strike field curves -- the
contours round a dome, a crest's end -- a rotation of a hundredth of a radian moves that point by
nearly a noise cell, and the noise wrapped into concentric fingerprint whorls round the high
ground. They survived every knob anyone thought to try (`?plainsK=0`, `?nodrain=1`, `?erg=0`)
because none of them owned the term. A domain transform must be applied to the LOCAL offset about
a point that does not move, or be keyed to a field whose value varies smoothly (a potential, the
way `_q` is), never to the global position under a rotating frame.

### 7.32 A medial axis grows an arm to every bump of its outline

The future's collision ranges are built along the medial axis of each overlap zone, and the
first cut drew starfish over North Africa and Siberia at +150 Myr: a crenellated, roundish zone's
skeleton sends an arm into every lobe of its edge. Two fixes, both needed: smooth the outline
first (1.3 degrees), and keep only the SPINE -- axis points where the zone is at least 0.75 as
thick as its thickest part within 3.5 degrees, since an arm into a lobe thins as it goes.

### 7.33 A rotation axis written in one frame and applied in another

The pop-in. `platerot.json` stores each plate's rotation to 0 Ma as an axis and angle in z-up
geography, (cos lat cos lon, cos lat sin lon, sin lat), and `build_platefield.py` computes it that
way; the shader's `dirFromUv` is y-up with latitude mirrored, (cos lat cos lon, −sin lat, cos lat sin
lon). The axis went to the GPU unmapped, so every keyframe's "material coordinate" was a rotation
about the wrong axis and no two keyframes agreed on where a piece of crust was. Every crust-keyed
texture -- the erosion relief, the lithology tint, the detail noise -- jumped at every keyframe,
by hundreds of kilometres in deep time, for as long as the feature (H2) had existed. Measured with
`?show=16`, which draws the material coordinate itself: 25 levels of change across the 405 Ma
crossing against 2.6 for an ordinary step; with the axis mapped (x, y, z) → (x, −z, y), 1.9 against
2.8. A second, smaller part: mid-interval the rotation was applied to the pixel's own direction
rather than to where its crust sat at keyframe A (`gMatOff`, `?matoff=0` for the old behaviour).
**Any vector that crosses from Python to GLSL crosses a frame: write the mapping down where the
data is loaded, and test continuity on the quantity itself, not on a render built from it.**

### 7.34 A roughness test is fooled by one sharp line

Scotese ran a narrow band of ±100 m noise along each schematic crest. An RMS over a ~120 km window
read that single line as a rough belt, so the relief deficit said nothing was missing exactly on
the crests -- the one part of a prism that most needed relief -- and the first bake left every
crest a prism (the weight map showed holes along each one). The mean absolute value discounts a
sparse line (real terrain's is a steady 0.68 of its RMS at every height), and the past is now
decided by age rather than by any local test. **A statistic that squares its input is ruled by its
rarest values; when the thing to detect is "a smooth surface with one sharp feature", square
nothing.**

### 7.35 The control for synthetic terrain is the real terrain, degraded and regrown

Every synthesis this project has drawn was judged against what it replaced, and each looked like
an improvement. The control that finally calibrated the baked relief was to blur today's belts to
an envelope (a 60 km gaussian, the scale of Scotese's), run the whole bake on them, and put the
result beside the real Himalaya, Alps and Andes in the app. It exposed four defects no before/after
could: the amplitude normalised over too small a window (real relief is patchy), tables that ignored
regional slope (plateaus came out as rugged as flanks), a distribution that was Gaussian where the
real one is heavy-tailed, and "strike stripes" that drew worms. **When the question is "does it look
real", the reference must be the real thing put through the same pipeline.**

### 7.36 A quantile table must carry the tails that make the character

The first distribution map stopped at the 0.5th and 99.5th percentiles and clipped beyond them. On
real relief those tails are where the character is -- the finest band's 99.99th percentile is +11
standard deviations, its kurtosis 18 -- so the synthesis was capped at kurtosis 4 whatever else was
done. The table now runs from the 0.01st to the 99.99th percentile, and the map is fitted where the
table was measured (belts over 900 m), not over every upland, which had put the extremes in the
foothills.

### 7.37 Averaging a drained surface dams it

The baked relief drains everywhere by construction, and the lake bake still filled its valleys with
lakes -- 1% of the 400 Ma belts, against 0.19% before, and different lakes at each keyframe. The
lake bake reads the elevation at half resolution through PIL's bilinear filter on the 8-bit
encoding, and averaging a narrow gorge's walls into its floor raises the outlet above the valley
behind it: every narrow outlet becomes a dam at the coarse scale. Checked where the consumer reads
(`relief._lake_view` reproduces the resize and the encoding) and filled there; the source's own
basins are kept. **A property guaranteed at one resolution is not guaranteed after resampling;
check it where the consumer reads, through the consumer's own path.**

### 7.38 Python's `hash()` of a string is salted per process

The sea floor was not reproducible: two bakes of 400 Ma with identical code and inputs differed in
69,466 ocean cells by up to 1.8 km, and an A/B of the lake fix would not repeat. `PYTHONHASHSEED=0`
made it deterministic, which named the cause: `seamounts.py` seeded each hotspot chain with
`abs(hash(name))`, and CPython salts `str` hashes per process. The bakes run in a worker pool, so
every worker drew a different chain for the same named plume -- the seamounts along a hotspot track
re-rolled between neighbouring keyframes baked by different workers, and no two builds agreed.
Fixed with `zlib.crc32` (`seamounts._name_seed`). **Any seed derived from `hash()` of a string, or
from iterating a `set` of strings, is a per-process random number; test determinism with two
different `PYTHONHASHSEED` values, not with a repeat inside one process.**

### 7.39 A quantity smaller than the encoding's step is not in the data

The shipped elevation is 8-bit and sqrt-encoded: one code is `(4/255)·sqrt(8000·z)`, 20 m at 200 m,
63 m at 2 km, 89 m at 4 km, and the AVIF codec adds its own error (33 m rms, up to 150 m, over the
400 Ma belts, where rugged relief costs the encoder most). Three consumers read differences smaller
than that as data. The lake bake filled codec pits as lakes -- on one keyframe the codec alone
doubled the belt lake cover -- and now keeps a closed basin only if it is at least one code deep at
its spill level (`bake_lakes.drop_unresolved`). The shader's local relief `rug` read a code step on
a plain as relief along every code contour (the prairie squiggles), and now subtracts half a code
from each difference. **Before a threshold reads a small difference, ask what one step of the
field's own encoding is there.**

### 7.40 Blend the values across a boundary, not the coordinates

`relief.material` smoothed each pixel's 0 Ma position over ~1° so two plates' frames would blend
instead of stepping. Two plates' 0 Ma positions can be thousands of km apart, so inside a ~300 km
strip the coordinate SWEPT from one frame to the other: the crust stretched 6–46× along every
boundary, and every noise evaluated on it -- the seed, the massifs, the lithology, the sheets --
turned to sub-pixel stripes running down the belts' axes, which are sutures. `relief.Material` now
keeps each plate's own frame, evaluates the noise in each, and blends the values
(`sum w n / sqrt(sum w^2)`, which keeps the variance). The same holds for a phase: the sheets'
phase drifts are a fraction of a cycle, or the blend ramps through several cycles and draws
stripes again. **A coordinate interpolated between two frames is a position in neither.**

### 7.41 A first difference is zero on every crest

`rug`, the shader's local relief, was the gradient over ±31 km. A gradient vanishes at every
extremum, so through a rugged range it read saturated on the flanks and fell to nothing along each
ridge and valley axis (`?show=6`: white with black squiggles), and everything keyed to it followed:
the bare-rock gate put the lowland colour -- laterite orange, dune fields -- back along the lines,
and the detail amplitude pulsed with the phase of the ranges. The second difference over the same
taps is largest exactly where the first vanishes; for a ridge spacing of four baselines the sum of
their squares is the same at crest, flank and floor. **A measure of "how much relief" must not
depend on where in the waveform the pixel sits.**

### 7.42 A stream-power landscape drains across strike

Thrust sheets forced into the landscape model's uplift and erodibility at a 16:1 contrast did not
make the belts linear: its own bands measured an orientation coherence of 0.31–0.35 against real
belts' 0.38–0.53. At steady state the drainage runs down the regional slope, across strike, and
the sheets only put steps in its transverse profiles. Real belts are linear at the RANGE scale
(~100–500 km: the Rockies and the Rocky Mountain Trench, the Subandes and the Altiplano) because
there topography is structure -- uplifted sheets and basement blocks, synclinal and fault-bounded
valleys -- not dissection. So the 2–4 px band mixes the major ranges into the model's own, and a
fourth band (σ 4–8 px) is laid from sub-belts and calibrated to real belts; the control's
coherence in the 1–2, 2–4 and 4–8 px bands came to 0.43/0.44/0.51 against the real 0.38/0.44/0.53. **Ask which process
sets a scale before asking a model of another process to produce it.**

### 7.43 A difference of noise across a wide baseline is not a slope

The land hillshade differenced base plus procedural detail over ±23.5 km. For the base that is a
smoothed gradient; for every detail octave finer than the baseline it is two unrelated samples of
noise, which varies across the screen at the noise's own scale and belongs to no hill -- no lit side,
no shadowed one. At globe zoom that reads as grain a pixel wide; at close zoom it was 5–20 km clouds
over the Po plain as thickly as over the Alps, and so were the grain's random normal tilts (§5.12).
**Take each band's slope over a baseline matched to the band, or let it stand down when it is no
longer finer than a pixel.** `?show=15` (lighting only) is the view that shows it.

### 7.44 A threshold on a lossy field's derivative must clear the codec's error

`rug` allowed half a code for the 8-bit quantisation. The elevation is AVIF, and its transform
blocks add about a code at their edges (0.96 against 0.31 inside a block on the Alberta prairie,
3.1× at 16 texels, 2.0× at 8). Where real relief is a code or two, the block edges were `rug`, and
every threshold on it -- bare rock, alluvium, erg and hamada, the dissection gate -- drew
rectangles. Lossless would remove the cause at 5.2× the bytes (about +200 MB); a threshold turns a
one-code step into a hard edge, so decisions read `rugC` with the whole error allowed while
quantities that merely scale keep `rug`. **Measure the step energy on block boundaries against
off-boundary before blaming the model (§7.13).**

### 7.45 A track's first entry is not the present

`biota.label_point` took a label's present-day point as `tr[0]`, which held while every track
started at 0 Ma. A name that continues into the future carries its future points ahead of it
(−95 … 0 … 55), so the Himalaya's "present" became its +95 Myr position at 12° N and six Tibetan
taxa fell outside their ranges (`audit_biota`, 0 → 6). The interpolators that clamp at the
youngest end were right by construction; the one that meant "today" was not. **Look up the entry
for the age you mean.**

### 7.46 A weight set inside one branch is zero in the other

The close-zoom weight was first computed inside the sub-63° branch of the land gradient, and the
grain that reads it lives in the colour block, which both branches reach -- so above 63° it stayed
zero, and the Arctic kept every cloud the fix removed elsewhere, with no error and no warning. A
per-pixel quantity that describes the camera, not the branch, is set before the branch.

### 7.47 A validator that reads a file tests the file

`audit_deeptime`, `audit_island_biomes` and `audit_land_grain` measure screenshots on disk. From
9 August to 26 September they read the same August files while the shader changed under them, and
every build printed their passes. Re-shot, the Permian check failed (0.43 green against a 0.32 cap)
-- and the failure was the framing's, not the map's: 2E 45S at 280 Ma is southern Gondwana's
temperate belt (median rain 0.092), where the Early Permian had coal swamps, and it had passed in
August only because an older palette drew that belt drier; the model's own desert heart, 7.6E 23.4S,
reads 0.01. Both halves were invisible while the file was stale. `build_site_shots.refresh()` now
re-takes every shot older than the shader, the app, the fields, the labels or the audit that frames
it, before those audits run, and stops the build if one does not land. **A test's input has a date;
check it before reading its verdict.**

## 8. Sources

| role | source |
|---|---|
| Plate topologies | Merdith, A. S. et al. (2021), *Earth-Science Reviews* 214, 103477 · Zenodo 4485738 · CC-BY 4.0 |
| Feature-track rotations | Scotese, C. R. (2016), PALEOMAP Global Plate Model `m15g60_v2d3` · in `Scotese_PaleoAtlas_v3` · CC-BY 4.0 — the PaleoDEMs' own frame |
| Paleo-DEMs | Scotese, C. R. & Wright, N. (2018), PALEOMAP PaleoDEMs · Zenodo 5460860 · CC-BY 4.0 |
| Present plate motions | NNR-MORVEL56 (Argus, Gordon & DeMets, 2011) |
| Present boundaries | Bird, P. (2003), PB2002 · *G³* 4(3) |
| Sea-floor depth | GDH1 plate model (Stein, C. A. & Stein, S., 1992, *Nature* 359, 123–129); von Kármán roughness model for abyssal hills |
| Future climate | Farnsworth, A. et al. (2023), *Nature Geoscience* 16, 901–908 |
| Solar model | Gough, D. O. (1981), *Solar Physics* 74, 21–34 |
| Impacts | Impact Earth database (Osinski et al.) and Schmieder & Kring (2020) |
| Intervals | ICS chart v2024/12 |
| Clouds | NASA *Blue Marble: Clouds* — NASA/Goddard Space Flight Center, image by Reto Stöckli; `cloud_combined_8192.tif`, published 11 February 2002, a multi-day composite; reduced to `web/imagery/nasa-clouds-4096.jpg` (provenance and hashes in `nasa-clouds.json`); usage per science.nasa.gov/earth/faq |
| Illustrations | PhyloPic — CC0, Public Domain Mark or CC-BY only; contributors credited individually |
| Software | pyGPlates / GPlates; three.js + GLSL |

---

## 9. Known limits

- **Deep time and deep future are interpretive.** Pre-540 Ma and future frames are authored reconstructions — real cratons rotated into supercontinent fits. Treat this as a visualisation of the published record, not a precise map.

- **Palaeozoic longitude is a choice, not a measurement, and a residual against another reconstruction is EXPECTED.** Palaeomagnetism fixes palaeolatitude and orientation and says nothing about longitude, so before ~175 Ma — where the oldest sea floor and its magnetic stripes run out — every published model picks its own. Measured against Deep Time Maps (Blakey), an independent reconstruction: 5° mean |Δlon| over 0–100 Ma, 12° over 100–260 Ma, and **73° over 260–525 Ma, reaching 146° at 500 Ma**. Scotese's own model moved by up to **60°** between its ~2000 and 2016 editions. Latitude agrees throughout — land-versus-latitude correlation 0.87–0.97 across 400–525 Ma — which is the signature of a one-dimensional uncertainty. Chasing the residual to zero is the wrong goal; part of it can also be a true-polar-wander correction present in one model and absent in another.
- **The synthesised spreading network is plausible, not surveyed.** The pattern is real; the particular line is not. Same standing as the modelled rivers.
- **So are a deep-time range's valleys and massifs.** The baked relief (§5.10) puts back the form Scotese's smooth envelopes leave out -- an asymmetric wedge, a stream-power drainage network under the age's own rainfall, amplitudes and distributions matched to real belts of the same height and slope -- for every upland older than 55-70 Ma; no particular valley, pass or peak in it is a claim about the Palaeozoic. Where a range stood, how wide and how high over a few hundred kilometres is still the PaleoDEM's; the crest is moved up to ~80 km toward the foreland. The thrust sheets and sub-belts that make a range linear (3.14) are laid on the strike of the envelope and match real belts' linearity by band (coherence 0.43/0.44/0.51 against 0.38/0.44/0.53); their vergence follows the foreland the reconstruction implies, and no particular sheet is a claim either. The future's collision ranges are one step further out: their geometry comes from where the rigidly rotated groups overlap, which is the same kinematic input the domes had, drawn as an orogen instead of a lump.
- **41 tracked labels** still sit on the wrong medium for more than a third of their span, down from 62 before the frame switch. The old root cause — a Merdith-vs-Scotese frame mismatch patched with a rigid global longitude shift — is gone; tracks now use Scotese's own rotations, so the mismatch is zero by construction. What remains is a different and smaller set of causes: about a third of them are submarine **plateaus** (Ontong Java, Manihiki, Agulhas, Broken Ridge, Mascarene, Kerguelen) where "wrong medium" means the audit expected land and the feature is genuinely a drowned plateau, and most of the rest are terranes below what a 20 km grid resolves.

- **A small block in a shredded region is below the grid, in any frame.** The Rhodope Massif is the worked example: nine anchors *inside the same massif*, all assigned the same plate, score anywhere from 0.15 to 0.92 on the medium test under **either** rotation model. The spread is the measurement — the answer depends on which texel you land in, not on the reconstruction — so its residual is recorded rather than tuned away.

- **Four labels are authored at coordinates that are water today**, and so are never plate-tracked in any frame: **Gulf of California**, **Red Sea Rift** (both rifts that have already opened into sea), **West Antarctic Rift** (below sea level under ice) and **Kerguelen Microcontinent** (a drowned plateau). `coord_is_present_day()` routes them to `snapLabel`'s terrain search by design — a track follows crust, and a point in open water has no crust to follow. They are correct as authored; the build lists them under "labels left untracked" every run.
- **The oldest ocean crust is capped at 190 Myr, and one basin is probably older than that.** `MAX_CRUST_AGE = 190` is right for the world's ocean floor: everything older has been subducted, which is why the Pacific has no Jurassic floor left. The exception is the deep **eastern Mediterranean** — the Ionian and Herodotus basins may be surviving **Palaeozoic Tethyan floor, 270–340 Ma**, trapped behind the closing of Tethys rather than consumed with it. If so it is by a wide margin the oldest ocean crust on Earth, and this model draws it at 190 Myr like everything else, so it comes out a few hundred metres too shallow and with the wrong fabric age. The dating is contested and the basins are buried under kilometres of Messinian salt, which is part of why. Recorded rather than special-cased: one basin's disputed age is not worth a branch in the depth law.

- **The late Ediacaran draws too little land ice, and that is the price of one reference frame.** `ice_audit` wants 2-10% of land under ice at 570 Ma, for the cool interval after the Gaskiers glaciation; the model draws **0.3%**. It is not the ice model. Pinning the generated Precambrian world to PALEOMAP at the handoff -- so that Siberia and Laurentia stop drifting away from their own names (section 7.14) -- also adopts PALEOMAP's Ediacaran latitudes, and they are tropical: at 570 Ma **60% of all land lies within 30 degrees of the equator and only 7% above 60**, against 46%/16% at 545 and 42%/16% at 650. There is barely any high-latitude land to freeze. The literature figure assumes continents further poleward than this frame puts them. Warming the ice threshold until the number matched would be a compensating error hiding a geography disagreement, so it is recorded instead, and `audit_all` allows exactly this one finding.

- **Hotspot chains are generic**, smeared along plate motion, rather than modelled per plume with an explicit island-formation-and-subsidence history.
- **The biota cards are composed from a registry, and these are their limits.** (The three-tier panel — exception-curated → province assemblage → global list — is gone; §5.6.) All 38,036 card-ages pass the gate, which means no organism is outside its lifetime, its crust or its declared range, and none is under the wrong body form. It does not mean every card is the best card:
  - *Depth is uneven, and measured.* The registry holds 1,565 taxa. Class- and order-level entries on marine cards, measured by `build/measure_generic.py` on the shipped `life.json` (marine slot-ages; the 3.7–3.8 figures used an unrecorded counting and are not comparable): 20% of Cenozoic, 25% of Mesozoic, 25% of late Palaeozoic (28% in 3.8), 22% of early Palaeozoic (38% in 3.9), 38% of Precambrian (51%) — the Cryogenian and the small-shelly interval, where the record itself is thin. The curated record's own class-level names ("Ammonoidea", "Fusulinida") are replaced by genera where the registry has them at home there (`taxa_src/upgrade_curated.py`, re-run after any batch): class-level curated slot-ages 6,188 → 2,840; what remains is mostly the Tonian oceans' acritarchs and cyanobacteria and the vent Archaea, which are the honest answer. The earliest Cambrian shelf (541–521 Ma) is one list on every continent, because the small shelly fauna was. Cenozoic and Mesozoic land are well served; Ordovician–Silurian land is cryptospore crust by design.
  - *Region codes are block-sized now, and still coarse.* East Asia is four codes (North China, South China, Indochina, Sibumasu), Australia two (east, west), Europe two (`eu-n` Baltica–Avalonia, `eu-s` the peri-Gondwanan south: Iberia, France, Bohemia, the Alps, Italy, the Balkans) and eastern North America two (`na-e` the Laurentian craton, `na-av` the Avalon and Carolina terranes), with the old codes as aliases. The Europe line is approximated (the Rheic suture at 50°N, the TESZ as a step across Poland); within `eu-n`, Avalonia and Baltica were 30° apart until the Silurian and share a code, so Baltica's endemics carry `avoid`; Mongolia shares `as-ne` with North China. About 540 taxa carry a finer `box`, `avoid` list, sliced latitude band or dated habitat; the rest are as precise as their code. The placement listing (`audit_biota.py --placements`) has been read at thirty-four ages, every 10–25 Myr from 0 to 600 Ma; it is the check that finds what no rule can, and it must be read again after any large registry change. A box is not consulted on an ocean card (an ocean has no footprint), so a coastal species gets its basin's code and nothing else.
  - *A label is a point with a reach.* Long or irregular features (the Cordillera, the Central Asian Orogenic Belt) are approximated by an ellipse round one coordinate.
  - *Twenty-six body forms are hand-drawn* (belemnite, conodont, blastoid, bryozoan, horn coral, rudist, stromatoporoid, zosterophyll, progymnosperm, astrapothere, embrithopod, mesosaur, ostracod, uncoiled ammonite, bamboo, Namacalathus, agnostid, and the nine from 3.6) because no silhouette library holds them. They name the group at 46×31 px; they are not specimens.
  - *Ocean-island deep time is inference.* The Seychelles have no fossil record; their 3–62 Ma cards show the lineages phylogeny says were aboard and print a note saying so. Kerguelen's Miocene conifers are from wood in its lavas; its fauna then is inferred.
  - *A label is a point with a reach, and the future has forelands it never had.* The fifty future keyframes' foreland fields are baked from the synthesised belts, like the rest of the future series: illustrative.

- **Eleven curated localities are flagged `exception`** and the province model must never speak over them — Solnhofen, the Zechstein, Muschelkalk and Nama seas, the Messinian salt basin, the Paratethys, Lake Pannon, the Mid-Atlantic Ridge and East Pacific Rise vent faunas, the Beringian steppe-tundra, and Wallacea. Being atypical for their province is the entire point of each. `audit_curated_biota.py` checks the flag against a reading of the name, so a new curated entry has to declare itself.

- **We and Blakey agree about how much continent there was, and disagree about how much of it was dry.** This is the honest shape of the two largest remaining disagreements with an independent reconstruction, and they turn out to be one disagreement. At 525 Ma our land is 10.1 points below his — the biggest single-age gap in the whole audit — but **land plus shelf agrees to 1.0 point** (31.7% against 32.7%). Same continents, different shoreline. From 360 Ma back the same thing shows as us drawing 3–11 points *more* shelf sea than he does. Our own Cambrian series is smooth and tracks our eustatic curve (18.6% land at 540 Ma → 16.6% at 525 → 17.2% at 500), while his drops eleven points in 25 Myr against his own neighbours — so where the two differ at 525 Ma, the anomaly is not on our side. Recorded rather than tuned: this is two published reconstructions disagreeing about flooding, not a defect.

- **Present-day biota**: 110 labels carry a curated list; every other present-day card is composed from the registry for its own crust, habitat and latitude.

- **The present-day rainfall runs dry over highlands and the monsoon, and colours BC, the Ganges and Tibet's snow wrong (3.15).** Against 67 sites with real annual precipitation the shipped 0 Ma field ranks at Spearman 0.644: the Columbia Mountains read 0.024 (real ~0.30), the Ganges plain 0.03–0.12 (real 1–2 m a year), Lhasa 0.003, the Himalayan crest 0.000. The ranges draw brown, the Ganges orange, and the glacier line lands on the plateau. The orographic strip that drains the air over high ground is the same lever that keeps Pangaea's interior dry, a trade the user chose (`audit_biomes.py`, 2026-08-09); a physical orographic mode that lifts moisture over ranges was built and measured (`render.OROG_MODE`), and it wets Pangaea's interior from 17% to 58% above 0.2, so it is not shipped. The fix that does not touch deep time is an observed present-day anchor (a precipitation climatology blended out over the first few tens of Myr, the delta method), which needs a dataset the repository does not hold.

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
