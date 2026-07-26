# The Supercontinent Cycle

**Domain:** plate tectonics · **Status:** first pass, 2026-07-26 · **Feeds:** `eras_data.json` supercontinents, `build_synthetic.pre_placement()`, label windows in `features.py`

---

## 1. What the cycle is

Continental lithosphere is buoyant and does not subduct. Once created it is shuffled indefinitely, so the same crust is repeatedly gathered into a single mass and dispersed again. One full gather–disperse turn takes **300–500 Myr**. This is the single largest-amplitude boundary condition on everything else the model draws: sea level, climate, ocean circulation, biological provinciality and the shape of the coastline all follow it.

The cycle is not a clock. Each turn assembles a *different* set of blocks in a *different* arrangement, and the mechanism by which the next supercontinent forms differs between turns:

| mechanism | how the next supercontinent forms | example |
|---|---|---|
| **introversion** | the *interior* ocean that opened during breakup closes again; the continents reverse their motion | Pangaea (the Rheic — an interior ocean of Pannotia/Gondwana — closed) |
| **extroversion** | the interior ocean keeps widening and the *exterior* superocean closes instead; continents travel ~180° | Rodinia → Gondwana is often read this way |
| **orthoversion** | the next assembly forms ~90° away from the last, over the downwelling girdle that surrounds the old one | proposed for Amasia (Arctic closure) |

**Model implication.** The future series in `build_fields.future_grid` implements one specific hypothesis (Pangaea Ultima / Pangaea Proxima — an *introverted* Atlantic closure). That is a defensible choice because Farnsworth et al. (2024) modelled the climate on exactly that reconstruction, but the app should say so: it is one of four published futures, not the projected future. See `research/01-plate-tectonics/05-future-supercontinents.md`.

---

## 2. The named supercontinents

Confidence falls off steeply with age. Only the last two are reconstructions in the strict sense; the earlier ones are correlations of orogenic belts and paleomagnetic poles with large permissive error.

| supercontinent | age (Ma) | confidence | note |
|---|---|---|---|
| Vaalbara | 3600–2800 | speculative | Kaapvaal + Pilbara only; possibly never more than two blocks |
| Ur | ~3000 | speculative | |
| Kenorland / Superia | 2700–2100 | low | possibly several independent supercratons rather than one mass |
| **Columbia (Nuna)** | 1800–1500 | moderate | first assembly with a broadly agreed cast |
| **Rodinia** | 1250–750 | moderate | configuration actively disputed — see §3 |
| Pannotia (Greater Gondwana) | ~633–573 | **contested** | may never have been a single coherent mass; several authors reject it outright |
| Gondwana | 550–180 | high | not a *super*continent (≈1/5 of continental area) but the dominant Palaeozoic mass |
| **Pangaea** | 335–175 | high | the only one reconstructed from preserved sea floor at its margins |
| Amasia / Pangaea Ultima / Novopangaea / Aurica | +200 to +250 | hypothesis | four incompatible published futures |

**Model implication — Pannotia.** The app treats Pannotia as a supercontinent card. The literature is genuinely split: the assembly of Gondwana (Brasiliano/Kuunga, ~630–520 Ma) overlapped the final breakup of Laurentia from Amazonia (~570–530 Ma), so there may never have been an instant at which the pieces were all joined. Card text should carry that, as the glaciation cards already carry `contested`. **Action: add a `contested` field to `eras_data.json` supercontinents and populate it for Pannotia, Kenorland, Vaalbara, Ur.**

---

## 3. Rodinia — why our 1000–540 Ma frames are authored

Rodinia assembled c. 1.26–0.90 Ga out of the fragments of Columbia, by the globally correlated **Grenvillian** orogenic system: Grenville (Laurentia), Sveconorwegian/Dalslandian (Baltica), Musgrave and Albany–Fraser (Australia), Sunsás (Amazonia), Kibaran (Africa).

Core arrangement most reconstructions agree on — **Laurentia at the centre**:

- **SE of Laurentia:** Baltica, Amazonia, West Africa
- **S:** Río de la Plata, São Francisco
- **SW:** Congo, Kalahari
- **NE:** Australia, India, East Antarctica
- **disputed:** Siberia, North China, South China, Tarim

The disagreement is about which block sat off Laurentia's *western* (present-day) margin, and it is not a detail — it changes the whole Pacific-side geometry:

| model | west-of-Laurentia neighbour |
|---|---|
| SWEAT | East Antarctica, with Australia north of it |
| AUSWUS | Australia directly |
| AUSMEX | Australia against present-day Mexico |
| Missing-Link | South China, between Australia and Laurentia |
| revised Missing-Link | Tarim in that role |

**Breakup, in four stages (IGCP 440):**

1. **825–800 Ma** — superplume; rifting in South Australia, South China, Tarim, Kalahari, India, Arabian–Nubian.
2. **800–750 Ma** — India and Congo–São Francisco detach. Mirovia is the surrounding superocean.
3. **750–700 Ma** — the centre of Rodinia crosses the equator; magmatism continues on Kalahari, West Australia, South China, Tarim, and the Laurentian margins.
4. **650–550 Ma** — **Iapetus opens** (east: Baltica–Laurentia; west: Amazonia–Laurentia) while **Adamastor, Braziliano and Mozambique close**; the Pan-African orogenies build Gondwana.

**Model implication.** `precambrian.py` generates craton blobs and `build_synthetic.pre_placement()` positions them. The staged breakup above is the correct skeleton for *when* a given craton should be moving and in which direction, and the four stages give natural break points at **825, 800, 750, 700, 650, 550 Ma** — which is exactly the age range where our labels are least stable. Documented positions per stage belong in `modeling/craton_positions.py`.

---

## 4. Gondwana — assembly, drift, dispersal

**Assembly** is a set of Pan-African sutures, not one event:

| orogeny | Ma | what it welded |
|---|---|---|
| East African | 800–650 | India + Madagascar onto East Africa (closes the Mozambique Ocean) |
| Brasiliano | 660–530 | the South American and African cratons to each other |
| Malagasy | 550–515 | Neoproterozoic India onto Azania + Congo–Tanzania–Bangweulu |
| Kuunga (Pinjarra) | 570–530 | Australia + East Antarctica onto the rest |
| Damara | 530–500 | Congo–Kalahari |
| Petermann | 630–520 | intracratonic, central Australia |
| Ross | 550–480 | the Pacific margin of East Antarctica |

Area ≈ **100 million km²**, about one fifth of Earth's surface — the dominant Palaeozoic landmass but not a true supercontinent.

**Palaeozoic drift.** Southern hemisphere throughout; the South Pole tracks across it from NW Africa (Late Ordovician, hence the Hirnantian ice sheet centred on the present Sahara) to southern Africa and then to Antarctica/Australia during the Late Palaeozoic Ice Age. This pole path is *the* control on the ice-line entries in `climate.py` for 460–300 Ma, and it is why our Late Devonian ice label had to be moved to the Paraná Basin (memory: the Bolivian Altiplano tracks to open ocean at 360 Ma).

**Terranes shed from the northern margin** — the single most useful table for our label work, because each of these is a name the app draws:

| terrane | rifted | destination | accreted |
|---|---|---|---|
| Avalonia | Cambrian–Early Ordovician | Baltica then Laurentia | 457–449 Ma (Baltica), Silurian–Devonian (Laurentia) |
| Armorica | Ordovician | France, Iberia | Variscan, C–P boundary |
| Cuyania / Precordillera | (from *Laurentia*) | NW Argentina | Ordovician |
| Chilenia | — | SW South America | after Cuyania |
| North & South China, Tarim, Qaidam | Devonian | Asia | Late Devonian–Permian (N. China), Permian–Triassic (S. China) |
| Sibumasu | Late Carb–Early Permian | SE Asia | Late Permian–Early Jurassic |
| Qiangtang | Late Carb–Early Permian | Asia | Early Jurassic |
| Lhasa | Late Triassic–Late Jurassic | Tibet | Early Cretaceous |
| Burma, Woyla | Late Triassic–Late Jurassic | SE Asia | Late Cretaceous |
| Afghan, Karakorum, Taurides, Lesser Caucasus, Alborz, Lut, Sanand, Mangyshlak | Permian onward | Alpine–Himalayan belt | Cenozoic, still deforming |

**Breakup**, with the ocean each stage opened:

| Ma | event |
|---|---|
| ~200 | CAMP; central Atlantic rifting; Gondwana begins to part from Laurasia |
| 200–170 | Karoo–Ferrar; the Weddell Sea region opens |
| ~184 | Antarctic Peninsula, Marie Byrd Land, Thurston Island detach; Falklands and Ellsworth–Whitmore blocks rotate 90° in opposite senses; Patagonia pushed west |
| ~190–100 | South Atlantic unzips south→north; Paraná–Etendeka 135–130; Benue Trough ~118; land connection persists to ~120 (identical dinosaur ichnofaunas); fully open ~83 |
| ~150 | oldest floor between Madagascar and Africa |
| 132.5–96 | India moves NW away from Australia–Antarctica; India–Antarctica separate ~120 |
| 118–95 | Kerguelen plume builds the Kerguelen Plateau; Ninetyeast Ridge from ~100 |
| ~84 | Zealandia (NZ, Campbell Plateau, Chatham Rise, Lord Howe Rise) separates |
| ~70 | Madagascar–India separate; Deccan at 66 accompanies India–Seychelles |
| ~96 | Australia–East Antarctica seafloor spreading begins in earnest (rifting from 132) |
| 34–23 | Tasman Gateway (33) and Drake Passage open; Antarctic Circumpolar Current established ~23 |

---

## 5. Pangaea

**Assembly** — three collisions and a long suturing:

- **Caledonian**, ~430 Ma: Baltica onto Laurentia, closing Iapetus; Avalonia already docked. → **Laurussia/Euramerica**.
- **Variscan/Hercynian**, Early Carboniferous: NW Africa onto SE Euramerica; the Rheic closes. Meseta and Mauritanide ranges.
- **Alleghanian/Ouachita**, Late Carboniferous–Permian: the southern Appalachians and the **Central Pangaean Mountains**, Himalayan in scale, peaking ~295 Ma and eroded to half height by the Lopingian.
- **Uralian**, Late Carboniferous–Permian: Kazakhstania onto Baltica; the Ural Ocean closes. → **Laurasia**.
- **~335 Ma**: the mass is coherent. Cimmeria rifts off Gondwana in the Early Permian, opening **Neo-Tethys** behind it as **Paleo-Tethys** closes ahead.

**Geography.** A C-shaped mass around the Tethys embayment, with **Panthalassa** everywhere else. Interior aridity on a continental scale; the **megamonsoon** peaks in the Triassic; the Central Pangaean Mountains cast a rain shadow across the northern interior. Coal deposition falls to its lowest in 300 Myr and is restricted to the *unattached* North and South China blocks — a fact worth surfacing in the app, because it is a case where the map explains the rock record directly.

**Breakup:**

| Ma | event |
|---|---|
| ~230 | first rifting, north-central Atlantic |
| ~200 | CAMP; the Triassic–Jurassic extinction |
| ~175 | rifting propagates Tethys→Pacific; central Atlantic opens |
| 150–140 | Gondwana fragments |
| 100–90 | Madagascar–India split; India accelerates to ~15 cm/yr; Coral and Tasman Seas open |
| 60–55 | Norwegian Sea; Greenland separates from Eurasia |
| ~50–40 | India–Asia collision begins |
| now | Red Sea and East African Rift are the continuing breakup |

---

## 6. Consequences the model already draws, and their cause here

| model quantity | cycle control |
|---|---|
| **sea level** | assembled → old cold deep sea floor → deep basins → low stand. Dispersed → young hot ridge volume → high stand. This is the first-order term; the ice term is second-order except in glacial maxima. |
| **climate mode** | assembled → icehouse (continental interiors, high albedo land at high latitude, low CO₂ from a small ridge system); dispersed → greenhouse. |
| **provinciality** | dispersed → endemism (our `region_taxa` should be *more* differentiated in the Cretaceous than in the Permian); assembled → cosmopolitanism (*Lystrosaurus* after the P–Tr). |
| **coal** | needs everwet equatorial lowlands; a supercontinent interior has none. |
| **evaporites** | need a restricted basin at a subtropical high; supercontinent margins make many. |

---

## Sources

- Wikipedia, *Supercontinent cycle*, *Rodinia*, *Gondwana*, *Pangaea*, *Laurentia*, *Baltica*, *Siberia (continent)*, *Avalonia*, *Terrane*, *List of orogenies* — retrieved 2026-07-26.
- IGCP Project 440 four-stage Rodinia breakup (via the Rodinia article).
- Merdith, A. S. et al. (2021), *Earth-Science Reviews* 214, 103477 — the rotation model the app actually uses.
- Farnsworth, A. et al. (2024), *Nature Geoscience* 17, 1109–1116 — future climate on the Pangaea Ultima reconstruction.

## Caution flags on the fetched material

Wikipedia's *List of orogenies* table contains several rows that are internally inconsistent and must **not** be copied into the model without a check: `Mozambique 2.97–2.65 Ga` (the Mozambique Belt is Neoproterozoic, ~800–650 Ma), `Napier 4.0 Ga` (older than the oldest rock), `Alpine 150–250 Ma`, `Himalayan 290–160 Ma`, `Mauritanide` listed under Neoproterozoic with a Carboniferous date. Where this file quotes a date it is from the body text of a topic article, not that table.
