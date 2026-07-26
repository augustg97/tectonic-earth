# WP-04 · Closing the gaps: four measured results

**2026-07-26, round 3.** This paper reports what happened when the register's P1 items
were actually executed rather than described. Four of them produced measurements. One
produced the largest single result this research programme has found.

---

## 1. A1 — the frame problem has a clean solution, and it was published in 2016

**The question.** The app's largest residual error is that ~27 tracked labels sit on the
wrong medium for more than a third of their span. The cause is a two-frame problem:
terrain from the Scotese & Wright PaleoDEMs, feature tracks from Merdith et al. (2021).
Palaeomagnetism never constrains absolute longitude, so the two models put the same
continent at different longitudes — ~9° at 90 Ma, ~21° at 150 Ma, ~40° in the Ordovician.
`frame_offset.py` patches it with a smoothed **rigid** longitude shift, which helped
(craters on plausible terrain 80% → 90%) but cannot close it, because the real difference
is regional.

**The finding.** Scotese publishes his own rotation model, and has since 2016.

```
Scotese_PaleoAtlas_v3.zip  (58 MB, EarthByte, CC-BY 4.0)
  └── PALEOMAP Global Plate Model/
        PALEOMAP_PlateModel.rot        79 KB   258 plate IDs
        PALEOMAP_PlatePolygons.gpml   5.3 MB
```

Header: `PALEOMAP Plate Model m15g60_v2d3 · by CR Scotese 02/01/2016`. It spans
**−250 Ma (future) to 1100 Ma** — the app's *entire* range, future included — and is
**CC-BY 4.0**, the same licence as the PaleoDEMs and Merdith.

**The experiment** (`modeling/frame_experiment.py`, read-only). 53 present-day land
points spread over every craton, back-advected three ways at ten ages, each landing point
scored against the app's own shipped `_e` texture. Land-today crust should still be
continental crust in the past — it may be a flooded shelf, but landing on **abyssal plain**
means the frame put it in the wrong ocean.

| frame | on land | shelf | **abyss (the error)** |
|---|---|---|---|
| Merdith, raw | 64% | 12% | 24% |
| Merdith + `frame_offset` (what the app does now) | 68% | 12% | 20% |
| **PALEOMAP rotations** | **79%** | 16% | **5%** |

**Abyssal-plain errors fall by a factor of four**, and PALEOMAP wins at *every one of the
ten ages*. It wins by most exactly where the frame gap was worst:

| age | Merdith-corrected abyss | PALEOMAP abyss |
|---|---|---|
| 450 Ma | 32% | **8%** |
| 500 Ma | 40% | **8%** |
| 400 Ma | 34% | **11%** |

This is what "the mismatch is zero by construction" looks like when you measure it. The
residual 5% is real error — a 20 km grid, a point sample, genuine model uncertainty — not
frame error.

**Consequences for the register.**

- **A1 — resolved.** The file exists, is licence-compatible, and covers the full range.
- **A3 (regional frame correction) — no longer needed.** It was an elaborate workaround for
  a problem that disappears when both halves of the pipeline use one frame.
- **A4 — demoted.** Anchoring labels to the DEM's own landmasses was partly a way to escape
  the frame dependence. It remains useful for a different reason (a label should ride the
  landmass it names), but it is no longer load-bearing.
- **F1 gains a quantitative path.** The model carries future rotations to +250 Myr, so our
  future series can be checked against Scotese's *rotations*, not just eyeballed against
  his JPEG.
- **A new risk to state plainly:** switching frames means every tracked label, crater, LIP
  and plateau moves. The change is an improvement in aggregate and will still look like a
  regression on any feature that happened to be well placed by the old error. Judge it on
  the population, exactly as this experiment does.

**What is still not solved.** Merdith remains the better model for *topology* — it has
resolved plate boundaries, which drives `build_plates_gplates.py`, and PALEOMAP's polygon
set is a different kind of object. The likely end state is **both**: Merdith for
boundaries, PALEOMAP for feature tracks, which is the frame the terrain is drawn in.

---

## 2. C1 / C3 / C4 / C10 — the climate table, measured

`modeling/climate_audit.py`, read-only, four independent checks.

### C1 — the Cretaceous is 6 °C too cool, and we never reach hothouse

Our Phanerozoic maximum is **30.0 °C at 90 Ma**. PhanDA's is **36 °C in the Turonian
(93.9–89.39 Ma)**.

The *position* is right — our peak sits where PhanDA's does. The *amplitude* is not. And
because 30 °C is exactly the icehouse/hothouse boundary, **no keyframe in the app ever
enters the hothouse state**, while PhanDA finds Earth spent more of the Phanerozoic warm
than cold. Every downstream field inherits this: ice line, rainfall through
`render.compute_fields`, biome colour, and the ocean-anoxia rule (OAEs require GMST above
~25 °C, and ours sit only just above it).

### C3 — the O₂ peak is 36%, and it should be ~30%

Our maximum is **36.0% at 280 Ma**. Krause et al. (2022), the current review, puts the
Permo-Carboniferous maximum near **30%**; 35% is the high end of older GEOCARBSULF runs.
The *timing* is right (Cisuralian). Note this compounds a card error already in the audit
register — the Guadalupian card says "~30–35%" while the table itself says 36.

### C4 — two GMST/CO₂ transitions worth a second look

Using PhanDA's ~8 °C apparent Earth-system sensitivity per CO₂ doubling as a consistency
check, not a law:

- **66 → 56 Ma:** CO₂ doubles 810 → 1600 ppm; GMST moves only +1.5 °C (26.0 → 27.5). This
  is the Palaeocene–Eocene interval, which contains the PETM and runs into the EECO — the
  one place where a large warming is best documented. Suspicious.
- **380 → 360 Ma:** CO₂ nearly halves 1500 → 810; GMST moves −1.0 °C.

Neither is proof of error — palaeogeography and solar luminosity move GMST too — but both
sit where the record is strongest.

### C10 — the faint young Sun is handled correctly

Tonian mean GMST **18.9 °C** against **14.4 °C** today, with solar luminosity **−6.7%**.
Warmer despite a dimmer Sun, which is exactly the expected resolution of the paradox: the
CO₂ column (5,600 ppm at 1000 Ma) is doing the compensating. **No change needed** — and
worth recording as a check that passed, since a table can be wrong in this direction just
as easily.

---

## 3. D1 / D3 / D4 — one catalogue closes three gaps

`modeling/hotspots.py`: **53 hotspots** with present-day coordinates, riding plate, chain,
LIP root, start age, plume flux where published, and a confidence grade. Nine are graded
`strong`; only **Yellowstone** is consistently imaged from the deep mantle to the surface,
which is the calibration for how confident any plume card should sound.

**Eight are rooted in a LIP**, which is the link the app is missing between its volcanism
layer and its ocean floor:

| plume | LIP | then |
|---|---|---|
| Réunion | Deccan Traps, 66 Ma | Laccadive–Chagos → Maldives → Mascarene → Réunion |
| Tristan da Cunha | Paraná–Etendeka, 133 Ma | Walvis Ridge **and** Rio Grande Rise — mirror trails on two plates |
| Kerguelen | Kerguelen Plateau, 118 Ma | Ninetyeast Ridge, ~5,000 km, the longest straight ridge on Earth |
| Galápagos | Caribbean LIP, 92 Ma | Cocos Ridge **and** Carnegie Ridge |
| Iceland | NAIP, 62 Ma | Greenland–Iceland–Faroe Ridge, built on both plates |
| Yellowstone | Columbia River Basalt, 16.5 Ma | Snake River Plain |
| Marion | Madagascar, 88 Ma | Madagascar Ridge |
| Afar | Ethiopian Traps, 30 Ma | a continent splitting three ways |

**D3 falls out directly.** `ASEISMIC_RIDGES` maps **15 named ridges** — every one listed as
"absent or generic" in README §10 — to the plume that built it, with the age span of each
limb. Ninetyeast, Walvis, Rio Grande, Chagos–Laccadive, Cocos, Carnegie, Emperor, Hawaiian,
Louisville, Nazca, Greenland–Iceland–Faroe, New England, Vitória–Trindade, Broken,
Mascarene. These are not a texture problem; they are a catalogue problem, and this is the
catalogue.

**D4 falls out as arithmetic.** An edifice is built at the ridge and then subsides with the
plate on the same half-space law the sea floor uses:

> `summit_depth = (ridge_depth − edifice_height) + 0.350 · √(age in Myr)`

| edifice age | summit | reads as |
|---|---|---|
| 0 Myr | −1.40 km | island |
| 10 Myr | −0.29 km | island |
| 20 Myr | +0.17 km | atoll / shallow bank |
| 40 Myr | +0.81 km | guyot |
| 100 Myr | +2.10 km | deep guyot |

Islands drown at about **16 Myr**, which is the right order for the Hawaiian chain — Midway,
at ~28 Ma, is an atoll. Seeding seamounts along a plume track and applying this one line
produces islands at the young end, atolls in the middle and flat-topped guyots at the old
end **without a single new noise function**. That is the structural-over-cosmetic rule
applied exactly.

---

## 4. B2 / B3 — the biota audits, one confirmed and one downgraded

### B2 — regional coverage is thinnest exactly where provinciality was highest

Count of `region_taxa` spans covering each age:

| age | 0 | 20 | 50 | 90 | 200 | 250 | 300 | 350 | **420** | **460** | 500 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| entries | 48 | 34 | 11 | 5 | 13 | 12 | 4 | 4 | **2** | **2** | 7 |

Coverage falls off with age, which is a curation artifact — we simply know the modern world
better. But the shape matters: the thinnest coverage in the whole record, **two regional
entries**, sits at **420 and 460 Ma** — the Ordovician–Silurian, when the continents were
maximally scattered across latitude and marine provinciality was at its Palaeozoic peak.
The data is least differentiated exactly where the world was most differentiated.

**Concrete target:** the Ordovician–Silurian (the two trilobite realms, the Malvinokaffric
province, the Baltic and Laurentian carbonate shelves) and the Carboniferous (Euramerican
vs Cathaysian vs Angaran vs Gondwanan) are where new regional entries buy the most.

### B3 — downgraded: the Malvinokaffric entry is not a realm error

The register assumed "Malvinokaffric flora" was mis-realmed. It is not. The entry reads:

> `['Malvinokaffric flora', 'class', 'land', 'Early sparse vegetation of horsetails and
> progymnosperms on the southern floodplains.']` — Gondwana, 419–359 Ma

Realm `land` is correct, the content is a plausible Devonian southern high-latitude flora,
and the icon bug that first drew attention to it was fixed months ago. **Only the name is
loose**: "Malvinokaffric" is a *marine* realm, so attaching it to a flora implies a formal
floral province that is not established. Recommend renaming to **"Southern Gondwanan
floodplain flora"** and keeping the taxa. This is a P4 wording fix, not the P1 correctness
problem the register recorded. The three genuinely marine Malvinokaffric entries alongside
it are correct as they stand.

---

## 5. What these four results change

1. **Adopt PALEOMAP rotations for feature tracks.** Biggest single available improvement;
   retire A3; judge on the population.
2. **Raise the Cretaceous** to reach the hothouse state, and check the Palaeocene–Eocene
   transition while there.
3. **Lower the O₂ peak** from 36% to ~30%, in the table *and* on the Guadalupian card.
4. **Wire the hotspot catalogue into `seamounts.field()`** — it closes the seamount, the
   aseismic-ridge and the guyot gaps together, and the physics is one line.
5. **Add Ordovician–Silurian and Carboniferous regional biota**, where coverage is thinnest
   and provinciality was highest.
6. **Rename the Malvinokaffric flora**; leave its taxa alone.

Every one of these is a build-side change, and per the standing rule this folder has not
applied any of them.
