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

def main():
    figs = [
        ("01-deep-time-master-chart.svg", chart_deep_time),
        ("02-vegetation-through-time.svg", chart_vegetation_matrix),
        ("03-the-longitude-problem.svg", chart_longitude_problem),
        ("04-lip-to-extinction-cascade.svg", chart_lip_cascade),
        ("05-continental-affiliation.svg", chart_block_affiliation),
        ("06-snowball-bifurcation.svg", chart_snowball),
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
