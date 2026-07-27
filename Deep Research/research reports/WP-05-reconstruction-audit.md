# WP-05 · The reconstruction, audited against two published series

**2026-07-26, round 8.** Register items **A5** and **F1**. The app's palaeogeography had
never been compared with anything outside its own pipeline, and its future series had never
been compared with anything at all. Both now have been, on 31 ages, with a re-runnable
script: [`modeling/audit_reconstruction.py`](../modeling/audit_reconstruction.py).

The reference images are copyrighted (© CPGS, © C. R. Scotese). **Nothing here reproduces
them**; every number is a measurement taken against them and the images stay out of git.

---

## 0. What had to be true before any number meant anything

The reference maps are Mollweide, our fields are equirectangular, and getting that
conversion wrong would have made every figure below meaningless while still looking
plausible. So the projection was validated first, at 0 Ma, the one age where both sides are
the real Earth:

| present-day control | result |
|---|---|
| land/sea agreement, our 0 Ma field vs `00-Ma-PresentMOLL-tn.jpg` | **96.8%** |
| land IoU | **0.897** · kappa **0.924** |
| best-fit longitude offset | **0°** |
| mean displacement of a reference land pixel to ours | **3 km** |
| reference land + ice, measured | **28.8%** — Earth is 29.2% |
| reference ice, measured | **13.0 Mkm²** — Antarctica + Greenland is 15.7 |

Mollweide is equal-area, so a pixel count on the reference's own grid *is* an area integral:
no cos(latitude) weighting, and none of the polar exaggeration that makes the eye the worst
available instrument for this.

Two corrections to this folder's own tooling had to happen first, and both belong in the
record.

**The decode constant was wrong.** `build/fieldpack.py` uses `Z_RANGE = 8000.0`, and so does
every other consumer in `build/`. `modeling/frame_experiment.py:_decode()` uses **11000.0**,
and the A5/F1 handoff prompt inherited the error by telling this session to decode "exactly
as `_decode()` does". Consequence for WP-04: its headline is untouched, because its
land/abyss split is scored with one threshold across all three frames and the ranking cannot
move — but its "shelf" boundary is really **−364 m**, not −500 m, and the deepest bin is
mislabelled. This is the sixth time an audit's disagreement with the app has turned out to be
the research's error. The rule keeps paying.

**The ice colour rule needed neutrality, not saturation.** A saturation cut read 1.1% of the
420 Ma map as ice, all of it below 30° latitude in a world with no ice sheets. The culprit is
a pale green-grey Silurian lowland, median RGB (217,228,212). Real ice in this series is
genuinely neutral — (250,250,251) at the present pole, (246,246,247) on the Gondwanan sheet
at 300 Ma. Requiring `|R−G|` and `|G−B|` to be small separates them where one saturation
number cannot. The tighter rule runs about **17% low** on ice area at both the present day
and the LGM; that bias is consistent, so ratios between ages survive it, and it is stated
wherever an ice number appears below.

---

## 1. The two references are not the same kind of witness

This is the single most important thing to get right about the whole audit, and it is not
obvious from the file listing.

- **Deep Time Maps™** is Ron Blakey's reconstruction (Colorado Plateau Geosystems). It is
  **independent** of ours — different author, different plate model, different
  palaeogeographic judgement. Disagreement with it is a real result.
- **Our terrain is the Scotese & Wright PaleoDEMs**, read straight through
  (`build/build_frames.py:read_dem` does periodicity repair and nothing else). So the Scotese
  series is a **self-consistency** check. It should agree; if it does not, our pipeline broke
  something on the way in.

That asymmetry decides how every disagreement below is read.

---

## 2. Land area — the app tracks an independent reconstruction closely

Land fraction is the cheapest and most diagnostic number, and it is the one that comes out
well. Over 31 matched ages the mean bias is **+1.6 percentage points**, and 25 of 31 ages
sit within ±4 points.

| era | ages | mean land bias (ours − DTM) |
|---|---|---|
| 0–100 Ma | 8 | **+1.6 pp** |
| 100–260 Ma | 9 | **+5.5 pp** |
| 260–525 Ma | 14 | **−0.8 pp** |

Selected ages, with the latitudinal distribution of that land:

| age | DTM land | ours | Δ | land-vs-latitude RMS |
|---|---|---|---|---|
| 0 | 28.8% | 29.5% | +0.7 | 9.9% |
| 50 | 27.2% | 27.3% | +0.1 | 11.5% |
| 90 | 23.8% | 25.5% | +1.6 | 7.4% |
| 150 | 27.6% | 32.9% | **+5.2** | 22.2% |
| 200 | 27.6% | 36.4% | **+8.8** | 12.8% |
| 240 | 28.3% | 37.7% | **+9.4** | 13.4% |
| 300 | 22.4% | 22.5% | +0.2 | 8.9% |
| 420 | 18.0% | 14.7% | −3.3 | 6.7% |
| 450 | 15.1% | 16.7% | +1.6 | 7.7% |
| 500 | 15.8% | 15.9% | +0.1 | 9.4% |
| 525 | 26.7% | 15.0% | **−11.6** | 23.6% |

Two things stand out and both recur below.

**The Triassic–Jurassic runs 5–9 points too much land.** 150, 180, 200 and 240 Ma are the
four worst ages in the whole series on this measure, and §4 shows why: it is not extra
continent, it is missing sea.

**525 Ma disagrees by 11.6 points, and it is the only Cambrian age that does.** At 500 Ma the
two agree to 0.1 points. The disagreement is inside DTM's own series as much as between the
two: Blakey's land drops 26.7% → 15.8% across those 25 Myr. That is the Sauk transgression,
which was real and large, but an 11-point fall in 25 Myr is steep, and the honest verdict is
that this one is unresolved rather than ours.

---

## 3. Position — the Palaeozoic disagreement is real, and it is not ours

Plain agreement percentage is a trap that gets worse with age: at 450 Ma the reference is 85%
ocean, so a map predicting "ocean everywhere" would already score 85%. Everything below is
IoU and Cohen's kappa, which have no such floor.

| age | IoU | kappa | fitted Δlon | IoU after | kappa after | median displacement, DTM→ours |
|---|---|---|---|---|---|---|
| 0 | 0.897 | 0.924 | −0° | 0.895 | 0.922 | 0 km |
| 50 | 0.486 | 0.524 | +7° | 0.534 | 0.583 | 0 km |
| 90 | 0.462 | 0.512 | +9° | 0.589 | 0.657 | 0 km |
| 150 | 0.500 | 0.524 | +15° | 0.533 | 0.565 | 0 km |
| 200 | 0.587 | 0.621 | +11° | 0.639 | 0.679 | 0 km |
| 250 | 0.670 | 0.725 | +3° | 0.682 | 0.737 | 0 km |
| 300 | 0.454 | 0.516 | −23° | 0.650 | 0.727 | 0 km |
| 340 | 0.279 | 0.287 | −44° | 0.474 | 0.548 | 127 km |
| 400 | 0.222 | 0.229 | −87° | 0.371 | 0.443 | 458 km |
| 420 | 0.068 | **−0.041** | −99° | 0.388 | 0.471 | 1217 km |
| 450 | 0.100 | 0.027 | −86° | **0.601** | **0.702** | 1164 km |
| 500 | 0.112 | 0.051 | −161° | 0.375 | 0.458 | 655 km |

| era | mean IoU | after Δlon | mean kappa | after | mean abs Δlon |
|---|---|---|---|---|---|
| 0–100 Ma | 0.617 | 0.667 | 0.658 | 0.716 | **5°** |
| 100–260 Ma | 0.558 | 0.621 | 0.592 | 0.665 | **12°** |
| 260–525 Ma | 0.272 | 0.470 | 0.264 | 0.544 | **73°** |

Read plainly: through the Mesozoic and Cenozoic the two reconstructions are the same world
to within a few degrees of longitude and a coastline's width. From the Devonian back they
are not — at 420 Ma the overlap is *worse than chance* (kappa −0.04) until a rigid rotation
is applied, after which it recovers to 0.47. The disagreement is almost entirely a **single
longitude number per age**, which is exactly the signature the longitude problem predicts:
palaeomagnetism fixes palaeolatitude and never palaeolongitude. The latitude check confirms
it — the land-versus-latitude profiles agree throughout, including where longitude does not:
RMS **6.7–9.5%** and correlation **0.87–0.97** across 400–525 Ma, the very ages where the
longitude fit is largest.

### 3.1 Whose longitude is it?

A rigid offset between two maps says nothing about which one moved. A third witness settles
it: **PALEOMAP_PlateModel.rot**, Scotese's own rotations, applied to present-day land.

| age | ours vs PALEOMAP | DTM vs PALEOMAP | DTM vs ours | Scotese plates vs ours |
|---|---|---|---|---|
| 50 | **+0°** (κ 0.76) | +7° | +7° | +1° |
| 90 | **+0°** (κ 0.62) | +9° | +8° | −4° |
| 150 | **+0°** (κ 0.74) | +16° | +14° | −6° |
| 200 | **+0°** (κ 0.76) | +12° | +11° | +18° |
| 250 | **+0°** (κ 0.68) | +3° | +3° | +3° |
| 300 | **+2°** (κ 0.61) | −19° | −23° | +1° |
| 350 | **+1°** (κ 0.58) | −24° | −45° | −13° |
| 400 | **+1°** (κ 0.54) | −39° | −88° | −31° |
| 450 | **−2°** (κ 0.59) | −88° | −86° | −51° |
| 500 | **−2°** (κ 0.58) | −146° | −167° | −30° |

**Our terrain sits in the PALEOMAP frame to within 2° at every one of ten ages, from 50 to
500 Ma.** That is the control passing, and it confirms from the terrain side what WP-04
argued from the tracking side: the PaleoDEM arrives in Scotese's frame and our pipeline does
not disturb it.

So the Palaeozoic offset belongs to **Blakey vs Scotese**, not to us. Two independent
published reconstructions place the early Palaeozoic continents up to 146° of longitude
apart, and we are faithful to the one we are built from.

### 3.2 Scotese has moved too

The 16 numbered PALEOMAP plates are the older atlas (© C. R. Scotese, ~2000). Against our
terrain they sit within **13° through 0–306 Ma** — and then diverge to **−30°, −60°, −54°,
−31°** at 342, 425, 458 and 514 Ma. Their 0 Ma control is clean (Δlon +1°, agreement 91.4%),
so the geometry is trustworthy even though their land *area* is not comparable (Scotese draws
Antarctica and Greenland as ocean and overprints modern coastlines, names and a legend, which
is why their land reads 21.9% at the present day).

The conclusion is worth stating in its own right: **Scotese's own Palaeozoic longitudes moved
by up to 60° between the ~2000 atlas and the 2016 rotation model our PaleoDEMs are built on.**
Palaeozoic longitude is not a number any reconstruction should be quoted to the degree, and
the app should say so.

---

## 4. Shelf seas — the Triassic Pangaea has no continental shelf

DTM's bright shallow-water tint is a cartographic class, not a depth contour, so it was
calibrated rather than assumed: at 0 Ma the tint covers 9.53% of the surface and our field
matches that area at **z > −1305 m** (9.62%). That cut was then frozen and applied unchanged
at every other age.

The last two columns below are asked **only where both models put continental crust, after
the rigid longitude fit** — otherwise the answer is about placement, not about flooding.

| age | DTM shelf | ours | Δ | their shelf = our land | their land = our shelf |
|---|---|---|---|---|---|
| 0 | 9.5% | 9.4% | −0.1 | 19% | 1% |
| 30 | 11.2% | 7.8% | −3.5 | 74% | 8% |
| 90 | 14.4% | 15.0% | +0.7 | 43% | 19% |
| 150 | 9.9% | 7.7% | −2.2 | 72% | 15% |
| 180 | 8.1% | 4.7% | −3.4 | 77% | 6% |
| 200 | 8.0% | **3.1%** | **−4.9** | **83%** | 4% |
| 240 | 8.0% | **1.8%** | **−6.2** | **93%** | 2% |
| 300 | 11.9% | 14.8% | +2.9 | 36% | 18% |
| 380 | 11.8% | 19.7% | **+7.8** | 46% | 45% |
| 420 | 11.4% | 19.9% | **+8.6** | 32% | 37% |
| 470 | 9.9% | 17.9% | **+8.0** | 38% | 30% |
| 525 | 5.0% | 16.4% | **+11.4** | 19% | 28% |

The 0 Ma row is the control and it passes: the two agree to 0.1 points and only 19% of DTM's
shelf is dry land in ours, which is the resolution difference between a 20 km grid and a
thumbnail.

**The Triassic–Jurassic fails badly.** At 240 Ma we draw **1.8%** shallow sea against DTM's
8.0%, and **93% of everything Blakey draws as shelf sea we draw as dry land**. Rendered side
by side the difference is not subtle: DTM's 240 Ma Pangaea carries a wide bright shelf all
round its margin, a broad epicontinental sea over northern Asia and a shelf-covered Tethyan
archipelago; ours is a solid mass with a fringe one or two pixels wide and essentially no
epeiric sea anywhere. This is the same defect the +5 to +9 point land excess reported in §2
— it was never extra continent, it was missing sea. `build/epeiric.py` exists precisely for
this and does not reach the Triassic.

**The Palaeozoic fails the other way.** From 360 Ma back we draw 3–11 points *more* shallow
sea than Blakey does, and 25–45% of what he draws as dry land we have under water. Given that
DTM's own Palaeozoic land fraction is close to ours (§2), the two disagree about how much of
the same continent is flooded, in opposite directions in the two eras. That is a genuine
open disagreement between published reconstructions rather than an obvious defect on our
side, and it is recorded as such.

---

## 5. Ice — a check that passes, against a reference that cannot carry it

| age | DTM ice | ours | DTM polar | our polar | our ice as % of land | `ice_audit` literature range |
|---|---|---|---|---|---|---|
| 0 | 2.55% | 2.98% | 2.53% | 2.95% | 10.1% | 8–13% |
| 21 ka | 5.98% | — | 4.89% | — | — | (our nearest keyframe is 0 Ma) |
| 30 | 2.25% | 1.97% | 2.12% | 1.76% | 6.0% | 5–10% (25 Ma) |
| 50 → 250 | 0.00–0.04% | **0.00%** | **0.00%** | **0.00%** | 0% | 0–1% |
| 280 | 1.65% | 1.48% | 0.92% | 1.48% | 6.0% | 3–10% |
| 300 | 1.56% | 3.72% | 1.06% | 3.72% | 16.5% | 10–22% |
| 320 | 0.17% | 3.06% | 0.05% | 3.06% | 12.2% | 10–22% (315 Ma) |
| 440 | 0.48% | 2.34% | 0.00% | 2.33% | 13.4% | 5–16% (445 Ma) |

**The long ice-free interval is the result worth recording.** Across fourteen keyframes from
50 to 250 Ma both reconstructions carry no ice sheet at all — DTM's residual 0.00–0.04% is
scattered single-pixel mountain snow at low latitude, and our field is exactly zero. Two
independent sources agreeing that the Mesozoic had no polar ice is a check that passes, and
this project has learned to write those down.

**At the Palaeozoic glacial maxima we are inside the literature and DTM is below it.** At
300 Ma our ice is 16.5% of land against the 10–22% that `build/ice_audit.py`'s literature
table gives for the Late Palaeozoic Ice Age peak; DTM's is 7.0% of land, and correcting for
this audit's 17% low bias only lifts it to ~8.4%. At 320 and 440 Ma Blakey draws essentially
no polar ice at all, where the record has a Pennsylvanian maximum and the Hirnantian
glaciation respectively. **Blakey's series is not a usable ice reference in the Palaeozoic**;
it is internally inconsistent about whether ice sheets get painted, and where our two differ,
the literature backs the app.

**The spatial-pattern check the handoff wanted cannot be delivered at the interesting ages.**
At 0 Ma, where both sides describe the *same real ice sheets*, the ice IoU is only 0.430 —
that is the noise floor of this measurement, set by margin shading and the 17% bias, not by
disagreement. No deep-time age comes close to it, and at the ages where it might have meant
something the reference has no ice to compare against. Ice *area* remains checkable
(`ice_audit.py` already does it properly); ice *pattern* against DTM does not.

---

## 6. F1 — the future series, and the largest single defect this audit found

Our future is built by rigidly rotating present-day plate groups toward `GROUP_TARGET` in
`build/build_fields.py`. It had never been checked against anything.

`PALEOMAP_PlateModel.rot` carries rotations to **−250 Ma**, so the check is quantitative
rather than a look at a JPEG. Those rotations were validated first: advected to −250 Ma they
reproduce the Future World arrangement — Africa central, North America west, South America
SSW, Eurasia east, Antarctica due south, an interior sea, and an empty Pacific hemisphere.
They are a fair stand-in for `20F250v4.jpg`.

### 6.1 The future series destroys a third of Earth's continental area

| +Myr | our land | Mkm² | r50 | r90 | emptiest hemisphere | PALEOMAP land | Mkm² | r50 | r90 | emptiest |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 29.0% | **148.1** | 58° | 116° | 9.7% | 31.1% | **158.8** | 59° | 118° | 11.5% |
| 50 | 25.3% | 129.0 | 58° | 102° | 7.0% | 30.1% | 153.6 | 57° | 119° | 12.6% |
| 100 | 23.8% | 121.5 | 56° | 89° | 2.5% | 29.5% | 150.6 | 56° | 119° | 12.0% |
| 150 | 22.2% | 113.3 | 52° | 76° | **0.3%** | 29.9% | 152.7 | 61° | 116° | 12.6% |
| 200 | 20.4% | 104.0 | 46° | 66° | 0.2% | 30.0% | 152.9 | 62° | 95° | 7.3% |
| 250 | 18.2% | **92.6** | 41° | 60° | 0.2% | 29.4% | **150.0** | 50° | 76° | 1.3% |

*r50/r90 are the angular radii holding 50% and 90% of the land about its own centroid — how
tightly the world is assembled, independent of where it sits. PALEOMAP's mask is rasterised
and closed, so it carries about +2 points of its own bias; the point is that it is flat.*

**Continental crust is conserved over 250 Myr. Ours is not: 148.1 → 92.6 Mkm², a 37% loss.**
PALEOMAP's rigid rotations lose 5.5%, all of it rasterisation. The loss is monotonic and
smooth, and the mechanism is visible in `future_grid`:

```python
out = np.maximum(out, z)          # overlap -> collision keeps the high ground
```

Where two group rotations land on the same ground, one survives and the other's area is
annihilated. The signature confirms the mechanism exactly — the loss is concentrated in low
ground:

| +Myr | land > 1 km | land > 2 km | land < 1 km | mean land elevation |
|---|---|---|---|---|
| 0 | 30.1 Mkm² | 8.7 Mkm² | 118.0 Mkm² | 667 m |
| 250 | 27.6 Mkm² | 8.6 Mkm² | **65.0 Mkm²** | **879 m** |

High ground is flat to within 8%; low ground falls 45%; the mean elevation of what survives
rises by 212 m. `maximum` is a "high ground wins" rule, so overlapping plains are deleted and
mountains are not. Coastal plain, shelf and continental interior are exactly the ground a
biosphere lives on, and 53 Mkm² of it disappears over the series.

### 6.2 It also assembles too early and too tightly

Our emptiest hemisphere is down to **0.3% land by +150 Myr**, where PALEOMAP is still at
12.6% and only closes to 1.3% at +250. And at +250 our supercontinent is materially more
compact than Scotese's: **r90 60° against 76°**. In ours 90% of the land lies within 6,650 km of its own
centroid; in Scotese's it takes 8,450 km, and his Pangaea Ultima sprawls over roughly 120°
of longitude.

### 6.3 The six claims from `20F250v4.jpg`, answered

| # | claim | verdict | evidence |
|---|---|---|---|
| 1 | **Africa at the centre** of the assembled mass | **HOLDS** | Africa's land centroid is **962 km** from the centroid of all land — nearest of any group; next is Australia at 3,922 km |
| 2 | North America **WNW**, South America **SSW**, Eurasia **east** | **PARTLY** | bearings from Africa: N America **298° (WNW)** ✓, Eurasia **66° (ENE)** ✓, South America **247° (WSW)** where Scotese gives 201° — right side, ~45° too far north |
| 3 | a **"Mediterranean Mts"** collisional belt NE from Africa into Eurasia | **FAILS** | land above 2 km is 8.7 → 8.6 Mkm² across the whole series. The construction rotates present topography and resolves collisions with `maximum`; it has no mechanism to build an orogen, so no belt can appear anywhere |
| 4 | Antarctica + Australia a **SEPARATE southern mass** on a narrow neck | **FAILS** | Australia sits **2,969 km east of Africa on bearing 85°**, welded into the main mass; Antarctica is 5,786 km south on 185°. In PALEOMAP Australia is at 121°/11,032 km, in Antarctica's quadrant |
| 5 | an **interior sea** survives — Pangaea Ultima is not a solid disc | **PARTLY** | an enclosed sea does exist — **12.2 Mkm²** inside the main mass, 13% of our land area, against PALEOMAP's 20.6 Mkm² and 13%, so proportionally the same ✓. But its shore is 30% South America, 23% Africa, 23% Antarctica, 16% Eurasia, **6% North America**. The sea is real; it is between the wrong continents |
| 6 | the **Pacific occupies essentially the whole opposite hemisphere** | **HOLDS** | emptiest hemisphere **0.2% land**, centred (155°W, 25°S); PALEOMAP gives 1.3% |

Two hold, two partly, two fail. The overall shape of the story the app tells about the future
— everything gathers, Africa in the middle, an ocean on the other side, a sea trapped inside
— survives the check. The internal arrangement does not, and the area loss is a defect
independent of any question about where the continents should go.

---

## 7. What this changes

Ordered by measured value.

1. **Flood the Triassic–Jurassic.** `epeiric.py` does not reach 150–250 Ma, and at 240 Ma
   **93%** of an independent reconstruction's shelf sea is dry land in ours. This is the
   largest terrain defect the audit found and it explains the +5 to +9 point land excess as a
   side effect. → **new register item G1, P1**
2. **Stop the future series destroying land.** 148 → 93 Mkm² over 250 Myr, concentrated in
   low ground, caused by `np.maximum` resolving group overlap. Any fix — allocating
   overlapped ground to one group, shrinking the targets so groups meet rather than
   interpenetrate, or conserving area explicitly — is better than the present behaviour.
   → **F12, P1**
3. **State the Palaeozoic longitude limit on the About page, with the number.** Two published
   reconstructions differ by up to **146°**, and Scotese's own model moved by up to **60°**
   between editions. A6 already asks for the honest limit; this supplies the measurement.
   → **A6 upgraded, and A8**
4. **Slow the future assembly and loosen it.** Pangaea Proxima closes ~100 Myr early and ends
   ~16° too compact in r90. → **F13**
5. **Say that no mountains are built in the future**, or build them. There is no orogeny in
   the future series by construction, so the "Mediterranean Mts" of the reconstruction our
   climate is calibrated on cannot appear. → **F14**
6. **Fix `frame_experiment.py`'s `Z_RANGE`** to 8000.0 and re-state its shelf boundary.
   → **E6**

### What passed, and should be recorded as passing

- **The reprojection and the present-day control**: 96.8% agreement, IoU 0.897, 3 km mean
  displacement, reference land 28.8% against Earth's 29.2%.
- **Land area through the Mesozoic and Cenozoic**: mean bias +1.6 pp over eight ages,
  |Δlon| 5°.
- **Our terrain is in the PALEOMAP frame** to within 2° at every one of ten ages, 50–500 Ma.
  This is the terrain-side confirmation of WP-04 §1.
- **The Mesozoic is ice-free in both reconstructions**, at fourteen consecutive keyframes.
- **Our Palaeozoic ice extent is inside the literature range where DTM's is below it** —
  16.5% of land at 300 Ma against a 10–22% target.
- **Palaeolatitude agrees everywhere**, including where longitude does not: land-versus-
  latitude RMS 6.7–9.5% and correlation 0.87–0.97 across 400–525 Ma.

---

## 8. Limits of this audit, stated plainly

- **The caption is masked.** Every DTM map carries "«age» / © CPGS" burnt into the lower left.
  It is masked identically on both sides, which costs about **2.9% of the globe** in a fixed
  patch of southern-hemisphere map space. Fractions are over the surviving 97.1%.
- **Ice area reads ~17% low** on the reference, at both the present day and the LGM. Ratios
  between ages survive it; absolute Mkm² from the reference should be read as a lower bound.
- **Deep-ocean bathymetry cannot be compared.** From 15 Ma back, DTM's abyssal ocean is a
  near-flat fill (20–37% of ocean pixels in one colour bin), so only the present-day and
  Pliocene maps carry real bathymetry. The shallow ramp is comparable; the deep basins are not.
- **The Scotese numbered plates give geometry, not area.** They omit Antarctic and Greenland
  ice as land and overprint modern coastlines, names, subduction ticks and a legend. Their
  0 Ma longitude control is clean (+1°); their 0 Ma land fraction reads 21.9%.
- **The shallow-water cut is calibrated at 0 Ma and assumes the palette is stable.** The
  present map is real bathymetry and the deep-time maps are schematic, so the cut carries
  that assumption. The Triassic and Palaeozoic conclusions were checked at −500 m and −2000 m
  as well and do not flip.
- **21 ka is reported but excluded from the summary.** Our nearest keyframe is 0 Ma, which is
  the modern world and not the Last Glacial Maximum, so the comparison is between the wrong
  two things by 4.3 points of land.
- **`paleomap_land` is a rigid advection of present-day land**, so it ignores terrane
  accretion and flooding. It is used for frame alignment and area conservation, where those
  omissions do not matter, and never as a palaeogeography.

---

## Reproducing this

```bash
cd "Deep Research/modeling" && ../../venv/bin/python audit_reconstruction.py
```

`--validate` runs the present-day control alone; `--dtm`, `--frames`, `--scotese` and
`--future` run one section each; `--selftest` checks the Mollweide round-trip, the equal-area
property, the colour rules against the learned palette, the decode against
`build/fieldpack.py`, and the present-day control. Read-only throughout — it writes nothing,
and it imports `build/` only to reuse the app's own ice arithmetic and its future rotations,
so a change to `GROUP_TARGET` shows up here instead of leaving this report describing a
future the app no longer builds.
