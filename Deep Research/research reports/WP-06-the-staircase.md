# WP-06 — The staircase: one cause, six paths, four wrong fixes

**2026-07-28.** Written after four attempted fixes, of which three were aimed at the wrong
mechanism and one addressed a sixth of the real one. This paper records the mechanism, the
evidence, why each earlier attempt failed, and the intervention that follows from it.

---

## 1. The symptom

At zoom, the deep ocean is crossed by large angular slabs — flat regions of constant shade
bounded by long straight edges with square corners and a stepped, rasterised look. Reported
across many ages and views. It is not subtle: the slabs are tens of degrees across.

It occurs at **every age**, including 133 Ma. An earlier draft of this paper claimed
133 Ma was clean and built an era-dependence argument on it; the user corrected that, and
the correction mattered — 135 Ma turns out to have the **largest raw step of any age
measured** (1,155 m, against 1,061 at 615 Ma). What varies with era is not whether the
artefact exists but *which* fix removes it, which is the subject of §4.

---

## 2. The mechanism

### 2.1 Where the field comes from

`crustage.build()` assigns crustal age by a **nearest-isochron search, performed
independently per plate**:

```python
for p, (xyz, ag, aid) in per.items():      # per PLATE
    sel = np.flatnonzero(flat == p)
    d, i = cKDTree(xyz).query(G[sel], k=1)  # NEAREST isochron
    age[sel] = ag[i]                        # take its age wholesale
```

Two consequences, and both are structural rather than incidental:

- `k=1` makes the field a **Voronoi tessellation** of the isochrons: flat facets, hard step
  at every boundary.
- the search runs **per plate**, so the field is discontinuous across every **plate
  boundary** — and plate polygons are long straight edges. That is the shape on screen.

### 2.2 Why it is era-dependent

The facets exist everywhere, but the amount of real data available to override them
varies enormously. Measured surveyed-age coverage (from `realage`):

| age | surveyed % of ocean |
|---|---|
| 0 Ma | 55.5% |
| 45 Ma | 36.8% |
| 135 Ma | 7.0% |
| 250 Ma | 0.1% |
| 400 Ma and older | **0.0%** |

From ~250 Ma back the age field is **100% model**, so it is 100% facets and the model is
the only thing to fix. In the 45-135 Ma window the coverage is *partial*, and that turns
out to be the hardest case of all: the model and the data disagree, and the machinery that
reconciles them (`_spread`) carries its own steps. **45 Ma, at 37% coverage, has the worst
residual of any age.** Neither extreme is the problem; the seam between them is.

### 2.3 How big the step is

Measured at 615 Ma, between **adjacent cells** (25 km):

| quantity | value |
|---|---|
| 99.5th-pct age change | **70 Myr** |
| depth change the GDH1 law gives that | **1,349 m** |
| what a real abyssal plain does | 50–125 m |

A 1.3 km cliff across 25 km, following plate-polygon edges. That is the staircase.

### 2.4 The six paths — this is why the last fix failed

The age field is not consumed once. Every one of these reads it, and each is a separate
route onto the screen:

| # | consumer | line | effect of a facet edge |
|---|---|---|---|
| 1 | depth (`depth_from_age`) | 778 | a 1.3 km wall, blended 72% into elevation |
| 2 | spreading direction (`gradient(age)`) | 796 | fabric orientation flips |
| 3 | **fracture zones** (`fz` from along-isochron age jumps) | 879–891 | an artificial step *looks exactly like a scar*; baked as a trough |
| 4 | seamount-chain amplitude (`1.1 − age/110`) | 952 | step in relief amplitude |
| 5 | **sediment thickness** (`_sd.thickness(age…)`) | 992 | step in burial → the fabric abruptly changes character |
| 6 | **the shipped `_o` R channel** (`spread_deg = age × 30/111.19`) | 1075–1078 | the shader keys its periodic fault sets to this — a step is a phase jump, a gradient change is a wavelength change |

I smoothed the age for **path 1 only** and measured no improvement in the shipped field.
That result was correct and the fix was not: paths 3, 5 and 6 run *after* the depth blend
and re-impose the edges. Path 6 is probably the most visible of all, because the shader
draws periodic structure keyed to it.

**Evidence that path 3 is doing real damage.** Fraction of ocean flagged as a fracture zone:

| age | `fz > 0.5` raw | with the fix | verdict |
|---|---|---|---|
| 615 Ma | 2.17% | **0.18%** | ~92% of "scars" were artefacts |
| 725 Ma | 2.75% | **0.30%** | ~89% artefacts |
| 0 Ma | 6.73% | 4.55% | real scars largely preserved |

---

## 3. Why four fixes failed

| # | fix | what it addressed | why it missed |
|---|---|---|---|
| 1 | elevation to AVIF | WebP's 4×4 transform blocks | **real defect, wrong scale** — 4 px, the symptom is tens of px |
| 2 | spin the tap cross | axis-aligned rank-statistic contours | randomising a stencil does not smooth it; produced a *ragged* edge, and shipped briefly |
| 3 | ring-8 robust mean | the same, done properly | **real defect, wrong subsystem** — `shelfHi`/`prom` are the shelf gate, not the abyss |
| 4 | smooth age for depth | path 1 of 6 | five other paths re-impose the edges downstream |

Fixes 1 and 3 were genuine improvements to genuine defects. Neither was *this* defect.

**The method error, which is the real lesson.** In each round I formed a hypothesis and
went straight to a fix, when three cheap measurements would have ruled it out:

1. **Measure the artefact's scale** before matching it to a candidate. 4 px ≠ 40 px.
2. **Take the era-dependence seriously.** "Bad at 617, clean at 133" is a searchlight
   pointing at anything that varies with data coverage. It named the cause in one step once
   I finally used it.
3. **Enumerate every consumer before intervening on one.** I patched path 1 without
   asking how many paths existed.

There is a fourth, about verification: the browser pane renders at 800×450 and downsamples
this artefact away, so for three rounds I "verified" against something that could not show
it. The `readPixels` → PNG → decode → view pipeline built in round four is the fix for that
and should be used from now on.

---

## 4. The intervention — TWO changes, not one

The first draft proposed one change. Measurement across the whole timeline says it is
necessary but **not sufficient**, and the second change is what makes it work everywhere.

### 4.1 Smooth the MODEL age at source (`oceanage.fuse`)

```python
model = np.where(np.isfinite(model), model, MAX_AGE).astype(np.float64)
model = gaussian_filter(model, 3.0 deg, ...)          # kill the Voronoi facets
both  = ok & np.isfinite(surv)
sp    = _spread(np.where(both, surv - model, 0.0), both)
sp    = gaussian_filter(sp, 1.5 deg, ...)             # and the reconciliation seam
age   = np.where(both, surv, model + sp)              # surveyed data still wins, exactly
```

Why this is the right level rather than a convenient one:

- It targets **the artefact and only the artefact**. The facets belong to the *model's*
  assignment rule. Surveyed age is measurement and is re-imposed exactly, so the existing
  `both` mask already draws the line for us.
- It is **more physically correct**, not merely smoother: crustal age genuinely varies
  smoothly away from a ridge, so a step function is the wrong shape for the quantity.
- It is upstream of **all six consumers**, so no downstream path can re-impose the edges.
  This is the only change that helps the fabric, the fracture zones, the sediment and the
  shipped `_o` coordinate — the depth-side fix in §4.2 does nothing for any of them.

The second smoothing (of `sp`) is needed because `_spread` diffuses a correction whose
magnitude is set by *how wrong the model was*, so it inherits large gradients. At 135 Ma the
smoothed model contributes 5.2 Myr of step and `sp` contributes 12.1.

### 4.2 Smooth the age on the DEPTH path only (`seafloor.py`, already written)

Depth is a **regional** quantity — it varies over hundreds of kilometres — so smoothing the
age by 3.3° before the GDH1 law costs nothing real. It catches the residual that §4.1
cannot, because in the 0–135 Ma window part of that residual is *genuine surveyed structure*
which must stay sharp for the fabric and the fracture zones but should not appear as a
kilometre-high wall in the bathymetry.

This is the principled division: **sharp where the data is real and the feature is
fine-scale; smooth where the quantity is regional.**

### 4.3 Measured, across the whole timeline

Depth step, 99.5th percentile, metres per 25 km cell. Target 50–125.

| age | raw | §4.1 only | §4.1 + §4.2 |
|---|---|---|---|
| 0 Ma | 719 | 376 | **55** |
| 45 Ma | 1,350 | 703 | **63** |
| 90 Ma | 1,321 | 405 | **67** |
| 135 Ma | 1,155 | 282 | **58** |
| 200 Ma | 1,504 | 107 | **72** |
| 250 Ma | 1,218 | 91 | **62** |
| 615 Ma | 1,061 | 85 | **58** |
| 725 Ma | 1,112 | 94 | **64** |

Every age lands inside the physical range. Note that §4.1 alone leaves 45 Ma at 703 m —
this is exactly the case the first draft would have shipped and the user would have
rejected again.

### 4.4 Real data is not touched

The decisive control. Fracture zones flagged, split by whether the cell has surveyed data:

| | inside surveyed (real) | outside (modelled) |
|---|---|---|
| 0 Ma | 3.17% → **3.11%** | 10.21% → **2.76%** |
| 45 Ma | 7.31% → **7.16%** | 10.47% → **2.23%** |
| 615 Ma | — (no data) | 2.17% → **0.18%** |

Real scars survive to within 0.06 pp. Roughly three-quarters of the invented ones go. In the
Precambrian, where there was never any data, **92% of what the model called a fracture zone
was invented by its own facet edges** and is now gone.

### 4.5 The deeper fix, and why it is not this one

Replacing `k=1` with an inverse-distance blend of the four nearest isochrons was implemented
and measured: **70 → 47.5 Myr**, i.e. 1,349 → 1,061 m. Better, and *not sufficient*, because
the residual sits at plate boundaries the per-plate search never crosses. It also
invalidates 2.7 GB of isochron cache across 251 ages. Recorded as **D9** — worth doing as
its own pass, on top of this, not instead of it.

### 4.6 Cost

Only the `ocean` cache is invalidated; `crustage` is untouched, so the expensive pyGPlates
isochron work is reused. A few seconds per age, then the standard re-skin.

### 4.7 What this does not fix

- The **lattice** near Ontong Java — a separate regression from the ring-8 stencil, still
  outstanding.
- Whatever residual the shader's own procedural fabric contributes; this paper is about the
  field beneath it.

---

## 5. Verification plan

Measure, not eyeball, and at the right scale:

1. **Large-scale relief**, fabric smoothed away (σ 8): the metric that actually tracks slab
   edges. Cell-to-cell relief does not — it is dominated by procedural fabric, which is why
   my first check on the rebuilt frames was uninformative.
2. **`fz` coverage** at 615/725 Ma, expected ≈ 0.2–0.3%.
3. **0 Ma control**: land/sea, depth histogram and fracture-zone count must not move
   materially.
4. **Full-resolution visual** at 617 and 724 Ma via the `readPixels` capture pipeline —
   the user's own worst cases, at a resolution that can actually show the artefact.
