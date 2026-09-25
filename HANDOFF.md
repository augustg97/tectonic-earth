# Handoff — Tectonic Earth (mountains 3.12; flora and fauna 3.6–3.11)

Paste this whole file as the first message of a new session.

---

## What you are working on

**Tectonic Earth** — interactive deep-time paleogeography app, 1000 Ma → +250 Myr, globe + Mollweide map.

- Repo: `/Users/augustgweon/Tectonic Plate Model` (venv at `./venv/bin/python`; do NOT move it to `~/Desktop`)
- Live: https://augustg97.github.io/tectonic-earth/ (GitHub Pages serves `main:/docs`)
- **Read `README.md` first**: §2 working rules, §5.10 mountains (the erosion relief), §5.1b the
  future series (the collision zone), §5.6 the biota subsystem, §6 the gate and the build
  commands, §7 traps (7.30–7.32 are this round's), §9 known limits.
- `build/taxa/SCHEMA.md` is the authoring contract for organisms.

## The latest round: mountains (3.12, 2026-09-24)

The user: "our mountains before the end-Permian and in the future still look not good -- the
pre-end-Permian mountains look like symmetric triangular prisms, and the future mountains clump
up unrealistically... Let's fix these mountains so they look and appear natural and complex."
(The future in general being rough was deferred by the user: "we'll address that later".)

**What was wrong, measured.** Inside belts, the relief finer than ~60–90 km is 84 m at 1 km and
176 m at 2.2 km of regional elevation today, 16–44 m at 300–400 Ma, 11 m in the Precambrian,
~23 m on the future's belts: Scotese drew old belts as smooth envelopes and the future's belts
were gaussian domes over the plate-overlap patches. The prism's dark face is shade clamped at
zero (a smooth flank at the base's ~156x is tilted past the sun), not colour (README 7.30).

**What shipped.**
- `build/relief_deficit.py` — the relief deficit in the blue of every `_f` (`build_foreland`
  writes it too). `--stats`, `--calib`, `-j 4`.
- `eroRelief()` in `web/shaders/index__FRAG.frag.glsl` — a slope-steered, branching erosion
  filter, material-keyed, 96 km → 0.75 km; coarse octaves times the deficit, fine ones always;
  analytic slope into the normal; height into z and tone; the envelope's face handed to the
  facets; faded under ice; no new water. The fold-axis noise compression (fingerprint whorls,
  7.31) is retired while it is on. Knobs `?ero= ?eroN= ?eroF=`, masks `?show=10..15`.
- `_zone_orogen()` in `build/build_fields.py` — the future's collision zones as plateau + a main
  range on the pruned medial axis (7.32) + swell + crust-keyed segmentation; 50 future keyframes
  rebuilt with their `_d _w _f _q _x`. +250 Myr: >2 km 13.0, >4 km 2.5 Mkm², summit 6.5 km.
- Both sheet sets re-baked, the preview atlas rebuilt; `FIELD_V`, `SHEET_V`, `IMAGERY_V` bumped.

**Open, none of it asked for.** The Precambrian belts are 1–1.5 km swells and are dissected
lightly (little relief to cut; their height is `precambrian.py`'s). The future ranges sit where
the rigid groups overlap — the same kinematic input as before, drawn as an orogen. The future
still carries the Antarctic ice surface as land. **The future's orogen LABELS are fixed authored
points** (`features.py`: Neo-Himalaya 60°E 25°N, Trans-Atlantic Belt 0°E 25°N, Afro-European Belt,
Australasian Belt) with no tie to where the model's collision zones are: at +250 Myr the
Neo-Himalaya label sits just east of the new range system and the Trans-Atlantic Belt over the
sea, and that label's text describes an Atlantic closure this model's +250 frame does not show.
Pre-existing (labels.json did not change this round); it belongs to the deferred future round —
position them from `_zone_orogen`'s medial axes, or re-word them. Judge the look on a real display: `?ero=0`
beside the default, and `?eroN=` (normal gain, default 100) / `?ero=` (depth) to bracket it.

## The flora-and-fauna task (3.6–3.11)

The user asked for the feature cards' flora and fauna to be fixed **systematically**: every card
rich, accurate, diverse, with the right icon, the right organisms for that place and time, and a
tracking system so it cannot decay. The system shipped in 3.6; 3.7–3.11 (2026-09-22) added
depth — 409 taxa for the seas, Palaeozoic land and the Precambrian — read the placement
listing at thirty-four ages and re-read it after every batch, re-anchored nine mislaid
labels, hand-drew the last forms, closed the five 404s, rewrote the class-level curated
lists by tool, and split every region code that was two crusts (East Asia into four blocks,
Australia into two, Europe into two, eastern North America into two). The user's
instructions were "keep going until completion", then "the remaining placement ages and the
Mesozoic seas", then "the late Palaeozoic shelves and the in-between ages, Precambrian,
region codes", then "the eu split and the early Palaeozoic seas, and Ediacaran, and the
re-read", then "address all remaining next round/handoff items": all done; the queue below
is what depth remains, and none of it was asked for. There is no open loop; every round ends
deployed and verified live.

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

- Last live deploy: **`DATA_V=20260925-0752`**, release 3.12 (the mountains), commit `08d2f435` (the record is the commit after it).
  Before it: 3.11, `DATA_V=20260922-1642`, commit `da86a95c`.
- Cache versions: `FIELD_V='20260925-relief'`, `SHEET_V='20260925'`, `IMAGERY_V='20260925'`
  (in `web/app.js` AND `web/ambient.html`).
- Nothing uncommitted that matters; `build/verify/` (proof PNGs) and `data/pbdb/` (the PBDB
  cache) are gitignored on purpose.
- `audit_all.py --quick`: all validators at baseline. Biota: 14 hard checks at 0; parent-form
  drawings **0** (ratchet at 0); curated exceptions **12**. The frame gate is skipped under `--quick`.
- Registry: **1,565 taxa** in 26 files; 744 illustrations shipped. ~560 taxa carry a box,
  avoid list, sliced latitude, dated habitat or block-level range. The curated record
  (`life_data.json`, 212 spans) is genus-level wherever the registry can be: 63 class-level
  names replaced by `taxa_src/upgrade_curated.py`; class-level curated slot-ages 6,188 → 2,840.
- Marine slot-ages at class/order level, by `build/measure_generic.py` (run it on two
  `life.json` files side by side; the 3.7–3.8 figures used an unrecorded counting and are not
  comparable): Cz 20%, Mz 25%, late Pz 25%, early Pz 22%, Pc 38%.
- Placement listing read at: 0, 3, 5, 10, 15, 20, 35, 40, 50, 60, 80, 90, 100, 110, 120, 150,
  170, 190, 200, 215, 230, 250, 265, 280, 300, 320, 350, 375, 400, 420, 450, 480, 500, 600 Ma.
- Region codes: `as-ne as-s as-ic as-sb` (East Asia by block), `au-w au-e`, `eu-n eu-s`
  (Baltica–Avalonia / the peri-Gondwanan south), `na-e na-av` (Laurentian craton / the
  Avalon and Carolina terranes); `as-e`, `as-se`, `au`, `eu` are aliases and `na` includes
  `na-av` while `laurentia` does not. `pbdb.REGIONS` is first-match boxes;
  `biota.LAND_CODES`/`ALIASES`; after any change run `taxa_src/recode_regions.py` so the
  PBDB evidence on every entry is binned under the new table (offline, from the cache).

## What the sixth round found (3.11)

1. **The curated record was the last class-level layer**, and it is fixable by tool: a curated
   name has authority over place, so the upgrader applies the composer's own place rules
   (at_home, in_reach, latitude, habitat, at three ages the genus is alive) before it lets a
   genus in, and keeps the curated prose on the first genus because the prose is about the
   place. 49 names stay: the Tonian oceans' acritarchs and cyanobacteria (the honest answer),
   vent Archaea, the Arctic's cold bivalves (a KEEP list with reasons).
2. **A two-realm genus must be written in the realm the span asked for**: Groenlandaspis is
   `fresh` first and `sea` too; written as `fresh` on the Kaskaskia Sea it tripped the
   realm-lock validator. The upgrader writes the curated realm.
3. **A group is matched by classification tokens AND form**, and forms lie: an edrioasteroid
   drawn as a crinoid matched "Crinoidea"; an anaspid drawn as an ostracoderm matched
   "Osteostraci"; a tommotiid's PBDB phylum is Brachiopoda. `GROUPS` names the tokens and
   `EXCLUDE_FORMS` the exceptions; read the report before `--apply`.
4. The Cryogenian record is thin but not empty (Bavlinella, Leiosphaeridia, the Datangpo and
   Twitya beds); the stage-marker agnostoids are cosmopolitan by nature, so the early
   Palaeozoic's generic share does not fall further from them.
5. A proof sheet composes a card for a label at an age the label does not exist (Avalonia at
   515 Ma): the composer answers, the shipped data has no run, the sheet shows an empty card.
   Choose ages inside the label's span.

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

- **Mountains (3.12).** Split albedo from lighting (`?show=14/15`) before tuning either: the
  prism's dark face was shade clamped at zero (README 7.30). Measure km per pixel off the camera
  (zoom 2.5 is ~7 km/px) before choosing octave scales. The sheet bake used to stall for its whole
  deadline on the 1000 Ma keyframe, whose `_v` the timeline declares absent (fixed in
  `_sheetKindsResident`). `bake_sheets.py` always writes `web/sheets/` and resets its manifest on a
  width change: park the other set before baking. A driver that uses `multiprocessing` needs an
  `if __name__ == "__main__":` guard: macOS spawns workers by re-importing the script, so an
  unguarded one re-ran every step in each worker (four processes writing the same files) and the
  pool respawned the dying workers until killed by PID.

Plus the standing ones: a process backgrounded with `&` inside a tool call dies with the call;
`pgrep -f` matches the waiter itself — wait on a PID.

## The work queue, ranked by how much of the remaining gap each closes

1. **After any batch**: `--placements` at a few ages near its span, read; then
   `taxa_src/upgrade_curated.py` (report, read, `--apply`) so the curated cards take the new
   genera too. These two are the maintenance loop; nothing else in the queue is owed.
2. **What is still class-level is honestly so**: the Tonian and Cryogenian oceans' plankton
   (acritarchs, cyanobacteria), the vent Archaea, the small-shelly interval's list. A further
   Ediacaran Doushantuo–Lantian batch (Weng'an embryos, Lantian macroalgae by genus) would
   move the Precambrian a point or two.
3. **Sub-leaf structure stays on `avoid` lists** (Avalonia/Baltica, Mongolia/North China,
   Carolina/Avalon) until the listing shows a card wrong because of it; none did at fifteen
   ages after the mirrored lists.
4. **The future series' foreland fields are illustrative** (baked from synthesised belts). Fine
   as long as README §9 says so.

## Commands to ship

```bash
cd build
../venv/bin/python -c "import build_webdata as b; b.build_labels(); b.build_life(); b.build_updatelog()"
../venv/bin/python audit_all.py --quick
../venv/bin/python check_shader.py && ../venv/bin/python build_site.py   # stamps DATA_V, writes ../docs
# A SHADER change invalidates both sheet sets and the preview atlas (README 5.9, 5.11):
#   mv ../web/sheets ../web/sheets4096 ; ../venv/bin/python bake_sheets.py --width 2048
#   mv ../web/sheets2048 <backup> ; mv ../web/sheets ../web/sheets2048 ; mv ../web/sheets4096 <backup>
#   ../venv/bin/python bake_sheets.py            # the 4096 set, into ../web/sheets
#   ../venv/bin/python build_timeline_preview.py # then bump SHEET_V and IMAGERY_V in app.js AND ambient.html
# A FIELD change (any _e/_f/...) wants FIELD_V bumped in both too, or browsers keep the old textures.
cd .. && git add -A build web docs README.md HANDOFF.md "Deep Research" && git commit && git push origin main
curl -s "https://augustg97.github.io/tectonic-earth/?cb=$RANDOM" | grep -o "DATA_V='[0-9-]*'"
```
