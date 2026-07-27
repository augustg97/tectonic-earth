# Model gaps register

Every open item this research programme has produced, tied to the specific Tectonic Earth
subsystem it would change. **This is the handover surface between research and the build.**
Nothing here has been applied to the model — that is deliberate; this folder does not
change the app.

Priority: **P1** = closes a known visible defect · **P2** = adds real fidelity ·
**P3** = correctness housekeeping · **P4** = worth knowing, no action yet.
Status: **RESOLVED** = answered, with the answer recorded · **MEASURED** = quantified and
ready to apply · **RETIRED** = no longer needed · items with no status are open.

## Round 3 resolutions (2026-07-26) — see [WP-04](research%20reports/WP-04-closing-the-gaps.md)

| item | status | result |
|---|---|---|
| **A1** | **RESOLVED** | Scotese DOES publish rotations: `PALEOMAP_PlateModel.rot`, CC-BY 4.0, −250→1100 Ma, 258 plate IDs, inside `Scotese_PaleoAtlas_v3.zip`. Measured over 53 land points × 10 ages on our own shipped field: **abyssal-plain errors 20% → 5%**, better at every age, best in the Palaeozoic where the gap was worst. |
| **A3** | **RETIRED** | A regional frame correction is an elaborate workaround for a problem that vanishes when both halves use one frame. |
| **A4** | demoted P2→P3 | Still worth doing (a label should ride the landmass it names) but no longer load-bearing for the frame problem. |
| **C1** | **MEASURED** | Our Phanerozoic max is **30.0 °C at 90 Ma** vs PhanDA's **36 °C in the Turonian**. Position right, amplitude 6 °C short; **no keyframe ever reaches the hothouse state**. |
| **C3** | **MEASURED** | Our O₂ peak is **36.0% at 280 Ma**; current review says ~30%. Timing right, amplitude wrong. Compounds the Guadalupian card error (F9). |
| **C4** | **MEASURED** | Two suspicious transitions: 66→56 Ma (CO₂ doubles, GMST +1.5 °C) and 380→360 Ma. Both sit where the record is strongest. |
| **C10** | **RESOLVED, no action** | Tonian 18.9 °C vs 14.4 °C today at −6.7% solar: CO₂ compensates correctly. A check that passed. |
| **D1** | **DELIVERED** | `modeling/hotspots.py` — 53 hotspots with coordinates, chains, LIP roots, flux, confidence. 8 rooted in a LIP. |
| **D3** | **DELIVERED** | `ASEISMIC_RIDGES` maps all 15 named ridges to the plume that built each. Not a texture problem — a catalogue problem. |
| **D4** | **DELIVERED** | `summit_depth()` — one line of half-space subsidence gives islands → atolls → guyots, crossover at ~16 Myr. |
| **B3** | **DOWNGRADED P1→P4** | Not a realm error. The entry is correctly `land` with plausible Devonian content; only the NAME is loose. Rename, keep the taxa. |
| **B2** | **MEASURED** | Regional coverage is thinnest (2 entries) at 420–460 Ma — exactly where Palaeozoic provinciality peaked. |
| **A2** | **DELIVERED** | `modeling/audit_label_windows.py` — 46 labels matched to a block or assembly, **2 findings**. Building it exposed that `ASSEMBLIES["top"]` was breakup ONSET, so a naive check reported 6 false errors; added `recognisable_until()` (Pangaea rifts from 175 Ma and is one continent for 75 Myr more). |
| **E4** | **DELIVERED** | `deeptime.STAGES` 73 → **101**, complete through the Palaeozoic. The strengthened epoch-tiling selftest then caught **two pre-existing errors of my own**: the Cambrian epochs were mis-bounded (Terreneuvian/Series 2/Miaolingian) and Ludlow ran to 425 instead of 423. |
| **F10** | **CLOSED, by authoring instead** | Four fetch attempts across three rounds; Commons returned 429 or nothing acceptably licensed every time. Applied the library's own first rule — *author it if you can* — and generated **`12-climate-vs-phanda.svg`** straight from `build/climate.py`, which is a better artifact than the stock CO₂ curve would have been: it draws the C1/C3/C4 findings on the app's own numbers and cannot drift from the table it assesses. The Hawaii–Emperor, Pangaea-breakup and Wilson-cycle slots stay empty and are not worth more fetch attempts. |
| **F11** | **CLOSED, negative result** | The "English" Glossopteris query returned the same figure in **Dutch**, twice. There is no English-labelled equivalent on Commons under any query tried. The German one stays, flagged. |
| **E2** | **CLOSED, partial** | Torsvik & Cocks (2017) is a **book** and not obtainable here. Lyons, Reinhard & Planavsky (2014) is paywalled and the open mirrors probed were 301/404. Both remain cited-not-consulted, and every claim resting on them is flagged as such in the dossiers. Recording this as a limit rather than leaving it looking pending. |
| **A5 / F1** | **HANDED OFF** | [`HANDOFF-A5-F1-reference-map-audit.md`](HANDOFF-A5-F1-reference-map-audit.md) — a self-contained prompt for a parallel session. Needs image reprojection and comparison at scale, which is its own job. |
| **B10** | **PARTIAL** | `taxa_db.py` 105 → **114**. Honest correction: 12 of the 21 taxa I drafted were ALREADY in the database — the "mid-Cambrian–Silurian thin patch" diagnosis was half wrong. The Cambrian was fine (16); the real gaps were the **Ordovician (14)** and **Silurian (15)**, now filled with *Sacabambaspis*, *Aegirocassis*, *Promissum*, *Pterygotus*, *Arandaspis*, *Birkenia*, *Favosites*, *Aysheaia*, *Haikouichthys*. Its selftest caught all three of my mistakes: duplicates, a missing optional field, and a zero-length age range. |
| **E5** | **DELIVERED** | Every module is stdlib-only except `climate_ebm`/`ocean_circulation` (numpy, already a project dependency), so `build/` can import any of them with a two-line `sys.path` insert. Verified. |
| **B1** | **DECIDED + AUDITED** | Design chosen: *model decides, curated is a flagged exception*; unplaced points get the global list **explicitly labelled as global**. `modeling/audit_curated_biota.py` split all 198 curated spans: **9 exceptions, 67 province-typical, 121 the model cannot place, 0 conflicts.** The bottleneck turns out to be the PROVINCE MODEL'S COVERAGE, not the curated data — so extending `paleobiogeography.py` comes before any wiring. |
| **B1 coverage** | **DELIVERED** | The province model was **vastly extended** and the bottleneck is closed. New schemes: Tonian–Cryogenian marine (1000–635 Ma, incl. both snowball oceans), Ediacaran (Avalon / White Sea / Nama), Ordovician split out with its five named shelf provinces, Silurian split out (cosmopolitan + Malvinokaffric), Triassic split out (post-extinction flattening), Cenozoic marine rewritten around gateway tectonics, and a Silurian–Devonian land-colonisation sequence. Plus **named latitudinal fallbacks** so no cell is ever an unnamed shrug. **49 distinct provinces across 0–1000 Ma.** Curated spans placed: **67 → 188, unplaced 121 → 0.** |
| **B7** | **DELIVERED** | `modeling/lagerstatten.py` — **30 Konservat- and Konzentrat-Lagerstätten** with present-day coordinates, block, window, setting, and what each shows that nothing else does. Its selftest caught the real trap: nine sites named `Laurussia`, which is an *assembly* and has no plate to ride — corrected to the craton each sits on. |
| **C6** | **DELIVERED** | `modeling/ocean_circulation.py` — wind-driven surface circulation from a land/sea mask alone: banded wind stress → Sverdrup interior → westward integration → western boundary current, plus eastern-boundary upwelling and a circumpolar test. **Closing Drake Passage switches the ACC off**, which is the 34–23 Ma story from geometry alone. Two bugs found by its own selftest: the closure test put the land bridge in the northern hemisphere, and the circumpolar test was satisfied by the *Arctic* (a ring of water round a pole is not a current — the jet needs the westerly belt). Honest limitation recorded: psi is a westward ramp per row, so it wants streamlines, not a per-pixel fill. |

---

## A. Label placement — the standing "serious problem"

| # | P | item | touches | from |
|---|---|---|---|---|
| A1 | **P1** | **Check whether the Scotese PALEOMAP series publishes or implies its own rotation file.** If it does, tracking features in that frame makes the Merdith↔Scotese mismatch identically zero and A3 becomes unnecessary. Highest value per hour of anything in this register. | `paleo_tracks.py` | WP-01 §3 |
| A2 | **P1** | **Add an existence gate to every crustal label.** `paleogeography.exists(block, age)` and `affiliation(block, age)` are written and tested. Wire them into `build_labels()` as a validator: a block label must not draw outside the block's life, an assembly label must not draw outside the assembly's window, and every contradicted window in `features.py` should raise a warning. Detects a class of error the pipeline currently cannot see. | `build_webdata.build_labels`, `features.LABELS` | WP-01 §3 |
| A3 | P2 | **Make the frame correction regional, not rigid.** Fit a longitude offset per major block, smooth each in time, interpolate spatially by great-circle distance. Score on land–sea agreement over the whole window, not on a cloud centroid. Only if A1 fails. | `frame_offset.py` | WP-01 §3 |
| A4 | P2 | **Generalise the composite-fragment treatment to all crustal label types** (continent, craton, orogen, terrane, region, plateau), so the final position comes from the DEM's own land and has no frame dependence at all. Water labels keep their separate path and must not be smoothed. | `build_webdata`, `features.COMPOSITE_LABELS` | WP-01 §3 |
| A5 | P2 | **Audit the ~76 DeepTimeMaps palaeogeographic maps against our own frames at matched ages.** Already requested by the user; the best independent check available. | reconstruction as a whole | WP-01 |
| A6 | P3 | State the honest limit on the About page: positions before ~175 Ma are reconstructions not measurements; palaeomagnetism never fixes longitude; this map combines two frames. | `web/index.html` About | WP-01 §4 |
| A7 | P3 | Note in README §9 that a small track-vs-DEM residual is **expected** — part of it can be a true-polar-wander correction present in one model and absent in the other. Chasing it to zero is the wrong goal. | `README.md` | research 01/02 |

## B. Life, biota cards and provinces

| # | P | item | touches | from |
|---|---|---|---|---|
| B1 | **P1** | **Replace `regionTaxaAt`'s hand-keyed default with `province(age, lat, realm, block)`**, keeping the curated lists as overrides for genuinely distinctive localities. The fallback stops being "one global list". | `build/life.py`, `build_webdata.build_life` | WP-02 §4 |
| B2 | **P1** | **Run the provinciality audit.** `provinciality(age)` predicts the Permian/Triassic should be *less* differentiated and the Late Cretaceous/Neogene *more*. Measure `life_data.json` against it. If the data does the opposite, the data is wrong. | `life_data.json` | WP-02 §1 |
| B3 | **P1** | **Re-check the "Malvinokaffric flora" entry.** The Malvinokaffric is a **marine** realm; a flora of that name is at best loose. Check realm, taxa and the name itself. | `life_data.json` | WP-02 §2 |
| B4 | P2 | **Carry attributes into the cards** — size, habit, diet — from `taxa_db.py`. The illustrations (273 PhyloPic silhouettes) are far ahead of the text. | `life.py`, biota panel | WP-02 §4 |
| B5 | P2 | **Realm-locking must be a property of the locality, not the label type.** Solnhofen (marine + terrestrial + aerial) and *Hesperornis* (a bird that dives) prove the strict lock is wrong. The existing `MARINE_REGIONS` exceptions should become the documented rule. | `life.MARINE_REGIONS` | WP-02 §4 |
| B6 | P2 | **Enforce the terrestrial gates in the shader, not only in labels**: no canopy before ~385 Ma, no grassland before ~40 Ma, no C4 savanna before ~8 Ma, no vegetation before ~470 Ma. A Silurian continent should be rock and thin damp crust, not green. | terrain `FRAG` biome colour | WP-02 §4 |
| B7 | P2 | **Add Lagerstätten as point features** riding their own continent's track: Burgess, Chengjiang, Qingjiang, Sirius Passet, Emu Bay, Orsten, Rhynie, Mazon Creek, Solnhofen, Messel, Yixian, La Brea, Riversleigh. The machinery already exists. | `features.py`, `build_webdata` | WP-02 §4 |
| B8 | P2 | **Add biotic-interchange events** as cards: Great American Interchange, trans-Arctic interchange, the Grande Coupure, *Lystrosaurus* after the P–Tr. Moments when the map causes the biology. | new card type | WP-02 §4 |
| B9 | P3 | The **Carboniferous rainforest collapse is Euramerican only** — Cathaysian rainforest persists to the end-Permian. Same age, different vegetation on different blocks. Make sure the biome text and the biota cards can express that. | `life.py`, biome text | research 06/01 |
| B10 | P3 | Grow `taxa_db.py` past 105 entries. Thinnest interval is **mid-Cambrian to Silurian**. | `modeling/taxa_db.py` | WP-02 |
| B11 | P3 | Verify the Devonian realm names (Eastern Americas / Old World / Malvinokaffric) against a primary source — currently stated from general literature. | research 06/01 | WP-02 |
| B12 | P4 | The "high O₂ → giant arthropods → rainforest collapse killed them" chain is **contested**: both *Meganeura* and *Arthropleura* are now found after the collapse and probably forest-independent. State as hypothesis. | card text | research 05/01 |

## C. Climate, atmosphere and ocean chemistry

| # | P | item | touches | from |
|---|---|---|---|---|
| C1 | **P1** | **Obtain the PhanDA GMST series (Judd et al. 2024) and diff it against `climate.py`.** Especially the Cretaceous — PhanDA's global maximum is **36 °C in the Turonian**, and if our peak is well under 30 °C every downstream field inherits the error. | `climate.py`, `refresh_manifest.py` | research 04/01 |
| C2 | P2 | **Name the climate state in the readout** ("warm greenhouse, no polar ice") using PhanDA's five-state scheme, driven by the `iceLand`/`iceSea` we already measure. A state is more useful to a reader than a number. | readout | research 04/01 |
| C3 | P2 | **Check the O₂ curve**: the Permo-Carboniferous peak should be near **30%**, not 35%, and should sit in the Pennsylvanian–early Permian. | `climate.py` | research 05/01 |
| C4 | P2 | **Sanity-check GMST against CO₂** using PhanDA's ~8 °C apparent Earth-system sensitivity per doubling. If our CO₂ doubles between two ages and GMST moves 1 °C, one of the columns is wrong. | `climate.py` | research 04/01 |
| C5 | P2 | **Add a "climate events" navigable structure** for the PETM, the Cretaceous OAEs, the Toarcian and the Eocene optima. They are shorter than a 5 Myr keyframe so they cannot be *drawn*, but the extinction/glaciation card pattern carries them perfectly. | new panel, `eras_data.json` | research 04/01 |
| C6 | P2 | **Build the ocean-current model.** Not a fluid solver: a latitude-banded gyre template (subtropical ~30°, subpolar ~55°, equatorial counter-current) over the real basin geometry, with west-intensification built in, plus an ACC when and only when a circumpolar path exists. Gateways then explain themselves. | new `modeling/ocean_circulation.py` → shader | research 05/01 |
| C7 | P3 | **Decide and cite one sea-level curve.** The published curves genuinely disagree (a 2016 review is titled *"A 'chaos' of Phanerozoic eustatic curves"*). Say which one the app uses. | `climate.py`, About | research 04/01 |
| C8 | P3 | **Add `contested` to `eras_data.json` supercontinents** and populate it for Pannotia, Kenorland, Vaalbara, Ur — mirroring what the glaciation cards already do. | `eras_data.json`, `eras.py` | research 01/01 |
| C9 | P3 | **Represent OAEs as sea-floor sediment, not water colour.** Anoxia is subsurface: the Black Sea is euxinic below ~100 m and looks entirely normal at the surface. Black laminated mud on the floor is real; a green ocean is not. | shader, `SEA_COLOUR` | research 05/01 |
| C10 | P4 | Check the Tonian rows: solar luminosity is −8% at 1000 Ma, but the faint young Sun must be compensated by CO₂, so a cold Tonian frame would be wrong for the wrong reason. | `climate.py` | research 04/01 |

## D. Ocean floor, crust and plumes

| # | P | item | touches | from |
|---|---|---|---|---|
| D1 | **P1** | **Assemble a hotspot catalogue with coordinates** (Hawaii, Louisville, Tristan/Gough, Réunion, Kerguelen, Iceland, Yellowstone, Galápagos, St Helena, Easter, Marquesas, Cook–Austral, Samoa, Cape Verde, Canary, Azores, Afar, Marion, Crozet, Bouvet, Macdonald, Pitcairn, Society, Juan Fernández, Bowie, Cobb, Guadalupe) → `modeling/hotspot_catalogue.csv`. Wikipedia's *List of hotspots* 404s; build it from the individual articles or from Steinberger (2000). | `features.HOTSPOTS` | research 03/01 |
| D2 | **P1** | **Wire `hotspot` into `seamounts.field()`.** The input exists and is unused. Seeding seamounts along plume tracks — dense at the active end, subsiding and drowning with crustal age away from it — is the mechanism, and it replaces "scatter by crustal age". Closes README §10's *"seamounts are not clustered along plume tracks"*. | `seamounts.py`, `seafloor.py` | research 03/01 |
| D3 | **P1** | **Aseismic ridges are plume tracks.** Ninetyeast, Walvis, Rio Grande, Chagos–Laccadive, Cocos, Carnegie, Emperor. The same catalogue closes README §10's *"aseismic ridges and marginal basins are absent or generic"*. | `seafloor.PLATEAUS` | research 03/01 |
| D4 | P2 | **Guyots fall out for free** once D2 is done: a seamount that grew above sea level and then subsided with the cooling plate is flat-topped. Old chains should show flat tops at depth, young ones sharp cones and islands. A drawable prediction. | `seamounts.py` | research 03/01 |
| D5 | P2 | **Add a GDH1-style flattening term to the depth–age law.** Half-space cooling gives 6.9 km at 150 Myr, deeper than almost anywhere real. Measure the change on 100–180 Myr crust. | `seafloor.py` | research 03/01 |
| D6 | P2 | **Link LIPs to their environmental consequence as card content**: Ontong Java → OAE 1a, Caribbean → OAE 2, NAIP → PETM, Karoo–Ferrar → T-OAE, Siberian Traps → End-Permian, CAMP → End-Triassic. No new geometry needed. | `features.EVENT_NOTES` | research 03/01 |
| D7 | P3 | State on plume cards that **hotspots are not fixed** — inter-hotspot motion is demonstrable before ~90 Ma, and the Hawaii–Emperor bend is now widely read as plume motion rather than a change in Pacific plate direction. A track before ~90 Ma is a model output. | card text | research 03/01 |
| D8 | P4 | The deep Mediterranean may be **Palaeozoic Tethyan floor** (Ionian/Herodotus basins, 270–340 Ma) — far older than the 180–200 Ma oldest crust elsewhere. Worth a card if it survives checking. | `features.py` | research 03/01 |

## E. Research programme itself

| # | P | item |
|---|---|---|
| E1 | P2 | **Retry the rate-limited figure fetches.** Nine slots are empty, most because Commons returned 429 — which must not be recorded as an absence. The Glossopteris distribution map (the Suess figure) and the Rodinia reconstruction matter most. |
| E2 | P2 | **Obtain and read**: Torsvik & Cocks, *Earth History and Palaeogeography* (2017); Lyons, Reinhard & Planavsky (2014) *Nature* 506 on oxygenation; Steinberger (2000) on hotspots; Krause et al. (2022) *Annu. Rev.* on Phanerozoic O₂; the PhanDA supplementary data. |
| E3 | P3 | **Fill the empty dossier folders**: `02-continental-crust`, `07-ecosystems-biomes`, `08-timescale-and-methods`, `09-source-documents`. |
| E4 | P3 | Extend `deeptime.STAGES` below the Frasnian — currently complete for the Mesozoic and Cenozoic, representative for the Palaeozoic. |
| E5 | P4 | Consider making the modelling package importable from `build/` (it is dependency-light on purpose) so the app can consume `province()`, `biome()` and the event catalogues directly rather than duplicating them. |

## F. From the resource review and the card audit (round 2, 2026-07-26)

| # | P | item | touches | from |
|---|---|---|---|---|
| F1 | **P1** | **Audit our future series against Scotese's Future World +50 / +150 / +250 maps** — the only external check it has ever had. From `20F250v4.jpg`: Africa at the CENTRE, North America to its WNW, South America SSW, Eurasia east; a "Mediterranean Mts" collisional belt; Antarctica+Australia a SEPARATE southern mass on a narrow neck; an INTERIOR SEA surviving between North America and Africa/Eurasia (Pangaea Ultima is not a solid disc); Pacific occupying the whole opposite hemisphere. | `build_fields.future_grid`, `PLATE_GROUP`, `GROUP_TARGET` | resource review |
| F2 | **P1** | **Add a "climate events" navigable structure** — a fifth panel beside intervals, supercontinents, glaciations and extinctions, using the same `#ctxStack` pattern. It carries the 11 coverage gaps the audit found (PETM, Azolla, OAE 1a/1b/2/3, EECO, MECO, MMCO, GOE, Hirnantian anoxia), all of which are shorter than a keyframe and so can never be drawn. Drafts written. | new panel, `eras_data.json` | card audit |
| F3 | **P2** | **Add the Baykonurian glaciation** (~547–540 Ma), a terminal-Ediacaran glaciation absent from most compilations and from our table. Diamictites in Kazakhstan, Iran, Baltica. Overlaps the Ediacaran biotic turnover. | `climate.py`, `eras_data.json` | Timeline of glaciation |
| F4 | **P2** | **Model back-arc basins by slab roll-back** rather than leaving marginal basins generic (README §10). Figure 10 draws the mechanism; the western Pacific's scatter of small seas is the thing to reproduce. | `seafloor.py` | resource review |
| F5 | **P2** | **Hedge the four contested claims** the audit found stated flatly: giant-arthropod oxygen (×2), post-collapse endemism (×2), Panama closure (×2). Drafts written. | `features.py`, `eras_data.json` | card audit |
| F6 | **P2** | **Add the Permian Basin evaporite succession** as a card — Wolfcamp → Leonard → Guadalupian → Ochoan Castile, with the Capitan reef rimming a basin that strangled itself. The CPGS regional series walks it in eight maps. | `features.py` | resource review |
| F7 | P3 | **Credit Suess as well as Wegener** on the Glossopteris card — Suess used exactly this evidence in 1885 and *named Gondwana*, the name the app puts on every Palaeozoic frame. | `features.DESCRIPTIONS` | card audit |
| F8 | P3 | **State whose future Pangaea Proxima is.** One of four published futures, chosen because Farnsworth et al. (2024) modelled the climate on that geometry. Alternatives: Novopangaea, Aurica, Amasia. | `features.DESCRIPTIONS` | card drafts |
| F9 | P3 | O₂ peak on the Guadalupian card: give ~30%, not ~30–35%. | `eras_data.json` | card audit |
| F10 | P3 | **Retry four rate-limited figure fetches**: Hawaii–Emperor chain, Phanerozoic CO₂ curve, Pangaea breakup sequence, a licence-clean Wilson cycle. A 429 is not an absence. | `fetch_reference_figures.py` | figure review |
| F11 | P4 | Seek an **English** version of the Snider-Pellegrini/Wegener fossil map (ours is German) and of the Rodinia reconstruction (ours is Hebrew). | `collected/` | figure review |

**What the card audit did NOT find:** any HIGH-severity error. 667 cards, 214,000 characters, zero factual errors at HIGH. Two of the three date disagreements the first run reported were errors in **this folder's** catalogue, not the app's — `deeptime.py` was corrected to match the app, which separates the late Famennian pulse from the Late Palaeozoic Ice Age more cleanly than the common convention does.

---

**Count: 50 items — 12 at P1.** The five that would move the app furthest, in order:
**A1** (check for PALEOMAP rotations), **D1+D2** (hotspot catalogue → seamount chains),
**F2** (the climate-events panel — 11 cards already drafted, no geometry needed),
**B1** (province model behind the biota panel), **C1** (PhanDA diff).
