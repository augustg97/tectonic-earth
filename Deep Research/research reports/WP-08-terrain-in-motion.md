# WP-08 — Terrain in motion: why mountains do not appear to emerge

**2026-07-29.** Investigation only; nothing implemented. The question came from the user as
a visual complaint: mountain ranges, seabeds and other places where crust piles up "seem
accurate, but do not visually appear to form in a natural geophysical fluid dynamic way."

The first job was to decide whether that is a data problem or a presentation problem,
because the two have opposite fixes and the wrong one is expensive. **It is a presentation
problem.** The heights and their timing are already right. What is wrong is everything that
happens between one keyframe and the next.

Every number here is reproducible with `modeling/audit_terrain_motion.py`, which reads the
**shipped** fields rather than the source DEMs, so it measures what a viewer sees.

---

## Finding 0 — The PaleoDEMs encode orogeny correctly, and this is the finding that sets the plan

Before proposing to build mountains, check whether they are already built. Sampling the
shipped `_e` field inside a plate-tracked box over four well-constrained orogens:

| orogen | rise | peak | decay | today |
|---|---|---|---|---|
| **Himalaya / Tibet** | p95 889 m at 60 Ma → 1,206 at 50 → 7,751 at 40 | 8,000 m at 25–30 Ma | 5,687 at 10 | **5,272 m** |
| **Appalachians** | 2,047 m at 340 Ma | **2,805 m at 300 Ma**, 20.6% of the box above 2 km | 1,255 at 200, 620 at 150 | **620 m** |
| **Caledonides** | 2,446 m at 420 Ma | 2,731 m at 340 Ma | 1,742 at 300, 1,409 at 200 | **151 m** |
| **Urals** | — | 1,409 m at 300 Ma | 488 at 250 | **520 m** |

That is the real history. The Appalachian curve in particular reproduces the literature
statement the supercontinent dossier records — Himalayan at ~300 Ma, 1–2 km now — and the
Caledonides wear from 2.7 km to 151 m. **Scotese & Wright already did the geology.**

The consequence for the plan is total, so it is stated as a constraint rather than a
finding: **the PaleoDEM is authoritative for where a mountain is and how high it is. This
work owns the path between keyframes and the character of the surface, and nothing in it
may change a keyframe's hypsometry.** Any session that "improves" the Himalaya is
introducing an error into data that is currently correct, and will trip `audit_all.py`.

One caveat found on the way: at 20–40 Ma the Himalaya box reaches **8,000 m, which is
`Z_RANGE` exactly** — the signed-sqrt encoder's ceiling (`build/fieldpack.py:13`). Scotese's
Tibet is being clipped at those ages. Whether the source exceeds 8,000 m is unmeasured;
raising `Z_RANGE` changes the elevation quantum everywhere and invalidates all 251 shipped
`_e` textures, so it needs a measurement before it needs a decision.

---

## Finding 1 — The app cross-dissolves crust that moves tens of texels

`baseElev` is a cross-fade between two stationary images:

```glsl
// web/index.html:1511-1513
float baseElev(vec2 uv){
  return mix(decElev(texture2D(elevA,uv).r), decElev(texture2D(elevB,uv).r), mixf);
}
```

That is a motion only if the crust barely moves between the two frames. It does not.
Tracking 162 present-day points on the app's own PALEOMAP rotations, over one 5 Myr
keyframe interval:

| age | km per step (med / p90 / max) | **texels of the 4096 grid** (med / p90 / max) |
|---|---|---|
| 10 Ma | 69 / 418 / 559 | 7.1 / 42.7 / 57.1 |
| 50 Ma | 137 / 241 / 633 | 14.0 / 24.7 / **64.7** |
| 100 Ma | 150 / 270 / 340 | 15.4 / 27.6 / 34.7 |
| 200 Ma | 222 / 300 / 515 | 22.7 / 30.6 / 52.6 |
| 300 Ma | 192 / 212 / 303 | 19.7 / 21.7 / 30.9 |
| **400 Ma** | 410 / 499 / 508 | **42.0** / 51.0 / 51.9 |
| 500 Ma | 234 / 318 / 537 | 24.0 / 32.5 / 54.9 |

One texel is ~9.8 km. So the typical keyframe cross-fades relief across **14 to 42 texels**,
and the fastest crust across **65**. A dissolve at that scale is a double exposure: every
mountain front, coastline and trench splits into two half-amplitude copies at mid-interval
and snaps back at the keyframe. Continents do not slide, they fade from one place to
another — which is precisely the reported symptom, and it is worst in the Palaeozoic, where
the median displacement is 410 km per step.

WP-06's first method rule was to measure the artefact's scale before matching it to a
candidate. This is that measurement, and it rules out several tempting small-scale
explanations at a stroke: at 42 texels, no amount of encoder quality, texture filtering or
noise tuning is the cause.

---

## Finding 2 — The procedural micro-relief is nailed to latitude and longitude

Every ridge, crest and valley finer than the 9.8 km grid comes from `detail3`, a ridged-noise
model that is genuinely good — it is why the Himalaya have crests and the Amazon does not.
But it is evaluated at a fixed geographic direction:

```glsl
// web/index.html:1588-1590
float elevAt(vec2 uv, float rug){
  return elevDetail(baseElev(uv), dirFromUv(uv), rug);
}
// web/index.html:1390-1394 -- a pure function of uv, with no age term
vec3 dirFromUv(vec2 uv){ ... }
```

There is **no `mixf`, no age and no `uTime` anywhere in the terrain noise.** `uDetail` is
set to 1 at construction and never written again. So the fine structure of a mountain range
is a property of the *place on the globe*, not of the *crust*: as a continent drifts, it
slides out from under its own mountains' texture, and the ridges stay behind. Only the
amplitude and the smooth↔ridged blend travel with the plate, because those come from the
interpolated field.

This is the same defect the sea floor was rebuilt to remove — abyssal-hill fabric keyed to
the present ridge rather than to the isochron (README §5.3). The land side never got the
equivalent fix.

---

## Finding 3 — Relief arrives as a step, and the source series has authoring noise on top

Two different problems, both visible in the same series.

**(a) The step.** Inside a plate-tracked box on the growing Himalaya, the p95 elevation goes
1,861 m at 45 Ma → **7,751 m at 40 Ma**: `+5,890 m in one 5 Myr keyframe`, then essentially
flat for the next 15 Myr. Rendered as a linear ramp in `mixf`, the entire plateau inflates
uniformly in place over five million years of scrub time. There is no propagation outward
from the suture, no advancing deformation front, no foreland trough — none of the things
that make a collision look like a collision. India really did collide, so this is not a data
error; but *where within the interval* the relief arrives is entirely an artefact of 5 Myr
keyframe spacing.

**(b) The noise.** Global land above 1 km, frame to frame:

| interval | Δ land >1 km |
|---|---|
| 15 → 20 Ma | **+2.30 pp** |
| 20 → 25 Ma | **−2.80 pp** |
| 95 → 100 Ma | **+2.52 pp** |
| 100 → 105 Ma | **−2.75 pp** |

Spike and immediate revert, on single frames, at both 20 Ma and 100 Ma. One percentage point
of the globe is ~1.5 Mkm², so this is roughly a third of the Alpine–Himalayan belt appearing
and vanishing within 5 Myr. No eustatic curve can move land above *one kilometre* at all.

This is the sibling of what G1 already recorded for shelf area — "the raw PaleoDEMs swing
8.6 → 4.5 → 3.0 → 6.3 → 1.6 → 8.2 → 13.8% across seven adjacent frames while sea level slides
smoothly, which is authoring and not geology" — now measured in relief. G1's remedy (score
each frame against its own ±70 Myr neighbourhood) is the precedent for the remedy here.

Land area is jumpy too: 36.5% → 33.1% → 29.1% across 40 → 45 → 50 Ma.

---

## Finding 4 — No tectonic state reaches the shader, so it could not draw a collision if it tried

Four separate places where the information exists and is discarded:

1. **`motA` is bound but never sampled.** The motion texture is declared
   (`web/index.html:1306`), allocated (:3576) and bound every frame (:5628), and there is not
   one `texture2D(motA, …)` in the fragment shader. Motion reaches the CPU for the arrow
   overlay and nothing else.
2. **`motion.classify()` is dead code.** It computes ridge / trench / transform strength from
   the divergence and shear of the motion field (`build/motion.py:145-181`) and nothing calls
   it. `motion.encode_bounds()` likewise. Two independent surveys of this codebase read these
   as working features.
3. **Merdith's own orogens are thrown away.** `build_plates_gplates.py:51` maps
   `OrogenicBelt` → `"trench"`, collapsing a per-keyframe, correctly-rotated orogen geometry
   into a generic line colour.
4. **`plates_time.json` carries no velocity for any age ≥ 0.** The `r` field (relative speed)
   exists on 2,205 segments, all of them legacy synthetic *future* entries;
   `build_plates_gplates.py` never writes it and nothing reads it.

---

## Finding 5 — Relief is isotropic, and real orogens are not

`detail3` is isotropic ridged noise: it makes rough ground, and rough ground at any
orientation. Real mountain belts are **linear** — parallel fold ridges, en-échelon ranges, a
structural grain that runs along the suture. The Valley-and-Ridge Appalachians, the Zagros,
the Jura and the Verkhoyansk are stripes, and stripes are what the eye reads as *crust that
has been shortened*. Isotropic roughness reads as bumpy ground, however tall it is.

The machinery to fix this already exists in the project and is applied to the sea floor:
the abyssal-hill fabric is anisotropic and oriented by the spreading direction carried in
the `_o` texture's G/B channels. The land side needs the same treatment with a different
azimuth source.

---

## Finding 6 — Vertex and fragment stages interpolate elevation in different domains

```glsl
// web/index.html:1287 -- vertex: mix the ENCODED byte, then decode
float e=mix(texture2D(elevA,uv).r, texture2D(elevB,uv).r, mixf);
// web/index.html:1512 -- fragment: decode, THEN mix
mix(decElev(texture2D(elevA,uv).r), decElev(texture2D(elevB,uv).r), mixf)
```

`dec_elev` is quadratic, so `mix∘dec ≠ dec∘mix`. Mid-interval the displaced geometry and the
shaded, coloured elevation disagree, worst where the two keyframes straddle sea level —
exactly at a migrating coastline. Minor beside Findings 1–3, but it is three lines to fix
and it muddies any before/after comparison made while it is present.

Related documentation error worth correcting in the same pass: `handoff_blend`'s docstring
(`build_fields.py:875-877`) justifies itself by asserting that it blends "in the SIGNED-SQRT
domain the shader already interpolates keyframes in." That is true of the vertex stage only.
The blend is still the right thing to do — it was validated by land-area measurement, not by
the docstring — but the stated reason is wrong.

---

## Finding 7 — Land is blurry because detail is suppressed on low ground and then shaded at the wrong scale

Added 2026-07-30 from two screenshots the user supplied: a ~250 Ma globe over Siberia and
Laurasia, and a zoom onto Jurassic North America. Both show the same thing — vast smooth
tan-and-olive expanses with almost no structure, while the Altai/Tien Shan/Qilian belts in
the same frame *do* show ridges. Detail is present on high ground and absent everywhere else.
Four causes, all measured, and the fourth changes what the fix should be.

**(a) The procedural detail is deliberately scaled down on low ground, by a factor of 14.**

```glsl
// web/index.html:1583
float det=(n*250.0+n2*130.0)*(1.0+rug*1.5)*uDetail*clamp(z/900.0,0.15,1.0);
```

`rug` is near zero on a plain, so both multipliers collapse together:

| terrain | z | rug | procedural relief |
|---|---|---|---|
| coastal plain | 150 m | 0.00 | **±32 m** |
| interior lowland | 300 m | 0.05 | **±68 m** |
| upland | 900 m | 0.30 | ±276 m |
| mountain | 3,000 m | 0.90 | **±447 m** |

±32 m spread across a 24.5 km noise cell is a gradient of 0.13%. Nothing will shade that.
Both screenshots are almost entirely the first two rows.

**(b) The hillshade differentiates at 47 km while the detail runs down to 1.3 km.**

```glsl
// web/index.html:1885 -- central difference, so the baseline is twice this
float da=2.4/2048.0*PI;   // = 0.00368 rad = 23.5 km
```

The two detail generators produce ten octaves between them:

| generator | octave sizes |
|---|---|
| `detail3(d*260)` | 24.5 · 11.8 · 5.7 · 2.8 · **1.3** km |
| `detail3(d*70)` | 91.0 · 44.0 · 21.2 · 10.3 · 5.0 km |

Only **three of the ten** are coarser than the gradient's half-step. The other seven are
computed, added to the height field, and then differentiated over a baseline up to 18×
their own wavelength — which does not resolve them, it aliases them into low-amplitude
noise. The app is paying for detail it cannot show. This is the inverse of the
already-recorded failure where two systems own one scale band: here a wide band, roughly
1–20 km, is written by one system and read by none.

**(c) Bilinear magnification, no mipmaps, no anisotropy** (`web/index.html:1033-1034`). At
zoom the 4096-wide field magnifies to smooth ramps, which is the correct behaviour and is
exactly why the procedural layer has to carry the fine scales — and it currently does not,
per (a) and (b).

**(d) There is no headroom in the source, so a bigger texture is not the fix.**

| | grid | cell |
|---|---|---|
| source PaleoDEM (6 arc-min) | 3,600 × 1,801 | 0.100° = 11.1 km |
| shipped `_e` | 4,096 × 2,048 | 0.088° = **9.8 km** |

The shipped field is already **1.14× finer than the data behind it.** Raising it to 8192
would quadruple memory and rebuild time for literally zero additional information. **The
answer to "more resolution on land" is a better procedural layer and a hillshade that can
see it, not a bigger elevation texture.** Worth stating plainly because "increase the
resolution" reads as a texture-size change and that is the one thing here that cannot work.

**One further gap, and it is the interesting one.** `_d`'s drainage channel already carries a
per-keyframe valley network at 2048×1024, derived from the real terrain by priority-flood and
D8 routing — and it is used **only for colour** (riparian green, channels, marshes, deltas at
`web/index.html:2318-2334`). It never touches elevation or the normal. So the app already
knows where the valleys on a plain are and declines to carve them. Lowlands do not need more
*noise*; they need the structure the model has already computed. That is what distinguishes a
real floodplain from fbm.

---

## Finding 8 — The polygonal margins are a coarse field under a steep threshold

Visible in both screenshots and distinct from Finding 7 — the opposite defect. The pale
shelf-ice and shallow-water margins, and the small lakes, have hard quadrilateral edges at a
consistent cell size, not the organic fraying the ice model intends. Bilinear magnification of
a coarse grid followed by a steep threshold produces exactly that: the interpolant is
piecewise-bilinear, so a threshold through it traces the texel quads.

The rainfall field is the prime suspect on arithmetic, not on impression:

- `_r` is **1536 × 768 = 26.1 km/texel**, against elevation's 9.8 — **2.7× coarser**.
- `arid = 1 − clamp(Rf/0.85, 0, 1)`, then `Tela = −5.0 − 7.0*arid` — a **7 °C** swing.
- `ela = (T0 − Tela)/0.0058` — **172 m of snowline per °C**, so **1,207 m** over the range.
- `snow = clamp((zp − snowline)/400.0, …)` — a **400 m** ramp.

So the aridity term alone can move the snowline **3.0× the width of the ramp that draws it**,
and it does so on a grid 2.7× coarser than the terrain. A third of that range between two
adjacent rainfall texels is a full ramp width across 26 km, which thresholds into visible
polygons.

This is the same class as the accumulation term removed on 2026-07-22 — polar rainfall being
"tiny and NOISY … jittering the threshold a couple of degrees between neighbouring cells",
which was found to be the splotchiness rather than the ice model. That fix removed one
rainfall→ice path. **The `arid → Tela → ela` path was not touched and has three times the
leverage.**

Constraint on any fix: `ice_audit.py` currently passes 22/22 with the present ice line, and
the calibration behind `MARGIN_OFFSET = −5.0` is load-bearing. Smooth the *input* or widen the
*ramp*; do not re-tune the ice line, which is measured against the literature.

---

## What this adds up to

One symptom, six mechanisms, and WP-06's third method rule says to enumerate every consumer
before intervening on one. Fixing the cross-dissolve alone leaves the texture pinned to the
globe; fixing the texture alone leaves the crust ghosting; fixing both still leaves the
Himalaya inflating in place in one step, with no fabric to say the crust was shortened.

The plan they justify is **section H of `MODEL-GAPS.md`**, in eight items:

| | | |
|---|---|---|
| **H1** | Advect the fields between keyframes instead of cross-fading them | Finding 1 |
| **H2** | Give the shader a material coordinate so texture rides with the crust | Finding 2 |
| **H3** | Regularise the source series in time | Finding 3 |
| **H4** | Ship a tectonic-state field and draw an anisotropic fold fabric from it | Findings 4, 5 |
| **H5** | Seed the landforms of collision the 20 km grid cannot resolve | Finding 0 |
| **H6** | Fix the interpolation-domain mismatch and the dead code behind it | Finding 6 |
| **H7** | Carry real detail on low ground, and shade it at its own scale | Finding 7 |
| **H8** | Stop thresholding a 26 km field into polygons | Finding 8 |

**H4 and H7 must be calibrated as one change, not two.** The fold fabric and the isotropic
detail amplitude both write into `elevDetail`'s output over the same 1–25 km band. Tuning
either against a version of the other that is about to change guarantees re-tuning — the
lesson WP-07 recorded when `SUTURE_UPLIFT`, fitted to relief already near 2 km, had to build
an orogen from a peneplain once erosion was corrected.

**H7 must come after H1 and H2, and the reason is not cost.** More high-frequency land detail
makes both of those defects *worse*: more content to double-expose across a 14–42 texel
cross-dissolve, and a far more visible slide when the crust moves out from under a texture
that is pinned to the globe. Shipping H7 first would make the app look worse in motion while
looking better in a still.

`HANDOFF-TERRAIN-MOTION.md` carries the implementation detail, the sequencing argument and
the traps.

---

## Two method notes for whoever implements this

**The artefact is temporal, so the evidence must be temporal.** A single screenshot cannot
show a cross-dissolve — at any fixed `mixf` the frame looks fine. Ground truth is a strip of
renders at `mixf` = 0, 0.25, 0.5, 0.75, 1.0 across one keyframe interval, centred on a
collision. WP-06 lost three rounds "verifying" an artefact against a viewport that
downsampled it away; this one is invisible to a still image, which is a stricter version of
the same trap.

**Two changes that compose are one calibration.** WP-07 recorded this after `SUTURE_UPLIFT`,
tuned to top up relief that was already near 2 km, had to build an orogen from a peneplain
once erosion was corrected. H4's fabric constants tuned before H1 ships will be wrong after
it, because H1 changes what the relief under them looks like at every non-keyframe age.
