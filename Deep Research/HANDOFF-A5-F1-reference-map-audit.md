# Handoff prompt — A5 / F1, the reference-map audit

**Paste everything below the line into a new session.** It runs in parallel with the main
Deep Research work and touches nothing that work touches.

---

You are auditing the Tectonic Earth deep-time globe against two independent published
reconstructions. This is **register items A5 and F1** from
`Deep Research/MODEL-GAPS.md`. Read `Deep Research/README.md` and
`Deep Research/research reports/WP-04-closing-the-gaps.md` first — WP-04 §1 explains the
reference-frame problem this audit measures.

## What you are comparing

`Deep Time Maps and Resources/` holds three reference series. **They are copyrighted
(© CPGS, © C. R. Scotese) — measure against them, never reproduce them.** A numeric
comparison table is fine; shipping or committing the images is not.

| series | files | what it gives you |
|---|---|---|
| Deep Time Maps™ global Mollweide | 36 `*-MOLL-tn.jpg`, 32 distinct ages Present→525 Ma | land / shallow shelf sea / deep ocean / ice, as **colour classes** |
| Scotese PALEOMAP | 16 numbered `.jpg`, 0→650 Ma | the same, plus **named** oceans, continents, mountain belts |
| **Scotese Future World** | `18F050v4.jpg` +50 Ma, `19F150v4.jpg` +150 Ma, `20F250v4.jpg` +250 Ma | **the only external check our future series has ever had** |

Our own output is the shipped elevation field: `web/fields/phan_<age>_e.webp` (and
`fut_*` for negative ages), signed-sqrt encoded — decode exactly as
`Deep Research/modeling/frame_experiment.py:_decode()` does. There are 251 keyframes at
5 Myr spacing, so every reference age is within half a keyframe of one of ours.

## The four measurements, in value order

1. **Land fraction.** Classify each reference map's pixels into land / shelf / deep /
   ice by colour, in the Mollweide projection, and compare the land fraction with ours at
   the matched age. This is the single most diagnostic number and the cheapest to get.
2. **Shelf-sea extent.** The bright cyan band. Our 20 km DEM under-resolves epicontinental
   seas — that is why `build/epeiric.py` exists — and this says by how much, and where.
3. **Ice extent.** White. `build/ice_audit.py` already checks ice *area* against a
   literature table; this checks the **spatial pattern**, which area cannot.
4. **Continental position.** Where a coastline sits, not just how much there is. This is
   the frame check, and it is the one that interacts with the pending PALEOMAP switch.

## Method that will actually work

- **Reproject, don't eyeball.** The reference maps are Mollweide; our fields are
  equirectangular. Invert the Mollweide (the app's own shader does this — see the map
  view in `web/index.html`) to sample the reference at our grid, or forward-project ours.
  Getting this wrong makes every number meaningless, so **validate the reprojection on
  the present-day map first**: our 0 Ma frame against `00-Ma-PresentMOLL-tn.jpg` should
  agree closely, and if it does not, the reprojection is wrong, not the model.
- **Colour classification needs a legend, not a guess.** Sample the known regions of the
  present-day map to learn the class colours, then apply those to the deep-time maps —
  the palette is consistent across the series.
- **The maps are thumbnails.** Check the actual pixel dimensions before trusting fine
  detail; `-tn` means thumbnail and several are small.
- **Report per-age, not just an average.** The interesting result is *where* the
  disagreement concentrates. WP-04 found the frame error was worst in the Palaeozoic, and
  this audit should be able to say the same thing independently.

## For F1 specifically — the future

Our future series is built by rigidly rotating present-day plate groups toward
`GROUP_TARGET` in `build/build_fields.py`. It has never been checked against anything.
From `20F250v4.jpg` (© 2000 C. R. Scotese), the reconstruction our climate is calibrated
on (Farnsworth et al. 2024 used this geometry) shows:

- **Africa at the centre** of the assembled mass
- **North America to its west-northwest**, South America south-southwest, Eurasia east
- a **"Mediterranean Mts"** collisional belt running NE from Africa into Eurasia
- **Antarctica + Australia a SEPARATE southern mass** on a narrow neck, not fully merged
- **an interior sea surviving** between North America and Africa/Eurasia — Pangaea Ultima
  is not a solid disc
- the **Pacific occupying essentially the whole opposite hemisphere**

Check each of those against our +250 Myr frame and say plainly which hold.

**A stronger check is now available and is worth doing first:** `PALEOMAP_PlateModel.rot`
(already downloaded to `data/paleomap_gpm/…`, CC-BY 4.0) contains **future rotations to
−250 Ma**. So the future series can be compared against Scotese's *rotations* rather than
against a JPEG. That is a quantitative test, not a visual one.

## Rules for this work

Read `README.md` §2 — the six standing working rules — and follow them. The two that
matter most here:

- **Measure before concluding.** Every real finding in this project so far was invisible
  to inspection and obvious to a histogram.
- **Be honest in the assessment.** If our reconstruction disagrees with both references,
  say so with the numbers. If it agrees, say that too — a check that passes is a result
  worth recording, and this project has had several.

One more, learned the hard way across four rounds: **when an audit disagrees with the
app, check your own reference table first.** It has been the research's error, not the
app's, five times now.

## Deliverables

1. `Deep Research/research reports/WP-05-reconstruction-audit.md` — the numbers per age,
   per measurement, with a plain verdict.
2. `Deep Research/modeling/audit_reconstruction.py` — re-runnable, read-only, so the
   audit can be repeated after the PALEOMAP switch lands.
3. Register updates in `Deep Research/MODEL-GAPS.md` marking A5 and F1, and new items for
   whatever it finds.
4. A commit. **Do not commit any image from `Deep Time Maps and Resources/`.**

Do not change anything in `build/` or `web/`. This folder informs the model; it does not
edit it.
