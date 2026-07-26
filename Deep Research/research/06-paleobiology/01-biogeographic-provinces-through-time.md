# Biogeographic Provinces Through Deep Time

**Domain:** paleobiology / biogeography · **Status:** first pass, 2026-07-26
**Feeds directly:** `build/life.py` `region_taxa` and `MARINE_REGIONS`, `build/add_*_life.py`, `build_webdata.region_tags()`, the biota panel
**The problem this solves:** the app currently assigns taxa to a *named label* (a plate, a sea, a mountain range) by hand, region by region. That does not scale and it leaves gaps — 32 of 55 marine labels once fell through to a single global list. What is needed is a **model**: given (age, palaeolatitude, palaeolongitude, realm, marine/terrestrial), return the *province*, and from the province the characteristic biota. This file is the evidence base for that model.

---

## 1. The principle

Provinciality is set by **barriers** and **gradients**, in that order:

| control | terrestrial | marine |
|---|---|---|
| **barrier** | ocean, mountain chain, desert, ice sheet | deep ocean basin (for shelf faunas), land bridge, salinity/temperature front |
| **gradient** | latitude → temperature and precipitation | latitude → SST; depth → light, pressure, oxygen |
| **connection** | land bridge, island chain, corridor | seaway, current, larval dispersal |

The single most useful generalisation: **dispersal makes cosmopolitans; isolation makes endemics.** A supercontinent world (Permian, Triassic) has few terrestrial provinces and many marine ones (one long coastline, many isolated shelf seas). A dispersed world (Cretaceous, Neogene) reverses it — many terrestrial provinces, fewer marine ones once the ocean gateways connect.

**This is a testable prediction for the app.** Our `region_taxa` should be *less* differentiated in the Permian and *more* differentiated in the Late Cretaceous and Neogene than it is today. If the current data does the opposite, the data is wrong.

---

## 2. Marine provinces, interval by interval

### Ediacaran (635–538.8 Ma) — three assemblages, and they are as much temporal as spatial

| assemblage | age (Ma) | type locality | character |
|---|---|---|---|
| **Avalon** | 575–565 | Mistaken Point, Newfoundland; Charnwood, England | deep water, below photic; fractal **rangeomorphs** (*Charnia*, *Fractofusus*); suspension/osmotrophic |
| **White Sea** | 560–550 | White Sea, Russia; Ediacara Hills, S Australia | shallow, highest diversity; *Dickinsonia* (to 1.4 m), *Kimberella* (~5 cm, radula-like grazer), *Yorgia*, *Spriggina*, *Tribrachidium* |
| **Nama** | 550–538.8 | Namibia | sandy, 3-D preservation; erniettomorphs (*Ernietta*, *Pteridinium*, *Rangea*); the **first skeletons**, *Cloudina* and *Namacalathus* |

Whether these are three faunas or one fauna in three environments is unresolved — probably both. **Model note:** the app already has a Nama Sea region; Avalon and White Sea deserve the same treatment, and the assemblage is a better organising unit than the continent here.

Everything lives on or in a **microbial mat**. Nothing burrows deeply. That is why the Ediacaran sea floor should be drawn (and described) as a sealed, textured surface, and why *Cloudina* boreholes — the first predation — matter.

### Cambrian (538.8–485.4 Ma) — two trilobite realms

The cleanest deep-time province signal in the whole record, and it maps directly onto our reconstruction:

| province | continents | endemic marker |
|---|---|---|
| **Olenellid** | Laurentia, Baltica, Siberia | olenellid trilobites (*Olenellus*, *Holmia*, *Schmidtiellus*, *Kjerulfia*) |
| **Redlichiid** | Gondwana (incl. South China, Australia, Antarctica) | redlichiid trilobites |
| **Bigotinid** (intermediate) | peri-Gondwanan margins | overlap of both |

Pandemic in both: ellipsocephaloids, eodiscids. Phylogenetic work suggests a *uniform* trilobite fauna before the Pannotia breakup, with the two provinces emerging **as a consequence of that breakup** — i.e. our own map explains the biogeography, which is exactly the kind of link the app should surface on a card.

Lagerstätten to place: **Chengjiang** (~518 Ma, Yunnan, South China), **Sirius Passet** (Early Cambrian, North Greenland = Laurentia), **Emu Bay** (Australia = Gondwana), **Qingjiang** (~518 Ma, Hubei), **Burgess Shale** (~508 Ma, Laurentian margin), **Orsten** (Late Cambrian, Sweden = Baltica). Each is a *point* on a specific continent and should ride that continent's track.

### Ordovician (485.4–443.8 Ma) — the GOBE, then endemism

The **Great Ordovician Biodiversification Event**, 497.05–467.33 Ma (~30 Myr): marine orders doubled, families tripled. It installed the **Palaeozoic Evolutionary Fauna** — articulate brachiopods, bryozoans, crinoids, rugose/tabulate corals, cephalopods, graptolites, conodonts — which then held the shelves until the end-Permian.

Provinciality was *high* in the Ordovician, and it rose through the period: the continents were maximally scattered across latitude, with Laurentia on the equator, Baltica in southern mid-latitudes and Gondwana straddling the South Pole. Late Ordovician diversification is explicitly described as slowing **because endemism increased**. Named faunal realms of the period conventionally track that dispersion.

Reef builders switched from Cambrian archaeocyath/microbial mounds to **stromatoporoid–tabulate–rugose** frameworks — a change our reef icon and reef descriptions should honour, since "reef" is not one thing across deep time.

### Silurian–Devonian — the Old Red Sandstone continent and the Malvinokaffric realm

With Laurussia assembled, the marine realms of the Devonian are conventionally:

- **Eastern Americas Realm** — the Appalachian basin and the epeiric seas of eastern Laurussia.
- **Old World Realm** — Europe, North Africa, Asia.
- **Malvinokaffric Realm** — cold-water, high southern latitude Gondwana (South America, southern Africa, the Falklands/Malvinas — hence the name). Low diversity, no reefs, distinctive brachiopod and trilobite assemblages.

**Model note.** The app already carries a *Malvinokaffric flora* entry (it was the taxon that exposed the reptile-fallback icon bug). The realm is chiefly a **marine** concept; a "Malvinokaffric flora" is at best loose. Worth re-checking that entry's realm and taxa.

Devonian reefs are the largest of the Phanerozoic (stromatoporoid–coral), and they collapse at the Frasnian–Famennian. The reef crisis is a first-class event that our reef biomes should reflect.

### Carboniferous–Permian — marine provinces become latitude bands

With Pangaea assembling, the marine world reorganises: one long shelf, plus isolated interior seas. Conventional provinces are **Boreal** (northern, cool), **Tethyan** (equatorial, warm, fusulinid- and reef-rich), **Gondwanan/Austral** (southern, cool, glacially influenced). The **fusulinid foraminifera** are the classic Tethyan warm-water marker; their absence in Gondwanan sequences is a diagnostic.

Named restricted basins with their own biotas: **Zechstein Sea** (Late Permian, hypersaline, N Europe), **Delaware Basin** (Capitan reef complex, Guadalupian, Texas), **Muschelkalk Sea** (Middle Triassic, Germanic basin).

### Mesozoic — Boreal vs Tethyan, and the Marine Revolution

The dominant Jurassic–Cretaceous marine division is **Boreal** (cool, northern; belemnite- and *Buchia*-dominated) against **Tethyan** (warm, equatorial; rudist reefs, ammonite-rich, larger benthic forams). The boundary migrates with climate, and the *Viking Corridor* and *Hispanic Corridor* are the gateways whose opening and closing switch the two on and off — both already exist as app regions.

The **Mesozoic Marine Revolution** (onset now pushed back into the Triassic, Anisian–Aalenian, running through the Cretaceous) is a *predation* revolution, and it restructured the benthos:

- **predators:** durophagous decapods and stomatopods, teleosts, shell-boring gastropods, ptychodontoid sharks; plus placodonts, ichthyosaurs, plesiosaurs, pliosaurs, mosasaurs.
- **prey responses:** thicker and more sculptured shells, spines, **cementation** (oysters), **infaunalisation** (burrowing), autotomy, and the retreat of stalked crinoids into deep water.
- **net effect:** the Palaeozoic-style sessile epifaunal shelf gives way to an infaunal and pelagic world. Brachiopods decline; bivalves rise.

Alongside it, the **plankton revolution** — coccolithophores (~201 Ma, hence the modern clear blue ocean; already in the app's sea-colour model), planktonic foraminifera, dinoflagellates, and later diatoms — changed the ocean's carbon pump and its colour.

### Cenozoic — modern realms assemble as gateways open and close

The modern marine realm system (12 WWF realms) is a product of Cenozoic gateway tectonics:

| gateway | event | consequence |
|---|---|---|
| Tasman Gateway | opens ~33 Ma | with Drake, isolates Antarctica |
| Drake Passage | crust 34–29 Ma; fully open ~23 Ma | **Antarctic Circumpolar Current** → Antarctic glaciation, a thermally isolated Southern Ocean realm |
| Tethys closure / Gomphotherium land bridge | ~19–14 Ma | severs Indo-Pacific from Atlantic; ends the circumglobal tropical current |
| Messinian Salinity Crisis | 5.96–5.33 Ma | Mediterranean desiccates; endemic biota annihilated and recolonised |
| Isthmus of Panama | shoaling from ~10 Ma, land route ~2.7 Ma (dating contested) | Atlantic/Pacific marine provinces split; **Great American Interchange** on land |
| Bering Strait | opens ~5.5–5.3 Ma | trans-Arctic biotic interchange |

---

## 3. Terrestrial provinces, interval by interval

### Before the Devonian
There is no terrestrial biogeography worth the name. Land is microbial crust, then (Ordovician, from ~470 Ma cryptospores) liverwort-grade plants, then (Silurian) the first vascular plants. **The app is right to describe pre-Devonian land as bare regolith with microbial crusts and to refuse a biome map there.**

### Devonian — the first forests
- **Wattieza** (~385 Ma), ~8 m, the first tree-form.
- **Archaeopteris** (Late Devonian), to **30 m**, real wood, formed the first forests; roots to ~1 m depth.
- **Prototaxites** — giant fungal (probably) columns to 8 m, an organism with no modern analogue; the app has a bespoke icon for it, correctly.
- First seeds: **Elkinsia**, Late Devonian.

Provinces are weak; the flora is broadly cosmopolitan across Laurussia and Gondwana, which is itself informative — a low-diversity flora spreads.

### Carboniferous — coal forests, and the first real floral provinces
Equatorial Euramerican wetlands: arborescent lycopsids (**Lepidodendron**, **Sigillaria**) to **>50 m tall and 2 m across**, with *determinate* growth; **Calamites** horsetails >10 m; medullosalean seed ferns; **Cordaites**. These are the coal.

**Carboniferous rainforest collapse, ~305 Ma** (end-Moscovian into early Kasimovian): glaciation and aridification fragment the equatorial rainforest into shrinking islands. Sea level falls ~100 m; CO₂ hits an all-time low. Lycopsids crash and are replaced by **tree ferns** and seed ferns. Labyrinthodont amphibians are hit hardest (they must return to water); **amniotes** — synapsids and sauropsids — do better in the drier world and radiate, becoming substantially larger. Note the article flags a 2018 study finding *increased* cosmopolitanism rather than the classic endemism-by-fragmentation story: **treat "rainforest islands drove endemism" as contested**.

Critically for the map: **the collapse is a Euramerican event.** In **Cathaysia** (China), Carboniferous-style everwet rainforest **persists until the end of the Permian**. The same age therefore needs different vegetation on different blocks — which is precisely what a province model buys us and a global biome table cannot express.

### Permian — four floral provinces, and this is the canonical case

| province | palaeolatitude | flora |
|---|---|---|
| **Angaran** | northern mid-to-high (Siberia) | cordaitalean-dominated, deciduous, growth rings; cool temperate |
| **Euramerican** | low, tropical (Laurussia) | seasonally dry tropical; tree ferns, conifers, peltasperms |
| **Cathaysian** | low, tropical (N and S China) | everwet tropical; gigantopterids; **coal continues here when it stops everywhere else** |
| **Gondwanan** | southern mid-to-high | **Glossopteris** flora |

- **Mixed floras exist and are tectonically informative.** Cathaysian–Angaran mixing from the early Late Permian in North China is read as the *start of collision* between Siberia and the Sino-Korean–Tarim blocks. The Oman **Gharif** mixed flora is used to test Permian Pangaea fits. Migratory interchange between Angaran, Euramerican and Cathaysian floras is now documented, overturning the older picture of sealed provinces. **This is a direct check on our reconstruction**: if our map puts two blocks adjacent at an age when their floras are still distinct, the map is wrong.

**Glossopteris**, in detail, because it is the single most iconic deep-time plant and our card should be right:
- Glossopteridales, a **seed fern** (pteridosperm), not a fern — long misclassified.
- Woody trees and shrubs; trunk to **80 cm** diameter, height likely to **30 m**; softwood resembling Araucariaceae.
- Tongue-shaped leaves with **reticulate venation**, 2–30 cm.
- Grew in **very wet soils**, like modern bald cypress; formed the Gondwanan coal swamps.
- **Polar forests**: broad growth rings from Antarctica show strong spring–summer growth and abrupt cessation, in as little as a month. Inferred **conical, widely spaced** crowns to exploit low-angle polar light. Some populations mixed evergreen and deciduous.
- Range: Early Permian (~298.9 Ma) to the end-Permian (~251.9 Ma); >70 species from India alone. Rare peri-Gondwanan records from Morocco, Oman, Anatolia, New Guinea, Thailand, Laos mark **mixed zones**.
- **Its distribution across five now-separated continents was Suess's evidence for Gondwana** — a story the app should tell, since it is the historical origin of the very reconstruction we draw.
- Died out **before 252.3 Ma**, ~350 kyr *ahead of* the marine extinction. Replaced by *Dicroidium* in the Triassic.

### Triassic–Jurassic
*Dicroidium* flora in Gondwana; conifers, cycads, Bennettitales, ginkgoes globally. Pangaea's breakup begins to build provinces again but the Jurassic flora remains broadly cosmopolitan — a real and drawable fact: **the same forest type from Greenland to Antarctica**.

### Cretaceous — angiosperms and the return of provinciality
Angiosperms originate and diversify from ~130 Ma; by the Late Cretaceous >50% of modern angiosperm orders exist and the clade is ~70% of species. Flowering trees overtake conifers. As Gondwana fragments, **each fragment starts its own experiment** — the origin of the modern Neotropical, Afrotropical, Australasian and Antarctic floras.

### Cenozoic — the modern realms
Eight WWF terrestrial realms: Palearctic (54.1 M km²), Nearctic (22.9), Afrotropical (22.1), Neotropical (19.0), Australasian (7.6), Indomalayan (7.5), Oceanian (1.0), Antarctic (0.3). Every boundary is a tectonic or climatic fact:

- **Wallace Line** — the deep-water Makassar/Lombok straits, never bridged at low sea level; Australasian vs Indomalayan.
- **Australasian isolation** — since ~35 Ma, producing the marsupial fauna.
- **Great American Interchange** — the definitive case study, and worth the app's space:
  - South America isolated through most of the Cenozoic: **notoungulates, litopterns, astrapotheres, pyrotheres** (native ungulates), **xenarthrans** (sloths, armadillos, anteaters), **sparassodonts** (metatherian predators), **phorusrhacid terror birds**, sebecid crocodilians, giant caimans.
  - Rafting arrivals long before the isthmus: **caviomorph rodents ~40 Ma** and **primates ~36 Ma**, both from Africa.
  - Island-hopping both ways from ~9 Ma (ground sloths reach N America), procyonids south ~7.3 Ma, terror birds possibly north by ~5 Ma.
  - **Full interchange accelerates ~2.7 Ma** (Piacenzian).
  - **Asymmetric outcome:** northern taxa dominate. Sigmodontine rodents alone reach >80 South American genera; canids and cervids diversify; much of the endemic South American fauna is extinguished. Northward success is limited to xenarthrans (ground sloths in ≥8 lineages, *Megalonyx* to Yukon/Alaska), opossums, porcupines, and one notoungulate (*Mixotoxodon*).
  - Explanation offered: North America's ~6× larger evolutionary arena, connected to Eurasia, versus South America connected only to Antarctica and Australia.
  - **Late Pleistocene, ~12 ka:** nearly all of the megafauna on both sides dies, with human arrival cited as pivotal.
- **Grasslands.** Grasses become ecologically important from ~40 Ma; C4 grasslands expand in the late Miocene under low CO₂ and seasonal aridity. **The app's rule of no grassland before the Cenozoic is correct** and should be tightened further: no *C4* grassland before ~8 Ma.

---

## 4. What to build from this — the province model

A function `province(age, lon, lat, realm)` returning a province name plus a confidence, implemented as:

1. **Marine:** classify by palaeolatitude band (Boreal / warm-temperate / Tethyan-tropical / Austral) *and* by basin connectivity from the plate model. Cross-check against the named realms above for each interval.
2. **Terrestrial:** classify by (a) which landmass the point is on (already available from `resolve_to_landmasses`), (b) palaeolatitude band, (c) the interval's known province list.
3. **Return "unknown" honestly** where the record does not support a province — a global fallback is fine, silent fabrication is not.

This replaces per-label hand-curation with a system, which is the standing rule. Draft implementation: `modeling/paleobiogeography.py`.

---

## Sources

- Wikipedia: *Ediacaran biota*, *Cambrian explosion*, *Great Ordovician Biodiversification Event*, *Carboniferous rainforest collapse*, *Glossopteris*, *Evolutionary history of plants*, *Mesozoic marine revolution*, *Great American Interchange*, *Biogeographic realm*, *Phytogeography* — retrieved 2026-07-26.
- Permian phytogeography: Wang (Cathaysia flora and mixed Cathaysian–Angaran floras, *Acta Geologica Sinica*); Cleal & Thomas / Wagner on Euramerican–Cathaysian relations (*Earth-Science Reviews* 2007); Berthelin et al., Oman Gharif mixed palaeoflora (*Palaeo-3* 2003); Naugolnykh, western extension of the Angaran province (*J. Asian Earth Sci.* 2009).
- Cambrian provinces: Pillola (1991) Bigotinid Province; olenellid/redlichiid province literature via the Baltic olenellid work.
- Vermeij, G. J. — the Mesozoic Marine Revolution concept.

## Open items

- [ ] Verify the Devonian realm names (Eastern Americas / Old World / Malvinokaffric) against a primary source — they are stated here from general literature, not from a fetched article.
- [ ] Re-check the app's "Malvinokaffric flora" entry: realm, taxa, and whether the name should be marine.
- [ ] Build `modeling/paleobiogeography.py`.
- [ ] Audit `region_taxa` for the prediction in §1 (Permian under-differentiated? Cretaceous over-generalised?).
