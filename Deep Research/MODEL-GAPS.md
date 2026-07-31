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
