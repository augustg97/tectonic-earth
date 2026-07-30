# WP-09 — Performance audit: where the frames go (2026-07-30)

**The user's report:** "the model often lags, or is slow to render when jumping across the
timeline, and the frame rate seems a bit jagged." Constraint on every remedy: **no reduction
of richness, detail, functionality or information.** Every proposed fix is either
output-identical (same pixels) or output-invisible (same look, verified by A/B).

## Method

Measured live on the user's own machine (Apple M1, ANGLE Metal, Chrome), app served from
localhost via `build/serve.py`. The in-app Browser pane never fires rAF
(`document.hidden === true`), so frames were driven by hand with `APP.step()` and GPU time
was taken as wall time of `render + readPixels(1px)` (forced pipeline completion). The
canvas was forced to 2560×1440 (`setPixelRatio(2); setSize(1280,720)`) because the pane's
layout viewport is 0×0 after navigation.

Shader cost was attributed with a **variant build** — a copy of index.html with
URL-switchable kill-switches injected into the GLSL template literal (`${PERF.has(...)}`
interpolations; the file is a plain template literal, so this needs no build step):

- `?nodetail` — `detail3()` returns 0 (kills the 2×5-octave elevation detail everywhere)
- `?nonoise` — `vnoise3()` returns 0.5 (kills ALL hash noise in the terrain FRAG)
- `?basegrad` — the 4-tap hillshade gradient samples `baseElev` instead of full `elevAt`
- `?noaa` / `?nopdb` — `antialias:false` / `preserveDrawingBuffer:false`

Main-thread costs were attributed by wrapping `texSubImage2D`/`texStorage2D`/`texImage2D`
on the live GL context and timing `APP.step()` across forced keyframe crossings and jumps.
Live-network numbers came from `performance.getEntriesByType('resource')` on the deployed
site in real Chrome.

**Caveat on absolute numbers.** The measuring context is an occluded window; Metal may
deprioritise it, and forced completion serialises a pipeline that normally overlaps. Treat
the absolute milliseconds as an upper bound and the *ratios* as solid — they reproduce
within ~2% run-to-run and scale correctly with pixel count (72 ms at a 26%-smaller globe vs
110 ms full-cover, 40.8 ms at DPR 1).

## Findings — GPU (the steady frame)

All at 2560×1440, globe view, age 1000, p50 of 9–20 forced-completion frames:

| configuration | p50 ms | delta vs baseline |
|---|---|---|
| full frame (baseline harness) | **72.0** | — |
| `?basegrad` (hillshade gradient on base field only) | 57.8 | **−14.2 — the 4 `elevAt` taps** |
| `?nodetail` (no `detail3` anywhere) | 56.0 | −16.0 — the whole elevation-detail stack |
| `?nonoise` (no `vnoise3` anywhere) | **14.4** | **−57.6 — ALL hash noise: 80% of the frame** |
| `?noaa&nopdb` | 57.3 | −14.7 — MSAA resolve + preserve copy |
| clouds hidden (earlier session, vs 110 baseline) | −10.5 | the CFRAG shell |
| background only (globe hidden) | 5.6 | stars + readback overhead |

**F1. The frame is fragment-bound, and ~80% of it is procedural hash noise.** The terrain
FRAG has 68 noise call sites; `vnoise3` is 8 `sin`-hash corner evaluations + a trilinear
mix, `fbm3` is 5 of those, `detail3` is a 10-octave double walk, and the hillshade normal
re-runs the full `elevAt` stack at 4 offsets (F2). The clouds' `cfb` is another 20 octaves
per fragment of the same construction. At DPR 2 on a 7.3 MP fullscreen canvas this lands at
an estimated 140–220 ms/frame worst case — single-digit FPS when the globe fills the
window, which is the reported "lag" and "jagged".

**F2. The hillshade gradient pays the detail stack four extra times.** `gE/gN` at
`index.html:2177` difference full `elevAt` (base + `elevDetail` = 2× `detail3`) at ±23.5 km
— yet octaves finer than the baseline mostly cancel across it (H7's finding). The shader
already knows this trick: the 8-tap deep-water ring deliberately samples `baseElev` for
exactly this reason (comment at rel. line ~2258, "forty extra noise evaluations per
fragment, measured at 11.5 ms"). The main gradient never got the same treatment. Fixing it
structurally belongs to H7 (shade detail at its own scale); cheaply, the noise LUT (P4)
cuts its cost with zero output change.

**F3. MSAA + preserveDrawingBuffer cost ~15 ms (~20%).** `preserveDrawingBuffer:false` is
pixel-identical and free — it only requires `APP.shoot()` to render once before reading.
MSAA-off is NOT automatically acceptable: it changes silhouette and overlay-line quality;
decide by screenshot A/B (P5).

## Findings — main thread (the hitches)

Steady-state JS per frame is **~1 ms** (labels, cards, readout, camera all fine — not the
problem). The hitches are texture residency:

| event | stall | of which decode+upload |
|---|---|---|
| keyframe crossing during playback | **152.7 ms** | 122.2 ms, 18 textures |
| scrub straight BACK over the same boundary | **101.1 ms** | 18 textures again — already evicted |
| far jump (all files already local) | 164–263 ms | ~210 ms; the two 4096×2048 `_e` AVIFs alone are 72.7+39.1 ms |
| far jump on the live site, unprefetched age | + network | field fetch p50 **296 ms**, p95 **580 ms** (h2, real connection) |

**F4. Decode and upload happen synchronously at first bind, on the render path.**
`loadField` stores a raw `HTMLImageElement`; nothing ever decodes it until the first
`renderer.render()` that binds it, where Chrome pays AVIF/WebP decode + `texSubImage2D`
upload inside one frame. An 8.4 MP AVIF is ~40–75 ms; a crossing binds ~10 new files and a
jump ~15–18.

**F5. `TEX_CAP=24` was sized for 6 field kinds; there are now 10.** A bound pair holds
15–18 textures, so the cache fits ~1.3 keyframes: the previous keyframe is evicted by the
time playback crosses the next boundary, and scrubbing back replays the whole storm. (This
exact trap was recorded in the terrain-motion memory — "adding two kinds makes 24 slots
barely three keyframes… raise it" — and the raise never happened.)

**F6. Playback at default speed crosses a boundary every fraction of a second**, so F4+F5
inject a ~150 ms stall at that cadence on top of the F1 frame cost: that is the "jagged"
texture of the lag, distinct from the low average rate.

**F7. Jumps additionally rebuild overlays** (`buildBoundaries`+`buildHotspots`+
`buildVectors` in `jumpTo`, plus the crossing rebuild in `loop()`): the ~50 ms non-texture
tail of a jump. Secondary but same-frame.

**F8. What is already right and should not be touched:** the 12-file boot splash; the
re-aiming 4-wide prefetch pump; per-kind uniform gates (`uWarp/uMat/uTect/uFore`) that make
partial binds safe — these are the bones the fixes below stand on. Boot is fast; the pump
fills 127 MB in background correctly.

## The plan is MODEL-GAPS section P

P1–P9 there, sequenced. Expected end state, honestly stated: crossings and scrub-back
~free (from ~150/~100 ms), local jumps <70 ms (from ~260), live jumps network-bound with a
progressive first correct frame in ~1 fetch RTT, steady GPU frame cut ~2.5–3× (LUT factor
to be measured, not promised — the 80% noise share is an upper bound on what it can win,
since `?nonoise` also collapses branches the LUT must keep). Fullscreen locked-60 on M1 is
NOT promised; P4b (bake whole static-domain noise sums into equirect textures) is the
documented extension if P4 alone does not reach it.

**Explicitly not proposed**, per the constraint: resolution/DPR reduction, octave cuts,
cloud/atmosphere simplification, MSAA-off-by-default without the screenshot verdict, or any
change to what is drawn. An interaction-time dynamic-resolution floor was considered and
left out — it trades transient sharpness, which is the user's call, not an audit's.

## Reproduction

- Variant build: the Python snippet in this session's transcript (5 replacements on a copy
  of `web/index.html`; each asserts `count==1` so drift fails loudly).
- Probe: force canvas size, warm 6 steps, then p50 of 9–11 × (`APP.step()` +
  `readPixels(1px)`).
- Crossing storm: wrap `texSubImage2D` on `Object.getPrototypeOf(gl)`, set
  `state.age` across a boundary, time one `APP.step()`.
- The two prior GPU baselines to beat: **110.2 ms** (full-cover globe) / **72.0 ms**
  (harness framing), and **14.4 ms** as the measured noise-free floor of the same scene.

## Addendum — implemented and deployed, 2026-07-30 (same day)

The plan shipped the same day; the measured results, the two rejected-for-now levers
(gradient-on-base, whose pinned A/B moved 28–35% of land pixels; the R8 lattice, whose
quantisation measurably softened ridged crests before the R16F upgrade restored parity), and
the honest headline live in **MODEL-GAPS "P — IMPLEMENTED"**. Key numbers: crossings
152.7 → 1–9 ms warm (0 synchronous uploads, now gated by `build/audit_perf.py` in
`build_site.py`); scrub-back 101 → 7–9 ms; far jumps 164–263 → 44–99 ms first frame with
background refinement; overlay leak +93 geometries/crossing → 0; steady GPU frame −6%
(LUT16) against a measured 28.7 ms noise-free floor that defines the next round.

Instrumentation that outlived the audit: `web/_verify.html` (headless driver: shots /
timing / storm / pin), `?perf=1` HUD, `?oldnoise` A/B switch. The Browser pane proved
untrustworthy for timing (hidden-tab rAF + intensive timer throttling + occluded-GPU
scheduling); headless Chrome `--headless=new` runs the real ANGLE Metal GPU and is the
reliable lab.
