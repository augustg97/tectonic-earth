"""Replay every biota card the app can show, and check it against the registry.

READ-ONLY (it writes only under build/verify/, which is gitignored). It reads
what SHIPS -- web/life.json and web/labels.json -- not what the build meant to
ship, so a stale life.json, a run-length bug or an age-mapping slip shows up
here as the reader would meet it.

What it holds the cards to. Every number is printed whether or not it is zero:
a check that speaks only when it fails cannot be trended and is unreadable
exactly when it passes.

  registry invalid        an entry that breaks the schema
  unregistered on cards   a name the app shows that the registry does not know,
                          so nothing vouches for its age, place or drawing
  no drawing              a taxon whose form resolves to no icon. There is no
                          realm fallback any more, so this is a hole, not a lizard
  form findings           the classification says the form is wrong (Ursus as a
                          canid). This is the check that catches a wrong icon
                          without anyone looking at it
  anachronisms            a taxon on a card at an age it was not alive
  misplaced               a taxon on a card whose crust it never lived on
  (--placements AGE       prints taxon -> labels for that age: the review that
                          finds what the rules cannot -- read it)
  curated conflicts       a curated list claims a taxon for a label its registry
                          range excludes: one of the two is wrong
  land cards, no fauna    ) after 385 Ma both exist everywhere there is land,
  land cards, no flora    ) so a card showing only one is the reported defect
  thin cards              fewer than four organisms
  homeless labels         a card label with no home crust: no local biota possible
  parent-form drawings    declared approximations (a brontothere as a rhino)

    python3 audit_biota.py              the gate
    python3 audit_biota.py --ledger     also write build/verify/biota_ledger.md
    python3 audit_biota.py --sheets     also write the contact sheets (HTML)
    python3 audit_biota.py --coverage   where the registry is thin, by crust and era
"""
import collections
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import biota                                                # noqa: E402
from biota_forms import FORMS                               # noqa: E402

WEB = os.path.join(HERE, "..", "web")
VERIFY = os.path.join(HERE, "verify")

ERAS = [(0, 0, "Present"), (0.01, 2.6, "Quaternary"), (2.6, 23, "Neogene"),
        (23, 66, "Palaeogene"), (66, 145, "Cretaceous"), (145, 201, "Jurassic"),
        (201, 252, "Triassic"), (252, 299, "Permian"), (299, 359, "Carboniferous"),
        (359, 419, "Devonian"), (419, 444, "Silurian"), (444, 485, "Ordovician"),
        (485, 539, "Cambrian"), (539, 635, "Ediacaran"), (635, 1000, "Tonian-Cryogenian")]


def load_shipped():
    with open(os.path.join(WEB, "life.json")) as f:
        life = json.load(f)
    with open(os.path.join(WEB, "labels.json")) as f:
        labels = json.load(f)
    return life, labels


def replay(life, labels):
    """Yield (label, app_age, biota_age, tier, prov_id, groups[(key,[taxon recs])])."""
    table = life.get("taxa") or []
    cards = life.get("cards") or {}
    by = collections.defaultdict(list)
    for l in labels:
        by[l["n"]].append(l)
    for name, card in cards.items():
        if name not in by:
            continue
        for run in card["r"]:
            a_lo, a_hi, tier, pid, groups = run[:5]
            for a in range(int(a_lo), int(a_hi) + 1):
                # a name can be two labels with two windows (North China)
                lab = next((l for l in by[name] if a in biota.app_ages(l)), by[name][0])
                yield (lab, a, biota.biota_age(lab, a), tier, pid,
                       [(k, [table[i] for i in ids]) for k, ids in groups], run)


def audit(write_ledger=False, write_sheets=False):
    import features                                          # noqa: PLC0415
    life, labels = load_shipped()
    reg = biota.load()["taxa"]
    out = collections.OrderedDict()
    detail = collections.defaultdict(list)

    out["registry taxa"] = len(reg)
    bad = biota.validate(reg)
    out["registry invalid entries"] = len(bad)
    detail["registry invalid entries"] = bad
    rev = biota.review(reg)
    out["form findings"] = sum(1 for r in rev if r[0] == "FORM")
    detail["form findings"] = [f"{n}: {m}" for s, n, m in rev if s == "FORM"]
    out["range findings vs PBDB"] = sum(1 for r in rev if r[0].startswith("RANGE"))
    detail["range findings vs PBDB"] = [f"{n}: {m}" for s, n, m in rev
                                        if s.startswith("RANGE")]

    icons = life.get("icons") or {}
    table = life.get("taxa") or []
    shown = {t["n"] for t in table}
    for e in life.get("life", []):
        shown.update(t["n"] for t in e.get("taxa", []))
    unreg = sorted(n for n in shown if biota.get(n) is None)
    out["unregistered names on cards"] = len(unreg)
    detail["unregistered names on cards"] = unreg
    nodraw = sorted(t["n"] for t in table if not t.get("ic") or t["ic"] not in icons)
    for e in life.get("life", []):
        nodraw += [t["n"] for t in e.get("taxa", []) if not t.get("ic") or t["ic"] not in icons]
    nodraw = sorted(set(nodraw))
    out["taxa with no drawing"] = len(nodraw)
    detail["taxa with no drawing"] = nodraw

    # how each shown taxon gets its drawing
    how = collections.Counter()
    parents = []
    with open(os.path.join(HERE, "life_icons.json")) as f:
        all_icons = json.load(f)
    for n in sorted(shown):
        if biota.get(n) is None:
            continue
        _ic, h = biota.icon_for(n, all_icons)
        how[h] += 1
        if h == "parent":
            parents.append(f"{n} [{biota.get(n)['form']}]")
    out["drawn from own silhouette"] = how["own"] + how["rep"]
    out["drawn from form icon"] = how["form"]
    out["drawn from a PARENT form (declared approximation)"] = how["parent"]
    detail["drawn from a PARENT form (declared approximation)"] = parents

    ana, mis, conf = set(), set(), set()
    nofauna, noflora, thin = [], [], []
    homeless = set()
    lists = collections.Counter()
    list_labels = collections.defaultdict(set)
    tiers = collections.Counter()
    n_cards = 0
    ledger = collections.OrderedDict()
    home_cache = {}
    with open(os.path.join(HERE, "life_data.json")) as f:
        _ld = json.load(f)
    curated = _ld.get("region_taxa") or {}
    # A `sparse` span is the declaration that the honest list here is short, and
    # the card prints its reason. Those label-ages are not held to the minimums.
    sparse = _ld.get("sparse") or {}

    def is_sparse(name, age):
        return any(min(r["a0"], r["a1"]) - 1e-9 <= age <= max(r["a0"], r["a1"]) + 1e-9
                   for r in sparse.get(name, ()))
    out_of_box = set()
    for lab, a, ba, tier, pid, groups, run in replay(life, labels):
        n_cards += 1
        tiers[tier] += 1
        name = lab["n"]
        hk = (name, ba) if isinstance((biota.LABEL_HOME.get(name) or [None])[0], dict) else name
        if hk not in home_cache:
            home_cache[hk] = biota.label_home(lab, features, ba)
        home = home_cache[hk]
        if home is None:
            homeless.add(name)
        marine = biota.is_marine(lab, ba)
        span = biota.curated_at(curated.get(name), ba)
        cur_names = {(t[0] if isinstance(t, (list, tuple)) else t["name"])
                     for t in (span or {}).get("taxa", [])}
        own = [(k, ts) for k, ts in groups if not k.startswith("shelf-")]
        flat = [t for _k, ts in groups for t in ts]
        for t in flat:
            e = biota.get(t["n"])
            if e is None:
                continue
            if not biota.alive(e, ba):
                ana.add((name, a, t["n"], f"{e['fad']}-{e['lad']} Ma"))
            is_cur = t["n"] in cur_names or any(k in cur_names for k in e.get("aka", ()))
            sea_key = any(k.startswith(("sea-", "shelf-")) and t in ts for k, ts in groups)
            if home is not None and not biota.at_home(e, home, ba, ice=not is_cur,
                                                      sea_card=(marine or sea_key) if not is_cur else None):
                # a curated taxon whose range NEVER includes this crust is a data
                # disagreement to settle; one that is merely early or late here
                # should have been withheld by the composer, so it is misplaced
                if tier in ("c", "x") and not biota._ever_home(e, home):
                    conf.add((name, t["n"]))
                else:
                    mis.add((name, t["n"]))
            # inside the right region and outside the taxon's own range within it
            if not is_cur and not biota.in_reach(e, lab, ba):
                out_of_box.add((name, t["n"]))
        n_fa = sum(len(ts) for k, ts in own if k == "fauna")
        n_fl = sum(len(ts) for k, ts in own if k == "flora")
        if not marine and ba <= biota.SHELF_TOO_BEFORE and not is_sparse(name, ba):
            if n_fa == 0:
                nofauna.append((name, a))
            if n_fl == 0:
                noflora.append((name, a))
        if len(flat) < 4 and (marine or ba <= biota.NO_LAND_LIFE_BEFORE) \
                and not is_sparse(name, ba):
            thin.append((name, a, len(flat)))
        key = tuple(t["n"] for t in flat)
        lists[key] += 1
        list_labels[key].add(name)
        ledger.setdefault(name, []).append((a, tier, pid, groups))

    out["card-ages replayed"] = n_cards
    out["anachronisms"] = len(ana)
    detail["anachronisms"] = [f"{l} at {a} Ma lists {n} ({r})" for l, a, n, r in sorted(ana)][:60]
    out["misplaced taxa"] = len(mis)
    detail["misplaced taxa"] = [f"{n} on {l}" for l, n in sorted(mis)][:60]
    out["taxa outside their own range within a region"] = len(out_of_box)
    detail["taxa outside their own range within a region"] = \
        [f"{n} on {l}" for l, n in sorted(out_of_box)][:60]
    out["curated-vs-range conflicts"] = len(conf)
    detail["curated-vs-range conflicts"] = [f"{n} on {l}" for l, n in sorted(conf)][:80]
    out["land card-ages with no fauna"] = len(nofauna)
    detail["land card-ages with no fauna"] = _runs(nofauna)
    out["land card-ages with no flora"] = len(noflora)
    detail["land card-ages with no flora"] = _runs(noflora)
    out["thin card-ages (under 4 organisms)"] = len(thin)
    detail["thin card-ages (under 4 organisms)"] = _runs([(n, a) for n, a, _c in thin])
    out["homeless labels"] = len(homeless)
    detail["homeless labels"] = sorted(homeless)

    # labels that SHOULD carry a card and carry none at some age
    gaps = []
    cards = life.get("cards") or {}
    for lab in labels:
        if lab["t"] not in biota.CARD_TYPES:
            continue
        ages = biota.app_ages(lab)
        have = set()
        for run in (cards.get(lab["n"]) or {}).get("r", []):
            have.update(range(int(run[0]), int(run[1]) + 1))
        miss = [a for a in ages if a not in have
                and (lab["t"] in biota.MARINE_TYPES or a <= biota.NO_LAND_LIFE_BEFORE)]
        gaps += [(lab["n"], a) for a in miss]
    out["card-ages with NO biota at all"] = len(gaps)
    detail["card-ages with NO biota at all"] = _runs(gaps)

    # The globe draws these labels under water. A present-day label whose own
    # ground is deep sea on the shipped DEM, and whose card still lists land
    # life, is the card contradicting the map it sits on. The present is the one
    # age at which the DEM is simply the Earth, so that is where it is checked;
    # biota.SUBMERGED carries the dates for the past.
    drowned = []
    try:
        import statistics                                    # noqa: PLC0415
        import audit_labels as AL                             # noqa: PLC0415
        for lab in labels:
            if lab["t"] not in biota.CARD_TYPES or lab["t"] in biota.MARINE_TYPES \
                    or lab["t"] == "lake" or min(lab["a0"], lab["a1"]) > 0.011 \
                    or lab["n"] in biota.DROWNED_LAND_OK:
                continue
            x, y = AL.track_pos(lab.get("tr"), lab["lon"], lab["lat"], 0)
            es = [AL.elev_at(0, x + dx, y + dy)
                  for dx, dy in ((0, 0), (.4, 0), (-.4, 0), (0, .4), (0, -.4))]
            es = [v for v in es if v is not None]
            if not es or statistics.median(es) > -200:
                continue
            run0 = next((r for r in (cards.get(lab["n"]) or {}).get("r", []) if r[0] <= 0), None)
            if run0 and any(not k.startswith(("sea-", "shelf-")) for k, _ids in run0[4]):
                drowned.append(f"{lab['n']} ({statistics.median(es):.0f} m)")
    except Exception as ex:                                  # noqa: BLE001
        drowned.append(f"DEM check could not run: {ex}")
    out["land cards on drowned ground"] = len(drowned)
    detail["land cards on drowned ground"] = drowned

    out["distinct lists"] = len(lists)
    if lists:
        worst = max(list_labels.items(), key=lambda kv: len(kv[1]))
        out["most labels sharing one identical list"] = len(worst[1])
        detail["most labels sharing one identical list"] = [
            ", ".join(worst[0]), "on: " + ", ".join(sorted(worst[1])[:14])]
    out["tiers"] = dict(tiers)

    if write_ledger:
        _write_ledger(ledger, life)
    if write_sheets:
        _write_sheets(life, all_icons)
    return out, detail


def _runs(pairs):
    """[(label, age)] -> ['Label: 12-40, 55 Ma', ...] so a finding is readable."""
    by = collections.defaultdict(list)
    for n, a in pairs:
        by[n].append(a)
    rows = []
    for n, ages in sorted(by.items(), key=lambda kv: -len(kv[1])):
        ages = sorted(set(ages))
        spans, s, p = [], ages[0], ages[0]
        for a in ages[1:]:
            if a != p + 1:
                spans.append((s, p))
                s = a
            p = a
        spans.append((s, p))
        rows.append(f"{n}: " + ", ".join(f"{x}" if x == y else f"{x}-{y}" for x, y in spans)
                    + " Ma")
    return rows[:60]


def _write_ledger(ledger, life):
    os.makedirs(VERIFY, exist_ok=True)
    prov = life.get("provinces") or {}
    fn = os.path.join(VERIFY, "biota_ledger.md")
    with open(fn, "w") as f:
        f.write("# Biota ledger\n\nEvery card, every run, exactly as shipped. "
                "Generated by build/audit_biota.py --ledger.\n")
        for name, rows in ledger.items():
            f.write(f"\n## {name}\n\n")
            last = None
            for a, tier, pid, groups in rows:
                key = (tier, pid, tuple((k, tuple(t["n"] for t in ts)) for k, ts in groups))
                if last and last[0] == key:
                    last[2] = a
                    continue
                if last:
                    _ledger_row(f, last, prov)
                last = [key, a, a]
            if last:
                _ledger_row(f, last, prov)
    print(f"  ledger -> {os.path.relpath(fn, HERE)}")


def _ledger_row(f, last, prov):
    (tier, pid, groups), a0, a1 = last
    p = (prov.get(str(pid)) or prov.get(pid) or {}).get("n", "") if pid is not None else ""
    span = f"{a0}" if a0 == a1 else f"{a0}-{a1}"
    f.write(f"- **{span} Ma** [{tier}] {p}\n")
    for k, names in groups:
        f.write(f"  - {k}: {', '.join(names)}\n")


def _write_sheets(life, all_icons):
    """Contact sheets: every drawing beside every name that uses it.

    The test is the one the icon work has always used -- cover the caption, name
    the group -- and the sheet is laid out to make that a two-minute scan: one
    block per FORM, the form's own drawing first, then each member taxon with
    the drawing it actually gets and how it got it.
    """
    os.makedirs(VERIFY, exist_ok=True)
    reg = biota.load()["taxa"]
    shown = {t["n"] for t in life.get("taxa") or []}
    for e in life.get("life", []):
        shown.update(t["n"] for t in e.get("taxa", []))
    by_form = collections.defaultdict(list)
    for n in sorted(shown):
        e = biota.get(n)
        if e:
            by_form[e["form"]].append(e)
    css = ("body{background:#0d131a;color:#cfd9e6;font:12px -apple-system,Helvetica,sans-serif;"
           "margin:14px}h2{font-size:13px;margin:16px 0 6px;color:#eed6a6;border-top:1px solid "
           "#2a3644;padding-top:8px}.g{display:flex;flex-wrap:wrap;gap:8px}.c{width:118px}"
           ".i{--ko:#161d25;width:92px;height:62px;border-radius:6px;background:rgba(150,190,120,.13);"
           "border:1px solid #2a3644;color:#c2debb;display:flex;align-items:center;"
           "justify-content:center}.i svg{width:88px;height:58px;fill:currentColor;"
           "stroke-linecap:round;stroke-linejoin:round}.n{font-size:10px;line-height:1.25;"
           "margin-top:3px}.h{font-size:9px;color:#7d8fa3}.parent .i{border-color:#e0764a}"
           ".form .i{background:rgba(226,178,90,.13);color:#eed6a6}")
    forms = sorted(by_form, key=lambda k: (FORMS[k]["kind"], k))
    per = 40
    pages = [forms[i:i + per] for i in range(0, len(forms), per)]
    for pi, page in enumerate(pages):
        rows = []
        for form in page:
            fk = FORMS[form]["icon"] or form
            rows.append(f"<h2>{html.escape(form)} &mdash; {html.escape(FORMS[form]['desc'])} "
                        f"<span class=h>({FORMS[form]['kind']})</span></h2><div class=g>")
            rows.append(f"<div class='c form'><div class=i><svg viewBox='0 0 64 40'>"
                        f"{all_icons.get(fk, '')}</svg></div><div class=n>FORM ICON"
                        f"<div class=h>{html.escape(fk)}{'' if fk in all_icons else ' (MISSING)'}"
                        f"</div></div></div>")
            for e in by_form[form]:
                ic, how = biota.icon_for(e["n"], all_icons)
                rows.append(f"<div class='c {how or ''}'><div class=i><svg viewBox='0 0 64 40'>"
                            f"{all_icons.get(ic or '', '')}</svg></div><div class=n>"
                            f"{html.escape(e['n'])}<div class=h>{how}: {html.escape(ic or 'NONE')}"
                            f"</div></div></div>")
            rows.append("</div>")
        fn = os.path.join(VERIFY, f"biota_sheet_{pi + 1:02d}.html")
        with open(fn, "w") as f:
            f.write(f"<!doctype html><meta charset=utf-8><style>{css}</style>" + "".join(rows))
    print(f"  contact sheets -> build/verify/biota_sheet_01..{len(pages):02d}.html")


def coverage():
    """How many fauna and flora the registry can offer each crust in each era.

    This is the authoring worklist: a cell with two animals in it is a card
    that will show the same two animals on every label in that region for the
    whole period.
    """
    reg = biota.load()["taxa"]
    print("registry depth by home crust and era: fauna/flora available "
          "(land+air+fresh), then marine fauna\n")
    codes = list(biota.LAND_CODES)
    print("era".ljust(18) + "".join(c.rjust(7) for c in codes))
    thin = []
    for lo, hi, era in ERAS:
        mid = (lo + hi) / 2.0
        row_l, row_m = [], []
        for c in codes:
            fa = fl = ma = 0
            for e in reg.values():
                if e.get("assemblage") or not biota.alive(e, mid):
                    continue
                if not biota.at_home(e, {c}, mid):
                    continue
                sec = biota._section(e)
                if e["realm"] == "sea":
                    ma += sec == "fauna"
                elif sec == "fauna":
                    fa += 1
                elif sec == "flora":
                    fl += 1
            row_l.append(f"{fa}/{fl}")
            row_m.append(str(ma))
            if mid <= 385 and (fa < 4 or fl < 4):
                thin.append((era, c, fa, fl))
        print(era.ljust(18) + "".join(x.rjust(7) for x in row_l))
        print("  marine".ljust(18) + "".join(x.rjust(7) for x in row_m))
    print(f"\nthin land cells (under 4 fauna or 4 flora, since the Devonian): {len(thin)}")
    return thin


def placements(age):
    """taxon -> the labels it lands on at `age`, for every taxon the COMPOSER chose
    (curated entries are an author's statement about that place and are left out).

    This listing, read by eye, is what found alligators on the Great Lakes, Amazon
    river dolphins in Lake Titicaca and sequoias on the Gulf of California: each
    was inside its region code, so no rule objected. Reasoning about the filter
    found none of them. Run it at a few ages after any large registry change.
    """
    life, labels = load_shipped()
    with open(os.path.join(HERE, "life_data.json")) as f:
        curated = json.load(f).get("region_taxa") or {}
    use = collections.defaultdict(list)
    for lab, a, ba, _tier, _pid, groups, _run in replay(life, labels):
        if a != int(round(age)):
            continue
        span = biota.curated_at(curated.get(lab["n"]), ba)
        cur = {(t[0] if isinstance(t, (list, tuple)) else t["name"])
               for t in (span or {}).get("taxa", [])}
        plat = biota.lat_at(lab, ba)
        for _k, ts in groups:
            for t in ts:
                if t["n"] not in cur:
                    use[t["n"]].append(lab["n"] + (f"({plat:.0f})" if plat is not None else ""))
    print(f"{len(use)} composer-chosen taxa on cards at {age:g} Ma  --  label(palaeolatitude)")
    for n, v in sorted(use.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"{n} [{len(v)}]: " + ", ".join(v))
    return 0


def main(argv):
    if "--placements" in argv:
        i = argv.index("--placements")
        return placements(float(argv[i + 1]) if len(argv) > i + 1 else 0.0)
    if "--coverage" in argv:
        coverage()
        return 0
    out, detail = audit("--ledger" in argv, "--sheets" in argv)
    verbose = "-v" in argv or "--verbose" in argv
    w = max(len(k) for k in out)
    for k, v in out.items():
        print(f"  {k.ljust(w)}  {v}")
        rows = detail.get(k) or []
        for r in rows[: (40 if verbose else 6)]:
            print(f"      {r}")
        if len(rows) > (40 if verbose else 6):
            print(f"      ... {len(rows) - (40 if verbose else 6)} more (-v)")
    # machine-readable lines for audit_all.py
    print()
    for k in ("registry invalid entries", "unregistered names on cards",
              "taxa with no drawing", "form findings", "anachronisms", "misplaced taxa",
              "curated-vs-range conflicts", "land card-ages with no fauna",
              "land card-ages with no flora", "thin card-ages (under 4 organisms)",
              "homeless labels", "card-ages with NO biota at all",
              "taxa outside their own range within a region", "land cards on drowned ground",
              "drawn from a PARENT form (declared approximation)",
              "range findings vs PBDB"):
        print(f"BIOTA {k}: {out[k]}")
    hard = ("registry invalid entries", "unregistered names on cards", "taxa with no drawing",
            "form findings", "anachronisms", "misplaced taxa",
            "taxa outside their own range within a region", "land cards on drowned ground")
    return 1 if any(out[k] for k in hard) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
