# The no-regression protocol

**2026-07-26.** Answering a direct question: *when we say a change will look like a
regression, can we avoid or account for it — can the implementation maintain and not
reduce the accuracy of each frame?*

**Yes, substantially — and where it cannot, the residue can be made small, named and
justified rather than merely accepted.** This document is the mechanism.

---

## 1. Why "it will look like a regression" was the wrong thing to say

The old pipeline carried **two errors that partly cancelled**:

| | |
|---|---|
| (a) | Merdith's absolute frame is not Scotese's — they disagree about longitude by ~9° at 90 Ma and ~40° in the Ordovician |
| (b) | `frame_offset.py` applies a single **rigid global** correction per age |

Where (b) happened to match the local regional offset, a feature landed correctly **by
cancellation, not by being right**. Remove both errors and that feature moves. That is not
a regression; it is the removal of a compensating error, and keeping it would mean keeping
a bug because it flattered one label.

WP-05 confirms the shape of this independently: measured against Deep Time Maps (Blakey —
a genuinely independent reconstruction), our Palaeozoic disagreement is **almost entirely a
single longitude number per age**, exactly what the longitude problem predicts. At 420 Ma
the raw overlap is worse than chance (kappa −0.04) and recovers to 0.47 under a rigid
rotation, while the **latitude profiles agree throughout** (RMS 6.7–9.5%, correlation
0.87–0.97 across 400–525 Ma). Latitude is measured; longitude is chosen. The frame switch
is a change to the chosen half.

## 2. The gate: `modeling/regression_gate.py`

Read-only. It scores **every feature the build actually plate-tracks**, on its own age
window, under both frames, against the shipped elevation field — and reports the *individual*
outcome, not the average.

It mirrors the build's real tracking rules (`build_webdata.py:1125`): ocean labels are
excluded because they take the `COMPOSITE_WATER` / `nearest_water` path, and so are
deep-Precambrian labels, sub-5 Myr windows and coordinates not on land today. Getting this
wrong invents regressions that cannot happen — the first run scored 26 regressions, five of
which were ocean labels the build never tracks this way.

**Current result for the frame switch:**

| | |
|---|---|
| features scored | **158** |
| improved | **58** |
| unchanged | **79** |
| regressed | **21** |
| mean score | **0.746 → 0.833** |

Regressions by cause:

| class | n | meaning |
|---|---|---|
| **PRE-EXISTING** | 8 | bad in *both* frames. The switch revealed it; it did not cause it. Fix the feature. |
| **DEM-LIMITED** | 3 | the target medium is not resolvable at 20 km. No frame fixes this — see `epeiric.py`. |
| **CANCELLATION** | 3 | small drop from a position the rigid correction happened to suit. |
| **TRUE** | **7** | the only class that should block anything. |

**So the honest count is 7 features out of 158, not "everything moves".**

## 3. The seven, diagnosed

Inspected individually rather than left as a number:

| feature | old → new | what is actually happening |
|---|---|---|
| **Gulf of California** | 0.50 → 0.00 | **Not a frame effect at all.** At 0 Ma both frames give the *identical* position and both read −1305 m. It is a `rift` label whose coordinate is in water; it can never satisfy a land test. **Mis-typed or mis-placed data.** |
| **Red Sea Rift** | 0.67 → 0.00 | Same class: authored inside the Red Sea, which is water today. It should not have passed the land-today gate — the coarse `_present_elevation` lookup let it through. **Data fix.** |
| **Newark Rift Valleys** | 1.00 → 0.20 | Positions differ by **18° of latitude** at 210 Ma. The two models are supposed to *agree* on latitude, so this is a **plate-assignment problem** (PALEOMAP pid 224), not a frame disagreement. Worth one look. |
| **West Antarctic Rift** | 0.64 → 0.27 | Antarctic interior, near the pole where the partitioner is least reliable and the DEM least informative. |
| **Cimmerian Belt** | 0.86 → 0.43 | **The new position is better at the age checked** — shelf (−44 m) versus deep (−2880 m) — and worse at others. Cimmeria is a *ribbon of seven fragments*, already a `COMPOSITE_LABELS` case; a single point cannot represent it under either frame. |
| **Kerguelen Microcontinent** | 0.75 → 0.50 | New position reads **land (+207 m)** where old read shelf. For an emergent 118–95 Ma plateau, land is arguably the *correct* answer and the scorer's `island` expectation is what is wrong. |
| **Rhodope Massif** | 0.62 → 0.46 | Small Aegean block in the most tectonically shredded region on Earth; neither model resolves it. |

**Four of the seven are data or scorer problems, not frame regressions.** Two are
genuinely ambiguous. That is the real residue.

## 4. The protocol — five steps, in order

1. **Never ship on an average.** Run `regression_gate.py` before and after. An aggregate
   improvement with an unexamined tail is not evidence.
2. **Classify every regression.** A drop that is bad in both frames is a pre-existing
   error surfacing, and the correct response is to **fix the feature**, never to keep the
   compensating error.
3. **Adjudicate the true ones with an independent witness.** Our own PaleoDEM cannot settle
   a dispute in which it is one of the parties. `modeling/audit_reconstruction.py` scores
   against Deep Time Maps, which is independent of both our terrain and our tracks.
4. **Fix, exempt, or record.** Every surviving TRUE case must end in one of: a corrected
   coordinate/window/type; a documented exemption with a reason; or a recorded known-limit.
   None may be silent.
5. **Re-run and diff.** The gate is re-runnable by design. Ship when the TRUE count is zero
   or every remaining case has a written reason.

## 5. The same discipline for the other staged changes

The frame switch is the one with a bespoke harness. Every other item already has a
pre-existing quantitative gate, and **the rule is that none of them may move backwards**:

| change | the gate that must not regress | where |
|---|---|---|
| **Raise the Cretaceous (C1)** | `ice_audit.py` — 22/22 keyframes inside the literature ice range. Warming the Cretaceous must not push an ice-bearing frame out of range, and the Mesozoic ice-free interval (50–250 Ma, confirmed by *two* independent sources in WP-05) must stay exactly zero. | `build/ice_audit.py` |
| | `climate_audit.py` — the GMST/CO₂ consistency check must not develop new violations. | `modeling/climate_audit.py` |
| **Lower O₂ (C3)** | metadata only; no geometry, no field rebuild. `audit_cards.py` must stay at 0 HIGH. | `modeling/audit_cards.py` |
| **Hotspots → seamounts (D1–D4)** | the sea-floor measurements in README §10: ocean R/B 0.39, G/B 0.48, saturation 0.61, the four spectral bands, local grain coherence. Seeding along plume tracks must not move any of them outside the reference envelope. | README §10 table |
| **B1 biota panel** | `audit_curated_biota.py` — the **9 exceptions must remain exceptions**; a run that reclassifies Solnhofen as province-typical is a bug. And no card may lose content: a label with a curated list today must not end up with less than the province assemblage. | `modeling/audit_curated_biota.py` |
| **Card text (Tier 2)** | `audit_cards.py` 0 HIGH, and coverage may only go up — every event currently mentioned must still be mentioned. | `modeling/audit_cards.py` |
| **Label windows** | `audit_label_windows.py` — currently 2 findings from 46 matched. It may not increase. | `modeling/audit_label_windows.py` |
| **Everything** | `check_shader.py` before any shader edit; the live `DATA_V` stamp after deploy. | `build/check_shader.py` |

## 6. What this cannot promise

Being straight about the limit:

- **The classifier in `regression_gate.py` is currently heuristic.** It separates
  PRE-EXISTING / DEM-LIMITED / CANCELLATION / TRUE by score thresholds and label type, not
  by consulting the independent witness. Wiring `audit_reconstruction.py` in as the
  adjudicator is the obvious next improvement and would likely move two or three of the
  seven out of TRUE.
- **"Accuracy" here is medium-match** — does the feature sit on land, shelf or deep water
  as its own name implies. That is a good proxy and not the whole truth; a feature can be
  on land and still on the wrong continent. WP-05's IoU and kappa measurements are the
  stronger test and cover the map as a whole rather than per feature.
- **Where two published models genuinely disagree, no protocol resolves it.** WP-05 found
  our Palaeozoic shelf seas run 3–11 points *more* extensive than Blakey's and our
  Triassic–Jurassic runs 5–9 points *less*. Those are open disagreements between
  reconstructions, and the honest response is to record them, which it does.

---

**Bottom line for the implementation session:** the frame switch improves 58 features,
leaves 79 unchanged, and needs a decision on **7**, of which four look like data errors the
switch merely exposed. That is a manageable, named list — not an unquantified risk. Run the
gate, work the list, and ship when it is empty or written down.
