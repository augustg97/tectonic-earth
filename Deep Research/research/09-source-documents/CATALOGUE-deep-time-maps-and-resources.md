# Catalogue: `Deep Time Maps and Resources/`

**Reviewed 2026-07-26** — all 121 files opened and looked at on contact sheets, plus the
11 bookmarked URLs resolved. 71 MB, not in git.

**The headline, and it constrains everything else: almost none of this is shippable.**
The paleogeographic map series are © Colorado Plateau Geosystems (Deep Time Maps™) and
© C. R. Scotese; the process diagrams are © Encyclopædia Britannica, Inc. They are
excellent **reference material for auditing our own output**, which is a legitimate
internal use, but they cannot be redistributed in the app under the project's standing
licence policy (PD / CC0 / plain CC-BY only). Anything we want on a card has to be
authored, or fetched under licence, or replaced by an equivalent from Commons.

---

## 1. Deep Time Maps™ / Colorado Plateau Geosystems — global Mollweide series (36 files)

`*-MOLL-tn.jpg`, plus two orthographic and two rectangular crops. Watermarked **© CPGS**.
Palette: tan/olive land, bright cyan shallow shelf sea, dark blue deep ocean, white ice.

**Ages present (32 distinct):** Present, 21 ka, 5, 15, 30, 50, 66, 75, 90, 110, 130, 150,
170, 180, 200, 220, 240, 250, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 450, 470,
500, 525 Ma. Extras: `280-Ma-L-Permian-Ortho-Pangea` (orthographic on Pangaea),
`400-Ma-L-Devonian-Ortho-NAM`, `30-Ma-…-RECT-crop-50`, `50-Ma…-RECT-crop-full`.

**What they are good for.** This is the audit set the user has already asked for. Every one
of these ages is within half a keyframe of one of ours, so a side-by-side at matched
projection tests, in order of what our pipeline can actually get wrong:

1. **Shelf-sea extent** — the cyan band. Our 20 km DEM under-resolves epicontinental seas
   (the reason `epeiric.py` exists), and this series shows exactly where they should be.
2. **Ice extent** — white. Cross-checks `ice_audit.py`'s literature target table with a
   *spatial* pattern rather than an area.
3. **Continental outline and position** — the frame check of gap A5.
4. **Land/sea fraction** — measurable directly off the pixels.

**How to use them without a licence problem:** measure, don't reproduce. A numeric
comparison table in a research report is fine; shipping the image is not.

## 2. C. R. Scotese PALEOMAP series — global maps with NAMED features (16 files)

Numbered `.jpg` files, watermarked **© C.R. Scotese**. Unlike the CPGS series these carry
**labels** — ocean names, continent names, mountain belts, subduction zones and spreading
ridges with a legend — which makes them the better reference for **label placement**, not
just coastlines.

| file | age | title |
|---|---|---|
| `000.jpg` | 0 | Modern World |
| `014.jpg` | 14 Ma | Middle Miocene |
| `050.jpg` | 50.2 Ma | Middle Eocene |
| `066.jpg` | 66 Ma | K/T Boundary |
| `094.jpg` | 94 Ma | Late Cretaceous |
| `152.jpg` | 152 Ma | Late Jurassic |
| `195.jpg` | 195 Ma | Early Jurassic |
| `237.jpg` | 237 Ma | Early Triassic |
| `255.jpg` | 255 Ma | Late Permian |
| `306.jpg` | 306 Ma | Late Carboniferous |
| `342.jpg` | 356 Ma | Early Carboniferous *(filename and caption disagree — caption says 356)* |
| `390.jpg` | 390 Ma | Early Devonian |
| `425.jpg` | 425 Ma | Middle Silurian |
| `458.jpg` | 458 Ma | Middle Ordovician |
| `514.jpg` | 514 Ma | Late Cambrian |
| `650.jpg` | 650 Ma | Late Proterozoic |
| **`18F050v4.jpg`** | **+50 Ma** | **Future World** |
| **`19F150v4.jpg`** | **+150 Ma** | **Future World** |
| **`20F250v4.jpg`** | **+250 Ma** | **Future World** |

**The three future maps are the most valuable single item in the folder**, because our
future series is a hypothesis with no independent check, and this is the hypothesis it
implements. Read from `20F250v4.jpg` (© 2000 C. R. Scotese):

- **Africa sits at the centre** of the assembled mass, with North America to its
  west-northwest, South America to its south-southwest, Eurasia to its east.
- A **"Mediterranean Mts"** belt runs NE from Africa into Eurasia — the collisional
  suture, and the future analogue of the Central Pangaean Mountains.
- **Antarctica + Australia form a separate southern mass** joined by a narrow neck toward
  South America/Africa, not fully merged.
- **An interior sea survives** between North America and Africa/Eurasia — Pangaea Ultima
  is not a solid disc.
- **The Pacific occupies essentially the whole opposite hemisphere**, ringed by subduction
  along the assembled continent's western and southern margins.

Named continental blocks on the deep-time maps (Gondwana, Laurentia, Baltica, Siberia,
Avalonia, Kazakhstania, North/South China, Cimmeria) and named oceans (Panthalassic,
Paleo-Tethys, Tethys, Rheic, Iapetus, Panafrican, Indo-Atlantic) are exactly our label
vocabulary, at exactly the ages we most often get wrong.

## 3. Colorado Plateau Geosystems — North American regional series (18 files)

`miss-*`, `penn-*`, `perm-*`, `atokan-*`, `desmoines-*`. Stage-level North American
paleogeography through the Mississippian, Pennsylvanian and Permian, with **explicit
highstand/lowstand pairs** for the Atokan, Desmoinesian and Morrowan.

**Why this matters more than it looks.** Those pairs are **glacio-eustatic cyclothems** —
the Late Palaeozoic Ice Age writing its glacial–interglacial cycles into the North
American shelf. They alternate on ~100 kyr to ~400 kyr, two orders of magnitude below our
5 Myr keyframe, so we can never draw them. But they establish the *amplitude* our
Pennsylvanian sea level should sit in the middle of, and they show the Permian Basin
evolving through Wolfcamp → Leonard → Guadalupian → **Ochoan/Castile evaporites**, which
is a card-worthy story the app does not currently tell.

## 4. Encyclopædia Britannica process diagrams (21 `.webp`)

© Encyclopædia Britannica, Inc. **Not shippable**, but several are the clearest statement
of a mechanism we model, and two changed what is in the dossiers:

| file | content | bearing on our model |
|---|---|---|
| **`globe-diagram-processes-supercontinent-cycle.webp`** | **introversion / extroversion / orthoversion**, sourced to **Pastor-Galán et al., "Supercontinents: Myths, Mysteries, and Milestones", Geol. Soc. Lond. Spec. Pub. 470:39–64 (2018)** | **a real citation for §1 of the supercontinent dossier**, which had the three mechanisms from a secondary source only |
| `pitch-continental-shelf-slope-way-transition-region(-1).webp` | shelf–slope–rise anatomy, with a dense **dendritic** canyon comb across the whole slope | already the reason our canyons are dendritic (HANDOFF) |
| `Map-oceanic-crust-pattern-Earth-age-scale.webp` | global crustal age with a colour scale | the pattern `seafloor.py`/`crustage.py` synthesise |
| `magma-polarity-field-oceanic-crust-Earth-rock.webp` | magnetic stripe formation | the isochron concept behind the age field |
| `crust-Oceanic-destruction-theory-Production-Earth-plate.webp` | production vs destruction balance | why ridge volume drives sea level |
| `slab-weight-trench-rest-tablecloth-process-pull.webp` | slab pull | |
| `slab-process-sea-anchor-back-arc-basin-formation.webp`, `trench-process-back-arc-basin-formation.webp` | back-arc basin opening by roll-back, 4 panels each | **marginal basins are a named gap** (README §10); this is the mechanism |
| `subduction-zones-Stratovolcanoes-Earth-plate-margins-activity.webp` | arc volcanism at margins | |
| `subducting-plate-plane-path-earthquakes-mantle.webp` | Wadati–Benioff zone | |
| `types-eruptions.webp` | eruption styles | volcanism card art |
| `Diagram-Atolls-atoll-formation-process-islands-parts.webp` | fringing reef → barrier → atoll, with subsidence | **the guyot/atoll prediction of gap D4** — this is Darwin's subsidence model, and it is the same physics as a drowning seamount |
| `Distribution-landmasses-…-Permian / -1 / -2 / -3 / (base)` | five paleogeographic maps (Late Permian 255, Late Carboniferous 306, Early Triassic 237, Late Jurassic 152) with a legend: **Mountains / Land / Shallow seas / Deep ocean basins / Subduction zone / Sea-floor spreading ridge** | a second independent shelf-sea reference |
| `Rodinia-map-Earth.webp` | Rodinia, 1.3–1.1 Ga | our 1000 Ma frame |
| `Map-world-continents-supercontinent-Earth-Pangea.webp` | Pangaea | |
| `location-continents-Earth.webp` | Wegener-style 4-panel drift, 225/150/100/present Ma | |
| `Section-San-Andreas-Fault-California-Carrizo-Plain.webp` | transform fault, aerial | |
| `Paleogeography-paleoceanography-times-Early-Permian.gif` | Early Permian paleogeography + **paleoceanography** | the current-model gap C6 |
| `Infographic-continents-evidence-history-Earth.webp` | evidence for **submerged continents** | Zealandia, Mauritia — `seafloor.PLATEAUS` |

## 5. Wikipedia / Commons figures (7 files) — **licence must be checked individually**

`All_palaeotemps.svg.webp` (the Phanerozoic temperature composite),
`OxygenLevel-1000ma.svg.webp`, `Geologic_Clock_with_events_and_periods.svg.webp`,
`Human_evolution_chart-en.svg.webp`, `Paleoglobe_NO_1590_mya-vector-colors.svg.webp`
(Columbia/Nuna at 1590 Ma), `Positions_of_ancient_continents,_550_million_years_ago.jpg`,
`World_map_of_bathymetric_data_-_GEBCO_2014.jpg`, `LGM.jpg`.

**Do not assume these are usable.** Wikipedia figures are commonly **CC-BY-SA**, which the
project's policy refuses because share-alike would reach the whole project. Each needs its
Commons file page checked before any of it is shipped. `All_palaeotemps` in particular is
a well-known composite that predates PhanDA and should not be used as a temperature
reference now in any case.

## 6. Bookmarked URLs (11 `.webloc`)

| bookmark | URL |
|---|---|
| Scotese PALEOMAP home | http://www.scotese.com/Default.htm |
| Deep Time Maps — Arctic | https://deeptimemaps.com/map-lists-thumbnails/arctic/ |
| Deep Time Maps — Western Interior Seaway | https://deeptimemaps.com/map-lists-thumbnails/western-interior-seaway/ |
| Britannica — plate tectonics / transform faults | https://www.britannica.com/science/plate-tectonics/Transform-faults |
| Wikipedia — History of Earth | https://en.wikipedia.org/wiki/History_of_Earth |
| Wikipedia — Paleoclimatology | https://en.wikipedia.org/wiki/Paleoclimatology |
| Wikipedia — **Timeline of glaciation** | https://en.wikipedia.org/wiki/Timeline_of_glaciation |
| Wikipedia — **List of periods and events in climate history** | https://en.wikipedia.org/wiki/List_of_periods_and_events_in_climate_history |
| Wikipedia — **Azolla event** | https://en.wikipedia.org/wiki/Azolla_event |
| Wikipedia — Snowball Huronian (image) | …/History_of_Earth#/media/File:Snowball_Huronian.jpg |
| Wikipedia — North America terrain 2003 (image) | …/History_of_Earth#/media/File:North_america_terrain_2003_map.jpg |

The three in bold are new material and were fetched — see
`research/04-paleoclimate/02-climate-events-timeline.md`.

**The Western Interior Seaway bookmark is pointed**: the WIS label was the specific case
that exposed the frame mismatch, and Deep Time Maps publishes a dedicated WIS series.

---

## What this review changed

1. **A real citation for the coalescence pathways** — Pastor-Galán et al. (2018) — added to
   `research/01-plate-tectonics/01-supercontinent-cycle.md`.
2. **The Scotese future maps give our future series an external check** for the first time.
   New gap item.
3. **Back-arc basin roll-back diagrams** address a named model gap (marginal basins) with a
   mechanism rather than a texture.
4. **Atoll formation = seamount subsidence**, which is the same physics as the guyot
   prediction already in gap D4 — one model covers both.
5. **The licence finding is itself a result**: this folder is an audit reference, not an
   illustration source. The illustration library has to be authored or licence-fetched.
