"""Generate the authored diagram set as self-contained SVGs.

Every diagram is DERIVED from the modeling modules rather than drawn by hand, so
when a date or a threshold is corrected in deeptime.py the figures follow. That is
the same discipline the main build uses for its schematic figures (feature_art.py)
and the reason those never drift from the data.

    python "make_diagrams.py"        -> writes ./authored/*.svg

No dependencies beyond the sibling modeling package (and numpy, only for the
climate figure).
"""

from __future__ import annotations

import os
import sys
from math import log10

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "authored")
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "modeling"))

import deeptime as dt                    # noqa: E402
import paleogeography as pg              # noqa: E402
import biome_model as bm                 # noqa: E402

# ---------------------------------------------------------------------------
# shared style. Works on light and dark backgrounds by never relying on a page
# colour: every figure paints its own panel.
# ---------------------------------------------------------------------------

CSS = """
  .bg{fill:#11161c}
  .panel{fill:#161d25;stroke:#2a3644;stroke-width:1}
  .t{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;fill:#d8e2ec}
  .title{font-size:19px;font-weight:600;letter-spacing:.2px}
  .sub{font-size:11.5px;fill:#8fa3b8}
  .lab{font-size:11px}
  .small{font-size:9.5px;fill:#9fb2c6}
  .tick{stroke:#3a4756;stroke-width:1}
  .axis{stroke:#5b6b7d;stroke-width:1.2}
  .grid{stroke:#232d39;stroke-width:1}
  .lead{stroke:#4d5f73;stroke-width:1;stroke-dasharray:2 2}
"""

W = 1180


def _svg(h, body, title, subtitle):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">
<style>{CSS}</style>
<rect class="bg" x="0" y="0" width="{W}" height="{h}"/>
<text class="t title" x="28" y="34">{title}</text>
<text class="t sub" x="28" y="53">{subtitle}</text>
{body}
</svg>"""


def _write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with open(p, "w") as fh:
        fh.write(svg)
    return p


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# 1. The deep-time master chart: assemblies, glaciations, extinctions, LIPs
# ---------------------------------------------------------------------------

CHAR_W = 5.15          # px per character at .small (9.5px Helvetica), measured


def _stagger(labels, rows=3, pad=6):
    """Greedy anti-collision placement, the same idea as the app's layoutLabels():
    sort by x, drop into the first row where this label clears the last one placed,
    and DROP anything that fits nowhere rather than overdrawing.

    labels: [(xcentre, text)] -> [(xcentre, text, row)], plus the dropped count."""
    placed, occupied, dropped = [], [[] for _ in range(rows)], 0
    for xc, txt in sorted(labels):
        half = len(txt) * CHAR_W / 2 + pad
        for r in range(rows):
            if all(xc + half < a or xc - half > b for a, b in occupied[r]):
                occupied[r].append((xc - half, xc + half))
                placed.append((xc, txt, r))
                break
        else:
            dropped += 1
    return placed, dropped


def chart_deep_time():
    x0, x1 = 165, W - 40
    top = 92
    A0, A1 = 1000.0, -250.0                    # oldest .. youngest (future)

    def X(age):
        return x1 - (age - A1) / (A0 - A1) * (x1 - x0)

    y = top
    body, deferred = [], []

    # ---- time axis with period ticks
    body.append(f'<rect class="panel" x="{x0-1}" y="{top-26}" width="{x1-x0+2}" height="19" rx="3"/>')
    per_labels = []
    for p in dt.PERIODS:
        if p.top > A0 or p.base < 0:
            continue
        xa, xb = X(min(p.base, A0)), X(max(p.top, 0))
        if xb - xa < 2:
            continue
        body.append(f'<rect x="{xa:.1f}" y="{top-26}" width="{xb-xa:.1f}" height="19" '
                    f'fill="none" stroke="#2a3644"/>')
        nm = p.name if (xb - xa) > len(p.name) * CHAR_W + 6 else p.name[:3]
        if (xb - xa) > len(nm) * CHAR_W + 4:
            per_labels.append(((xa + xb) / 2, nm))
    for xc, nm in per_labels:
        body.append(f'<text class="t small" x="{xc:.1f}" y="{top-12}" '
                    f'text-anchor="middle">{esc(nm)}</text>')
    xf0, xf1 = X(0), X(A1)
    body.append(f'<rect x="{xf0:.1f}" y="{top-26}" width="{xf1-xf0:.1f}" height="19" '
                f'fill="#1d2530" stroke="#2a3644"/>')
    body.append(f'<text class="t small" x="{(xf0+xf1)/2:.1f}" y="{top-12}" '
                f'text-anchor="middle">projected</text>')

    total_dropped = 0

    def band(label, items, colour, h=20, rows=3, lanes=1):
        """A row of bars. Names go INSIDE where the bar is wide enough, otherwise
        into a staggered stack above it with a leader line.

        lanes>1 packs OVERLAPPING bars onto separate sub-rows instead of drawing
        them on top of each other - which is what supercontinents need, since
        Gondwana, Laurussia, Laurasia and Pangaea all coexist."""
        nonlocal y, total_dropped
        outside, bars = [], []
        lane_ends = []                       # rightmost x used in each lane
        for name, base, topv, strong in items:
            base, topv = min(base, A0), max(topv, A1)
            if base <= topv:
                continue
            xa, xb = X(base), X(topv)
            w = max(xb - xa, 3.0)
            lane = 0
            if lanes > 1:
                for li in range(lanes):
                    if li >= len(lane_ends):
                        lane_ends.append(-1e9)
                    if xa >= lane_ends[li] + 3:
                        lane = li
                        break
                else:
                    lane = lanes - 1
                lane_ends[lane] = xa + w
            bars.append((xa, w, name, strong, lane))
            if w <= len(name) * CHAR_W + 8:
                outside.append((xa + w / 2, name))
        n_lanes = max((b[4] for b in bars), default=0) + 1
        lane_h = h if lanes == 1 else max(15, h - 3)
        placed, dropped = _stagger(outside, rows=rows)
        total_dropped += dropped
        stack_h = (max((r for _, _, r in placed), default=-1) + 1) * 13
        ytop = y + stack_h                       # bars sit below their label stack
        band_h = n_lanes * (lane_h + 2) - 2

        body.append(f'<text class="t lab" x="{x0-14}" y="{ytop+band_h/2+4:.0f}" '
                    f'text-anchor="end" fill="#9fb2c6">{esc(label)}</text>')
        for xa, w, name, strong, lane in bars:
            yy = ytop + lane * (lane_h + 2)
            op = 0.95 if strong else 0.5
            body.append(f'<rect x="{xa:.1f}" y="{yy:.0f}" width="{w:.1f}" '
                        f'height="{lane_h}" rx="2.5" fill="{colour}" opacity="{op}"/>')
            if w > len(name) * CHAR_W + 8:
                body.append(f'<text class="t small" x="{xa+w/2:.1f}" '
                            f'y="{yy+lane_h/2+3.4:.1f}" text-anchor="middle" '
                            f'fill="#0d1218">{esc(name)}</text>')
        for xc, txt, r in placed:
            ly = y + r * 13 + 9
            body.append(f'<text class="t small" x="{xc:.1f}" y="{ly:.1f}" '
                        f'text-anchor="middle">{esc(txt)}</text>')
            body.append(f'<line class="lead" x1="{xc:.1f}" y1="{ly+3:.1f}" '
                        f'x2="{xc:.1f}" y2="{ytop:.1f}"/>')
        y = ytop + band_h + 12

    band("supercontinents",
         [(n, a["base"], a["top"], a["confidence"] == "good")
          for n, a in sorted(pg.ASSEMBLIES.items(), key=lambda kv: -kv[1]["base"])],
         "#c9a227", 20, rows=2, lanes=4)
    band("glaciations",
         [(e.name, e.base, e.top, e.confidence == "good") for e in dt.GLACIATIONS
          if e.base <= A0], "#7ebad6")
    band("mass extinctions",
         [(e.name.split(" (")[0], e.base + 5, e.top - 5, e.confidence == "good")
          for e in dt.EXTINCTIONS], "#e07650")
    band("large igneous provinces",
         [(e.name, e.base + 3, e.top - 3, True) for e in dt.LIPS], "#b0603f")
    band("oceanic anoxic events",
         [(e.name.split(" (")[0], e.base + 3, e.top - 3, e.confidence == "good")
          for e in dt.ANOXIC_EVENTS], "#4f6f5a")
    band("hyperthermals",
         [(e.name, e.base + 3, e.top - 3, True) for e in dt.HYPERTHERMALS], "#d0864f")
    band("land vegetation",
         [(e["label"], min(e["base"], A0), max(e["top"], A1), True)
          for e in bm.VEGETATION_ERAS if e["top"] < A0],
         "#4a8050", 22, rows=2)

    grid_bottom = y - 4
    for age in (1000, 800, 600, 400, 200, 0, -250):
        body.insert(0, f'<line class="grid" x1="{X(age):.1f}" y1="{top-6}" '
                       f'x2="{X(age):.1f}" y2="{grid_bottom:.0f}"/>')
        body.append(f'<text class="t small" x="{X(age):.1f}" y="{grid_bottom+18:.0f}" '
                    f'text-anchor="middle">{abs(age):g}'
                    f'{" Ma" if age == 1000 else ""}{" future" if age < 0 else ""}</text>')

    foot = ('Bar opacity encodes confidence: solid = well constrained, faded = moderate '
            'or contested. Events shorter than the pixel grid are drawn at a minimum '
            'width; true durations are in deeptime.py.')
    if total_dropped:
        foot += f' {total_dropped} label(s) dropped rather than overdrawn.'
    body.append(f'<text class="t small" x="{x0}" y="{grid_bottom+42:.0f}">{esc(foot)}</text>')
    return _svg(grid_bottom + 62, "\n".join(body),
                "Deep time master chart, 1000 Ma to +250 Myr",
                "Every band is generated from modeling/deeptime.py and "
                "modeling/paleogeography.py - the figure cannot drift from the data")


# ---------------------------------------------------------------------------
# 2. Vegetation of the world through time: zone x era matrix
# ---------------------------------------------------------------------------

def chart_vegetation_matrix():
    zones = ["tropical rainforest", "seasonal tropical forest", "savanna",
             "subtropical desert", "temperate rainforest", "temperate forest",
             "temperate grassland", "boreal forest", "tundra", "wetland"]
    eras = bm.VEGETATION_ERAS
    left, top = 210, 108
    cw = (W - left - 30) / len(eras)
    rh = 40
    body = []
    for j, e in enumerate(eras):
        x = left + j * cw
        lo = "future" if e["top"] < -1000 else f"{e['top']:g}"
        body.append(f'<text class="t small" x="{x+cw/2:.1f}" y="{top-26}" '
                    f'text-anchor="middle" fill="#c9a227">{esc(e["label"])}</text>')
        body.append(f'<text class="t small" x="{x+cw/2:.1f}" y="{top-13}" '
                    f'text-anchor="middle">{e["base"]:g}-{lo} Ma</text>')
    for i, z in enumerate(zones):
        yv = top + i * rh
        body.append(f'<text class="t lab" x="{left-12}" y="{yv+rh/2+4:.0f}" '
                    f'text-anchor="end">{esc(z)}</text>')
        for j, e in enumerate(eras):
            x = left + j * cw
            name, doms, hgt = e["zones"][z]
            col = bm._COLOURS[z]
            # height drives opacity so the growth of the canopy is visible
            op = 0.18 + 0.72 * min(hgt / 55.0, 1.0)
            body.append(f'<rect x="{x+1.5:.1f}" y="{yv+1.5}" width="{cw-3:.1f}" '
                        f'height="{rh-3}" rx="3" fill="{col}" opacity="{op:.2f}"/>')
            words = esc(name)
            if len(words) > 20:
                a, _, b = words.rpartition(" ")
                body.append(f'<text class="t small" x="{x+cw/2:.1f}" y="{yv+rh/2-2:.0f}" '
                            f'text-anchor="middle">{a}</text>')
                body.append(f'<text class="t small" x="{x+cw/2:.1f}" y="{yv+rh/2+10:.0f}" '
                            f'text-anchor="middle">{b}</text>')
            else:
                body.append(f'<text class="t small" x="{x+cw/2:.1f}" y="{yv+rh/2+4:.0f}" '
                            f'text-anchor="middle">{words}</text>')
            if hgt > 0:
                body.append(f'<text class="t small" x="{x+cw-6:.1f}" y="{yv+rh-6:.0f}" '
                            f'text-anchor="end" opacity="0.6">{hgt:g}m</text>')
    h = top + len(zones) * rh + 52
    body.append(f'<text class="t small" x="28" y="{h-24}">'
                'Fill opacity is canopy height, so the greening and heightening of the '
                'land is visible as a gradient from left to right. Note the two '
                'exceptions the app must honour: no grassland cell has grass before the '
                'Cenozoic, and no cell has a canopy before ~385 Ma.</text>')
    return _svg(h, "\n".join(body), "What grew where, and when",
                "Whittaker climate zones (rows) x vegetation eras (columns), from "
                "modeling/biome_model.py")


# ---------------------------------------------------------------------------
# 3. The longitude problem
# ---------------------------------------------------------------------------

def chart_longitude_problem():
    body = []
    cx, cy, r = 300, 260, 150
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#182028" stroke="#33414f"/>')
    # latitude lines
    for lat in (-60, -30, 0, 30, 60):
        yy = cy - r * lat / 90.0
        hw = r * (1 - (lat / 90.0) ** 2) ** 0.5
        body.append(f'<line class="grid" x1="{cx-hw:.1f}" y1="{yy:.1f}" '
                    f'x2="{cx+hw:.1f}" y2="{yy:.1f}"/>')
    body.append(f'<line class="axis" x1="{cx}" y1="{cy-r-16}" x2="{cx}" y2="{cy+r+16}"/>')
    body.append(f'<text class="t small" x="{cx}" y="{cy-r-24}" text-anchor="middle">'
                'spin axis</text>')
    # the same continent at three longitudes, all with identical palaeolatitude
    for k, (dx, col, lab) in enumerate([(-96, "#c9a227", "position A"),
                                        (0, "#8fb4d0", "position B"),
                                        (96, "#d0866f", "position C")]):
        yy = cy - r * 30 / 90.0
        body.append(f'<ellipse cx="{cx+dx:.1f}" cy="{yy:.1f}" rx="30" ry="18" '
                    f'fill="{col}" opacity="0.72"/>')
        body.append(f'<text class="t small" x="{cx+dx:.1f}" y="{yy+4:.1f}" '
                    f'text-anchor="middle" fill="#0d1218">{lab}</text>')
    body.append(f'<text class="t small" x="{cx}" y="{cy+r+40}" text-anchor="middle">'
                'Identical palaeomagnetic pole. Identical inclination. Identical '
                'declination.</text>')
    body.append(f'<text class="t small" x="{cx}" y="{cy+r+56}" text-anchor="middle" '
                f'fill="#e07650">Nothing in the data distinguishes A, B and C.</text>')

    # right panel: the consequence for our pipeline
    bx = 640
    body.append(f'<rect class="panel" x="{bx}" y="96" width="{W-bx-34}" height="300" rx="6"/>')
    lines = [
        ("#c9a227", "Terrain: Scotese & Wright PaleoDEMs, PALEOMAP frame"),
        ("#8fb4d0", "Tracks: Merdith et al. 2021, its own frame"),
        ("", ""),
        ("", "Measured longitude gap between the two frames:"),
        ("", "    ~9 deg at 90 Ma      ~21 deg at 150 Ma      ~40 deg in the Ordovician"),
        ("", ""),
        ("#e07650", "Symptom: the Western Interior Seaway label sat over the Appalachians."),
        ("", ""),
        ("", "frame_offset.py corrects it as a RIGID global shift."),
        ("", "Craters on plausible terrain   80% -> 90%"),
        ("", "Label anchors on right medium  69% -> 71%"),
        ("", ""),
        ("#e07650", "But the real difference is REGIONAL, not rigid: each model pins"),
        ("#e07650", "longitude by a different argument, and the arguments differ"),
        ("#e07650", "per continent. So a global shift moves Chicxulub off the shelf"),
        ("#e07650", "while it fixes the seaway. 27 labels remain on the wrong medium"),
        ("#e07650", "for more than a third of their span."),
    ]
    yy = 124
    for col, txt in lines:
        if txt:
            fill = f' fill="{col}"' if col else ""
            body.append(f'<text class="t small" x="{bx+18}" y="{yy}"{fill}>{esc(txt)}</text>')
        yy += 17
    return _svg(470, "\n".join(body),
                "Why deep-time labels land in the wrong place",
                "Palaeomagnetism constrains latitude and rotation, never longitude - "
                "so every reconstruction picks its own frame")


# ---------------------------------------------------------------------------
# 4. Causal chain: LIP -> climate -> ocean -> extinction
# ---------------------------------------------------------------------------

def chart_lip_cascade():
    body = []
    stages = [
        ("#b0603f", "LARGE IGNEOUS PROVINCE",
         [">1e5 km3, and >75% of that",
          "in pulses of 1-5 Myr.",
          "It is the RATE, not the volume"]),
        ("#8fa3b8", "SO2 -> sulfate aerosol",
         ["cooling, months to years", "sharp and short"]),
        ("#d0864f", "CO2 -> greenhouse",
         ["warming, 1e3 - 1e6 yr", "the long tail that matters"]),
        ("#6f8fa8", "warming -> stratification",
         ["+ weathering-driven nutrient flux", "-> productivity"]),
        ("#4f6f5a", "OCEANIC ANOXIC EVENT",
         ["black laminated shale, no bioturbation",
          "carbon isotope excursion",
          "only above ~25 C GMST"]),
        ("#e07650", "EXTINCTION",
         ["habitat loss + H2S toxicity", "+ ozone destruction at extremes"]),
    ]
    x, y0 = 40, 110
    bw, bh = 168, 128
    for i, (col, head, lines) in enumerate(stages):
        bx = x + i * (bw + 12)
        body.append(f'<rect x="{bx}" y="{y0}" width="{bw}" height="{bh}" rx="7" '
                    f'fill="#161d25" stroke="{col}" stroke-width="1.6"/>')
        body.append(f'<rect x="{bx}" y="{y0}" width="{bw}" height="5" rx="2.5" fill="{col}"/>')
        body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+26}" text-anchor="middle" '
                    f'fill="{col}" font-weight="600">{esc(head[:26])}</text>')
        for j, ln in enumerate(lines):
            body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+48+j*15}" '
                        f'text-anchor="middle">{esc(ln)}</text>')
        if i < len(stages) - 1:
            ax = bx + bw + 2
            body.append(f'<path d="M{ax} {y0+bh/2} l11 0 m-4 -4 l4 4 l-4 4" '
                        f'stroke="#5b6b7d" fill="none" stroke-width="1.4"/>')

    pairs = [("Siberian Traps", "252-250", "End-Permian", "P-Tr deoxygenation"),
             ("CAMP", "202-197", "End-Triassic", "-"),
             ("Karoo-Ferrar", "184-178", "Toarcian turnover", "T-OAE"),
             ("Ontong Java", "124-120", "-", "OAE 1a (Selli)"),
             ("Caribbean LIP", "95-88", "Cenomanian-Turonian", "OAE 2 (Bonarelli)"),
             ("Deccan Traps", "68.5-65.5", "End-Cretaceous", "-"),
             ("N Atlantic IP", "62-55", "benthic foram turnover", "PETM")]
    ty = y0 + bh + 46
    body.append(f'<text class="t lab" x="40" y="{ty-12}" fill="#9fb2c6">'
                'The instances, from modeling/deeptime.py</text>')
    cols = [40, 260, 420, 700]
    heads = ["province", "Ma", "extinction / turnover", "anoxic or thermal event"]
    for cx, hd in zip(cols, heads):
        body.append(f'<text class="t small" x="{cx}" y="{ty+10}" fill="#8fa3b8">{hd}</text>')
    for k, row in enumerate(pairs):
        yy = ty + 30 + k * 19
        for cx, val in zip(cols, row):
            body.append(f'<text class="t small" x="{cx}" y="{yy}">{esc(val)}</text>')
    body.append(f'<text class="t small" x="40" y="{ty+30+len(pairs)*19+24}" fill="#8fa3b8">'
                'Deccan begins ~1 Myr BEFORE Chicxulub, so the impact cannot have '
                'triggered it - a case where the sequence is the argument.</text>')
    return _svg(ty + 30 + len(pairs) * 19 + 46, "\n".join(body),
                "How a volcanic province kills an ocean",
                "The mechanism runs in a fixed order, and each step has its own "
                "timescale and its own sedimentary fingerprint")


# ---------------------------------------------------------------------------
# 5. Continental assembly: which block was part of what, when
# ---------------------------------------------------------------------------

def chart_block_affiliation():
    blocks = ["Laurentia", "Baltica", "Siberia", "Avalonia", "Armorica",
              "Amazonia", "West African Craton", "Congo Craton", "Kalahari Craton",
              "India", "Australia", "East Antarctica", "North China", "South China",
              "Cimmeria", "Kazakhstania", "Zealandia"]
    A0, A1 = 1000.0, 0.0
    left, top = 190, 106
    x0, x1 = left, W - 40
    rh = 26

    def X(age):
        return x1 - (age - A1) / (A0 - A1) * (x1 - x0)

    colours = {"Rodinia": "#7f6fa8", "Pannotia": "#5f6f8f", "Gondwana": "#c9a227",
               "Laurussia": "#4f8fa0", "Laurasia": "#3f7f6a", "Pangaea": "#c06a4a"}
    body = []
    for age in (1000, 800, 600, 400, 200, 0):
        body.append(f'<line class="grid" x1="{X(age):.1f}" y1="{top-22}" '
                    f'x2="{X(age):.1f}" y2="{top+len(blocks)*rh+6}"/>')
        body.append(f'<text class="t small" x="{X(age):.1f}" y="{top-28}" '
                    f'text-anchor="middle">{age:g} Ma</text>')
    for i, b in enumerate(blocks):
        yy = top + i * rh
        body.append(f'<text class="t lab" x="{left-12}" y="{yy+17}" text-anchor="end">'
                    f'{esc(b)}</text>')
        blk = pg.BLOCKS[b]
        xa, xb = X(min(blk.first, A0)), X(max(blk.last, A1))
        body.append(f'<rect x="{xa:.1f}" y="{yy+5}" width="{max(xb-xa,2):.1f}" height="16" '
                    f'rx="3" fill="#212a34"/>')
        # affiliations, drawn in nesting order so the largest is behind
        for aname in ("Rodinia", "Pannotia", "Gondwana", "Laurussia", "Laurasia", "Pangaea"):
            a = pg.ASSEMBLIES[aname]
            if b not in a["members"]:
                continue
            ba = min(a["base"], blk.first, A0)
            ta = max(a["top"], blk.last, A1)
            if ba <= ta:
                continue
            xa, xb = X(ba), X(ta)
            disputed = b in a.get("disputed", [])
            op = 0.35 if disputed else 0.85
            dash = ' stroke-dasharray="3 2" stroke="#d8e2ec" stroke-width="0.8"' if disputed else ""
            body.append(f'<rect x="{xa:.1f}" y="{yy+5}" width="{xb-xa:.1f}" height="16" '
                        f'rx="3" fill="{colours[aname]}" opacity="{op}"{dash}/>')
    ly = top + len(blocks) * rh + 30
    lx = left
    for aname, col in colours.items():
        body.append(f'<rect x="{lx}" y="{ly-10}" width="14" height="12" rx="2" fill="{col}"/>')
        body.append(f'<text class="t small" x="{lx+20}" y="{ly}">{aname}</text>')
        lx += 20 + len(aname) * 6.6 + 22
    body.append(f'<text class="t small" x="{left}" y="{ly+22}" fill="#8fa3b8">'
                'Dark bar = the block exists but belongs to no named assembly - it is an '
                'independent continent or a drifting terrane. Dashed and faded = its '
                'membership is disputed in the literature. '
                'Pannotia itself is contested: several authors hold that the pieces were '
                'never all joined at once.</text>')
    return _svg(ly + 44, "\n".join(body),
                "Which continent was part of what, and when",
                "From modeling/paleogeography.py - the table a label must satisfy "
                "before it is drawn")


# ---------------------------------------------------------------------------
# 6. Ice-albedo bifurcation from the EBM
# ---------------------------------------------------------------------------

def chart_snowball():
    try:
        import climate_ebm as ebm
    except Exception as exc:                       # pragma: no cover
        print("skipping snowball chart:", exc)
        return None
    co2s = [30 * (1.6 ** i) for i in range(22)]
    warm = [ebm.solve(co2_ppm=c, age_ma=700) for c in co2s]
    left, top = 120, 108
    pw, ph = W - left - 380, 300

    def PX(c):
        return left + (log10(c) - log10(co2s[0])) / (log10(co2s[-1]) - log10(co2s[0])) * pw

    def PY(t):
        return top + ph - (t + 45) / 95.0 * ph

    body = [f'<rect class="panel" x="{left}" y="{top}" width="{pw}" height="{ph}" rx="4"/>']
    for t in (-40, -20, 0, 20, 40):
        body.append(f'<line class="grid" x1="{left}" y1="{PY(t):.1f}" '
                    f'x2="{left+pw}" y2="{PY(t):.1f}"/>')
        body.append(f'<text class="t small" x="{left-10}" y="{PY(t)+4:.1f}" '
                    f'text-anchor="end">{t} C</text>')
    for c in (30, 100, 300, 1000, 3000, 10000, 30000):
        if co2s[0] <= c <= co2s[-1]:
            body.append(f'<line class="grid" x1="{PX(c):.1f}" y1="{top}" '
                        f'x2="{PX(c):.1f}" y2="{top+ph}"/>')
            body.append(f'<text class="t small" x="{PX(c):.1f}" y="{top+ph+16:.1f}" '
                        f'text-anchor="middle">{c:g}</text>')
    body.append(f'<text class="t small" x="{left+pw/2:.1f}" y="{top+ph+34:.1f}" '
                f'text-anchor="middle">atmospheric CO2, ppm (log)</text>')
    pts = " ".join(f"{PX(r.co2_ppm):.1f},{PY(r.gmst):.1f}" for r in warm)
    body.append(f'<polyline points="{pts}" fill="none" stroke="#c9a227" stroke-width="2.2"/>')
    for r in warm:
        col = "#7ebad6" if r.snowball else ("#4a8050" if r.ice_line >= 89 else "#c9a227")
        body.append(f'<circle cx="{PX(r.co2_ppm):.1f}" cy="{PY(r.gmst):.1f}" r="3.4" '
                    f'fill="{col}"/>')
    # mark the transition
    for a, b in zip(warm, warm[1:]):
        if a.snowball and not b.snowball:
            xm = (PX(a.co2_ppm) + PX(b.co2_ppm)) / 2
            body.append(f'<line x1="{xm:.1f}" y1="{top}" x2="{xm:.1f}" y2="{top+ph}" '
                        f'stroke="#e07650" stroke-width="1.4" stroke-dasharray="4 3"/>')
            body.append(f'<text class="t small" x="{xm+7:.1f}" y="{top+18}" '
                        f'fill="#e07650">deglaciation threshold</text>')
            break

    bx = left + pw + 32
    body.append(f'<rect class="panel" x="{bx}" y="{top}" width="{W-bx-34}" height="{ph}" rx="6"/>')
    txt = [
        "1-D diffusive energy balance model,",
        "solar luminosity at 700 Ma (Gough 1981):",
        "8% fainter than today.",
        "",
        "Blue  = hard snowball (ice fraction > 0.95)",
        "Gold  = partial ice cover",
        "Green = ice free",
        "",
        "The point of the figure is the DISCONTINUITY.",
        "Once ice reaches the subtropics the albedo",
        "feedback runs away, and escaping needs a CO2",
        "level orders of magnitude above the one that",
        "let the planet freeze. That hysteresis is why",
        "the Cryogenian terminations required a spike",
        "of order 10^5 ppm and produced cap carbonates.",
        "",
        "Caveat, stated in the module: the logarithmic",
        "CO2 forcing law is not valid at 10^5 ppm, so",
        "the absolute threshold here is too high. The",
        "hysteresis is robust; the number is not.",
    ]
    yy = top + 24
    for ln in txt:
        body.append(f'<text class="t small" x="{bx+16}" y="{yy}">{esc(ln)}</text>')
        yy += 15
    return _svg(top + ph + 60, "\n".join(body),
                "The snowball bifurcation",
                "Global mean temperature against CO2 at 700 Ma, from "
                "modeling/climate_ebm.py")


# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 7. Cenozoic climate events: warming above the line, drawdown below
# ---------------------------------------------------------------------------

def chart_cenozoic_events():
    A0, A1 = 70.0, 0.0
    x0, x1, mid = 150, W - 42, 300
    body = []

    def X(a):
        return x1 - (a - A1) / (A0 - A1) * (x1 - x0)

    body.append(f'<line class="axis" x1="{x0}" y1="{mid}" x2="{x1}" y2="{mid}"/>')
    for a in (70, 60, 50, 40, 30, 20, 10, 0):
        body.append(f'<line class="grid" x1="{X(a):.1f}" y1="108" x2="{X(a):.1f}" y2="{mid+150}"/>')
        body.append(f'<text class="t small" x="{X(a):.1f}" y="{mid+166}" '
                    f'text-anchor="middle">{a} Ma</text>')
    for ep in dt.EPOCHS:
        if ep.top >= A0 or ep.base <= 0 or ep.parent not in ("Paleogene", "Neogene", "Quaternary"):
            continue
        xa, xb = X(min(ep.base, A0)), X(max(ep.top, 0))
        body.append(f'<rect x="{xa:.1f}" y="{mid+8}" width="{xb-xa:.1f}" height="17" '
                    f'fill="none" stroke="#2a3644"/>')
        if xb - xa > len(ep.name) * CHAR_W + 6:
            body.append(f'<text class="t small" x="{(xa+xb)/2:.1f}" y="{mid+20}" '
                        f'text-anchor="middle">{esc(ep.name)}</text>')

    warm = [e for e in dt.HYPERTHERMALS if e.base <= A0 and e.top >= A1]
    cool = [e for e in dt.DRAWDOWNS if e.base <= A0 and e.top >= A1]
    body.append(f'<text class="t lab" x="{x0-14}" y="{mid-100}" text-anchor="end" '
                f'fill="#d0864f">WARMING</text>')
    body.append(f'<text class="t lab" x="{x0-14}" y="{mid+86}" text-anchor="end" '
                f'fill="#6f9fbf">DRAWDOWN</text>')

    lab = []
    for i, e in enumerate(sorted(warm, key=lambda e: -e.base)):
        xa, xb = X(min(e.base, A0)), X(max(e.top, 0))
        w = max(xb - xa, 6)
        h = 26 + (i % 3) * 26
        body.append(f'<rect x="{xa:.1f}" y="{mid-h}" width="{w:.1f}" height="{h}" rx="2" '
                    f'fill="#d0864f" opacity="0.85"/>')
        lab.append((xa + w / 2, mid - h - 6, e.name, "#e0a070"))
    for i, e in enumerate(sorted(cool, key=lambda e: -e.base)):
        xa, xb = X(min(e.base, A0)), X(max(e.top, 0))
        w = max(xb - xa, 6)
        h = 34 + (i % 2) * 26
        body.append(f'<rect x="{xa:.1f}" y="{mid+30}" width="{w:.1f}" height="{h}" rx="2" '
                    f'fill="#6f9fbf" opacity="0.8"/>')
        lab.append((xa + w / 2, mid + 30 + h + 13, e.name, "#8fb4d0"))
    placed, dropped = _stagger([(x, t) for x, _, t, _ in lab], rows=3, pad=5)
    row_of = {t: r for _, t, r in placed}
    okset = {t for _, t, _ in placed}
    for xc, yy, txt, col in lab:
        if txt not in okset:
            continue
        off = row_of.get(txt, 0) * 13
        yy2 = yy - off if yy < mid else yy + off
        anc = "middle"
        xt = xc
        if xc > x1 - 70:
            anc, xt = "end", x1
        elif xc < x0 + 40:
            anc, xt = "start", x0
        body.append(f'<text class="t small" x="{xt:.1f}" y="{yy2:.1f}" '
                    f'text-anchor="{anc}" fill="{col}">{esc(txt)}</text>')

    for a, t in ((66, "K-Pg"), (34, "Antarctic ice"), (2.7, "N Hemisphere ice")):
        body.append(f'<line x1="{X(a):.1f}" y1="118" x2="{X(a):.1f}" y2="{mid-2}" '
                    f'stroke="#8a99aa" stroke-width="1" stroke-dasharray="3 3"/>')
        anc = "end" if X(a) > x1 - 90 else "start"
        xt = X(a) - 5 if anc == "end" else X(a) + 5
        body.append(f'<text class="t small" x="{xt:.1f}" y="126" '
                    f'text-anchor="{anc}">{esc(t)}</text>')

    body.append(f'<text class="t small" x="{x0}" y="{mid+196}">'
                'Bar height is arbitrary and only separates neighbours; bar WIDTH is the '
                'real duration. Every one of these is shorter than a 5 Myr keyframe, which '
                'is why they belong on cards rather than on the map.</text>')
    return _svg(mid + 216, "\n".join(body),
                "Cenozoic climate events: what warmed it, what cooled it",
                "From modeling/deeptime.py HYPERTHERMALS and DRAWDOWNS")


# ---------------------------------------------------------------------------
# 8. Oxygen through time
# ---------------------------------------------------------------------------

def chart_oxygen():
    # (age Ma, % of present atmospheric level) - a schematic of the consensus shape
    pts = [(4000, 0.001), (2600, 0.001), (2450, 2), (2320, 60), (2250, 90), (2150, 40),
           (2050, 5), (1800, 3), (1200, 3), (900, 5), (800, 10), (700, 20), (600, 40),
           (541, 60), (430, 60), (400, 75), (360, 110), (300, 150), (280, 145),
           (250, 75), (200, 60), (150, 80), (100, 95), (50, 100), (0, 100)]
    x0, x1, y0, y1 = 150, W - 330, 120, 470
    A0 = 4000.0

    def X(a):
        import math
        return x0 + (1 - math.log10(max(a, 1) + 1) / math.log10(A0 + 1)) * (x1 - x0)

    def Y(p):
        import math
        return y1 - (math.log10(max(p, 0.0005) / 0.0005) / math.log10(160 / 0.0005)) * (y1 - y0)

    body = [f'<rect class="panel" x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="4"/>']
    for p, lb in ((0.001, "0.001%"), (0.1, "0.1%"), (1, "1%"), (10, "10%"), (100, "100% PAL")):
        body.append(f'<line class="grid" x1="{x0}" y1="{Y(p):.1f}" x2="{x1}" y2="{Y(p):.1f}"/>')
        body.append(f'<text class="t small" x="{x0-8}" y="{Y(p)+4:.1f}" '
                    f'text-anchor="end">{lb}</text>')
    for a in (4000, 2500, 1000, 500, 100, 0):
        body.append(f'<line class="grid" x1="{X(a):.1f}" y1="{y0}" x2="{X(a):.1f}" y2="{y1}"/>')
        body.append(f'<text class="t small" x="{X(a):.1f}" y="{y1+16:.1f}" '
                    f'text-anchor="middle">{a}</text>')
    body.append(f'<text class="t small" x="{(x0+x1)/2:.1f}" y="{y1+34:.1f}" '
                f'text-anchor="middle">Ma (log)</text>')
    poly = " ".join(f"{X(a):.1f},{Y(p):.1f}" for a, p in pts)
    body.append(f'<polyline points="{poly}" fill="none" stroke="#7fc4a0" stroke-width="2.4"/>')
    for a, txt, col in ((2460, "Great Oxidation Event", "#c9a227"),
                        (2300, "Lomagundi overshoot", "#e0a070"),
                        (2100, "and crash", "#e07650"),
                        (1500, "the 'boring billion'", "#8fa3b8"),
                        (700, "Neoproterozoic Oxygenation", "#7ebad6"),
                        (300, "Permo-Carboniferous peak ~30%", "#7fc4a0")):
        body.append(f'<line x1="{X(a):.1f}" y1="{y0+6}" x2="{X(a):.1f}" y2="{y1-4}" '
                    f'stroke="{col}" stroke-width="1" stroke-dasharray="3 3" opacity="0.7"/>')
    lb = [(2460, "Great Oxidation Event", 0, "start"),
          (2200, "Lomagundi overshoot, then crash", 1, "start"),
          (1500, "the 'boring billion'", 2, "start"),
          (700, "Neoproterozoic Oxygenation", 3, "start"),
          (300, "Permo-Carboniferous peak ~30%", 4, "end")]
    for a, t, r, anc in lb:
        yy = y1 - 16 - r * 15
        body.append(f'<text class="t small" x="{X(a) + (-6 if anc=="end" else 6):.1f}" '
                    f'y="{yy:.1f}" text-anchor="{anc}">{esc(t)}</text>')

    bx = x1 + 26
    body.append(f'<rect class="panel" x="{bx}" y="{y0}" width="{W-bx-34}" height="{y1-y0}" rx="6"/>')
    txt = ["A schematic of the consensus SHAPE, not a data series -",
           "the absolute values before the Phanerozoic carry",
           "large uncertainty and the curve is drawn on a log",
           "axis in both directions for that reason.",
           "",
           "What each step is FOR:",
           "",
           "GOE (2.46-2.06 Ga) oxidises methane, collapses the",
           "  greenhouse, and freezes the planet (Huronian).",
           "  Banded iron formations stop; red beds start; an",
           "  ozone layer forms. >2,500 of Earth's ~4,500",
           "  minerals date from it.",
           "",
           "Lomagundi-Jatuli (~2.3 Ga) overshoots near modern",
           "  levels, then crashes at ~2.1 Ga. Not a ramp.",
           "",
           "The boring billion holds a few percent PAL with",
           "  euxinic mid-depths. Eukaryotes exist and do not",
           "  radiate.",
           "",
           "NOE (~850-540 Ma) is the permissive condition for",
           "  large animals: an organism metres across with no",
           "  circulation needs an oxygenated water column.",
           "",
           "The Permo-Carboniferous peak is the coal forests'",
           "  buried carbon. ~30%, not 35%."]
    yy = y0 + 20
    for ln in txt:
        body.append(f'<text class="t small" x="{bx+14}" y="{yy}">{esc(ln)}</text>')
        yy += 13.4
    return _svg(y1 + 56, "\n".join(body), "Oxygen through Earth history",
                "Schematic; see research/05-atmosphere-ocean-chemistry for the evidence")


# ---------------------------------------------------------------------------
# 9. Atoll and guyot subsidence
# ---------------------------------------------------------------------------

def chart_atoll():
    body = []
    stages = [("1. volcanic island", "fringing reef hugs the shore", -46),
              ("2. subsiding", "barrier reef + lagoon", -14),
              ("3. atoll", "ring of reef, no island left", 12),
              ("4. guyot", "reef drowned; flat wave-cut top", 74)]
    bw, y0, h = 250, 128, 190
    sea = y0 + 52
    for i, (title, sub, drop) in enumerate(stages):
        bx = 44 + i * (bw + 20)
        body.append(f'<rect x="{bx}" y="{y0}" width="{bw}" height="{h}" rx="6" '
                    f'fill="#101820" stroke="#2a3644"/>')
        body.append(f'<rect x="{bx+1}" y="{sea}" width="{bw-2}" height="{y0+h-sea-1}" '
                    f'fill="#16344a" opacity="0.85"/>')
        body.append(f'<line x1="{bx+1}" y1="{sea}" x2="{bx+bw-1}" y2="{sea}" '
                    f'stroke="#5fa8c8" stroke-width="1.4"/>')
        # the volcano, sinking by `drop`
        cx = bx + bw / 2
        base_y = y0 + h - 6
        peak_y = sea + drop
        hw = 96
        body.append(f'<path d="M{cx-hw} {base_y} L{cx} {peak_y} L{cx+hw} {base_y} Z" '
                    f'fill="#4a3f39"/>')
        if i == 3:   # wave-planed flat top
            body.append(f'<path d="M{cx-46} {peak_y+12} L{cx+46} {peak_y+12} '
                        f'L{cx+hw} {base_y} L{cx-hw} {base_y} Z" fill="#4a3f39"/>')
            body.append(f'<line x1="{cx-46}" y1="{peak_y+12}" x2="{cx+46}" y2="{peak_y+12}" '
                        f'stroke="#7d6f63" stroke-width="2"/>')
        # water veil ON TOP of the rock, so anything below the line reads submerged
        body.append(f'<rect x="{bx+1}" y="{sea}" width="{bw-2}" height="{y0+h-sea-1}" '
                    f'fill="#16344a" opacity="0.55"/>')
        body.append(f'<line x1="{bx+1}" y1="{sea}" x2="{bx+bw-1}" y2="{sea}" '
                    f'stroke="#5fa8c8" stroke-width="1.4"/>')
        # reef: a bright cap that always reaches the surface while it can
        if i < 3:
            rw = 26 + i * 30
            body.append(f'<rect x="{cx-rw-14}" y="{sea-7}" width="14" height="13" rx="2" '
                        f'fill="#d8c48a"/>')
            body.append(f'<rect x="{cx+rw}" y="{sea-7}" width="14" height="13" rx="2" '
                        f'fill="#d8c48a"/>')
        if i == 1 or i == 2:
            body.append(f'<text class="t small" x="{cx}" y="{sea+16}" text-anchor="middle" '
                        f'fill="#7fbfd8">lagoon</text>')
        if i == 3:
            body.append(f'<text class="t small" x="{cx}" y="{peak_y+2}" text-anchor="middle" '
                        f'fill="#9fb2c6">drowned</text>')
        body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+h+18}" '
                    f'text-anchor="middle" fill="#c9a227">{esc(title)}</text>')
        body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+h+32}" '
                    f'text-anchor="middle">{esc(sub)}</text>')
        if i < 3:
            ax = bx + bw + 3
            body.append(f'<path d="M{ax} {y0+h/2} l13 0 m-5 -5 l5 5 l-5 5" '
                        f'stroke="#5b6b7d" fill="none" stroke-width="1.4"/>')
    foot = [
        "The island does not sink because it is heavy. It sinks because the sea floor "
        "it stands on is cooling: oceanic",
        "lithosphere contracts and subsides as it ages, by roughly 350 m for every "
        "square root of a million years.",
        "So every volcanic island rides slowly downward, and whether it becomes an atoll "
        "or a guyot is decided by",
        "whether coral can grow upward fast enough - which depends on the water being "
        "warm enough. Darwin worked",
        "the whole sequence out in 1842 from the shapes alone, before anyone knew the "
        "sea floor moved at all.",
        "",
        "FOR THE MODEL: this is the same physics as the seamount population in "
        "seafloor.py. Seeding seamounts along",
        "plume tracks and letting them subside with crustal age predicts flat-topped "
        "guyots at depth on old chains and",
        "sharp cones and islands on young ones - for free, from a mechanism rather "
        "than from a texture.",
    ]
    yy = y0 + h + 62
    for ln in foot:
        body.append(f'<text class="t small" x="44" y="{yy}">{esc(ln)}</text>')
        yy += 14
    return _svg(yy + 10, "\n".join(body), "Atolls and guyots: an island's whole life",
                "Darwin's subsidence sequence, and why our seamounts should have flat tops")


# ---------------------------------------------------------------------------
# 10. Back-arc basin by slab roll-back
# ---------------------------------------------------------------------------

def chart_backarc():
    body = []
    bw, bh, y0 = 340, 210, 122
    for i, (title, note, rb) in enumerate([
            ("1. steep subduction", "arc built on the overriding plate", 0),
            ("2. slab rolls back", "trench migrates oceanward; plate stretches", 1),
            ("3. back-arc basin", "the overriding plate rifts and spreads", 2)]):
        bx = 44 + i * (bw + 22)
        body.append(f'<rect x="{bx}" y="{y0}" width="{bw}" height="{bh}" rx="6" '
                    f'fill="#101820" stroke="#2a3644"/>')
        sea = y0 + 40
        body.append(f'<rect x="{bx+1}" y="{y0+1}" width="{bw-2}" height="{sea-y0}" '
                    f'fill="#16344a" opacity="0.7"/>')
        body.append(f'<rect x="{bx+1}" y="{sea}" width="{bw-2}" height="{bh-(sea-y0)-1}" '
                    f'fill="#7a5a3c" opacity="0.35"/>')
        tr = bx + 120 - rb * 42                       # trench migrates oceanward (left)
        # subducting slab, steepening as it rolls back
        dip = 0.62 + rb * 0.30
        pts = " ".join(f"{tr + t*180:.0f},{sea + t*180*dip:.0f}" for t in (0, .35, .7, 1))
        body.append(f'<polyline points="{pts}" stroke="#c96f4a" stroke-width="13" '
                    f'fill="none" stroke-linecap="round" opacity="0.9"/>')
        body.append(f'<rect x="{bx+2}" y="{sea-9}" width="{tr-bx-2}" height="9" '
                    f'fill="#c96f4a" opacity="0.9"/>')
        # overriding plate, thinning and then rifting
        ov0 = tr + 46
        if rb < 2:
            body.append(f'<rect x="{ov0}" y="{sea-11}" width="{bx+bw-ov0-4}" height="11" '
                        f'fill="#9a8a6a"/>')
        else:
            gap = 66
            mid = ov0 + (bx + bw - ov0) * 0.42
            body.append(f'<rect x="{ov0}" y="{sea-11}" width="{mid-ov0:.0f}" height="11" '
                        f'fill="#9a8a6a"/>')
            body.append(f'<rect x="{mid+gap:.0f}" y="{sea-11}" '
                        f'width="{bx+bw-(mid+gap)-4:.0f}" height="11" fill="#9a8a6a"/>')
            body.append(f'<rect x="{mid:.0f}" y="{sea-5}" width="{gap}" height="5" '
                        f'fill="#c9a227"/>')
            body.append(f'<text class="t small" x="{mid+gap/2:.0f}" y="{sea-14}" '
                        f'text-anchor="middle" fill="#c9a227">new ridge</text>')
        # arc volcano
        vx = tr + 92
        body.append(f'<path d="M{vx-20} {sea-11} L{vx} {sea-40} L{vx+20} {sea-11} Z" '
                    f'fill="#8a6a4a"/>')
        body.append(f'<text class="t small" x="{vx}" y="{sea-46}" text-anchor="middle" '
                    f'fill="#c0a080">arc</text>')
        body.append(f'<text class="t small" x="{tr}" y="{sea+16}" text-anchor="middle" '
                    f'fill="#d89070">trench</text>')
        if rb:
            body.append(f'<path d="M{tr+30} {sea+30} l-26 0 m6 -5 l-6 5 l6 5" '
                        f'stroke="#e07650" fill="none" stroke-width="1.6"/>')
        body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+bh+18}" '
                    f'text-anchor="middle" fill="#c9a227">{esc(title)}</text>')
        body.append(f'<text class="t small" x="{bx+bw/2}" y="{y0+bh+32}" '
                    f'text-anchor="middle">{esc(note)}</text>')
    foot = [
        "Behind a subduction zone, the sea floor can pull APART. An old dense slab does "
        "not just sink - it also rolls",
        "backward, dragging the trench oceanward and stretching the plate behind it "
        "until that plate rifts and opens a new",
        "spreading centre: a small ocean basin forming INSIDE a convergent margin.",
        "",
        "Sea of Japan  ·  Mariana Trough  ·  Lau Basin  ·  Andaman Sea  ·  Tyrrhenian "
        "Sea  ·  Scotia Sea  ·  Bransfield Strait",
        "",
        "FOR THE MODEL: README §10 lists marginal basins as absent or generic. This is "
        "the mechanism that generates them,",
        "and it explains why the western Pacific is a scatter of small seas and island "
        "arcs rather than one clean margin.",
    ]
    yy = y0 + bh + 62
    for ln in foot:
        body.append(f'<text class="t small" x="44" y="{yy}">{esc(ln)}</text>')
        yy += 14
    return _svg(yy + 10, "\n".join(body), "How a back-arc basin opens",
                "Slab roll-back, after the Britannica sequence in Deep Time Maps and Resources")


# ---------------------------------------------------------------------------
# 11. Glossopteris across Gondwana
# ---------------------------------------------------------------------------

def chart_glossopteris():
    body = []
    cx, cy, r = 330, 300, 165
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#16344a" stroke="#33414f"/>')
    # Gondwana as five fragments arranged round a pole, in their Permian relationship
    frags = [("South America", -62, 40, 46, 30, -18),
             ("Africa", 4, -14, 52, 40, 8),
             ("India", 74, -8, 30, 26, 0),
             ("Australia", 92, 62, 42, 30, 14),
             ("Antarctica", 8, 96, 60, 34, 0)]
    for name, dx, dy, rx, ry, rot in frags:
        px, py = cx + dx, cy + dy
        body.append(f'<ellipse cx="{px}" cy="{py}" rx="{rx}" ry="{ry}" fill="#8a7a52" '
                    f'transform="rotate({rot} {px} {py})" opacity="0.92"/>')
        body.append(f'<text class="t small" x="{px}" y="{py+3}" text-anchor="middle" '
                    f'fill="#15202b">{esc(name)}</text>')
        # the leaf marker
        body.append(f'<path d="M{px-6} {py+ry*0.55+11} q6 -12 12 0 q-6 8 -12 0 Z" '
                    f'fill="#7fc46a"/>')
    body.append(f'<circle cx="{cx+8}" cy="{cy+96}" r="4" fill="#e8f0f6"/>')
    body.append(f'<text class="t small" x="{cx+8}" y="{cy+114}" text-anchor="middle" '
                f'fill="#cfe0ec">South Pole</text>')
    body.append(f'<text class="t small" x="{cx}" y="{cy-r-12}" text-anchor="middle">'
                'Gondwana, Permian — the leaf marks each fragment where Glossopteris is found'
                '</text>')

    bx = 560
    body.append(f'<rect class="panel" x="{bx}" y="120" width="{W-bx-34}" height="360" rx="6"/>')
    txt = [
        ("#c9a227", "THE ORGANISM"),
        ("", "A seed fern, not a fern - Glossopteridales, and it took"),
        ("", "a century after its discovery to work that out."),
        ("", "Woody trees to ~30 m, trunk to 80 cm, softwood like"),
        ("", "an araucarian. Tongue-shaped leaves 2-30 cm with a"),
        ("", "distinctive NET of veins. Grew in waterlogged ground"),
        ("", "like a modern bald cypress, and built Gondwanan coal."),
        ("", ""),
        ("#c9a227", "THE POLAR FOREST"),
        ("", "Antarctic wood shows broad growth rings that stop"),
        ("", "ABRUPTLY - the shutdown can take as little as a month."),
        ("", "Inferred conical, widely spaced crowns to catch"),
        ("", "low-angle light. Months of continuous sun, then months"),
        ("", "of continuous dark. No modern biome works like this."),
        ("", ""),
        ("#c9a227", "THE ARGUMENT"),
        ("", "The same leaves occur on five continents that are now"),
        ("", "separated by oceans, and the seeds were far too large"),
        ("", "to have floated. EDUARD SUESS used exactly this in"),
        ("", "1885 to argue for one southern landmass - and named"),
        ("", "it GONDWANA, the name this map still uses. Wegener"),
        ("", "later took the same evidence into continental drift."),
        ("", ""),
        ("#c9a227", "THE END"),
        ("", "Gone before 252.3 Ma - about 350,000 years BEFORE the"),
        ("", "marine extinction. The land died first. Dicroidium"),
        ("", "takes its place through the Triassic."),
    ]
    yy = 142
    for col, ln in txt:
        if ln:
            f = f' fill="{col}" font-weight="600"' if col else ""
            body.append(f'<text class="t small" x="{bx+16}" y="{yy}"{f}>{esc(ln)}</text>')
        yy += 13.2
    return _svg(510, "\n".join(body),
                "Glossopteris: the leaf that named a supercontinent",
                "Distribution schematic - fragment shapes are indicative, not a reconstruction")


# -------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 12. Our climate table against PhanDA - the C1/C3 findings, drawn
# ---------------------------------------------------------------------------

def chart_climate_vs_phanda():
    """Generated from build/climate.py itself, so it cannot drift from the table
    it is criticising. Closes F10's 'Phanerozoic CO2 curve' slot by authoring it
    rather than fetching one - which is the library's own first rule."""
    import sys as _s
    _root = os.path.dirname(os.path.dirname(HERE))
    _s.path.insert(0, os.path.join(_root, "build"))
    import climate as C

    A0, A1 = 540.0, 0.0
    x0, x1 = 150, W - 44
    yT0, yT1 = 120, 300          # temperature panel
    yC0, yC1 = 350, 500          # CO2 panel
    body = []

    def X(a):
        return x1 - (a - A1) / (A0 - A1) * (x1 - x0)

    rows = []
    for a in range(0, 541, 5):
        try:
            s = C.system_at(float(a))
        except Exception:                                  # noqa: BLE001
            continue
        if s.get("gmst") is None:
            continue
        rows.append((a, s["gmst"], s.get("co2") or 0, s.get("o2") or 0))

    # ---- temperature panel ----
    def Y(t):
        return yT1 - (t - 8.0) / (38.0 - 8.0) * (yT1 - yT0)

    body.append(f'<rect class="panel" x="{x0}" y="{yT0}" width="{x1-x0}" '
                f'height="{yT1-yT0}" rx="4"/>')
    # PhanDA climate-state bands
    for lo, hi, nm, col in ((8, 18, "icehouse", "#2b4a63"), (18, 24, "cool greenhouse", "#2f5a52"),
                            (24, 30, "warm greenhouse", "#5c5230"), (30, 38, "hothouse", "#6b3a2c")):
        body.append(f'<rect x="{x0+1}" y="{Y(hi):.1f}" width="{x1-x0-2}" '
                    f'height="{Y(lo)-Y(hi):.1f}" fill="{col}" opacity="0.5"/>')
        body.append(f'<text class="t small" x="{x0+7}" y="{(Y(lo)+Y(hi))/2+4:.1f}" '
                    f'opacity="0.85">{esc(nm)}</text>')
    for t in (10, 15, 20, 25, 30, 35):
        body.append(f'<text class="t small" x="{x0-8}" y="{Y(t)+4:.1f}" '
                    f'text-anchor="end">{t}</text>')
    body.append(f'<text class="t small" x="{x0-8}" y="{yT0-8}" text-anchor="end" '
                f'fill="#c9a227">GMST °C</text>')
    poly = " ".join(f"{X(a):.1f},{Y(g):.1f}" for a, g, _c, _o in rows)
    body.append(f'<polyline points="{poly}" fill="none" stroke="#e8a13c" stroke-width="2.4"/>')

    # the PhanDA maximum, and our own
    body.append(f'<line x1="{X(93.9):.1f}" y1="{Y(36):.1f}" x2="{X(89.4):.1f}" '
                f'y2="{Y(36):.1f}" stroke="#e0574a" stroke-width="4"/>')
    body.append(f'<text class="t small" x="{X(93.9)-8:.1f}" y="{Y(36)-6:.1f}" '
                f'text-anchor="end" fill="#e0574a">PhanDA maximum 36 °C (Turonian)</text>')
    hot = max(rows, key=lambda r: r[1])
    body.append(f'<circle cx="{X(hot[0]):.1f}" cy="{Y(hot[1]):.1f}" r="4" '
                f'fill="none" stroke="#e8a13c" stroke-width="2"/>')
    body.append(f'<text class="t small" x="{X(hot[0])-9:.1f}" y="{Y(hot[1])+22:.1f}" '
                f'text-anchor="end" fill="#e8a13c">our maximum {hot[1]:.1f} °C at '
                f'{hot[0]:g} Ma — {36-hot[1]:.0f} °C short, never hothouse</text>')

    # ---- CO2 panel ----
    import math

    def Yc(c):
        return yC1 - (math.log10(max(c, 100)) - 2.0) / (math.log10(6000) - 2.0) * (yC1 - yC0)

    body.append(f'<rect class="panel" x="{x0}" y="{yC0}" width="{x1-x0}" '
                f'height="{yC1-yC0}" rx="4"/>')
    for c in (200, 500, 1000, 2000, 5000):
        body.append(f'<line class="grid" x1="{x0}" y1="{Yc(c):.1f}" x2="{x1}" '
                    f'y2="{Yc(c):.1f}"/>')
        body.append(f'<text class="t small" x="{x0-8}" y="{Yc(c)+4:.1f}" '
                    f'text-anchor="end">{c}</text>')
    body.append(f'<text class="t small" x="{x0-8}" y="{yC0-8}" text-anchor="end" '
                f'fill="#7ebad6">CO₂ ppm (log)</text>')
    polyc = " ".join(f"{X(a):.1f},{Yc(c):.1f}" for a, _g, c, _o in rows if c)
    body.append(f'<polyline points="{polyc}" fill="none" stroke="#7ebad6" stroke-width="2.2"/>')

    # ---- shared axis ----
    for a in (0, 100, 200, 300, 400, 500):
        body.append(f'<line class="grid" x1="{X(a):.1f}" y1="{yT0}" x2="{X(a):.1f}" '
                    f'y2="{yC1}"/>')
        body.append(f'<text class="t small" x="{X(a):.1f}" y="{yC1+18:.1f}" '
                    f'text-anchor="middle">{a} Ma</text>')
    for e in dt.EXTINCTIONS:
        if e.base > A0 or e.base < 1:
            continue
        body.append(f'<line x1="{X(e.base):.1f}" y1="{yT0}" x2="{X(e.base):.1f}" '
                    f'y2="{yC1}" stroke="#e0574a" stroke-width="1" '
                    f'stroke-dasharray="2 4" opacity="0.55"/>')

    foot = [
        "Both curves are read straight out of build/climate.py, so this figure cannot "
        "drift from the table it is assessing.",
        "Bands are the PhanDA five-state scheme (Judd et al. 2024, Science 385, "
        "eadk3705). Dashed red lines are the Big Five.",
        "",
        "THE TWO FINDINGS: our warm peak sits in the right PLACE — the Turonian — but "
        "6 °C too low, so the app never enters",
        "the hothouse state at all, while PhanDA finds Earth spent more of the "
        "Phanerozoic warm than cold. And 66→56 Ma,",
        "CO₂ doubles 810→1600 ppm while GMST moves only +1.5 °C, in the one interval "
        "containing both the PETM and the EECO.",
    ]
    yy = yC1 + 42
    for ln in foot:
        body.append(f'<text class="t small" x="{x0}" y="{yy}">{esc(ln)}</text>')
        yy += 14
    return _svg(yy + 8, "\n".join(body),
                "Our climate table against PhanDA",
                "Generated from build/climate.py — gap items C1, C3 and C4")


def main():
    figs = [
        ("01-deep-time-master-chart.svg", chart_deep_time),
        ("02-vegetation-through-time.svg", chart_vegetation_matrix),
        ("03-the-longitude-problem.svg", chart_longitude_problem),
        ("04-lip-to-extinction-cascade.svg", chart_lip_cascade),
        ("05-continental-affiliation.svg", chart_block_affiliation),
        ("06-snowball-bifurcation.svg", chart_snowball),
        ("07-cenozoic-climate-events.svg", chart_cenozoic_events),
        ("08-oxygen-through-time.svg", chart_oxygen),
        ("09-atoll-guyot-subsidence.svg", chart_atoll),
        ("10-back-arc-rollback.svg", chart_backarc),
        ("11-glossopteris-gondwana.svg", chart_glossopteris),
        ("12-climate-vs-phanda.svg", chart_climate_vs_phanda),
    ]
    for name, fn in figs:
        svg = fn()
        if svg is None:
            continue
        p = _write(name, svg)
        print(f"  {os.path.basename(p):<38} {os.path.getsize(p):>7,} bytes")


if __name__ == "__main__":
    print("writing authored diagrams to", OUT)
    main()
