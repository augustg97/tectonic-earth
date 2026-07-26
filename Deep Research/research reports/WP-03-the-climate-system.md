# WP-03 · The Climate System Across Deep Time

**Deep Research white paper 03** · drafted 2026-07-26 · status: **v1, actionable**
**Scope:** global temperature, CO₂, oxygen, ice, sea level, ocean chemistry and circulation from 1000 Ma to +250 Myr, and what Tectonic Earth's climate table should be checked against.
**Figures:** [`06-snowball-bifurcation.svg`](../diagrams%20and%20illustrations/authored/06-snowball-bifurcation.svg) · [`04-lip-to-extinction-cascade.svg`](../diagrams%20and%20illustrations/authored/04-lip-to-extinction-cascade.svg) · [`01-deep-time-master-chart.svg`](../diagrams%20and%20illustrations/authored/01-deep-time-master-chart.svg)
**Code:** [`modeling/climate_ebm.py`](../modeling/climate_ebm.py) · [`modeling/deeptime.py`](../modeling/deeptime.py)

---

## Executive summary

The app's climate table was built and repeatedly corrected before **PhanDA** (Judd, Tierney et al., *Science* 385, eadk3705, September 2024) existed. PhanDA is a paleoclimate **data assimilation** — >150,000 proxy data points blended with >850 Earth-system model simulations run at the correct continental configuration for each interval — and it is now the reference standard for Phanerozoic global mean surface temperature. Three of its results bear directly on us:

- **GMST spans 11 °C to 36 °C.** The maximum is the **Turonian (93.9–89.4 Ma)**; the minimum is Late Pleistocene glacial. Earth spent **more** of the Phanerozoic warm than cold, and the modern ~15 °C sits near the cold end of the distribution.
- **CO₂ is the dominant control**, with an *apparent Earth-system sensitivity* of **~8 °C per doubling** — much larger than the ~3 °C equilibrium sensitivity, because a deep-time average necessarily folds in the slow feedbacks.
- **Five climate states**, of which three are named in the coverage: cool greenhouse 21–24 °C with some polar ice, warm greenhouse 24–30 °C with none, icehouse with polar ice and glacial–interglacial cycles.

PhanDA covers 485 Ma → present. Our window runs to 1000 Ma, so **half our Precambrian is outside any GMST curve** and rests on glacial deposits instead. The app should say so.

---

## 1. What to re-check in `climate.py`, and why

| check | test | why it matters downstream |
|---|---|---|
| **Cretaceous GMST** | is our peak near 30–36 °C? | rainfall (`render.compute_fields`), ice line, biome colour and vegetation all derive from temperature; a cool greenhouse propagates everywhere |
| **CO₂ vs GMST consistency** | between any two ages, does ΔGMST ≈ 8 °C × log₂(CO₂ ratio)? | catches a wrong value in *either* column |
| **O₂ peak** | ~**30%**, in the Pennsylvanian–early Permian | 35% is the high end of older GEOCARBSULF runs; Krause et al. (2022) is the current review |
| **Tonian rows** | the Sun is 8% fainter at 1000 Ma; is CO₂ high enough to compensate? | a cold Tonian for the wrong reason is worse than a warm one |
| **Ice lines vs the EBM** | does the table's `iceS` sit where the physics puts it, given the table's own CO₂ and solar? | `iceS` is currently an *input*; this makes it falsifiable |

That last row is the point of `modeling/climate_ebm.py`. The ice audit already checks *drawn* ice area against the literature — good, and it took the model from 11/22 keyframes out of range to 22/22. But it cannot say whether the ice line is *physically consistent* with the CO₂ we claim in the same row. A one-dimensional diffusive energy-balance model can.

**Read the EBM's stated limits before quoting it.** Calibrated on the present it gives 13.4 °C and an ice line at 71.8°, against a real 14–15 °C and a margin near 70–75°. But it **understates hothouses badly** — 17 °C at 1000 ppm and 90 Ma against PhanDA's ~36 °C for the Turonian — because a 1-D model with no clouds, no water-vapour lapse-rate amplification and no continents has an effective sensitivity of ~2.5 °C per doubling rather than PhanDA's ~8. Use it for the **shape** of the response and the **position** of the ice line, never for absolute greenhouse GMST.

---

## 2. The snowball bifurcation, and why it is worth drawing

The EBM does reproduce, cleanly, the one thing a linear climate intuition cannot: **hysteresis**. Once ice reaches the subtropics, the albedo feedback runs away and the planet freezes over; escaping again needs a CO₂ level orders of magnitude above the one that let it freeze. That is why the Cryogenian terminations required a CO₂ spike of order 10⁵ ppm — the Marinoan ended at ~635 Ma once volcanic CO₂ reached about **12% by volume (~120,000 ppm)** — and why each termination is followed by a **cap carbonate** and a super-greenhouse.

Our climate table already carries a CO₂ spike near "~350× modern" at each termination, which is the same statement. The EBM's own escape threshold comes out high (~1400× at 700 Ma) for a reason it declares: the logarithmic CO₂ forcing law is simply wrong by a large factor at 10⁵ ppm. **The hysteresis is robust; the number is not.** The app should present the mechanism, not the threshold.

Also settled by earlier work and worth keeping: the Cryogenian is **two** snowballs with a genuine non-glacial interlude — Sturtian 717.4→661.7, gap, Marinoan ~650→635.5 — not one long freeze. Gaskiers (~580 Ma) is ≤340 kyr and regional. The "Kaigas" ~750 Ma glaciation is rejected in current literature.

---

## 3. The oxygen story, told correctly

| interval | O₂ | evidence |
|---|---|---|
| before ~2.45 Ga | **~0.001% PAL** | mass-independent S isotope fractionation (no ozone); detrital pyrite and uraninite surviving in river sands |
| GOE 2.46–2.06 Ga | to 0.02–0.04 atm, ~10% PAL by the end | banded iron formations peak ~2.5 Ga and vanish by 1.85; red beds from ~2.0; S-MIF gone after ~2.3 |
| Lomagundi–Jatuli ~2.3 Ga | an **overshoot**, possibly near-modern | followed by a crash at ~2.1 (Shunga–Francevillian) |
| "boring billion" 1.8–0.8 Ga | a few percent PAL, widely euxinic mid-depths | eukaryotes exist and do not radiate |
| NOE ~850–540 Ma | to near-modern | the permissive condition for large animals |
| Phanerozoic | below present until the late Devonian; **~30% peak in the Permo-Carboniferous**; Mesozoic low; recovery to 21% | GEOCARBSULF and successors |

The GOE's consequences are the more interesting half: oxidising methane — the Archaean greenhouse gas — to CO₂ and water collapsed the greenhouse and triggered the **Huronian glaciation** (2.45–2.22 Ga); anaerobes were mass-extinguished; and **over 2,500 of Earth's ~4,500 mineral species owe their existence to it.**

The right causal frame for the app's Ediacaran card is not "oxygen rose and then animals appeared" but "**the ocean interior finally stopped being anoxic, and macroscopic multicellularity became possible in it**".

---

## 4. Ocean chemistry — and the rendering rule it implies

Redox states in the order the record shows them: **ferruginous** (dissolved Fe²⁺, BIFs) → **euxinic** (free H₂S below a shallow chemocline) → **oxic-stratified** (oxygen-minimum zones) → **fully ventilated**.

**Anoxia is subsurface.** The Black Sea is fully euxinic below ~100 m and its surface looks entirely ordinary; atmospheric CO₂ shifts Rayleigh scattering by <2% even at 6000 ppm. So:

- **Do not** render green, purple, milky or blood-red global oceans for anoxic intervals.
- **Do** keep the conservative surface progression already implemented — iron-tinted/greener Precambrian → modern coccolith-clear blue after ~201 Ma, productivity greening *shelves* and not gyres.
- **Do** consider representing an OAE where it actually lives: **black, finely laminated, un-bioturbated mud on the shelf and basin floor.** (70% of the world's oil source rocks are Mesozoic — they *are* these events.)

Two further chemistry facts the app could draw:
- **Calcite and aragonite seas alternate** with seawater Mg/Ca, which is set by ridge hydrothermal flux — i.e. by the supercontinent cycle. This governs which organisms build reefs.
- **The carbonate factory moves offshore at ~201 Ma** when coccolithophores begin raining carbonate onto the deep floor. Before that, carbonate accumulates almost entirely on shelves. That is a real change in what the sea floor *is made of*, and it is the same date as the ocean-colour change.

---

## 5. Circulation, and the cheapest honest model

The app has no ocean-current model at all. It does not need a fluid solver. It needs three structural facts:

1. **Subtropical gyres are asymmetric** — a broad diffuse eastern equatorward limb, a narrow fast **western boundary current**. Ekman transport at ~45° to the wind drives **eastern-boundary upwelling**, which is where the most productive water on Earth is.
2. **The conveyor is slow**: the oldest water upwells in the North Pacific after ~1000 years.
3. **The Antarctic Circumpolar Current exists only when a circumpolar path exists** — Drake Passage crust is 34–29 Ma and the full ACC dates from ~23 Ma.

A latitude-banded gyre template laid over the real basin geometry from the elevation field, with west intensification built in and an ACC gated on circumpolar connectivity, produces all three from geometry the model already has.

And then the **gateways explain themselves**, which is the cleanest link in the whole app between the plate model and the climate readout:

| gateway | when | consequence |
|---|---|---|
| Tethys circumglobal seaway | closes ~19–14 Ma | end of the circumglobal tropical current |
| Drake + Tasman | 34–23 Ma | ACC; Antarctic thermal isolation and glaciation |
| Panama | shoals ~10 Ma, land route ~2.7 Ma | strengthened Gulf Stream; Great American Interchange |
| Bering | ~5.5 Ma | trans-Arctic interchange |
| Turgai Strait | closes ~29 Ma | Asian–European mammal exchange |
| Viking / Hispanic Corridors | Mesozoic | Boreal↔Tethyan faunal mixing |

---

## 6. What the app should stop claiming, and what it should start saying

**Stop:** presenting deep-time GMST, CO₂ and sea level as measurements. They are model-plus-proxy products and the error bars widen going back. Every proxy has a specific failure mode — δ¹⁸O entangles temperature with ice volume and seawater composition; Mg/Ca must be corrected for a seawater ratio that has changed twofold; **TEX86 saturates above ~30 °C, exactly where the hothouses are**; alkenones only exist from ~130 Ma; stomatal index saturates above ~1000 ppm.

**Start:** naming the **climate state** rather than only a number. "Warm greenhouse — no polar ice" is a sentence a reader can use, it is defensible from PhanDA's own scheme, and the app already measures `iceLand` and `iceSea` per keyframe, so the claim and the map cannot drift apart. That last property is the one that has repeatedly mattered: the "Ice: polar caps" readout was once inferred from a *threshold* rather than from drawn ice, and 41 of 119 claiming keyframes announced polar caps over an ice-free map.

---

## Open items

- [ ] Obtain the PhanDA GMST time series and produce a diff table against `climate.py`.
- [ ] Check the O₂ peak (30% not 35%) and its position.
- [ ] Add a "climate events" navigable structure for the PETM, OAEs and the Eocene optima — shorter than a keyframe, so cards rather than geometry.
- [ ] Build `modeling/ocean_circulation.py`.
- [ ] Decide and cite one sea-level curve; the published ones genuinely disagree.
- [ ] Add `contested` to the supercontinent entries, as the glaciation cards already do.

## Sources

Judd, Tierney et al. (2024), *Science* 385, eadk3705 (PhanDA), with the Mills perspective. Berner (2006) GEOCARBSULF; Krause et al. (2018) *Nat. Commun.*; Krause, Mills et al. (2022) *Annu. Rev. Earth Planet. Sci.* Gough (1981) *Solar Physics* 74, 21. Haq & Schutter (2008); Haq & Al-Qahtani (2005); Snedden & Liu (2010); Ruban (2016) on the disagreement between them. Hardie (1996) on calcite/aragonite seas. Wikipedia *Great Oxidation Event*, *Anoxic event*, *Ocean current*, *Carbon dioxide in Earth's atmosphere*, *Geologic temperature record* (retrieved 2026-07-26; the last is thin and PhanDA supersedes it).
