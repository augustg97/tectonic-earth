# WP-07 — The future era: why it is stiff, and why its coastlines step

**2026-07-28.** Investigation only; nothing implemented. Four findings, three of them
measured defects rather than matters of taste, and one of them a regression I introduced
and did not catch.

---

## Finding 1 — The future staircase is nearest-neighbour sampling

`future_grid()` builds each future keyframe by **inverse-warping the present DEM**: for every
output cell it rotates back by the group's rotation, asks a mask which group owns that spot,
and looks up the elevation. Both lookups use `.astype(int)` — floor, i.e. **nearest
neighbour** — and both sources are far coarser than the output:

| what | resolution | per cell | vs the 0.088° output |
|---|---|---|---|
| group mask `gid` | 360 × 720 | **0.500°** | **5.7 output cells** |
| source DEM `Zsrc` | 900 × 1800 | 0.200° | 2.3 output cells |
| output field | 2048 × 4096 | 0.088° | — |

So every continental margin in the future era has its **claim boundary quantised to half a
degree**, and its elevation to a fifth of one. That is the staircase, and it is a completely
separate mechanism from the ocean staircase in WP-06 (which is the crustal-age Voronoi).

Verified directly: the same source window resampled the two ways, thresholded at sea level.
Nearest gives a blocky stepped coast; bilinear gives a natural curve. (`samp_nearest.png` /
`samp_bilinear.png`.)

Two false starts worth recording so they are not repeated: a phase test against the output
grid found nothing, because after a **rotation** the source grid is no longer aligned with
the output grid and the steps run at rotated angles; and an "identical adjacent cells" test
found nothing either, because 8-bit elevation quantisation makes neighbours identical
anyway. Only isolating the sampling itself settled it.

---

## Finding 2 — G5's collisional uplift does not reach the shipped fields

I reported in round 3 that suture uplift took land above 2 km from 8.8 to 13.8 Mkm². The
shipped fields say otherwise:

| | >0 | >1 km | >2 km | >3 km | mean |
|---|---|---|---|---|---|
| today | 148.4 | 30.2 | **8.7** | **4.3** | 663 m |
| +250 Myr | 128.8 | 28.9 | **8.7** | **4.3** | 712 m |

Above 2 km and above 3 km are **identical to the decimal** after a quarter of a billion years.

The cause is a resolution dependence. The belt seed is widened with
`maximum_filter(seed, size=3)` — a size in **cells, not degrees** — and is then raised to
`SUTURE_POW = 3`, which cubes the loss. The same physical future, computed at three
resolutions:

| grid | what `size=3` covers | >2 km |
|---|---|---|
| 512 × 1024 | 1.05° | 11.5 Mkm² |
| 1024 × 2048 | 0.53° | 9.3 Mkm² |
| **2048 × 4096 (shipped)** | **0.26°** | **8.9 Mkm²** |

I measured G5 at low resolution and it evaporates at production resolution. This is exactly
the trap `build_fields.py`'s own module docstring warns about — *"EVERY SPATIAL FILTER BELOW
IS IN CELLS … each is a claim about the WORLD and not a claim about the raster"* — and it is
the second time in this project a filter in cells has silently changed meaning. It should
have been caught by measuring the shipped field rather than the function's return value.

---

## Finding 3 — The terrain is rigid by construction

`future_grid` applies a **pure rigid rotation** of present-day terrain, per group:

```python
Rm = axis_angle_scale(Rfull, frac)
S  = Rm.T @ T                       # rotate the query point back
z  = np.where(claims, Zsrc[sy, sx], -9999.0)
out = np.maximum(out, z)            # overlap -> keep the high ground
```

There is no mechanism anywhere for **erosion**, **crustal shortening**, **accretion**,
**margin subsidence** or **sedimentation**. A continent is a rubber stamp of its present
self, moved across the globe and pressed down again.

That is precisely the user's observation. Australia crosses Indonesia, south-east Asia and
east Africa and emerges with the same outline because nothing in the model can deform it.
East Africa keeps its thin snakey rift-sliver shape for 250 Myr because nothing can widen a
margin or fill a basin. And the hypsometry above confirms it: **every present-day mountain
range is still standing, at its present height, at +250 Myr.**

For scale, the Appalachians were Himalayan at ~300 Ma and are 1–2 km now. On this model's
physics they would still be Himalayan.

---

## Finding 4 — 12.8 Mkm² of convergence is computed and thrown away

Where two groups' warped footprints overlap, `out = np.maximum(out, z)` keeps the higher and
discards the rest. Measured:

| | cells claimed by >1 group | **both land** | max claims on one cell |
|---|---|---|---|
| +125 Myr | 98.9 Mkm² | 9.3 Mkm² | 4 |
| +250 Myr | 128.6 Mkm² | **12.8 Mkm²** | 4 |

Land-on-land overlap **is** the convergence. 12.8 Mkm² is larger than the entire
Alpine–Himalayan collision zone, and the model already computes it and then deletes it. It
is both the reason collisions look like interpenetration and the obvious physical source for
the mountains that ought to result.

---

## Proposed solutions

Ordered by confidence and by payoff per unit of risk. Nothing here is implemented yet.

### S1 — Sample properly (fixes the staircase)

- **Elevation**: replace the floor lookup with bilinear (`map_coordinates(order=1)`), taking
  care that longitude wraps.
- **Group mask**: raise `rasterise_groups` from 360 × 720 to ~1440 × 2880 (0.125°), so the
  claim boundary is four times finer than the output cell rather than six times coarser.
  It is a vectorised point-in-polygon test, so the cost is seconds and it is computed once.

Note the existing fractal fraying of the claim direction already perturbs margins by a
degree or two. On a coarse mask that fraying lands *on top of* half-degree steps; on a fine
mask it does what it was written to do — headlands and embayments.

**Confidence: high.** The mechanism is proven and the fix is mechanical.

### S2 — Make the suture belt resolution-independent

Express the seed's widening in **degrees**, then re-tune `SUTURE_UPLIFT` so the *shipped*
2048 × 4096 field hits the intended target. Verify by measuring `fut_0250_e.avif`, never the
function's return value at a convenient resolution.

**Confidence: high.** It is a bug with a measured signature.

### S3 — Erode the inherited relief

Decay topographic excess toward a regional base with a time constant, scaled by `frac`, and
applied **before** the suture uplift so that old ranges wear down while new ones rise.

Calibration against the Appalachian analogue (>4 km at 300 Ma → 1–2 km now) puts τ at
roughly 100–150 Myr. Measured effect at +250 Myr:

| τ | excess surviving | >1 km | >2 km | >3 km |
|---|---|---|---|---|
| none | 100% | 34.5 | 11.5 | 4.8 |
| 200 Myr | 29% | 30.0 | 6.0 | 2.4 |
| **120 Myr** | **12%** | **29.2** | **5.1** | **2.0** |
| 80 Myr | 4% | 28.8 | 4.9 | 1.8 |

This is the single change that most directly answers "unnaturally stable". It also changes
*outlines*, not just heights: worn-down coastal ground drops toward sea level and floods.

**Confidence: high on the mechanism, medium on the constant.** τ is a modelling choice and
should be stated as one on the card.

### S4 — Turn the discarded overlap into crustal thickening

Instead of `max()` alone, use the **land-on-land overlap** as the uplift source: crustal
thickening is proportional to shortening, and the overlap is the shortening. This is
physically better founded than the current adjacency seed — which only knows that two groups
are *near* each other, not how hard they are converging — and it uses a quantity the code
already computes.

Expected: collisions build a real belt where the convergence is greatest, and the "two
outlines superimposed" look goes away because the contact thickens and merges rather than
one map simply winning.

**Confidence: medium-high.** Needs care that four-way overlaps do not stack into absurd
heights; cap by total overlap depth rather than summing pairs.

### S5 — Subside the rifted margins (East Africa)

Where a group's land is adjacent to ocean that *opened behind it*, subside the trailing
margin with time and let a shelf wedge accumulate. This is what turns East Africa's knife-
edge sliver into a continent with a real passive margin, and it is the same mechanism that
made the Atlantic margins.

**Confidence: medium.** Well motivated, but it needs a reliable "this margin is young and
rifted" test, and the group masks are derived from present-day plate polygons, which is a
crude basis for one.

---

## Sequencing

S1 and S2 are bug fixes and should go first — they are cheap, low-risk, and S2 restores
behaviour that was supposed to be there already. S3 is the big conceptual win and should be
tuned against the hypsometry table above. S4 follows naturally from S3 (erode the old, raise
the new). S5 last, and only if the margin test can be made honest.

All of it is one rebuild, since it all lives in `future_grid`.

**Not to be confused with:** the ocean staircase (WP-06, a different mechanism, already
fixed and rebuilding) and the Ontong Java lattice (a ring-8 shader regression, outstanding).

---

## Implemented, 2026-07-28

All five, in one pass, all in `future_grid` plus `rasterise_groups`.

| | change | measured |
|---|---|---|
| **S1** | bilinear elevation sampling (`_bilerp`); group mask 0.5° → **0.125°** | coastline crenulation 41,660 → **31,840** edge cells (−24%) |
| **S2** | seed widening in **degrees** (`SUTURE_SEED_DEG = 0.35`), not cells | >2 km 8.7 → **12.0** Mkm² — the uplift now reaches the shipped field at all |
| **S3** | two-time-constant erosion, applied **before** uplift | τ 150 Myr relief / 400 Myr regional, floor 300 m |
| **S4** | land-on-land overlap drives the belt, capped at 2 | the 12.8 Mkm² that used to be discarded |
| **S5** | rifted margins subside toward unclaimed new ocean | −700 m at the margin by +250 Myr |

The finer mask needed the scanline restricted to each ring's **bounding box** —
6,605 ring vertices against 4.1M cells is 2.7e10 tests — which is exact rather
than approximate, and brings the mask to 7.5 s.

**Hypsometry at +250 Myr, on the shipped 2048×4096 field** (today in brackets):

| | >0 | >1 km | >2 km | >3 km | max |
|---|---|---|---|---|---|
| shipped | 133.6 (143.1) | 25.2 (29.9) | **10.7** (8.8) | **5.8** (4.3) | 6.4 km (9.7) |

More high ground than today because a supercontinent is assembling; less moderate
upland because 250 Myr of weather has taken the old ranges down. Everest-height
peaks are gone, which is the point — nothing in the old model could remove them.

### The calibration trap, and it is the one Finding 2 warned about

`SUTURE_UPLIFT = 3400` was tuned to top up relief that was already near 2 km.
Once S3 correctly wore that relief away, the same constant had to build an orogen
from a peneplain, and it could not: **erosion alone took >3 km to 0.0 Mkm²**, and
erosion plus the old uplift gave >2 km of 1.2 against today's 8.8. Sweeping them
**together** on the shipped field landed on 9000 m and pow 2.5. Two changes that
compose are one calibration, not two — and measuring the function's return value
at a convenient resolution is exactly what produced Finding 2 in the first place.
