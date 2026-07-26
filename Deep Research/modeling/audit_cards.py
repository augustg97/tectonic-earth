"""Audit Tectonic Earth's card text against the Deep Research findings.

READ-ONLY. It imports the app's own data (build/features.py, eras_data.json,
life_data.json), checks it against the catalogues and models in this folder, and
writes a discrepancy register. It changes nothing.

Run from anywhere:

    ../../venv/bin/python audit_cards.py                 # print the register
    ../../venv/bin/python audit_cards.py --md out.md     # write markdown

Six families of check, each of which had to be defensible on its own before it
earned a place here - a noisy audit is worse than none:

  COVERAGE   a catalogued event that no card anywhere mentions
  DATE       a card whose age window disagrees with the catalogue
  CONTESTED  a genuinely open question stated flatly
  ANACHRON   vocabulary that postdates the card's own window
     (no grassland before ~40 Ma, no canopy before ~385 Ma, no vegetation
      before ~470 Ma, no C4 savanna before ~8 Ma)
  SUPERSEDED a claim the current literature has moved past
  ATTRIB     a discovery credited to the wrong person

Severity: HIGH = factually wrong or misleading · MED = incomplete or over-confident
· LOW = polish.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # the repo root
BUILD = os.path.join(ROOT, "build")
sys.path.insert(0, HERE)
sys.path.insert(0, BUILD)

import deeptime as dt                                   # noqa: E402


# ---------------------------------------------------------------------------
# load the app's card corpus
# ---------------------------------------------------------------------------

def load_cards():
    """{(kind, name): text} over every user-visible string the app ships."""
    import features as F
    eras = json.load(open(os.path.join(BUILD, "eras_data.json")))
    life = json.load(open(os.path.join(BUILD, "life_data.json")))

    cards = {}
    windows = {}

    for name, txt in F.DESCRIPTIONS.items():
        cards[("label", name)] = txt
    for name, txt in F.EVENT_NOTES.items():
        cards[("event", name)] = txt
    for name, phases in F.PHASES.items():
        for i, ph in enumerate(phases):
            body = ph[2] if len(ph) > 2 else ""
            cards[("phase", f"{name}[{i}]")] = body
            windows[("phase", f"{name}[{i}]")] = (ph[0], ph[1])
    for it in eras["intervals"]:
        cards[("interval", it["name"])] = " ".join(
            [it.get("summary", "")] + list(it.get("key_events", []) or []))
        windows[("interval", it["name"])] = (it["a1"], it["a0"])
    for g in eras["glaciations"]:
        cards[("glaciation", g["name"])] = " ".join(
            str(g.get(f, "")) for f in ("summary", "cause", "end", "life", "contested"))
        windows[("glaciation", g["name"])] = (g["a0"], g["a1"])
    for s in eras["supercontinents"]:
        cards[("supercontinent", s["name"])] = " ".join(
            str(s.get(f, "")) for f in ("summary", "life", "fate"))
        a = s.get("assembly") or [None, None]
        b = s.get("breakup") or [None, None]
        if a[1] is not None and b[0] is not None:
            windows[("supercontinent", s["name"])] = (a[1], b[0])
    for e in life["life"]:
        cards[("life", e["interval"])] = e.get("summary", "")
        windows[("life", e["interval"])] = (e["a0"], e["a1"])
    for b in life["biomes"]:
        nm = b.get("name") or b.get("biome") or "?"
        cards[("biome", f"{nm}@{b.get('a0','?')}")] = b.get("note", "") or b.get("summary", "")
        if b.get("a0") is not None:
            windows[("biome", f"{nm}@{b.get('a0','?')}")] = (b["a0"], b.get("a1", b["a0"]))

    # The mass-extinction cards are an inline const in web/index.html, not a data
    # file. Omitting them made the coverage check report the K-Pg as uncovered, which
    # is exactly the kind of false negative that discredits an audit.
    idx = os.path.join(ROOT, "web", "index.html")
    if os.path.exists(idx):
        html = open(idx).read()
        i = html.find("MASS_EXTINCTIONS")
        if i > 0:
            blk = html[i: html.find("\n];", i)]
            for m in re.finditer(r'name:"([^"]+)"', blk):
                nm = m.group(1)
                seg = blk[m.end(): m.end() + 4000]
                cards[("extinction-card", nm)] = re.sub(r"<[^>]+>", " ", seg)
            his = [float(x) for x in re.findall(r"hi:\s*(-?[\d.]+)", blk)]
            los = [float(x) for x in re.findall(r"lo:\s*(-?[\d.]+)", blk)]
            for (k, nm) in list(cards):
                if k == "extinction-card" and his and los:
                    windows[(k, nm)] = (max(his), min(los))

    # label windows from features.LABELS  (type, name, lon, lat, a0, a1)
    for row in F.LABELS:
        if len(row) >= 6:
            windows.setdefault(("label", row[1]), (max(row[4], row[5]), min(row[4], row[5])))
    return cards, windows, F


# ---------------------------------------------------------------------------
# findings
# ---------------------------------------------------------------------------

class Finding:
    __slots__ = ("check", "severity", "kind", "name", "detail", "evidence", "fix")

    def __init__(self, check, severity, kind, name, detail, evidence, fix=""):
        self.check, self.severity = check, severity
        self.kind, self.name = kind, name
        self.detail, self.evidence, self.fix = detail, evidence, fix

    def __repr__(self):
        return f"[{self.severity}] {self.check} {self.kind}:{self.name} — {self.detail}"


SEV_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2}


# ---------------------------------------------------------------------------
# CHECK 1 — coverage: catalogued events nothing mentions
# ---------------------------------------------------------------------------

# Alternate spellings the app may legitimately use instead of the catalogue name.
ALIASES = {
    "End-Cretaceous (K-Pg)": ("K-Pg", "K/T", "End-Cretaceous", "Cretaceous-Paleogene",
                             "Cretaceous–Paleogene", "Chicxulub"),
    "End-Permian": ("Permian-Triassic", "Permian–Triassic", "Great Dying", "end-Permian"),
    "End-Triassic": ("Triassic-Jurassic", "Triassic–Jurassic", "end-Triassic"),
    "End-Ordovician": ("Ordovician-Silurian", "Ordovician–Silurian", "Hirnantian"),
    "Late Palaeozoic Ice Age": ("Late Paleozoic", "Karoo Ice Age", "LPIA"),
    "OAE 2 (Bonarelli)": ("Bonarelli", "OAE 2", "Cenomanian-Turonian"),
    "OAE 1a (Selli)": ("Selli", "OAE 1a"),
    "T-OAE (Toarcian)": ("Toarcian",),
    "North Atlantic Igneous Province": ("North Atlantic Igneous", "NAIP",
                                        "Brito-Arctic", "Iceland plume"),
    "Columbia River Basalt": ("Columbia River",),
    "P-Tr deoxygenation": ("Permian-Triassic", "Permian–Triassic"),
    "Cretaceous Thermal Maximum": ("Cretaceous Thermal", "Turonian"),
    "Late Cenozoic Ice Age": ("Late Cenozoic", "Quaternary glaciation"),
    "Great Oxidation Event": ("Great Oxidation", "Great Oxygenation"),
    "Holocene / Anthropocene": ("Holocene", "Anthropocene"),
    "Carboniferous rainforest collapse": ("rainforest collapse",),
    "Devonian land-plant weathering": ("land plants", "deep roots", "rooted"),
    "Himalayan uplift weathering": ("Himalaya",),
    "End-Ediacaran": ("Ediacaran biota", "Ediacaran extinction",
                      "end-Ediacaran", "Ediacaran turnover"),
    "Baykonurian": ("Baykonur",),
    "Early Cretaceous cool snap": ("Early Cretaceous Cool Snap",),
    "Late Devonian glaciation": ("Late Devonian Glaciation",),
    "Caribbean LIP": ("Caribbean Large Igneous", "Caribbean Plateau",
                      "Caribbean-Colombian"),
}

# Events we deliberately do not expect a card for.
COVERAGE_EXEMPT = {"Pongola", "Huronian", "SPICE", "Ireviken", "Lau", "ETM-2 (ELMO)"}


def check_coverage(cards):
    corpus = " || ".join(f"{k[1]} :: {v}" for k, v in cards.items())
    out = []
    for kind, events in dt._CATALOGUES.items():
        for e in events:
            if e.name in COVERAGE_EXEMPT:
                continue
            if e.base > 1000 and kind != "drawdown":
                continue                                   # outside the app's window
            names = (e.name,) + ALIASES.get(e.name, ())
            if any(re.search(re.escape(n), corpus, re.I) for n in names):
                continue
            sev = "MED" if kind in ("lip", "glaciation", "extinction") else "LOW"
            if kind in ("anoxia", "hyperthermal", "drawdown") and e.confidence == "good":
                sev = "MED"
            out.append(Finding(
                "COVERAGE", sev, kind, e.name,
                f"no card anywhere mentions this {kind} ({e.base:g}-{e.top:g} Ma)",
                e.note[:180] or "see deeptime.py",
                f"add to {'features.EVENT_NOTES' if kind=='lip' else 'a card or a new climate-events panel'}"))
    return out


# ---------------------------------------------------------------------------
# CHECK 2 — dates: app windows vs catalogue windows
# ---------------------------------------------------------------------------

WINDOW_MAP = {          # app card name -> catalogue event name
    "Sturtian Glaciation": "Sturtian",
    "Marinoan Glaciation": "Marinoan",
    "Gaskiers Glaciation": "Gaskiers",
    "Late Devonian Glaciation": "Late Devonian glaciation",
    "Late Palaeozoic Ice Age": "Late Palaeozoic Ice Age",
    "Late Cenozoic Ice Age": "Late Cenozoic Ice Age",
    "Early Cretaceous Cool Snap": "Early Cretaceous cool snap",
}
TOL = 5.0               # Ma; the app's keyframe spacing, so anything under this is noise


def check_dates(windows):
    byname = {e.name: e for lst in dt._CATALOGUES.values() for e in lst}
    out = []
    for (kind, name), (a0, a1) in windows.items():
        tgt = WINDOW_MAP.get(name)
        if not tgt or tgt not in byname:
            continue
        e = byname[tgt]
        base, top = max(a0, a1), min(a0, a1)
        db, dtp = base - e.base, top - e.top
        if abs(db) <= TOL and abs(dtp) <= TOL:
            continue
        out.append(Finding(
            "DATE", "MED" if max(abs(db), abs(dtp)) < 20 else "HIGH", kind, name,
            f"app window {base:g}-{top:g} Ma vs catalogue {e.base:g}-{e.top:g} "
            f"(base {db:+.1f}, top {dtp:+.1f})",
            e.note[:160] or "deeptime.py",
            f"set a0={e.base:g}, a1={e.top:g}"))
    return out


# ---------------------------------------------------------------------------
# CHECK 3 — contested claims stated flatly
# ---------------------------------------------------------------------------

HEDGES = r"(disput|contest|debat|propos|may |might |possibl|probabl|argu|uncertain|" \
         r"not settled|open question|thought to|interpret|one hypothes|claim|" \
         r"provisional|permissive|some (?:authors|reconstructions)|unclear|" \
         r"is not (?:agreed|settled)|no consensus|questioned)"

CONTESTED = [
    ("Rodinia configuration", r"Rodinia[^.]{0,120}?\b(?:next to|adjacent|abutt|against|"
     r"faced|opposite|lay (?:along|beside)|on the (?:western|eastern) (?:margin|side)|"
     r"between .{0,30} and )",
     "The configuration is disputed - SWEAT / AUSWUS / AUSMEX / Missing-Link / revised "
     "Missing-Link differ on what sat off Laurentia's present-western margin. Naming "
     "Rodinia is fine; asserting an adjacency is the part that needs a hedge.",
     "research/01-plate-tectonics/01-supercontinent-cycle.md §3", "MED"),
    ("Hawaii-Emperor bend", r"Emperor Seamounts|Hawaii.{0,40}bend|bend.{0,40}Hawaii",
     "The bend is now widely read as PLUME motion rather than a change in Pacific plate "
     "direction; hotspots are demonstrably not fixed before ~90 Ma.",
     "research/03-oceanic-crust/01-ocean-basins-crust-lips-and-plumes.md §4", "MED"),
    ("Panama closure", r"Isthmus of Panama|Panama",
     "The shoaling history is actively debated back to ~10 Ma; 2.7 Ma is the full "
     "interchange, not an undisputed closure date.",
     "research/06-paleobiology/01-biogeographic-provinces-through-time.md §2", "LOW"),
    ("Carboniferous endemism", r"rainforest collapse",
     "The classic 'rainforest islands drove endemism' story is contested — a 2018 study "
     "finds INCREASED cosmopolitanism.",
     "research/06-paleobiology/01-biogeographic-provinces-through-time.md §3", "MED"),
    ("giant arthropod oxygen", r"Arthropleura|Meganeura|giant (?:insect|arthropod|dragonfl)",
     "Both taxa are now found AFTER the rainforest collapse and were probably "
     "forest-independent, so the high-O2 -> giants -> collapse chain is a hypothesis.",
     "research/05-atmosphere-ocean-chemistry/01-atmosphere-oxygen-and-ocean-chemistry.md §1",
     "MED"),
]


def check_contested(cards):
    out = []
    for topic, pat, why, ev, sev in CONTESTED:
        for (kind, name), txt in cards.items():
            if not re.search(pat, txt, re.I):
                continue
            if re.search(HEDGES, txt, re.I):
                continue
            out.append(Finding(
                "CONTESTED", sev, kind, name,
                f"mentions {topic} without hedging", why, ev))
    return out


# ---------------------------------------------------------------------------
# CHECK 4 — anachronistic vocabulary
# ---------------------------------------------------------------------------

GATES = [
    (r"\bgrass(?:es|land|y)?\b|\bsavann?a\b|\bsteppe\b|\bprairie\b", 40.0,
     "grasses become ecologically important only from ~40 Ma"),
    (r"\bC4\b", 8.0, "C4 grasslands expand only from ~8 Ma"),
    (r"\bforest\b|\bcanopy\b|\bwoodland\b|\btree[s]?\b|\btimber\b", 385.0,
     "no tree-form plant before ~385 Ma (Wattieza); Archaeopteris forests by ~375"),
    (r"\bvegetat|\bplant[s]?\b|\bflora\b|\bmeadow", 470.0,
     "earliest embryophyte spores are Middle Ordovician, ~470 Ma"),
    (r"\bflower|\bangiosperm|\bblossom", 135.0,
     "angiosperms originate and diversify from ~130 Ma"),
]
# words that legitimately appear in a pre-gate card while DENYING the thing
NEGATED = r"(no |not |never |before |absen|lack|without |bare |first |earliest |would not|" \
          r"had yet|yet to|nothing |pre-|until )"


def check_anachronisms(cards, windows):
    out = []
    for key, txt in cards.items():
        w = windows.get(key)
        if not w:
            continue
        base, young = max(w), min(w)
        for pat, gate, why in GATES:
            # Only an anachronism if the ENTIRE window predates the innovation. An
            # interval card spanning 393-382 Ma may legitimately say "trees": Wattieza
            # appears at ~385, inside it.
            if young <= gate:
                continue
            m = re.search(pat, txt, re.I)
            if not m:
                continue
            ctx = txt[max(0, m.start() - 70): m.start() + 40]
            if re.search(NEGATED, ctx, re.I):
                continue
            out.append(Finding(
                "ANACHRON", "HIGH" if base > gate * 1.5 else "MED", key[0], key[1],
                f'says "{m.group(0)}" but its whole window is {base:g}-{young:g} Ma',
                why,
                "reword, or narrow the window"))
    return out


# ---------------------------------------------------------------------------
# CHECK 5 / 6 — superseded claims and misattribution
# ---------------------------------------------------------------------------

TEXT_RULES = [
    ("SUPERSEDED", "LOW", r"35\s*%.{0,40}oxygen|oxygen.{0,40}35\s*%",
     "the Permo-Carboniferous O2 peak is best given as ~30%; 35% is the high end of older "
     "GEOCARBSULF runs and Krause et al. (2022) is the current review",
     "research/05-atmosphere-ocean-chemistry/01-atmosphere-oxygen-and-ocean-chemistry.md §1"),
    ("SUPERSEDED", "MED", r"Kaigas",
     "the ~750 Ma Kaigas glaciation is rejected in current literature; its type deposits "
     "are rift-scarp debris, not till", "project memory, 2026-07-18 audit"),
    ("SUPERSEDED", "LOW", r"single (?:long )?(?:freeze|glaciation).{0,60}Cryogenian|"
                          r"Cryogenian.{0,60}single (?:long )?(?:freeze|glaciation)",
     "the Cryogenian is TWO snowballs with a genuine non-glacial interlude",
     "research/04-paleoclimate/01-phanerozoic-climate-record.md §3"),
    ("ATTRIB", "LOW", r"Wegener'?s? (?:original )?argument",
     "Glossopteris was Eduard SUESS's evidence for Gondwana (1885); Wegener later used it "
     "for drift. Crediting Wegener alone drops the origin of the name Gondwana itself",
     "research/06-paleobiology/…§3"),
    ("SUPERSEDED", "MED", r"anoxi\w*.{0,60}(green|purple|milky|red) (?:ocean|sea|water)|"
                          r"(green|purple|milky) (?:ocean|sea).{0,60}anoxi",
     "anoxia is SUBSURFACE — the Black Sea is euxinic below ~100 m and looks normal at the "
     "surface", "research/05-atmosphere-ocean-chemistry/…§2"),
]


REFUTES = r"(rejected|no longer|once[- ]cited|discredit|not accepted|is not a|" \
          r"disput|withdrawn|abandoned|turned out|now (?:read|thought|known)|" \
          r"formerly|superseded|debunk|not till|not a snowball|has been)"


def check_text_rules(cards):
    out = []
    for check, sev, pat, why, ev in TEXT_RULES:
        for (kind, name), txt in cards.items():
            m = re.search(pat, txt, re.I)
            if not m:
                continue
            # A card that REFUTES the superseded claim is doing the right thing.
            ctx = txt[max(0, m.start() - 120): m.end() + 160]
            if re.search(REFUTES, ctx, re.I):
                continue
            out.append(Finding(check, sev, kind, name,
                               f'"{txt[max(0,m.start()-30):m.end()+30].strip()}"', why, ev))
    return out


# ---------------------------------------------------------------------------

def run():
    cards, windows, F = load_cards()
    findings = []
    findings += check_coverage(cards)
    findings += check_dates(windows)
    findings += check_contested(cards)
    findings += check_anachronisms(cards, windows)
    findings += check_text_rules(cards)
    findings.sort(key=lambda f: (SEV_ORDER[f.severity], f.check, f.kind, f.name))
    return cards, findings


def to_markdown(cards, findings):
    n = len(cards)
    chars = sum(len(v) for v in cards.values())
    lines = [
        "# Card-text audit register",
        "",
        f"Generated by `modeling/audit_cards.py` over **{n} cards / {chars:,} characters** "
        "of user-visible text in `features.DESCRIPTIONS`, `features.EVENT_NOTES`, "
        "`features.PHASES`, `eras_data.json` (intervals, glaciations, supercontinents) and "
        "`life_data.json`.",
        "",
        "Read-only: the audit changes nothing. Re-run it after any card edit.",
        "",
        f"**{len(findings)} findings** — "
        + ", ".join(f"{s} {sum(1 for f in findings if f.severity == s)}"
                    for s in ("HIGH", "MED", "LOW")),
        "",
    ]
    for sev in ("HIGH", "MED", "LOW"):
        rows = [f for f in findings if f.severity == sev]
        if not rows:
            continue
        lines += [f"## {sev} ({len(rows)})", "",
                  "| check | card | finding | why | fix |", "|---|---|---|---|---|"]
        for f in rows:
            lines.append(f"| {f.check} | `{f.kind}` **{f.name}** | {f.detail} | "
                         f"{f.evidence} | {f.fix} |")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    cards, findings = run()
    if "--md" in sys.argv:
        path = sys.argv[sys.argv.index("--md") + 1]
        with open(path, "w") as fh:
            fh.write(to_markdown(cards, findings))
        print(f"wrote {path}: {len(findings)} findings over {len(cards)} cards")
    else:
        print(f"{len(cards)} cards, "
              f"{sum(len(v) for v in cards.values()):,} characters of card text")
        for sev in ("HIGH", "MED", "LOW"):
            rows = [f for f in findings if f.severity == sev]
            print(f"\n===== {sev} ({len(rows)}) =====")
            for f in rows:
                print(f"  {f.check:10s} {f.kind}:{f.name}")
                print(f"             {f.detail}")
