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
tracking system so it cannot decay. The system shipped in 3.6; 3.7–3.10 (2026-09-22) added
depth — 355 taxa for the seas, Palaeozoic land and the Precambrian — read the placement
listing at thirty-four ages and re-read it after every batch, re-anchored nine mislaid
labels, hand-drew the last forms, closed the five 404s, rewrote the class-level curated
lists, and split every region code that was two crusts (East Asia into four blocks, Australia
into two, Europe into two, eastern North America into two). The user's instructions were
"keep going until completion", then "the remaining placement ages and the Mesozoic seas",
then "the late Palaeozoic shelves and the in-between ages, Precambrian, region codes", then
"the eu split and the early Palaeozoic seas, and Ediacaran, and the re-read": all done. What
is left is in the work queue below, and all of it is depth. There is no open loop; every
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

New organisms: add `E(...)` lines to a batch in `build/taxa_src/`, run it, then
`taxa_src/fetch_evidence.py <file>` (PBDB cross-check; resolve findings in the batch SOURCE, never
the JSON), then ALWAYS re-run `taxa_src/ranges_within_regions.py`, then `build_silhouettes.py
registry` for own drawings, then `fix_form_icons.py` if a form pass ran.

## State right now

- Last live deploy: **`DATA_V=20260922-1608`**, release 3.10, commit `f26b056a` (the record —
  README, HANDOFF, MODEL-GAPS, TRAPS — is the commit after it).
- Nothing uncommitted that matters; `build/verify/` (proof PNGs) and `data/pbdb/` (the PBDB
  cache) are gitignored on purpose.
- `audit_all.py --quick`: all validators at baseline. Biota: 14 hard checks at 0; parent-form
  drawings **0** (ratchet at 0); curated exceptions **12**. The frame gate is skipped under `--quick`.
- Registry: **1,511 taxa** in 25 files; 739 illustrations shipped. ~540 taxa carry a box,
  avoid list, sliced latitude, dated habitat or block-level range.
- Marine slot-ages at class/order level, by `build/measure_generic.py` (run it on two
  `life.json` files side by side; the 3.7–3.8 figures used an unrecorded counting and are not
  comparable): Cz 22%, Mz 26%, late Pz 27%, early Pz 21%, Pc 42%.
- Placement listing read at: 0, 3, 5, 10, 15, 20, 35, 40, 50, 60, 80, 90, 100, 110, 120, 150,
  170, 190, 200, 215, 230, 250, 265, 280, 300, 320, 350, 375, 400, 420, 450, 480, 500, 600 Ma.
- Region codes: `as-ne as-s as-ic as-sb` (East Asia by block), `au-w au-e`, `eu-n eu-s`
  (Baltica–Avalonia / the peri-Gondwanan south), `na-e na-av` (Laurentian craton / the
  Avalon and Carolina terranes); `as-e`, `as-se`, `au`, `eu` are aliases and `na` includes
  `na-av` while `laurentia` does not. `pbdb.REGIONS` is first-match boxes;
  `biota.LAND_CODES`/`ALIASES`; after any change run `taxa_src/recode_regions.py` so the
  PBDB evidence on every entry is binned under the new table (offline, from the cache).

## What the fifth round found (3.10)

1. **A code split is three edits and one script**: boxes in `pbdb.REGIONS` (the new leaves
   first, first-match), leaves in `biota.LAND_CODES`, the old code in `biota.ALIASES` (and
   in the group aliases it belonged to), the palaeo-frame `LABEL_HOME`s that named it, then
   `taxa_src/recode_regions.py` so the evidence speaks the new codes and `biota.py --check`
   can dispute a range. Narrow entries by evidence (≥5 collections in one leaf, ≤2 in the
   other, only for ages when the leaves were separate crusts) plus the one-locality names.
2. **`PATCH` is a dict literal and Python keeps the last of a repeated key** (README §7.29):
   51 names had silently lost an earlier round's field. `_patch_merged()` merges by `ast`.
3. Within a leaf there is still structure: Avalonia vs Baltica inside `eu-n`, Mongolia vs
   North China inside `as-ne`, Carolina vs Avalon inside `na-av`. `avoid` and boxes carry
   those; a further split is only worth it when the listing shows a card wrong because of it.
4. The Tonian craton cards had no named assemblage for West Africa, the Congo or the
   Kalahari; the record has them (Atar, Mbuji-Mayi, Rasthof). An assemblage ranks behind
   real genera on a card by design, so the cosmopolitan Tonian genera show first.
5. Sponges were dated to the Tonian by a molecular-clock note; the card at 1000 Ma said
   Porifera. The fad is now the Cryogenian biomarker (660 Ma).

## What the fourth round found (3.9)

1. The in-between ages found the same shapes as before at a finer grain: a Pliocene Arctic
   card typed "tundra" from 5 Ma took hipparions and chalicotheres at 71°N (the label now
   begins at 2.8 Ma with the ice; latitude bands on the genera); families with one continent
   per epoch (anthracotheres, entelodonts, brontotheres, carcharodontosaurs) ranged by time
   slice; genera of one formation (Chinle, Germanic Keuper, Karoo, Cowie Harbour) given boxes.
2. **A box is not consulted on an ocean card** — an ocean has no footprint — so a coastal
   species with a land code reaches every basin that code touches (Thalassocnus on the Atlantic
   and Southern Ocean). Give a shore animal its basin code only.
3. **A label on the right crust today can ride the wrong plate.** The Tethyan Himalaya at
   (88, 29) sat on the Lhasa polygon 30 km north of the suture; at 110 Ma its card stood at
   12°N with India at 43°S. Moved to Tingri (87, 28.5), plate 501; a third detector in
   `audit_label_plate.py` compares each label's home-code continent with its plate block
   (README §7.27). The Anatolide-Tauride block is ACCEPTED there with a reason.
4. **A block resolved by nearest anchor drifts with the age.** "Amuria" is not the province
   model's "Amuria / Mongolia", so the fallback gave it North China's block and a Cathaysian
   banner over an Angaran list. `provinces.LABEL_BLOCK` (README §7.28).
5. Mongolia shares `as-ne` with North China but was Angaran in the Permian: `_NOT_CATHAYSIA`
   avoid lists on the Cathaysian flora until the code is split further. Likewise `eu` spans
   Baltica and the peri-Gondwanan terranes (`_PERI_GONDWANA`).
6. The generic-share measure was quoted from an unrecorded script; now `measure_generic.py`.

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
- The live stamp is in the PAGE (`?cb=`), not in `app.js`: a poll that greps the wrong URL
  reads an empty string forever and looks like a deploy that never landed.
- A name written twice in `ranges_within_regions.PATCH` is merged now; before 3.10 the later
  entry silently replaced the earlier one (README §7.29). Batch-regenerated files (`x-*.json`)
  are the ones that lose the field; hand-authored files keep what an earlier run applied.
- After a `features.py` change run `build_labels()` as well as `build_life()`; `labels.json`
  carries the tracks the cards' palaeolatitudes come from.

Plus the standing ones: a process backgrounded with `&` inside a tool call dies with the call;
`pgrep -f` matches the waiter itself — wait on a PID.

## The work queue, ranked by how much of the remaining gap each closes

1. **The Cryogenian and the Cambrian Series 2 are the generic remainder** (Pc 42%, ePz 21%):
   the Cryogenian record is thin by nature (Tindir, Kingston Peak, the Sturtian–Marinoan
   interlude's acritarchs); the 541–521 Ma small-shelly interval is one list by nature. Only
   the Ediacaran Doushantuo–Lantian and the Furongian by block can still go further.
2. **Curated spans that are still generic** on smaller labels (the province markers are
   class-level by design; the "c" tier is genus-level on the continents).
3. **Sub-leaf structure carried by `avoid`**: Avalonia vs Baltica in `eu-n` (a split along
   the Iapetus/Tornquist suture would cut Britain in two), Mongolia vs North China in
   `as-ne` (`_NOT_CATHAYSIA`), Carolina vs Avalon in `na-av` (`_AVALON` boxes). Split a code
   only when the listing shows a card wrong because of it.
4. **Read the listing again** after any batch of more than ~20 taxa: `--placements` at a few
   ages near the batch's span. It is the check that finds what no rule can.
5. **The future series' foreland fields are illustrative** (baked from synthesised belts). Fine
   as long as README §9 says so.

## Commands to ship

```bash
cd build
../venv/bin/python -c "import build_webdata as b; b.build_labels(); b.build_life(); b.build_updatelog()"
../venv/bin/python audit_all.py --quick
../venv/bin/python check_shader.py && ../venv/bin/python build_site.py   # stamps DATA_V, writes ../docs
cd .. && git add -A build web docs README.md HANDOFF.md "Deep Research" && git commit && git push origin main
curl -s "https://augustg97.github.io/tectonic-earth/?cb=$RANDOM" | grep -o "DATA_V='[0-9-]*'"
```
