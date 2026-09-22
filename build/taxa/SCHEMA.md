# The taxon registry

Every organism that any Tectonic Earth card can show is declared **once**, here, in
`build/taxa/*.json`. `build/biota.py` loads every file, validates it, and composes each
card from it; `build/audit_biota.py` replays every card the app can show and fails the
build on an anachronism, a misplacement, a land card with no fauna or no flora, or a
taxon with no drawing. A name defined in two files is an error.

```json
{
  "taxa": {
    "Megatherium": {
      "rank": "genus",
      "realm": "land",
      "form": "groundsloth",
      "fad": 5.3, "lad": 0.011,
      "range": ["sa", {"t": [2.7, 0.011], "in": ["ca"]}],
      "hab": ["grassland", "forest"],
      "w": 3,
      "note": "An elephant-sized ground sloth of the Pampas, rearing on its hind legs and tail to strip branches. It died out about 11,000 years ago, within centuries of people arriving."
    }
  }
}
```

## Fields

| field | required | meaning |
|---|---|---|
| `rank` | yes | species, genus, family, order, class, phylum, clade, informal, assemblage … |
| `realm` | yes | `sea` · `land` · `air` (flying animals only) · `fresh` |
| `form` | yes | body plan, a key of `biota_forms.FORMS`. **Decides the drawing.** Choose the most specific form that is true. |
| `fad`, `lad` | yes | first and last appearance, **Ma**. `lad: 0` means extant. Use the real stratigraphic range, stage-level precision. A Pleistocene extinction is `0.011`, not `0`. |
| `range` | yes | where it lived. A list of region codes (apply for the whole lifetime) and/or time slices `{"t": [old, young], "in": [codes]}`. Every moment of `fad`–`lad` must be covered by something. |
| `note` | yes | one or two sentences, ≤ 320 characters, in the app's voice: concrete, specific, what makes it worth knowing. No "is a genus of". |
| `hab` | no | habitats it is tied to: `desert forest rainforest grassland tundra alpine wetland lake river coast island cave reef shelf pelagic deep vent ice`. Omit for a generalist or where unknown. A taxon with `hab` never appears on a card of a different habitat (a desert card shows only desert-capable taxa), so only state what is true. |
| `lat` | no | `[min, max]` absolute palaeolatitude, for climate-zoned taxa with long ranges (reef corals `[0,35]`, reindeer `[50,90]`). May be sliced by time — `[{"t": [95, 34], "lat": [0, 78]}, {"t": [34, 0], "lat": [0, 40]}]` — because palms stood at 70° in the Eocene and stop near 40° now. |
| `box` | no | a finer address INSIDE the region codes, which are continent-sized: `[[lon_w, lon_e, lat_s, lat_n], …]` in present-day coordinates. A label with a local footprint shows the taxon only if its point lies within `biota.label_reach` of a box; continents and whole oceans ignore boxes. A relict with a wider fossil range takes a time-sliced box, `{"t": [old, young], "box": [[…]]}` (giant sequoia is a Sierra Nevada tree only since 2.6 Ma). Split a box that crosses the date line. |
| `avoid` | no | label names this taxon must never be used as fill on — the blunt instrument for what a point and a reach cannot say (the Alps and the northern Apennines are two degrees apart and share no ibex). Validated against `labels.json`. |
| `pic` | no | the PhyloPic taxon to trace for an entry that is not itself a genus or species (`"Ceratioidei"` → `"pic": "Melanocetus"`). |
| `only` | no (curated span) | on a span in `life_data.json`: the curated list is the whole card, and the model adds nothing (Lake Vostok under its ice). |
| `pbdb_ok` · `place_ok` · `conf_note` | no | the reviewer's verdict on a PBDB disagreement about dates or places, with the reason. `taxa_src/fetch_evidence.py` attaches the record; the batch writer preserves these. A homonym is recorded as `"pbdb": {"homonym": "..."}`. |
| `w` | no | prominence 1–3. 3 = the one a museum would lead with. Default 2. |
| `rep` | no | for a higher taxon or assemblage: the registry taxon whose silhouette stands for it (`"Litopterna"` → `"rep": "Macrauchenia"`). |
| `assemblage` | no | `true` for a Lagerstätte or named fauna/flora ("Morrison fauna"). At most one is shown per card, after the real organisms. Must have `rep`. |
| `cls` | when PBDB has nothing | `{"phylum","class","order","family"}` — the classification, so the form can be checked. |
| `aka` | no | other display names that mean this entry (`"Jehol Biota"` ← `"Jehol biota"`). |
| `conf` | no | `good` · `moderate` · `contested`. |
| `fill` | no | `false` = only show where a curated list or province names it; never used as general fill. For entries that are only meaningful at one locality. |
| `pbdb` | tool-written | the PBDB evidence snapshot. Do not hand-edit. |
| `pbdb_ok` | no | `true` = the authored range knowingly disagrees with the PBDB's, with the reason in `conf_note`. |

### Three rules about place that the composer applies for you

- **"Cosmopolitan" stops at the edge of the continents.** A land, freshwater or flying taxon ranged `cosmo` is not at home on a label whose home is ocean basin and nothing else (Kerguelen, Mauritius, a seamount). Ocean-island life is ranged on its ocean's code (`ind`, `sou`, `arc`) and boxed to its archipelago.
- **After 34 Ma, Antarctica takes only what names it.** `cosmo` and `gondwana` do not reach a label whose only crust is `an` once the ice is there; write `"an"` explicitly (with a slice) for anything that really persisted.
- **Polar ground takes nothing on trust.** Poleward of 70° in the ice ages (north from 2.6 Ma, south from 14 Ma) a card is tundra and ice whatever the label's type, and a taxon with no `hab` is not assumed onto it.

**Write the batch, not the JSON.** `taxa_src/<batch>.py` is the source; it regenerates `taxa/<file>.json` and carries forward only what tools attach (`pbdb`, the `*_ok` verdicts, `conf_note`, `no_own_icon`). A hand edit to the JSON alone is lost on the next run. Refinements to existing entries go in `taxa_src/ranges_within_regions.py`, which is re-applied after every batch.

Notes are place-neutral. A registry note is shown on every card the taxon reaches, so it must not say "here" or name one locality as if it were the card's; the sentence about a taxon AT a place belongs in that label's curated list in `life_data.json`.

## Region codes

**Where the fossils are found today** — present-day crust. A fossil lies in the crust its
animal lived on, so this is independent of any plate model and valid at any age:
*Lystrosaurus* is `af-s, in, an, as-e, eu` because that is where it is dug up.

```
na-w  W North America: Cordillera, Great Plains, Alaska south of 60N
na-e  E North America: shield, Appalachians, coastal plain
na-n  Arctic North America (north of 60N)
ca    Mexico south of the Tropic, Central America, Caribbean
gl    Greenland
sa-n  tropical South America: Amazonia, N and central Andes (north of 18S)
sa-s  southern cone, Patagonia, Falklands
eu    Europe to the Urals, incl. Iceland
af-n  Maghreb, Sahara, Egypt        af-e  Rift, Ethiopia, Horn
af-w  Guinea, Congo basin           af-s  Karoo, Kalahari, Zambezi
mg    Madagascar                    ar    Arabian plate
as-w  Anatolia, Caucasus, Iran, Afghanistan
as-n  Siberia, Russian Far East     as-c  Kazakhstan, Tarim, Tibet, Mongolia
as-e  China, Korea, Japan           as-se Indochina, Sundaland, Philippines
in    Indian subcontinent           au    Australia, Tasmania
ng    New Guinea                    nz    New Zealand, New Caledonia
oc    Pacific islands               an    Antarctica
```

Aliases: `na sa af as` (all sub-codes) · `laurentia` (na+gl) · `euramerica` · `laurasia`
· `holarctic` · `gondwana` · `afro-arabia` · `sahul` · `old-world` · `new-world` ·
`neotropics` · `cosmo` (everywhere — use for genuinely cosmopolitan or open-ocean taxa).

Marine taxa use the **crust whose shelf they are found on** (an Ordovician Laurentian
trilobite is `na`), and/or an ocean basin for the living and recently living:
`pac atl ind arc sou med tet(hys) pan(thalassa) iap(etus) rhe(ic) ura(l) mir(ovia)`.
Pelagic, cosmopolitan forms are `cosmo`.

Use time slices for dispersal: camels are `na` from 45 Ma, `old-world` only from ~7 Ma,
`sa` from 3 Ma, and gone from `na` at 0.011.

## Forms

`python3 build/biota_forms.py` lists them; the table is `FORMS` in `build/biota_forms.py`.
Pick the most specific true one: *Ursus* is `bear`, not `carnivoran`; *Macrauchenia* is
`litoptern`; kelp is `kelp`; a lichen is `lichen`. If nothing fits, add the form to
`new_forms` in your file (`{"name": {"kind","desc","terms":[PhyloPic search terms],
"parent": "nearest existing form", "of": [PBDB clade names]}}`) rather than forcing a
wrong one — a wrong form is exactly the bug this registry exists to end.

## Evidence

`python3 build/pbdb.py "Name"` prints what the Paleobiology Database knows: classification,
first/last appearance (`fea`/`lla`), and `regions` — occurrence counts per region code
with oldest/youngest age. **Use it; do not trust it blindly.** PBDB ranges include
misidentifications (it starts *Megatherium* in the Oligocene). The authored range should
be the consensus one; where it knowingly departs from the PBDB's, set `pbdb_ok: true`
and say why in `conf_note`.

`python3 build/biota.py --check-file build/taxa/yourfile.json` validates one file.
