# WP-02 · The Biosphere Through Deep Time

**Deep Research white paper 02** · drafted 2026-07-26 · status: **v1, actionable**
**Scope:** flora and fauna across deep time — what lived, how big, how it lived, where, and when — plus the province system that organises it, and how Tectonic Earth should represent all of it.
**Figures:** [`02-vegetation-through-time.svg`](../diagrams%20and%20illustrations/authored/02-vegetation-through-time.svg) · [`01-deep-time-master-chart.svg`](../diagrams%20and%20illustrations/authored/01-deep-time-master-chart.svg)
**Code:** [`modeling/paleobiogeography.py`](../modeling/paleobiogeography.py) · [`modeling/biome_model.py`](../modeling/biome_model.py) · [`modeling/taxa_db.py`](../modeling/taxa_db.py)

---

## Executive summary

The app's biota panels are curated **per named label**. That approach has already produced three distinct failure modes, all recorded in the project's own history: every ocean showing the same animals; oceans showing land animals; and *Proconsul*, an African ape, appearing on the East Tasman Plateau. Each was fixed where it was found. None was fixed as a class, because **there is no model of where a taxon belongs** — only a table of where someone put it.

This paper supplies three interlocking models to replace the table:

1. **A province model** (`paleobiogeography.py`) — given age, palaeolatitude, realm and (optionally) the continental block, return the biogeographic province, with an honest "no named province is established here" answer where the record does not support one.
2. **A vegetation model** (`biome_model.py`) — separate the *timeless* Whittaker climate cell from the *historical* question of what occupied it. 14 zones × 8 vegetation eras, so a new age automatically produces defensible vegetation instead of needing another hand-written row.
3. **A taxon database with attributes** (`taxa_db.py`) — 105 seed entries carrying size, habit, diet, realm, age range and provinces, which is what a card needs to say something specific and what an audit needs to check anything at all.

Together they make one testable prediction, stated in §1, that the existing `life_data.json` can be measured against.

---

## 1. The organising principle, and a prediction

Provinciality is set by **barriers** first and **gradients** second.

| control | terrestrial | marine |
|---|---|---|
| barrier | ocean, mountain chain, desert, ice sheet | deep basin (for shelf faunas), land bridge, thermal/salinity front |
| gradient | latitude → temperature and precipitation | latitude → SST; depth → light, pressure, oxygen |
| connection | land bridge, island chain, corridor | seaway, current, larval dispersal |

**Dispersal makes cosmopolitans; isolation makes endemics.** A supercontinent world has few terrestrial provinces and many marine ones (one long coast, many isolated interior seas). A dispersed world reverses it.

**The prediction:** our `region_taxa` should be **less** differentiated in the Permian and Triassic, and **more** differentiated in the Late Cretaceous and Neogene, than it is today. `paleobiogeography.provinciality(age)` returns this as a number (0.25 assembled → 0.6 partly assembled → 0.9 dispersed). If the curated data does the opposite, the data is wrong — and that is an audit anyone can run.

---

## 2. Marine provinces, and the taxa that mark them

**Ediacaran (635–538.8 Ma) — three assemblages, as much temporal as spatial.**
*Avalon* 575–565 (Mistaken Point; deep water, below the photic zone; fractal **rangeomorphs** — *Charnia*, *Fractofusus*), *White Sea* 560–550 (Russia and South Australia; the most diverse; *Dickinsonia* to **1.4 m**, *Kimberella* ~5 cm with a radula-like grazing apparatus, *Yorgia*, *Tribrachidium*), *Nama* 550–539 (Namibia; erniettomorphs, and the **first skeletons** — *Cloudina*, *Namacalathus*). Everything lives on or in a **microbial mat**; almost nothing burrows. *Cloudina* carries drill holes: the first predation.

**Cambrian (538.8–485.4 Ma) — two trilobite realms, and they map onto our reconstruction.**
*Olenellid Province* on Laurentia, Baltica and Siberia (*Olenellus*, *Holmia*, *Schmidtiellus*, *Kjerulfia*); *Redlichiid Province* on Gondwana (redlichiids); *Bigotinid Province* on peri-Gondwanan margins where both overlap. Phylogenetic work suggests a *uniform* trilobite fauna before the Pannotia breakup, with the two provinces emerging **as a consequence of it** — the map explains the biogeography, which is exactly the link a card should make. Lagerstätten to place on their own continents: Chengjiang and Qingjiang (~518 Ma, South China), Sirius Passet (Greenland/Laurentia), Emu Bay (Australia), Burgess Shale (~508 Ma, Laurentian margin), Orsten (Baltica).

**Ordovician — the GOBE, then endemism.** 497.05–467.33 Ma: marine orders double, families triple, installing the **Palaeozoic Evolutionary Fauna** (articulate brachiopods, bryozoans, crinoids, rugose and tabulate corals, cephalopods, graptolites, conodonts) that holds the shelves until the end-Permian. Late Ordovician diversification slows **because endemism rises**. Reef builders switch from Cambrian archaeocyath/microbial mounds to **stromatoporoid–tabulate–rugose** frameworks — "reef" is not one thing across deep time, and our reef icon and reef text should say which one.

**Devonian — Eastern Americas / Old World / Malvinokaffric.** The Malvinokaffric is a cold-water, high-southern-latitude Gondwanan realm: low diversity, **no reefs**, distinctive brachiopods and trilobites. **It is a marine realm; "Malvinokaffric flora" is a misnomer, and our entry of that name should be re-checked** — it was the taxon that exposed the reptile-icon fallback bug. Devonian reefs are the largest of the Phanerozoic and collapse at the Frasnian–Famennian (Kellwasser).

**Carboniferous–Permian — latitude bands.** Boreal (cool north), Tethyan (equatorial, warm, **fusulinid**-rich and reef-rich), Gondwanan/Austral (cool south, glacially influenced, *Eurydesma*). Fusulinid **presence** marks the warm realm and **absence** marks the cool ones — a clean diagnostic.

**Mesozoic — Boreal vs Tethyan, plus the Marine Revolution.** Boreal (*Buchia*, belemnites) against Tethyan (rudist reefs, larger benthic foraminifera). The boundary migrates with climate, and the **Viking** and **Hispanic Corridors** switch their exchange on and off — both already exist as app regions. The **Mesozoic Marine Revolution** (onset now in the Triassic, Anisian–Aalenian) is a predation revolution: durophagous decapods and stomatopods, teleosts, shell-boring gastropods, ptychodontoid sharks, plus placodonts, ichthyosaurs, plesiosaurs, pliosaurs and mosasaurs; prey respond with thicker sculptured shells, spines, **cementation** (oysters), **infaunalisation**, autotomy, and the retreat of stalked crinoids into deep water. The sessile epifaunal Palaeozoic shelf becomes an infaunal and pelagic world.

**Cenozoic — gateways.** The modern realms are a product of gateway tectonics: Tasman (~33 Ma) and Drake (crust 34–29, full ACC ~23 Ma) isolating Antarctica; Tethys closure (~19–14 Ma) ending the circumglobal tropical current; Messinian (5.96–5.33 Ma); Panama shoaling from ~10 Ma with the land route ~2.7 Ma; Bering ~5.5 Ma.

---

## 3. Terrestrial provinces, and the vegetation that defines them

The full matrix is the figure; the arguments are these.

**Before ~470 Ma there is no terrestrial biogeography.** Land is bare regolith with at most a microbial and possibly fungal crust — and, because there are no roots, **rivers are braided with no stable banks**. The app is right to refuse a biome map here, and the river model should reflect it too.

**Devonian — the first forests, and they are cosmopolitan.** *Wattieza* ~8 m (~385 Ma); **Archaeopteris to 30 m** with real wood and roots to ~1 m, forming the first forests; *Prototaxites*, a probable fungus to **8 m**, with no modern analogue — for ~130 Myr the largest organism on land was probably a fungus. First seeds: *Elkinsia*, Late Devonian. Deep rooting begins the weathering-and-burial CO₂ drawdown that ends in the Late Palaeozoic Ice Age. **A low-diversity flora spreads**, so provinces are weak — itself an informative fact.

**Carboniferous — the coal forests.** Arborescent lycopsids **>50 m tall and 2 m across** (*Lepidodendron*, *Sigillaria*) with *determinate* growth — grew as a pole, reproduced once, died. *Calamites* >10 m with a unifacial cambium. Medullosalean seed ferns; *Cordaites*.

**The Carboniferous rainforest collapse (~305 Ma) is a Euramerican event only** — and this is the single most important biogeographic fact for the app, because it means the *same age* needs *different vegetation on different blocks*. Glaciation and aridification fragment the equatorial rainforest; sea level falls ~100 m; CO₂ hits an all-time low; lycopsids crash and tree ferns and seed ferns replace them; labyrinthodont amphibians are hit hardest and **amniotes** radiate. In **Cathaysia**, Carboniferous-style everwet rainforest **persists to the end-Permian**. (Note: the classic "rainforest islands drove endemism" story is now contested — a 2018 study finds *increased* cosmopolitanism. State it as a hypothesis.)

**Permian — four floral provinces, the canonical case.**

| province | latitude | flora |
|---|---|---|
| **Angaran** | N mid-high (Siberia) | cordaitalean, deciduous, growth rings (*Rufloria*) |
| **Euramerican** | low tropical | seasonally dry: tree ferns, conifers, peltasperms |
| **Cathaysian** | low tropical | everwet, gigantopterids; **coal continues here alone** |
| **Gondwanan** | S mid-high | **Glossopteris** flora |

**Mixed floras are tectonically informative.** Cathaysian–Angaran mixing in North China from the early Late Permian is read as the *start* of collision between Siberia and the Sino-Korean–Tarim blocks; the Oman **Gharif** mixed flora is used to test Permian Pangaea fits. **This is a direct check on our reconstruction:** if our map juxtaposes two blocks at an age when their floras are still distinct, the map is wrong.

**Glossopteris in detail**, because it is the most iconic deep-time plant and the card should be right: a **seed fern** (Glossopteridales), long misclassified as a fern; woody trees to ~**30 m** with trunks to **80 cm**; tongue-shaped leaves 2–30 cm with **reticulate venation**; grew in **very wet soils** like a modern bald cypress and built the Gondwanan coal; Antarctic wood shows broad growth rings and an abrupt autumn shutdown taking **as little as a month**, implying conical, widely spaced crowns to exploit low-angle polar light; >70 species from India alone; rare peri-Gondwanan records (Morocco, Oman, Anatolia, New Guinea, Thailand, Laos) mark **mixed zones**. **Its distribution across five now-separated continents was Suess's evidence for Gondwana** — the historical origin of the very reconstruction we draw. It died out **before 252.3 Ma, ~350 kyr ahead of the marine extinction**, and was replaced by *Dicroidium*.

**Mesozoic — cosmopolitan again.** Conifers, cycads, Bennettitales, ginkgoes: **the same forest type from Greenland to Antarctica**, a real and drawable fact. High-latitude forest under a polar light regime is a biome with **no modern analogue**.

**Cretaceous–Cenozoic — provinciality returns.** Angiosperms from ~130 Ma; by the Late Cretaceous >50% of modern orders and ~70% of species; flowering trees overtake conifers. Grasses become ecologically important from **~40 Ma**; **C4 grasslands expand ~8 Ma**. Polar broadleaf-deciduous forest (*Metasequoia*) grows inside the Arctic Circle in the Eocene.

**The Great American Interchange** is the case study worth the app's space: South America isolated with notoungulates, litopterns, astrapotheres, pyrotheres, xenarthrans, sparassodonts, phorusrhacid terror birds; rafting arrivals of caviomorph rodents (~40 Ma) and primates (~36 Ma) from Africa; island-hopping from ~9 Ma; full interchange from **~2.7 Ma**; and a strikingly **asymmetric** outcome — sigmodontine rodents alone reach >80 South American genera while northward success is limited to xenarthrans, opossums, porcupines and one notoungulate. Then, at ~12 ka, nearly all the megafauna on both sides dies, with human arrival cited as pivotal.

---

## 4. What to build in the app

### B1 — Region tags become province queries
Replace `regionTaxaAt(name)`'s hand-curated keying with `province(age, lat, realm, block)`, keeping the curated lists as *overrides* where a named locality genuinely deserves its own fauna (Solnhofen, Muschelkalk, the WIS sub-basins, the Sloss cratonic seas). **The default stops being "one global list" and starts being "the province's list".**

### B2 — Realm-locking must be a property of the LOCALITY, not the label type
Two entries prove a strict lock is wrong: **Solnhofen** is a hypersaline lagoon whose fauna is marine, terrestrial *and* aerial; ***Hesperornis*** is a bird by clade and a marine diver by ecology. `MARINE_REGIONS` already deliberately excludes Solnhofen and the Hudson Seaway for this reason — that exception should become the documented rule.

### B3 — Carry attributes, not just names
Every taxon in `taxa_db.py` has size, habit and diet. A card that says "*Lepidodendron* — arborescent lycopsid, over 50 m tall, unbranched pole with determinate growth: it grew, reproduced once and died" is worth ten that say "*Lepidodendron*, plant". **The illustration work is already excellent (273 PhyloPic silhouettes); the text has not kept up.**

### B4 — Enforce the terrestrial gates in the biome shader, not just in the labels
`biome_model.py` encodes them: no canopy before ~385 Ma, no grassland before ~40 Ma, no C4 savanna before ~8 Ma, no vegetation at all before ~470 Ma. The shader's land colour should take an era parameter so a Silurian continent is *rock and thin damp crust*, not green.

### B5 — Two new card types, both cheap
- **Lagerstätten** as first-class point features riding their own continent's track (Burgess, Chengjiang, Sirius Passet, Solnhofen, Messel, Yixian, Rhynie, Mazon Creek, La Brea, Riversleigh). Each is a window into a whole biota and the app already has the machinery.
- **Biotic interchange events** (Great American Interchange, trans-Arctic, the Grande Coupure, *Lystrosaurus*' post-extinction spread) — they are moments when the map *causes* the biology, which is the app's whole thesis.

---

## 5. Honest limits to state on the cards

- Reconstructed biotas are **assemblages of what was preserved**, and preservation is biased toward shallow marine carbonate and away from uplands, deserts and the deep sea.
- Soft-bodied life is invisible except at the handful of Lagerstätten, so the Ediacaran and Cambrian pictures rest on a few dozen sites.
- Ranges shown are **known** ranges; a first appearance is a first *preservation*.
- Where the record supports no province, the app should say so rather than fall back to a global list silently. `Province.confidence == 'none'` exists for exactly that.

---

## Open items

- [ ] Verify the Devonian realm names against a primary source (stated here from general literature).
- [ ] Re-check the app's "Malvinokaffric flora" entry: realm, taxa, name.
- [ ] Run the §1 provinciality audit against `life_data.json`.
- [ ] Grow `taxa_db.py` beyond 105 seed entries; the thinnest interval is the mid-Cambrian to Silurian.
- [ ] Wire `province()` into `build/life.py` behind the existing curated overrides.

## Sources

Wikipedia *Ediacaran biota*, *Cambrian explosion*, *Great Ordovician Biodiversification Event*, *Carboniferous rainforest collapse*, *Glossopteris*, *Evolutionary history of plants*, *Mesozoic marine revolution*, *Great American Interchange*, *Biogeographic realm* (retrieved 2026-07-26). Permian phytogeography: Wang, *Cathaysia flora and mixed Cathaysian–Angaran floras*; Cleal & Thomas / Wagner on Euramerican–Cathaysian relations, *Earth-Sci. Rev.* 2007; Berthelin et al., Oman Gharif mixed palaeoflora, *Palaeo-3* 2003; Naugolnykh, western extension of the Angaran province, *J. Asian Earth Sci.* 2009. Pillola (1991) for the Bigotinid Province. Vermeij for the Mesozoic Marine Revolution.
