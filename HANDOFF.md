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
tracking system so it cannot decay. That system shipped in release 3.6. What remains is DEPTH
(the work queue below), not mechanism. There is no open loop; the standing rule applies — every
round ends deployed and verified live.

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

New organisms: add `E(...)` lines to a batch in `build/taxa_src/`, run it, then ALWAYS re-run
`taxa_src/ranges_within_regions.py` (the batch scripts regenerate their JSON and would drop its
refinements otherwise), then `build_silhouettes.py registry` for own drawings.

## State right now

- Last live deploy: **`DATA_V=20260921-2222`**, release 3.6, commit `e76651ff`.
- Nothing uncommitted that matters; `build/verify/` (1.3 GB of proof PNGs) and `data/pbdb/` (the
  PBDB cache) are gitignored on purpose.
- `audit_all.py --quick`: all validators at baseline. Biota: 14 hard checks at 0; parent-form
  drawings **30** (ratchet, may only fall). The frame gate is skipped under `--quick`.
- Registry: **1,156 taxa** in 16 files; 1,039 of them reach a card. 668 illustrations shipped.
  `web/life.json` is 1.96 MB raw, ~450 KB gzipped.

## What this round found

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
- The batch scripts overwrite their own JSON: re-run `ranges_within_regions.py` after any of them.
- Headless Chrome: no spaces in `file://` paths; `--headless=new` never exits after a
  screenshot — wait for the file and kill the PID (§7.23).
- Git on this repo is slow; a timed-out `git add` leaves `.git/index.lock`.
- `build_webdata.build_updatelog()` must run before `build_site.py`, or `docs/updatelog.json`
  ships the previous release's log.

Plus the standing ones: a process backgrounded with `&` inside a tool call dies with the call;
`pgrep -f` matches the waiter itself — wait on a PID.

## The work queue, ranked by how much of the remaining gap each closes

1. **Deep-time placement review.** Run the "taxon → labels" listing at 1–5 Ma, 20, 50, 100, 150,
   250, 300 and 400 Ma and read it, as was done for 0 Ma. Expect the same classes: endemics
   leaking across a coarse code, notes naming a place, lowland taxa on high ground.
2. **Palaeozoic and Mesozoic marine depth.** Open-ocean and many shelf cards before the
   Cretaceous lean on class- and order-level entries. `pbdb.py --top <code> <old> <young> <clade>`
   lists what is actually found, and the menus from this round are kept in
   `build/taxa_src/pbdb_menus/` (top genera per region × era). Target: genus-level fauna for every Sloss sea, the Tethys and Panthalassa
   margins by stage.
3. **Devonian–Carboniferous land fauna outside Euramerica**, and regional Palaeozoic floras
   (Cathaysian, Angaran) at genus level.
4. **Reduce the 30 parent-form drawings** — hand-draw the forms PhyloPic lacks (belemnite,
   conodont animal, blastoid, bryozoan colony, rudist, stromatoporoid, horn coral, agnostid,
   zosterophyll, progymnosperm, astrapothere, embrithopod, mesosaur, ostracod, heteromorph,
   bamboo, goblet). `fix_form_icons.py` `HAND` shows the format; the ratchet then tightens.
5. **Palaeo-frame labels drawn on the wrong crust** (Gilboa Forest at 84.5°S at 385 Ma, Acadian
   Belt, Oslo Rift, Rotliegend Desert, Zechstein Sea, Solnhofen Lagoon…). Biota is already right
   via `LABEL_HOME`; the label POSITION is wrong and `audit_label_plate.py` misses it. A task
   chip was spawned for this ("Fix labels tracked along the wrong crust").
6. **Seventeen Tonian–Cryogenian land labels share one identical list.** Honest, dull. Block-level
   microfossil assemblages (Bitter Springs, Chuar, Svanbergfjellet, Doushantuo) would differentiate them.
7. Optional: finer region codes (split `as-se` Sundaland/Wallacea, `sa-s` Atacama/Patagonia,
   `na-w` by latitude) — only if the box mechanism proves too fiddly to maintain.

## Commands to ship

```bash
cd build
../venv/bin/python -c "import build_webdata as b; b.build_life(); b.build_updatelog()"
../venv/bin/python audit_all.py --quick
../venv/bin/python check_shader.py && ../venv/bin/python build_site.py   # stamps DATA_V, writes ../docs
cd .. && git add -A build web docs README.md HANDOFF.md "Deep Research" && git commit && git push origin main
curl -s "https://augustg97.github.io/tectonic-earth/?cb=$RANDOM" | grep -o "DATA_V='[0-9-]*'"
```
