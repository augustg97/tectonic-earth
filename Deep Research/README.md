# Deep Research — a deep-time Earth-systems knowledge base for Tectonic Earth

**Started 2026-07-26.** A standing research programme and expert system covering plate
tectonics, oceanic and continental crust, palaeoclimate, atmosphere and ocean chemistry,
ecosystems and palaeobiology across deep time.

**This folder does not change the Tectonic Earth model.** Nothing here is imported by
`build/`. Its output is *evidence and models* that inform continuous updates to the app —
so that when a number, a coastline, a label or a card changes, the change has a citation
and a mechanism behind it rather than a guess.

---

## How it is organised

```
Deep Research/
├── research/                     evidence: dossiers per domain, with sources and caution flags
│   ├── 01-plate-tectonics/
│   ├── 02-continental-crust/
│   ├── 03-oceanic-crust/
│   ├── 04-paleoclimate/
│   ├── 05-atmosphere-ocean-chemistry/
│   ├── 06-paleobiology/
│   ├── 07-ecosystems-biomes/
│   ├── 08-timescale-and-methods/
│   └── 09-source-documents/      fetched primary/secondary material kept verbatim
├── diagrams and illustrations/
│   ├── authored/                 SVGs GENERATED from the models, so they cannot drift
│   ├── collected/                third-party figures + MANIFEST.json (licence + review)
│   ├── make_diagrams.py
│   └── fetch_reference_figures.py
├── research reports/             illustrated white papers, each ending in actions
├── modeling/                     runnable models of planetary systems across deep time
└── MODEL-GAPS.md                 the register that ties research to app defects
```

---

## The models (all runnable, all self-testing)

Run any of them directly — each has a `_selftest()` and prints a worked demonstration.

```bash
cd "Deep Research/modeling" && ../../venv/bin/python deeptime.py
```

| module | what it is | current state |
|---|---|---|
| [`deeptime.py`](modeling/deeptime.py) | ICS v2024/12 chronology to stage level, plus catalogues of glaciations, extinctions, anoxic events, hyperthermals, carbon drawdowns and LIPs, with confidence on every entry | **101 stages**, 34 epochs, 22 periods, 54 events · selftest passes |
| [`paleogeography.py`](modeling/paleogeography.py) | continental blocks: present-day anchors, existence windows, assembly membership, orogenies, terrane rift/accretion events | 56 blocks, 6 assemblies, 35 orogenies, 31 terrane events · selftest passes |
| [`paleobiogeography.py`](modeling/paleobiogeography.py) | province model — `province(age, lat, realm, block)` and `provinciality(age)` | **49 distinct provinces over 0–1000 Ma**; 9 marine + 5 terrestrial schemes; no cell unnamed · selftest passes |
| [`climate_ebm.py`](modeling/climate_ebm.py) | 1-D diffusive energy-balance climate model with ice-albedo feedback and the snowball bifurcation | present-day 13.4 °C, ice line 71.8° · **known to understate hothouses, see its docstring** |
| [`biome_model.py`](modeling/biome_model.py) | Whittaker climate zone **×** vegetation era → what actually grew there at that age | 14 zones × 8 eras · selftest passes |
| [`taxa_db.py`](modeling/taxa_db.py) | taxa with **attributes**: size, habit, diet, realm, age range, provinces | 105 seed taxa; emits `taxa.json` · selftest passes |
| [`hotspots.py`](modeling/hotspots.py) | 53 hotspots with coordinates, chains, LIP roots, flux and confidence; all 15 named aseismic ridges mapped to their plume; the guyot subsidence law | selftest passes |
| [`lagerstatten.py`](modeling/lagerstatten.py) | 30 Lagerstätten as point features: present-day coordinates, block for the plate track, window, setting, significance | selftest passes |
| [`ocean_circulation.py`](modeling/ocean_circulation.py) | wind-driven surface circulation from a land/sea mask: Sverdrup gyres, western boundary currents, eastern-boundary upwelling, and the circumpolar-current test | present-day validated; **closing Drake switches the ACC off** |

### Audits (read-only; they change nothing)

| script | catches | current result |
|---|---|---|
| [`audit_cards.py`](modeling/audit_cards.py) | coverage, dates, unhedged contested claims, anachronisms, superseded claims, misattribution | 667 cards, **0 HIGH** |
| [`audit_label_windows.py`](modeling/audit_label_windows.py) | a label drawn when the entity it names did not exist | 46 matched, **2 findings** |
| [`audit_curated_biota.py`](modeling/audit_curated_biota.py) | curated biota vs the province model — the B1 exception/typical split | 197 spans, **9 exceptions, 188 placed, 0 unplaced** |
| [`climate_audit.py`](modeling/climate_audit.py) | `climate.py` against PhanDA and GEOCARBSULF | **6 findings** |
| [`frame_experiment.py`](modeling/frame_experiment.py) | reconstruction frame quality, measured on a population | **the A1 result** |

The models are deliberately dependency-light (stdlib only, except numpy for the EBM) so
that `build/` can import any of them later without adding a dependency.

---

## The research dossiers

| file | covers |
|---|---|
| [`01-plate-tectonics/01-supercontinent-cycle.md`](research/01-plate-tectonics/01-supercontinent-cycle.md) | the gather–disperse cycle; Rodinia, Pannotia, Gondwana, Pangaea; assembly orogenies; terrane inventory; the consequences the app already draws |
| [`01-plate-tectonics/02-reconstruction-methods-and-reference-frames.md`](research/01-plate-tectonics/02-reconstruction-methods-and-reference-frames.md) | Euler rotations, plate circuits, the data types and their reach, **the longitude problem**, true polar wander, and what a real fix to our label error looks like |
| [`03-oceanic-crust/01-ocean-basins-crust-lips-and-plumes.md`](research/03-oceanic-crust/01-ocean-basins-crust-lips-and-plumes.md) | crustal structure and depth–age law, LIP inventory with volumes, oceanic anoxic events, hotspot chains — and the catalogue that would fix our scattered seamounts |
| [`04-paleoclimate/01-phanerozoic-climate-record.md`](research/04-paleoclimate/01-phanerozoic-climate-record.md) | **PhanDA** (Judd et al. 2024) as the new GMST standard, CO₂ history, named climate events, sea level, and what each proxy can and cannot say |
| [`05-atmosphere-ocean-chemistry/01-atmosphere-oxygen-and-ocean-chemistry.md`](research/05-atmosphere-ocean-chemistry/01-atmosphere-oxygen-and-ocean-chemistry.md) | GOE, the boring billion, the Neoproterozoic Oxygenation Event, Phanerozoic O₂, ocean redox, calcite/aragonite seas, circulation and gateways |
| [`06-paleobiology/01-biogeographic-provinces-through-time.md`](research/06-paleobiology/01-biogeographic-provinces-through-time.md) | marine and terrestrial provinces interval by interval, the Permian four-province world, Glossopteris in detail, the Great American Interchange |
| [`02-continental-crust/01-cratons-and-continental-growth.md`](research/02-continental-crust/01-cratons-and-continental-growth.md) | why continents are permanent and ocean floor is not, craton/orogen/terrane anatomy, Laurentia worked through, the four orogen types |
| [`07-ecosystems-biomes/01-biome-evolution-and-ecosystem-structure.md`](research/07-ecosystems-biomes/01-biome-evolution-and-ecosystem-structure.md) | the climate-cell vs occupancy split, the eight vegetation eras, four biomes with **no modern analogue**, reef and substrate turnovers |
| [`08-timescale-and-methods/01-timescale-dating-and-uncertainty.md`](research/08-timescale-and-methods/01-timescale-dating-and-uncertainty.md) | GSSP vs chronometric units, what each dating method can deliver, and a list of things the app currently states flatly that the literature does not settle |

## The white papers

| paper | thesis |
|---|---|
| [`WP-01 · Where the continents were, and why our labels miss`](research%20reports/WP-01-where-the-continents-were.md) | the label error has **three** causes and only one is addressed; three ranked remediations, the cheapest of which is brand new |
| [`WP-02 · The biosphere through deep time`](research%20reports/WP-02-the-biosphere-through-deep-time.md) | replace per-label curation with a province model, a vegetation model and an attribute-carrying taxon database; five concrete app changes |
| [`WP-03 · The climate system across deep time`](research%20reports/WP-03-the-climate-system.md) | our climate table predates PhanDA; what to re-check, what to add, and what the app should stop claiming |
| [`WP-04 · Closing the gaps: four measured results`](research%20reports/WP-04-closing-the-gaps.md) | **Scotese publishes his own rotations** and using them cuts placement error fourfold; the Cretaceous is 6 °C too cool; one hotspot catalogue closes four register items |

## Handoff prompts

| file | for |
|---|---|
| [`HANDOFF-IMPLEMENTATION.md`](HANDOFF-IMPLEMENTATION.md) | **the session that finally changes the app.** Tiered by measured value, with the traps that have each cost real time. |
| [`HANDOFF-A5-F1-reference-map-audit.md`](HANDOFF-A5-F1-reference-map-audit.md) | auditing our reconstruction against the DeepTimeMaps and Scotese series — runs in parallel, touches nothing else. |

## Staged for the build

**[`STAGED-CHANGES.md`](research%20reports/STAGED-CHANGES.md)** is the handover surface:
every gap item that would touch `build/` or `web/`, with the artifact that makes it a
drop-in, ordered by measured value. Nothing in this folder has been applied to the app.

Top of that list: **switch feature tracks to the PALEOMAP rotation model** — measured to
cut abyssal-plain placement errors from 20% to 5%.

## The card audit

| document | what it is |
|---|---|
| [`CARD-AUDIT-register.md`](research%20reports/CARD-AUDIT-register.md) | generated by [`modeling/audit_cards.py`](modeling/audit_cards.py) over **667 cards / 214,000 characters** of user-visible text. Six check families: coverage, dates, contested claims, anachronistic vocabulary, superseded claims, misattribution. Re-run it after any card edit. |
| [`CARD-DRAFTS-round-1.md`](research%20reports/CARD-DRAFTS-round-1.md) | ready-to-paste replacement text for every finding, plus the cards the resource review argued for. **Nothing applied to the model** — a review draft. |

**Zero HIGH findings.** Two of the three date disagreements the first run reported turned
out to be errors in *this folder's* catalogue, not the app's, and `deeptime.py` was
corrected to match.

## The figures

Authored, generated from the models by `make_diagrams.py`:

1. `01-deep-time-master-chart.svg` — supercontinents, glaciations, extinctions, LIPs, anoxic events, hyperthermals and vegetation on one 1250-Myr axis
2. `02-vegetation-through-time.svg` — Whittaker zones × vegetation eras; fill opacity is canopy height, so the greening of the land is visible as a gradient
3. `03-the-longitude-problem.svg` — why palaeomagnetism cannot place a continent in longitude, and what that costs us
4. `04-lip-to-extinction-cascade.svg` — the fixed mechanistic order from eruption to extinction, with the seven instances
5. `05-continental-affiliation.svg` — which block belonged to what, when, with disputed memberships dashed
6. `06-snowball-bifurcation.svg` — GMST against CO₂ at 700 Ma from the EBM, showing the hysteresis

The pooled index across all three tiers — authored, collected and the copyrighted
reference material in `Deep Time Maps and Resources/` — is
[`REFERENCE-LIBRARY.md`](diagrams%20and%20illustrations/REFERENCE-LIBRARY.md).

Collected third-party figures live in `collected/` with a `MANIFEST.json` recording
licence, source, author **and a visual review verdict**. Licence policy matches the rest
of the project: **public domain / CC0 / PDM / plain CC-BY only; share-alike and
non-commercial refused.** Of the first eight fetched, one was an entirely wrong subject
and three were mislabelled — correct licence never implies correct subject.

---

## Working method

1. **Verify, don't reconstruct from memory.** Every claim in a dossier is traceable to a
   named source, and where a fetched source is internally inconsistent the dossier says so
   rather than propagating it (see the caution flag on Wikipedia's *List of orogenies*).
2. **Say what is contested.** Pannotia's existence, the Rodinia configuration, Early
   Cretaceous ice, the endemism story after the Carboniferous rainforest collapse, the
   Hawaii–Emperor bend, the Panama closure date. A card that states these flatly
   misrepresents how well they are known.
3. **Prefer a model to a table.** Every research finding that could be a hand-written row
   is instead written as a function with a selftest, so a new age produces a defensible
   answer without new authoring.
4. **Figures are generated, not drawn.** They read from the same modules, so a corrected
   date propagates into the illustration automatically.
5. **Every white paper ends in actions**, and every action lands in `MODEL-GAPS.md`.

---

## Status

**v2, 2026-07-26.** Two rounds in one day.

*Round 1* — 8 research dossiers, 3 white papers, 6 generated figures, 6 runnable models.

*Round 2* — reviewed all 121 files in `Deep Time Maps and Resources/` and resolved its 11
bookmarks; catalogued them with provenance and licence; added a 9th dossier and a resource
catalogue; **audited all 667 cards / 214,000 characters of the app's user-visible text**
and drafted replacement copy for every finding; added 5 figures (11 total) and 4 more
collected ones (11 total, all reviewed); added the Baykonurian glaciation, the Azolla
event and a carbon-drawdown catalogue to `deeptime.py`.

All selftests pass; all 46 internal links resolve. See [`MODEL-GAPS.md`](MODEL-GAPS.md)
for the **50 open items**, 12 at P1.

Next round, in priority order: check for a published PALEOMAP rotation file (A1); the
DeepTimeMaps and Scotese-future audits against our own frames (A5, F1); the climate-events
panel, whose 11 cards are already drafted (F2); the hotspot catalogue and the seamount
wiring (D1–D2); the PhanDA diff (C1).
