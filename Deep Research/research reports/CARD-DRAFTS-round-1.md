# Card drafts, round 1

**Drafted 2026-07-26 from the audit register.** Ready-to-paste text for every finding in
[`CARD-AUDIT-register.md`](CARD-AUDIT-register.md), plus the cards the resource review
argued for. **Nothing here has been applied to the model** — this is a review draft.

**The headline is a good one:** 667 cards, 214,000 characters of user-visible text,
**zero HIGH findings**. Two of the three date disagreements the first audit run reported
turned out to be errors in *my* catalogue, not the app's — the app separates the late
Famennian pulse from the Late Palaeozoic Ice Age and leaves the earliest Carboniferous
warm interval between them, which is more internally consistent than the common
"360–255 Ma" convention. `deeptime.py` was corrected to match. What remains is
**coverage** (things missing) and **hedging** (open questions stated flatly), not error.

Legend: **EDIT** = change existing text · **ADD** = new card · **FIG** = wants an
illustration (see §5).

---

## 1. EDIT — hedge the genuinely open questions (4 findings)

### 1.1 `interval` **Pennsylvanian** — the giant-arthropod oxygen story
> **Append:** The link is a hypothesis, not a settled result. *Arthropleura* and
> *Meganeura* are both now found in strata *younger* than the rainforest collapse, and
> both were probably forest-independent, so "high oxygen made them and the collapse
> killed them" is a story the fossil record does not yet support end to end.

*Evidence:* `research/05-atmosphere-ocean-chemistry/…§1`.

### 1.2 `interval` **Pennsylvanian** and `glaciation` **Late Palaeozoic Ice Age** — endemism after the collapse
> **Replace** any statement that fragmentation drove endemism **with:** The classic
> reading is that each surviving rainforest island evolved its own fauna. A 2018
> re-analysis found the opposite — increased *cosmopolitanism* — so treat the
> fragmentation as established and its biogeographic consequence as open.

*Evidence:* `research/06-paleobiology/…§3`.

### 1.3 `supercontinent` **Pangaea** — same arthropod caveat
Apply 1.1's sentence.

### 1.4 `interval` **Pliocene** and `life` **Pliocene** — Panama
> **Replace** "the Isthmus of Panama closed" **with:** the Isthmus of Panama completed a
> land bridge. Shoaling had been under way since perhaps 10 Ma and the closure date is
> actively debated; what is well dated is the *interchange*, which accelerates sharply
> at about 2.7 Ma.

*Evidence:* `research/06-paleobiology/…§2`.

---

## 2. EDIT — attribution and precision (2 findings)

### 2.1 `label` **Glossopteris Flora** — credit Suess as well as Wegener  · **FIG**
Current text credits the Glossopteris distribution to "one of Wegener's original
arguments". True but incomplete: **Eduard Suess** used exactly this evidence in 1885 to
propose the southern landmass and to *name it Gondwana* — the name the app itself uses on
every Palaeozoic frame.

> **Draft replacement.** The tongue-leaved seed fern that carpeted high-latitude Gondwana
> — a real tree, up to about 30 m, with a trunk to 80 cm and leaves 2–30 cm long carrying
> a distinctive net of veins. It grew in waterlogged ground like a modern bald cypress and
> built the southern coal. In Antarctic wood its growth rings are broad and then stop
> abruptly, in as little as a month: these were polar forests, running flat out through a
> summer of continuous light and shutting down for a winter of continuous dark.
> The same leaves turn up in South America, Africa, India, Australia and Antarctica —
> and the seeds were far too big to cross an ocean. **Eduard Suess used exactly this in
> 1885 to argue for a single southern landmass, and gave it the name this map still uses:
> Gondwana.** Wegener took the same evidence further, into continental drift. It died out
> before 252.3 Ma, some 350,000 years *ahead* of the marine extinction.

### 2.2 `interval` **Middle Permian (Guadalupian)** — the oxygen number
> **Replace** "~30–35%" **with** "~30%". 35% is the high end of older GEOCARBSULF runs;
> Krause et al. (2022) is the current review and puts the Permo-Carboniferous peak near
> 30%.

---

## 3. ADD — the missing events

These are the coverage gaps. They are all **shorter than a 5 Myr keyframe**, so none can
be *drawn*; they want the card treatment the extinctions and glaciations already have.
**Recommendation: one new navigable structure, "Climate events"**, alongside intervals,
supercontinents, glaciations and extinctions — same `#ctxStack` pattern, a fifth accent
colour.

### 3.1 ADD `climate-event` **Palaeocene–Eocene Thermal Maximum (PETM)** — 56.0–55.8 Ma · **FIG**
> The fastest large warming in the geological record, and the closest thing deep time
> offers to a controlled experiment on our own. Somewhere between 3,000 and 7,000 billion
> tonnes of carbon entered the ocean–atmosphere system in roughly 20,000 years, and global
> mean temperature rose **5–8 °C**. The Arctic Ocean reached sea-surface temperatures a
> swimmer would call warm. The deep sea acidified sharply enough to dissolve carbonate on
> the sea floor, and benthic foraminifera suffered their largest extinction of the
> Cenozoic — while on land, mammals responded by getting small, and the modern orders
> (primates, artiodactyls, perissodactyls) appear almost at once and spread across the
> northern continents. The system took about 200,000 years to clean it up, which is the
> number worth remembering: the release was fast, the recovery was not.
> **Source of the carbon:** unresolved. The North Atlantic Igneous Province, erupting
> through organic-rich sediment, is the leading candidate; destabilised methane hydrate
> and thawing permafrost are the others.

### 3.2 ADD `climate-event` **Azolla event** — ~49.3–48.5 Ma · **FIG**
> For about 800,000 years the Arctic Ocean was a freshwater pond covered in fern.
> Continental positions had left the basin almost cut off, and high evaporation plus river
> discharge stacked a fresh layer on top of dense salt water — deep enough for *Azolla*,
> a floating fern, to colonise the whole surface. Under 20 hours of daylight and a very
> high CO₂ sky it can double its biomass in two or three days, fixing roughly a tonne of
> nitrogen and removing about six tonnes of carbon per acre per year. Over four million
> square kilometres and 800,000 years, that is enough on its own to account for an **80%
> fall in atmospheric CO₂ — from about 3,500 ppm in the early Eocene to about 650 ppm.**
> Arctic sea-surface temperatures fell from around 13 °C toward the freezing values of
> today, and for the first time in more than 500 million years the planet could carry ice
> at both poles. This is the moment greenhouse Earth begins turning into the icehouse we
> live in — and the agent was a pond weed.
> **Evidence:** an eight-metre-plus unit in the ACEX Arctic cores, alternating marine
> silica with millimetre laminae of fossil *Azolla*, correlated basin-wide by a gamma-ray
> spike. **Confidence:** moderate — the magnitude of the drawdown is debated even where
> the deposit is not.

### 3.3 ADD `climate-event` **Oceanic Anoxic Event 2 (Bonarelli)** — 94.3–93.5 Ma · **FIG**
> At the hottest moment of the last 200 million years, the deep ocean ran out of oxygen.
> Global mean surface temperature was near 36 °C — the Phanerozoic maximum — and a warm
> ocean holds less oxygen, mixes less, and was being fed nutrients by a hyperactive
> hydrological cycle. Productivity bloomed, the organic rain stripped what oxygen was left,
> and for roughly **820,000 years** the sea floor across much of the world accumulated
> **black, finely laminated mud with no burrows in it at all** — no animal could live
> there to disturb it. The trigger was almost certainly the Caribbean and Madagascar
> large igneous provinces.
> **A point about how this looked:** anoxia is a *subsurface* condition. The Black Sea is
> completely oxygen-free below about 100 m today and its surface looks entirely ordinary.
> The Cretaceous ocean was not green or purple; it was blue, over a dead floor.
> Around 70% of the world's oil source rocks are Mesozoic, and events like this are why.

### 3.4 ADD `climate-event` **Oceanic Anoxic Event 1a (Selli)** — 120.5–119.3 Ma
> The earlier of the two great Cretaceous anoxic events, lasting about 1.0–1.3 million
> years and triggered by the **Ontong Java Plateau** — the largest volcanic edifice on
> Earth, 1.86 million km² of sea floor built in a few million years. Calcareous
> nannoplankton suffered a sharp crisis, and the carbon isotope record swings hard.
> *Companions worth mentioning on the same card, or as sub-entries:* **OAE 1b (Paquier)**,
> Albian, and **OAE 3**, Coniacian–Santonian and more regional than global.

### 3.5 ADD `climate-event` **Early Eocene Climatic Optimum (EECO)** — 53–49 Ma
> The warmest sustained interval of the Cenozoic and the top of the long Palaeogene
> greenhouse: crocodilians and palms in the Arctic, no permanent ice anywhere, and the
> pole-to-equator temperature gradient at its flattest. Everything after it is, on
> average, downhill — the EECO is where the 50-million-year cooling that produced the
> modern world begins.
> *Companions:* **MECO** (~40.5–40 Ma, a 4–6 °C warm reversal in the middle of the
> cooling) and the **Mid-Miocene Climatic Optimum** (~17–14 Ma, the last time the world
> was reliably warmer than today).

### 3.6 ADD `glaciation` **Baykonurian Glaciation** — ~547–540 Ma
> A terminal-Ediacaran glaciation that most compilations leave out, recorded by
> diamictites in Kazakhstan, Iran, Baltica and elsewhere. It sits in the last few million
> years of the Precambrian, overlapping the disappearance of the Ediacaran biota and
> ending just before the Cambrian boundary — which makes it a candidate contributor to
> that turnover, though the case is not made. Its extent is poorly constrained and it was
> nothing like a snowball. **Confidence: moderate.**

### 3.7 ADD `climate-event` **Great Oxidation Event** — 2.46–2.06 Ga (outside the map, card only)
> The single largest change in Earth's surface chemistry, and it happened long before this
> map begins. Free oxygen went from about 0.001% of today's level to a few percent.
> Everything followed from it: **methane**, the greenhouse gas holding the Archaean warm,
> was oxidised away and the planet froze into the **Huronian glaciation**; banded iron
> formations, which need a deep ocean full of dissolved iron, largely stopped forming by
> 1.85 Ga; red beds appeared; an ozone layer formed and the strange sulfur-isotope
> chemistry of an unshielded atmosphere disappeared from the record. Anaerobic life was
> mass-extinguished — the biosphere may have contracted by more than 80%. And **more than
> 2,500 of Earth's roughly 4,500 mineral species owe their existence to it.**
> It was not a smooth ramp: oxygen overshot near modern levels around 2.3 Ga
> (Lomagundi–Jatuli) and crashed again at 2.1 Ga.

### 3.8 ADD `event` **Caribbean Large Igneous Province** — 95–88 Ma
> Built by the Galápagos plume on the floor of the Pacific and then rammed into the gap
> between the Americas, where it survives as the thick, buoyant crust under the Caribbean
> Sea — one of the few oceanic plateaus that escaped subduction by being too light to
> sink. Its eruption is the leading trigger for **OAE 2**.

### 3.9 ADD `event` **Hirnantian anoxia** — 445.2–443.1 Ma
Attach to the existing End-Ordovician extinction card rather than standing alone: the
extinction's second pulse *is* the spread of anoxic water back over the shelves as the ice
melted, and the app's extinction card already describes the one-two punch without naming
the mechanism.

---

## 4. ADD — cards the resource review argued for

### 4.1 ADD `region` **Permian Basin evaporite succession** (west Texas / New Mexico) · **FIG**
The Colorado Plateau Geosystems regional series in `Deep Time Maps and Resources/` walks
the basin through **Wolfcamp → Leonard → Guadalupian → Ochoan** in eight maps, ending with
the **Castile** evaporites.
> A tropical sea that slowly strangled. Through the Permian, a deep basin on Pangaea's
> western margin was progressively cut off from the open ocean by its own reefs — the
> Capitan reef complex, one of the best-exposed fossil reefs on Earth, grew around its
> rim. Once the connection narrowed enough, evaporation won: the Ochoan **Castile
> Formation** is hundreds of metres of gypsum and halite, laid down in varve-like annual
> couplets that can be counted. A restricted basin under a subtropical high is the
> standard recipe for salt, and Pangaea's margins made many of them — the **Zechstein Sea**
> of northern Europe is the same story at the same time.

### 4.2 ADD `feature-type` **Back-arc basin** · **FIG**
Named as a model gap in README §10 ("marginal basins absent or generic"). The Britannica
roll-back sequence is the mechanism.
> Behind a subduction zone, the ocean floor can pull *apart*. As an old, dense slab sinks
> it also rolls backward, dragging the trench oceanward and stretching the plate behind
> it until that plate rifts and a new spreading centre opens — a small ocean basin
> forming *inside* a convergent margin. The Sea of Japan, the Mariana Trough, the Lau
> Basin, the Andaman Sea and the Tyrrhenian are all this. It is why the western Pacific
> is a scatter of small seas and island arcs rather than a single clean margin.

### 4.3 ADD `feature-type` **Atolls and guyots — the subsidence sequence** · **FIG**
> Every volcanic island is temporary. It is built on ocean floor that cools, contracts and
> sinks as it ages, so the island rides slowly downward. If it sits in warm enough water,
> coral grows upward as fast as the island sinks: a **fringing reef** hugging the shore
> becomes a **barrier reef** with a lagoon behind it, and finally an **atoll** — a ring of
> reef around open water where a mountain used to be. Where the water is too cold or the
> subsidence too fast, the island simply drowns, and its wave-planed top survives as a
> flat-topped seamount, a **guyot**, sometimes a kilometre or more below the surface.
> Darwin worked the sequence out in 1842 from the shapes alone, before anyone knew the sea
> floor moved.

### 4.4 EDIT `label` **Pangaea Proxima** — say whose future this is
> **Append:** This is one of four published futures, not a forecast. It follows C. R.
> Scotese's Pangaea Ultima reconstruction, in which the Atlantic closes again
> (*introversion*) — chosen here because Farnsworth et al. (2024) modelled the climate on
> exactly this geometry, so the map and the temperature readout agree. The alternatives
> are **Novopangaea** (the Pacific closes instead), **Aurica** (both close) and **Amasia**
> (everything gathers over the Arctic). Beyond about 50 million years, plate motions
> cannot be projected — only reasoned about.

---

## 5. Illustrations wanted

| card | figure | status |
|---|---|---|
| PETM, EECO, MECO, MMCO, Azolla | **Cenozoic climate events on one axis**, warming above the line and drawdowns below | authored: `07-cenozoic-climate-events.svg` |
| OAE 1a / OAE 2 | **LIP → anoxia cascade** | exists: `04-lip-to-extinction-cascade.svg` |
| Great Oxidation Event | **oxygen through time**, with the Lomagundi overshoot and the crash | authored: `08-oxygen-through-time.svg` |
| Atolls and guyots | **Darwin's subsidence sequence** | authored: `09-atoll-guyot-subsidence.svg` |
| Back-arc basin | **slab roll-back opening a basin** | authored: `10-back-arc-rollback.svg` |
| Glossopteris Flora | **the five-continent distribution** that made the Gondwana argument | authored: `11-glossopteris-gondwana.svg` |
| Permian Basin | reef-rimmed basin → evaporite | not yet |
| Ediacaran assemblages | Avalon / White Sea / Nama in sequence | not yet |

---

## 6. What NOT to change

Worth recording, because an audit that only lists faults misrepresents the corpus:

- **The Pannotia supercontinent card is exemplary.** It states the case, names the
  objection (Gondwana was still assembling while Laurentia was already leaving), names the
  critics (Meert, Evans) and the defender (Scotese), and says the app treats it as
  provisional. This is the standard the other contested cards should be brought to.
- **The Early Cretaceous Cool Snap card** already says "everything about it, including
  whether it happened" is contested, and explains why it is drawn anyway. Leave it.
- **The Tonian card correctly rejects the Kaigas glaciation.** The audit's first pass
  flagged it for merely containing the word; the check now recognises refutation.
- **The glaciation date windows are well chosen** and, as noted at the top, better than the
  common convention in two cases.
