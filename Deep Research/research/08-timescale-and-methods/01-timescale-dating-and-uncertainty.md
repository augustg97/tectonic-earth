# The Timescale, Dating, and How Certain Any Deep-Time Number Is

**Domain:** method · **Status:** first pass, 2026-07-26
**Feeds:** `eras_data.json`, every age window in `features.py`, the readout, all card text
**Model:** [`modeling/deeptime.py`](../../modeling/deeptime.py) — ICS v2024/12 to stage level, with a confidence field on every event

---

## 1. Two different kinds of "age"

- **Chronostratigraphic** units (System, Series, Stage) are defined by a **GSSP** — a golden spike driven into a specific bed at a specific outcrop. The unit *is* the rock above that point. Its numeric age is then measured, and **can change** when the measurement improves, without the unit itself changing at all.
- **Chronometric** units are defined by a round number. Everything below the Ediacaran (635 Ma) is chronometric: the Cryogenian base at 720 Ma and the Tonian base at 1000 Ma are *decisions*, not spikes.

**Consequence for the app:** our whole Precambrian window, 1000–635 Ma, sits on chronometric boundaries. They will not move, but they also do not mark anything that happened. A card that treats "the start of the Tonian" as an event is over-reading the timescale.

**A GSSP defines a BASE**, so the boundary instant belongs to the *younger* unit. 66.0 Ma is Paleogene; 66.001 Ma is Cretaceous. `deeptime.py` implements this and asserts it in its selftest — it is the kind of off-by-one that silently mis-assigns every boundary event otherwise.

---

## 2. What each dating method can actually deliver

| method | typical precision | limits |
|---|---|---|
| **U–Pb on zircon (CA-ID-TIMS)** | 0.05–0.1% (±0.1 Myr at 250 Ma) | needs a datable ash bed at the right level; zircons can be inherited or reset |
| U–Pb (SIMS/LA-ICP-MS) | 1–2% | fast and cheap, much less precise |
| **⁴⁰Ar/³⁹Ar** | 0.1–0.5% | needs a K-bearing mineral; sensitive to argon loss and to the age of the flux monitor |
| Rb–Sr, Sm–Nd, Lu–Hf | 1–3% | usually isochrons on whole rock; open-system risk |
| **K–Ar on authigenic clay** | poor and often meaningless | **the Woodleigh cautionary case**: its "364 Ma" rests entirely on this, is formally disputed (Renne et al. 2002), and the real bracket is 168–2005 Ma |
| Magnetostratigraphy | correlation, not age | needs an independent anchor and a reversal pattern |
| Biostratigraphy | zone-level, often <1 Myr in the Mesozoic | only as good as the zonal scheme, and provincial faunas break correlation |
| **Astrochronology** | 20–400 kyr cycles, superb *relative* precision | needs a continuous well-sampled section; anchoring is a separate problem |
| Radiocarbon | ±decades to centuries | ≤~55 ka only |

**Rule of thumb the app should respect:** an age quoted to three significant figures beyond ~500 Ma is usually claiming precision the method does not have. The ICS itself carries formal uncertainties on most boundaries.

---

## 3. Confidence is a first-class field, not a footnote

`deeptime.py` gives every event a `confidence` of `good` / `moderate` / `contested`, and `paleogeography.py` does the same for blocks and assembly memberships. This is not decoration: the app already learned that a flat statement misrepresents an open question. The glaciation cards carry a `contested` field precisely because the hard-vs-slushball snowball question, and whether the Early Cretaceous had any ice at all, are both genuinely unsettled.

Things currently stated flatly in the app that the literature does not settle:

| claim | actual state |
|---|---|
| Pannotia was a supercontinent | contested; the pieces may never have all been joined |
| the Rodinia configuration | five competing models for what sat off Laurentia's western margin |
| Early Cretaceous ice | contested |
| the Hawaii–Emperor bend records a plate-motion change | now widely read as **plume** motion |
| the Isthmus of Panama closed at 2.7 Ma | the shoaling history is actively debated back to ~10 Ma |
| the Carboniferous rainforest collapse drove endemism | a 2018 study finds *increased* cosmopolitanism |
| high O₂ produced the giant Carboniferous arthropods | both taxa now found after the collapse and probably forest-independent |
| Woodleigh is 364 Ma | K–Ar on authigenic clay, disputed; bracket is 168–2005 Ma |
| Karakul is 25 Ma | **no radiometric age at all**; 25 Ma is an early guess |

The last two are already flagged `poor` in `IMPACT_CONFIDENCE`. The rest are not flagged anywhere.

---

## 4. Precision the app's own grid imposes

Independently of the science, three of our own choices set floors on what can be represented:

- **5 Myr keyframes.** Anything shorter than that cannot be *drawn*, only *described*. The PETM (~200 kyr), the Messinian (~630 kyr), OAE 2 (~820 kyr), the Hirnantian (~2 Myr) and the entire Quaternary glacial cycle are all sub-keyframe. Cards, not geometry.
- **~9.8 km grid (2048×1024).** Epicontinental seas 60–165 m deep are at or below what the source PaleoDEMs resolve — which is why `epeiric.py` seeds the Trans-Saharan and Cannonball seaways rather than expecting them to appear. Notable lakes need the same treatment.
- **`labelVisible` slack of 0.8 Myr**, reduced from 2.5 (half a keyframe) after names outlived their features. Pleistocene megalakes with windows of only kiloyears need `min(2.5, |a1−a0|·0.5)` or they float onto the present-day map.

---

## 5. Practice for this research programme

1. Quote a number **with its source**, and where sources disagree, say so and give both.
2. **Do not propagate an inconsistent source.** Wikipedia's *List of orogenies* table contains rows that contradict the topic articles (Mozambique at 2.97–2.65 Ga; Napier at 4.0 Ga, older than the oldest rock; Alpine at 150–250 Ma). Dates in these dossiers come from body text, not that table.
3. **A rate limit is not an absence.** A 429 looks exactly like "no such image"; the figure-fetch script backs off and records `no-results (could be a rate limit)` rather than concluding the figure does not exist.
4. **Correct licence does not mean correct subject.** Of the first eight figures fetched under a strict licence filter, one was a 1913 chromosome diagram matched on the word "cycle" and three were mislabelled. Everything is eyeballed on a contact sheet before use.

---

## Sources

ICS International Chronostratigraphic Chart v2024/12. Schmieder & Kring (2020) and the Impact Earth database for impact-age confidence. Renne et al. (2002) on Woodleigh. Method precisions are standard geochronology and should be re-sourced to a named text before being quoted in the app.
