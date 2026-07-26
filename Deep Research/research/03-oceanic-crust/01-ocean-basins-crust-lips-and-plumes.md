# Ocean Basins: Crust, Large Igneous Provinces and Plumes

**Domain:** oceanic crust · **Status:** first pass, 2026-07-26
**Feeds directly:** `build/seafloor.py`, `build/crustage.py`, `build/oceanage.py`, `build/seamounts.py`, `build/sediment.py`, `features.HOTSPOTS` / `PLUME_PROVINCE` / `VISIBLE_UNTIL`
**Named model gaps this addresses:** *"plume positions are hashed rather than from a real hotspot catalogue"*; *"seamounts are not clustered along plume tracks"*; *"aseismic ridges and marginal basins are absent or generic"*.

---

## 1. What oceanic crust is, in numbers

| layer | thickness | material |
|---|---|---|
| 1 — sediment | ~0.4 km mean (≈0 at the ridge, thick at old margins) | pelagic ooze, clay, turbidites |
| 2A — extrusive | ~0.5 km | pillow basalt |
| 2B — sheeted dykes | ~1.5 km | diabase |
| 3 — plutonic | ~5 km (>⅔ of the volume) | gabbro, ultramafic cumulates |

- Total **7 ± 1 km**; ultraslow ridges give **4–5 km**; plume-influenced crust is thicker — **Iceland ~20 km**.
- Density **3.0 g/cm³** vs continental **2.7** — this density contrast is why ocean is low and continent is high, and why continental crust is never subducted wholesale.
- **Oldest surviving in-place crust: ~180–200 Ma** (western Pacific, central Atlantic). Possible Mediterranean remnants at **270–340 Ma** (Ionian/Herodotus basins) — a genuinely useful fact for the app, because it means the deep Mediterranean may be Palaeozoic Tethyan floor.

**Depth–age.** Half-space cooling: `depth ≈ 2600 + 350·√(age in Myr)` metres — already implemented in `seafloor.py`. It over-deepens beyond ~80 Myr where a plate model (flattening toward ~5.7 km) fits better. **Worth checking**: at 150 Myr half-space gives 6.9 km, which is deeper than almost anywhere real. A GDH1-style flattening term would be a structural improvement, not a cosmetic one.

---

## 2. Large igneous provinces

**Definition (2008 refinement):** >1×10⁵ km³, lifespan ≤~50 Myr, with **>75% emplaced in pulses of 1–5 Myr**. That last clause is the whole environmental story: it is not the volume, it is the rate.

| province | region | age (Ma) | area (M km²) | volume (M km³) | associated event |
|---|---|---|---|---|---|
| Siberian Traps | Russia | ~250 | 1.5–3.9 | 0.9–2.0 | **End-Permian extinction** |
| CAMP | pan-Atlantic | 201–197 | 11 | 2.5 | **End-Triassic extinction** |
| Karoo–Ferrar | S Africa / Antarctica | ~183 | | | **Toarcian OAE + extinction** |
| Ontong Java | Pacific | ~122 | 1.86 | 8.4 | OAE 1a (Selli) |
| Caribbean / Madagascar | | ~94–88 | | | **OAE 2 (Bonarelli)** |
| Deccan Traps | India | ~66 | 0.5–0.8 | 0.5–1.0 | **K–Pg, with Chicxulub** |
| North Atlantic Igneous Province | Arctic/N Atlantic | 62–55 | 1.3 | 6.6 | **PETM** |

**Environmental mechanism, in the order it acts:**
1. **SO₂ → sulfate aerosol → cooling**, months to years. Sharp, short.
2. **CO₂ → warming**, 10³–10⁶ yr. The long tail.
3. **Warming → stratification + weathering-driven nutrient flux → productivity → anoxia/euxinia**, i.e. an OAE.
4. **H₂S from a euxinic water column**, toxic and ozone-destroying at extremes.
5. **Hg/TOC anomalies** are the geochemical fingerprint used to tie a stratigraphic level to a distant eruption.

**Emplacement models:** plume head (the standard); plate rupture with shallow fertile mantle; antipodal impact focusing (controversial and largely rejected — Deccan predates Chicxulub by ~1 Myr, so it cannot have been triggered by it).

**Model implication.** The app already treats a LIP as an eruption *and* a landform with a `VISIBLE_UNTIL` life, which is right. What is missing is the **environmental consequence as a first-class object**: Ontong Java → OAE 1a, Caribbean → OAE 2, NAIP → PETM, Karoo–Ferrar → T-OAE. Those are four ready-made cards linking the volcanism layer to the climate readout, and they need no new geometry.

---

## 3. Oceanic anoxic events

| event | age | duration | trigger |
|---|---|---|---|
| Hirnantian anoxia | ~445–443 Ma | repetitive, oxic-interspersed | glaciation/deglaciation cycling |
| Ireviken, Lau | Silurian | | |
| Kellwasser | ~372 Ma (F–F) | | |
| Hangenberg | ~359 Ma (D–C) | | |
| Permian–Triassic deoxygenation | ~252 Ma | | Siberian Traps runaway CO₂ |
| **T-OAE (Toarcian)** | ~183 Ma | <1 Myr | Karoo–Ferrar |
| **OAE 1a (Selli)** | ~120 Ma | 1.0–1.3 Myr | Ontong Java |
| OAE 1b (Paquier) | Albian | | |
| **OAE 2 (Bonarelli)** | ~93 Ma | ~820 kyr | Caribbean / Madagascar LIPs |
| OAE 3 | Coniacian–Santonian | | |

- OAEs occur when GMST is **>~25 °C** — i.e. warm greenhouse and above. That is a rule our climate table can be checked against: no OAE in an icehouse frame.
- Signature: **black, finely laminated organic shale with no bioturbation** + a carbon isotope excursion. **70% of the world's oil source rocks are Mesozoic**, which is these events.
- **Anoxia is a subsurface phenomenon.** Recorded in project memory and worth restating here as research, not just as a rendering rule: the Black Sea is fully euxinic below ~100 m and looks entirely normal at the surface. **Do not colour a global ocean green or purple for an OAE.** The correct rendering is a *shelf* and *basin-floor* signal, or none at all.

---

## 4. Hotspots and plume tracks

**Mechanism:** the standard model is a narrow upwelling from the core–mantle boundary, roughly fixed while the plate slides over it, producing an **age-progressive chain**. The competing model is thin/weak lithosphere allowing passive melting with no deep plume. Yellowstone is described as the only plume consistently imaged from deep mantle to surface — a useful calibration on how confident any plume card should sound.

**Chains that matter for our map:**

| hotspot | present position | chain / trail | key ages |
|---|---|---|---|
| **Hawaii** | 18°55′N 155°16′W (hotspot ~40 km SE of Kīlauea) | Hawaiian ridge → **Emperor seamounts**; the bend | bend ~47 Ma; Meiji seamount ~85 Ma |
| **Louisville** | SW Pacific | Louisville seamount chain → Osbourn Trough | ~80 Ma to present |
| **Tristan / Gough** | S Atlantic | **Walvis Ridge** + Rio Grande Rise | rooted in Paraná–Etendeka, 135–130 Ma |
| **Réunion** | 21°06′S 55°30′E | **Deccan → Laccadive–Chagos → Maldives → Mascarene → Réunion** | Deccan 68.5–66 Ma |
| **Kerguelen** | S Indian | Kerguelen Plateau, Ninetyeast Ridge, Broken Ridge | plateau 118–95 Ma; Ninetyeast from ~100 Ma |
| **Iceland** | N Atlantic | NAIP; Greenland–Iceland–Faroe ridge | 62–55 Ma onset |
| **Yellowstone** | NW USA | Snake River Plain → Columbia River Basalt | CRB ~16.7–15.9 Ma |
| **Galápagos** | E Pacific | Cocos & Carnegie ridges; **Caribbean LIP** | CLIP ~95–88 Ma |
| **St Helena, Easter, Marquesas, Cook–Austral, Samoa, Cape Verde, Canary, Azores, Afar, Marion, Crozet, Amsterdam, Bouvet, Balleny, Macdonald, Pitcairn, Society, Juan Fernández, Bowie, Cobb, Guadalupe** | | | catalogue not yet assembled with coordinates |

**Model implication — the concrete fix for the two named gaps:**

1. **Build a real hotspot catalogue** with present-day coordinates and, where published, a mantle-frame position through time. `features.HOTSPOTS` already has 37 LIP entries with age windows plus long-lived plumes; what it lacks is **coordinates for the plume itself over time** and a **track polyline** for the chain.
2. **Wire `hotspot` into `seamounts.field()`.** The input exists and is unused. Seeding seamounts along plume tracks — dense near the active end, subsiding and drowning with crustal age away from it — replaces "scatter by crustal age" with the actual mechanism, which is the structural-over-cosmetic rule applied exactly.
3. **Guyots fall out for free.** A seamount that grew above sea level and then subsided with the cooling plate is flat-topped. That is a *drawable* prediction: old chains should show flat tops at depth, young ones sharp cones and islands.
4. **Aseismic ridges are plume tracks.** Ninetyeast, Walvis, Rio Grande, Chagos–Laccadive, Cocos, Carnegie, Emperor — every one of the "absent or generic" features in README §10 is a hotspot trail. One catalogue closes both gaps.

**Fixity caveat to record on the cards:** hotspots are *not* fixed. Relative motion between hotspot groups is demonstrable before ~90 Ma, and the Hawaii–Emperor bend is now widely read as substantial **plume motion**, not a change in Pacific plate direction. So a plume track drawn before ~90 Ma is a model output, not a measurement.

---

## 5. What the app still cannot do, and why that is fine

- **Deep-time sea floor cannot be accurate.** That crust was subducted; the record is gone. The isochron model correlates 0.41 with the surveyed grid where both exist. The target is *structural correctness* — right kinds of features in the right relationships — not fidelity.
- **Coastline and shelf-break detail is data-limited**, not shader-limited: our grid is ~9.8 km and matches the source PaleoDEMs exactly, against 15 arc-seconds for modern near-shore bathymetry.

---

## Sources

- Wikipedia: *Oceanic crust*, *Large igneous province*, *Hotspot (geology)*, *Anoxic event* — retrieved 2026-07-26. (*List of hotspots* returns 404; the coordinate catalogue must be assembled from the individual hotspot articles or from a published compilation.)
- Steinberger, B. (2000), "Plumes in a convecting mantle: models and observations for individual hotspots", *JGR* 105 — the standard hotspot catalogue with positions. **Obtain.**
- Coffin, M. F. & Eldholm, O. — LIP definition and inventory; Bryan & Ernst (2008) for the refined definition.
- Parsons & Sclater (1977) half-space cooling; Stein & Stein (1992) GDH1 plate model for the flattening term.

## Open items

- [ ] Assemble a hotspot catalogue CSV with coordinates → `modeling/hotspot_catalogue.csv`.
- [ ] Add a GDH1 flattening term to the depth–age law in `seafloor.py` and measure the change at 100–180 Myr crust.
- [ ] Add LIP → OAE / hyperthermal links as card content.
