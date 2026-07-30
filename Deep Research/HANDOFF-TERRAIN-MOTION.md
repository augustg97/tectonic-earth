# Handoff — make landforms emerge tectonically (MODEL-GAPS section H)

**Written 2026-07-29. Nothing in `build/` or `web/` was touched by the session that wrote
this** — another session was working the repo concurrently, so this round is research and
planning only. Everything below is a proposal with its evidence attached.

**Read first, in this order:**
1. `research reports/WP-08-terrain-in-motion.md` — the six findings and their numbers.
2. `MODEL-GAPS.md` section H — the six items, the governing constraint, the sequencing.
3. This file — implementation detail, traps, and the definition of done.

**Re-measure before you start:**
```bash
cd "Deep Research/modeling" && ../../venv/bin/python audit_terrain_motion.py
```
It should print `at baseline` on all four numbers. If it does not, the app changed under
this plan and the numbers in WP-08 need re-deriving before you trust any of them.

---

## The one-paragraph brief

The app's mountains are in the right place at the right height at the right time — that was
measured at four orogens and it holds (WP-08 Finding 0). What is wrong is that they do not
*arrive* like mountains. The app cross-fades between keyframes that are 14–42 texels apart,
so crust ghosts instead of sliding; the procedural ridge-and-valley detail is nailed to
latitude and longitude, so a continent drifts out from under its own texture; relief lands
in one 5 Myr step (+5,890 m for the Himalaya) and inflates uniformly in place; and no
tectonic information reaches the shader at all, so it cannot draw a fold fabric, a suture or
a foreland even in principle. Six items, sequenced **H1 → H2 → H6 → H4 → H3 → H5**.

**The governing constraint, restated because it is the one that can do damage:** the
PaleoDEM is authoritative. H1, H2, H4, H5 and H6 must leave every keyframe's hypsometry
unchanged. Do not build an uplift model for 0–540 Ma — Scotese already did the geology, and
adding one puts error into data that is currently correct.

---

## H1 — Advect instead of cross-fade

### The change in the shader

```glsl
// replaces web/index.html:1511-1513
// dAB is the uv displacement carrying crust from keyframe A to keyframe B.
float baseElev(vec2 uv, vec2 dAB){
  return mix(decElev(texture2D(elevA, uv + mixf * dAB).r),
             decElev(texture2D(elevB, uv - (1.0 - mixf) * dAB).r), mixf);
}
```

Each keyframe is carried toward the other so that the *same piece of crust* lines up in
both taps, then blended. At `mixf` = 0 and 1 this is exactly today's behaviour, so the
keyframes themselves cannot move — which is also the gate: **hypsometry at every integer
keyframe must be bit-identical to today's.**

### Where `dAB` comes from

Three sources, in descending order of quality. Prototype on (2), ship (1).

1. **Exact, from the rotation model.** Rasterise a plate-ID field per keyframe from the
   Merdith topologies that `build_plates_gplates.py` already resolves, then apply the finite
   rotation from age A to age B per plate. No block-matching noise. This is the one to ship,
   and it shares its plate-ID raster with H2 — build them together.
2. **The existing `_m` field.** Already shipped, already bound as `motA`, and currently
   sampled by nothing. Free, and enough to see whether the idea works in an afternoon. Not
   shippable: it is block-matched over a ±15 Myr baseline, so it is smoothed and
   confidence-gated and undershoots fast plates (the known Deccan half-distance problem).
3. Hybrid — `_m` where its confidence channel is high, rotations elsewhere. Only if (1)
   turns out to be too coarse near boundaries.

Proposed new field **`_v`**, 1024×512, WebP lossless:
`R,G` = uv displacement to the next younger keyframe, signed, scaled to a fixed maximum;
`B` = **tear** — the local divergence of the displacement field.

### The tear channel is the point, not a side effect

Warping across a plate boundary does not close cleanly, and both failure modes are physically
correct:

- **Divergence opens a gap** at a spreading ridge. That is new crust, and the younger
  keyframe already contains it — take the gap from B.
- **Convergence overlaps.** That is the collision. **This is the shortening signal H4
  needs**, and it is the same insight WP-07 recorded for the future branch, where 12.8 Mkm²
  of land-on-land overlap is computed and then deleted by `np.maximum`.

So H1 and H4 share one field, and getting H1 right hands H4 its main input for free.

### Two traps specific to this warp

**Poles.** A uv displacement in longitude is `dlon / cos(lat)` texels, which diverges at the
pole. An uncapped warp smears the high latitudes into streaks. `seafloor.py` already fades
its distance-transform work out poleward of 72° for the same reason, and `polar_lowpass`
exists in `build_fields.py` — follow that precedent rather than inventing a new one, and cap
the displacement magnitude.

**The antimeridian.** Elevation textures are `RepeatWrapping` in S, so a longitude warp wraps
correctly for free — but only if `dAB` itself is computed with `(dlon + 180) % 360 - 180`.
This project has now had longitude-treated-as-a-finite-axis bugs in three independent places
(`README` §, the `make_periodic` work, `future_grid`'s non-integer harmonic). Assume it will
happen again here.

### Enumerate every consumer — WP-06's third rule

Warp everything that is a property of the **crust**:
`_e` (elevation), `_d` (drainage / substrate / fetch), `_w` (lake depth), `_o` (ocean
structure).
Do **not** warp `_r` (rainfall) — that is a property of the atmosphere over a *position*, and
warping it would drag the ITCZ around with the continents.

Getting this list wrong is subtle and slow to notice: warp only `_e` and the rivers, lakes and
sea-floor fabric will detach from the terrain they belong to and slide across it.

### Cost

`elevAt` is called **five times per pixel** for the hillshade gradient
(`web/index.html:1885-1887`). Sample `_v` **once** per pixel and pass `dAB` down into
`baseElev` — do not sample it inside `elevDetail`, or the cost is 5× for nothing. The
instruction budget here is real and has already bitten: six `fbm3` taps once made the
fragment program fail to *link* on software GL, with no compile error at all.

---

## H2 — Material coordinates, so texture rides with the crust

`elevAt` evaluates every noise tap at `dirFromUv(uv)`, a pure function of position
(`web/index.html:1390-1394`, called at :1588-1590). There is no age, `mixf` or `uTime`
anywhere in the terrain noise, and `uDetail` is set to 1 at construction and never written
again.

### Implementation

Nearest-filtered **plate-ID texture** (shares the raster with H1) plus
`uniform vec4 uPlateQ[64]` — one quaternion per plate, interpolated in JS between the two
keyframes. The shader rotates `sdir` into a fixed reference frame by its plate's quaternion
and samples the noise there.

**Do not store lon/lat in an 8-bit texture instead.** 360° over 256 levels is 1.4°, about
156 km, against noise whose finest octave resolves 1.3 km. It will look like a fix and be a
quantiser.

Plate IDs do not interpolate, so the ID raster snaps at keyframe boundaries. That only
matters within a few cells of a plate boundary, because neighbouring cells on the same plate
rotate identically — acceptable, and softenable later if it shows.

### Which taps move, and which must not

**Move — these belong to the rock:**
`detail3` micro-relief, both taps (`sdir*260`, `sdir*70`); the normal-perturbation grain
(`sdir*145`); the lithology mottle (`sdir*11`); the bare-rock colour variation (`sdir*33`).

**Stay geographic — these belong to the climate or the water:**
the tundra polar mottle (`sdir*38`); the glacier tongue noise (`sdir*22`); cloud noise; water
sheen; the savanna stipple and vegetation mottle (vegetation follows climate, not crust).

Moving a climate pattern onto material coordinates would drag the tundra dapple around with
the continent — wrong, and it will not be obvious in a still.

---

## H6 — Do this early; it is three lines and it unblocks honest comparison

The vertex stage mixes the encoded byte and decodes after (`web/index.html:1287`) while
`baseElev` decodes then mixes (:1512). `dec_elev` is quadratic, so displaced geometry and
shaded elevation disagree mid-interval — worst exactly where a coastline is migrating, which
is where you will be looking. Make the vertex stage decode-then-mix.

While there: `motion.classify()` and `motion.encode_bounds()` are dead code that two
independent surveys of this repo read as working features — use them or delete them. And
`build_plates_gplates.py:51` maps `OrogenicBelt` → `"trench"`; give it its own class, because
H4 wants exactly that geometry.

---

## H4 — The tectonic-state field, and the fabric that makes it read as collision

New per-keyframe texture **`_t`**, 1024×512, derived from the plate topologies + H1's
displacement field + the shipped `_e`. **No DEM needed**, so it costs about 2 s a keyframe
like `build_surface.py` (~8 min for 251), not a full field rebuild.

| ch | quantity | source |
|---|---|---|
| **R** | shortening rate | negative divergence of the H1 displacement field, plus proximity to a resolved `SubductionZone` / `OrogenicBelt` sub-segment |
| **G** | orogen age — Myr since this cell last exceeded a shortening threshold, saturating ~400 Myr | integrate R backwards through the keyframe series |
| **B** | structural azimuth — fold-axis direction, perpendicular to shortening, i.e. parallel to the suture; encode 0–180° | shortening direction |

### What the shader does with it

**Anisotropic fold fabric — this is the single strongest cue.** Stretch the `detail3` domain
along the azimuth in B so ridges run *along* the belt. Real orogens are stripes: the
Valley-and-Ridge Appalachians, the Zagros, the Jura, the Verkhoyansk. Isotropic roughness
reads as bumpy ground however tall it is. **Reuse the sea floor's abyssal-hill machinery
rather than writing new** — `_o`'s G/B channels already orient an anisotropic fabric by
spreading direction, and that code is debugged.

**Character by orogen age.** Young (G≈0): high ridged fraction, sharp crests, bare rock, deep
incision. Old (G large): smooth fbm, rounded summits, soil and vegetation, dendritic
drainage. This is what makes the Appalachians visibly *wear down* rather than merely get
shorter — the elevation data already does the height, and this does the ageing.

**Active front.** Where R is high, a narrow band of fresh rock and steep relief on the
vergent side.

### Calibration order

Tune H4's constants **after H1 has shipped**, never before. WP-07's `SUTURE_UPLIFT` was tuned
to top up relief already near 2 km and then had to build an orogen from a peneplain once
erosion was corrected — *two changes that compose are one calibration.* H1 changes what the
relief under H4 looks like at every non-keyframe age.

### Validation

- Five Britannica paleogeographic maps with an explicit **Mountains** legend class at 306,
  255, 237 and 152 Ma, in `Deep Time Maps and Resources/`, all named
  `Distribution-landmasses-regions-seas-ocean-basins-*.webp` with the suffixes `Permian`,
  `locations`, `locations-1`, `locations-2`, `locations-3` — the only source in the folder
  that maps mountains as a class.
- The 16 labelled Scotese PALEOMAP maps name mountain belts.
- `research reports/FRAME-REGRESSION-gate.md` already scores **39 named orogen features** and
  is a ready-made harness.
- **Licence: measure against all of these, never reproduce them.** © CPGS / © C. R. Scotese /
  © Encyclopædia Britannica.

---

## H3 — Regularise the source series (the only item that can trip the publish gate)

Two problems. Do **(a) alone first and re-measure** — H1 and H4 may carry (b) on their own,
and (b)'s fix is the riskier one.

**(a) Authoring noise.** Land above 1 km moves +2.30 pp then −2.80 pp across 15→20→25 Ma, and
+2.52 then −2.75 across 95→100→105. Spike-and-revert on single frames; ~1.5 Mkm² per pp; no
eustatic curve moves land above a kilometre at all. Use G1's remedy — score each frame
against its own neighbourhood median and damp only the excursions its neighbours contradict.
G7+G8's rule still governs: **record a disagreement, do not tune to it** — the one exception
being a frame that is anomalous against *its own neighbours*, which is the signature of
authoring rather than of geology.

**(b) The 5 Myr step.** If easing is still needed after (a), it must apply to the **relief
residual only, never to the base.** The comment at `web/index.html:5593` is explicit that
easing `mixf` globally makes continents accelerate and stall at every keyframe — it is there
because someone already thought of this.

**This item changes shipped hypsometry**, so it is the one that can move an `audit_all.py`
number. If a number legitimately improves, tighten its baseline in the same commit.

---

## H5 — Landforms of collision the grid cannot resolve

Same discipline as `epeiric.py` and the present-day lakes: seed only what the DEM provably
cannot carry, and say so.

**Foreland basins first.** A range *plus its parallel trough* is the diagnostic signature of
collision. The trough is 100–300 km wide and a few hundred metres deep — below what a 20 km
grid authored at 1° reliably carries. It follows from a flexural (elastic-plate) response to
H4's own topographic load, with one free parameter (effective elastic thickness), and it
draws the Ganges plain, the Po basin, the Alberta foredeep and the Appalachian foreland.

**Then accretionary wedges.** `seafloor.py` already builds trenches with an outer rise; the
wedge is the other half, and it is what makes a subduction zone read as *scraping* rather
than as a groove.

**F4 is part of this item, not separate** — back-arc basins by slab roll-back belong with the
rest of the convergent-margin geometry.

---

## Traps

Most of these have already cost this project a session each.

**Shader — all three of these show up as a BLACK GLOBE with working panels and labels:**
- GLSL reserved words: `flat`, `patch`, `sample`, `smooth`, `filter`, `shared`, `buffer`,
  `input`, `output`. three.js reports only `useProgram: program not valid`.
- **A backtick inside a FRAG/CFRAG comment** closes the JS template literal. APP never
  initialises. This has happened more than once.
- Duplicate declaration at the same GLSL scope.
- **`build/check_shader.py` catches all three plus brace balance and needs no browser. Run it
  before every shader ship.**

**Instruction budget is real.** Six `fbm3` taps on the per-pixel path once failed to *link*
on software GL with no compile error. Broad fields use single-octave `vnoise3`. Treat every
new texture read and noise tap on the whole-planet path as expensive — and remember `elevAt`
runs five times per pixel.

**The latitude flip.** In the FRAG, `float lat = 90.0 - uv.y*180.0` is the **negated**
geographic latitude, on both the globe and the map. It went unnoticed for years because `lat`
only ever fed hemisphere-symmetric climate. Any new code needing true latitude must use
`-lat`. `lonD` *is* true longitude.

**Field textures carry no cache version — and this work adds two new ones.** The eight JSON
files are fetched as `name.json?v=DATA_V` and stamped by `build/stamp_data_version.py`;
`web/fields/*` deliberately does not, because it is ~750 files that rarely change. **While
you are iterating on `_v` or `_t` you will be served stale textures** and the app will run
perfectly while showing the old ones. Hard-reload, or add a version to the new textures while
developing and strip it before shipping.

**`TEX_CAP = 24`** (`web/index.html:1022`) is the LRU texture cache. Six kinds per keyframe
today; two more takes it to eight, so 24 slots is three keyframes' worth and playback needs
two live at once. **Raise `TEX_CAP` when you add a texture kind** or playback will thrash.

**`frameAt()` returns the first interval containing the age**, so at an exact keyframe X the
app samples the field of X−5. This drives label jumps at exact keyframes and will confuse any
before/after taken at a round number. `build/probe_labels.py` replicates it offline.

**Deployment.** `build_site.py` `copytree`s `web/fields` → `docs/fields`, so new field
textures ship automatically — but new **JSON** must be added to `DATA_FILES` or it silently
never ships. `build_site.py` runs `audit_all.py --quick` as a **publish gate** and refuses to
publish if a number moved backwards.

**Process.** macOS has no `timeout(1)` — `timeout 200 chrome …` fails instantly with
`real 0.00`, which reads exactly like a hung render. `pgrep -f "build_fields.py"` matches the
waiter's own command line; use the bracket trick `pgrep -f "[b]uild_fields.py"`. A server or
build started with `&`/`nohup` inside a Bash call **dies when that call ends** — use
`run_in_background: true`.

**Another session is working this repo.** Rebase rather than clobber, and check `git status`
before assuming a file is as this document describes it.

---

## Verification — and the reason the usual recipe is not enough

**The artefact is temporal, so the evidence must be temporal.** A single screenshot cannot
show a cross-dissolve: at any fixed `mixf` the frame looks fine. **Ground truth is a strip of
renders at `mixf` = 0, 0.25, 0.5, 0.75, 1.0 across one keyframe interval, centred on a
collision.** WP-06 lost three rounds "verifying" an artefact against a viewport that
downsampled it away; this is a stricter version of the same trap, because here the artefact
is invisible to *any* still.

Suggested test cases, all of which the plan should visibly improve:
- **India–Asia, 60 → 20 Ma** — the +5,890 m step, and the biggest collision in the series.
- **Appalachians, 340 → 200 Ma** — ageing and decay; should go from sharp to worn, not just
  from tall to short.
- **A mid-ocean ridge at any age** — the divergence half of the tear channel.
- **A fast plate at 400 Ma** — worst-case displacement, median 42 texels.

**Rendering, because the Browser pane cannot composite the WebGL canvas here.** Screenshots
of the globe come back as a blown-out white blob and the pane reports `document.hidden ===
true`, so `requestAnimationFrame` never fires. Working recipe: copy `web/` to the scratchpad,
serve it with `build/serve.py`, and drive **headless Chrome with
`--enable-unsafe-swiftshader`**; freeze rAF with `W.requestAnimationFrame=()=>0`, then drive
frames by hand with `APP.step()` (about ×10). Camera is `state.rot` (radians;
centred longitude = `rot_deg + 90`), `state.tilt`, `state.zoom` (larger = further away,
default 3.05). `window.APP` also exposes `DATA`, `jumpTo`, `showFeature`, `projectLL`,
`selectAt`, and `window.__ERRORS` catches uncaught exceptions.

`web/_diag.html` tells "shader broken" from "just slow" in ~4 s. A full terrain shot is 2–4
minutes, dominated by loading ~750 textures rather than by rendering.

**Cheap non-visual diagnostic, and it is how the ice bugs were actually found:** dump the
field being debugged straight to a PNG from Python — H1's displacement magnitude, H4's
azimuth as hue, the tear channel red/blue — for three ages stacked. Seconds to make, shows
the pattern directly, and does not need the camera to be on the lit side.

---

## Definition of done

| gate | how |
|---|---|
| Hypsometry unchanged at every keyframe (H1, H2, H4, H5, H6) | land %, >1 km, >2 km identical to today's at integer ages |
| No shader regression | `build/check_shader.py` clean; globe renders; `window.__ERRORS` empty |
| No audit regression | `build/audit_all.py` at or better than baseline — it is the publish gate |
| The defect actually moved | `modeling/audit_terrain_motion.py` numbers **down**, and the baselines tightened in the same commit |
| It looks right | the five-frame temporal strip at India–Asia and at the Appalachians, judged by eye — **the user's eye, on the live site**, for the final call |

---

## Cost estimate

| item | build work | rebuild |
|---|---|---|
| H1 | plate-ID rasteriser + `_v` baker + shader | ~2 s/keyframe, ~10 min for 251. **No `_e` rebuild.** |
| H2 | shares H1's raster; shader + uniform plumbing | none |
| H6 | three lines + dead-code decision | none |
| H4 | `_t` baker + fabric in FRAG | ~2 s/keyframe, ~10 min. **No `_e` rebuild.** |
| H3 | regulariser in `build_fields` | **full field rebuild** — budget ~85 min, not the "35 minutes" four files still claim; that figure predates the grid doubling to 2048×4096 |
| H5 | flexure module + wedge in `seafloor.py` | full rebuild, or fold into H3's |

**The four items that carry most of the visual change — H1, H2, H6 and H4 — need no
elevation rebuild between them**, only two ~10-minute field bakes. That is the main reason
this sequencing is worth following: the bulk of the work can be iterated in minutes rather
than in hours, and only H3 and H5 pay the full rebuild.
