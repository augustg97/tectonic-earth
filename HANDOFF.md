# Handoff — Tectonic Earth, flora and fauna

Paste this whole file as the first message of a new session.

---

## What you are working on

**Tectonic Earth** — interactive deep-time paleogeography app, 1000 Ma → +250 Myr, globe + Mollweide map.

- Repo: `/Users/augustgweon/Tectonic Plate Model` (venv at `./venv/bin/python`; do NOT move it to `~/Desktop`)
- Live: https://augustg97.github.io/tectonic-earth/ (GitHub Pages serves `main:/docs`)
- **Read `README.md` first**: §2 working rules, §5.6 the biota subsystem, §6 the gate and the
  "adding an organism" commands, §7.18–7.23 this work's traps, §9 known limits.
- `build/taxa/SCHEMA.md` is the authoring contract for organisms.

## The current task

The user asked for the feature cards' flora and fauna to be fixed **systematically**: every card
rich, accurate, diverse, with the right icon, the right organisms for that place and time, and a
tracking system so it cannot decay. The system shipped in 3.6; 3.7 and 3.8 (2026-09-22) added depth — 226 taxa for the seas,
Palaeozoic land and the Precambrian — read the placement listing at twenty ages, re-anchored
eight mislaid labels, hand-drew the last forms, closed the five 404s, and rewrote the
class-level curated lists. The user's instruction was "keep going until completion" and then
"keep going with the remaining placement ages and the Mesozoic seas, and any other remaining
items": those are done. What is left is in the work queue below, and all of it is depth. There
is no open loop; every round ends deployed and verified live.

## How the system works, in one paragraph

Every organism is declared once in `build/taxa/*.json` (form → drawing; `fad`/`lad`; `range` in
present-day crust codes with time slices; `hab`, `lat`, `box`, `avoid`). `biota.compose()` builds
each label's card per whole-Myr age: curated list (`life_data.json`, authority over place, none
over time) → province markers → registry fill, filtered by lifetime, crust, habitat, latitude and
the taxon's own range within the region, balanced into Fauna / Flora / other. Label-side setting
is dated: `SUBMERGED`, time-sliced `LABEL_HOME`, `HABITAT_SINCE`, the polar rule. It ships as
`cards` in `web/life.json`. `audit_biota.py` replays all 38,036 card-ages from the shipped file.

## The measurement harness — reuse it

```bash
cd build
../venv/bin/python biota.py --check                    # registry: schema, form, range vs PBDB
../venv/bin/python biota.py --card "Lake Titicaca" 0 3 # compose one label, no rebuild
../venv/bin/python -c "import build_webdata as b; b.build_life()"   # rebuild web/life.json (~2 min)
../venv/bin/python audit_biota.py -v                   # the gate, with detail
../venv/bin/python audit_all.py --quick                # everything against baselines
../venv/bin/python verify_cards.py tag "Alps@0" "Antarctica@20"     # -> build/verify/cards_tag.png
../venv/bin/python verify_icons.py forms               # icon contact sheet
../venv/bin/python pbdb.py --top sa-s 23 5.3 Mammalia 40            # what the PBDB has for a region x interval
```

**The review that finds misplacements** is a listing, not a rule: for the present day, print
"taxon → labels it lands on" for every non-curated taxon and read it. The tool is
`audit_biota.py --placements <age>` (taxon → labels, curated entries left out).
Every defect of the second half of this round
was found that way. Do the same for 1–5 Ma, 50 Ma and 150 Ma next.

New organisms: add `E(...)` lines to a batch in `build/taxa_src/`, run it, then
`taxa_src/fetch_evidence.py <file>` (PBDB cross-check; resolve findings in the batch SOURCE, never
the JSON), then ALWAYS re-run `taxa_src/ranges_within_regions.py`, then `build_silhouettes.py
registry` for own drawings, then `fix_form_icons.py` if a form pass ran.

## State right now

- Last live deploy: **`DATA_V=20260922-0339`**, release 3.8, commit `5c94cdf9`.
- Nothing uncommitted that matters; `build/verify/` (proof PNGs) and `data/pbdb/` (the PBDB
  cache) are gitignored on purpose.
- `audit_all.py --quick`: all validators at baseline. Biota: 14 hard checks at 0; parent-form
  drawings **0** (ratchet at 0); curated exceptions **12**. The frame gate is skipped under `--quick`.
- Registry: **1,382 taxa** in 23 files; 1,229 reach a card; 724 illustrations shipped. ~330 taxa
  carry a box, avoid list, sliced latitude or dated habitat.
- Marine card slots at class/order level: Cz 33%, Mz 40%, late Pz 43%, early Pz 36%, Pc 77%.
- Placement listing read at: 0, 3, 10, 20, 35, 50, 80, 100, 120, 150, 200, 230, 250, 280, 300,
  350, 400, 450, 500, 600 Ma.

## What the third round found (3.8)

1. The later placement ages found fewer, and different, things: lineages shown before they
   reached a continent (ceratopsids in Asia, hadrosaurs in the south), an animal of one
   Lagerstätte on every label of its continent (Scelidosaurus, the Jehol fauna), provincial
   floras leaking across `as-e`/`as-se`/`eu` (Angara, Cathaysia), and a warm Laurentian shelf
   fauna reaching the cold Gondwanan margin through the ocean codes. `avoid` and latitude
   bands did most of the work; boxes need present-day points that palaeo labels lack.
2. A region code can be two provinces at once (`as-e` = North and South China; `as-se` =
   Indochina and Sibumasu). `avoid` by label name is the honest tool where no box can separate them.
3. An oceanic terrane (Wrangellia) typed "island" was a land card with dicynodonts. SUBMERGED
   with a reef/shelf habitat is the setting for an arc.
4. The PBDB's "sea" pseudo-region (collections on no continent) counted against every authored
   range; a basin code now answers it.

## What the second round found (3.7)

1. **Depth changed the composer's job.** With genera available, curated class-level names
   ("Brachiopoda", "Ichthyosauria") were still filling the cards; they now keep one slot when
   four genera are at hand. Genericness on Palaeozoic sea cards nearly halved.
2. **The placement listing at deep time finds a different class of error**: a lineage shown
   before it reached a continent (Rhododendron on Eocene India, Nothofagus on Miocene Parana),
   a cosmopolitan Palaeozoic plant that was really provincial (Lepidodendron, Cordaites,
   Calamites on Gondwana; Rufloria in China), a Solnhofen animal on every Jurassic European
   label. Boxes and time-sliced ranges fixed them; the polar rule needed the LPIA.
3. **Six labels rode the wrong continent** because a palaeo coordinate happened to be land
   today (README §7.24). The home-crust detector in `audit_label_plate.py` catches this class.
4. **Overlapping curated spans lost taxa silently**; **a province name shared across schemes
   swapped descriptions** (§7.25); **a batch writer regenerating its file discarded what tools
   attached** (§7.26). All three fixed structurally.

## What the first round found (3.6)

1. The three reported defects had one shape: **a value with no declared lifetime, place or form
   cannot be wrong in any way a script can see**, and a fallback that always succeeds hides the
   rest. Icons were bound by name substring with a per-realm fallback; province markers were bare
   tuples. (README §7.18.)
2. Region codes are continent-sized. After the registry shipped, the present-day listing still
   showed alligators on the Great Lakes and Amazon dolphins in Titicaca. Fixed with `box` +
   label footprint + `avoid` + altitude-aware habitat (§7.20).
3. "Cosmopolitan" was three false claims: mid-ocean crust, post-Eocene Antarctica, polar ground
   (§7.19).
4. Sixteen labels typed as land are drawn under deep water. The present-day DEM check found them
   mechanically; `SUBMERGED` carries the dates for the past.
5. The province model called every warm sea after 14 Ma "Indo-Pacific". Split by basin hint.
6. Registry notes leak place ("of the interior sea", "here"). Notes are now place-neutral by
   contract and local notes apply only where the taxon is curated (`run[6]`).

## Traps that have each cost real time

- **Subagents for bulk authoring exhausted the account's session limit twice** (12 Fable agents,
  then ~20 Sonnet agents; Sonnet also hit the 64k output cap on sheets over ~50 taxa). Writing
  compact `E(...)` batches directly was far cheaper and better. If agents are used at all: ≤25
  items per sheet, an explicit output budget, patches only.
- PBDB and PhyloPic homonyms (§7.21). Match classification, not just the name.
- The batch scripts regenerate their own JSON: re-run `ranges_within_regions.py` after any of them,
  and put every authored edit in the batch source (the writer preserves only tool-attached keys).
- `build_site.py` refuses when the timeline changed and the preview atlas was not rebuilt: run
  `build_timeline_preview.py` and bump `IMAGERY_V` in BOTH `web/app.js` and `web/ambient.html`.
- Headless Chrome: no spaces in `file://` paths; `--headless=new` never exits after a
  screenshot — wait for the file and kill the PID (§7.23).
- Git on this repo is slow; a timed-out `git add` leaves `.git/index.lock`.
- `build_webdata.build_updatelog()` must run before `build_site.py`, or `docs/updatelog.json`
  ships the previous release's log.

Plus the standing ones: a process backgrounded with `&` inside a tool call dies with the call;
`pgrep -f` matches the waiter itself — wait on a PID.

## The work queue, ranked by how much of the remaining gap each closes

1. **Late Palaeozoic seas at 43%**: the Carboniferous–Permian shelves outside North America
   (the Ural Ocean, the Cathaysian and Gondwanan shelves) and the Devonian reef faunas of
   Australia and the Rhenish shelf. `pbdb_menus/*.md` for as-e, au, eu.
2. **Precambrian at 77%**: microbial by nature. Only the Ediacaran can go further (the White
   Sea and Avalon assemblages at genus level are curated already; the rest is acritarchs).
3. **Placement at the ages between** (the review sampled every ~25–50 Myr): a pass at 5, 15,
   40, 60, 90, 110, 170, 190, 215, 265, 320, 375, 420, 480 Ma would find a handful each.
4. **Curated spans that are still generic** on smaller labels (the province markers are
   class-level by design; the "c" tier is now genus-level on the continents).
5. **Region codes remain continent-sized** where no box or avoid has been authored; the
   listing is how to find them. Splitting `as-e` (North/South China) and `as-se`
   (Indochina/Sibumasu) would retire a dozen `avoid` lists.
6. **The future series' foreland fields are illustrative** (baked from synthesised belts). Fine
   as long as README §9 says so.

## Commands to ship

```bash
cd build
../venv/bin/python -c "import build_webdata as b; b.build_life(); b.build_updatelog()"
../venv/bin/python audit_all.py --quick
../venv/bin/python check_shader.py && ../venv/bin/python build_site.py   # stamps DATA_V, writes ../docs
cd .. && git add -A build web docs README.md HANDOFF.md "Deep Research" && git commit && git push origin main
curl -s "https://augustg97.github.io/tectonic-earth/?cb=$RANDOM" | grep -o "DATA_V='[0-9-]*'"
```
