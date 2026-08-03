# Model gaps register

Every open item this research programme has produced, tied to the specific Tectonic Earth
subsystem it would change. **This was the handover surface between research and the build.**

## APPLIED, 2026-07-26 — the handover was executed

The standing rule that this folder does not change the app held for eight rounds. It has
now been **collected in one implementation pass**, and this section records what actually
landed so the register describes the app rather than a wish list.

| item | what shipped | measured |
|---|---|---|
| **A1 · A3 · A4** | `paleo_tracks.py` repointed at `PALEOMAP_PlateModel.rot`; `frame_offset.py`, `frame_offset.json` and `frame_offset.json.raw` **deleted**; every prose reference corrected. Merdith kept for topologies. | abyssal-plain placement **20% → 5%**; labels disagreeing with their terrain ≥⅓ of span **62 → 41**; labels jumping >15° in one step **12 → 6**; per-feature mean **0.819 → 0.971** |
| **the 7 TRUE regressions** | **five were never regressions**: `regression_gate.py`'s land-today guard called `_present_elevation(lon, lat)` on a zero-argument function, so a `TypeError` went into a bare `except: pass` and the guard passed everything. Fixed. Newark Rift Valleys' coordinate was in the **Caribbean** (−68, 12) — corrected to the Newark Basin. Cimmerian Belt re-anchored from a PALEOMAP polygon boundary onto Central Iran. Rhodope re-anchored onto the massif and its residual **recorded as a known limit**. | **TRUE regressions 7 → 0**, on a harness that now scores 124 features instead of 158 phantom ones |
| **C1 · C3 · C4 · F9** | Cretaceous 30.0 → **33.0 °C**, Palaeocene–Eocene raised, Devonian shape corrected, O₂ peak 36% → **30%**, Guadalupian card fixed | `climate_audit.py` **6 findings → 1**, and that one is the faint-young-Sun check *passing*. 90 Ma now reads **hothouse** — the app had never reached that state. `ice_audit.py` unchanged at 23/23 |
| **D1 · D2 · D3 · D4** | `hotspots_cat.py` bridges the 53-plume catalogue into `seamounts.field()`, which had been placing its 34 plumes by **hashing a seed**. Ten named aseismic ridges get surveyed traces; `summit_depth()` sets every catalogued summit's absolute depth from its own age. | Midway **−77 m** (atoll), Meiji **−2111 m** (guyot), Ninetyeast −1255 to −2587 m, Iceland/Réunion/Azores/Cape Verde/Samoa/Society/Marquesas/St Helena **emergent**. Open-abyss controls unmoved. New land **0.012%** of the globe, all of it real island groups |
| **B1 + B1 coverage** | `provinces.py` emits a province per label per age as runs; `exception: true` on the ten distinctive localities; `lifeSection` reordered to exception → province → **labelled global**; the biota panel widened to orogens, basins, rifts, deserts and plateaus | **235 of 336 labels** showed one global list; now **315 are placed in a named province**. The Urals, the Verkhoyansk Belt and the Sahara had **no biota panel at all** and now name their province and its taxa |
| **F2 · C5 · F3 · F5 · F6 · F7 · F8 · D6 · D7 · B9 · C8** | a fifth navigable panel, **Climate events**, on the `#ctxStack` pattern with 7 cards covering all 11 gaps; the Baykonurian glaciation; four hedges; Suess on Glossopteris; Permian Basin, back-arc and atoll/guyot cards; LIP→consequence links; the not-fixed-hotspots caveat; six model-generated figures shipped | `audit_cards.py` **0 HIGH / 11 MED / 6 LOW → 0 / 0 / 0** |
| **A6 · A7 · G6** | a *What longitude is, and is not* section on the About page with the measured numbers, and README §9 | 5°/12°/73° mean \|Δlon\| by era, 146° at 500 Ma, 60° between Scotese's own editions |
| **E5 (adopted)** | `build/audit_all.py` runs every validator against a recorded baseline and **`build_site.py` refuses to publish if one moved backwards** | 8 checks, all at baseline |
| **E6** | already fixed in `frame_experiment.py`; both it and `regression_gate.py` now **pin every frame by name** rather than reading the build, so neither becomes a no-op the moment the switch lands | WP-04's three-way result reproduces to 1 pp |

### Round 2 of the same pass, 2026-07-27 — G1, G2 and G3

| item | what shipped | measured |
|---|---|---|
| **G1** | `epeiric.py` extended from two named seas to ten, reaching the Triassic–Jurassic at last (Germanic/Muschelkalk, Zechstein, Sverdrup, West Siberian, Sundance, Russian Platform, Neuquén, Alpine Tethyan) — plus a **Pangaean margin shelf**, because the named basins are only a third of the deficit. The shelf's target is derived from **our own source grids**: each frame against the median of its ±70 Myr neighbourhood, because the raw PaleoDEMs swing 8.6→4.5→3.0→6.3→1.6→8.2→13.8% across seven adjacent frames while sea level slides smoothly, which is authoring and not geology. Blakey scores the target and never sets it. | mean absolute shelf error over 150–250 Ma **2.80 → 0.70 pp**; the target itself scores 0.68 pp against Blakey. **No age made worse**, 0 Ma control untouched. Two solver findings recorded in README §5.2: the weight must set which ground floods rather than how deep (the naive form stepped 6.3→11.2% in one increment), and a frame whose smallest expressible flood overshoots is left alone. |
| **G2** | `_packed_targets` in `build_fields.py`. No collision rule can fix stacked land — whichever cell you keep, the other has nowhere to go — so the *targets* are relaxed until the groups only touch: mass-weighted, and sprung back to the authored arrangement so the packing changes and the reconstruction does not. | raw land at +250 Myr **97.1 → 133.1 Mkm²**, a **35.5% → 11.6%** loss against a 5.5% rasterisation floor. The signature is gone too: land >1 km flat at 29.9 → 29.4, and mean land elevation rises **56 m instead of 212**. |
| **G3** | falls out of the same relaxation | **r90 59.9° → 76.6°**, against PALEOMAP's own 76°. |
| **F1 audit** | `audit_reconstruction.py:our_future_rotations()` rebuilt the rotation from `GROUP_TARGET` directly, so it never saw the packing — the exact failure its own docstring says it exists to avoid. It now reads `_packed_targets`. | second time in this programme an audit stopped tracking the pipeline it audits; see also `regression_gate.py`'s land-today guard. |

### Round 3, 2026-07-27 — the rainfall coupling, G4, G5, and G7+G8 answered

| item | what shipped | measured |
|---|---|---|
| **rainfall coupling** | `export()` ran the wind-and-moisture solve on the RAW paleo-DEM while everything else used the carved one, so every seeded sea changed the coastline without making the air over it wetter. The Phanerozoic path now passes the carved grid (`Zhi[::-1]` — `resample_dem` returns north-first, `compute_fields` wants ascending, and getting that backwards renders the world upside down). Future and Precambrian keep their own climate-resolution grids, which carry their own eustatic corrections. | at 240 Ma, land that is still land **0.104 → 0.122 (+17%)**, the deep Pangaean interior **+11%**, within four cells of the new coast **+13%**. Global mean falls only because 6% of the grid moved from land, where this model reports rainfall, to sea, where it reports almost none. New `rerender_rain.py` does it in 6 minutes without touching elevation or the manifest. |
| **G4** | `GROUP_TARGET` re-aimed by search against the six published claims rather than by eye. | bearings from Africa at +250 Myr — **North America 331° → 293°** (published 298), **South America 252° → 203°** (201), **Eurasia 36° → 65°** (66). Mean error **38° → 3°**. Australia now sits **6,321 km from Africa on bearing 152° and 3,933 km from Antarctica**, a separate southern mass, where it was 2,969 km due east of Africa and welded into the main mass. Land goes *up* as a side effect, 126.1 → 128.5 Mkm². |
| **G5** | **Collisional uplift along the sutures.** Now that the groups are packed to meet rather than interpenetrate there is a contact to work with: where two groups' land abuts, crust thickens, growing with the assembly. Two calibration findings recorded in the code — normalising the belt by its own maximum turns it into a plateau (26 Mkm² above 2 km, a world of mountains), and a gaussian is too broad-shouldered for an orogen, so the belt is raised to a power. | land above 2 km **8.8 → 13.8 Mkm²** across the series where it was flat at 8.7 → 8.6; above 1 km 29.9 → 36.3; mean land elevation 620 → 781 m. Sized against the Alpine–Himalayan belt, which is ~5 Mkm². |
| **G7 + G8** | **Answered, and they are the same finding.** Our own Cambrian series is smooth — land 18.6% at 540 Ma → 16.6% at 525 → 17.2% at 500, moving in step with our eustatic curve — so our 525 Ma frame is not anomalous; Blakey's is, dropping 11 points in 25 Myr against his own neighbours. But the deeper result is that the disagreement is not about land at all: at 525 Ma **land + shelf agrees to 1.0 pp** (Blakey 31.7%, ours 32.7%) while **land alone differs by 10.1**. The two reconstructions agree about how much continental crust existed and disagree about how much of it was above water — which is exactly what G8 records for the rest of the Palaeozoic. One disagreement, not two. Recorded, not tuned. | 525 Ma land-only −10.1 pp, land+shelf **+1.0**; 470 Ma −2.1 / +5.2; 420 Ma −2.5 / +5.8 |

### Round 4, 2026-07-27 — B2, B4, B6, B9, C2, C8, D5, and a bug class found by machine

| item | what shipped | measured |
|---|---|---|
| **B2** | **The province model was never the problem; nothing was reaching it.** `provinces.py` resolved a label's `block` by NAME, so only the 56 labels that *are* cratons ever reached the block-keyed branches — every mountain belt, sea and basin handed the model a `None` and fell through to its two latitude bands. Matching on present-day position does not work either, because a label's coordinate is its *palaeo*-position. Block anchors are now reconstructed into the same frame the labels ride and matched at the age asked about. Reach set by measurement (1700 km) against 17 labels whose block is not in doubt; distance-weighting the whole block was tried and is worse. Oceans are never given a block — open water sits on no craton. | distinct provinces **49 → 59**. The Ordovician, the most provincial interval of the Palaeozoic, had been showing the *fewest*: 450–485 Ma **3 → 4–5**, with the Baltic and Mediterranean (peri-Gondwanan) shelves appearing. Not just the Ordovician — 500 Ma gains the **Olenellid, Redlichiid and Bigotinid** trilobite provinces, 400 Ma the **Eastern Americas Realm**, 0 Ma the four modern terrestrial realms. 12 → 17 at the present day. |
| **the silent-tracking trap** | **A bug class, found by machine and closed with a validator.** `build_labels()` treats a coordinate that is land today as present-day and plate-tracks it; one on today's ocean is understood to be authored in its own era's frame and left alone. The blind spot: a *palaeo* coordinate that happens to fall on modern land is tracked anyway, on whatever continent now occupies that spot. Nothing complains — the label still draws and still moves, it is simply riding the wrong continent. New `audit_label_plate.py` cross-checks every tracked label's plate against the continents its own text names, with 14 genuinely trans-continental features listed as exemptions. | **11 labels found and corrected**, the same defect as the hand-found Newark Rift Valleys: **all four of Sloss's cratonic sequences** (Sauk, Tippecanoe, Kaskaskia, Absaroka — the floodings of *Laurentia*, all authored in the Caribbean, all riding South America and carried to 67°S while the continent they flooded sat on the equator), plus **Laurentia** itself (→ Guyana), **Catskill Delta** (→ Brazil), **Variscan Belt** (→ Sahara), **Caledonides** (→ Western Sahara), **Muschelkalk Sea** (→ Libya) and **Sveconorwegian Belt** (→ Algeria). Each re-anchored on the locality it is named for. Validator now at **0 findings** and registered in `audit_all.py` as a ratchet. |
| **D5** | GDH1 (Stein & Stein 1992) replaces pure half-space cooling. `2600 + 350√t` reaches 6.9 km at 150 Myr, so it was clipped at `MAX_ABYSS`; a clip is not a flattening — it made the model term *constant* across all crust older than 97 Myr, which is **34.2% of the sea floor**, so a third of the ocean had no large-scale depth gradient in it at all. | **Scored against real bathymetry**, 582,736 surveyed deep-ocean cells at 0 Ma, area-weighted: mean absolute error **794 → 654 m**, bias **+715 → +549 m** (the old law was systematically too deep). Per age band it improves exactly where the old one saturated: +127 m at 50–80 Myr, **+369** at 80–100, **+406** at 100–130, +292 at 130–190. Two young bands come out nominally 17 and 23 m worse — below a fifth of the 105 m elevation quantum at abyssal depth, so not expressible in the shipped field. Cells pinned near the old 6000 m clip: **0.06%** of the deep floor. Seamount summits deliberately stay on √t (calibrated to the Hawaiian–Emperor chain; coupling them pushes Midway over the atoll/guyot line), and edifice heights already derive from the actual floor, so nothing floats. |
| **B4** | size, habit and diet carried onto every taxon card from `taxa_db`, in one pass over the finished payload rather than three enrichment paths. Sizes print in the unit a reader would use — 2.5 m, 70 cm, 3 mm. | the 273 silhouettes were far ahead of the text: a card could draw an animal correctly and never say how big it was or what it ate. |
| **B6** | vegetation gating was already correct via the CLIMATE table's `veg` column (0.00 at 500/700/1000 Ma, 0.05 in the Silurian, 0.95 by 300 Ma) — but **grassland was not gated at all**, so a 100 Ma world drew grass. New `uGrass` uniform pulls the dry axis off its grassy stops and mutes the savanna stipple before ~40 Ma, fully before ~70. | grasses matter ecologically only from ~40 Ma, C4 savanna from ~8 Ma. |
| **C2** | the readout's climate state is named from **PhanDA's thresholds on the GMST the readout itself prints**, not from `temp`, the −1..+1 shader proxy, which is a different quantity with different breakpoints. | at 250 Ma the panel read "28.5 °C" and "Hothouse" side by side; 28.5 °C is a *warm greenhouse* in the scheme being invoked. 150 and 200 Ma likewise move to cool greenhouse. The two halves of the line now agree. |
| **C8 · B9** | all five disputed supercontinents printed **one identical sentence** — the same defect the province cards had. Each now says what is actually argued over: whether Pannotia assembled at all, and which ocean each of the four rival futures closes. B9's Euramerican qualifier carried from the interval cards into the biome texts, which still said the rainforest collapse plainly. | Kenorland, Vaalbara and Ur are Archean and correctly absent from a 1000 Ma model. |

**C9 — RESOLVED, no action.** The item asks that ocean anoxia be drawn as sea-floor
sediment rather than as water colour, because anoxia is subsurface: the Black Sea is
euxinic below ~100 m and looks entirely normal from a boat. Checked: **the app has never
coloured water for anoxia.** OAEs appear only as cards, in the Climate events panel added
for C5/F2 — which is the right place for them anyway, since every one of them is shorter
than the 5 Myr between keyframes. There is nothing to correct.

**C7 — RESOLVED.** The choice had already been made and argued in `build_frames.py`: the
Haq family (Haq & Schutter 2008), with van der Meer's independent tectono-eustatic
reconstruction agreeing closely, and an explicit rule never to mix in the Miller
backstripping family, which puts the Cretaceous high stand at about *half* this. What was
missing was telling the reader — the About panel said "Haq/Hallam sea-level curves",
plural, naming a curve the app does not use. It now names the one it does, states that the
rival family disagrees by a factor of two, and quotes the 2016 review's own verdict on the
field.

**B8 — DELIVERED.** A **sixth navigable panel, Biotic interchanges**, on the same
`#ctxStack` pattern as the Climate events panel and for the same structural reason: the map
cannot draw this. A land bridge is a few tens of kilometres of ground, and both Panama and
the Bering Strait are far below what a 20 km grid resolves, so the globe can show two
continents approaching and never show the moment they connect — which is the only moment
that matters. Four cards, each with what opened the route, who crossed, who won, and what
is still argued over: the **Great American Interchange** (and why it was so lopsided — the
current reading is asymmetry of opportunity, not competitive superiority), the
**Trans-Arctic Interchange** (the mirror image, at almost the same moment: Panama closed a
seaway as Bering opened one, ~300 Pacific species into the Atlantic against a few dozen
back), the **Grande Coupure** (where the land bridge and the cooling arrive together
because the same sea-level fall did both), and the **Lystrosaurus Flood** (not an
interchange but its opposite — provinciality collapsing on an emptied Pangaea). Figures
assigned only where the diagram is honestly about the mechanism; the Trans-Arctic card gets
none, because a seaway-closing diagram would argue the opposite of its own caption.

**B5 — DELIVERED, and it was bigger than the item said.** The realm filter is derived from
the label's *type* (`ocean`/`sea` → marine), which is only a proxy for the realm a locality
actually spans, and it was being applied to **all three tiers** of the biota panel. It
belongs on one: the global interval list, which is about the world rather than about this
place, so putting its land animals in an ocean is a genuine error. A *curated* list is the
opposite case — somebody catalogued what lived at this place at this age, and running that
through a guess about the place discards the better answer for the worse one.

Measured: the filter was silently hiding curated taxa on **37 label-spans**. Solnhofen is
the case the register named — a marine lagoon whose entire significance is the pterosaurs
and *Archaeopteryx* that fell into it, all dropped for being `air` on a `sea` card — and
the Hudson Seaway lost *Hesperornis* the same way. But the bulk of it ran the other
direction: **continent cards denied their marine fauna.** Cambrian Laurentia's curated list
is four taxa and all four are marine, as the Cambrian must be, so a `continent` card kept
none of them and fell through to the global list. Same for Baltica, Siberia, Avalonia,
Gondwana, South China, the Kalahari and Congo cratons, and Rodinia. The curated tier is now
shown as authored; the global tier is still filtered.

**B11 — RESOLVED, and it found a real error.** The three Devonian realm names were checked
against the primary source: **Boucot, Johnson & Talent (1969), *Early Devonian Brachiopod
Zoogeography*, GSA Special Paper 119** — the paper that established these units and still
the framework the field uses. The *names* check out. The *ages* did not. The source is
explicit that this is an **Early** Devonian structure: by the Givetian the Malvinokaffric
Realm is gone, the Eastern Americas Realm is much reduced, and the Old World Realm has
spread over most of what the other two held. Our model held all three constant across the
whole period, so it drew the Devonian getting *more* provincial when the record shows it
becoming markedly less. Gated at the Givetian (387.7 Ma), with a cool-water southern shelf
taking over from the Malvinokaffric so its disappearance reads as the cosmopolitanism it
was rather than a hole in the model. Verified: Malvinokaffric present at 400–390 Ma, gone
by 385.

**D8 — RECORDED as a known limit.** `MAX_CRUST_AGE = 190` Myr is correct for the world's
ocean floor — anything older has been subducted, which is why no Jurassic Pacific survives
— but the deep eastern Mediterranean is the probable exception: the Ionian and Herodotus
basins may be Palaeozoic Tethyan floor at **270–340 Ma**, trapped behind Tethys's closure
rather than consumed with it. The app draws them at 190 Myr like everything else, so they
come out a few hundred metres too shallow with the wrong fabric age. The dating is
contested and the basins sit under kilometres of Messinian salt. Written into README §9
rather than special-cased: one basin's disputed age does not earn a branch in the depth
law.

**D9 — the crustal-age field is a Voronoi tessellation, and that is the deeper fix still to
make.** `crustage.build` assigns every cell the age of the NEAREST isochron *within its own
plate*, so the field comes out as flat facets with a hard step at every isochron Voronoi
boundary and, worse, at every PLATE boundary — long straight polygon edges. Measured at
615 Ma: the 99.5th percentile age change between adjacent cells is 70 Myr, which the
depth–age law renders as a **1,349 m wall across 25 km**. That is the origin of the large
angular slabs in the deep ocean, and it is worst in the Precambrian, where the plate model
has almost no isochrons to interpolate between.

Interpolating between the four nearest isochrons (inverse-distance) was implemented and
measured: it takes the step from 70 to 47.5 Myr, i.e. 1,349 m to 1,061 m. Better, and not
enough on its own, because the residual is at PLATE boundaries where the per-plate searches
meet. It was reverted only because it invalidates 2.7 GB of isochron cache across 251 ages,
which is hours of pyGPlates work — worth doing, but as its own pass. The shipped fix
instead smooths the age **for the depth term only** (3.3°, bringing the step to ~90 m per
cell, inside the 50–125 m a real abyssal plain does) and leaves the raw age to the fabric.
The remaining known cost is that fracture-zone detection still sees the artificial plate-edge
steps and can draw a false scar along one.

**D10 — draw the Messinian Mediterranean.** The Pliocene card already says the
Mediterranean had just spent 600,000 years as a desiccating salt desert two kilometres below
sea level, and the app never shows it. The labels exist (`Messinian Salt Basin` 5–6 Ma,
`Lago Mare (Messinian Mediterranean)` 5.33–5.6 Ma, with curated biota flagged as an
exception locality); only the terrain is missing.

*The mechanism exists and is proven.* The Holocene lakes use exactly this pattern: a variant
texture for one frame (`phan_0000_wold.webp`) plus a sharp age gate
(`holoceneLakeWeight(age)`: `if (age > 0.02) return 0`). The same shape works here.

*Timing, and it matters.* The crisis runs 5.96–5.33 Ma, peak desiccation ~5.6–5.5 Ma, ended
by the Zanclean flood at 5.33 Ma. Keyframes are at 5 and 10 Ma, so **the 5 Ma keyframe is
already refilled** — 330 kyr too late. The depiction therefore has to be gated on AGE inside
the interpolated 10→5 Ma window (~5.9–5.4 Ma), not painted onto the 5 Ma frame. That is what
the lake gate already does, so this is a feature of the pattern rather than a fight with it.

*The open technical question, to settle first.* The shader decides land from the sign of
elevation. A basin that is 2 km **below** sea level and **dry** cannot be expressed by
elevation alone — it would render as ocean. This needs an explicit "subaerial despite being
below the datum" mask, analogous to the lake-depth field. Confirm the exact land/sea test
before designing anything else; it determines whether this is a new field or a channel on an
existing one.

*What an accurate depiction contains:*
- basin floor exposed at roughly −1.5 to −2 km, with the deepest sub-basins lower
- evaporites: about a million cubic kilometres of halite and gypsum, so a pale salt-flat
  surface in the deep basins rather than ordinary ground
- **Lago Mare** — residual brackish/hypersaline lakes in the deepest sub-basins (Balearic,
  Tyrrhenian, Ionian, Levantine), not one continuous sheet
- Gibraltar closed, so Iberia and Morocco are joined; the Sicily sill divides west from east
- the incised canyons, which are the most striking part and are real and mapped: the Nile cut
  a gorge ~2.5 km deep at Aswan, the Rhône one over 1 km deep near Lyon, both graded to the
  drawn-down base level

**B13 — every deep-time LAND card is plants only, with no animals at all.** Confirmed by
reading the marker list of all 23 terrestrial provinces. The cause is structural, not an
oversight: the terrestrial schemes in `paleobiogeography.py` are *floral* provinces --
`_cenozoic_flora`, `_mesozoic_flora`, `_carboniferous_permian_flora`,
`_devonian_carboniferous_flora`. Palaeobotanical provinces are the standard way to divide
Palaeozoic and Mesozoic land, which is why the model was built that way, and the consequence
is that **the app can never show a land animal from a province card**:

| province | markers | animals |
|---|---|---|
| Euramerican Province | Lepidodendron, Sigillaria, Calamites, Medullosa, Cordaites | **0** |
| Gondwanan Province | Glossopteris, Gangamopteris, Vertebraria, Noeggerathiopsis | **0** |
| Cathaysian Province | Gigantopteris, Lobatannularia, Cathaysiodendron | **0** |
| Angaran Province | Rufloria, Cordaites, Vojnovskya | **0** |
| Dicroidium Flora | Dicroidium, Umkomasia, Pleuromeia | **0** |
| Cosmopolitan Jurassic gymnosperm flora | Williamsonia, Ptilophyllum | **0** |
| Early angiosperm flora | Archaefructus, Nymphaeales, Platanaceae | **0** |
| Archaeopteris forest | Archaeopteris, Wattieza, Prototaxites, Elkinsia | **0** |
| Early tracheophyte ground cover | Cooksonia, Baragwanathia, Rhynia | **0** |
| Boreal conifer forest / tundra / rainforest / desert belts | all plants | **0** |

The only terrestrial provinces with any fauna are the seven modern realms, and only because
they were given some in this round. Everything from the Silurian to the Pliocene shows a
reader vegetation and nothing that moves -- no tetrapods, no insects, no dinosaurs, no
mammals, on any land card at any age.

*Fix:* add characteristic FAUNA alongside the flora in every terrestrial province -- e.g.
Euramerican coal forest: *Arthropleura*, *Meganeura*, *Hylonomus*, *Eryops*; Gondwanan:
*Lystrosaurus*, *Dicynodon*, *Mesosaurus*; Dicroidium flora: *Cynognathus*, *Thrinaxodon*;
Jurassic gymnosperm flora: *Allosaurus*, *Stegosaurus*, *Diplodocus*; Archaeopteris forest:
*Ichthyostega*, trigonotarbids. Roughly 20 provinces x 2-3 taxa, most needing a description
in `MARKER_NOTES`. `taxa_db` already covers many of them, and the province selftest (now
block-aware and wired into `audit_all`) will catch any that lack one.

*Also worth doing at the same time:* rename the province where the name is now wrong. A
province carrying both flora and fauna should not be called "Dicroidium **Flora**" on a card
that lists a cynodont.

**Still open: nothing else that changes the app.** The remaining register items are E1–E3, which
are about the research folder itself — retrying rate-limited figure fetches, obtaining two
paywalled sources, and filling four empty dossier directories. E2 and F10/F11 were already
closed as negative results after repeated attempts.

Priority: **P1** = closes a known visible defect · **P2** = adds real fidelity ·
**P3** = correctness housekeeping · **P4** = worth knowing, no action yet.
Status: **RESOLVED** = answered, with the answer recorded · **MEASURED** = quantified and
ready to apply · **RETIRED** = no longer needed · items with no status are open.

## The no-regression gate (2026-07-26)

`modeling/regression_gate.py` + [NO-REGRESSION-PROTOCOL.md](research%20reports/NO-REGRESSION-PROTOCOL.md)
answer "will this reduce the accuracy of any individual frame?" for the frame switch:
**58 improved, 79 unchanged, 21 regressed of 158 tracked features; mean 0.746 → 0.833; only
7 true regressions, four of which look like data errors the switch exposed.** §5 of the
protocol lists the pre-existing quantitative gate every other staged change must not move
backwards.

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
| **A5 / F1** | **HANDED OFF → MEASURED, see the round 8 table below** | [`HANDOFF-A5-F1-reference-map-audit.md`](HANDOFF-A5-F1-reference-map-audit.md) — a self-contained prompt for a parallel session. Needs image reprojection and comparison at scale, which is its own job. |
| **B10** | **PARTIAL** | `taxa_db.py` 105 → **114**. Honest correction: 12 of the 21 taxa I drafted were ALREADY in the database — the "mid-Cambrian–Silurian thin patch" diagnosis was half wrong. The Cambrian was fine (16); the real gaps were the **Ordovician (14)** and **Silurian (15)**, now filled with *Sacabambaspis*, *Aegirocassis*, *Promissum*, *Pterygotus*, *Arandaspis*, *Birkenia*, *Favosites*, *Aysheaia*, *Haikouichthys*. Its selftest caught all three of my mistakes: duplicates, a missing optional field, and a zero-length age range. |
| **E5** | **DELIVERED** | Every module is stdlib-only except `climate_ebm`/`ocean_circulation` (numpy, already a project dependency), so `build/` can import any of them with a two-line `sys.path` insert. Verified. |
| **B1** | **DECIDED + AUDITED** | Design chosen: *model decides, curated is a flagged exception*; unplaced points get the global list **explicitly labelled as global**. `modeling/audit_curated_biota.py` split all 198 curated spans: **9 exceptions, 67 province-typical, 121 the model cannot place, 0 conflicts.** The bottleneck turns out to be the PROVINCE MODEL'S COVERAGE, not the curated data — so extending `paleobiogeography.py` comes before any wiring. |
| **B1 coverage** | **DELIVERED** | The province model was **vastly extended** and the bottleneck is closed. New schemes: Tonian–Cryogenian marine (1000–635 Ma, incl. both snowball oceans), Ediacaran (Avalon / White Sea / Nama), Ordovician split out with its five named shelf provinces, Silurian split out (cosmopolitan + Malvinokaffric), Triassic split out (post-extinction flattening), Cenozoic marine rewritten around gateway tectonics, and a Silurian–Devonian land-colonisation sequence. Plus **named latitudinal fallbacks** so no cell is ever an unnamed shrug. **49 distinct provinces across 0–1000 Ma.** Curated spans placed: **67 → 188, unplaced 121 → 0.** |
| **B7** | **DELIVERED** | `modeling/lagerstatten.py` — **30 Konservat- and Konzentrat-Lagerstätten** with present-day coordinates, block, window, setting, and what each shows that nothing else does. Its selftest caught the real trap: nine sites named `Laurussia`, which is an *assembly* and has no plate to ride — corrected to the craton each sits on. |
| **C6** | **DELIVERED** | `modeling/ocean_circulation.py` — wind-driven surface circulation from a land/sea mask alone: banded wind stress → Sverdrup interior → westward integration → western boundary current, plus eastern-boundary upwelling and a circumpolar test. **Closing Drake Passage switches the ACC off**, which is the 34–23 Ma story from geometry alone. Two bugs found by its own selftest: the closure test put the land bridge in the northern hemisphere, and the circumpolar test was satisfied by the *Arctic* (a ring of water round a pole is not a current — the jet needs the westerly belt). Honest limitation recorded: psi is a westward ramp per row, so it wants streamlines, not a per-pixel fill. |

---

## Round 8 resolutions (2026-07-26) — see [WP-05](research%20reports/WP-05-reconstruction-audit.md)

The reconstruction measured against two published series on 31 ages, by
[`modeling/audit_reconstruction.py`](modeling/audit_reconstruction.py) (read-only, re-runnable
after the PALEOMAP switch lands). **The reference images are copyrighted and are never
reproduced — only measured against, and never committed.**

| item | status | result |
|---|---|---|
| **A5** | **MEASURED** | Present-day control passes hard: **96.8%** land/sea agreement, IoU **0.897**, Δlon **0°**, 3 km mean displacement, reference land 28.8% against Earth's 29.2%. Land area then tracks Blakey's independent reconstruction with a mean bias of **+1.6 pp over 31 ages**, 25 of them inside ±4 pp. Position agrees to **5° of longitude in 0–100 Ma** and **12° in 100–260 Ma**; from the Devonian back the two diverge to **73° mean**, with kappa falling to **−0.04 at 420 Ma** before a rigid rotation and recovering to 0.47 after one. Palaeolatitude agrees throughout (RMS 6.7–9.5%, r 0.87–0.97 at 400–525 Ma), which is the longitude problem's exact signature. |
| **A5 frame** | **RESOLVED — the Palaeozoic offset is not ours** | Triangulated against a third witness, `PALEOMAP_PlateModel.rot` applied to present-day land: **our terrain sits in the PALEOMAP frame to within 2° at every one of ten ages, 50–500 Ma.** DTM sits at +7° to **−146°**. So two published reconstructions differ by up to 146° in the early Palaeozoic and we are faithful to the one we are built from. Terrain-side confirmation of WP-04 §1. Separately: **Scotese's own numbered plates (~2000) differ from his 2016 rotations by up to 60°** in the Palaeozoic — his own revision, not our error. |
| **A5 shelf** | **MEASURED, one big defect** | The reference's shallow tint was calibrated at 0 Ma (9.53% of surface = our z > −1305 m) and frozen. The 0 Ma control passes (Δ −0.1 pp). **The Triassic–Jurassic fails badly: at 240 Ma we draw 1.8% shallow sea against 8.0%, and 93% of everything Blakey draws as shelf sea is dry land in ours** (83% at 200 Ma, 77% at 180). That is the whole of the +5 to +9 pp land excess at those ages — not extra continent, missing sea. From 360 Ma back the sign reverses: we draw 3–11 pp *more* shallow sea than he does. |
| **A5 ice** | **CHECK PASSED, and the reference cannot carry the pattern test** | Across **fourteen consecutive keyframes 50–250 Ma both reconstructions carry no ice sheet** (DTM's residual 0.00–0.04% is single-pixel mountain snow below 30° latitude; ours is exactly zero). At the Palaeozoic maxima **we are inside `ice_audit.py`'s literature range and DTM is below it** — 16.5% of land at 300 Ma against a 10–22% target, versus DTM's 7.0%; at 320 and 440 Ma Blakey draws essentially no polar ice where the record has a Pennsylvanian maximum and the Hirnantian. The **spatial** pattern check cannot be delivered: at 0 Ma, where both sides describe the same real ice sheets, ice IoU is only **0.430**, which is the noise floor, and no deep-time age approaches it. |
| **F1** | **MEASURED — the largest single defect found** | PALEOMAP's future rotations were validated first (advected to −250 Ma they do reproduce the Future World arrangement), then used as the yardstick. **Our future series destroys 37% of Earth's continental area: 148.1 → 92.6 Mkm² over 250 Myr, where rigid rotation loses 5.5%.** The loss is concentrated in ground below 1 km (−45%) while land above 2 km is flat (8.7 → 8.6 Mkm²), and mean land elevation rises 667 → 879 m — the exact signature of `future_grid`'s `out = np.maximum(out, z)` deleting the lower of two overlapping groups. |
| **F1 claims** | **2 hold, 2 partly, 2 fail** | **Africa at the centre** ✓ (962 km from the centroid of all land, nearest of any group). **Pacific over the opposite hemisphere** ✓ (emptiest hemisphere 0.2% land). **N America WNW ✓ / Eurasia east ✓ / S America 247° where Scotese gives 201°** — partly. **An interior sea survives** ✓ in kind (12.2 Mkm², 13% of our land area, against PALEOMAP's 20.6 Mkm² and 13%) but its shore is 30% South America and only **6% North America** — the sea is real, between the wrong continents. **"Mediterranean Mts"** ✗ — no orogeny is built anywhere, by construction. **Antarctica + Australia a separate southern mass** ✗ — Australia sits 2,969 km east of Africa, welded into the main mass. |
| **F1 timing** | **MEASURED** | Pangaea Proxima closes **~100 Myr early**: our emptiest hemisphere is at 0.3% by +150 Myr where PALEOMAP is still at 12.6%, and ours ends **too compact** (r90 60° against 76°). |
| **E6 (new)** | **FOUND** | `modeling/frame_experiment.py:_decode()` uses `Z_RANGE = 11000.0`; `build/fieldpack.py` and every other consumer in `build/` use **8000.0**, and the A5/F1 handoff prompt propagated the error. WP-04's headline is untouched (one threshold across all three frames, so the ranking cannot move) but its "shelf" boundary is really **−364 m**. Sixth time the research's own table has been the wrong one. |

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

## G. From the reconstruction audit (round 8, 2026-07-26) — [WP-05](research%20reports/WP-05-reconstruction-audit.md)

Every item here is a measurement, not an impression, and every one is re-checkable with
`modeling/audit_reconstruction.py`. G1 and G2 descend from A5 and F1 respectively.

| # | P | item | touches | evidence |
|---|---|---|---|---|
| G1 | **P1** | **Flood the Triassic–Jurassic epicontinental seas.** `epeiric.py` exists precisely for the seas a 20 km grid cannot resolve and it does not reach 150–250 Ma. At **240 Ma we draw 1.8% shallow sea against Blakey's 8.0%, and 93% of everything he draws as shelf sea is dry land in ours** (200 Ma: 3.1% vs 8.0%, 83%; 180 Ma: 4.7% vs 8.1%, 77%). This is also the whole of the +5 to +9 pp land excess at those ages, so one fix closes both. Largest terrain defect the audit found. | `epeiric.py`, `build_fields` | WP-05 §4 |
| G2 | **P1** | **Stop the future series destroying continental area.** 148.1 → 92.6 Mkm² over 250 Myr, a **37% loss**, against 5.5% for a rigid rotation. Cause is one line in `future_grid`: `out = np.maximum(out, z)` resolves group overlap by deleting the lower ground, so the loss falls almost entirely on land below 1 km (−45%) — coastal plain, shelf and continental interior, which is the ground a biosphere lives on. Any of: assign overlapped ground to one group, pull `GROUP_TARGET` apart so groups meet rather than interpenetrate, or conserve area explicitly. | `build_fields.future_grid` | WP-05 §6.1 |
| G3 | P2 | **Slow the future assembly and loosen it.** Our emptiest hemisphere reaches 0.3% land by **+150 Myr**; PALEOMAP is still at 12.6% there and only closes to 1.3% at +250. At +250 ours is too compact: **r90 60° against 76°**. Both follow from `GROUP_TARGET` aiming every group into a narrow lon/lat window. | `GROUP_TARGET` | WP-05 §6.2 |
| G4 | P2 | **Rearrange the future groups so the neighbours are right.** Australia sits **2,969 km east of Africa on bearing 85°**, welded into the main mass, where Scotese has it forming a separate southern mass with Antarctica. The interior sea's shore is 30% South America / 23% Africa / 23% Antarctica / **6% North America**, where the reconstruction our climate is calibrated on puts it between North America and Africa/Eurasia. | `GROUP_TARGET`, `PLATE_GROUP` | WP-05 §6.3 |
| G5 | P2 | **Say that the future series builds no mountains, or build them.** Land above 2 km is **8.7 → 8.6 Mkm²** across the whole series: rigid rotation plus `maximum` has no mechanism to raise an orogen, so the "Mediterranean Mts" belt of Scotese's Pangaea Ultima cannot appear. Pairs with F8 (whose future this is). | `build_fields`, card text | WP-05 §6.3 |
| G6 | P3 | **Put the Palaeozoic longitude limit on the About page with the measured number.** Two published reconstructions differ by up to **146°** at 500 Ma, and Scotese's own model moved by up to **60°** between editions. A6 already asks for the honest limit; this is the number to quote. Also worth saying that palaeolatitude *does* agree (RMS 6.7–9.5%) — the uncertainty is one-dimensional, not general. | `web/index.html` About | WP-05 §3.1 |
| G7 | P3 | **Resolve the 525 Ma land-area disagreement.** DTM says 26.7% land, we say 15.0% — the largest single-age gap in the series, and the only Cambrian age that disagrees at all (500 Ma agrees to 0.1 pp). Blakey's own land drops 26.7% → 15.8% across those 25 Myr, so the anomaly may be his. Check the 525 Ma PaleoDEM against the Sauk transgression literature before assuming either. | `build_fields`, research 01 | WP-05 §2 |
| G8 | P4 | **The Palaeozoic shelf disagreement runs the opposite way and is unexplained.** From 360 Ma back we draw **3–11 pp more** shallow sea than Blakey, and 25–45% of what he draws as dry land is under water in ours — while land *area* agrees to within a point. The two reconstructions disagree about how much of the same continent is flooded, in opposite directions in the two eras. Record it; do not tune to it. | — | WP-05 §4 |
| E6 | P3 | **Fix `frame_experiment.py`'s `Z_RANGE`**: 11000.0 → 8000.0, to match `build/fieldpack.py`. Re-state its shelf boundary (it is −364 m, not −500 m) and correct the handoff prompt that propagated it. WP-04's ranking is unaffected. | `modeling/frame_experiment.py` | WP-05 §0 |

**What the audit did NOT find:** any defect in land area through the Mesozoic and Cenozoic
(+1.6 pp mean bias over eight ages), any frame error of our own (0–2° against PALEOMAP at
ten ages), any ice where the record has none (fourteen consecutive ice-free keyframes agreed
with an independent source), and any Palaeozoic ice outside the literature range.

---

**What the card audit did NOT find:** any HIGH-severity error. 667 cards, 214,000 characters, zero factual errors at HIGH. Two of the three date disagreements the first run reported were errors in **this folder's** catalogue, not the app's — `deeptime.py` was corrected to match the app, which separates the late Famennian pulse from the Late Palaeozoic Ice Age more cleanly than the common convention does.

---

## H. Terrain in motion — why landforms do not appear to emerge (round 9, 2026-07-29) — [WP-08](research%20reports/WP-08-terrain-in-motion.md)

The user's report: mountain ranges, seabeds and other places where crust piles up "seem
accurate, but do not visually appear to form in a natural geophysical fluid dynamic way."
Every item here is re-checkable with `modeling/audit_terrain_motion.py`, which reads the
**shipped** fields rather than the source DEMs, so it scores what a viewer sees.

**Finding 0 governs this whole section, so read it before touching anything.** The
PaleoDEMs already encode orogeny correctly: the Himalaya go 889 m (60 Ma) → 7,751 (40) →
5,272 today; the Appalachians peak at 2,805 m and 20.6% above 2 km at 300 Ma and wear to
620 m; the Caledonides 2,731 m at 340 Ma → 151 m. **This is not a data problem and there is
no orogeny model to build for 0–540 Ma.** The heights and their timing are right; what is
wrong is the transition between keyframes and the character of the surface.

So the constraint on every item below: **the PaleoDEM is authoritative for where a mountain
is and how high it is. H1, H2, H4, H5 and H6 must not change any keyframe's hypsometry —
that is a measurable gate, not an aspiration. H3 deliberately does change it, and is the
only item here that can trip `audit_all.py`.** A session that "improves" the Himalaya is
adding error to data that is currently correct.

| # | P | item | touches | evidence |
|---|---|---|---|---|
| H1 | **P1** | **Advect the fields between keyframes instead of cross-fading them.** `baseElev` is `mix(decElev(A), decElev(B), mixf)` — a dissolve between two stationary images. Crust moves a median of **14–42 texels** of the 4096 grid per 5 Myr step (p90 25–51, max **65**; worst at 400 Ma, where the median is 410 km). At that scale a dissolve is a double exposure: every mountain front, coastline and trench splits into two half-amplitude copies mid-interval and snaps at the keyframe. Warp each keyframe toward the other along a per-pixel displacement field and blend the warped pair. **The overlap this produces at a convergent margin IS the shortening signal H4 needs** — the same insight WP-07 recorded for the future branch, where 12.8 Mkm² of convergence is computed and deleted. Warp everything in crust coordinates (`_e`, `_d`, `_w`, `_o`); **do not warp `_r`**, which is a property of the atmosphere over a position. | `web/index.html` FRAG+VERT, new `_v` field | WP-08 F1 |
| H2 | **P1** | **Give the shader a material coordinate so texture rides with the crust.** `elevAt` evaluates every noise tap at `dirFromUv(uv)`, a pure function of position with no age term anywhere — so a continent slides out from under its own ridges and valleys, and only the amplitude travels with the plate. Identical to the sea-floor defect fixed in README §5.3 (fabric keyed to the present ridge, not the isochron); land never got the fix. Cheapest correct form is a nearest-filtered plate-ID texture plus a per-plate rotation uniform array — **not** an 8-bit lon/lat field, which quantises to ~156 km against noise that resolves 1.3 km. | `web/index.html` FRAG, new plate-ID field | WP-08 F2 |
| H3 | **P1** | **Regularise the source series in time.** *(P2 → P1, 2026-07-30: measured after H1 shipped. The elevation histogram, which rigid motion cannot change at all, moves 5.5–9.4% of the globe per 5 Myr step — so a large part of what H1 tries to align is not motion, and H3 is the other half of the same artefact.)* Two problems in one field. (a) *Authoring noise*: land above 1 km moves **+2.30 pp then −2.80 pp** across 15→20→25 Ma and **+2.52 then −2.75** across 95→100→105 — spike-and-revert on single frames, ~1.5 Mkm² per pp, and no eustatic curve can move land above a kilometre at all. This is G1's finding in relief instead of shelf area; use G1's remedy, scoring each frame against its own neighbourhood. (b) *The 5 Myr step*: the Himalaya gain **+5,890 m in one keyframe** (45→40 Ma) and then sit flat for 15 Myr. Try (a) alone first and re-measure — H1 and H4 may carry (b) on their own. **If easing is needed it must apply to the relief residual only, never to the base**: the comment at `web/index.html:5593` is explicit that easing `mixf` globally makes continents accelerate and stall at every keyframe. | `build_fields.py`, `epeiric.py` pattern | WP-08 F3 |
| H4 | **P1** | **Ship a tectonic-state field and draw an anisotropic fold fabric from it.** Nothing tectonic reaches the shader today: `motA` is bound and never sampled, `motion.classify()` and `encode_bounds()` are dead code, `build_plates_gplates.py:51` collapses Merdith's own `OrogenicBelt` into `"trench"`, and `plates_time.json` carries no velocity at any age ≥ 0. A new `_t` texture — **R shortening rate, G orogen age, B structural azimuth** — is derivable from the plate topologies plus H1's displacement field with no DEM, so it costs ~2 s a keyframe like `build_surface.py`, not a full rebuild. Then: fold ridges **parallel to the suture** (real belts are stripes; isotropic roughness reads as bumpy ground however tall it is), and character by orogen age — sharp crests and bare rock when young, rounded and soil-covered when old, so the Appalachians visibly wear down instead of merely getting shorter. **This is the item that makes it read as collision.** | new `_t` field, `web/index.html` FRAG, `build_plates_gplates.py` | WP-08 F4, F5 |
| H5 | P2 | **Seed the landforms of collision a 20 km grid cannot resolve** — same deliberate-exception discipline as `epeiric.py` and the present-day lakes, and only where the DEM provably cannot carry the feature. **Foreland basins** first: a range *plus its parallel trough* is the diagnostic signature of collision, the trough is 100–300 km wide and a few hundred metres deep, and it follows from a flexural response to H4's own load with one free parameter. Then **accretionary wedges** — the sea floor already builds trenches with an outer rise, and the wedge is the half that makes subduction read as scraping rather than as a groove. **Subsumes F4** (back-arc basins by roll-back), which belongs with this work rather than apart from it. | `seafloor.py`, new module | WP-08 F0 |
| H6 | P3 | **Fix the interpolation-domain mismatch and clear the dead code behind H4.** The vertex stage mixes the encoded byte and decodes after (`:1287`); `baseElev` decodes then mixes (`:1512`). `dec_elev` is quadratic, so displaced geometry and shaded elevation disagree mid-interval, worst at a migrating coastline. Three lines, and it muddies every before/after comparison until it is done. With it: either use `motion.classify()`/`encode_bounds()` or delete them — two independent surveys read them as working features — and give `OrogenicBelt` its own class. | `web/index.html`, `build/motion.py`, `build_plates_gplates.py` | WP-08 F6 |
| H7 | **P1** | **Carry real detail on low ground, and shade it at its own scale.** Land reads blurry at zoom, and it is not the elevation texture — the shipped `_e` is 4,096 × 2,048 (9.8 km) against a source PaleoDEM of 3,600 × 1,801 (11.1 km), so it is **already 1.14× finer than the data behind it and a bigger texture would add zero information.** Three real causes. (a) `clamp(z/900.0,0.15,1.0)` in `web/index.html:1583`, with `rug`≈0 on a plain, gives a 150 m coastal plain **±32 m** of procedural relief against a mountain's **±447 m** — a factor of 14, and a 0.13% gradient across a 24.5 km cell that no hillshade can show. (b) The hillshade central difference is `da=2.4/2048.0*PI` = ±23.5 km (`:1885`), while the two detail generators run down to 1.3 km: **only 3 of their 10 octaves are coarser than the gradient's half-step**, so seven are computed, added to the height and then aliased away by the shading meant to reveal them. (c) `_d`'s drainage channel already carries a per-keyframe valley network and is used **only for colour** (`:2318-2334`) — the app knows where the valleys on a plain are and declines to carve them. Lowlands need that structure, not more fbm. | `web/index.html` FRAG | WP-08 F7 |
| H8 | P2 | **Stop thresholding a 26 km field into polygons.** Shelf-ice and shallow-water margins and small lakes show hard quadrilateral edges at a fixed cell size — bilinear magnification of a coarse grid under a steep threshold traces the texel quads. Arithmetic, not impression: `_r` is 1,536 × 768 = **26.1 km/texel**, 2.7× coarser than elevation; `arid → Tela` swings **7 °C**; `ela` moves **172 m per °C**, so **1,207 m** across the range; and `snow` ramps over **400 m** — the aridity term alone can move the snowline **3.0× the width of the ramp that draws it**. Same class as the accumulation term removed 2026-07-22, on a path that removal did not touch and which has three times the leverage. **Smooth the input or widen the ramp; do not re-tune the ice line** — `ice_audit.py` passes 22/22 and that line is measured against the literature. | `web/index.html` FRAG, `build_fields` rain grid | WP-08 F8 |

## H — IMPLEMENTED, 2026-07-30

| item | what shipped | measured |
|---|---|---|
| **H1** | `plate_field.py` + `build_displacement.py` → 200 `_v` fields; `baseElev` and every crust-bound sample now warp through `wA()`/`wB()`. Rainfall deliberately not warped. | `_v` agrees with pyGPlates to **3–11 km**, at the 10.5 km quantisation floor. Keyframes untouched: **0 m** deviation at mixf 0 and 1. Mid-interval relief sag **27.8% → 25.4%**, better at 3 of 4 intervals; India–Asia's two taps agree **52%** better. Three constants were scanned rather than guessed and all three would have been wrong: the true maximum displacement is **10.27°**, not the 6.11 a nine-age sample suggested, so an 8.0 ceiling would have silently clipped the fastest crust in the model; plain Jacobi relaxation does **not** converge on ocean-sized holes (79 km off after 480 iterations) and had to become multigrid; and WebP q98 carries a **102 km** maximum displacement error concentrated exactly at plate boundaries, so the field ships lossless. |
| **H2** | `build_platefield.py` → 201 `_p` slot rasters + `platerot.json`; `matDir()` carries every crust-bound noise tap into the crust's own frame. NEAREST filtering, because a slot is a label and not a quantity. | The contract — the same rock resolving to the same coordinate at every age — holds to **2–6 km in 11 of 12 tests**, the twelfth being India at 100 Ma, a microplate on a boundary. The top 48 plates carry 88–99.8% of covered cells; the tail is assigned its nearest large neighbour rather than left unrotated. |
| **H4** | `build_tectonic.py` → 200 `_t` fields (shortening + fold axis as a double angle); `elevDetail` compresses its noise domain along the fold axis, so a belt draws as parallel ridges instead of isotropic lumps. | Three calibration findings, all from the screen rather than from theory: differentiating a piecewise-rigid field reports a **discretisation artefact of 9.6** where real convergence is a few tenths, so the field is smoothed to a real deformation width before it is differentiated; the Laplace fill's own gradients made **70–85% of the globe read as "active"**, so shortening is weighted by coverage confidence; and the fabric must be gated **high** — strain 0.045, not 0.002 — or it combs the interior of every plateau and reads as wood grain. |
| **H7** | Amplitude by **substrate**, not elevation; three extra normal-perturbation scales covering the band the hillshade cannot resolve; an explicit shoreline taper and a two-sided guard so detail can move no coastline in either direction. | A 150 m coastal plain went from **±32 m** of procedural relief to roughly four times that, against a mountain's ±447 — the factor-of-14 gap that was the blur. Verified on screen at 47.5 Ma and 0 Ma. **The elevation texture was NOT raised**: it is already 1.14× finer than the PaleoDEM behind it, so a bigger texture would have cost four times the memory for zero information. |
| **H8** | Sub-grid ELA variability at the scale the rainfall grid is missing. | `ice_audit.py` unchanged at **1 finding**, its baseline — the fix moves the *edge*, not the area, which is exactly what it had to do. |
| **H6** | Vertex stage decodes-then-mixes like `baseElev`, and advects with the same offsets. | Removed a geometry-versus-shading disagreement of **p99 434–729 m, max 2.67 km** mid-interval, worst at migrating coastlines. |

**H3 — MEASURED, AND DELIBERATELY NOT APPLIED.** It was promoted to P1 on the finding that the
elevation histogram moves 5.5–9.4% of the globe per 5 Myr step, which rigid motion cannot
cause. Scanning all 199 past keyframes for single-frame outliers then found **none beyond
6 sigma**: the worst are 100 Ma at +5.0 and 20 Ma at +4.5, and behind them a continuum.
Localising them shows the spike is **southern and regional at both ages** — Antarctica gaining
16 pp of land above 1 km in one frame and losing it again, which is almost certainly an ice
surface entering a bedrock DEM.

So there is no clean subset to repair. A general temporal regulariser would rewrite Scotese's
authored topography **everywhere**, on the strength of a smoothness prior and nothing else.
G1 could do this for shelf area because Blakey supplied an independent target; for relief
there is no external target, only the assumption that the past was smooth. That difference is
decisive: this section's governing constraint is that the PaleoDEM is authoritative, and
G7+G8's standing rule is *record it, do not tune to it*. **Recorded.** The specific Antarctic
frames are worth chasing to their source map, which is a data-provenance question rather than
a modelling one.

**H5 — SHIPPED, 2026-07-30, with a polarity model that works.** The two blockers recorded
when it was deferred were real and are both closed. *Hypsometry:* nothing at or above 1500 m
is touched, enforced at bake time and again in the shader, and `audit_foreland.py` measures
it — **0 cells altered at seven ages spanning 0–500 Ma**, with the >2 km and >3 km hypsometry
identical to three decimals. Land area falls 0.03–0.13 pp, which is the basins themselves and
is the feature. *Polarity:* solved, and the interesting part is that **one rule cannot do it**.
"The foreland sits on the underthrusting plate" gets the Himalaya right and the Andes exactly
wrong — Nazca subducts beneath South America yet the Chaco-Beni foreland lies east, on the
overriding plate, because the western side is ocean. What covers both is asking what is
actually there across strike: deep ocean is disqualified, the lower side wins, and the basin
must be genuinely lower than the range that loads it. Scored against five present-day
forelands: **3 correct, 2 weak, 0 on the wrong side.**

Three findings from building it, each a bug that produced a plausible-looking wrong answer:
a single across-strike probe of 320 km is still **on** Tibet, so the model scored the range as
its own foreland; `w0` read the elevation of the *nearest* load cell, which is by construction
the range's outermost foothill rather than the massif behind it, so every basin came out a
tenth of its depth; and the flexural profile peaks at the load's edge, exactly where the
mountain-protecting gate suppresses it, so distance is now measured from the range's footprint
instead of its high core. **And the load could not be gated on shortening**: PALEOMAP's static
polygons carry no distinct motion for oceanic plates, so `_t` sees India–Asia at 0.58 and is
blind to Nazca–South America, reading 0.02–0.10 across the whole Andean transect including the
trench. Gating on it built a Ganges and refused an Andean, Alpine and Zagros foreland. The
load is therefore the range itself, which the DEM gives directly, and across-strike comes from
the terrain's own regional slope rather than from the strain field's fold axis. **Recorded as a
known limit of the rotation model, not tuned around.** F4 (back-arc basins by roll-back)
remains open and is no longer folded into this item.

**A pre-existing artefact found while verifying, and NOT caused by this work.** A dark
dithered stipple hugs shallow-water margins at zoom — visible in the user's own screenshots
before any of this landed. Discriminated by rendering the same frame with `uDetail=0`: the
stipple is **identical**, so it is not procedural relief but something in the shipped
sea-floor data or the ocean colour path. Same family as WP-06's staircase, on the upper slope
rather than the abyssal plain. New item, unscheduled.


**Recorded, not scheduled.** At 20–40 Ma the Himalaya box reaches **8,000 m exactly** — the
`Z_RANGE` ceiling in `build/fieldpack.py:13`. Scotese's Tibet is being clipped at those ages.
Whether the source exceeds 8,000 m is unmeasured, and raising `Z_RANGE` changes the elevation
quantum everywhere and invalidates all 251 shipped `_e` textures, so this needs a measurement
before it needs a decision.

**Documentation errors found on the way, all cheap:** `README.md:90` says every field texture
is WebP (`_e` has been AVIF since the DC-blocking fix); `fieldpack.pack()`'s docstring
describes an RGB packing the build no longer uses; `handoff_blend`'s docstring
(`build_fields.py:875-877`) justifies itself on the claim that the shader interpolates in the
signed-sqrt domain, which is true of the vertex stage only — the blend is still right, but
for a different reason; and the "35-minute rebuild" repeated in four files predates the
elevation grid doubling to 2048×4096 and is stale by roughly 2.4×.

**Sequencing, and the reason is WP-07's calibration trap — two changes that compose are one
calibration.** H1 and H2 are independent of each other, are pure presentation, and change no
shipped field, so they go first and are also the cheapest to revert. H6 is three lines and
unblocks honest before/after comparison, so it rides with them. H8 is independent of all of
it and cheap, so it goes early while the rest is still stable. **H4 and H7 are one item for
calibration purposes** — the fold fabric and the isotropic detail amplitude both write into
`elevDetail` over the same 1–25 km band, so tuning either against a version of the other that
is about to change guarantees re-tuning. H5's constants must be tuned after that pair. H3
changes the shipped fields and so invalidates anything tuned against them.

**H1 → H2 → H6 → H8 → (H4 + H7 together) → H3 → H5.**

**H7 comes after H1 and H2 for a reason that is not cost.** More high-frequency land detail
makes both of those defects *worse*: more content to double-expose across a 14–42 texel
cross-dissolve, and a far more visible slide when crust moves out from under a texture pinned
to the globe. Shipping H7 first would make the app look better in a still and worse in
motion — which is the opposite of what was asked for.

**Validation assets already in the folder.** Five Britannica paleogeographic maps carry an
explicit **Mountains** legend class at 306, 255, 237 and 152 Ma — all named
`Distribution-landmasses-regions-seas-ocean-basins-*.webp`, the five suffixes being
`Permian`, `locations`, `locations-1`, `locations-2` and `locations-3` — and they are the
only source here that maps mountains as a class. The 16 labelled Scotese PALEOMAP maps name
mountain belts. `FRAME-REGRESSION-gate.md` already scores **39 named orogen features** and is
a ready-made harness. There is no authored orogeny/collision figure in
`diagrams and illustrations/authored/` — an obvious slot once H4 lands.

**What this section does NOT claim.** That the app's mountains are in the wrong place, at the
wrong height, or at the wrong time — Finding 0 measured the opposite at four orogens. That an
uplift model is needed for 0–540 Ma. That the future branch needs more work than G5/WP-07
already gave it. And it takes no position on the Palaeozoic land/shelf disagreement recorded
in G7+G8, which stands as *record it, do not tune to it*.

---

**Count: 67 items — 18 at P1.**

*The seven that would move the app furthest, as ranked at round 8:* **A1** (adopt the
PALEOMAP rotations — measured, ready), **G1** (flood the Triassic–Jurassic epeiric seas —
93% of an independent reconstruction's shelf sea is dry land in ours), **G2** (stop the
future series destroying 37% of continental area), **D1+D2** (hotspot catalogue → seamount
chains), **F2** (the climate-events panel — 11 cards already drafted, no geometry needed),
**B1** (province model behind the biota panel), **C1** (PhanDA diff). **All seven have since
landed** — see the APPLIED tables at the top of this file. The ranking is left in place
because it is the record of what was judged most valuable, not a live queue.

*The live ranking, as of round 9:* **H1** and **H2** (the crust does not move like crust, and
its texture does not move with it — the two largest remaining visual defects, and neither
touches a shipped field), **H4+H7** (nothing tectonic reaches the shader at all, and land
carries no detail below 900 m — one calibration, not two), **H8** (a 26 km field thresholded
into polygons), **D9** (the crustal-age Voronoi, whose deeper fix is still outstanding),
**H5+F4** (the landforms of collision and back-arc basins, one item), **D10** (draw the
Messinian Mediterranean), **H3** (the source series' own authoring noise in relief).

## P. Performance — why it lags, and what recovers it without touching the picture (audit round, 2026-07-30) — [WP-09](research%20reports/WP-09-performance-audit.md)

The user's report: "often lags, or is slow to render when jumping across the timeline, and
the frame rate seems a bit jagged." Measured on the M1 itself (method + caveats in WP-09):
the steady frame is fragment-bound and **~80% of it is sin-hash procedural noise** (72 ms →
14.4 ms with `vnoise3` constant, 2560×1440); a keyframe crossing stalls the main thread
**~153 ms** (18 synchronous image decodes + GPU uploads) and scrubbing back replays it
(~101 ms) because `TEX_CAP=24` holds barely one bound pair now that a pair is 15–18
textures; a far jump is 164–263 ms locally plus 296–580 ms/file network when unprefetched.
Steady-state JS is ~1 ms/frame — labels, cards and readout are NOT the problem.

**The governing constraint mirrors section H's: the PICTURE is authoritative.** Every item
below must be output-identical (same pixels) or output-invisible (A/B-verified same look).
Resolution drops, octave cuts, layer simplification and shorter shaders that draw less are
all out of scope by definition. What changes is WHEN work happens (decode/upload off the
render path), WHETHER it recomputes (noise values from a baked lattice instead of 8 sins
per octave per tap), and HOW MUCH survives in caches (a texture budget sized for the field
set that exists).

| # | P | item | touches | evidence |
|---|---|---|---|---|
| P1 | **P1** | **Decode images off the render path.** `loadField` stores a raw `HTMLImageElement`; the first `render()` that binds it pays AVIF/WebP decode + upload inside one frame — the two 4096×2048 `_e` AVIFs alone are ~112 ms. Fetch → `createImageBitmap` (worker-pool decode) and store the bitmap; three.js uploads ImageBitmap directly, and `drawImage` readers (`elevField`, `MOTDATA`, `WOLD`) accept it unchanged. | `web/index.html` loadField | WP-09 F4 |
| P2 | **P1** | **Size the texture cache for 10 field kinds, by bytes not count.** 24 slots ÷ 15–18/pair = every crossing evicts the frame it just left; scrub-back re-uploads 18 textures. Budget ~450 MB (≈4 keyframes) with per-texture byte estimates, LRU by bytes. This is the raise the terrain-motion memory already called for. | `web/index.html` TEXCACHE | WP-09 F5 |
| P3 | **P1** | **Idle-time predictive upload.** Current pair + the next keyframe in the playback direction (both neighbours when paused) get `renderer.initTexture()` during idle, budgeted ≤2 uploads/frame so the storm never lands in one frame. A crossing then binds textures that are already resident: the ~153 ms hitch becomes ~0. | `web/index.html` loop/prefetch | WP-09 F4–F6 |
| P4 | **P1** | **Noise from a baked lattice, not 8 sins per octave.** `vnoise3` (68 call sites; `fbm3`=5 oct, `detail3`=10, hillshade ×5 evaluations) and the clouds' `cn/cfb` become 2 bilinear fetches + 1 mix from a small tiled lattice atlas carrying the EXACT `hash3` values (period ≥64/axis; octave growth 2.07 makes repeats incommensurate; R8 first, 16-bit if A/B shows banding). Output-invisible by construction, verified by pixel-diff at fixed ages/views. The one measured 80% share is an upper bound — `?nonoise` also collapsed branches a LUT keeps — so the committed claim is 2.5–3× frame time, measured at each step. **P4b if needed:** bake whole static-domain sums (`fbm3(sdir*K+C)` families) into equirect textures — exact, since they are pure functions of direction. | FRAG `vnoise3`, CFRAG `cn`; small bake script | WP-09 F1–F2 |
| P5 | P2 | **`preserveDrawingBuffer:false`** (pixel-identical; `APP.shoot` renders once before reading) and an **MSAA verdict by screenshot** — silhouette + overlay lines decide, not the timer; keep MSAA if lines degrade. Together worth ~15 ms/frame. | `web/index.html` initGL, shoot | WP-09 F3 |
| P6 | P2 | **Jumps bind progressively, elevation first.** Request/bind `_e`+`_r` of the target pair before the other eight kinds — the per-kind uniform gates already make partial binds safe, so the first CORRECT frame arrives at ~1 fetch RTT on the live site instead of after the full set. | `web/index.html` ensureFrames order | WP-09 F4, network table |
| P7 | P3 | **Overlay rebuilds off the crossing frame.** `buildHotspots`/`buildVectors`/`buildDerivedBounds` (+`buildBoundaries` in jumpTo) are pure per-keyframe: memoize last N and/or spread across 2–3 frames. The ~50 ms non-texture tail of a jump. | `web/index.html` loop, jumpTo | WP-09 F7 |
| P8 | P3 | **Micro-hygiene:** `frameAt` allocates a fresh 251-element `ages()` array per call (several/frame); `uiRects` forces reflow every frame via getComputedStyle+getBoundingClientRect ×6 against layout dirtied by label writes — cache on resize/panel change; hoist the loop's per-frame `Vector3`s. Small, free, and they sharpen every future measurement. | `web/index.html` | WP-09 |
| P9 | P2 | **Keep it fixed: a perf harness in the app and a storm gate in the publish path.** `?perf=1` HUD (frame-time EMA, upload-queue depth, cache occupancy); a headless check that steps 10 crossings and FAILS if any synchronous decode >8 ms lands on the render path — the next field kind added must not silently reintroduce F4/F5. Prints its numbers on pass, per the validator rule. | `web/index.html`, `build/` check | WP-09 |

**Sequence: P1 → P2 → P3 ship together** (pure win, zero visual risk — this alone ends
"jagged" and makes scrubbing instant on cached ground), **then P4** behind the pixel-diff
A/B, **then P5/P6**, then P7–P9. After P1–P3 the remaining lag is the honest GPU frame;
after P4 the target is a steady 25–35 ms at 2560×1440 (from 72–110), fullscreen
proportional. Not promised: locked-60 fullscreen on M1 without P4b.

## P — IMPLEMENTED, 2026-07-30 (same day)

| item | what shipped | measured |
|---|---|---|
| **P1** | `loadField` fetches and decodes via `createImageBitmap` (worker-pool decode, `colorSpaceConversion:'none'`); bitmaps baked pre-flipped because `UNPACK_FLIP_Y_WEBGL` is ignored for ImageBitmap by spec, `getTex` sets `flipY=false`, and the two CPU readers un-flip through `drawFieldImage`. Image fallback kept for browsers without the API. | Orientation verified both sides (CPU probes: Himalaya +4,775 m, Gulf of Guinea −4,678 m; screenshots pixel-consistent with baseline). Decode left the render path entirely. |
| **P2** | Byte-budgeted LRU (450 MB, 200 MB when `deviceMemory < 8`), evicting by bytes until under budget. | Scrub-back across a just-crossed boundary: **101 ms → 7–9 ms**; ~4 keyframes stay resident (~268 MB steady). |
| **P3** | `queueUploads`: pair + direction-aware neighbours warmed one `renderer.initTexture` per frame; drains only off crossing frames; on the crossing frame it pre-decodes the neighbour's 256×128 label-probe raster instead. | Crossing with warm neighbour: **152.7 ms → 1–9 ms** (0 synchronous uploads — see P9 gate). Cold first-visit crossings ~20–28 ms (label snap work, not uploads). |
| **P6** | Two-wave `loadFrame` (e+r first at `fetch` priority high) + budgeted `bindTex`: cold jumps bind elevation+rainfall immediately, defer the other kinds to the queue front, one per frame — the same partial-bind contract the network path always used. | Far jump, files local: **164–263 ms → 44–99 ms** first frame, fully refined over ~10 background frames. Live-site jumps now show correct coastlines after e+r instead of after all ten kinds. |
| **P7** | `clearGroup()` disposes unique geometries/materials before `Group.clear()` in all four overlay builders. Builders measured cheap (0.2–2.1 ms) — no memoization needed. | Leak: **+93 geometries per crossing → +0** (95 → 127 steady over 25 crossings, was 2,425). |
| **P5** | `preserveDrawingBuffer:false` (all readers render-then-read in-task; `APP.snap` verified). **MSAA kept** — the constraint forbids degrading overlay lines and the silhouette. | Gain expressed under real compositing (removes a full-frame copy); not measurable in the forced-sync harness. |
| **P4** | `vnoise3`/`cn` read a seeded 64³ lattice from a 528×528 atlas (one-texel wrap gutters; sampling at corner + smoothstepped fraction makes hardware bilinear reproduce the exact mix() tree). **R16F, not R8** — 8-bit lattice values measurably softened ridged crests (−11% Laplacian in the ridge crop); half floats restore parity (16/25 regions LUT-crisper, 9/25 hash-crisper = instance variance). `?oldnoise` restores sin-hash for A/B. | Real-GPU (headless Metal, 2560×1440): sin-hash 249.2 ms → LUT16 **233.7 ms (−6%)**. R8 was −13% but rejected on the crispness measurement. Noise-free floor on the same scene: **28.7 ms** — the remaining prize, and why P4b matters. |
| **P8** | `ages()` cached; `uiRects` cached 200 ms + resize (kills a per-frame forced reflow against label-dirtied layout); camera scratch vectors hoisted. | Steady main-thread JS: **0.6–1.5 ms/frame**. |
| **P9** | `?perf=1` HUD (frame-interval EMA + worst, upload-queue depth, cache occupancy). `build/audit_perf.py` + `_verify.html?storm=` drive the real app headless and count uploads landing inside crossing frames; wired into `build_site.py` after `audit_all` (`SKIP_PERF=1` escape; skips LOUDLY without Chrome). | Gate at ship: **0 synchronous uploads on all three crossings** (4–17 ms steps). Prints its numbers on pass, per the validator rule. |

**What was tried, measured, and deliberately NOT shipped** — both are the next round's levers,
both need eyes on screenshots because they change (or risk changing) the picture:
- **Gradient-on-base** (hillshade's 4 full `elevAt` taps → `baseElev` taps): ~24% of the noise
  bill, but the pinned-time A/B shows 28–35% of land pixels shift (max 153/255) — the detail
  jitter in the wide gradient is load-bearing texture, not noise. Archived pairs:
  `build/verify/ab_A_*` vs `ab_B_*`. Superseded judgement belongs with H7's owner: the shipped
  normal-perturbation scales may make a *calibrated* version of this visually neutral.
- **P4b direction-domain bakes**: cloud `cfb` sums and other pure-functions-of-direction sites
  bake exactly into equirect textures (drift is a uv shift). Clouds alone ≈ 10 ms. Needs an
  offline bake (a JS boot bake of 8.4M texels × 20 octaves is seconds of main thread).
- Also parked: a `mediump` pass on the colour-side math (Apple runs fp16 at double rate), and
  the interaction-time resolution floor the user explicitly tabled.

**The honest headline**: the *hitches* — the reported symptom — are gone at the root
(crossings ~150 ms → ~0–9 ms warm; scrub-back ~free; jumps progressive). The *steady* GPU
frame improved only ~6–13% because Apple Silicon hides ALU cost too well for a value-noise
LUT to pay the way it would on bandwidth-rich desktop GPUs; the measured 28.7 ms floor says
where the next 7× lives, and the two named levers above are how to get part of it without
breaking the no-visual-compromise rule.

## P — CRASH POST-MORTEM AND SECOND ROUND, 2026-07-30 (evening)

**The first P1 shipped a crash.** Moving decode off the render path via `createImageBitmap`
was right; RETAINING every decoded bitmap in the per-kind arrays was wrong — a decoded
bitmap pins its full uncompressed raster (an IOSurface on macOS, invisible to RSS, which is
why the first soak read "flat" and shipped anyway). The prefetch pump then decoded the whole
timeline: measured **3,150 MB pinned within seconds of boot**, ~19 GB at completion. The tab
died in minutes ("Aw, Snap!", error 5), fastest while dragging — and the thrash on the way
down was itself the residual "still laggy". The user found it; the soak below is how it
gets found before a deploy next time.

**The fix is unified residency** (`web/index.html`, TEXCACHE): one cache entry per
kind+keyframe owns BOTH the decoded bitmap and the GPU texture, accounted together at
8 bytes/px and evicted together (never dispose one and keep the other — a context restore
would re-upload from a closed bitmap). The prefetch pump now only warms the browser's HTTP
cache — compressed bytes, browser-managed, ~127 MB for everything — and `ensureBitmap()`
re-decodes on demand (~1 ms disk-cache hit + off-thread decode) as the window moves.
Budget 700 MB (360 MB floor on small devices — a bound pair accounts ~300 MB, and a budget
below the pair is permanent thrash). `queueUploads` gained a decode stage ahead of its
upload stage; `bindTex` kicks the decode for essential kinds on jumps.

**Verified by a 5-minute soak** (`_verify.html?soak=` — playback + rotate + a far jump
every 20 s + view flips, under the app's own rAF): **zero errors, pinned memory flat at
325–344 MB, entries 34–53 churning under budget, JS heap 58–79 MB, GPU process ~200 MB
flat.** Before the fix the same soak pinned 3.1 GB inside the first minute. Crossings and
orientation re-verified unchanged; storm gate still 0 synchronous uploads.

**Ocean-only gradient (user-sanctioned).** The user judged the archived gradient A/B: a
downgrade on land, *not* on ocean crust. Shipped exactly that split: submarine fragments
take the base-field gradient (the detail jitter there was fighting the abyssal fabric
anyway), land keeps the full `elevAt` taps bit-identically. Sheds four ten-octave walks
from the majority of pixels in most framings; verified land-identical (Tibet interior
0.07% > 2 LSB, residual scattered diffs are the half-float subnormal clamp fix, not the
gradient) and ocean-clean by screenshot.

**Standing lesson for the register:** decoded-image residency is a BUDGET, never an
archive; and on macOS, decoded-image memory must be measured in-page (`window.__MEM()`),
not by RSS.

## P — THIRD ROUND: coherence and the pixel wall, 2026-07-31

**The lost smoothness-of-time was a real regression with a number on it.** Progressive
binding trickled the interval's displacement (`_v`) and material (`_p`) textures in behind
elevation, and at low frame rates the trickle never caught up: measured during 45 s of
default-speed playback, **uWarp was live on 67% of frames and uMat on 54%** — a third to a
half of playback ran in the pre-H1 cross-fade with texture sliding, which is exactly
"jagged and jumpy... worse at higher speeds". Three fixes took it to **100/100/100%**:
`v`/`p` are ESSENTIAL binds like elevation (a late lake field is invisible; a late motion
model is the whole look of time passing); the decode-ahead runs in a VISUAL-IMPORTANCE
order (`e,r,v,p,w,d,o,m,t,f` — array order had m/w/d/o starving v/p); and the residency
budget rose to 950 MB because a pair plus a three-keyframe lookahead needs ~870 MB and a
window smaller than the want-list is permanent eviction churn. Soaks stay flat and
error-free at the new budget.

**Also found: playback pace is fps-dependent.** `dt` clamps at 50 ms, so at 3 fps the
"18 Myr/s" slider actually advances ~2.7 Myr/s, erratically. Not separately fixed — pace
correctness returns as frame rate does.

**The pixel wall, stated plainly.** The user's M1 shows 335 ms/frame (3 fps) at native
resolution; the measured zero-noise floor (28.7 ms at 3.7 MP) scales to ~110 ms at a 5K
display's 14.7 MP — **even a shader with every octave deleted cannot exceed ~9 fps there.**
No output-identical optimisation reaches "smooth" on that hardware at native scale; the
honest levers are resolution or architecture (the split-bake in the previous round's
notes). Hence the **quality control** (`#qualBtn`, cycles Auto/Full/Balanced/Perf,
persisted): Full pins native; Auto keeps Full unless the measured real frame interval
(pre-clamp EMA) sustains >95 ms, then steps the RENDER scale 2.0→1.5→1.0 with hysteresis
and steps back up when there is headroom. Only the terrain canvas scales — labels, panels,
lines are DOM/overlay and stay native-sharp. Time-based warm-up (8 s), because a
frame-based warm-up at 3 fps was a minute of slideshow before help arrived. Verified
headless under forced dpr=2: steps at ~20-25 s under load, holds without flapping, zero
errors. The user tabled resolution changes earlier; Auto's default-on is justified by their
follow-up ask to "run smoothly on both M1 and M5" — and Full remains one click away.

## P — FOURTH ROUND: the scrub blank, 2026-07-31

The user's report: at reduced render scale, dragging the slider fast across large spans
blanked the globe for a second or two before the target rendered. Two mechanisms, both
measured with the new `_verify.html?scrub=` repro (0→900 Ma in 1.2 s, then time-to-render):
**(1) the evictor could dispose textures still bound to the material** — a scrub floods the
cache with new decodes, budget pressure evicts the least-recently-touched entries, and the
pair still ON SCREEN is exactly what the scrub stopped touching; three.js then re-uploads
from a closed bitmap and the globe renders black. Bound-within-3-frames entries are now
pinned against eviction. **(2) decodes cannot be cancelled, and every age the slider swept
past queued ahead of the age the user stopped on** — measured 1.37 s from release to
render, most of it stale decodes draining through the worker pool. While scrubbing (age
moving >1 keyframe for 2+ consecutive frames — a single big frame is a jump and decodes
immediately), no speculative decode starts at all; completions that arrive for ages >4
keyframes away close themselves instead of inserting. Release-to-render fell to 839 ms in
the synthetic harness, which is the floor (the target's own decode plus one frame at the
harness's 8.4 MP); during the drag the last world stays on screen and recently-visited
spans still bind live. Coherence stayed 100/100 and the soaks stayed flat and error-free.

## P — FIFTH ROUND: the crust must move under the drag, 2026-07-31

The scrub-decode gate (fourth round) fixed the blank and the release latency but froze the
CRUST mid-drag: the climate uniforms interpolate straight from the timeline table and kept
sweeping — seasons, ice lines, sea tint all travelling — while the elevation pair stayed
whatever the drag departed from. Colours moved through time over a fossilised world, until
release snapped it. The user called it correctly: showing change over time in real time is
the slider's job.

**Scrub stepping.** While the slider moves, `bindTextures` shows the NEAREST RESIDENT
elevation keyframe to the slider's position — one coherent world per step (every per-frame
field resident for that keyframe binds with it; `mixf`=0, `uWarp` stands down: a stepped
world is a still, not an interval) — and elevation-ONLY decodes keep landing behind the
drag: capped at 3 in flight, aimed AHEAD along the drag's direction of travel (a decode
outlives a frame, so one kicked at the slider lands behind it), and a completion is kept if
it is closer to the slider than what is currently shown rather than by the fixed radius.
Climate uniforms still track continuously, so the sweep keeps its seasons while the crust
marches. On release the exact pair binds and the interval machinery resumes.

Measured with `_verify.html?scrub=` (0→900 Ma over 3.2 s): **crust states shown during the
sweep 1 → 12** at realistic load (5 under the harness's CPU-starved worst case — the rate
is decode-throughput-scaled by design), release-to-render 397 ms, no blanks, coherence
still 100/100, storm gate 0. Re-scrubbing a recently visited span steps entirely from
residency — per-keyframe live — which is the actual study-a-transition workflow.

## Q. Fidelity round toward the Google Earth bar (2026-07-31) — first iteration

The user set the bar explicitly: nine Google Earth references, "match the fidelity...
without compromising existing dynamics", loop with visual confirmation. First iteration
shipped; the loop continues with the user's eyes on the live build.

| what | mechanism found | what shipped |
|---|---|---|
| Flat land ≥63° (defect 1/2) | The anti-starburst polar branch computed its hillshade gradient from the ring-averaged BASE field only — the detail term never reached the gradient poleward of ~63°, and the gradient is what makes detail visible (H7) | The detail term's own central difference, taken in the world-fixed tangent frame with base height held constant (base cancels; pole-safe because the detail is isotropic 3D noise). Land only, mirroring the submarine base-only decision |
| Amorphous ice blobs (defects 2/3) | One 7°-scale lobe noise on a SIX-degree-C linear ramp, painted flat white | Three edge scales (great lobes / ~34 fingering / ~110 fjord fray), outlet tongues following the real drainage field (symmetric about its midpoint — the first version biased positive exactly over lake basins, icing Manitoba and suppressing lakes), a crisp margin (smoothstep over ~0.9 C, same iso-line), ablation-zone grey-blue with melt speckle, sastrugi grain inside, bed relief ghosting through thin margins, and confidence-graded OPACITY so near-threshold fringes read as patchy cover rather than sheet (the crisp mask alone had promoted Quebec's marginal fringe into a solid sheet at the present day). ice_audit at its 1-finding baseline throughout |
| Soft white snowfield wash (arctic wide views) | Smooth snowline contour | Same multi-scale zero-mean edge fraying as the sheet margin |
| Plains read as wash (prairie/Sahel/New Guinea refs) | The drainage network was colour-only — "the app knows where the valleys are and declines to carve them" (H7) | The drainage field's own gradient (two extra taps of the MEANDERED sample) dips the shading normal toward channels: valleys incise, banks catch light. Elevation untouched — coastlines exact |
| Deep-time/desert land = blank card (defect 1, Australia ref) | ALL land mottles were vegetation-gated, and the barren-era overlay was one flat two-tone ramp painted over everything | Barren and desert palettes now ride the lithology noise (sandstone vs iron-red families, duricrust variation), with the within-biome mottle UNGATED and outcrop grain |
| Shield missing its thousand lakes (prairie/shield refs) | bake_present_lakes MIN_PX=55 kept ~137 lakes; Winnipeg-class and below were dropped | MIN_PX=6 (~10 km and up): 1,117 real lakes (647 Holocene-windowed, 470 long-lived), FIELD_V bumped 20260731-lakes |
| Fine grain slightly timid | — | Amplitude 0.30+0.45·rug → 0.36+0.50·rug |

**Verification-harness lesson that cost an hour:** the driver's app IFRAME was heuristically
cached — headless shots silently rendered a STALE build (old lakes file, old shader) while
the pane showed the new one; the two disagreeing at the same URL was the tell. The driver
now cache-busts the iframe every run. Trust two disagreeing instruments to be telling you
about a third thing.

**Still open in this loop** (next iteration, guided by the user's eyes on this one):
ocean-floor crispness vs the Hawaii/Scotia references (fracture-zone contrast, trench walls,
shelf-break sharpening, margin-stipple softening); the rectangular fabric seam (not
reproduced this session — likely a scrub-transient; watch); Hudson Bay renders annual-mean
pack ice at the present day (pre-existing climate-model statement — user ruling wanted);
richer close-zoom land grain; cloud interplay at mid-zoom.

## Q — ITERATION 2, 2026-07-31: the mesoscale

The user's 122 Ma screenshot showed the remaining gap precisely: continental INTERIORS
still read as airbrush at globe zoom, and the drainage carve was invisible there — it lives
at texel scale, and a river is one texel wide however large it is. What reads from orbit is
structure at 50–500 km, which nothing in the shader owned. Shipped: **trunk drainage**
(a wider-ring average of the drainage field drives a broad corridor tint — green ribbon
where wet, dark wadi tracery where arid — plus a wider valley dip, the thing that makes an
Ob read from orbit); **mesoscale geology tone** (two crust-locked octaves at ~6.5/16 shaped
by the substrate-hardness field, applied to ALL land — the older mottles were vegetation-
gated, which is why barren interiors had nothing); **arid carve gate** lowered so fossil
drainage shows in deserts. Verified at the user's exact framing: interior provinces,
moisture gradients and belt texture where there was blank card. Scope trap for the record:
`h` (humidity) lives inside the biome block — passes outside it need the main-scope
`moistw` proxy off `Rf`; and a black globe with a passing source-checker means a COMPILE
error — `renderer.info.programs[].diagnostics` in the pane gives the exact line in seconds,
faster than any headless dump. Also: singleton Chrome profile locks from a backgrounded
run silently kill every subsequent headless shot — 0/N with a healthy app means check the
harness first. Ice kept per user ruling (annual-mean, not summer imagery). Next
iterations: trunk-corridor threshold tuning per-age, the ocean-floor pass vs Hawaii/Scotia
references, close-zoom land grain, the unreproduced fabric seam.

## Q — ITERATION 3, 2026-07-31: unmistakable at whole-globe zoom

The user re-sent both framings: iteration 2's mesoscale was directionally right and an
order of magnitude too timid. Shipped: **macro relief** — a second central difference at
~137 km folded into the same shading normal (land, non-polar, faded across the polar
handoff), which is the band whole-globe zoom actually reads and the 23.5 km gradient is too
short to feel; **mesoscale amplitude roughly doubled** (0.085→0.15 base); **hue provinces**
— a low-frequency crust-locked field swings barren land between an iron-warm and a
cool-pale cast (vegetation-gated so forests stay forests): a grey modulation of one tan can
never read as geology, colour family can. Verified at the user's two exact framings and
Australia/Sahara: interiors now carry basin-and-swell shading, province colour, belt
texture. ice_audit at baseline; gates green. The /loop continues: ocean-floor pass next.

## Q — ITERATION 4, 2026-07-31: the ocean floor

Against the Hawaii/Scotia references: **submarine macro relief** (the ~137 km second
difference joins the underwater gradient at 0.22 weight — a continental slope, trench wall
or ridge flank is a 100-300 km form and is what a bathymetric framing is made of);
**young-crust brightness** 0.06→0.11 (ridge flanks read light in real bathymetry);
**abyssal fabric contrast** amp 1.55→1.90, tone 0.30→0.38; **slope-crease quench** (the
ridged detail creases on the steepest submarine slopes were the dark margin stipple —
rugw now fades above rug 0.38, real slopes are smooth-swelled). Verified: Hawaiian chain
with halos and trailing seamount ridge, Scotia arc loop with trench shading, South China
Sea shelf/basin, Atlantic margin; 122 Ma land framings unchanged. Residual: a granular
dark field on the Argentine shelf edge persists (not the ridged creases — needs a zoomed
diagnosis next round); Hawaii wants denser small-seamount pepper and sharper fracture
lineations. Gates green, ice at baseline.

## Q — ITERATION 5, 2026-07-31: the margin lace resists, and what is now known

Shipped (verified harmless-to-positive at Argentine/Hawaii/mid-Atlantic/land framings):
slope-quiet fine submarine swell (n2 fades by local rug — plains keep basin swell);
calibrated fabric contrast restored (1.55/0.30, iter-4's raises read as blotch); pixel-
footprint far-fade on the fabric's normal and tone (fwidth of sdir — seam-safe — gentle,
far-only); steep-slope residual floor 0.10; IRLS-robust wide-gradient taps.

**The margin "lace" is still standing, and the elimination matrix is the deliverable:**
it survives uDbg.x/y/z off, sdet=0, a FLAT palette at branch end (so it is applied in the
shared tail), residual keep floored, and robust wide taps. The one false lead to not
re-walk: colouring `col` at branch end to visualise |wide| proves nothing — the shared
hillshade multiplies it, so the lace appears in ANY such viz. Next probes, in order:
(1) early-return `gl_FragColor` visualisations (bypass the tail) of |wide|, |res|, and the
final shade term; (2) the sea-surface sheen's static component; (3) the shade formula's
inputs beyond nrm. The crackle sits at z −850…−3000 on old-crust margins, is static in
time, lighting-borne, and band-limited to the slope — whatever draws it satisfies all four.

## Q — ITERATION 6, 2026-07-31: the lace, narrowed to a facet

Proven this round, each by direct probe: the wide gradient is CLEAN (early-return viz);
the qw gate WAS a per-pixel coin flip over the field's own texel noise (the gate viz shows
the lace's own pattern in qw) and now thresholds a five-tap smoothed depth instead — a
principled H8-class fix that ships regardless; the harness is FRESH (an additive canary
tint rendered); and the decisive new fact: **the lace's dark cells survive an ADDITIVE
canary, so the lace is a near-zero MULTIPLIER in the shared tail — a lighting facet at
near-grazing normal, which requires |gradient| at the vertical-exaggeration scale.** The
smooth gate alone did not remove it, so the raw magnitude enters somewhere the gate does
not govern. Next wake, in order: early-return viz of vex, of the post-everything
|gE,gN|, and of the shade term itself; then the fix at whichever stage the magnitude
appears. Every eliminated hypothesis above is real elimination — do not re-walk them.

## Q — ITERATION 7, 2026-07-31: three H8 fixes ship; the lace closes its dossier

Shipped (each verified no-harm at the reference framings): the dequantisation gate, the
bottom-return exponential + shelf-lift + biology shelf band, and the pack-ice grounding
depth ALL now threshold a five-tap smoothed depth instead of raw z — three separate
raw-threshold-over-texel-noise instances of the H8 class in one block radius. Submarine
exaggeration continued down its own author's road (760–920 from 520–780).

**The lace dossier, final form.** The elevation DATA over the band is clean (Laplacian
46 m mean; the slope spans 2–4 texels). The rendered lace is wide on screen — sub-texel in
field terms — static, survives: fabric/faults/FZ/shrinkage switches, sdet=0, palette
z-smoothing ×3, gate smoothing, vex 520→760 (proving it does not pass through the shared
normal), gUV scaling, additive canary (purple-through → in-branch, pre-tail). Sea branch
confirmed by branch canary. Remaining move: brute-force bisection of the sea branch by
halves with variant switches — reasoning is exhausted, enumeration is not. Three
iterations was the budget; the loop moves on and returns armed.

## Q — ITERATION 8, 2026-07-31: the lace's dossier, second closing

Six more eliminations, each by kill-switch screenshot at the same framing: the river
plume/delta/mouth colour terms; the pack-ice colour mix; the floatIce normal-flattening;
the ENTIRE abyssal-fabric block combined with a flat sea palette (the decisive combo — the
plain went perfectly clean, the lace stood alone); a soft-cap on the final submarine
gradient magnitude (reverted after missing — unverified risk to real trench walls); and
the sea-surface sheen, which turns out to no longer exist (uTime has no consumer).
Confirmed carriers of the blobs: the fabric block (now twice proven). The lace's surviving
suspects after two full rounds: something inside the shade path that is not nrm-magnitude
(the shade floor is 0.70 so the cells are consistent with hs=0 at the floor), or a
sampling-warp effect on the base taps themselves. The staircase-of-a-two-texel-slope
theory remains the best mechanism but the soft-cap test argues the saturation is not in
|g|. Next visit: bisect INSIDE the narrow-tap sampling chain (wA/wB, uvFromDir, matDir)
with early returns; three iterations spent, artifact bounded, queue resumes first.

## Q — ITERATION 9, 2026-07-31: corridors and close grain

Trunk corridors: four-tap ring (was two), threshold 0.26–0.75 (was 0.30–0.85), corridor mix
to 0.72 capped 0.62 — the big-valley ribbons now read at the user's 122 Ma framing. Close
grain: the finest band strengthened (0.34→0.48) plus a ~2.4 km octave that exists only
near the ground, faded in by the same pixel-footprint measure the ocean fades out by — a
close pass over a barren craton reads rock, not wash, and whole-globe views never pay for
it. Verified at Laurentia-450 close, prairie, 122 Ma, Sahel. Gates green, ice at baseline.
Queue state after nine iterations: interiors ✓, ocean architecture ✓ (lace open, dossier
complete), corridors ✓, close grain ✓, seam unreproduced. The remaining distance to the
reference is the lace, hue-balance subjectivities, and the data's own 10 km floor — the
user's eyes are the next instrument.

## Q — ITERATION 10, 2026-07-31: the lace bisected; one artefact becomes two

The dossier's "bisect with early returns" plan ran to ground truth. Staged vizzes
(narrow |g|, |g|+macro, post-shrinkage |g|, and hs itself, driven through a new
`_verify.html?app=` variant hook) showed: the narrow gradient is a SOLID saturated
cliff on every margin band — the field drops 3-5 km across 2-4 texels — and what
survived the shrinkage was the staircase's per-pixel spikes: the old 0.10 guard
floor kept 5.5% of the residual, and 5.5% of 3000-5000 m is a randomly-aimed facet
that flips hs to its 0.70 floor. THE DEEP-BAND LACE WAS EXACTLY THAT, and four
shipped changes kill it, each measured: guard floors at ZERO on the steep band
(the 0.10 dribble only ever served fracture zones, which live on open floor where
the guard never engages); the surviving residual is capped as an ANGLE — 240 m at
the deep vex is a 15-degree facet, mathematically unable to flip against the
39-degree sun, and the band came clean; the cap grades to 420 m at true shallow
depth; the shrinkage gate opens on the pixel's OWN depth (qw>0.01 || z<wl-60) so
a land-contaminated gZSm cannot exempt a truly deep pixel; and all EIGHT wide taps
clamp to sea level (min(t,wl)) — near any coast the taps read +500..+2000 m land,
rwt sees a mere outlier, max(q,0.30) keeps 30% of it, and its SIGN flips as
bilinear tap positions slide along the coast. Land: bit-identical, measured 0
land-coloured pixels changed at the pinned framing. Hawaii chain, Scotia arc,
fracture floor: verified no-harm. Gates green, ice at baseline, storm 0 uploads.
DATA_V 20260801-0006, commit "No spike may flip a normal past the sun".

**THE SECOND ARTEFACT — the shallow-bank specks — is not the lace and survives it.**
Dark angular texel-scale chunks clustered on shallow banks (Burdwood, Falkland
shelf, Brazil/Chile coast strips), darks EXACTLY 0.70/1.34 of their neighbours on
all three channels. Elimination matrix, each by direct measurement at the same
pinned framing: residual caps x3 (byte-identical rows through every cap change);
NaN (magenta detector: zero hits); mesh displacement (uDisp*0: byte-identical);
polar branch (pw=0 at -52); data land-specks (decoded phan_0000: Falklands blob
only, Burdwood clean); raw-rug razor thresholds (rug viz: SMOOTH 0.61 at speck
pixels). What that last probe taught anyway: rug SATURATES (~0.6) on flat banks —
the field's 300 m rms shelf texel noise — so bakedRough=1 and the abyssal FABRIC
runs full-strength on continental banks where the ocean-structure field's
spreading-direction texels are FILL, i.e. garbage direction per texel. The specks
appear in a pure vec3(hs) viz — and that probe sits AFTER the sea-fabric normal
perturbation, which iteration 8 eliminated only at the DEEP band, never on banks.
ARMED FOR NEXT VISIT: (1) hs viz with the sea-branch fabric perturbation zeroed,
at the bank framing — one variant, decisive; (2) if confirmed, gate the fabric by
ocean-structure VALIDITY (crust age/spreading coverage or shelf proximity), not
by rug, which cannot distinguish steep from noisy. Probe files _lace_*.html and
the runner scripts remain in web/ (gitignored) and the scratchpad.

## Q — ITERATION 11, 2026-07-31: the pole joins the same ocean (user feedback)

The user reported the polar distortion "immune from our other improvements" — and
that immunity was the diagnosis: macro relief, the smoothed-depth gate, the robust
wide gradient, the shrinkage and its caps all lived inside the sub-63° branch, so
the polar ocean stayed a flat disc with a ring at exactly 63° where the systems cut
out, and every low-latitude improvement made it starker. Shipped: the submarine/land
machinery moved to a SHARED block parameterized by the branch's tangent frame
(Eax/Nax below 63°, the world-fixed ring frame t1/t2 above; all taps step-and-read,
pole-safe by construction), with basis conversion once at the end — direct assign
non-polar so that branch is float-identical (pixel-diff: 0 changed pixels at
Argentine and Hawaii; Scotia's changes confined to its in-frame polar band, 0 above
y=456). The vestigial (1.0-pw) macro fade — a no-op in a branch where pw≤0.004 —
became a branch-set weight: full at the pole, zero only inside ~89° where the
equirect columns converge (the bowtie the first after-shot showed at the exact
pole point; the fade dissolved it, verified by crop). prom/shelfHi now exist above
63° too, so shelf-band systems engage on Arctic shelves. Verified: 63° handoff ring
invisible (Fennoscandia framing); 80 Ma polar ocean carries shelf break + basin
swell; present pack ice shows margin structure with a smooth multi-year core;
39 Ma Antarctica has relief to the pole. Harness note: pb_sco white-frame was a
capture transient (redo clean) — a solid-white frame after multi-age shot runs is
the capture racing the decode, not a render bug. Gates green, ice at baseline,
storm 0 uploads. DATA_V 20260801-0035, commit "The pole joins the same ocean as
everywhere else".

**User feedback item 2, QUEUED (task #29): future-branch collision rigidity.** By
+250 Myr Australia scrapes through East Africa/SE Asia and exits shape-identical —
rigid-rotation future frames by construction. WP-07: 12.8 Mkm² of computed future
convergence is deleted; H-section: overlap at a convergent margin IS the shortening
signal. Next round: research the fut_* bake pipeline, design margin
indentation/suture building from the computed convergence, re-bake, verify at
+150/+250. Bank specks (iteration 10 matrix) remain armed behind it.

## Q — ITERATION 12, 2026-07-31: the weld (user feedback — Australia's shape)

S1-S5 built belts from the collision overlap but max() preserved every land cell
of both plates: an indenter crossed a whole collision with its outline readable.
S6, THE WELD, shipped after three measured calibration cycles: where collision
stands, the surface blends toward its own regional mean BEFORE the calibrated
uplift is re-added (so the S2/S4 +250 hypsometry moved <0.2 Mkm² at every
threshold — measured OFF/ON at matched resolution), and interleaved gulfs are
squeezed shut while deep gaps survive as remnant seas. The decisive design fact,
measured not assumed: the weld must drive off the BOTH-LAND OVERLAP (an area,
which survives wide smoothing) — a thin adjacency-line seed dilutes below its own
gates at welding width, which is why configurations 1-2 read identical on screen
(0.45% → 1.20% → corridor 4.45% |Δ|>50 m; sea→land closures 145 → 1,434 → 1,910
cells ≈ 465,000 km²). The weld carries its own wide low-power belt (WELD_SIGMA_X
2.2, WELD_POW 1.2, GAIN 1.6, MAX 0.85, SEA_LAG 0.25); the uplift keeps its sharp
calibrated one. Verified in-app: +250 interior reads as ONE welded orogenic
continent (no superimposed outlines, remnant seas); present-day control frame
untouched; coast-edge cells DOWN ~1% both at −125 and −250 (the pre-existing
coastal crenulation is inherited rigid-warp speckle, visible in the user's own
pre-weld screenshot — a future queue item, not a weld regression). Pipeline:
rebuild_future.py (50 frames, 67.6 min, e/r/o + climate solve), then per-frame
build_surface + bake_lakes + refresh_manifest. TWO HARNESS TRAPS for the log:
zsh does NOT word-split an unquoted $VAR — both sibling scripts received one
50-name string as a single argument, and build_surface.py exits 0 SILENTLY on a
missing basename (flagged for a loud-failure fix); and `{...} | tee` reports
tee's exit status, so the chain "succeeded" while dying — the absent CHAIN-DONE
marker was the truth. Verify batch work by output-file mtime census, never by a
piped exit code. Gates green, ice at baseline, storm 0 uploads.
DATA_V 20260801-0232, commit "A continent pays for its mountains in coastline".

## Q — ITERATION 13, 2026-07-31: the bank specks' carrier, proven and briefed

The iteration-10 suspect (fabric on fill-garbage shelf texels) died by direct
probe: the specks survive the sea-fabric normal-add zeroed, and an aniso viz
reads a solid 1.0 on the banks (the validity gate at ~3762 already works). The
TRUE carrier, proven by the first kill-switch this artefact has ever answered:
THE SUBMARINE CANYON SYSTEM — canyons off takes the cluster-box dark count from
~212-222 to EXACTLY 0. Mechanism, from its own code: the canyon noise domain is
sheared by a depth potential (CAX*(z*CF/78000)), and on bank edges the field's
±300 m texel noise shears adjacent pixels a full noise cell apart — k1-k0
becomes full-amplitude hash, ×9 into the normal plus the ×0.42 shadow —
re-entering through the z-shear the exact decorrelation the block's own comment
fixed for the angular step. Compounding it, cany's slopeBand thresholds RAW z.
Two H8 patches were implemented and MEASURED INSUFFICIENT (shear→gZSm,
slopeBand→gZSm: dark count 212→222, unchanged — the smoothed depth still
carries ~±134 m against a 260/78000 amplifier), and the slopeBand patch showed
a SIDE-EFFECT at wide zoom: a coherent band CONCENTRATES canyon coverage into a
heavy saturated stripe where noisy membership used to dither it soft. Both
patches REVERTED — nothing shipped this round. NEXT-ROUND BRIEF (one designed
change, A/B at wide+close): reformulate canyon elongation to follow the CLEAN
capped-gradient downslope direction (the way fold fabric follows gFold) instead
of a depth-potential shear; keep the seamount/prom guards; re-tune the shadow
bound; verify at Argentine wide (band character), bank close (specks=0 floor),
Hawaii (bit-identical expected), Scotia. Probe kit: _verify.html?app= variants;
nocany kill-switch reproduces the 0-floor.

## Q — ITERATION 14, 2026-07-31: real-scale mountains, coastlines that remember less

User round 2 for the future branch, both rulings shipped in one rebuild
(DATA_V 20260801-0511, commits "Mountains earn their height..." + fields).
THE BELT SPLITS: measured convergence (the both-land overlap) earns 9500 m at
its own power 2.0; adjacency-only contact earns 2900 m of foothills; combined
by max, never sum. S7 COASTAL EVOLUTION: the coastal band blends toward a
2-degree surface by COASTGEN 0.34 × frac × band weight — capes blunt, gulfs
fill, and the rigid-warp crenulation dissolves progressively with time. Weld
core deepened to 0.90/1.9. Calibrated across FOUR measured configurations on
the 1024-row preview (v1 overshot flat: collision power 2.5 crushes a patchy
overlap source to 0.2 Mkm² above 3 km; v2 overshot high: a 3n coalesce made
19.5 Mkm² above 2 km; v3/v4 bracketed): final +250 hypsometry 25.4 / 9.3 /
3.5 Mkm² above 1/2/3 km against today's 29.9 / 8.8 / 4.3 — a modest
supercontinent premium at 2 km, fewer extreme peaks, max 4.75 km base before
shader detail. AUSTRALIA: new coastline-persistence metric (fraction of the
rigidly-rotated present outline within 2 px of a final coast) drops 0.581 →
0.346 with interior survival 0.982 — two thirds of the outline genuinely
evolved, the continent intact. In-app verification: +250 interior reads as
arid orogenic upland with belts tracing sutures, clearly subordinate to the
present-day Himalaya control framing; −125 coasts softened; present-day
control untouched. Gates green, ice at baseline, storm 0 uploads. Remaining
future-branch items: residual blocky shelf steps at young fracs (S7 is
frac-weak there by design — revisit only if the user flags it), and the
canyon-domain redesign (iteration 13 brief) which is next.

## Q — ITERATION 15, 2026-07-31: the specks close; the camera confesses

THE BANK SPECKS ARE CLOSED (dark count 212 → 25, the survivors tracing genuine
slope walls). The road there rewrote the diagnosis twice: (1) the gradient-
aligned canyon-domain redesign from iteration 13's brief was implemented and
measured a NO-OP — a per-fragment tangent transform cannot anchor a
world-coherent stretch (dot(sdir,dh)=0 identically), which is worth keeping:
anisotropy needs a WORLD frame (the fabric's construction), not a local one.
(2) With the domain exonerated, the defect reframed as VISIBILITY: even a
healthy gully at ×9 normal gain and 0.42 shadow prints near-black blotches at
the noise's own 2-5 px cell scale, and a cany viz read 0.95 on the bank edges
the references show smooth — in-band by the system's own rules. Three levers
shipped: the depth-potential shear returns reading gZSm; punch grades by depth
(smoothstep(-350,-1100,gZSm) — full drama only below the shelf-edge zone);
and the closer, canyons require prom WELL BELOW the robust regional
(smoothstep(-150,-750,prom)) — a bank edge sits ABOVE its own regional however
steep its neighbourhood, a descending wall runs hundreds of metres under it.
Gully clamped ±0.5, shadow 2.4/0.34. slopeBand now thresholds gZSm. Hawaii
bit-identical at matched camera; the wide-frame canyon field reads as a
localized combed patch on the mid-slope, smooth above the break.

THE HARNESS CONFESSION, for every future framing: APP.lookAt TWEENS, the app
BOOTS FAR OUT, and the tween outlasts any fixed settle when zoom changes a
lot — so every FIRST-SLOT "wide" reference frame in this register (l10base_w,
f10_w, pb_*, the "zoom 1.25 whole-globe" shots) was a MID-TWEEN photograph
that happened to look like a plausible wide view. Every A/B stayed valid
because pin + identical slot order froze the same wrong camera on both sides
— which is also why the l13 "heavy band" read and the l13/l14 8.69% diffs
were artefacts of comparing a settled frame against a mid-tween one. The
driver now polls cam.position until still (3 consecutive 150 ms windows)
after the settle floor; the s0_* set is the first stabilized baseline. True
zoom semantics: 1.25 is a REGIONAL view, not whole-globe; whole-globe needs
zoom well under 1. Gates green, ice at baseline, storm 0 uploads.
DATA_V 20260801-0548, commit "Canyons on the walls, not on the banks; a
camera that has stopped".

## Q — ITERATION 16, 2026-07-31: UI round (user rulings)

Schematic shading and its toggle removed — Satellite is the default and only
view (state.shade stays 'sat'; the shader keeps uSchem at zero, so nothing
recompiled and the schematic path remains restorable in one line if ever
wanted). Geological Intervals panel now starts closed like its siblings.
Verified by full-DOM screenshot in the pane (app boots clean, right panel
goes View → Present-day layers, intervals collapsed). Gates green.
DATA_V 20260801-0605, commit "One way to see the world, and a quieter
sidebar".

## Q — REASSESSMENT, 2026-08-01: the road to Google Earth is now made of colour

First stabilized-camera sweep (ga_* set, ten framings, drag fix shipped the same
turn: zoom-proportional drag verified 0.1905 ratio at the clamp, exactly the
geometry's prediction). Zoom semantics settled for good: state.zoom IS camera
distance (smaller = closer); whole-globe needs ~4.5-5; APP.lookAt BYPASSES the
1.35 clamp (the "globe" shot at 0.62 landed under the surface clamp on abyssal
fabric — harness footnote).

STRUCTURE IS LARGELY THERE; COLOUR IS NOT. At every present-day framing the
distance to the reference is now dominated by palette truth, not relief:
- G1 LAND PALETTE (headline): our land is uniformly low-chroma olive/tan. The
  reference Earth's icons are missing: Amazon/Congo/SE Asia should be deep
  saturated rainforest green (ours a pale wash), taiga dark boreal green,
  Sahara warm orange-tan (ours olive), Australia's center RED, Ganges/N China
  plains agricultural green. Biome colour curves + chroma, possibly a baked
  vegetation-index field (rain+temp exist) if shader curves cannot carry it.
- G2 SHELF WATER: our shelves are pale washed halos with blobby edges; the
  reference shows narrow vivid turquoise bands with crisp seaward gradients.
  Depth-keyed chroma ramp retune.
- G3 OPEN-OCEAN TONE: ours is very dark navy with strong fabric at wide zoom;
  the reference is a calmer deep blue with subtle structure. Global brightness
  and fabric-contrast rebalance by pixel footprint.
- G4 CLOUDS AT CONTINENT ZOOM: grey haze smudges (e.g. over Sahul) rather than
  crisp cumulus fields; lighten/sharpen or thin at these zooms.
- Carry-overs: fabric seam watch (#23), Hawaii small-seamount pepper, future
  coastal blockiness at young fracs.
Round order: G1 first (several rounds, verified per-biome at Amazon/Sahara/
Australia/Siberia/India framings vs reference), then G2, G3, G4 as single
rounds. Drag fix DATA_V 20260801-0611-era, commit "The ground stays under
the hand".

## Q — ITERATION 17, 2026-08-01: G1 round 1 — the colours

All three biome-lattice axes re-anchored (wet end to true closed-canopy dark
green 0.075/0.235/0.098; taiga conifer green; hot sand warm orange 0.855/
0.678/0.447; olive cast cut from the dry/mid stops), wet-end grip pow 0.85 on
the humid half, savanna stipple deepened, red-bed warmed, and a LATERITE term:
arid hard ground on old shields iron-stains (bare × hardness × dryness ×
low-freq noise, 0.44 max) — central Australia reads red from orbit. Verified
at Amazon (dark carpet ✓), Australia (red interior ✓), Sahara (warmer, though
a green tinge still bleeds mid-desert), Siberia. THE REMAINING DISTANCE AT
THESE FRAMINGS IS THE CLIMATE FIELD'S REACH, not colour: the southern Amazon
and mid-Sahara sit at h values the palette can only obey. G1 ROUND 2 LEVER:
the h curve/bare gate (dry the Sahara core fully, extend canopy where Rf is
already high), verified against the same framings; then G2 shelf water.
Gates green, ice at baseline. DATA_V 20260801-0633, commit "The Earth gets
its colours back".

## Q — ITERATION 18, 2026-08-01: G1r2 + G2 + G4 in one pass; G3 closes honest

G1 ROUND 2 (climate reach): h = smoothstep(0.10, 0.72, Rf/(0.46·pet)) — the
aridity index kept, its response S-curved. Amazon canopy now spans the basin
as one dark sharply-bounded carpet; Sahara core cleans to orange erg (green
confined to Sahel + highlands); veget mottle floor 0.18→0.06; 122 Ma checked
(rich Cretaceous forest vs dry interior — the same curve serves deep time
correctly). G2 RE-SCOPED BY THE CODE'S OWN MEASUREMENTS: oceanColour was
calibrated against the reference frames by chromaticity/luminance binning in
an earlier round — "vivid turquoise" in the reassessment was wrong, and the
real defect was the smoothing plateaus' lobed edges printing through the
palette. Fix: zsb raw share graded by smoothed depth (0.55 above −40 m →
0.85 by −160 m) — crisp bank/lagoon rims, lace-band smoothing intact. G4:
cloud dens = pow(smoothstep(0.58,1.10,·),1.25), shade floor 0.80, core alpha
0.68 — the grey skirt over Sahul thins to a veil, cores whiten. G3 CLOSES AS
A NO-OP on principle: abyss tone and fabric contrast were measured against
the reference previously; re-judging calibrated values by memory is
regression by taste. First true whole-globe verification frame (zoom 4.6):
dark Amazon/Congo, orange Sahara, white broken cloud fields — the globe
reads near-reference at planet scale. NOTED for a future round: label
pile-up at whole-globe zoom is heavy (many overlapping labels — a
declutter-by-zoom pass is UX, not fidelity). Gates green, ice at baseline.
DATA_V 20260801-0708, commit "Rain decides, rims sharpen, clouds whiten".

## Q — ITERATION 19, 2026-08-01: few names from far away

Label declutter by zoom: zf=(state.zoom−2.4)/2.2 clamps 0..1; minPri=zf·62,
cap=60−zf·44 — regional and closer unchanged, whole-globe ~15 well-spaced
majors (measured live: 4 shown at 4.6 in the pane's DOM, ~15 in the richer
headless framing). THE HARNESS TELL: the first verification frame showed NO
change because snap()'s capture path projects labels ITSELF (the DOM path is
dead in a hidden pane) — the pane's live DOM proved the code worked while the
instrument photographed the old behavior. snap now mirrors the same tiering:
the instrument must match the instrumented. Gates green. DATA_V
20260801-0730, commit "Few names from far away".

Register state after nineteen iterations: G1 rounds 1-2, G2, G4 shipped; G3
closed honest; declutter shipped; both user-feedback future rounds and all
armed ocean artefacts closed. Open: fabric-seam watch (#23, unreproduced),
Hawaii pepper wish, future coastal blockiness at young fracs, per-biome
palette fine-tuning pending user verdict.

## Q — ITERATION 20, 2026-08-01: knoll pepper

Sparse sun-embossed knoll field on the deep floor (two taps at kd*310 — one
light-shifted 0.38 cells for the emboss — provinces at kd*23, threshold
0.775-0.85 on the max, ±0.24 tone, deepw- and footprint-gated). Hawaii frame:
fine shaded speck field, chain/halos untouched. Queue residual "small-
seamount pepper" closes; remaining open items are all user-verdict or
watch-list. Gates green. Commit "The floor gets its knolls".

## Q — ITERATION 21, 2026-08-01: land carves harder (loop resumed)

User resumed the loop: "more to go to Google Earth equivalence." Fresh pass at
the under-examined framings (39 Ma North America's first post-colour look, the
present prairie): the consistent gap is HILLSHADE PUNCH — soft wash where the
reference cuts valley shadow. Shipped: land shade floor 0.70→0.63, gain
0.62→0.74, cap 1.18→1.24 (sea unchanged at 0.70 — load-bearing in the lace
forensics); land macro second-difference 0.40→0.50. Measured +8% land-frame
luminance std at both framings; Cordillera visibly carved; Sahara stayed clean.
Gates green. Commit "Land carves harder".

## Q — ITERATION 22, 2026-08-01: far rivers refuse the shader (measured, reverted)

Three thread configurations over the trunk field were each INVISIBLE at the
Ob/Amazon framings; a trunk viz then measured the truth: at zoom 2.2 the
field's p99 is 0.112 (p95 0.100, mean 0.102) — the corridor signal at
regional footprints is ~0.1 over a 0.1 background, and no threshold exists
that draws a thread from a flat field. All thread edits REVERTED (zero
visible change = dead weight). THE ARCHITECTURAL BRIEF for a future round:
GE-style far-zoom rivers need a dilution-proof source — (a) bake-time traced
river POLYLINES per keyframe (flow-accumulation ridge tracing → rivers.json)
drawn as geometry like the boundaries layer, resolution-independent, the
right shape; or (b) a max-pooled trunk mipmap texture (max-downsample
resists averaging by construction) sampled at far footprints. (a) is
GE-equivalent and preferred; it is a bake+overlay round, not a shader
constant. Iteration 21's carve shipped earlier this wake and stands.

## Q — ITERATION 23, 2026-08-01: the river layer meets a false control (reverted)

The geometry-rivers round (iteration 22's brief) was implemented in full —
runtime hysteresis trace from the resident drainage bitmap (3,708 segments at
age 0, ~10 ms, zero new data), lineSeg geometry, crossing rebuild + loop
retry — and proved UNPAINTABLE in the headless pipeline through an eleven-way
elimination: object built/visible/parented/in-traversal (new ?rivdbg driver
mode), coordinates verified (53/47 N/S segment census — plausible for cell
counts), no NaN, frustumCulled off, radius ladder to 1.05, group swap into
overlay.boundaries, and an INIT-TIME STATIC LINE built exactly as boundaries
are — all zero pixels with depth test on; depthTest:false paints (867 px).
THE CONTROL WAS FALSE: the "990 red boundary pixels" that established 'lines
render headless' match HOTSPOT MARKERS (?layers=1 enables both); GL lines
plausibly never render in --headless=new ANGLE Metal shots at all, and the
depth-off paint is the one path the pipeline allows. All app edits REVERTED;
?rivdbg (build-state POST + same-session shot) and ?rivage stay in the
driver. NEXT ROUND, IN ORDER: (1) re-establish the control — boundaries-only
headless shot (extend layers param to individual flags) vs the PANE's real
render of the same state; if lines truly never rasterize headless, the
verification method for any line layer is the pane or pixel-diff-on-live,
and the harness limitation gets its own register note; (2) only then re-land
the rivers layer (the trace itself is proven and cheap). Iteration 21 stands
as this wake's shipped work.

## Q — ITERATION 24, 2026-08-01: rivers land; the harness confesses twice more

THE RIVERS LAYER SHIPS (DATA_V 20260801-era, commit "Rivers, traced from the
world's own drainage"): runtime hysteresis trace from the resident drainage
bitmap at each keyframe (~10 ms, zero data shipped), line geometry at 1.0035,
0x27556b @ 0.55, loop retry for late decodes. The Amazon basin reads as the
reference's dark winding thread network in composited verification frames.
TWO HARNESS FACTS, now permanent instrumentation: (1) GL LINE PRIMITIVES DO
NOT RASTERIZE in --headless=new ANGLE Metal — the boundaries-only control
(new granular ?layers=boundaries flag) frames 42 px over the Mid-Atlantic
Ridge vs 5,282 for hotspot markers; every past "lines render headless" belief
traced to markers. snap() therefore COMPOSITES line layers itself with the
render camera (the instrument draws what the scene provably holds; real
rasterization is a real browser's to confirm — the user's next look is the
GL-side verification). (2) The compositor's first horizon test (normal-based,
copied from the label path) rejected ALL segments (census 3539 occl / 0 pass)
while the depth-off magenta probe had already painted exactly the Amazon-box
count (867=867) at correct pixels — a near-side test is a DISTANCE
comparison (|wp−cam| < |cam|), not a normal test; why labels pass the normal
form remains unresolved and does not matter to the fix. Iteration 23's
"depth occlusion" mystery dissolves: there was never depth occlusion — lines
never rasterized at all, and depthTest:false "painting" was ANGLE's one
line-drawing path. Residuals: prairie-scale networks sit below the 15-cell
component floor (Mississippi absent at half-res — lower the floor or full-res
trace in a tuning round); thread lattice texture at close zoom; map view
skipped. Census instrumentation (?rivdbg: build state, N/S and lon-box
censuses, per-segment outcome counts) stays in the driver.

## Q — ITERATION 25, 2026-08-01: the Mississippi seeds

River-trace constants calibrated by an inclusion census (python prototype:
strong 0.43 / weak 0.22 / floor 10 at half-res → 18 networks, 1,329 cells,
Mississippi TRUE; shipped as 109/55/10 in bytes). Composited prairie frame
shows the thread to the Gulf; 569 px changed vs pre-rivers baseline. Gates
green. Commit "The Mississippi seeds". Remaining river residuals: close-zoom
lattice texture; map view; GL-side look awaits the user's browser.

## Q — ITERATION 26, 2026-08-01: three user-reported regressions, all closed

(1) THE GRID PATTERNS ON LAND were the iteration-24 river layer: an edge
between every adjacent pair of network cells draws a multi-cell channel as a
lattice. Three measured steps: one edge per cell to its highest-drainage
(= downstream) neighbour killed the lattice but left herringbone barbs;
pruning headwater tips helped; and the decisive measurement was that the
drainage field's channels are SEVERAL CELLS WIDE AT EVERY RESOLUTION (88-90%
of channel cells have >=3 channel neighbours, native 2048x1024 included), so
no threshold can thin them. Zhang-Suen thinning now runs over the network's
own cells (milliseconds) before the tree is built: single-cell threads.
(2) THE STRAIGHT BIOME BANDS returned because the jitter was applied AFTER
the humidity S-curve -- once saturated, noise on 0 or 1 does nothing, so all
wander collapsed onto a thin band. The perturbation now enters the aridity
INDEX, weighted by 4h(1-h) (peaks at the boundary, vanishes where the biome
is committed: cores solid BY CONSTRUCTION), plus real terms -- orographic
uplands, water-holding basins, green river corridors. First attempt (flat
+/-60% on the index) broke the Congo/Amazon canopy into patches and was
replaced by the edge weighting.
(3) THE FLAT FUTURE had two causes. EROSION_TAU_RELIEF 150 -> 340 Myr (at
150, a quarter-billion years leaves 19% of every slope -- a global peneplain;
at 340, 48%. +250 hypsometry 27.2/12.3/3.7 vs today's 29.9/8.8/4.3). And the
future frames shipped NO _t FIELD AT ALL, so orogens rendered as isotropic
hummocks -- "the mountains look weird". The belt raster is now baked into
fut_XXXX_t.webp per frame: shortening = belt strength, fold axis = the belt's
iso-contour tangent (a fold axis runs ALONG a belt), build_tectonic's own
encoding so the shader needed no change. Verified binding in-app: uTect=1 at
+250, fabric over 1.5% of the globe. COASTGEN 0.34 -> 0.46 takes Australia's
coastline persistence 0.346 -> 0.275 at 96% interior survival. Note for a
future round: future frames still ship no _p or _v (uMat=uWarp=0), so future
crust neither carries material coordinates nor advects between keyframes.
New driver mode ?evalq= (arbitrary in-app expression -> POST) is how the
uniform binding was proven. Gates green, ice at baseline. DATA_V
20260801-1732.

## Q — ITERATION 27, 2026-08-01: the canopy threshold no continent could reach

Measured the aridity index over the shipped fields (not guessed): Amazon 0.55,
Congo 0.36, Siberia 0.24, Sahara 0.11 — against a curve that only closed the
canopy at 0.80, so the Congo rendered 3% forested and the Amazon 37% where the
reference shows solid carpets. Canopy saturation 0.80 -> 0.62: wet cores close,
margins stay woodland, dry end unmoved (verified at Sahara and Siberia). Also
verified this wake: the rebuilt future terrain reads as a textured
supercontinent with an inland sea, and the derived fold fabric draws the
Neo-Himalaya as LINEAR PARALLEL RIDGES rather than hummocks — the round-26
bake works in the rendered world, not only in the uniform. The Congo remains
the model's own dry spot (its rainfall runs ~35% under the Amazon's where
reality is comparable) — a climate-solve question, logged, not papered over.
Gates green. DATA_V 20260801-1839.

## Q — ITERATION 28, 2026-08-01: the future stops dissolving

The future frames shipped no _v, so the app CROSS-FADED them -- the double
exposure H1 exists to prevent, still happening past the present. Derived
exactly rather than fitted: each group turns about ONE axis by an angle
proportional to frac, so the keyframe-to-keyframe rotation is a rotation
about that same axis by the angle difference (no raster differencing, no
plate model needed). New `build/bake_future_v.py` bakes all 50 in 1.9 min --
ownership is the only thing it needed from the elevation pipeline, so a full
future_grid per frame was unnecessary. Convention identical to
build_displacement (interval rotation applied to the grid's own directions,
east/north in the tangent frame), and Laplace-filled across unclaimed new
ocean because a hard zero against 2 deg of plate motion tears the texture
along every margin. Max 2.05 deg/step (range 12). VERIFIED IN-APP: uWarp=1
at +200 Myr; a mid-interval frame renders clean at 97% of a keyframe's edge
energy. Remaining future gap: _p (material coordinates) -- uMat=0, so future
detail is world-fixed rather than travelling with its crust. DATA_V
20260801-1918.

## Q — ITERATION 29, 2026-08-01: future crust carries its own texture

The last missing future motion field. Without _p, uMat stayed 0 past the
present and every ridge was evaluated at a pure function of POSITION -- the
H2 defect (a continent sliding out from under its own texture) alive in the
future era. Exact derivation again: build_platefield stores "the plate's
rotation from 0 Ma to this age", and for a group turning about one axis by
an angle proportional to frac that is (axis, frac x angle) -- consistency
with the Phanerozoic DEFINITION is what makes matDir() mean the same thing
on both sides of the present, so no sign guessing was needed. New
`build/bake_future_p.py`: ten groups into 48 slots, unclaimed cells take the
nearest claimed slot (as the Phanerozoic bake handles its microplate tail),
50 rasters + 50 platerot entries in 36 s. VERIFIED IN-APP at +200 Myr:
uMat=1 with uWarp=1 and uTect=1 -- the future now carries the complete
motion model (advection, material frame, fold fabric) -- and the collision
zone renders with no slot seams. The future-branch gap list from iteration
26 is now empty. DATA_V 20260801-1946.

## Q — ITERATION 30, 2026-08-01: canyons stop combing enclosed seas

A fresh close-zoom pass (the reference's own strongest ground) found the
Mediterranean covered in fingerprint whorls. Kill-switch bisection: fabric
normal off — whorls remain; dequantisation block off — whorls GO; canyons off
— basin texture energy halves (5.56 -> 2.87). The carrier is the CANYON
system, and the mechanism is iteration 10's own fix turned against it:
shelfHi = regional + 900, and the 160 km stencil CLAMPED its land taps to sea
level, so an enclosed sea reported a shelf directly above every basin cell.
Fix (three parts, each measured): land taps are EXCLUDED from the robust
regional rather than clamped (weight zero = "carries no information"; falls
back to the smoothed depth where nothing submarine is in reach); the
shrinkage stands down where the stencil is mostly land (scov gate); and
canyons require a sustained regional downslope (gWide 40-110), because depth
and local relief cannot separate a basin floor from a continental slope
(measured cany 0.56 / tilt 0.81 across the basin) while a 160 km descent
can -- and turbidity currents need precisely that. Result 5.56 -> 4.12
against the 2.87 floor, combing now confined to the margins where
Mediterranean canyons actually are; Argentine pixel-identical, Hawaii 0.4%.
Open from this pass: land relief at close zoom still reads soft against the
reference (the Alps as a brown smear) -- the next round's target.
DATA_V 20260801-2043.

## Q — ITERATION 31, 2026-08-01: ground you can stand on

Queue item 4 (close-zoom land grain), and the cause is structural rather than
a constant: the hillshade differences the field over a FIXED 35 km baseline at
every zoom, so a close pass sees a 35 km slope and nothing finer except what
the procedural octaves supply. Added a ~1.1 km band gated at gFineFade>0.80
(harder than the 2.4 km band's 0.55) so it exists only when a pixel is
genuinely small, raised the 2.4 km band 0.42->0.52, and scaled the whole
normal perturbation by (1+0.55*closeG). Measured: local contrast +19% Alps,
+29% Himalaya; the Himalaya reads as dissected snow and rock. HONEST CAVEAT
recorded rather than claimed away: the footprint fade reaches regional zoom,
so the 122 Ma reference framing gains texture too (32% of pixels move) --
inspected and judged an improvement (the Urals read as a range), but it is a
look change at a verified framing, not a no-op. DATA_V 20260801-2118.

## Q — ITERATION 32, 2026-08-01: one feature, one label (user report)

TWO LAKE PANNONS at 9 Ma, one in the western Mediterranean. Cause: features.py
carried the lake TWICE -- ("sea", 4-11) from before lakes were modelled and
("lake", 4.5-11.6) as what it is -- and each type has its own snapping rule, so
the sea-typed copy was pulled to the nearest open water and walked 1,500 km out
of its basin. Ethiopian Highlands was doubled the same way (region 0-30 +
plateau 0-31). Both stale entries removed; 336 -> 334 labels. NEW GATE
`audit_label_dupes.py` (registered in audit_all): same name AND overlapping
windows fails the build, while the legitimate case passes untouched -- a
drifting craton SHOULD be described at different positions in different windows
(North China 120-420 and 420-900), and flagging those would train the reader to
ignore the check. LITERATURE PASS (user's link): the Scandinavian Caledonides
article's own correction is that today's Scandes are NOT the Caledonian peaks --
the orogen was eroded and the modern range is a much later uplift of its roots,
glacially cut. Our card implied the range still stands; rewritten with the
430 Ma Baltica-Laurentia collision and the erosion/uplift distinction.
STANDING WORK for coming rounds: continue the per-formation literature review
(orogens first -- they are the most visible and the most often mythologised),
correcting cards AND, where the source describes present-day expression
(plateau remnants, fjord coasts, peneplains), checking that the rendered ground
agrees. DATA_V 20260801-2211.

## Q — ITERATION 33, 2026-08-01: the literature review begins (batch 1)

Ten orogen articles read against our own cards, with a reusable extractor
(`scratchpad/lit_extract.py`: infobox rows + lead + the dating sentence, so a
round can cover a dozen features without reading a dozen articles).
CORRECTED: Transantarctic Mts (Ross-orogeny ROCK, but the range is a ~65 Ma
rift-flank uplift), Urals (worn to 1,894 m; Laurussia met Siberia AND
Kazakhstania), Atlas (only the High Atlas is Alpine; the Anti-Atlas is a
re-lifted Palaeozoic belt), Variscan window 360 -> 380 Ma.
CLEAN: Appalachians, Alps, Andes, Zagros, Tien Shan, Verkhoyansk.
THE PATTERN WORTH NAMING, and the thing to hunt in later batches: three of
four corrections are the same error -- a card that gives only the OROGENY
implies the peaks have stood ever since, when a range's rocks and its relief
routinely differ in age by hundreds of millions of years (the Caledonides
correction in iteration 32 was the same shape). Next batches: the remaining
~53 orogens, then cratons/shields, then seas and basins; and for features
whose sources describe present-day expression, check the RENDER agrees, not
only the prose. DATA_V 20260801-2245.

## Q — ITERATION 34, 2026-08-01: the literature review, completed

Sixty-seven features checked against their own sources across seven batches,
screened by `scratchpad/lit_check.py` rather than read one by one: every age
the article states is compared with the label's window, the summit elevation
is pulled from the infobox, and a flag is raised where a card claims a range
stands "today" without saying it has been worn. Only flagged lines were read.

COVERAGE: 43 orogens; cratons and shields (Canadian, Fennoscandian, Guiana,
Yilgarn, Kalahari, Brazilian); oceans and seas (Tethys, Paratethys,
Panthalassa, Iapetus, Rheic, Western Interior Seaway); desert, rift, ice
sheet, plateaus, basins, rainforests.

CORRECTED (8 total, this iteration and 32-33): Caledonides, Transantarctic
Mts, Urals, Atlas, Variscan window, Verkhoyansk, Massif Central, Rhodope,
East African Orogen window. SEVEN of nine are the SAME error -- a card that
names an orogeny implies its peaks still stand, when rocks and relief
routinely differ in age by hundreds of millions of years. That pattern is now
the review's first question, and it is worth carrying to any future feature
text.

CLEAN AND WORTH SAYING SO: all eight North American Palaeozoic belts, all
eight Precambrian belts, every craton, every ocean and sea, the Sahara, the
East African Rift, the Laurentide sheet, Deccan, Tibet, Colorado Plateau,
Great Plains, Amazon, Congo. Verified non-gaps: the Siberian Traps are absent
from labels.json BY DESIGN -- they are a large igneous province and live in
the volcanism layer with peak 252 Ma (Deccan appears in both because it is
also a plateau today).

SCREEN LIMITS, recorded so a later reader does not trust it blindly: craton
"windows" are DISPLAY ranges, not formation ages, so age comparison is
meaningless for them; a range that is still rising may honestly claim to
stand today (Zagros, Laurentide rebound), which the refined screen now
allows. DATA_V 20260801-2306.

## Q — ITERATION 35, 2026-08-02: reading the articles, and what we did not have

The user's correction: the iteration-34 screen (infobox + lead + dating line)
is not reading an article. Two changes to the method, both kept:
(1) `scratchpad/lit_sections.py` pulls WHOLE geology / tectonics / formation /
palaeogeography / glaciation sections -- a 250 kB page is mostly climate and
economy, and the part that can teach this model something is a few thousand
words that want reading in full; (2) the review now runs against CATALOGUES
rather than only against our own list, which is the only way a gap can be
found at all.

CATALOGUE DIFF (Wikipedia: List of orogenies -- 91 named events against our 63
labels). The gaps were systematic, not random: Australia's INTERIOR orogens
and New Zealand were absent entirely. FIVE ADDED, each read in full first:
Southern Alps / Kaikoura (0-25 Ma; the model had NO New Zealand feature),
Delamerian (514-490, Flinders + Mount Lofty stumps, Ross Orogeny correlative,
faults active again since the Miocene), Petermann (630-520) and Alice Springs
(450-300) -- central Australia squeezed from within, twice, a thousand km from
any margin, the second tilting Uluru's beds to vertical -- and Hunter-Bowen
(265-230, arc accretion along 2,500 km of margin). 334 -> 339 labels.
HARD LIMIT FOUND BY READING: the three largest orogens in the catalogue
(Trans-Hudson 2.0-1.8 Ga, Svecofennian 2.0-1.8, Eburnean ~2.1) are older than
this model's 1000 Ma horizon and cannot be represented here at all -- worth
recording so a later reader does not "fix" their absence.
DETAIL HARVESTED, not yet applied: the Paratethys sections carry a great deal
we do not say (Oxfordian rift origin as an arm of the Central Atlantic system;
descent from Peri-Tethys; the Molasse / Vienna / Carpathian / Pannonian basin
chain; a Middle Miocene "Paratethyan biodiversity hotspot" of coral reefs and
deep-water endemics that lasted only ~3 Myr before cooling and anoxia ended
it). NEXT ROUNDS: work the section-reader across the remaining ~60 scraped
articles and the other catalogues (large igneous provinces, ancient lakes,
inland seas, cratons), enriching cards from full text and adding what is
missing and in range.

## Q — ITERATION 36, 2026-08-02: reading in full, and a deploy that lied

FULL-TEXT ENRICHMENT (geology sections read whole, not sampled):
- TIBETAN PLATEAU. Our card said "raised by India's collision" and stopped.
  The article's history is far better: a deep valley between ranges in the
  Palaeogene; suture zones that stayed tropical LOWLANDS until the late
  Oligocene, letting biota cross; a surface that FELL ~900 m between 25.5 and
  21.6 Ma before climbing again; near-modern height by 14-8 Ma; still rising
  ~5 mm/yr; and a genuinely open debate about whether its low relief is an
  uplifted peneplain or infilled basins at altitude.
- PARATETHYS. Descent from the Peri-Tethys, the Molasse-Vienna-Carpathian-
  Pannonian-Black-Caspian-Aral chain, narrow shallow gateways causing
  repeated anoxia, and a Middle Miocene coral-reef biodiversity hotspot that
  lasted ~3 Myr before cooling and anoxia ended it.
CATALOGUE DIFFS COMPLETED: large igneous provinces -- our 62 LIPs already
cover the catalogue, no gaps; ancient lakes -- added Lake Malawi (8.6 Myr,
more fish species than any lake on Earth) and the Aral Sea (Paratethys's
easternmost survivor); inland seas -- our 35 sea labels already include the
Sloss sequences and every catalogue entry in range.
A DEFECT THE BUILD ITSELF REPORTED, once its output was actually read: all
three Western Interior Seaway phases lay partly or wholly outside its own
78-95 Ma label window, so none could ever display. Clipped to the window
(90-95 opening, 82-90 widest, 78-82 withdrawing); Mowry and Bearpaw own the
ends by design.
AND A PROCESS LESSON, paid for in a false deploy: two cards were inserted
into the lake RADIUS table -- a dict of numbers keyed by the same names --
so lake_shape() multiplied a sentence by 0.72, build_labels died, and the
site kept serving the previous file. The deploy check reported "339 labels,
no Malawi" and was believed only because it was checked. VERIFY THE BUILT
ARTEFACT, NOT THE SOURCE EDIT: a successful string replacement is not a
successful build. 341 labels live. DATA_V 20260802-0058.

## Q — ITERATION 37, 2026-08-02: a copy-edit of all 341 cards

Every card read in full, substance untouched. MECHANICAL (applied only to
string literals, via Python's tokenizer, so no code or comment moved): 183
spaced double hyphens -> em dashes, matching the style the other cards already
used; 20 shouted words back to normal case (BALTICA, WOLFCAMP, LEONARD,
GUADALUPIAN, OCHOAN, DRY, PLUME, FRINGING REEF, BARRIER REEF, ATOLL, GUYOT,
LOWLANDS, RE-RAISED, BACK-ARC BASIN, APART, INSIDE -- LOWLANDS was mine, from
iteration 36); "million km2" -> km². Six further dashes sat across line
continuations where " -- " was never contiguous inside one literal, so the
first pass could not see them.
FOUND ONLY BY READING: "Parana- Etendeka" carried a space inside the compound
name because the string broke after the hyphen (the Walvis card spells it
correctly, which is how it stood out); "Archean" in the West Africa card
against "Archaean" in the Yilgarn one; and the label "Paleo-Tethys" against
"Palaeo-Tethys" used everywhere else in the prose. That last is a DICT KEY in
features.py, life.py and feature_art.py -- five uses had to move together or
the life and art lookups would have silently stopped matching, which is the
kind of rename that looks cosmetic and is not.
Verified in the built artefact rather than the source (iteration 36's lesson):
341 cards, zero mechanical issues, Palaeo-Tethys present, old spelling gone.
DATA_V 20260802-0210.

## Q — ITERATION 38, 2026-08-02: three user reports, and the measurement that
## reframes the biome problem

LABELS AT EVERY ZOOM. The 2026-08-01 zoom tiering is removed from both the live
layout and the capture path. The user's reason is better than the one it was
built for: a name present at one distance and gone at another cannot be checked
for, so tiering defeats INSPECTION -- it hides the difference between a label
the model lacks and one the view is withholding. Collision avoidance is now the
only thing that hides a name.

TETHYS x3 ON ONE SEA. "Tethys" and "Neotethys" are two names for the same
Mesozoic ocean, so the model labelled one basin twice, with Palaeo-Tethys on the
same water wherever the windows overlapped. Duplicate Neotethys entry deleted;
Tethys Ocean takes the whole 45-260 Ma life and moves SOUTH of the Cimmerian
ribbon; Palaeo-Tethys moves NORTH (102, 24) to where it lay. 341 -> 340 labels.

BIOME BANDS: STRUCTURAL FIX, THEN THE REAL ROOT CAUSE.
Fix shipped: everything driving the biome lookup was ultimately LATITUDE
(zonal rainfall; warmth = latitude minus lapse), so jitter only wobbled a line
that stayed a line. Fetch -- how far the wind has run over land, already baked
in the surface field -- is the one available variable with continental SHAPE
(measured 0.42-0.46 maritime, 0.96-1.00 interior), and now modulates both biome
axes. The boreal band bends into the interior as on Earth. Coupling halved after
the first strength dried the entire Atlantic seaboard to steppe: fetch is UPWIND
distance over land, not distance to the sea, so on east coasts it double-counts
against rainfall.
THE ROOT CAUSE, MEASURED (new task #37, G5): the baked RAINFALL FIELD is far
too dry over eastern continents. E North America Rf 0.04 against NW Europe 0.24
-- a sixfold gap reality does not have, both being roughly 700-1200 mm/yr --
with C Siberia 0.03 and the southern Great Plains 0.08, and the Congo already
measured ~35% under the Amazon. Converted to the humidity index those read
0.12, 0.14 and 0.18: steppe or desert. THE BIOME SHADER IS FAITHFULLY RENDERING
A BROKEN FIELD. Every "biomes look wrong" report in this session traces here,
and no amount of shader tuning can fix it -- the next round belongs in
climate.py's moisture advection, not in the palette.

## Q — THE GOOGLE EARTH PLAN, 2026-08-02 (five new reference frames)

Reference set: continental USA, Fennoscandia/Baltic, China/Japan, Americas from
orbit, Africa/Europe from orbit. Read against our own captures of the same
ground, the differences sort into seven items, in value order. G5 is first
because every biome complaint in this session traces to it.

G5 RAINFALL (root cause, task #37). Measured: E North America Rf 0.04 vs NW
Europe 0.24; C Siberia 0.03; S Great Plains 0.08; Congo ~35% under Amazon.
Reality has no such gaps. The biome shader renders this faithfully, so no
palette work can fix it. Belongs in climate.py's moisture advection: interiors
lose water too fast and there is no non-westerly moisture source (Gulf and
Atlantic inflow to eastern North America, monsoon inflow to Asia). Rebuild
rainfall -> surface -> lakes; gate on Rf ratios at six control boxes.

G6 DESERT INTERNAL STRUCTURE. GE's Sahara is not one tan: pale cream sand seas,
ORANGE dune fields, dark rocky massifs and hamada, white salt pans, all at
continental scale. Ours is close to uniform. Buildable from fields we already
ship (aridity, substrate hardness, drainage, the erg labels).

G7 ALPINE ZONATION. Every major range in the references is white on top, bare
grey-brown rock below the snow, dark conifer below that, in narrow bands that
follow the ridge. Ours reads as a broad brown smear with snow only at the
highest ground. Elevation + temperature banding, per pixel.

G8 GLACIATED-SHIELD LAKE STIPPLE. Fennoscandia and the Canadian Shield in GE
are dark green stippled with THOUSANDS of small blue lakes -- the single most
recognisable texture of deglaciated crust. We ship 1,117 present-day lakes but
they do not read at this density.

G9 CARBONATE PLATFORMS. The Bahamas and the Caribbean banks are the brightest
thing on the Americas frame: vivid turquoise over shallow carbonate. Our shelf
palette is uniform pale blue and misses them entirely.

G10 FOREST PATCHINESS at 10-50 km. GE's forests vary continuously (clearings,
burns, ridges, agriculture); ours are smooth washes at that scale.

G11 COASTLINE CRISPNESS. Ours pixelates at the 10 km field near close zoom;
GE's coast stays sharp because its data does not run out.

Order of work: G5 (bake, multi-round), then G7 and G6 (shader, visible
everywhere), then G9, G8, G10, G11. Each round: implement, verify headlessly at
the matching reference framing, gates, deploy, register.

## Q — ITERATION 39, 2026-08-02: G5, the rainfall field — a sign, a geometry,
## and moisture with no upstream source

Iteration 38 measured the thing that made every previous biome round fail:
**eastern North America was drier than the Sahara** in our own field (0.048 vs
0.043). This round fixed the climate solve rather than the palette. Four
defects, each found by measurement, each structural:

**1. No meridional transport.** `_rainfall` advected moisture only east-west,
so the Atlantic and the Gulf sat downwind of nothing and North America's east
coast was fed by air that had crossed the entire continent. Added `_advect_ns`,
a poleward march per hemisphere, gated to the cyclone belt (32-62°) and damped
by subtropical descent. Eastern North America ×2.6.

**2. The subsidence shadow was cast the wrong way.** The Rodwell-Hoskins block
had a careful paragraph explaining that monsoon heating drives descent to its
WEST — and then `np.roll(ms, +shift)`, which moves a field EAST. So India's
descending limb was landing on southeast Asia. Measured consequence: **the Rub
al Khali indexed 0.33 while monsoon China indexed 0.20** — the model had the
desert and the forest swapped. One character.

**3. Descent delivered in 40° jumps, over ocean.** Three discrete lags meant
Arabia's shadow was sourced from exactly 40/80/120° east — the Bay of Bengal,
which is ocean, where `monsoon × land` is zero. Replaced with a continuous
westward-decaying limb, and weighted to the subtropical ridge (26°): one
uniform gain could not both dry the Rub al Khali and spare the Sahel, because
they sit on the same belt and differ in LATITUDE, not longitude. After: Sahel
0.103, Sahara 0.010.

**4. Recycled moisture with no upstream source.** The evapotranspiration floor
was a constant, so 3,000 km into Asia the air was still being handed water that
had never fallen anywhere. Made the floor decay with distance since the air
last crossed open water (`RECYCLE_KM = 1800`). Kazakhstan and the Taklamakan
had been indexing as temperate forest.

**AND ONE THE FIX ITSELF INTRODUCED.** Each column of the meridional march is
an independent 1-D atmosphere, so neighbouring columns drift apart and the
field carries vertical stripes — the exact mirror of the horizontal streaks the
zonal pass leaves, which the code already fixed years ago three lines below.
Mixed the moisture laterally INSIDE the march (eddies, not a post-hoc blur):
field streak energy −16 to −39%.

**The threshold was never the problem.** Re-derived against the repaired field,
the canopy curve lands at `smoothstep(0.03, 0.61)` — the top essentially
unchanged from the 0.62 chosen in iteration 27. Every past attempt to tune this
line traded one continent for another because the field made it impossible:
with the Rub al Khali at 0.404 and the Congo at 0.321, **no threshold placed
anywhere separates forest from desert**. Chosen by minimising misclassification
SEVERITY over 18 reference biomes, not count: 15/18 exact and nothing off by
more than one class, so no desert draws as forest.

Rainforest 0.41-0.56 · temperate forest 0.33-0.40 · steppe 0.08-0.32 · desert
0.01-0.02.

**Verified visually, A/B, by re-baking the pre-change field from `HEAD`'s
`render.py`** — the fields are gitignored, so the baseline had to be
regenerated rather than checked out. Before: the whole eastern United States
tan, indistinguishable from the Great Plains. After: green forest → gold plains
→ brown west, with the hundredth-meridian dry line where it belongs. The same
A/B settled a false alarm: the soft north-south bands in the eastern US are in
the BEFORE frame too — drainage corridors, not something this round introduced.

Cost: 251 rainfall fields (15 min), 251 surface fields (21 min), lakes, manifest
— `_d` and `_w` both derive from rain. Gates all at baseline (ice 1 finding at
570 Ma, label dupes 0, storm gate 0 synchronous uploads). Pangaea's arid
interior deepened, which is the right direction for a megamonsoon supercontinent.

Still open on this front, for later rounds: the Congo does not read as the solid
dark carpet GE shows, and the Rub al Khali, Taklamakan and Kazakh steppe are
each one class too wet.

## Q — ITERATION 40, 2026-08-02: G7, a treeline is an isotherm, and a band you
## cannot see is not a band

The bare-rock band was `clamp((zp-1700.0)/1500.0)` — **one absolute altitude for
the whole planet**, ramped over 1.5 km. 1,700 m is alpine desert in Lapland and
cloud forest in Ecuador, which is why every range read as one broad brown smear.

**A treeline is not an altitude, it is an isotherm** — the same physics the ELA
solve three lines below already models, with a different threshold. So it is
derived the same way, from `T0` and the same 5.8 °C/km lapse. The threshold
itself has to move with latitude: treeline sits near +3.5 °C mean-annual at the
equator but BELOW freezing in the Alps, because a seasonal climate grows trees
through a warm summer that a cold annual mean hides. `s2` (sin² lat), already in
`T0`, is the seasonality proxy. Calibrated against real treelines: ~3,900 m
equatorial Andes, ~1,750 m Alps, floor 600 m in Lapland.

**Then the honest part: moving it changed almost nothing.** 3.1% of Himalayan
pixels, 0.6% of Andean. A red-paint diagnostic proved the code ran and covered
the whole range — so the band was in the right place and had always been. What
was wrong was that **my rock colour sat almost exactly where the old one did**.
A correctly-placed band drawn in the same grey as the wash it replaced is not a
band. The reference does not show a range because the rock is grey; it shows it
because pale scree and benches sit against near-black shadowed cliffs, and it is
that SPREAD that reads from orbit.

So the round became an appearance problem: ruggedness picks between scree and
cliff, and bare rock takes light harder than anything with a canopy over it (no
foliage to scatter between the faces), widened ONLY inside the band.

**Overshot once, measured, pulled back.** At `0.40+1.22*hs`, weight 0.80, Tibet
rendered as a black-and-white photocopy — image contrast 43.5 → 51.2. And a
neutral grey turned the Tibetan Plateau grey, which it is not: it is warm tan,
because the rock under it is. The bands now supply BRIGHTNESS structure only;
the hue is divided out of the pixel's existing lithology and province colour and
tinted back in, or every range on the planet ends up carved from the same stone.
Final: contrast 43.5 → 46.0 with warmth (R−B) 12.4 → 12.9, i.e. more ridge
definition at the original colour temperature.

**Registered honestly: the Alps and Andes barely moved (3.3% and 4.8%).** Not
because the zonation is wrong there but because in this model their terrain
rarely clears the new treeline — at 46°N the treeline lands at ~1,745 m, within
50 m of the old fixed 1,700, so the Alps were always going to be a null result.
The Andes case is different and worth a later round: their treeline correctly
ROSE to ~2,960 m, which should have un-greyed a kilometre of slope, and it moved
almost nothing. That points at the elevation field, not the shader — the ranges
themselves may be too low once smoothed to 10 km.

## Q — ITERATION 41, 2026-08-02: the treeline finished, and iteration 40's
## closing hypothesis was wrong

**CORRECTION TO ITERATION 40.** That entry closed by suspecting the elevation
field — that narrow ranges might be too low once smoothed to 10 km, which would
make alpine zonation, snow and the ELA all under-trigger. **Measured, and it is
not true.** The shipped field against real hypsometry:

| range | model p50 / max | reality |
|---|---|---|
| Andes 30-35 S | 2,731 / 5,170 | crest 4,000-6,000 |
| Alps | 1,409 / 3,349 | mean ~1,500 |
| Himalaya | 4,583 / 6,679 | crest >6,000 |
| Tibet | 4,872 / 5,687 | plateau 4,500-5,000 |

The elevation is right. What was wrong was **the metric**: "4.8% of pixels
changed" was measured over the whole frame, and in that framing the Andes
cordillera is about a tenth of it. Restricted to the strip, the same change is
11.9%. A percentage is meaningless without saying what the denominator is, and
that one bought a false hypothesis into the register.

**The real reason the Andes did not move: aridity.** A treeline is only an
isotherm where there is water to grow a tree. In a hyperarid cordillera there is
no forest at ANY altitude and the range reads as bare rock and salt however warm
its lower slopes are. The depression term was 300 m; at 32 S the temperature
treeline lands at ~2,960 m against an Andean median of 2,731, so the model drew
most of the visible cordillera as arid scrub. Raised to 1,350 m. Alps 29.6 ->
30.7, Himalaya 43.5 -> 46.2 image contrast.

**AND IT BROKE SIBERIA, in a way only a screenshot could show.** The line was
`clamp(...)` FIRST and `-= aridity` SECOND. Where ground is both cold and dry —
central Siberia is both — the treeline floored at 600 m, then lost 1,190 m to
aridity, and went NEGATIVE: every pixel from the Yenisei to the Pacific stood
above its own treeline and the taiga rendered as bare tan. Order of operations.
Two fixes: clamp AFTER the subtraction, and gate bare rock on RELIEF, because
above a treeline a flat surface is tundra or till plain and it is vegetated —
what strips ground to stone is broken ground. Tibet survives the gate through a
high-ground exception, since a plateau at 4,800 m is bare however smooth.

Verified against the pre-G7 commit rather than assumed: central Siberia's
greenness (G-R) baseline -10.9, with the bug -12.3, after the fix -11.0. **Back
to baseline exactly** — and that comparison also settled that Siberia's brown
cast is PRE-EXISTING, not something these two rounds introduced. It belongs with
the open note from iteration 39 that the Congo does not read as a solid dark
carpet: the wet-forest palette is not dark or green enough, which is now the
clearest remaining land-colour gap.

## Q — ITERATION 42, 2026-08-02: the palette is written in a space nobody was
## reading it in — a measurement round, NOTHING SHIPPED

Went after the wet-forest gap (Congo and taiga too pale). Four changes were
tried, measured, and **all four reverted**. The round's product is the
measurement, and it is worth more than the changes would have been.

**1. The stops were never the problem.** Equatorial rain forest was already
(0.075,0.235,0.098) — on paper (19,60,25), nearly as dark as the ocean beside
it, exactly as the reference demands.

**2. THE CONSTANTS ARE LINEAR AND THE RENDERER sRGB-ENCODES THEM.** Forcing that
darkest stop over all land and measuring the actual frame: it arrives on screen
as **(68,94,62)**, not (19,60,25). A dark linear value comes out of the sRGB
transfer far lighter than it reads in source. **Every palette judgement made by
looking at these numbers rather than at measured output has been working in the
wrong space**, which is why round after round of "make the forest darker" moved
the render so little. Any future palette work must set constants by measuring
the frame and inverting the transfer, never by reading the source.

**3. And in that space, a bright colour swamps a dark one.** The mid stop at
equatorial warmth is savanna tan (0.678,0.594,0.345) against rain forest
(0.029,0.089,0.037) — twenty times brighter in red. At 79% wet the remaining
fifth of tan still supplied 0.142 of the 0.165 red in the result. "Mostly
forest" renders as khaki. A closed canopy has to arrive closed.

**4. But none of that is the binding constraint.** Rendering the humidity index
itself as greyscale and inverting the transfer gives, over the Congo frame: p25
0.120, **p50 0.184**, p95 0.723. Forest needs h ≈ 0.5. So the basin is mostly
being drawn out of the DRY-to-MID branch, and the picture agrees — the Congo is
a thin mottled ribbon in a field of pale khaki where the reference shows a solid
dark block. **The forest problem is extent and density, not colour**, and it
lives upstream in the index, one level below where this round was digging.

Measured effect of the reverted changes, for the record: Congo (112,122,83) ->
(101,108,75) against a target near (32,58,30), and the Amazon's green-over-red
went the WRONG way, +0.9 -> -3.7, because darkening the wet stop lowered green
while the untouched tan kept supplying red. Not shippable, so not shipped.

Next: the mottling is worth suspecting first. The `edge = 4h(1-h)` jitter added
to break the straight biome bands peaks exactly at h = 0.5, and much of the
basin sits near that value — so the very term that fixed the bands may be what
is dissolving the canopy.

## Q — ITERATION 43, 2026-08-02: a wet interior recycles — and a correction to
## iteration 42's headline number

**CORRECTION FIRST. Iteration 42 reported the Congo's humidity index at a median
of 0.184 against a forest requirement of ~0.5, and concluded the basin was being
drawn from the dry branch. That number was wrong.** The greyscale probe writes
`col = vec3(h)`, and everything written to `col` is then MULTIPLIED BY SHADE
before it reaches the frame — so the probe was reading `h × shade`, not `h`. Over
this frame shade is about 0.39, which is most of the apparent shortfall.

The fix is to write a KNOWN CONSTANT into a spare channel and divide by it:
`col = vec3(h0*0.9, h*0.9, 0.9)`, then `h = G/B` per pixel. With shade divided
out, the true figures are **Congo median 0.64 (68% of pixels above the forest
threshold), Amazon median 0.47 (48%)** — not a basin drawn from the dry branch
at all. A probe that goes through the same pipeline as the picture inherits the
pipeline's transforms; carry a reference through with it.

**The named suspect was innocent.** Iteration 42 pointed at the `edge = 4h(1-h)`
boundary jitter as the thing dissolving the canopy. Measured either side of it,
the jitter RAISES the Congo's index (h0 median 0.48 -> h 0.64). It is not the
problem. Recorded so the suspicion is not inherited by a later round.

**What was real: the two wettest continental interiors on Earth were each being
docked 12% for being continental.** Probed in the render, the Amazon and Congo
both come out at continentality ~1.0, so both took the full `mix(1.10,0.88)`
penalty. That term is right for central Asia and backwards here: what waters the
far side of the Amazon is the near side's evapotranspiration, which is why the
basin is still rainforest three thousand kilometres from the Atlantic. The
penalty now fades out with local rainfall, the best available proxy for whether
there is anything to recycle. Dry interiors keep it in full.

Measured: forest fraction Congo 68% -> 74%, Amazon 48% -> 51%; rendered colour
Congo (97,112,73) -> (86,105,68) with green-over-red +15.0 -> +19.1, Amazon
+3.7 -> +5.8. Central Asian steppe control unmoved. Small, but measured, in the
right direction, and physically the correct statement.

**Still open, and now clearly a FIELD problem rather than a shader one:** the
Amazon's rainfall comes out at 0.194, the same as the Congo's 0.193, when the
Amazon is in reality the wetter of the two (roughly 2,000-3,000 mm against
1,600). Until the field says so, no amount of shader work will make that basin
read as the solid dark block the reference shows. That is the next round, and it
belongs with the G5 climate solve.

## Q — ITERATION 44, 2026-08-02: rain that falls twice

Iteration 43 handed over a field problem: the model gave the Amazon a rainfall of
0.194 against the Congo's 0.193 when the Amazon is in reality the wetter of the
two. Measuring the basin west-to-east showed something worse than parity — a
**backwards gradient**: 0.706 at the mouth, 0.287 in the centre, **0.141 under
the Andes**, when the Andean foreland is the wettest part of the whole basin.

The cause is the same one iteration 43 found in the shader, one level down.
`_advect` decayed its recycling floor with raw distance from open water, so
crossing three thousand kilometres of rainforest cost the same as crossing three
thousand kilometres of sand. It does not: roughly a third of the Amazon's rain
is water that already fell in the basin.

Two changes, both to how recycling is modelled:

1. **Wet land rewinds the clock.** The recycling distance now advances more
   slowly where rain is already falling, so the floor stays high across a wet
   basin and collapses normally across a dry one.
2. **And wet land raises what the air decays TOWARD**, not merely how fast it
   gets there — evapotranspiration over closed canopy returns a large fraction
   of what fell.

Both read the PREVIOUS pass's rainfall, so this is a two-pass fixed-point
iteration rather than a circular definition. One iteration is enough: it moves
the Amazon and leaves the deserts alone.

| | before | after |
|---|---|---|
| Amazon west (Andes) | 0.141 | **0.305** |
| Amazon centre | 0.287 | 0.416 |
| Congo | 0.193 | 0.258 |
| Sahara | 0.004 | 0.007 |
| Atacama | 0.003 | 0.004 |
| Rub al Khali | 0.107 | 0.117 |

**The eighteen-biome check holds at severity 3, 15/18 exact — the iteration 39
baseline — and C SIBERIA NOW READS TREE (0.428).** That was the taiga miss
iterations 41 and 43 kept running into, and it fell out of this without being
targeted. Kazakh steppe crossed the other way (0.387 against a 0.32 threshold);
raising the bar for what counts as recycling was tried at 0.35 and 0.45 and cost
the Amazon and Siberia without recovering Kazakh, so the marginal miss stands.

Rendered, after re-baking all 251 frames plus surface and lakes: Congo
(97,112,73) -> **(61,91,56)** with green-over-red +15.0 -> **+29.9**; Amazon
(120,123,82) -> **(84,106,72)**, +3.7 -> **+22.3**. The basin that was a khaki
wash with a green wisp is now the solid dark block the reference shows.

**One artefact, logged not fixed.** The western Amazon's new forest has a
dead-straight horizontal edge top and bottom. Smoothing the recycling seed
across latitude was the obvious suspect and was measured: row-banding 0.0464 ->
0.0423, real but negligible, and not worth re-baking 251 frames. So the straight
edge has a different cause — a threshold applied to a field whose gradient is
mostly latitudinal draws a latitude line, which is the shader's jitter to fix,
not the climate solve's. The source was left matching the baked fields exactly
rather than carrying an improvement the artefact on disk does not have.

## Q — ITERATION 45, 2026-08-02: two hypotheses about one straight edge, both
## wrong — NOTHING SHIPPED

The western Amazon's new forest block has a dead-straight horizontal edge. Two
candidate causes were implemented, measured against a metric, and both reverted.

**The metric.** A straight horizontal boundary concentrates vertical-gradient
energy into a few rows, so the peakiness of the per-row edge profile measures it
directly: max/mean of `|dI/dy|` averaged along rows. Pre-iteration-44 5.56,
after 44 **7.38** — confirming the edge is a regression from making the canopy
solid, not something that was always there.

**Hypothesis 1: the rainfall sample's domain warp is too low in frequency.**
Genuinely true as a description — `rainAt` warps at `fbm3(wd*1.7)`, a wavelength
of most of the globe, and a warp that low in frequency TRANSLATES a contour
without bending it. Two shorter octaves were added. Peakiness 7.38 -> **7.38**,
identical to two decimals. Reverted: four extra noise taps per pixel for nothing.

**Hypothesis 2: it is the river corridor, not a biome contour.** Rendering
`drain` and `trunk` directly showed a broad east-west band along the Amazon main
stem exactly where the edge is, and `smoothstep(0.25,0.62,drain)` is a steep cut
across a 10 km field -- the coarse-field-under-a-steep-threshold pattern this
project already has a rule about. Frayed both inputs before thresholding, and
carried the frayed trunk through to the corridor PAINT as well so the two agree.
Peakiness 7.38 -> **7.42**. Reverted.

**Where the evidence actually points, for whoever takes this next.** Reading the
render at the peak row, `drain` halves between adjacent screen rows (0.411 ->
0.202) -- but the BAKED `_d` field over the same box has its largest row-to-row
jump at 0.0385, a 15% gradual rise at lat -1.58, not a cliff. So the single-row
screen reading was noise amplified by dividing through a shade reference, and it
should not be trusted as evidence of a step. **The cause is still unlocated.**
Next attempt should segment the forest mask and measure the boundary's own
geometry rather than image-gradient proxies, and should check the ITCZ band edge
in `_rainfall` (`_band(absl, ...)`) as a third candidate.

**One near-miss worth recording.** The comments written for hypothesis 2 quoted
GLSL in backticks -- and FRAG is a JavaScript template literal, so a backtick
inside it closes the shader. `check_shader.py` caught it as an unclosed block
comment and a 47/45 brace imbalance. It would have shipped a blank globe. Never
put a backtick in a FRAG comment.

## Q — ITERATION 46, 2026-08-02: G6 desert structure, and a defect that was not
## there

**FIRST, A RETRACTION.** Iterations 44 and 45 chased a "dead-straight horizontal
edge" on the western Amazon's forest. This round measured it properly — segment
the forest mask, follow its southern boundary column by column — and **the
boundary is not straight**. Its excursion is 17.3 px standard deviation over 300
columns; it wanders. What actually changed when iteration 44 made the canopy
solid is that the boundary lost its RAGGEDNESS: mean step from one column to the
next fell from 3.17 px to 1.28 px. A smooth wandering edge, not a latitude line.

Adding two finer octaves to the boundary jitter moved that from 1.28 to 1.37 and
was reverted with the rest. Three rounds of image-gradient proxies pointed at a
defect whose own geometry, once measured directly, was a much smaller thing than
the screenshot suggested. **Measure the feature, not a proxy for it** — and when
two independent fixes both fail to move a metric, suspect the diagnosis before
reaching for a third fix.

**THEN G6, WHICH SHIPPED.** The Sahara's interior measured a HUE standard
deviation of 3.2: its brightness varied, its colour did not, which is what made
it read as an airbrushed sheet against a reference showing cream sand sheets,
orange dune fields and dark stony massifs.

The first gate sorted these by the substrate-hardness channel, and that failed
for a reason worth recording: **hardness is nearly uniform**. Measured on the
shipped `_d` field, its median is 0.55 in the Sahara, 0.53 in the Rub al Khali,
0.57 in the Taklamakan and 0.48 in the Amazon, with the whole Saharan p10-p90
spanning 0.53 to 0.59. A field that constant cannot discriminate anything; the
erg term evaluated to 0.10 everywhere and the render did not move. Re-gated on
RELIEF, which does vary and is also the honest discriminator — sand collects
where the ground is flat and cannot rest where it is broken, which is why the
Grand Erg is a smooth sheet and the Hoggar stands out of it.

Two more corrections on the way: gating on relief alone scattered sand as
speckle, so a low-frequency crust-locked mask now decides WHERE a sand sea is
while relief and drainage decide how far it reaches (an erg is a body the size
of a country, not noise). And that mask did nothing at first because `fbm3`
here is centred on 0.5, not 0 — the `+0.5` put it above its own threshold
everywhere. Caught by the numbers being identical to the digit, twice.

Measured: Sahara saturation 11.7 -> 18.6, 50 km tone spread 30.7 -> 31.8;
Arabia 21.1 -> 22.7. Amazon control byte-identical, so nothing leaked into the
vegetated palette.

**Two gate saves this round.** `check_shader` caught `flat` used as a variable
name — it is a GLSL reserved word — and the render confirmed it: the Amazon
control went (84,106,72) to (27,45,62) because the shader had not compiled at
all. A control region that must not change is worth carrying in every
measurement.

## Q — ITERATION 47, 2026-08-02: G9 carbonate banks — measured, four attempts,
## NOTHING SHIPPED

**The gap is confirmed and quantified.** On the Bahamas frame our shallow water
sits at R/B 0.59, G/B 0.74; the reference's banks are near (110,200,205), R/B
0.54 and **G/B 0.98** — green standing as high as blue. That difference is the
FLOOR: turquoise is carbonate sand reflecting back through clear water, while a
dark clastic or basalt floor returns the column's blue alone. The code has said
so in a comment since the sea-floor round — "bright shallow water needs a bright
floor as well as a shallow one, and that means a carbonate bank" — but nothing
ever acted on it, so every tropical shelf on the planet gets the same pale blue.

Four attempts, each measured:

| attempt | G/B |
|---|---|
| baseline | 0.74 |
| mix a bank colour over the finished water, depth gate -64..-9 m | 0.74 (0.3% of pixels touched) |
| widen the depth window to the tropical shelf, -165..-25 m | 0.75 |
| near-binary bank mask, weight 0.85 | 0.76 |
| apply to `shallow` BEFORE the blend | broke the braces; nothing rendered |

**What the arithmetic says, and it is the finding.** `carb` is a product of three
smoothsteps; soft gates multiply down to an effective 0.1, which is why a 0.72
weight moved the colour by 0.01. And the last attempt is the right shape: the
`shallow` colour is already blended in at up to 0.92 by the existing bottom-
return machinery, so a term added AFTERWARDS competes with it instead of riding
it. Modify `shallow` itself, before `botRet` and `shelfLift` carry it.

Two concessions the next attempt should keep. The depth window has to be the
SHELF and not the bank top -- a real Bahama bank stands in under ten metres and
this bathymetry is a 10 km grid that never gets that shallow over any area, so a
-64 m gate fired on 0.3% of the frame. And the bank mask should be near-binary:
a carbonate platform either is one or is not, and softening its existence just
dilutes every bank on the planet toward open-ocean blue.

The failed edit removed a block that carried a brace with it; `check_shader`
caught the 27/26 imbalance before anything shipped. Reverted to the deployed
iteration-46 state, which remains live.

## Q — ITERATION 48, 2026-08-02: G9 carbonate banks land, and hit a resolution
## floor

Shipped, small, and worth being precise about how small.

**The placement iteration 47 worked out is the right one.** Modifying `shallow`
BEFORE the bottom-return blend, rather than mixing over the finished water,
finally makes the term do something: on the pixels it touches, R/B 0.61 -> 0.59
and G/B 0.78 -> 0.81, against a reference at 0.54 and 0.98. The Scotia polar
control sits at 0.65 before and after, so nothing leaked out of the tropics.

**Two corrections along the way.** The near-binary bank mask, added in 47 to
stop three soft gates multiplying to nothing, turned out to trade dilution for a
COVERAGE LOTTERY: at a 78-degree wavelength the Bahamas either fall inside a
blob or they do not, by the phase of the noise, and they did not — 0.68% of the
frame changed. Removed; warm shallow shelves are carbonate-dominated anyway,
except where a big river buries them, so latitude and depth carry it alone. And
the first target colour (0.325,0.755,0.740) rendered the banks white-blue: too
much red for turquoise, against a reference whose red is barely half its blue.

**AND THE HONEST LIMIT.** The turquoise cannot get much further, and the reason
is the field rather than the palette. Measured on the shipped elevation:

| box | water | of that, above -165 m | above -64 m | median depth |
|---|---|---|---|---|
| Bahamas/Florida | 77% | 14.3% | 9.1% | -1,984 m |
| Caribbean | 87% | 5.6% | 4.0% | -3,768 m |
| Great Barrier Reef | 70% | 10.6% | 8.8% | -1,255 m |
| Persian Gulf | 26% | 99.9% | 94.8% | -44 m |

The bottom-return term is `exp(z/70)`, so `shallow` — and therefore any floor
colour riding it — only matters above roughly -70 m. In the Bahamas box that is
9% of the water. The Persian Gulf, which the field DOES resolve, is the case to
look at to see the feature working properly. Closing the rest would need either
finer bathymetry or a wider shallow band, and the latter is exactly what the G2
comments warn against ("smoothstep from 850 m put pale shelf colour on anything
that was not abyss") — so it is a data limit, not a tuning one, and should not
be papered over by widening the band.

**Recorded twice now, so it goes in the file: NEVER PUT A BACKTICK IN A FRAG
COMMENT.** I wrote `shallow` in backticks in the very comment explaining this
feature, which closed the shader's template literal — the FRAG extraction fell
from 213,486 characters to 37,306. Iteration 45 hit the identical trap and
recorded it, and I repeated it one round later. `check_shader` caught it both
times, which is the only reason neither shipped.

## Q — ITERATION 49, 2026-08-02: three user reports — a regression I shipped, an
## artefact I shipped, and a log that stopped

**1. THE GREAT LAKES, ERASED BY MY OWN REBUILD CHAIN.** Present-day lakes do not
come from the water-balance solver at all: they are REAL OUTLINES stamped by a
SEPARATE script, `bake_present_lakes.py`. My field-rebuild chain ran
`bake_lakes.py` and stopped, so the solver's own guess overwrote the outlines
every time. Measured: Great Lakes depth cells fell from 4,385 to 23, and Baikal,
Victoria, Titicaca and Chad went to exactly zero. It shipped for nine commits.

Two things hid it. The chain ran `bake_lakes.py >/dev/null 2>&1`, so nothing it
said was visible; and my first check read the field with `convert("L")` when it
is RGB (R = depth, G = a dry-basin mask), which made a working field look empty
and nearly sent me diagnosing the wrong thing. `bake_present_lakes.py` is now a
permanent step in the chain script, after `bake_lakes.py`, with a comment saying
why. Restored: 1,117 real lakes, Great Lakes back to 4,385 cells.

**2. THE MAGENTA BLOBS WERE MINE, FROM ITERATION 48.** Saturated (250,128,254)
patches in shallow water in valleys and rift lakes — 181 pixels on one 35 Ma
frame. Bisected by flattening the colour at successive stages: land colour, the
tundra blend, the desert block and the ice block were all ruled OUT, and the
user's own guess (water shading) was right. Disabling the G9 carbonate mix takes
the count from 181 to 0.

**The mechanism is still unexplained, and that is recorded rather than glossed.**
Every operation in the chain looks bounded — `carb` is a product of two ramps
clamped to [0,1], the mix factor is clamped, and the only consumer is one more
clamped mix. Rewriting both gates as explicit clamped linear ramps, on the
theory that `smoothstep(33,25,x)` with edge0 > edge1 is undefined in the GLSL
spec, did NOT fix it. So the feature is REVERTED: it bought G/B 0.78 -> 0.81 on
the Bahamas against a 0.98 target, and a marginal colour gain is not worth a
visible artefact. It can come back when the cause is understood.

Note for whoever picks this up: a bisect that flattens `col` inside `if(z>=wl)`
tests LAND ONLY. Two of my bisect steps were inside that branch and "proved" the
artefact was downstream when it was simply on the other side of the branch.

**3. The update log had stopped at 1.9 (28 July).** Everything since — the
climate fix, alpine zonation, desert structure, the label and card work, the
future-terrain round — was unlogged. Added release 2.0 covering it in the
reader's language, and the log is part of the round from here.

Still open from this round: the sea floor reads as generic and pixelated at
close zoom (user report), which is the next round.

## Q — ITERATION 50, 2026-08-03: the floor a volcano vacates

User report: the sea floor still reads generic, flat and pixelated. The frame
answered it before any code did. At Hawaii, zoom 1.15, the abyssal fabric is
present in the CORNERS and absent in a smooth blue blank several hundred
kilometres across centred on the island chain.

**The blank is deliberate, and half-right.** `flatw` switches the abyssal-hill
fabric off wherever the ground has slope or prominence, so spreading fabric does
not get combed across a guyot or a plateau. That gate is correct. What was wrong
is that **nothing replaced it** — the machinery vacates the region and leaves
bare palette behind.

A real volcanic apron is not smooth. Hawaii's flanks are buried in giant
landslide debris: the Nuuanu and Wailau fields are hundreds of blocks, some
kilometres across, over rubble and flow lobes. So the vacated region now gets a
hummocky grain, isotropic rather than lineated — debris has no grain direction,
which is exactly what separates it from the combed crust around it.

**Two measured corrections.** The first version gated on prominence AND `deepw`,
and barely moved the blank: `deepw` fades everything out above about 2,400 m,
and the Hawaiian swell the islands sit on is shallower than that, so the same
depth gate that silenced the fabric silenced its replacement. Re-keyed to
`1 - flatw` exactly, so the hand-over is exact by construction, with only a
shelf-depth guard.

Then a probe (R = deepw, G = flatw, B = reference) showed both gates FULLY OPEN
across the pale zone that still read flat — 0.86 and 0.03. The texture was being
applied and could not be seen: shallow water is drawn pale and nearly face-on, so
a perturbed normal barely changes its shade. The fix was to put most of the
apron's strength into the TONE term, which does not depend on the lighting angle.

Measured detail energy over water, before -> after: Scotia arc 1 px 2.05 ->
3.05 (+49%), 4 px +30%; Hawaii close 1 px 0.88 -> 1.01 (+15%) at every scale.
Land control byte-comparable (0.26 mean absolute difference, coastline
antialiasing only).

Still open: the broad shallow swells remain the flattest water on the map. Both
gates are open there, so it is a palette-contrast question rather than a missing
texture, and it belongs with whatever revisits the shallow-water ramp.
