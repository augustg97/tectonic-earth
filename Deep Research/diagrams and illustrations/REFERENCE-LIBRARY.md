# Reference library — the pooled illustration index

**Every illustration available to this project, in one place, 2026-07-26.**

The library is in three tiers, and the tier decides what you may do with the image:

| tier | where | licence | may ship in the app? |
|---|---|---|---|
| **A · authored** | `authored/` | ours | **yes** |
| **B · collected** | `collected/` | PD / CC0 / CC-BY only, each recorded | **yes**, with credit where CC-BY |
| **C · reference** | `../../Deep Time Maps and Resources/` | **© CPGS, © C. R. Scotese, © Encyclopædia Britannica** | **no — measure against them, never reproduce** |

That last row is the important finding of the resource review. The paleogeographic map
series and the process diagrams the user collected are outstanding *reference*, and they
are all copyrighted. They are **not** duplicated into this folder: doing so would add
71 MB of copyrighted binaries to git for no benefit. This file indexes them where they
sit.

---

## Tier A — authored (11 figures, generated from the models)

Run `python "make_diagrams.py"` to rebuild all of them. Because they read from
`modeling/`, a corrected date propagates into the figure automatically.

| # | figure | what it shows | used by |
|---|---|---|---|
| 01 | `01-deep-time-master-chart.svg` | supercontinents, glaciations, extinctions, LIPs, anoxic events, hyperthermals and vegetation on one 1250-Myr axis | WP-01, README |
| 02 | `02-vegetation-through-time.svg` | Whittaker zones × vegetation eras; opacity is canopy height, so the greening of the land is a visible gradient | WP-02, biome dossier |
| 03 | `03-the-longitude-problem.svg` | why palaeomagnetism cannot place a continent in longitude, and what it costs us | WP-01 |
| 04 | `04-lip-to-extinction-cascade.svg` | the fixed mechanistic order eruption → aerosol → CO₂ → anoxia → extinction, with the seven instances | OAE cards, WP-03 |
| 05 | `05-continental-affiliation.svg` | which block belonged to what, when; disputed memberships dashed | WP-01 |
| 06 | `06-snowball-bifurcation.svg` | GMST vs CO₂ at 700 Ma from the EBM; the hysteresis | WP-03, glaciation cards |
| 07 | `07-cenozoic-climate-events.svg` | warming above the line, carbon drawdown below — PETM, EECO, MECO, MMCO vs Azolla and Himalayan weathering | PETM / Azolla / EECO cards |
| 08 | `08-oxygen-through-time.svg` | GOE, the Lomagundi overshoot and crash, the boring billion, the NOE, the Permo-Carboniferous peak | GOE card, WP-03 |
| 09 | `09-atoll-guyot-subsidence.svg` | Darwin's subsidence sequence: island → barrier → atoll → guyot | atoll/guyot card, seamount work |
| 10 | `10-back-arc-rollback.svg` | slab roll-back opening a basin behind an arc | back-arc card, marginal-basin gap |
| 11 | `11-glossopteris-gondwana.svg` | the five-continent distribution and the Suess argument | Glossopteris card |

## Tier B — collected (11 files, each licence-checked and eye-checked)

Manifest with licence, source URL, author and a **review verdict** per file:
[`collected/MANIFEST.json`](collected/MANIFEST.json).

| file | subject | verdict |
|---|---|---|
| `crustal-age.png` | **NOAA age-of-oceanic-crust map, 0–280 Myr scale** | the best fetch of either round; directly comparable with our `_o` field |
| `glossopteris-distribution.png` | the Snider-Pellegrini/Wegener fossil map — Glossopteris, *Lystrosaurus*, *Mesosaurus*, *Cynognathus* across five continents | correct; **captions in German** |
| `subduction-zone.jpg` | Mariana arc cross-section with back-arc spreading axis and seismic velocities | correct and good |
| `pangaea-map.jpg` | Permian/Pangaea palaeogeography **with a biome legend** | correct; checkable against our biome shader at 250–280 Ma |
| `thermohaline-circulation.jpg` | the conveyor-belt schematic | correct, PD (US federal) |
| `continental-lithosphere-anatomy.jpg` | craton / shield / platform / orogen / margin cross-section | **renamed** — a mid-ocean-ridge query returned it; CC-BY, needs credit |
| `oxygen-history.png` | Phanerozoic atmospheric O₂ curve | **renamed** — a supercontinent-cycle query returned it |
| `crust-types-block-diagram.png` | continental vs oceanic crust block diagram | **renamed** — not the margin anatomy asked for |
| `carboniferous-regional-subdivisions.png` | Carboniferous regional stage correlation | **renamed** — not the ICS chart asked for |
| `sea-level-quaternary.gif` | 800 kyr climate + late Quaternary sea level to −140 m | **renamed** — not the Phanerozoic curve asked for |
| `rodinia-map.png` | Rodinia at 1.1 Ga with cratons and orogenic belts | correct subject, **labels in Hebrew** — reference only |

**Still wanted, and empty only because Commons rate-limited the runs** (a 429 is not an
absence): Hawaii–Emperor chain, Phanerozoic CO₂ curve, Pangaea breakup sequence, a
licence-clean Wilson-cycle diagram.

## Tier C — reference only, in `Deep Time Maps and Resources/`

Full catalogue with per-file notes:
[`../research/09-source-documents/CATALOGUE-deep-time-maps-and-resources.md`](../research/09-source-documents/CATALOGUE-deep-time-maps-and-resources.md).

| group | count | licence | best use |
|---|---|---|---|
| Deep Time Maps™ global Mollweide series, 32 ages Present→525 Ma | 36 | © CPGS | **the shelf-sea, ice-extent and coastline audit** — measure, don't reproduce |
| C. R. Scotese PALEOMAP series with **named** oceans and continents, 0→650 Ma | 16 | © Scotese | **the label-placement audit**; its vocabulary is our vocabulary |
| **Scotese Future World +50 / +150 / +250 Ma** | 3 | © Scotese | **the only external check our future series has ever had** |
| CPGS North American regional series, Mississippian→Permian, with highstand/lowstand pairs | 18 | © CPGS | glacio-eustatic cyclothem amplitude; the Permian Basin evaporite story |
| Encyclopædia Britannica process diagrams | 21 | © Britannica | mechanism reference — back-arc roll-back, atoll formation, slab pull, margin anatomy, coalescence pathways |
| Wikipedia/Commons figures | 8 | **check each individually — many are CC-BY-SA, which this project refuses** | — |
| Google Earth screenshots | 5 | Google | the sea-floor fidelity standard (HANDOFF) |
| Bookmarked URLs | 11 | — | Scotese PALEOMAP, Deep Time Maps WIS + Arctic, Britannica, five Wikipedia articles |

### Two Tier-C figures that changed the research

- **`globe-diagram-processes-supercontinent-cycle.webp`** cites **Pastor-Galán et al.,
  "Supercontinents: Myths, Mysteries, and Milestones", *Geol. Soc. Lond. Spec. Pub.*
  470:39–64 (2018)** — a real primary citation for the introversion / extroversion /
  orthoversion mechanisms, which the dossier previously had from a secondary source only.
- **`Diagram-Atolls-atoll-formation-process-islands-parts.webp`** is Darwin's subsidence
  model, which is *the same physics* as the guyot prediction already in the model-gaps
  register — one mechanism covers both, and figure 09 now draws it.

---

## Rules for adding to the library

1. **Author it if you can.** A generated figure cannot drift from the data, needs no
   licence, and can be restyled to match the app.
2. **If you fetch it, licence-check by machine and subject-check by eye.** Both traps have
   fired here: correct licence with a completely wrong subject (a 1913 chromosome diagram),
   and a rate limit that reads exactly like "no such image".
3. **Never assume Wikipedia means free.** CC-BY-SA is common there and this project
   refuses it, because share-alike would reach the whole project.
4. **Record the verdict, not just the file.** `MANIFEST.json` carries `review`,
   `review_note` and `verified_subject` for every entry, so the next person does not
   re-do the eyeballing.
