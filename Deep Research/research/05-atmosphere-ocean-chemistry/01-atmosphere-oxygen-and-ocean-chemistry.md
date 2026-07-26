# Atmosphere, Oxygen and Ocean Chemistry Through Deep Time

**Domain:** atmosphere / ocean chemistry · **Status:** first pass, 2026-07-26
**Feeds directly:** `climate.py` `o2` and `co2` columns, `SEA_COLOUR`, the readout, biota card text
**Why it matters for a *visual* model:** oxygen sets what animals are possible and how large they get; ocean redox sets what colour the shelf is and where black shale forms; and both change the sky and the sea in ways that are easy to over-dramatise. This file exists partly to bound the drama.

---

## 1. The oxygenation of the atmosphere

### Before ~2.45 Ga
O₂ at **~0.001% of present atmospheric level (PAL)**. Evidence: **mass-independent fractionation of sulfur isotopes** (requires unshielded UV photochemistry, hence no ozone), and **detrital pyrite, uraninite and siderite** surviving in river sands — minerals that oxidise within kilometres of transport in an oxygenated world.

### Great Oxidation Event, 2.46–2.06 Ga
- O₂ rises to **0.02–0.04 atm** (2–4% PAL), reaching ~10% PAL by the end.
- **Banded iron formations** peak ~2.5 Ga and largely vanish by 1.85 Ga — they need a *ferruginous deep ocean* (dissolved Fe²⁺) beneath an *oxidised shallow sea*, so their disappearance dates the oxidation of the deep.
- **Red beds** (hematite-coated sandstone) appear ~2.0 Ga.
- The **S-MIF signature disappears after ~2.3 Ga** — the ozone layer forms.
- **Lomagundi–Jatuli excursion, ~2.3 Ga:** an overshoot, possibly to near-modern O₂, followed by a **crash at ~2.1 Ga** (Shunga–Francevillian black shales). Oxygenation was not monotonic.
- **Consequences:** methane, the dominant Archaean greenhouse gas, is oxidised to CO₂ + H₂O; the greenhouse collapses; the **Huronian glaciation** (2.45–2.22 Ga) follows. Anaerobes are mass-extinguished — a biosphere contraction of >80% is proposed. Oxidative stress is invoked in the origin of eukaryotes; mitochondria evolve in the new oxygenated world. Over **2,500 of Earth's ~4,500 mineral species** owe their existence to the GOE.

### The "Boring Billion", ~1.8–0.8 Ga
Tectonically quiet (Columbia then Rodinia), chemically static, oxygen low — a few percent PAL — with widely **euxinic** (sulphidic) mid-depth water. This is the interval in which eukaryotes exist but do not radiate.

### Neoproterozoic Oxygenation Event, ~850–540 Ma
The second rise, to near-modern levels, straddling the Cryogenian snowballs. It is the permissive condition for large animals: an organism metres across with no circulatory system needs an oxygenated water column. **This is the correct causal frame for the app's Ediacaran card** — not "oxygen rose and then animals appeared", but "the ocean interior finally stopped being anoxic, and macroscopic multicellularity became possible in it".

### Phanerozoic O₂
Modelled by **GEOCARBSULF** (Berner 2006) and successors (Krause et al. 2018 GEOCARBSULFOR; Krause et al. 2022 review). Robust features:

- O₂ **below present** until near the end of the Devonian.
- A broad **late Palaeozoic maximum, ~30% O₂ in the Permo-Carboniferous** — driven by burial of the coal forests' organic carbon. (The often-quoted 35% is the high end of older model runs; ~30% is the better current number.)
- Decline through the Triassic to a Mesozoic low, then recovery to ~21%.

**Model check.** `climate.py`'s `o2` curve should peak near **30%, not 35%**, and the peak should sit in the Pennsylvanian–early Permian. The giant-arthropod story (*Meganeura*, *Arthropleura*) is traditionally hung on this peak — but note the Carboniferous-rainforest-collapse literature now finds both genera *after* the collapse and probably forest-independent, so the "high O₂ → giant insects → collapse killed them" chain should be stated as a hypothesis, not a fact.

---

## 2. Ocean chemistry

### Redox states, in order of the geological record
| state | dominant chemistry | when |
|---|---|---|
| **ferruginous** | dissolved Fe²⁺ in the deep ocean; BIFs | Archaean, and again in the Cryogenian |
| **euxinic** | free H₂S below a shallow chemocline | mid-Proterozoic; and locally during OAEs |
| **oxic-stratified** | oxygenated surface, oxygen-minimum zones at depth | Phanerozoic normal |
| **fully ventilated** | deep water oxygenated by cold sinking | icehouse Phanerozoic, including today |

**The rendering rule that follows** (and which project memory already records as the unanimous outcome of an earlier research round): euxinia and anoxia are **subsurface**. The Black Sea is euxinic below ~100 m and its surface looks entirely ordinary. Atmospheric CO₂ shifts Rayleigh scattering by <2% even at 6000 ppm. So:

- **Do not** render green, purple, milky or blood-red global oceans for anoxic intervals.
- **Do** render a defensible surface-colour progression: iron-tinted/greener Precambrian → modern coccolith-clear blue after ~201 Ma, with productivity greening *shelves*, not gyres.
- **Do** consider a *shelf-floor* or *basin* treatment for OAEs — black laminated mud on the sea floor is real and is where the signal actually lives.

### Carbonate and biomineralisation
- **Calcite vs aragonite seas** alternate with seawater Mg/Ca, which is set by ridge hydrothermal flux — i.e. by the supercontinent cycle. Aragonite seas: Cambrian, and Pennsylvanian→Triassic, and mid-Cenozoic→present. Calcite seas: Ordovician→Mississippian, and Jurassic→Palaeogene. This governs which organisms build reefs and how well shells preserve.
- **The carbonate factory moves offshore at ~201 Ma** when coccolithophores (and later planktonic foraminifera) begin raining carbonate onto the deep sea floor. Before that, carbonate accumulates almost entirely on shelves. This is a genuine, drawable change in what the sea floor *is made of*, and it is the same date as the ocean-colour change.

### Salinity
Broadly constant at ~35 psu over the Phanerozoic, buffered by evaporite deposition and dissolution. Large excursions are basinal, not global — Messinian (5.96–5.33 Ma), Zechstein (Late Permian). Do not vary global salinity in the model.

---

## 3. Ocean circulation

**Wind-driven surface layer.** Subtropical gyres, asymmetric by the beta effect: a **broad, diffuse eastern equatorward limb** and a **narrow, fast western boundary current** (Gulf Stream, Kuroshio, Agulhas, Brazil, East Australian). Ekman transport at ~45° to the wind sets coastal **upwelling** on eastern boundaries — the nutrient supply that makes the Peru, Benguela, Canary and California systems the most productive water on Earth. Transport is measured in **sverdrups** (1 Sv = 10⁶ m³/s ≈ 30 Amazons).

**Thermohaline / global conveyor.** Density-driven; North Atlantic Deep Water forms where the Gulf Stream's water has cooled enough to sink; the oldest water upwells in the North Pacific after **~1000 years**.

**Antarctic Circumpolar Current** — the largest current on Earth, wind-driven, uninterrupted around Antarctica, connecting all basins. It exists *only because* Drake Passage and the Tasman Gateway are open, which happened 34–23 Ma.

**Gateways are the controls, and they are tectonic.** This is the cleanest link between the app's plate model and its climate:

| gateway | closes/opens | consequence |
|---|---|---|
| Tethys circumglobal seaway | open through the Mesozoic, closed ~19–14 Ma | a circumglobal tropical current, then its loss |
| Drake + Tasman | open 34–23 Ma | ACC; Antarctic thermal isolation and glaciation |
| Panama | shoals from ~10 Ma, closed ~2.7 Ma | strengthened Gulf Stream; N Hemisphere glaciation debate |
| Bering | opens ~5.5 Ma | trans-Arctic interchange |
| Turgai Strait | closes ~29 Ma | Asian–European mammal exchange |
| Central American Seaway, Hispanic and Viking Corridors | Mesozoic | control Boreal/Tethyan faunal mixing |

**Model implication.** The app has no current model at all (listed as unfinished in README). A *cheap and honest* first version is not a fluid solver: it is a **latitude-banded gyre template** (subtropical gyres centred ~30°, subpolar ~55°, equatorial counter-current) laid over the actual basin geometry from the elevation field, with the west-intensification asymmetry built in, plus an ACC when and only when a circumpolar path exists. Everything on the right side of the table above then follows from geometry the model already has. Draft: `modeling/ocean_circulation.py`.

---

## Sources

- Wikipedia: *Great Oxidation Event*, *Ocean current*, *Anoxic event*, *Carbon dioxide in Earth's atmosphere* — retrieved 2026-07-26.
- Berner, R. A. (2006), GEOCARBSULF, *Geochimica et Cosmochimica Acta* 70, 5653.
- Krause, A. J. et al. (2018), *Nature Communications* 9, 4081 — GEOCARBSULFOR.
- Krause, A. J., Mills, B. J. W. et al. (2022), "Evolution of Atmospheric O₂ Through the Phanerozoic, Revisited", *Annu. Rev. Earth Planet. Sci.*
- Lyons, T. W., Reinhard, C. T. & Planavsky, N. J. (2014), *Nature* 506, 307 — the standard oxygenation history. **Obtain.**
- Hardie, L. A. (1996) — calcite/aragonite seas.

## Open items

- [ ] Diff `climate.py` `o2` against the Krause 2022 curve; check the Permo-Carboniferous peak value and position.
- [ ] Build `modeling/ocean_circulation.py` (banded gyre template + gateway logic).
- [ ] Decide whether to represent OAEs as sea-floor sediment colour rather than water colour.
