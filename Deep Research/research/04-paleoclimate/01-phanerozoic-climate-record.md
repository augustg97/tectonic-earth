# The Phanerozoic Climate Record

**Domain:** paleoclimate · **Status:** first pass, 2026-07-26
**Feeds directly:** `build/climate.py` (the era climate table: `gmst`, `co2`, `o2`, `iceS`, `sealevel`, `temp` anomaly), `refresh_manifest.py`, the readout, `#glPanel`
**Headline:** the reference standard for GMST is now **PhanDA (Judd et al. 2024, *Science* 385, eadk3705)**. Our table predates it and should be checked against it.

---

## 1. PhanDA — the current best global mean surface temperature curve

**Method.** Paleoclimate *data assimilation*: >150,000 published proxy data points across five proxy types, statistically blended with >850 Earth-system model simulations run at the appropriate continental configuration and atmospheric composition for each interval. This is important — earlier curves were proxy-only and therefore biased by where the proxies are (tropical shallow marine), whereas DA propagates a physically consistent global field.

**Coverage:** 485 Ma → present (i.e. Ordovician onward; it does **not** cover our 1000–485 Ma window).

**Range:** GMST spans **11 °C to 36 °C**.

- **Coldest:** ~11 °C, Late Pleistocene glacial maxima.
- **Hottest:** ~36 °C, **Turonian** (93.9–89.4 Ma).
- Earth spent **more** of the Phanerozoic warm than cold. The modern ~15 °C is near the cold end of the distribution, not the middle.

**Five climate states** are identified. The three named in secondary coverage:

| state | GMST | ice |
|---|---|---|
| icehouse | (coldest band) | polar ice + glacial–interglacial cycles |
| cool greenhouse | 21–24 °C | some polar ice |
| warm greenhouse | 24–30 °C | no polar ice |
| (hothouse / extreme, above 30 °C) | 30–36 °C | none |

**CO₂ is the dominant control**, with an *apparent Earth-system sensitivity* of **~8 °C per CO₂ doubling** over Phanerozoic timescales. That number is much larger than the ~3 °C equilibrium climate sensitivity, because it folds in the slow feedbacks (ice sheets, vegetation, weathering) that a deep-time average necessarily includes.

### Model implication — concrete

1. **Check `climate.py`'s `gmst` column against PhanDA.** In particular the Cretaceous: if our peak is well below 30 °C we are running the greenhouse too cool, and every downstream field (ice line, rainfall via `render.compute_fields`, biome colour) inherits the error.
2. **Our readout should name the climate state**, not just print a number — "warm greenhouse, no polar ice" is the sentence a reader can use, and it is exactly what `iceLand`/`iceSea` already measure. The state boundaries above give a defensible mapping.
3. **PhanDA stops at 485 Ma.** For 1000–485 Ma we remain on the older literature and should say so in the app's About page. The Cryogenian entries are constrained by glacial deposits, not by a GMST curve.
4. **~8 °C apparent sensitivity is a useful sanity check on our own table:** if our CO₂ column doubles between two ages and our GMST moves by 1 °C, one of the two columns is wrong.

---

## 2. Atmospheric CO₂

**Long-term trend: down.** Set by the balance of volcanic/metamorphic degassing against silicate weathering and organic carbon burial. Two step-changes dominate:

- **Devonian–Carboniferous**, the spread of deep-rooted vascular land plants accelerated silicate weathering and buried enormous organic carbon → the Late Palaeozoic CO₂ minimum and the LPIA.
- **Cenozoic**, Himalayan uplift exposing fresh silicate + declining degassing → the slide into the current icehouse.

Reference values (order of magnitude; proxy scatter is large):

| interval | CO₂ (ppm) | note |
|---|---|---|
| Cambrian ~500 Ma | up to ~4000 | |
| Ordovician ~450 Ma | ~300–700 (phytane) | proxy evidence explicitly called unreliable |
| Devonian ~400 Ma | ~2000 (peak of the last 420 Myr in some compilations) | |
| Carboniferous–Permian ~300 Ma | ~200–400 | the deep minimum; LPIA |
| Triassic–Jurassic ~220–200 | secondary peak | |
| Cretaceous | 4–6× modern preindustrial | |
| Eocene–Oligocene boundary ~34 Ma | ~760 | the threshold that glaciated Antarctica (tipping point quoted at ~600 ppm) |
| Miocene ~20 Ma | <300 | |
| Pleistocene glacials | 180–210 | interglacials 280–300 |

**Snowball termination:** the Marinoan ended at ~635 Ma after volcanic CO₂ built to **~12% by volume (~120,000 ppm)** — the escape threshold. Our climate table already carries a CO₂ spike near "~350× modern" at each Cryogenian termination, which is the same statement.

**Proxies and their weaknesses:** ice cores (direct, ≤800 kyr), stomatal index (calibration-sensitive, saturates at high CO₂), paleosol carbonates (assumption-heavy), boron isotopes in foraminifera (needs seawater δ¹¹B history), alkenones, phytane. None is reliable alone before the Cenozoic.

**Faint young Sun.** Solar luminosity was ~70% of modern at 4.5 Ga; the model already implements Gough (1981), giving −8% at 1000 Ma and +2.24% at +250 Myr. The paradox — liquid water despite a dim Sun — is resolved by much higher greenhouse forcing early on. **Our 1000 Ma frame should therefore *not* be cold merely because the Sun is dim; the CO₂ term must compensate.** Worth a check on the table's Tonian rows.

---

## 3. Named climate events, with what the model does or should do

| event | age | what happened | model status |
|---|---|---|---|
| Sturtian snowball | 717.4–661.7 Ma | ~56 Myr of low-latitude glaciation | in table (corrected 2026-07-18) |
| non-glacial interlude | 661.7–~650 | genuinely ice-free | in table |
| Marinoan snowball | ~650–635.5 | second global glaciation; cap carbonates | in table |
| Gaskiers | ~580 Ma | ≤340 kyr, **regional**, not a snowball | in table, correctly not a snowball |
| Hirnantian glaciation | ~445–443 Ma | short, sharp; South Pole over N Africa; drove the End-Ordovician extinction | in table + `#glPanel` |
| Late Devonian glaciation | ~372 & ~360 Ma | diamictites in Bolivia/Peru/Brazil | added 2026-07-23 (iceS=72) |
| Late Palaeozoic Ice Age (LPIA) | ~360–255 Ma | the longest Phanerozoic icehouse; Gondwanan ice sheets; drove the Carboniferous cyclothems | in table |
| Permian–Triassic hothouse | 252–247 Ma | equatorial "dead zone", SST >35 °C | check table |
| Early Jurassic Toarcian OAE | ~183 Ma | Karoo–Ferrar | not represented |
| Cretaceous OAE 1a / OAE 2 | ~120 / ~94 Ma | black shales, Ontong Java / Caribbean LIPs | not represented |
| Cretaceous Thermal Maximum | ~93.9–89.4 Ma (Turonian) | **PhanDA global maximum, 36 °C** | check table |
| K–Pg impact winter | 66 Ma | months–years of darkness, then a ~100 kyr warm pulse | extinction card only |
| PETM | 56 Ma | +5–8 °C in ~20 kyr, recovery ~200 kyr | not represented as an event |
| EECO | 53–49 Ma | the Cenozoic warm peak | check table |
| Eocene–Oligocene transition | ~34 Ma | Antarctic glaciation at ~760 ppm | in table |
| Mid-Miocene Climatic Optimum | ~17–14 Ma | | check |
| Northern Hemisphere glaciation | ~2.7 Ma | | in table |
| LGM | ~21 ka | sea level −125 m; pluvial lakes at maximum | represented via lakes note |

**Two events worth adding as first-class app objects:** the **PETM** and the **Cretaceous OAEs**. Both are short relative to a 5 Myr keyframe, so they cannot be *drawn*; but the extinction/glaciation card pattern (`#extinctBox`, `#glPanel`) is exactly the right vehicle — a fourth navigable structure, "climate events", would carry them without pretending the map resolves them.

---

## 4. Sea level

There is no single agreed Phanerozoic eustatic curve. The main published compilations are **Haq & Al-Qahtani (2005)** (Arabian platform), **Haq & Schutter (2008)** (Palaeozoic), **Snedden & Liu (2010)**, and strontium-isotope-based first-order reconstructions. They disagree substantially:

- long-term (first-order) shape is agreed: **highstands in the Ordovician and the Late Cretaceous, lowstands in the Permian–Triassic and the late Cenozoic**, following the supercontinent cycle through ridge volume.
- **Late Cretaceous highstand: +200 to +300 m**, submerging up to ~82% of Earth's surface at peak.
- amplitude of *third-order* cycles is contested: <40 m (one camp) vs frequently >40 m and periodically >100 m (Haq).
- A 2016 review is literally titled *"A 'chaos' of Phanerozoic eustatic curves"* — the disagreement is the state of the art, not a gap in our reading.

**Model implication.** Two things follow, and both are already half-implemented:

1. The **Phanerozoic PaleoDEMs are already relative to contemporaneous sea level** — do not subtract `sealevel_for()` from them (recorded trap). Only the future series needs the correction.
2. Because the curves disagree, **our sealevel column should be presented as a first-order estimate with an explicit source**, and the About page should say which curve. A reader who checks Haq against our number and finds 60 m of difference should be able to see why.

---

## 5. Proxies and their limits — what a card should never over-claim

| proxy | measures | breaks when |
|---|---|---|
| δ¹⁸O of carbonate | temperature *and* ice volume *and* salinity, entangled | diagenesis; ice-volume term unknown pre-Cenozoic; seawater δ¹⁸O secular change |
| Mg/Ca in foraminifera | temperature | seawater Mg/Ca has changed by a factor of ~2 across the Phanerozoic |
| TEX86 | sea surface temperature | calibration saturates above ~30 °C — exactly the interval we most care about |
| clumped isotopes (Δ47) | temperature independent of water composition | needs a lot of material; solid-state reordering in deep burial |
| alkenones | SST | only from ~130 Ma (haptophyte range) |
| leaf physiognomy / NLR | terrestrial MAT | needs modern analogues; no analogue for a polar broadleaf forest |
| stomatal index | CO₂ | saturates above ~1000 ppm |

**The honest sentence for the app:** deep-time temperature is a *model-plus-proxy* product, not a measurement, and the error bars widen going back. PhanDA publishes uncertainty envelopes; if we ever plot the curve, plot the envelope.

---

## Sources

- **Judd, E. J., Tierney, J. E., et al. (2024), "A 485-million-year history of Earth's surface temperature", *Science* 385, eadk3705** (doi:10.1126/science.adk3705). Perspective by B. J. W. Mills (Leeds). **Primary reference for GMST. Obtain the published PhanDA time series and diff it against `climate.py`.**
- Wikipedia, *Geologic temperature record*, *Carbon dioxide in Earth's atmosphere*, *Sea level rise* — retrieved 2026-07-26. (The temperature article is thin and should not be relied on for numbers; PhanDA supersedes it.)
- Haq, B. U. & Schutter, S. R. (2008), *Science* 322 — Palaeozoic sea level. Haq & Al-Qahtani (2005). Snedden & Liu (2010).
- Ruban, D. A. (2016), "A 'chaos' of Phanerozoic eustatic curves", *Journal of African Earth Sciences*.
- Berner, R. A. (2006), GEOCARBSULF, *GCA* 70 — coupled O₂/CO₂. Krause, A. J. et al. (2018), *Nature Communications* — GEOCARBSULFOR. Krause et al. (2022), *Annu. Rev. Earth Planet. Sci.* — "Evolution of Atmospheric O₂ Through the Phanerozoic, Revisited".
- Gough, D. O. (1981), *Solar Physics* 74, 21 — solar luminosity model, already implemented.

## Open items

- [ ] Obtain the PhanDA GMST series (Science supplementary / Zenodo) and produce a diff table against `climate.py`.
- [ ] Decide a single citable sea-level curve and record it.
- [ ] Decide whether to add a "climate events" navigable structure for PETM / OAEs / hyperthermals.
