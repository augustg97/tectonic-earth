# WP-01 · Where the Continents Were, and Why Our Labels Miss

**Deep Research white paper 01** · drafted 2026-07-26 · status: **v1, actionable**
**Scope:** continental assembly and dispersal 1000 Ma → present, reconstruction method, and the specific diagnosis of Tectonic Earth's label-placement error.
**Figures:** [`05-continental-affiliation.svg`](../diagrams%20and%20illustrations/authored/05-continental-affiliation.svg) · [`03-the-longitude-problem.svg`](../diagrams%20and%20illustrations/authored/03-the-longitude-problem.svg) · [`01-deep-time-master-chart.svg`](../diagrams%20and%20illustrations/authored/01-deep-time-master-chart.svg)
**Code:** [`modeling/paleogeography.py`](../modeling/paleogeography.py)

---

## Executive summary

The app's most persistent visible defect — labels drawn on the wrong ground — has **three independent causes**, and only one of them has been addressed.

1. **A reference-frame mismatch** between the terrain source (Scotese & Wright PaleoDEMs, PALEOMAP frame) and the motion source (Merdith et al. 2021, its own frame). Partly corrected by `frame_offset.py` as a rigid global longitude shift; the residual is the 27 labels still on the wrong medium for more than a third of their span. **The real difference is regional, not rigid, so a global shift cannot close it.**
2. **Coordinates that were never present-day positions.** A back-advected track only works on a modern coordinate. Paleo-entities authored in their own era's frame drift nonsensically. Largely fixed by `coord_is_present_day()` and `COMPOSITE_LABELS`, but the same class recurs whenever a new label is added.
3. **Labels with no existence test.** Nothing currently checks that "Avalonia" is only drawn while Avalonia *was* Avalonia, or that "Gondwana" is not drawn after 180 Ma. A window in `features.py` is an author's guess, not a constraint derived from the assembly history.

Cause (3) is entirely new work and the cheapest to fix. Cause (1) has a defined path. This paper sets out both.

---

## 1. What a reconstruction actually is, and what it cannot know

A plate reconstruction is a set of **finite rotations** — for each plate at each time, a rotation about an Euler pole. Motions are stored as a **plate circuit** hanging off a root plate (usually Africa), and **errors compose along the circuit**: an error on the Africa–Antarctica pole propagates undiminished into everything routed through Antarctica.

The data behind those rotations, and how far back each reaches:

| data | constrains | reach |
|---|---|---|
| marine magnetic isochrons | relative motion of two plates, both components | ~175 Ma |
| fracture zones | the direction of relative motion | ~175 Ma |
| **palaeomagnetism** | **palaeolatitude and rotation — never longitude** | ~2 Ga, widening error |
| hotspot tracks | absolute motion over the mantle *if hotspots are fixed* | reliable to ~90 Ma |
| slab tomography | where a trench was | to the Permian, best cases |
| LIP vs LLSVP margins | absolute longitude *if plume generation zones are stable* | Palaeozoic, weakly |
| geological piercing points | relative fit at an instant | any age |
| faunal/floral provinces | barriers, connections, latitude | Phanerozoic |

Before ~175 Ma the sea floor that recorded the motion has been subducted, so every reconstruction switches from *measurement* to *inference*.

### The longitude problem

The geocentric axial dipole field is **azimuthally symmetric about the spin axis**. A palaeomagnetic pole therefore gives palaeolatitude and a declination, and *nothing at all* about longitude. In the literature's own words: any conceivable longitude is equally viable for a block constrained by palaeomagnetism alone.

So every published deep-time model pins longitude with an extra assumption, and the assumptions differ:

| frame | the extra assumption |
|---|---|
| palaeomagnetic | one reference plate is taken to move least in longitude |
| fixed hotspot | a chosen hotspot group is mantle-fixed |
| moving hotspot | conduits advect in a modelled flow |
| slab-fitted | tomographic slabs sink vertically onto their trenches |
| LLSVP / plume generation zone | LIPs erupted over the margins of the two large low-shear-velocity provinces |
| TPW-corrected | true polar wander is removed before comparison |

**That is our bug, exactly.** Our features are positioned on Merdith's Earth and drawn on Scotese's. Measured gap: **≈9° at 90 Ma, ≈21° at 150 Ma, ≈40° in the Ordovician.** Symptom: the Western Interior Seaway label over the Appalachians.

`frame_offset.py` fits a per-age rigid longitude shift and smooths it (rolling median 7 → rolling mean 5 → re-anchor at 0). That took craters-on-plausible-terrain from **80% → 90%** and label anchors from **69% → 71%**. It also moved Chicxulub off its shelf onto land, which is the tell: **a global rigid shift is the wrong shape of correction.**

### True polar wander — a separate, additive term

TPW is the rotation of the *entire* mantle + lithosphere relative to the spin axis, keeping the maximum moment of inertia at the equator. It is **global and identical for every plate**, which is how it is separated from plate motion. Documented episodes include a ~25° southward shift of East Asia in the Jurassic (174–157 Ma) and a Late Cretaceous oscillation.

Consequence for us: our climate is computed from latitude in the shader, and latitude comes from the DEM's own frame, so TPW baked into the PaleoDEMs is honoured for free. But **part of any residual disagreement between a track and the DEM can be a TPW correction present in one model and absent in the other.** A small residual is *expected*; chasing it to zero is not the right goal, and README §9 should say so.

---

## 2. The assembly history, in the form the model needs

Full tables are in [`research/01-plate-tectonics/01-supercontinent-cycle.md`](../research/01-plate-tectonics/01-supercontinent-cycle.md); the machine-readable version is `modeling/paleogeography.py` (56 blocks, 6 assemblies, 35 orogenies, 31 terrane rift/accretion events). The load-bearing points:

**Rodinia** assembled 1.26–0.90 Ga by the globally correlated Grenvillian system (Grenville, Sveconorwegian, Musgrave, Albany–Fraser, Sunsás, Kibaran), with **Laurentia at the centre**. What sat off Laurentia's present-western margin is genuinely disputed — SWEAT (East Antarctica), AUSWUS (Australia), AUSMEX, Missing-Link (South China), revised Missing-Link (Tarim). Breakup came in four IGCP-440 stages with natural break points at **825, 800, 750, 700, 650, 550 Ma**, which is precisely the interval where our labels are least stable and where `precambrian.py` and `build_synthetic.pre_placement()` currently improvise.

**Pannotia** (~633–573 Ma) is **contested**: Gondwana's assembly overlapped Laurentia's departure from Amazonia, so there may never have been an instant when the pieces were all joined. Several authors reject it outright. Our supercontinent card states it flatly.

**Gondwana** (~550–180 Ma, ≈100 million km², a fifth of Earth's surface) assembled by a *set* of Pan-African sutures — East African 800–650, Brasiliano 660–530, Malagasy 550–515, Kuunga 570–530, Damara 530–500 — not one event. The South Pole tracks across it from NW Africa (Hirnantian) to southern Africa and then Antarctica/Australia (LPIA), which is the single control on our ice-line entries for 460–300 Ma.

**Pangaea** (~335–175 Ma) came from Caledonian (~430), Variscan (Early Carboniferous), Alleghanian/Ouachita (Late Carboniferous–Permian, building the Himalayan-scale Central Pangaean Mountains, peak ~295 Ma) and Uralian (Late Carboniferous–Permian). Cimmeria rifts off Gondwana in the Early Permian, opening Neo-Tethys behind as Paleo-Tethys closes ahead.

**The terrane table is the operationally important one**, because each of these is a name the app draws and each has a rift date, a destination and an accretion date:

| terrane | rifts | from | accretes | to |
|---|---|---|---|---|
| Avalonia | 500–480 | Gondwana | 457–449 / 420–400 | Baltica / Laurentia |
| Armorica | 480–450 | Gondwana | 340–300 | Laurussia (Variscan orocline) |
| Cuyania / Precordillera | 500–480 | **Laurentia** | 470–450 | Gondwana |
| N & S China, Tarim, Qaidam | 400–380 | Gondwana | 320–230 | Asia |
| Sibumasu, Qiangtang | 300–280 | Gondwana | 260–175 | SE Asia / Asia |
| Lhasa | 230–150 | Gondwana | 140–100 | Asia |
| Zealandia | 100–84 | Australia/Antarctica | — | (drifts, 94% submerged) |
| India | 132–120, 88–70 | Australia/Antarctica, Madagascar | 55–40 | Asia |

---

## 3. Three concrete remediations, ranked

### R1 — Add an existence gate to every crustal label (new; cheapest; highest certainty)

`paleogeography.exists(block, age)` and `affiliation(block, age)` are already written and tested. Wire them into `build_webdata.build_labels()` as a **validator**, not a placer:

- A label naming a block must not be drawn outside `[block.last, block.first]`.
- A label naming an *assembly* (Gondwana, Laurasia, Pangaea, Rodinia, Pannotia) must not be drawn outside that assembly's window.
- A label naming a block that is currently *inside* a named assembly should be de-prioritised in `layoutLabels()` relative to the assembly name — when Pangaea exists, "Baltica" competes with "Pangaea" for the same pixels and the reader wants the larger truth first.
- Emit a warning for every window in `features.py` that the table contradicts. This is the same discipline `build_webdata` already applies to `features.PHASES` windows.

**Expected effect:** removes a class of error that the current pipeline cannot even detect, at zero rendering cost.

### R2 — Replace the point-track with a landmass-track for crustal labels

The composite machinery (`COMPOSITE_LABELS` → `composite_track()` → `resolve_to_landmasses()`) already does the right thing for paleocontinents: it defines the entity by its **present-day fragments**, back-advects them, takes the spherical centroid, and then snaps to the **nearest part** of a real connected landmass in the DEM (not the centroid — a crescent continent's centroid is open water).

Generalise it. Any label whose subject is *crust* (continent, craton, orogen, terrane, region, plateau) should be defined by fragments and resolved onto the DEM's own land. **A label resolved this way has no frame dependence at all**, because the final position comes from the terrain we are actually drawing. That is the structural fix; the offset correction is a patch.

Labels whose subject is *water* keep their existing separate treatment (`COMPOSITE_WATER` + `nearest_water`, min depth 40 m), and must **not** be smoothed — a rolling mean walks a water label onto the beach.

### R3 — Make the frame correction regional

If R2 leaves cases that still need a frame fit (craters, LIPs, plumes — which are points on crust, not entities with fragments):

1. Fit a **separate longitude offset per major block** (Laurentia, Baltica, Siberia, Gondwana, the Chinas, Pacific-margin terranes), each smoothed in time as now.
2. Interpolate spatially between block anchors by great-circle distance so the correction field is continuous rather than a set of steps.
3. **Score on land–sea agreement over the whole window**, not on a cloud centroid — the metric should be the thing we care about.

**Before R3, check whether the PaleoDEM series ships or implies its own rotations.** If it does, tracking features in *that* frame makes the mismatch identically zero and R3 is unnecessary. This is the single highest-value thing to verify.

---

## 4. What to tell the reader

The app should not pretend to a precision it does not have. Three sentences, on the About page and on deep-time cards:

> Positions before ~175 Ma are reconstructions, not measurements: the sea floor that recorded the motion has been subducted. Palaeomagnetism fixes latitude and orientation but never longitude, so every published model chooses its own longitude convention — and this map combines two of them. Deep-time labels are placed on the best-matching ground rather than at an exact coordinate.

---

## Open items

- [ ] Check for a published PALEOMAP rotation file (would make R3 moot).
- [ ] Wire `paleogeography.exists()` / `affiliation()` into `build_labels()` as a validator; report contradicted windows.
- [ ] Extend the composite-fragment treatment to all crustal label types.
- [ ] Add `contested` to `eras_data.json` supercontinents; populate for Pannotia, Kenorland, Vaalbara, Ur.
- [ ] Audit the ~76 DeepTimeMaps paleogeographic maps in `Deep Time Maps and Resources/` against our own frames at matched ages — the user has already asked for this and it is the best independent check we have.

## Sources

Wikipedia *Rodinia*, *Gondwana*, *Pangaea*, *Supercontinent cycle*, *Laurentia*, *Baltica*, *Siberia (continent)*, *Avalonia*, *Terrane*, *Plate reconstruction*, *Apparent polar wander*, *True polar wander*, *List of orogenies* (retrieved 2026-07-26; the orogeny **table** has several corrupt rows and was not used for dates). Merdith et al. 2021 *Earth-Sci. Rev.* 214, 103477. Scotese & Wright 2018 PALEOMAP PaleoDEMs. Torsvik & Cocks, *Earth History and Palaeogeography* (2017) — **not yet consulted, obtain.**
