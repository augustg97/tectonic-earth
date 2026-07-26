# Modeling

Runnable models of planetary systems across deep time. These are the research folder's
*executable* output: where a research finding could have been a hand-written table, it is
instead a function with a selftest, so a new age produces a defensible answer without new
authoring.

Every module runs standalone and prints a worked demonstration:

```bash
cd "Deep Research/modeling"
../../venv/bin/python deeptime.py
../../venv/bin/python paleogeography.py
../../venv/bin/python paleobiogeography.py
../../venv/bin/python climate_ebm.py
../../venv/bin/python biome_model.py
../../venv/bin/python taxa_db.py        # also writes taxa.json
```

## Design rules

1. **Dependency-light on purpose.** Everything is stdlib-only except `climate_ebm.py`,
   which needs numpy. This is so `build/` can import any of them later without adding a
   dependency to the app's build chain.
2. **Every module has a `_selftest()`** that asserts internal consistency — no gaps or
   overlaps in the timescale, every assembly member a known block, every taxon's realm
   valid, no land taxon before land plants, the biome eras tiling time completely.
   The selftests are the contract; break one and the module tells you.
3. **Confidence is a field, not a footnote.** `good` / `moderate` / `contested` on events,
   blocks, assembly memberships and provinces. A card that states a contested thing flatly
   misrepresents how well it is known.
4. **"Unknown" is a legitimate return.** `paleobiogeography.province()` returns
   `confidence='none'` with a climate band where no named province scheme is established,
   rather than inventing one. Silent fabrication is the failure mode this whole folder
   exists to avoid.
5. **The figures read from these modules**, so a corrected date propagates into the
   illustrations automatically (`../diagrams and illustrations/make_diagrams.py`).

## Dependency graph

```
deeptime.py            (no deps)
paleogeography.py      (no deps)
biome_model.py         (no deps)
taxa_db.py             (no deps)
paleobiogeography.py   -> deeptime, paleogeography
climate_ebm.py         -> numpy
make_diagrams.py       -> deeptime, paleogeography, biome_model, climate_ebm
```

## How the app would consume these

None of this is wired into `build/` — that is deliberate. When it is, the natural seams are:

| module | app seam |
|---|---|
| `paleogeography.exists()` / `.affiliation()` | a **validator** in `build_webdata.build_labels()`: refuse to draw a block label outside the block's life, warn on every contradicted window in `features.py` |
| `paleobiogeography.province()` | the default behind `life.region_taxa`, with the curated lists kept as overrides for genuinely distinctive localities |
| `biome_model.biome()` | an era parameter on the terrain shader's land colour, so a Silurian continent is rock rather than green |
| `deeptime` catalogues | cross-check `features.py`, `climate.py` and `eras_data.json`; the confidence field feeds card text |
| `taxa_db` attributes | size / habit / diet on the biota cards, which currently carry names and a note only |
| `climate_ebm.solve()` | an offline check that `climate.py`'s ice line is physically consistent with its own CO₂ and solar luminosity — `iceS` is presently an input, not a consequence |

See [`../MODEL-GAPS.md`](../MODEL-GAPS.md) for the prioritised list.

## Known limits

- **`climate_ebm.py` understates hothouses.** ~2.5 °C per CO₂ doubling against PhanDA's
  ~8 °C apparent Earth-system sensitivity, because a 1-D model has no clouds, no
  water-vapour lapse-rate amplification and no continents. Use it for the shape of the
  response and the position of the ice line, never for absolute greenhouse GMST. Its
  snowball *escape threshold* is also too high — the logarithmic CO₂ forcing law is not
  valid at 10⁵ ppm. The hysteresis is the robust result; the number is not.
- **`taxa_db.py` is a 105-entry seed**, thinnest from the mid-Cambrian to the Silurian.
- **`deeptime.STAGES`** is complete for the Mesozoic and Cenozoic, representative for the
  Palaeozoic.
- **`paleogeography.py` anchors are approximate** — a handful of representative points per
  block, chosen to be on land today, not digitised craton outlines.
