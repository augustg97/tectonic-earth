# Plate Reconstruction: Data, Euler Rotations and Reference Frames

**Domain:** plate tectonics / method · **Status:** first pass, 2026-07-26
**Feeds directly:** `paleo_tracks.py`, `frame_offset.py`, `build_webdata.build_labels()`, `build_plates_gplates.py`
**Why this file exists:** the app's single largest residual error — *27 tracked labels sit on the wrong medium for more than a third of their span* — is a reference-frame problem, and this is the physics of that problem.

---

## 1. What a reconstruction is made of

A reconstruction is a set of **finite rotations**: for each plate and each time, a rotation about an **Euler pole** (a point on the sphere) through an angle. Any motion of a rigid cap on a sphere is exactly such a rotation, so the representation is complete and lossless for rigid plates. Deformation (rifting, orogenic shortening, back-arc opening) is *not* representable this way and is either ignored, absorbed into extra plates, or handled by deforming-mesh models.

Rotations are stored as a **plate circuit**: each plate's motion is given relative to a parent, the parent relative to *its* parent, up to a root (Africa in most models). To place a plate absolutely you compose the whole chain — and **errors compose with it**. A 2° error on the Africa–Antarctica pole propagates undiminished into every plate whose circuit passes through Antarctica.

### Data types, and how far back each reaches

| data | what it constrains | reach |
|---|---|---|
| **marine magnetic anomalies (isochrons)** | relative motion of two plates, exactly, in both components | to ~175 Ma; sparse before ~120 Ma |
| **fracture zones** | the *direction* of relative motion (flow lines) | same |
| **paleomagnetism (APWP)** | paleolatitude + rotation about the vertical. **Not longitude.** | to ~2 Ga, with growing error |
| **hotspot tracks** | absolute motion over the mantle, if hotspots are fixed | reliable to ~90 Ma; hotspot–hotspot relative motion is demonstrable before that |
| **seismic tomography of slabs** | where a trench *was*, ± the sinking rate assumption | to the Permian in the best cases |
| **LIPs vs. LLSVP margins** | absolute longitude, if plume generation zones are stable | Palaeozoic and older, weakly |
| **geological piercing points** (matched belts, ophiolites, distinctive basement) | relative fit at a moment | any age; the mainstay of Precambrian work |
| **faunal / floral provinces** | ocean barriers, land connections, latitude | Phanerozoic |

**Note the asymmetry.** For the last 175 Myr the sea floor records relative motion directly and the reconstructions are *measurements*. Before that everything is inference from continental rocks, and the further back you go the more the answer depends on which frame the author chose.

---

## 2. The longitude problem — the root of our label error

The geocentric axial dipole field is **azimuthally symmetric about the spin axis**. A paleomagnetic pole therefore carries paleolatitude and a declination (rotation), and nothing at all about longitude. In the article's words: *any conceivable longitude would be an equally viable option for the reconstruction of a tectonic element if its position is constrained by paleomagnetic data alone.*

Every published deep-time reconstruction therefore fixes longitude by an extra assumption, and different authors choose different ones:

| frame | the extra assumption |
|---|---|
| **paleomagnetic** | one reference plate is assumed to have minimal longitudinal motion; everything else hangs off it by relative rotations |
| **fixed hotspot** | a chosen hotspot group is fixed in the mantle |
| **moving hotspot** | hotspot conduits advect in a modelled mantle flow |
| **slab-fitted** | tomographic slabs are dropped vertically and matched to trenches |
| **LLSVP / plume-generation-zone** | LIP eruption sites lay above the margins of the two large low-shear-velocity provinces, which are assumed long-lived |
| **TPW-corrected** | the whole mantle+lithosphere is de-rotated to remove true polar wander before comparison |

**This is exactly our bug.** The terrain is Scotese & Wright's PaleoDEMs, built in the PALEOMAP frame. The tracks are Merdith et al. (2021), built in its own frame. Both are defensible; they are not the same Earth. `frame_offset.py` measures the discrepancy as a rigid longitude shift (≈9° at 90 Ma, ≈21° at 150 Ma, ≈40° in the Ordovician) and applies it — an improvement (craters on plausible terrain 80→90%) but not a fix, because **the true difference is not a rigid rotation**. Two models can differ by a *different* amount for Laurentia than for Gondwana at the same instant, since each was longitude-pinned by a different argument.

### What a real fix looks like

1. **Per-continent, not global.** Fit a separate longitude offset per major block (Laurentia, Baltica, Siberia, Gondwana, the Chinas, Pacific-margin terranes), each smoothed in time. Interpolate spatially between blocks by distance so the correction field is continuous.
2. **Fit on land–sea agreement, not on a cloud centroid.** Score by "does this label's medium (land/shelf/deep) match the DEM at the tracked point", integrated over its whole window, which is the metric we actually care about.
3. **Better: drop the second frame entirely.** Anchor features to the *DEM's own* land, by tracking a label as the nearest persistent landmass rather than as a point. The composite-landmass machinery (`resolve_to_landmasses`) already does this for paleocontinents; extending it to all crustal labels removes the frame dependence for those labels completely.
4. **Check whether Scotese publishes rotations.** If the PaleoDEM series ships or implies its own rotation file, tracking features in *that* frame makes the mismatch identically zero. This is the single highest-value thing to check.

**Recommended priority: (4) → (3) → (1).** (2) is a cheap improvement to what exists today.

---

## 3. True polar wander — a distinct, additive term

TPW is the rotation of the **entire** solid Earth (mantle + lithosphere) relative to the spin axis, driven by mass redistribution: the planet keeps its maximum moment of inertia at the equator, so a large enough load makes the whole shell roll. The rotational bulge readjusts, so it is not resisted indefinitely.

- It is **global and identical for every plate** — that is how it is separated from plate motion, which differs per plate.
- Documented: an East Asian southward shift of ~25° in the Jurassic (174–157 Ma); a Late Cretaceous oscillation; several proposed Neoproterozoic–Early Palaeozoic events, including the contested "inertial interchange" episodes around the Ediacaran–Cambrian.
- **Climatic consequence:** a 25° shift relocates the climate belts wholesale without any plate moving relative to any other. Aridity, ice line and biome position all move.

**Model implication.** Our climate is computed from latitude in the shader, and latitude comes from the DEM's own frame — so any TPW already baked into the PaleoDEMs is honoured for free. But if a label track and the DEM disagree, part of the disagreement can be a TPW correction present in one model and absent in the other. Worth stating in `README §9`, because it means a small residual is *expected* and chasing it to zero is not the right goal.

---

## 4. Practical notes for our pipeline

- **pyGPlates does not refuse negative times.** It extrapolates and returns confident nonsense (already recorded as trap #9).
- **The Merdith model needs both topology sets loaded** (`250-0` / `410-250` boundary files *and* the `1000-410` Topologies/Convergence/Divergence/Transforms set), or 600 and 900 Ma resolve to zero plates.
- **Latitude is the trustworthy coordinate.** Both models are pinned to the same paleomagnetic latitudes, which is why `frame_offset` deliberately corrects longitude only. Keep it that way.
- **A rigid global shift makes some things worse** (Chicxulub moves from shelf onto land). Any future correction must be evaluated on a population, never on a favourite feature.
- **Smoothing is mandatory.** The per-age fit is noisy because the objective is shallow; raw, it stepped 41° between 360 and 365 Ma. Rolling median → rolling mean → re-anchor at 0.

---

## Sources

- Wikipedia, *Plate reconstruction*, *Apparent polar wander*, *True polar wander*, *Terrane* — retrieved 2026-07-26.
- Merdith, A. S. et al. (2021), *Earth-Science Reviews* 214, 103477.
- Scotese, C. R. & Wright, N. (2018), PALEOMAP PaleoDEMs, Zenodo 5460860.
- Torsvik & Cocks, *Earth History and Palaeogeography* (2017) — the standard treatment of the longitude problem and the LLSVP frame. **Not yet consulted; obtain.**
