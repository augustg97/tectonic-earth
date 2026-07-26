# Biome Evolution and Ecosystem Structure Through Deep Time

**Domain:** ecosystems / biomes · **Status:** first pass, 2026-07-26
**Feeds directly:** the terrain shader's biome colour and treeline, `life.py` biome samples, biome labels in `features.py`
**Model:** [`modeling/biome_model.py`](../../modeling/biome_model.py) · **Figure:** [`02-vegetation-through-time.svg`](../../diagrams%20and%20illustrations/authored/02-vegetation-through-time.svg)

---

## 1. The separation that makes this tractable

A biome is two independent things and the app currently conflates them:

- **A climate cell** — where a place sits on the temperature/precipitation plane. This is *physics*, and it is timeless. 25 °C and 2500 mm is an everwet tropical lowland in the Carboniferous and in the Holocene alike.
- **An occupancy** — what was actually growing in that cell at that moment, which depends entirely on what had evolved. The same cell is a **lycopsid coal swamp** at 310 Ma, a **gigantopterid everwet forest** at 270 Ma, a **cycadophyte–conifer rainforest** at 200 Ma, a **paratropical rainforest** at 100 Ma, and a **dipterocarp rainforest** today.

Separating them turns a hand-written table into a model: 14 Whittaker zones × 8 vegetation eras, and any new age produces defensible vegetation without new authoring. That is the whole content of `biome_model.py`.

---

## 2. The vegetation eras, and what defines each

| era | Ma | the structural fact |
|---|---|---|
| **pre-vegetation** | >470 | Land is stone. Bare regolith, microbial and possibly fungal crust on damp surfaces. **No roots, so rivers are braided with no stable banks** — a fact the drainage model should honour, not just the colour. |
| **early vascular** | 470–385 | Rhyniophyte- and zosterophyll-grade plants, centimetres to a metre, in damp lowlands only. *Cooksonia*, *Baragwanathia*, *Aglaophyton* (with the earliest arbuscular mycorrhizae — land plants have always been partly fungal). **No canopy**, so no forest zone exists. |
| **first forests** | 385–323 | *Wattieza* ~8 m, then **Archaeopteris to 30 m** with real wood and roots to ~1 m. *Prototaxites*, a probable fungus to **8 m**. First seeds (*Elkinsia*). Deep rooting starts the weathering-and-burial CO₂ drawdown. |
| **coal forests** | 323–304 | Arborescent lycopsids **>50 m and 2 m across**, with *determinate* growth — grew as a pole, reproduced once, died. *Calamites* >10 m. O₂ near its ~30% Phanerozoic peak. |
| **Permian** | 304–252 | Post-collapse. **Province matters more than climate zone here** — see §4. |
| **Mesozoic gymnosperm** | 252–130 | Conifers, cycads, Bennettitales, ginkgoes; **strikingly cosmopolitan**, the same forest type from Greenland to Antarctica. |
| **angiosperm radiation** | 130–40 | Flowering trees overtake conifers; **no grassland yet**; paratropical broadleaf forest reaches both poles in the Eocene. |
| **modern** | 40–future | Grasses become ecologically important ~40 Ma; **C4 grasslands from ~8 Ma**. Tundra exists only once there is polar ice. |

---

## 3. Biomes with no modern analogue — and the app should draw them as such

Four of these are real, well-evidenced, and currently drawn as their nearest modern relative, which is wrong:

1. **Polar forest.** Broad-leaved deciduous and deciduous-conifer forest inside the Arctic and Antarctic Circles, through months of total darkness. *Glossopteris* in Permian Antarctica shows broad growth rings and an abrupt autumn shutdown taking **as little as a month**, implying conical, widely spaced crowns to exploit low-angle light. *Metasequoia* does the same job in the Eocene Arctic. **Not tundra, not taiga — a closed high-latitude forest.**
2. **The lycopsid coal swamp.** A canopy of 50-metre poles with determinate growth over standing water, with no true soil profile and an understorey of tree ferns and seed ferns. Nothing today is structured like it.
3. **Mammoth steppe.** Cold, dry, *productive* grassland across Beringia and northern Eurasia during the glacials, supporting a megafaunal biomass no modern tundra can. It vanished with the ice.
4. **The Ediacaran mat-ground sea floor.** A sealed, textured microbial surface, almost unburrowed, on which everything either lay or stood. The Cambrian substrate revolution destroyed it, and the app's sea floor should look and read differently before and after.

---

## 4. Where climate is not enough: the Permian

The Permian is the case that proves a biome model alone cannot do the job. At the *same climate cell*, four floral provinces coexisted, and the differences are tectonic, not climatic:

| province | flora | the point |
|---|---|---|
| Cathaysian | gigantopterid everwet forest | **coal continues here alone**; the ~305 Ma rainforest collapse was a **Euramerican** event and Cathaysian rainforest survives to the end-Permian |
| Euramerican | tree ferns, conifers, peltasperms | the collapse's victim; increasingly seasonally dry |
| Angaran | cordaitalean, deciduous, growth rings | cool temperate, seasonal |
| Gondwanan | *Glossopteris* swamp forest | wet-soil seed-fern forest; the source of Gondwanan coal |

So `biome_model.biome()` gives the *structure* and `paleobiogeography.province()` gives the *identity*, and a card needs both. The Permian entry in `biome_model.py` says so explicitly rather than pretending to resolve it.

---

## 5. Ecosystem structure — what changes, and when

Beyond vegetation, four structural transitions reshape whole ecosystems and are each drawable or describable:

| transition | when | what changes |
|---|---|---|
| **Cambrian substrate revolution** | 539–520 Ma | burrowing destroys the microbial mat-ground; sediment becomes mixed and oxygenated; stromatolites decline sharply |
| **Reef builder turnover** | repeatedly | archaeocyath + microbial (Cambrian) → stromatoporoid–tabulate–rugose (Ordovician–Devonian, largest reefs of the Phanerozoic) → **collapse at the Frasnian–Famennian** → sponge/microbial (Triassic recovery) → scleractinian coral (Jurassic) → **rudist bivalve** (Cretaceous) → scleractinian again (Cenozoic). "Reef" is never one thing. |
| **Mesozoic Marine Revolution** | Triassic → Cretaceous | predation drives thicker shells, spines, cementation, **infaunalisation**, and the retreat of stalked crinoids into deep water; the sessile epifaunal Palaeozoic shelf becomes infaunal and pelagic |
| **Plankton revolution** | ~220 Ma → | coccolithophores, planktonic foraminifera, dinoflagellates, later diatoms. **The carbonate factory moves off the shelf onto the deep sea floor at ~201 Ma** — a change in what the abyss is made of, and the same date as the ocean-colour change |

---

## 6. Terrestrial food-web milestones worth a card

- **~470 Ma** first embryophyte spores; land is colonisable.
- **~430 Ma** first vascular plants; first terrestrial arthropod detritivores.
- **~385–375 Ma** first forests; first true soils; rivers gain banks.
- **~360 Ma** tetrapods on land.
- **~320 Ma** amniotes — reproduction freed from standing water. After the ~305 Ma rainforest collapse they radiate and get substantially larger while labyrinthodonts decline.
- **~250 Ma** the first fully terrestrial vertebrate food webs with large herbivores *and* large carnivores throughout.
- **~130 Ma** angiosperms; co-evolution with pollinating insects.
- **~40 Ma → ~8 Ma** grasses, then C4 grasslands and the grazing megafauna that go with them; hypsodont teeth appear in response to grass phytoliths and dust.

---

## Implications for Tectonic Earth

1. **Gate the shader's land colour by era.** A Silurian continent should read as rock with thin damp crust in the lowlands, not green. The gates are already encoded: no vegetation before ~470 Ma, no canopy before ~385, no grassland before ~40, no C4 savanna before ~8.
2. **Name the vegetation, not the modern biome.** "Lycopsid coal swamp" is both more accurate and far more interesting than "tropical rainforest", and `biome_model.py` returns it for free.
3. **Rivers before roots should be braided.** The drainage field currently applies the same channel model at every age.
4. **Reef descriptions must state which reef.** A single "reef" biome sample spanning 540 Myr is wrong six times over.
5. **The four no-analogue biomes deserve their own cards** — they are among the most genuinely surprising things the app can show.

---

## Sources

Wikipedia *Evolutionary history of plants*, *Carboniferous rainforest collapse*, *Glossopteris*, *Mesozoic marine revolution*, *Ediacaran biota*, *Cambrian explosion* (retrieved 2026-07-26). Whittaker, R. H., *Communities and Ecosystems* (1975) for the climate-cell classification. Permian phytogeography as cited in `research/06-paleobiology/01-biogeographic-provinces-through-time.md`.
