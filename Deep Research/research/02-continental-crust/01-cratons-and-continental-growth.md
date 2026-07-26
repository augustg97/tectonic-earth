# Continental Crust: Cratons, Orogens and Continental Growth

**Domain:** continental crust · **Status:** first pass, 2026-07-26
**Feeds:** `precambrian.py` (generated craton blobs), `build_synthetic.pre_placement()`, orogen labels in `features.py`, `feature_art.py` cross-sections
**Model:** [`modeling/paleogeography.py`](../../modeling/paleogeography.py)

---

## 1. Why continents are permanent and ocean floor is not

| | continental | oceanic |
|---|---|---|
| density | ~2.7 g/cm³ | ~3.0 g/cm³ |
| thickness | 30–70 km | 7 ± 1 km |
| composition | felsic (granodioritic average), "sial" | mafic basalt/gabbro, "sima" |
| oldest surviving | **4.03–3.58 Ga** (Acasta Gneiss, Slave Craton) | ~180–200 Ma |

Continental crust is too buoyant to subduct wholesale, so it accumulates. Ocean floor is denser than the mantle it floats on once it has cooled ~20 Myr, so it is recycled on a ~180 Myr conveyor. **This one density contrast produces the entire structure of the app's world**: it is why land is high and ocean is low, why a supercontinent can reassemble the same crust repeatedly, and why deep-time sea floor can only ever be modelled while deep-time continents can be reconstructed.

---

## 2. The anatomy of a continent

- **Craton** — a stabilised Archaean–Palaeoproterozoic nucleus with a thick, cold, chemically depleted lithospheric keel (to ~250 km). Effectively unsubductable and mechanically inert; it deforms only at its edges.
  - **Shield** — where the craton's basement is exposed.
  - **Platform** — where the same basement is buried under a thin flat-lying sedimentary cover.
- **Orogen** — a belt of deformed crust marking where something collided. Orogens are how continents *grow* and how they *join*.
- **Terrane** — a fault-bounded crustal fragment with a history incompatible with its neighbours. Recognised by fault boundaries, stratigraphic incompatibility, **faunal mismatch** and **palaeomagnetic mismatch**; overlap formations and stitching plutons date the docking.
- **Passive margin** — a rifted edge, thermally subsiding, accumulating a sedimentary wedge. Becomes an *active* margin only when subduction initiates there, which is what closes an ocean.

**Model note.** The app's Precambrian landmasses are *generated*, not cut from the modern DEM (`precambrian.py`), and the tuning traps recorded there follow directly from this anatomy: strong collision uplift paints geometric scars because overlapping discs intersect on circular arcs, and strongly anisotropic fold noise turns a whole shield into corduroy. The physical reason both look wrong is that **a craton interior is inert** — the relief belongs at the edges, in the orogens, not across the shield.

---

## 3. Laurentia as the worked example

The best-documented craton assembly, and the core of Rodinia:

| component | age |
|---|---|
| Slave, Superior, Wyoming, Hearne, Rae, Nain (Archaean nuclei) | 4.03–2.5 Ga |
| **Trans-Hudson** orogeny — "likely similar to the modern Himalayas" | ~1.8 Ga |
| Penokean | 1850–1840 Ma |
| Yavapai | 1710–1680 Ma |
| Mazatzal | 1675–1600 Ma |
| Picuris | 1490–1450 Ma |
| **Midcontinent Rift** — the craton nearly split; Keweenawan flood basalts, copper | ~1.1 Ga |
| **Grenville** | 1300–950 Ma |

Then its Phanerozoic: equatorial and tectonically stable through the early Palaeozoic, covered by a warm epicontinental sea only ~60 m deep, with a passive western margin and an active eastern one (Taconic). Merges with Baltica and Avalonia at ~420 Ma; the western margin flips from passive to convergent; Ancestral Rockies in the Pennsylvanian; Alleghanian builds the Central Pangaean Mountains; then the Cordilleran terrane collage, the Western Interior Seaway, Sevier, Laramide, Basin and Range, and Baja rifting away in the Miocene.

**Two facts in there that the app should surface but currently does not:** a continental interior can be flooded to only ~60 m and still be *sea* for tens of millions of years (which is why epicontinental seas are so hard for a 20 km DEM to resolve, and why the `epeiric.py` seeding exists); and a craton can very nearly rift apart and then simply stop (the Midcontinent Rift), leaving a 1000-km-long failed structure that still shows in gravity today.

---

## 4. Continental growth: how crust is added

1. **Arc magmatism** — new juvenile crust at subduction zones. The dominant mode.
2. **Terrane accretion** — pre-existing fragments swept up and welded on. The Cordillera of western North America is a collage of dozens (Wrangellia, Stikinia, Alexander, Cache Creek, Sonomia).
3. **Continental collision** — thickening rather than addition, but it stabilises and cratonises.
4. **Underplating** — mafic magma ponded at the Moho, thickening crust from below; associated with LIPs.

Growth is offset by **crustal recycling**: sediment subduction, subduction erosion, and delamination of dense lower crust. Whether total continental volume has grown steadily, grown episodically, or been near-constant since the Archaean with only recycling changing is an open question — episodic peaks in zircon age spectra at ~2.7, ~1.9 and ~1.1 Ga are either growth pulses or **preservation** pulses tied to the supercontinent cycle, and that ambiguity is itself worth a card.

---

## 5. Orogen types, and why the app's cross-sections need more than one

`feature_art.py` already distinguishes an Andean arc from a continental collision, which is the most important split. The full set worth carrying:

| type | driver | example | signature |
|---|---|---|---|
| **accretionary / Cordilleran** | ocean–continent subduction | Andes, Cordillera | arc batholith, fore-arc basin, accreted terranes, no suture |
| **collisional** | continent–continent | Himalaya, Alps, Variscan, Grenville | suture with ophiolites, crustal doubling, high plateau, foreland basin |
| **intracratonic** | far-field stress on old weakness | Alice Springs, Petermann | no ocean involved at all; basement-cored ranges far from any margin |
| **transpressional** | oblique convergence | Transverse Ranges | strike-slip with local uplift |

**A high plateau requires collision.** Tibet exists because India is still pushing. That constraint is a useful check on any deep-time frame that draws one.

---

## 6. Open questions worth flagging on cards

- The **Rodinia configuration** is genuinely disputed (SWEAT / AUSWUS / AUSMEX / Missing-Link / revised Missing-Link) — see `research/01-plate-tectonics/01-supercontinent-cycle.md`.
- **Pannotia may never have existed** as a coherent mass.
- **When plate tectonics started** — estimates range from the Hadean to the Neoproterozoic; the app's 1000 Ma floor sits comfortably inside the modern-style regime under any of them, which is a reason the floor is well chosen.
- **Whether continental volume grew or was recycled** (§4).

---

## Sources

Wikipedia *Laurentia*, *Baltica*, *Siberia (continent)*, *Terrane*, *Oceanic crust*, *List of orogenies* (retrieved 2026-07-26; the orogeny **table** contains corrupt rows and was not used for dates). Craton/orogen anatomy is standard textbook material and should be re-sourced to a named text before any of it is quoted in the app.

## Open items

- [ ] Source the craton/orogen anatomy to a citable text rather than general knowledge.
- [ ] Add the four orogen types to `feature_art.py` if any are missing.
- [ ] Consider a card on the Midcontinent Rift — a failed rift is a good story and a good diagram.
