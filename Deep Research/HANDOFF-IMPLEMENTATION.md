# Handoff prompt — implementing the Deep Research findings

**Paste everything below the line into a new session**, once the register is complete.
This is the session that finally *changes the app*.

---

You are implementing the findings of the Tectonic Earth Deep Research programme. Six
rounds of research produced measurements, models and drafted copy; **none of it has been
applied**, deliberately — that folder informs the model and does not edit it. Your job is
to apply it.

## Read these first, in order

1. `README.md` — especially **§2, the six working rules**. Each came from a specific
   failure. §7 (traps) will save you hours.
2. `Deep Research/research reports/STAGED-CHANGES.md` — **the handover surface.** Every
   item, with the artifact that makes it a drop-in, ordered by measured value.
3. `Deep Research/research reports/WP-04-closing-the-gaps.md` — the four measured results
   that justify the top of that list.
4. `Deep Research/MODEL-GAPS.md` — the full register with status per item.

## The order, and why

Work Tier 1 first. It is ordered by measured value and the items are independent.

### 1. Switch feature tracks to the PALEOMAP rotation model

**The single highest-value change available.** Measured over 53 present-day land points ×
10 ages against our own shipped field: abyssal-plain placement errors **20% → 5%**, better
at every age, best in the Palaeozoic where the frame gap was worst.

The files are already downloaded and gitignored:
`data/paleomap_gpm/Scotese PaleoAtlas_v3/PALEOMAP Global Plate Model/PALEOMAP_PlateModel.rot`
(CC-BY 4.0, 258 plate IDs, −250 → 1100 Ma).

In `build/paleo_tracks.py`, repoint `ROT`/`STATIC` and set `correct_frame=False`
throughout — the frame correction becomes meaningless *and harmful* once both halves of
the pipeline share a frame. **Keep Merdith for boundaries**: `build_plates_gplates.py`
needs resolved topologies, which PALEOMAP's polygon set does not provide.

**The warning that matters most in this whole document:** every tracked label, crater, LIP
and plateau moves. The change is an improvement *in aggregate* and **will look like a
regression on any individual feature that happened to be well placed by the old error.**
Judge it on the population — rerun `Deep Research/modeling/frame_experiment.py`,
`build/audit_labels.py` and `build/audit_label_motion.py` and compare the numbers. Do not
let one favourite feature drive the decision. Then re-derive or delete `frame_offset.json`.

### 2. Climate table corrections

- **Raise the Cretaceous.** Our Phanerozoic maximum is 30.0 °C at 90 Ma; PhanDA (Judd et
  al. 2024) puts it at 36 °C in the Turonian. Position right, amplitude 6 °C short — and
  because 30 °C is exactly the hothouse boundary, **no keyframe in the app ever reaches
  that state**.
- **Lower the O₂ peak** from 36% to ~30%, in `climate.py` *and* on the Guadalupian card,
  which says "~30–35%".
- **Look at 66 → 56 Ma**, where CO₂ doubles 810 → 1600 ppm and GMST moves only +1.5 °C.

Rerun `Deep Research/modeling/climate_audit.py` after. Note the cost: rainfall and ice
depend on temperature, so a large change forces a field rebuild (~25 min) — but the
readout alone needs only `refresh_manifest.py`.

### 3. Hotspots → seamounts, aseismic ridges, guyots

`Deep Research/modeling/hotspots.py` has 53 hotspots with coordinates, chains, LIP roots
and confidence, plus `ASEISMIC_RIDGES` mapping all 15 "absent or generic" ridges
(README §10) to the plume that built each. `seamounts.field()` already takes a `hotspot`
argument and ignores it. Seed along reconstructed plume tracks, then apply

```python
summit_depth = (ridge_depth - edifice_height) + 0.350 * sqrt(age_Myr)
```

Islands drown at ~16 Myr — right for the Hawaiian chain, where Midway at ~28 Ma is an
atoll. That one line gives islands, atolls and flat-topped guyots **without a new noise
function**. Four register items, one mechanism.

### 4. B1 — the biota panel

**Decided by the user: model decides, curated is a flagged exception.** Where the model
has no province, show the global interval list **under a heading that says it is global** —
never implying those taxa lived at that spot.

`Deep Research/modeling/paleobiogeography.py` now returns a named province for **every**
cell in 0–1000 Ma (49 distinct provinces). `audit_curated_biota.py` has already split all
197 curated spans: **9 exceptions, 188 province-typical, 0 conflicts.** The nine are
Solnhofen, Zechstein, Muschelkalk, Nama, Messinian, Paratethys, Lake Pannon,
Mid-Atlantic Ridge, East Pacific Rise, Beringian Steppe-Tundra.

Shape: add `exception: true` to those nine in `life_data.json`; have `regionTaxaAt` return
`(taxa, is_exception)`; make `lifeSection`'s order **exception-curated → province
assemblage → labelled global list**, with the heading naming which one the reader is
seeing. Keep `audit_curated_biota.py` runnable so a new curated entry must declare itself.

## Then Tier 2 — the card text

All of it is written in `Deep Research/research reports/CARD-DRAFTS-round-1.md`, ready to
paste: four hedges on contested claims, the Suess attribution on Glossopteris, the O₂
number, the Pangaea Proxima provenance, and new cards for the PETM, the Azolla event,
OAE 1a/2, the Great Oxidation Event, the Baykonurian glaciation, the Permian Basin,
back-arc basins, and atolls/guyots.

Most of the new ones are **shorter than a 5 Myr keyframe and cannot be drawn**, which is
why STAGED-CHANGES recommends a **fifth navigable panel, "Climate events"**, on the same
`#ctxStack` pattern as intervals / supercontinents / glaciations / extinctions.

Six authored figures already exist for these cards in
`Deep Research/diagrams and illustrations/authored/` — 04, 07, 08, 09, 10, 11. They are
generated by `make_diagrams.py` from the models, so they cannot drift.

## Then Tier 3 — adopt the validators

Four read-only, re-runnable audits in `Deep Research/modeling/`. Run `audit_cards.py`
after any card edit and `audit_label_windows.py` after any `features.LABELS` edit. Both
fail loudly and cost seconds.

## Traps that have each cost real time

From `README.md` §7 and project memory. These are not hypothetical.

- **Run `python build/check_shader.py` before every shader edit.** A backtick anywhere in
  shader source — *even in a comment* — closes the JS template literal and you get a black
  globe with working panels. Reserved words (`flat`, `patch`, `sample`, `smooth`, `filter`,
  `shared`, `buffer`, `input`, `output`) do the same.
- **Cache-busting is built in.** `build_site.py` calls `stamp_data_version.py`. If you
  deploy by hand, run it yourself or the change will look like it never happened.
- **`pgrep -f <script>` matches the waiter's own command line.** Use `[b]uild_fields.py`.
- **A preview server started with `&` inside a Bash call dies when that call ends.** Start
  it as its own background task.
- **The Browser pane cannot composite the WebGL canvas here.** Use the headless-Chrome
  recipe in memory, or `gl.readPixels`. DOM overlays composite fine.
- **`pygplates` does not refuse negative times** — it extrapolates and returns confident
  nonsense.

## How to work

Follow the six rules in `README.md` §2. The three that bite hardest on this particular
job:

- **Visually verify.** "The field has the value" is not confirmation. Render it and look.
- **Fix the system, not the instance.** Every item above is deliberately a system change;
  keep it that way.
- **Address every item and never silently drop one.** If something can't be done, say so
  and say why.

And the pattern this programme kept hitting, worth carrying forward: **when an audit
disagrees with the app, check the audit first.** Five times out of five so far, the error
was in the research, not in the model.

## Finishing

Rebuild order is in `README.md` §6. End with `build_site.py` → commit → push to `main`,
and verify the live `DATA_V` stamp and a live render at
https://augustg97.github.io/tectonic-earth/ — the user reviews on the live site, so a
local-only change reads as "not done".

Update `Deep Research/MODEL-GAPS.md` as you go so the register reflects what is actually
in the app.
