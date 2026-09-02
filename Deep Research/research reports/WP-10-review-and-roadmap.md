# WP-10 — Review and roadmap: mountains, performance, and a laptop-friendly ambient build

**2026-09-01.** A full read of the project as it stands (README, HANDOFF, the 154-iteration
register in MODEL-GAPS, the live shader and loader in `web/index.html`, the build pipeline),
plus headless renders and field measurements taken for this review. Nothing here has been
applied; it is the case for what to do next, in priority order, for the user to rule on.

Three complaints were raised: mountains read as squiggly in some places and flat or uniform in
others; the app is heavy on GPU, CPU and RAM; and Ambient mode is not a background mode. The
short version of this paper is that all three have the **same** cause, and one architectural
change addresses all three. The mountains are the exception in that they also need their own
model.

---

## 0. The answer in a page

1. **The mountains are noise, and the log already proved noise cannot get there.** Everything
   on land finer than ~50 km is synthesised per pixel from value noise: ridged fBm in the height
   (lattice cells of 24 km and 91 km, octaves down to ~1 km), a `sin²(fBm)` tone band, and a
   sine grating in the shading normal. The first two are the squiggle (ridged worms and
   contour loops); the grating is the "uniform" look. Two unit conventions a factor of 2π apart
   coexist in the shader, so the grating meant to draw 26 km and 13.6 km ridges actually draws
   163 km and 85 km stripes, and the tone bands documented as 26 km and 83 km sit near 8 km
   and 27 km. Measured on a Himalaya frame, the three constructions together move the picture
   by 8.5/255 and removing them *raises* organisation (coherence 0.39 → 0.43). The height
   gates that switch all of it on exclude deep time, and the 23.5 km hillshade stencil is blind
   at 47 km, so real ridge-and-valley, in the data or in the synthesis, is never lit. Iterations 75–77 measured the
   ceiling of this approach at 60 % of Blue Marble's organisation and closed the family. The
   sea floor was rebuilt on a *model* (crustal age, spreading direction, faulting, sediment);
   the land never was. It needs one: baked, eroded, strike-oriented relief, lit at its own
   scale. Section 4, plan B.

2. **The frame is heavy because the whole planet is recomputed per pixel per frame, and ~95 %
   of that is a pure function of (keyframe, uv).** A land pixel evaluates on the order of
   290 noise lookups (580 lattice fetches) and 31 field reads; the project's own numbers are
   72 ms per frame at 2560×1440 on an M1 and 335 ms (3 fps) at a 5K display, against a
   noise-free floor of 28.7 ms that alone rules out smooth playback at native resolution. The
   hillshade sun is a fixed cartographic azimuth in the local frame, so the shaded world can be
   computed **once per keyframe** and looked up, with only the water surface, terminator,
   clouds and close-zoom detail left live. That removes the pixel wall, most of the 950 MB
   residency budget, and most of the decode churn. Section 4, plan A.

3. **Ambient is the same renderer with the chrome hidden.** It plays at 18 Myr/s (a keyframe
   crossing and ten image decodes every 0.28 s) through the full shader at device pixel
   ratio 2. No tuning of that mode gets it to "background". A separate ~300-line page over
   pre-baked world sheets (about 50 MB for the whole timeline at 2048×1024) runs at 60 fps at
   a few per cent of a laptop GPU and works as a tab, a screensaver or a wallpaper.
   Section 4, plan C.

4. **Two things found on the way that should be fixed regardless.** The foreland-flexure
   field sinks the Gangetic plain below sea level (Patna −54 m, Guwahati −24 m, Dhaka −21 m in
   the shader's base elevation; 0.76 % of present-day land), so the whole Himalayan front is
   drawn as a shallow sea. And the repo carries 152 MB of deploy assets in history, 624 Finder
   conflict copies in `site/`, and a stale copy of the shader in `web/shaders/` that is 500
   lines behind the one that ships. Section 2.4 and plan D.

Recommended order: **D1 and B1 in the first week** (small, visible), **plan A next** (it is the
foundation for everything else and turns mountain work into a one-minute re-bake loop),
**plan C on top of A** (nearly free once A exists), **plan B** as the long pole.

---

## 1. Method and caveats

- Read in full: `README.md`, `HANDOFF.md`, `Deep Research/MODEL-GAPS.md` (7,179 lines), the
  WP-08 and WP-09 reports, `web/index.html` (8,765 lines, of which the fragment shader is
  3,821), the bakers for every field kind, and the audit and verification harness.
- The shader read here is the **live** one, extracted from `index.html`. The copies in
  `web/shaders/` are stale (3,313 lines against 3,821) and must not be read as the shader.
- Renders were taken headless in this review environment with the app's own
  `APP.lookAt`/`APP.snap` harness on SwiftShader (software GL). They are pixel-faithful and
  useless for timing, so every performance number below is the project's own measurement on
  the user's M1, cited from WP-09 and MODEL-GAPS section P.
- Field measurements decode the shipped `docs/fields` textures exactly as the shader does.

---

## 2. Findings

### 2.1 Where the frame goes

**Architecture.** One fragment shader draws the globe and the map. Per fragment it decodes and
interpolates ten field kinds, recomputes temperature, relief, biome, water, ice, and the
ocean fabric, and shades the result. Static profile of the live shader:

| | count |
|---|---|
| lines | 3,821 |
| value-noise call sites (`vnoise3`) | 78 |
| five-octave fBm call sites (`fbm3`) | 49 |
| field texture reads (`texture2D`) | 39 |
| noise lookups per fragment, upper bound with every gate open | ~410 (820 lattice fetches) |
| of which on the land path | ~290 |
| of which the two-fractal height detail, run 5× (centre + 4 gradient taps) | 100 |
| of which the rainfall lookup's warp alone | 20 (4 × fBm) |
| clouds, per cloud fragment | 20 more octaves |

**Measured cost (the project's own numbers, M1, Chrome, ANGLE Metal).**

| scene | ms / frame |
|---|---|
| 2560×1440, globe, harness framing | 72 (233 real-GPU headless) |
| 2560×1440, globe filling the frame | 110 |
| 5K native, the user's display | 335 (3 fps) |
| the same scene with every noise call removed | 28.7 at 3.7 MP → ~110 at 14.7 MP |

So the picture is fragment-bound, ~80 % of it is noise, and even a noise-free shader cannot
reach 10 fps at native 5K. The quality governor's only lever is to render at DPR 1.0, which
is why "Auto" reads as blurry on a Retina laptop.

**What actually depends on the camera.** Almost nothing. The hillshade sun is a fixed
azimuth in the local east/north frame (`Lh = (-0.55, 0.55)`, rotated into a world-fixed frame
near the poles) — the cartographic convention, and exactly bakeable. The terms that do depend
on the view are the pixel-footprint fades (`sfoot`, `gFineFade`, the fabric's own fade), the
day/night terminator (view-space), the sea-surface sheen (`uTime`), the cloud shell, the
atmosphere, and the two close-zoom grain octaves. Everything else is a pure function of the
keyframe pair, `mixf`, and `uv`. That is the fact plan A stands on.

**RAM.** Decoded bitmap plus GPU copy are accounted at 8 bytes per pixel per kind; a bound
pair is ~300 MB; the residency budget is 950 MB on desktop (360 MB floor). The project's own
five-minute soak measured 325–344 MB pinned at the earlier 700 MB budget, 58–79 MB of JS heap,
and ~200 MB in the GPU process. On top of that the prefetch pump warms all 138 MB of fields
into the browser cache on every visit, including on battery and on hidden tabs.

**CPU.** Playback at the default 18 Myr/s crosses a keyframe every 0.28 s, and a crossing
decodes up to ten files (the 4096×2048 elevation AVIF at 30–70 ms each). That is roughly a
core, continuously, before the GPU starts, and it is exactly what Ambient runs forever. A
second CPU cost is invisible in the profile: `dt` is clamped at 50 ms, so at 3 fps the
"18 Myr/s" slider advances 2.7 Myr/s, unevenly — pace is a function of frame rate.

**Minor.** MSAA plus DPR 2 is four times the fragments of a 1× buffer for a picture that is
already shaded per pixel. The 1024×512 displaced sphere is not a cost.

### 2.2 Why the mountains look the way they do

Follow one land pixel through the pipeline:

1. The shipped elevation is 9.8 km per texel, which matches the 6′ PaleoDEM source. There is
   no finer data anywhere in the pipeline (WP-08 finding 0; iteration 62).
2. The relief that lights the *data* is a central difference over ±23.5 km. As a filter that
   stencil peaks at a 94 km wavelength and is identically zero at 47 km. Ridge-and-valley
   lives at 10–30 km, inside the null. This is the whole of "prisms": a range is lit as one
   smooth swell however much structure the height field carries (iteration 62 measured a
   900 m corrugation baked into the field moving the render by 1.7/255).
3. Everything finer than that is synthesised, by three constructions — and the shader
   describes their scales in two unit conventions a factor of 2π apart. A value-noise call
   `vnoise3(p*K)` on the unit sphere has a lattice cell of 6371/K km (the shader's own "24 km
   octave" for K = 260 uses this); a sine `sin(K·s)` has a period of 2π·6371/K km. The
   mountain code applies the second formula to noise and the first to sines, so every
   wavelength it names for the fold fabric is wrong by 2π:
   - **`detail3`, in the height**: five-octave *ridged* fBm with base cells of 24 km and
     91 km (octaves 24 / 12 / 6 / 3 / 1.3 km and 91 / 44 / 21 / 10 / 5 km), blended in by
     slope, with the sampling domain compressed along the fold axis. So relief in the 5–30 km
     band *does* exist in the height, at tens to a couple of hundred metres — what the stencil
     cannot light, and what remains is the
     ridged transform `(1-|2n-1|)²` with octave gating, which produces wormy crest lines by
     construction; compressing the domain only makes longer worms. This is most of "squiggly".
   - **The tone band**: `sin²(π·fBm)` multiplied into the albedo, documented as "~26 km, the
     real spacing of ridges in the Zagros" and "~83 km". The noise cells are 6371/1520 =
     4.2 km and 13 km, so the dominant wavelengths (about two cells) are **8 km and 27 km**,
     three times finer than documented. Measured (§5), 78 % of what this term adds is a
     broad *brightening* of the whole belt — `sin²` of a noise centred on 0.5 averages 0.85,
     not 0.5 — and the rest is texture at 8–27 km. A sine of a smooth field draws the
     *contour lines* of that field, wandering loops; README §7.5 names this construction's
     failure mode on the sea floor ("marbling — concentric loops") and retired it there.
   - **The normal grating**: `sin(across-strike coordinate × 246 + noise)` and `× 470`,
     documented as 26 km and 13.6 km. A sine's period is 2π/246 rad = **163 km** and 2π/470
     rad = **85 km**. Measured (§5), the energy this term adds rises monotonically toward long
     wavelengths and has no peak anywhere near 10–30 km. That is why iteration 62 found its
     gain "at WIDE zoom" and none up close: it never drew ridge-and-valley, it drew a handful
     of broad, phase-jittered stripes across each belt — the "uniform" look. It also builds the
     across-strike axis from the unrotated local frame (`Eax`, `Nax`) and dots it with the
     plate-rotated position, so outside the present day the stripes run in a direction that
     mixes two frames.
4. The gates: the tone band fires only above 1,100–2,500 m and the grating above 900–2,400 m,
   both also gated on `rug` and on shortening. Deep-time belts are genuinely low (0.7 % of land
   above 2.5 km at 300 Ma against 3.4 % today), so Pangaea's ranges get none of it and render
   as smooth prisms; iteration 57 measured this and accepted it. On flat ground the detail is
   faded by 70 %, and mid-elevation ground carries isotropic mottle. That is "flat / uniform".
5. The ceiling: `audit_texture.py` measures organisation against Blue Marble. Iteration 75
   reached 60 % by *removing* isotropic noise from flat ground; iterations 76–77 tried five
   ways of orienting noise (domain stretch, line-integral convolution, added and substituted,
   off local and regional slope) and every one scored at or below baseline. The register's
   own conclusion: organisation "will have to be BAKED … not grown per pixel". That is right.
   The half it stops short of is that a baked *direction* is not enough either — the sea floor
   works because `licGrad` has a physical direction *and* the relief it draws is simple
   (parallel hills). Mountains are not simple: they are drainage networks. What has to be
   baked is the relief itself.

Renders taken for this review, with the three constructions switched off one at a time, are
in §5, with the scale of each one's contribution measured from the difference image rather
than read off its comment. Each moves a Himalaya frame at continental zoom by 3–5/255, all
three together by 8.5/255, and switching them off *raises* structure-tensor coherence from
0.390 to 0.426: the machinery built to draw ridges adds texture and subtracts organisation.
The brushed streaking on Tibet survives all three being off. It is the *combing* itself —
the fold-axis compression of the height detail's sampling domain (release 2.2, "mountain
ranges start to comb"): switching only that compression off removes the streaks and leaves
coherence exactly where it was (0.389 against 0.390), which says the comb adds streaks and no
organisation. Switching every normal perturbation off (grain, grating, drainage carve) moves
the frame by 7.9/255 and raises coherence to 0.415. There is no mountain model underneath
any of it to reveal.

### 2.3 Ambient

`enterAmbient()` hides the chrome, sets `playing = true`, and adds a fixed 0.12 rad/s spin.
Nothing else changes: same shader, same DPR, same 950 MB residency, same prefetch, same decode
storm every 0.28 s. It is the app's *heaviest* state, not its lightest. A background mode
wants the opposite of what the app is optimised for: one wide framing, slow time, no
interaction — which is the ideal case for a pre-computed sequence, and the worst case for
per-pixel synthesis.

### 2.4 Defects noticed on the way

- **The foreland moat floods real plains.** `elevDetail` subtracts the flexural moat
  (`_f`, up to 620 m) from the base elevation wherever the ground is below ~1,500 m, and the
  water test runs on the result. Measured on the shipped fields at 0 Ma:

  | site | field elevation | moat | shader base | result |
  |---|---|---|---|---|
  | Ganges plain, Lucknow | 157 m | 102 m | +55 m | land |
  | Ganges plain, Patna | 73 m | 126 m | **−54 m** | sea |
  | Brahmaputra, Guwahati | 124 m | 148 m | **−24 m** | sea |
  | Ganges delta, Dhaka | 44 m | 66 m | **−21 m** | sea |
  | Po plain | 48 m | 24 m | +23 m | land |
  | Kansas (control) | 528 m | 5 m | +523 m | land |

  0.76 % of present-day land is pushed below sea level. On screen it is a pale-blue band the
  length of the Himalayan front (§5, first frame). The shader's own comment says a foreland
  "is a sediment basin … a low PLAIN and not a hole"; the elevation should not carry the moat
  where the plain is filled. `audit_foreland.py` only gates hypsometry above 1 km, so it
  cannot see this.
- **`web/shaders/*.glsl` is stale** — 3,313 lines against the 3,821 that ship. Nothing in
  `build/` writes it. Anyone reviewing "the shader" from those files reviews an old one.
- **`site/` is 624 Finder conflict copies** ("`fut_0005_e 2.webp`"), 13 MB, tracked in git —
  the exact files the `.gitignore` comment describes as deploy bloat.
- **`docs/fields` (138 MB, 2,460 files) is tracked.** Every reskin writes ~140 MB of new
  blobs into history; the shallow 50-commit clone is already a 285 MB pack. Pages needs the
  files served, not versioned.
- **README §3** still says six field kinds and 1,506 textures; there are ten and 2,460.
- **Pace depends on frame rate** (the 50 ms `dt` clamp), see §2.1.

---

## 3. Goals

| | goal | how it is measured |
|---|---|---|
| **G1** | **Mountains read as landform.** Organised ridge-and-valley at 5–30 km from a model; strike-oriented; welded to the crust; consistent across zoom; present in deep time in proportion to each age's own relief. | `audit_texture.py` organisation in orogens ≥ 85 % of Blue Marble (60 % today); structure-tensor coherence in belts ≥ 0.35 at close, mid and wide zoom (0.48 / 0.22 / 0.27 today); 5–30 km band energy at or above the reference; a squiggle detector (ridge-line tortuosity and closed-loop count) near the reference's; 300 Ma belts non-flat. |
| **G2** | **A frame costs what changes in it.** The world is computed once per keyframe and looked up per frame; the live per-pixel path runs only at close zoom. | ≤ 8 ms/frame on the M1 at DPR 2 at wide and medium zoom; steady residency ≤ 300 MB; ≤ 2 decodes per keyframe crossing; playback pace independent of frame rate; the existing storm gate stays at 0. |
| **G3** | **A real background build.** A separate lite page over pre-baked sheets. | 60 fps at ≤ 5 % GPU on a MacBook Air; ≤ 120 MB RAM; ≤ 60 MB total download, fetched lazily; runs as a tab, a screensaver and a wallpaper; no dependency on the 138 MB field set. |
| **G4** | **A repo that says what it ships.** | Plains dry; shader copies generated, not hand-kept; no junk tracked; large assets out of history; `index.html` split with a no-build deploy preserved; README numbers true. |
| **G5** | **Fewer, structural rounds.** | Every round starts from a known-answer pair; no further per-pixel noise tuning on land. |

---

## 4. Plans

### Plan A — bake per keyframe, look up per frame (G2; foundation for B and C)

**A1. An equirect render mode in the existing shader.** Add a third projection (`uProj = 2`)
in which the fragment's `uv` is the equirectangular coordinate directly, and render a
full-screen quad into a WebGL2 render target (the app already compiles under WebGL2).
Output two attachments: the **lit colour** (land and sea-floor shading complete, hillshade
included; no water-surface effects, no terminator, no clouds) and an **aux** attachment
carrying the detail height (16-bit split), the ice mask and the wet mask. In this mode
`sfoot` is a uniform (the bake footprint) instead of `fwidth`. This is a few dozen lines: the
shader already runs the map through the same body with a different `uv`.

**A2. World sheets per keyframe.** Bake at `mixf = 0` for each keyframe, so a sheet is a
cacheable, shippable object. The display shader (~150 lines) then samples sheet A and
sheet B through the existing displacement warp (`_v`), blends by `mixf`, takes height from
`_e` exactly as now so **the coastline still migrates by interpolation** rather than by a
dissolve, and adds water colour, sheen, terminator and atmosphere on top. Climate uniforms
become per-keyframe (a dissolve across the interval), which is the one visible change and is
invisible at playback speed.

**A3. Two sources for sheets.**
- *In-browser, on demand*: ~250 ms per keyframe at 4096×2048 on the M1 (one 8.4 MP pass of
  the current shader), baked one keyframe ahead in the playback direction, two or three
  resident. Enough for interactive use.
- *Offline, shipped*: headless Chrome through the existing `_verify.html` harness renders all
  251 keyframes in about a minute of GPU time; encode to AVIF. Calibrated on the app's own
  JPEGs (85–150 KB/MP): **2048×1024 ≈ 150–250 KB each, 40–60 MB for the timeline** —
  the lite build's whole dataset — and 4096×2048 ≈ 1 MB each, ~250 MB, optional for the
  main app's medium zoom. A shader change costs a one-minute re-bake, which is also the
  fastest mountain-iteration loop this project has ever had.

**A4. Level of detail.** Use the baked path whenever the pixel footprint is at or above a
sheet texel, and the live per-pixel path only below ~2 km/px (zoom under ~1.8), with a
cross-fade band between them. Most sessions, and every Ambient session, never leave the
baked path.

**A5. Hygiene wins independent of the bake** (each a day or less):
1. advance age by wall-clock time, and clamp only what needs clamping;
2. branch around noise whose fade weight is zero instead of evaluating and multiplying;
3. MSAA off for the terrain pass (overlay lines get their own anti-aliasing);
4. bake the rainfall lookup's 20-octave warp into `_r` offline;
5. do not warm 138 MB per visit on battery, metered connections, or hidden tabs
   (`navigator.getBattery`, `connection.saveData`, `document.hidden`);
6. stop re-rendering when nothing changed (paused, not dragging, no clock-driven effect on
   screen) — today `requestAnimationFrame` redraws the full planet regardless.

**Expected end state.** Wide and medium zoom at 2–8 ms per frame; residency 150–250 MB; one
sheet plus `_e` and `_v` per crossing. **Cost and risk.** A new asset class (the sheets);
a reframing of the README's "nothing is a pre-rendered picture of an era" — the model still
produces every pixel, it runs per keyframe instead of per frame, and the coastline still
interpolates. I would take that trade; at wide zoom a 9.8 km bake is *more* faithful than
per-pixel synthesis that aliases into the pixel.

### Plan B — a mountain model (G1)

**B1. Remove the squiggle generators (one day).** Retire the `sin²(fBm)` tone band, the
163/85 km normal grating and the ridged transform inside orogens (each measured as a net
loss of organisation, §5), and fix the 2π unit convention wherever a scale is named. This makes the ranges smoother, not better — it removes
the wrong answer so the right one can be seen against a clean baseline.

**B2. Build an orogen atlas offline (one to two weeks).** A small library of tileable relief
patches — eight to sixteen at 512×512, ~500 m per texel, ~250 km across — produced by a real
erosion simulator (stream-power incision with hillslope diffusion, the standard
FastScape-style implicit solver, ~200 lines of numpy) run with **anisotropic uplift**: fold
stripes at 8–25 km spacing for belts, plus a few dissected-plateau and dissected-lowland
patches. Erosion gives what noise cannot: connected dendritic valleys, sharp divides,
ridges that run, intermontane basins. Ship height + normal, 2–4 MB total.

**B3. Consume it in the shader — in both the bake and the live path (one week).** Sample the
atlas in the crust-fixed frame (`matDir`), rotated to the fold axis from `_t`, scaled by
relief relative to the age's own hypsometry (`topo_fabric` already computes that), with two
or three rotated samples blended to hide tiling. Add it to the **height**, so snow lines,
bare rock, coasts and treelines all see it, and derive the normal from the detailed height at
the bake texel — no 47 km blind spot. Three to six texture fetches replace ~60 noise
lookups.

**B4. Deep time.** Drop the absolute 1,100–2,500 m bars in favour of the age-relative gate
everywhere; scale amplitude by local relief so the hypsometry gates (`audit_foreland` style)
keep holding: the PaleoDEM stays authoritative for where a range is and how high (WP-08
finding 0).

**B5. Plains (the other half of the 40 % gap).** Bake a drainage-azimuth field from
`build_surface.py`'s D8 receivers — the register's own recommendation — and steer a
dissected-lowland patch by it; erg lineation from the wind-fetch channel.

**B6. Gates.** `audit_texture.py` organisation (target ≥ 85 %), coherence at three zooms,
5–30 km band energy, a tortuosity/closed-loop check, plus the known-answer-pair rule from
iterations 152–153 before any number is read.

### Plan C — the lite / Ambient build (G3)

**C1. `ambient.html`, ~300 lines.** Raw WebGL or three.js; loads the two 2048×1024 sheets
around the current age plus a 128×64 `_v`; shader: warp + blend, terminator, atmosphere rim,
optional slow cloud sheet from `_r`; 30 fps cap; `document.hidden` and
`prefers-reduced-motion` respected; sheets fetched two ahead. Time at 1–3 Myr/s (one
150 KB decode every few seconds). RAM ~80–120 MB, GPU trivial.

**C2. Packaging.** (a) `/ambient/` on the Pages site — free once C1 exists. (b) macOS
screensaver via WebViewScreenSaver, which shows a URL. (c) Wallpaper via Plash (macOS) or
Lively (Windows). (d) Optional Tauri app bundling the sheets for offline. Ship (a) and (b);
they need no packaging work at all.

**C3.** Point the main app's Ambient button at this page.

### Plan D — hygiene (G4)

- **D1** Fix the moat: apply it to substrate and relief amplitude, and never let it take the
  base elevation below `min(z, +30 m)` where the ground is dry in the field; re-run
  `audit_foreland` with a below-sea-level count added.
- **D2** Make `check_shader.py` write `web/shaders/*.glsl` from `index.html`, or delete them.
- **D3** Delete `site/`; add a pre-commit check for the `* [0-9].*` pattern.
- **D4** Move `docs/fields` (and the sheets) to release assets or an object store, addressed
  by a `FIELD_BASE` URL; keep the manifest in git; rewrite or leave history as the user
  prefers.
- **D5** Split `index.html` into `app.js`, `style.css` and `shaders/*.glsl`, concatenated by
  `build_site.py`; the deployed page stays a single static file.
- **D6** README §3 and §4 to the ten-kind reality.

### Sequencing and effort

| week | work | outcome on screen |
|---|---|---|
| 1 | D1–D3, A5, B1 | plains dry; no squiggles; pace correct; fewer redraws |
| 2–3 | A1–A4 | wide/medium zoom at a few ms; RAM down by ~3×; storm gate still 0 |
| 3–4 | C1–C2 | a real background build, screensaver-capable |
| 4–7 | B2–B4 | ranges with valleys and ridges that run, in every era |
| later | B5, D4–D5 | plains organised; repo slim |

Estimates assume one person and the project's existing harness; the erosion simulator is the
only genuinely new machinery.

---

## 5. Evidence: renders and A/B

Frames are in `Deep Research/research reports/wp10/`, rendered with the app's own
`APP.lookAt` / `APP.snap` harness at 960×600 on SwiftShader (pixel-faithful, not
timing-faithful). Zoom is camera distance in Earth radii: 1.35 is as close as the UI goes,
5 the whole globe; a 600-px-tall frame at zoom 1.6 is about 4.4 km per pixel.

| frame | what it shows |
|---|---|
| `himalaya_z16` | Tibet and the Himalaya as brushed metal, no valley network; the pale-blue band along the whole range front is the foreland moat drawing the Gangetic plain as a shallow sea |
| `himalaya_z30` | the whole globe from over India: one bright prism with a sheen; the flooded plain visible even here |
| `andes_z20` | a strike-carrying belt (0.53 shortening, 0.997 axis strength) that still reads as one smooth brown prism; the modelled sea floor beside it shows fracture zones and fabric |
| `pangaea300_z26` | the central Pangaean belt at 300 Ma as one long smooth swell |
| `globe_ambient` | the Ambient framing at 150 Ma: every pixel through the full shader every frame |

**Switching the three constructions off one at a time**, Himalaya at zoom 1.6, one-line
shader variants (`notone_`, `nocorr_`, `noridge_`, `plain_` frames):

| variant | band-pass σ (4–24 px) | coherence | mean \|Δ\| vs shipped, /255 |
|---|---|---|---|
| shipped | 16.76 | 0.390 | — |
| tone band off | 16.24 | 0.395 | 2.92 |
| normal grating off | 16.59 | 0.392 | 4.39 |
| ridged transform off | 16.74 | **0.416** | 5.31 |
| all three off | 16.08 | **0.426** | 8.53 |
| fold-axis compression off (`nofold_`) | 17.33 | 0.389 | 4.38 |
| every normal perturbation off (`nograin_`) | 16.31 | **0.415** | 7.89 |

Where each term's energy sits, from the difference image (energy density per unit
log-wavelength, %; the documented scales were 26 / 13.6 km for the grating and 26 / 83 km for
the tone band):

| band, km | 5–10 | 10–16 | 16–22 | 22–32 | 32–50 | 50–70 | 70–100 | 100–140 | 140–190 | 190–300 | >300 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tone band | 13 | 22 | 15 | 12 | 10 | 9 | 7 | 7 | 6 | 5 | **78** |
| normal grating | 14 | 23 | 16 | 15 | 16 | 18 | 21 | 24 | **29** | **30** | 26 |
| ridged transform | 34 | **57** | 38 | 31 | 24 | 16 | 11 | 7 | 5 | 2 | 2 |
| fold-axis compression | 30 | **54** | 39 | 35 | 25 | 18 | 13 | 8 | 5 | 3 | 1 |
| every normal perturbation | 14 | 24 | 17 | 17 | 17 | 20 | 25 | 26 | 27 | 24 | 24 |

Reading: the ridged transform and the fold compression are the two terms that live in the
ridge-and-valley band, and between them they are the worms and the streaks — removing the
first raises coherence, removing the second leaves it untouched. The tone band is mostly a
flat brightening. The grating's energy rises toward 150–300 km and has no peak near 26 or
13.6 km, which is the 2π error made visible.

---

## 6. Where I disagree with the standing rules

- **"No reduction of richness, detail or functionality"** (section P's constraint) is right
  as a rule about *what the model computes* and wrong as a rule about *when*. At wide zoom
  the picture is limited by pixels, not by richness, and per-pixel synthesis that aliases is
  a reduction in fidelity, not an increase.
- **"Nothing is a pre-rendered picture of an era"** (README §1) should be kept for the
  coastline (interpolated height, plan A2 preserves it) and dropped for shading. Google Earth
  is tiles; that is not what makes it a slideshow.
- **The iteration cadence.** 154 logged iterations in six weeks, a large share reverted, and
  the ones that moved the picture were all structural (crustal age, the catalogue, the codec,
  the displacement warp). The mountain register (51–57, 62, 66, 75–77) is the same story
  told six more times. Plan B is the structural version; I would not spend another round on
  per-pixel land noise.
