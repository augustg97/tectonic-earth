# Staged changes — everything ready to apply to the model

**2026-07-26.** Deep Research does not change the app. This file is the handover: every
gap item that would touch `build/` or `web/`, with the artifact that makes it a drop-in.
Ordered by measured value, not by register number.

Nothing here has been applied. Each row says exactly what to change and what evidence
backs it.

---

## Tier 1 — measured, high value, ready now

### 1. Switch feature tracks to the PALEOMAP rotation model · **A1, retires A3**

**Evidence:** `modeling/frame_experiment.py`, [WP-04 §1](WP-04-closing-the-gaps.md).
Abyssal-plain placement errors **20% → 5%** over 53 land points × 10 ages, better at every
age.

**Artifact:** already downloaded and extracted, gitignored like the other datasets.

```
data/paleomap_gpm/Scotese PaleoAtlas_v3/PALEOMAP Global Plate Model/
    PALEOMAP_PlateModel.rot        CC-BY 4.0, -250 -> 1100 Ma, 258 plate IDs
    PALEOMAP_PlatePolygons.gpml
```

**Change:** in `build/paleo_tracks.py`, point `ROT`/`STATIC` at these files and set
`correct_frame=False` throughout — the correction becomes meaningless and harmful once
both halves of the pipeline share a frame.

**Keep Merdith for boundaries.** `build_plates_gplates.py` needs resolved topologies, which
is a different object; PALEOMAP's polygon set does not replace it. The end state is both
models, each doing what it is good at.

**Then:** rerun `audit_labels.py` and `audit_label_motion.py`, and re-derive
`frame_offset.json` or delete it. **Judge on the population** — every tracked label,
crater, LIP and plateau moves, and any feature that was well placed by the old error will
look like a regression.

### 2. Raise the Cretaceous; the app never reaches hothouse · **C1**

**Evidence:** `modeling/climate_audit.py`. Our Phanerozoic maximum is **30.0 °C at 90 Ma**;
PhanDA's is **36 °C in the Turonian**. Position right, amplitude 6 °C short — and 30 °C is
exactly the hothouse boundary, so no keyframe ever enters that state.

**Change:** `build/climate.py` `SYSTEM`, the 90–100 Ma rows. Downstream: `refresh_manifest.py`
(no re-render needed for the readout), but rainfall and ice DO depend on temperature, so a
field rebuild follows if the change is large.

**Check while there:** 66 → 56 Ma, where CO₂ doubles 810 → 1600 ppm and GMST moves only
+1.5 °C. That interval contains the PETM and runs into the EECO.

### 3. Lower the O₂ peak from 36% to ~30% · **C3, F9**

`climate.py` peaks at **36.0% at 280 Ma**; Krause et al. (2022) puts it near 30%. Timing is
right. Fix the table *and* the Guadalupian card, which says "~30–35%".

### 4. Wire the hotspot catalogue into the sea floor · **D1, D2, D3, D4**

**Artifact:** `modeling/hotspots.py` — 53 hotspots with coordinates, chain, LIP root, start
age, flux, confidence; `ASEISMIC_RIDGES` maps all 15 named ridges to their plume.

**Change:** `seamounts.field()` already takes a `hotspot` argument and ignores it. Seed
along reconstructed plume tracks instead of by crustal age, then apply

```python
summit_depth = (ridge_depth - edifice_height) + 0.350 * sqrt(age_Myr)
```

Islands drown at ~16 Myr, which is the right order for the Hawaiian chain. That single line
delivers islands at the young end, atolls in the middle, **guyots** at the old end, and the
named aseismic ridges — four register items, no new noise function.

### 5. Flood the Triassic–Jurassic epicontinental seas · **G1**

**Evidence:** `modeling/audit_reconstruction.py`, [WP-05 §4](WP-05-reconstruction-audit.md).
At **240 Ma we draw 1.8% of the surface as shallow sea against Blakey's 8.0%, and 93% of
everything he draws as shelf sea is dry land in our field** — 83% at 200 Ma, 77% at 180 Ma.
The measurement is taken only where both models put continental crust, after a rigid
longitude fit, so it is about flooding and not about placement. The present-day control
passes (Δ −0.1 pp, only 19% of his shelf dry in ours), so the method is sound.

**Change:** `build/epeiric.py` already floods the seas a 20 km grid cannot resolve — the
Trans-Saharan Seaway, the Cannonball Sea — and its coverage stops short of the Triassic and
Jurassic. Extend it there: the Germanic Basin / Muschelkalk sea, the Sverdrup and West
Siberian basins, the Tethyan shelf carbonate platforms, the Sundance and Curtis seaways in
western North America.

**Bonus:** this is also the whole of the **+5 to +9 pp land excess** at 150–240 Ma reported
in WP-05 §2. It was never extra continent; it was missing sea. One fix closes both.

### 6. Stop the future series destroying continental area · **G2**

**Evidence:** [WP-05 §6.1](WP-05-reconstruction-audit.md). **148.1 → 92.6 Mkm² over 250 Myr,
a 37% loss.** PALEOMAP's rigid rotations over the same interval lose 5.5%, all of it
rasterisation. Continental crust is conserved on this timescale, so the trend is an artefact.

**Cause**, one line in `build_fields.future_grid`:

```python
out = np.maximum(out, z)          # overlap -> collision keeps the high ground
```

Where two group rotations land on the same ground, one survives and the other's area is
annihilated. The signature confirms it exactly: land above 2 km is flat (8.7 → 8.6 Mkm²)
while land below 1 km falls **45%** (118 → 65 Mkm²), and the mean elevation of what survives
rises 667 → 879 m. `maximum` is a "high ground wins" rule, so it eats plains and spares
mountains — and coastal plain, shelf and continental interior are exactly the ground the
biota, biome and rainfall layers are drawn on.

**Change**, in rough order of effort: pull `GROUP_TARGET` apart so groups meet rather than
interpenetrate (cheapest, and it also fixes G3's over-compact assembly); or allocate
contested ground to a single group before sampling; or add an explicit area-conservation
check to the build so this cannot regress silently. Whatever is chosen, `audit_reconstruction.py
--future` re-measures it in one command.

---

## Tier 2 — card content, all text written

| # | card | change | draft |
|---|---|---|---|
| F2 / C5 | **new "climate events" panel** | a fifth navigable structure beside intervals, supercontinents, glaciations, extinctions. 11 events, all shorter than a keyframe so none can be drawn. | [CARD-DRAFTS §3](CARD-DRAFTS-round-1.md) |
| F5 | Pennsylvanian ×2, Pangaea, LPIA | hedge the giant-arthropod oxygen chain and post-collapse endemism | §1.1–1.3 |
| F5 | Pliocene ×2 | "closed the Isthmus" → "completed a land bridge"; the closure date is debated | §1.4 |
| F7 | Glossopteris Flora | credit **Suess**, who used this evidence in 1885 and named Gondwana | §2.1 |
| F9 | Guadalupian | "~30–35%" → "~30%" | §2.2 |
| F8 | Pangaea Proxima | say it is one of four published futures and why this one | §4.4 |
| F6 | **new** Permian Basin | Wolfcamp → Leonard → Guadalupian → Ochoan Castile | §4.1 |
| F4 | **new** Back-arc basin | slab roll-back; addresses the marginal-basin gap | §4.2 |
| D4 | **new** Atolls and guyots | Darwin's subsidence sequence | §4.3 |
| D6 | LIP cards | link each to its consequence: Ontong Java → OAE 1a, Caribbean → OAE 2, NAIP → PETM, Karoo–Ferrar → T-OAE | `hotspots.py` |
| D7 | plume cards | state that hotspots are **not** fixed; only Yellowstone is imaged deep-to-surface | `hotspots.py` docstring |
| F3 | **new** Baykonurian glaciation | ~547–540 Ma, terminal Ediacaran | `deeptime.GLACIATIONS` |
| C8 | supercontinents | populate `disputed` for Kenorland, Vaalbara, Ur (Pannotia already exemplary) | — |
| B9 | Carboniferous biome text | the rainforest collapse is **Euramerican only**; Cathaysian rainforest persists to the end-Permian | research 06/01 |
| A6 / A7 | About page, README §9 | positions before ~175 Ma are reconstructions; palaeomagnetism never fixes longitude; a small residual is *expected* | WP-01 |

Figures for these already exist in `diagrams and illustrations/authored/`: 04 (LIP cascade),
07 (Cenozoic events), 08 (oxygen), 09 (atoll/guyot), 10 (back-arc), 11 (Glossopteris).

---

## Tier 3 — validators to adopt into the build

Three read-only audits that catch classes of error the pipeline cannot currently see. Each
is re-runnable and takes seconds.

| script | catches | current result |
|---|---|---|
| `modeling/audit_cards.py` | coverage gaps, date drift, unhedged contested claims, anachronistic vocabulary, superseded claims, misattribution | 667 cards, **0 HIGH** |
| `modeling/audit_label_windows.py` | a label drawn when the entity it names did not exist | 46 matched, **2 findings** |
| `modeling/climate_audit.py` | the climate table against PhanDA and GEOCARBSULF | **6 findings** |
| `modeling/frame_experiment.py` | reconstruction frame quality, on a population | the A1 result |

**Recommendation:** run `audit_cards.py` after any card edit and `audit_label_windows.py`
after any `features.LABELS` edit. Both fail loudly and cost nothing.

---

## Tier 1b — B1, now decided

**The decision (2026-07-26): model decides, curated is a flagged exception.**
`paleobiogeography.province()` runs everywhere. A curated list shows only where it is
genuinely distinctive; elsewhere the curated list is *checked against* the model rather
than silently overriding it. Where the model has no province, the card shows the global
interval list **under a heading that says it is global** — never implying those taxa lived
at that spot.

**Why this matters:** 106 of 336 labels have a curated entry, so **230 fall straight
through to one global list for the whole interval**. A Verkhoyansk Belt card at 250 Ma
currently shows "the world's Late Permian biota", not what lived there.

`modeling/audit_curated_biota.py` is the prerequisite that decision creates — it splits
all 198 curated spans into exception / typical / conflict:

| verdict | count | what happens to it |
|---|---|---|
| **EXCEPTION** | **9** | keep and flag; the model must never overwrite it |
| **province-typical** | **67** | the model can own these; curated prose moves to province level |
| **model cannot place** | **121** | falls to the labelled global list — *or the province model gets extended* |
| CONFLICT | 0 | none found |

The nine exceptions are exactly the localities whose whole point is being atypical:
**Solnhofen Lagoon, Zechstein Sea, Muschelkalk Sea, Nama Sea, Messinian Salt Basin,
Paratethys, Lake Pannon, Mid-Atlantic Ridge, East Pacific Rise, Beringian Steppe-Tundra.**

**The headline finding is the 121.** The bottleneck for B1 is *not* the curated data — it
is the **province model's own coverage**, which is thin in deep time and for basins. That
reverses the assumed order of work: extend `paleobiogeography.py` first, then wire it in.
Concretely, the model places 18 spans in the Tethyan Realm, 9 Boreal, 6 Austral, 5
Gondwanan, and nothing at all for most Palaeozoic seas.

**Implementation shape**, once coverage improves:

1. Add an `exception: true` flag to the nine entries in `life_data.json`.
2. `regionTaxaAt` returns `(taxa, is_exception)`.
3. `lifeSection` order becomes: exception-curated → province assemblage → labelled global
   list, with the heading naming which one the reader is looking at.
4. Keep `audit_curated_biota.py` in CI so a new curated entry has to declare itself.

## Tier 4 — modelling work still to do here first

| item | why it is not staged |
|---|---|
| **C6** ocean circulation | the gyre-template model is designed (research 05/01 §3) but not built |
| **B1** province-model coverage | DECIDED and audited (see Tier 1b). The remaining work is **extending the province model**, which now places only 67 of 198 curated spans — coverage, not design, is the bottleneck |
| **B10** grow `taxa_db.py` | 105 taxa; thinnest at mid-Cambrian–Silurian |
| **B7** Lagerstätten as point features | list drafted; coordinates not yet assembled |
| **A5 / F1** reference-map audits | the DeepTimeMaps and Scotese-future comparisons are set up but not run at scale |
| **F10 / F11** figure fetches | four slots still 429; the "English" Glossopteris came back in Dutch |

---

## What changed in this folder while doing the above

Recorded because both were errors in the research, not the app, and the app's own data was
right each time:

1. **`deeptime.py` glaciation dates** were corrected to match the app, which separates the
   late Famennian pulse from the LPIA more cleanly than the common "360–255" convention.
2. **`paleogeography.py` gained `recognisable_until()`.** A naive label audit reported six
   errors because `ASSEMBLIES["top"]` is breakup *onset* — Pangaea rifts from 175 Ma and is
   one continent for another 75 Myr. With the distinction, six findings became two.
3. **Two Cambrian epoch boundaries in `deeptime.py` were wrong** since round 1
   (Terreneuvian / Series 2 / Miaolingian), plus Ludlow's top. Caught by a *strengthened*
   selftest added when the Palaeozoic stages went in — the check that epochs must tile
   their period without gaps.
4. **`fetch_reference_figures.py` clobbered its own manifest**, destroying two rounds of
   hand-entered review verdicts. Restored from git; the fetcher now merges, and a failed
   retry can no longer erase a good earlier result.
