"""Redraw the fauna icons that could not be identified from the drawing.

Companion to add_land_icons.py, which did the same for plants. The audit here
was: render all 54 fauna icons at size and ask, of each, "if the caption were
removed, could you name the group?" Sixteen failed, and they were not the rare
ones -- plankton is the single most-used fauna drawing in the data (46 taxa) and
was a shapeless cloud of blobs; dickinsonia was pixel-identical to bivalve (a
circle with a line down it); fish, jawless, shark, whale, ichthyosaur and
mosasaur were the same featureless oval with a tail, so a hagfish-grade agnathan
and a 15 m marine lizard drew the same picture.

The rule applied: draw the feature that makes the group that group. A whale is
its horizontal fluke, a brachiopod is its pedicle, a trilobite is its three
lobes, an ostracoderm is its head shield, a nautiloid is its chambers.

Coordinates are the icon set's 64x40 box; ground, where an icon has one, is
y=39. Fill is currentColor; var(--ko) is the knockout colour used for interior
detail (eyes, sutures, segment lines). Idempotent.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")


def ko(d, w=1.3):
    """A knockout stroke -- interior detail cut into a solid silhouette."""
    return (f'<path d="{d}" fill="none" stroke="var(--ko)" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def solid(d):
    return f'<path d="{d}" fill="none" stroke="currentColor" ' \
           f'stroke-width="{{w}}" stroke-linecap="round"/>'


def stroke(d, w=2.4):
    return (f'<path d="{d}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def eye(x, y, r=1.7):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--ko)"/>'


# --- plankton: a chambered foraminifer, not a cloud of blobs. Built as a
#     spiral of overlapping chambers, which is exactly how the shell grows,
#     with two diatoms alongside. Distinct from acritarch, which is the
#     spiky-sphere drawing.
def _foram():
    import math
    parts = []
    cx, cy = 25.0, 20.5
    n = 8
    for i in range(n):
        ang = math.radians(-90 + i * (360.0 / n) * 1.02)
        rad = 3.2 + i * 0.72          # chambers enlarge along the spiral
        dist = 3.0 + i * 0.62
        x = cx + math.cos(ang) * dist
        y = cy + math.sin(ang) * dist
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}"/>')
    sutures = []
    for i in range(n):
        ang = math.radians(-90 + (i + 0.5) * (360.0 / n) * 1.02)
        dist = 3.0 + i * 0.62
        x0 = cx + math.cos(ang) * (dist - 2.2)
        y0 = cy + math.sin(ang) * (dist - 2.2)
        x1 = cx + math.cos(ang) * (dist + 3.4 + i * 0.5)
        y1 = cy + math.sin(ang) * (dist + 3.4 + i * 0.5)
        sutures.append(f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}")
    return "".join(parts) + ko("".join(sutures), 1.1)


NEW = {

"plankton": _foram()
 + '<circle cx="51.5" cy="10.5" r="5.2"/>'
 + ko("M47.2 7.6h8.6M46.6 10.5h9.8M47.2 13.4h8.6", 1.1)
 + '<ellipse cx="52.5" cy="29" rx="7.6" ry="2.7" '
   'transform="rotate(-22 52.5 29)"/>'
 + ko("M48.4 32.2l1.6-4M51.4 30.8l1.6-4M54.4 29.4l1.6-4", 1.1),

# --- bivalve: two valves gaping on a hinge. The old drawing (a circle with a
#     line down the middle) was also the dickinsonia drawing.
"bivalve":
 '<path d="M31 7.4c-6.4 1.2-19 7.6-19 16.4 0 4.8 4.2 8.6 9.8 8.6H31z"/>'
 '<path d="M33 7.4c6.4 1.2 19 7.6 19 16.4 0 4.8-4.2 8.6-9.8 8.6H33z"/>'
 + ko("M27.4 12.6q-9 5.4-11.6 12M28.6 17.4q-7.4 4.6-9.4 10.2"
      "M36.6 12.6q9 5.4 11.6 12M35.4 17.4q7.4 4.6 9.4 10.2", 1.2),

# --- brachiopod: symmetric about the midline, beaked, and ATTACHED BY A
#     PEDICLE -- which is the character that separates it from a clam and the
#     reason it can be drawn differently at all.
"brachiopod":
 '<path d="M32 4.6c9.8 0 17.4 5.8 17.4 12.2 0 7.4-7.8 14-17.4 14S14.6 24.2 14.6 '
 '16.8C14.6 10.4 22.2 4.6 32 4.6z"/>'
 '<path d="M28.8 29.8h6.4L32 34.6z"/>'
 + stroke("M32 34.2v4.4", 2.0)
 + ko("M32 33q-.6-13 0-27M27.2 32.2q-3.6-12-5.6-22.6M36.8 32.2q3.6-12 5.6-22.6"
      "M22.4 29.6q-5-8.6-7.2-15.4M41.6 29.6q5-8.6 7.2-15.4", 1.2),

# --- dickinsonia: a quilted oval of transverse isomers offset across the
#     midline (glide symmetry, not mirror symmetry) -- the whole reason it is
#     an argued-over Ediacaran and not obviously an animal.
"dickinsonia": (lambda: (
    '<ellipse cx="32" cy="20" rx="12.6" ry="16.6"/>'
    + ko("M32 4.2v31.6", 1.5)
    + ko("".join(
        "M32 {y0:.1f}q-6.4 .4-10.6 {dy:.1f}".format(
            y0=6.4 + i * 3.4, dy=1.6 + i * 0.18) for i in range(9)), 1.15)
    + ko("".join(
        "M32 {y0:.1f}q6.4 .4 10.6 {dy:.1f}".format(
            y0=8.1 + i * 3.4, dy=1.6 + i * 0.16) for i in range(8)), 1.15)))(),

# --- worm: a segmented annelid. Was a bare squiggle, which named nothing.
"worm": (lambda: (
    "".join(
        '<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{ry:.1f}" '
        'transform="rotate({a} {x:.1f} {y:.1f})"/>'.format(
            x=x, y=y, r=r, ry=r * 0.86, a=a)
        for x, y, r, a in [(8.6, 30.4, 3.7, -12), (15.4, 28.6, 4.0, -18),
                           (22.0, 25.8, 4.1, -28), (27.8, 21.8, 4.1, -38),
                           (33.0, 17.4, 4.0, -46), (39.0, 13.9, 3.9, -26),
                           (45.8, 12.2, 3.7, -10), (52.0, 12.4, 3.4, 6)])
    + ko("M10.6 33.4l2-5.6M17.6 31.4l1.6-5.8M24.2 28.2l2.2-5.4"
         "M30.2 24.2l2.8-4.8M36.0 19.6l3.4-4.2M42.4 15.6l1.6-5.6"
         "M48.8 14.2l.8-5.8", 1.15)
    + stroke("M54.6 10q3.4-2.6 5.6-2.2M54.8 14.8q3.6 1.4 5.4.8", 1.6)))(),

# --- nautiloid: an orthocone with its chambers showing, plus the tentacles.
#     A plain cone with three lines could have been anything.
"nautiloid":
 '<path d="M22 12L56 18.4c1.5.3 1.5 3.2 0 3.5L22 28z"/>'
 + ko("M28 13.2v13.6M33.8 14.4v11.2M39 15.4v9.2M43.8 16.3v7.4"
      "M48 17.1v5.8M51.6 17.8v4.4", 1.15)
 + '<path d="M22.4 12.6c-4.6 0-8 3.2-8 7.4s3.4 7.4 8 7.4z"/>'
 + stroke("M15.6 14.6q-5.4-.6-8.8 1.4M14.4 17.4q-6-1.4-9.8 0"
          "M14 20q-6.2-.4-10 1.2M14.4 22.6q-5.8 1-9.4 3"
          "M15.6 25.4q-5 2-7.8 4.6", 1.9)
 + eye(19, 20.2, 1.9),

# --- fish: fins. A ray-finned fish drawn without a dorsal, pelvic or gill
#     cover is just an oval, which is what six other groups also were.
"fish":
 '<path d="M8 20.4c6-6.8 14.6-10.4 23.4-10.4 6.3 0 11.8 1.9 15.6 4.8v11.2'
 'C43.2 29 37.7 30.8 31.4 30.8 22.6 30.8 14 27.2 8 20.4z"/>'
 '<path d="M46.6 15L57 8.2v24.4L46.6 25.8z"/>'
 '<path d="M27.4 10.6q3.8-6.4 9.6-7.4-2.6 4-3.2 8z"/>'
 '<path d="M26.6 29.6q1.4 5.4 5.4 7.4-4.6-.2-7.8-3.6z"/>'
 '<path d="M38 29.8q1.2 3.8 4 5.4-3.6 0-5.8-2.6z"/>'
 + ko("M20.4 12.6q-2.2 7.8 0 15.6", 1.4)
 + eye(15.4, 18.4, 1.9),

# --- jawless: an ostracoderm is a broad head SHIELD with a narrow trunk behind
#     it, eyes set close together on TOP, no jaw and no paired fins. Given a
#     forked tail and a pectoral fin it just becomes the fish drawing again.
"jawless":
 '<path d="M6.6 21.4c0-5.6 6.6-10 14.8-10 5.8 0 10.8 2.2 13.4 5.6l-.2 9.2'
 'c-2.6 3.4-7.6 5.6-13.2 5.6-8.2 0-14.8-4.6-14.8-10.4z"/>'
 '<path d="M34.6 17.6L47.4 19.8v2.2l-12.8 2.4z"/>'
 '<path d="M46.6 19.6l9.8-7.6-1.6 18-8.2-7.6z"/>'
 '<path d="M39.2 18q1.4-4.6 4.4-5.8-1.2 3.2-1.4 5.4z"/>'
 + ko("M8.8 25.6q6 3.4 13.6 3.4", 1.3)
 + ko("M12.4 17.2q4-2.6 9.4-2.6", 1.2)
 + eye(17.2, 14.8, 1.5) + eye(22.2, 14.6, 1.5),

# --- shark: gill slits and a strongly heterocercal tail -- the upper lobe is
#     roughly twice the lower, and a symmetric tail just reads as a tuna.
"shark":
 '<path d="M3.6 20.8c7-7.6 16.2-11.4 26-11.4 6 0 11.4 1.8 15.2 4.6l.2 12.2'
 'C41.2 28.8 35.8 30.6 29.6 30.6c-9.8 0-19-3.8-26-9.8z"/>'
 '<path d="M44.6 14L60.5 1.6l-5.2 19L60.5 30l-15.9-6z"/>'
 '<path d="M26.4 10.2q3.8-7.6 9.4-8.8-2.8 4.6-3.4 9.4z"/>'
 '<path d="M24.6 29.6q0 6.4 3.2 9-5.4-1.6-8-7.2z"/>'
 '<path d="M37.6 29.4q.8 4 3.4 5.8-3.8-.2-6-3z"/>'
 + ko("M18.4 13.8q-1.8 6.8-.6 12.8M21.6 13q-1.8 7.2-.6 13.6"
      "M24.8 12.6q-1.8 7.4-.6 14", 1.15)
 + eye(12.4, 18.6, 1.7),

# --- whale: the horizontal fluke, drawn big. With a fish tail it is a fish, and
#     with a small one it is still a fish. The blow is a tight V, because three
#     tall strokes off the head read as antlers.
"whale":
 '<path d="M4.6 22.6c4.4-7 12.8-11.4 23-11.4 8.6 0 15.8 3 20.2 6.8l.4 6.6'
 'C43.8 28.2 36.8 31 28.2 31 18 31 9 28.2 4.6 22.6z"/>'
 '<path d="M45.8 22.2q6.4-6.6 15.6-6.8-5.8 3.2-8.4 6.8 2.6 3.6 8.4 6.8'
 '-9.2-.2-15.6-6.8z"/>'
 '<path d="M32.6 11.8q3.8-5 7.8-5.2-3 3-3.8 6.2z"/>'
 '<path d="M18.6 29.2q1.2 5.8 5.6 8.4-5.8-1-9-6z"/>'
 + stroke("M11.4 10.4q-1.4-3.8-3.8-5.6M11.4 10.4q1.4-3.8 3.8-5.6", 1.8)
 + ko("M5.6 24.2q6.6 2.8 13.4 2.8", 1.3)
 + eye(11.4, 21, 1.6),

# --- ichthyosaur: long rostrum, enormous eye, lunate tail. It converged on the
#     dolphin, so the drawing has to show what a dolphin does not.
"ichthyosaur":
 '<path d="M3 20.6l14.6-5v9.6z"/>'
 '<path d="M15.6 14.8c4.2-1.8 8.8-2.8 13.4-2.8 7 0 13.2 2.2 17.4 5.6v5'
 'c-4.2 3.4-10.4 5.6-17.4 5.6-4.6 0-9.2-1-13.4-2.8z"/>'
 '<path d="M29.6 12.2q3.4-6 8.2-7-2.6 3.8-3.2 7.4z"/>'
 '<path d="M24 27.8q-1.2 6.2 1.8 9.2-5.2-1.8-7.6-7.2z"/>'
 '<path d="M37.4 27.6q0 4.4 2 6.6-4.2-1.2-6-5z"/>'
 '<path d="M45.6 17.8L58 8.6l-3.4 11.8L58 32.2l-12.4-9z"/>'
 + eye(20.4, 18.6, 2.6),

# --- mosasaur: a long toothed jaw, four paddles and a downturned tail fin.
"mosasaur":
 '<path d="M3 18.6l13.6-3.2 1 7.6L3.6 21.8z"/>'
 '<path d="M15.4 15c4.8-1.4 9.8-1.8 15-1.2 8.2 1 14.6 3.8 19 7.6l-1.6 5.4'
 'c-4.6-2.8-10.6-4.6-17.8-5-5-.3-10.2-1.4-15-3.2z"/>'
 '<path d="M22 24.2q-1.6 5.8.8 8.8-5.2-2.2-6.8-7.6z"/>'
 '<path d="M35.4 27q-.8 4.8 1.4 7.2-4.6-1.6-6-5.8z"/>'
 '<path d="M46.6 21.6l10.4-4.4-2.6 7.6 5.6 9.8-13.8-7.6z"/>'
 + ko("M4 20.6l12.4 1.2", 1.2)
 + ko("M6.6 19.4l.8 1.8M9.6 19.8l.8 1.8M12.6 20.2l.8 1.8", 1.0)
 + eye(14.4, 17.4, 1.5),

# --- trilobite: three lobes. The name of the group was the thing the drawing
#     was missing -- an axial lobe with a pleural lobe either side. Genal spines
#     sweep BACK along the body; stuck out sideways they read as ears, and an
#     outlined glabella between two big eyes reads as a face.
"trilobite": (lambda: (
    '<path d="M32 3.4c-9.2 0-16 4.6-16 10.2 0 .9.1 1.8.4 2.6h31.2c.3-.8.4-1.7.4'
    '-2.6 0-5.6-6.8-10.2-16-10.2z"/>'
    '<path d="M16.6 17.2h30.8c-.5 6.9-1.9 12.6-4.2 16.3-2.2 3.5-5.9 5.1-10.8 '
    '5.1s-8.6-1.6-10.8-5.1c-2.3-3.7-3.7-9.4-4.2-16.3z"/>'
    '<path d="M17 14.4l-8.6 10 3.2 1.6 6.4-7.4zM47 14.4l8.6 10-3.2 1.6-6.4'
    '-7.4z"/>'
    + ko("M27.2 6.4q-1 13.6 1.4 27.6M36.8 6.4q1 13.6-1.4 27.6", 1.5)
    + ko("".join("M{x0:.1f} {y:.1f}q{dx:.1f} 1.5 {dx2:.1f} 0".format(
        x0=17.6 + i * 1.0, y=20.4 + i * 3.5,
        dx=(28.8 - i * 2.0) / 2, dx2=28.8 - i * 2.0) for i in range(4)), 1.3)
    + eye(24.4, 10.6, 1.5) + eye(39.6, 10.6, 1.5)))(),

# --- crab: chelae, drawn big and open. A crab without claws is a beetle, and
#     eyes on stalks above a round body make it a tick.
"crab":
 '<ellipse cx="32" cy="24" rx="13" ry="7.8"/>'
 + stroke("M21.4 28.4l-7.6 5.6M20 24.6l-9 2M21 20.4l-7.8-3.6"
          "M42.6 28.4l7.6 5.6M44 24.6l9 2M43 20.4l7.8-3.6", 2.2)
 + stroke("M23.6 19.8L17.6 15M40.4 19.8l6-4.8", 2.8)
 + '<path d="M18.4 16.6q-3.6-4.8-9.6-6 2.4 2.6 3 5.2l-.6.8q-2.8-.4-5.6.8'
   ' 4.4 3.4 10.4 3z"/>'
 + '<path d="M45.6 16.6q3.6-4.8 9.6-6-2.4 2.6-3 5.2l.6.8q2.8-.4 5.6.8'
   '-4.4 3.4-10.4 3z"/>'
 + ko("M22 22.4q10-3.6 20 0M24 27.6q8 2.4 16 0", 1.2)
 + eye(27.4, 20.4, 1.7) + eye(36.6, 20.4, 1.7),

# --- reef: a REEF is an assemblage -- massive head, branching colony, plate --
#     which is what makes it a different drawing from a single coral.
"reef":
 '<path d="M2 39q7-6.4 17-6.4h26q10 0 17 6.4z"/>'
 '<path d="M15.6 33.6c-5.4 0-9.8-3.8-9.8-8.4s4.4-8.4 9.8-8.4 9.8 3.8 9.8 8.4'
 '-4.4 8.4-9.8 8.4z"/>'
 + ko("M7.6 21.4q8-3.4 16 0M6.4 25.4q9.2-3.6 18.4 0M7.6 29.4q8-3.4 16 0", 1.3)
 + stroke("M34 33.6V20.4M34 25l-5.6-5.4M34 23l5.6-6M28.4 19.6v-5.4"
          "M39.6 17v-5.4M28.4 14.2l-4-3.4M28.4 14.2l3.4-4"
          "M39.6 11.6l4-3.6M39.6 11.6l-3.4-4", 3.4)
 + '<ellipse cx="53" cy="24.4" rx="8.6" ry="2.2"/>'
 + '<path d="M51.4 33.2h3.2l-.8-8.8h-1.6z"/>'
 + ko("M46.4 24h13.2", 1.2),

# --- coral: staghorn. The give-away that the first two attempts were trees was
#     the tall bare trunk with a crown on top; a coral colony branches from
#     almost the base and spreads WIDER than it is tall.
"coral":
 '<path d="M17 39h30q-3.4-5.6-15-5.6T17 39z"/>'
 + stroke("M32 35.4V27.4", 6.0)
 + stroke("M32 28.4L21.4 19.4M32 28.4L26 14.6M32 28.4V12.4"
          "M32 28.4L38 14.6M32 28.4L42.6 19.4", 5.0)
 + stroke("M21.4 19.4l-4.6-4M26 14.6l-2.6-4.6M32 12.4V7.4"
          "M38 14.6l2.6-4.6M42.6 19.4l4.6-4", 3.8)
 + ko("M16.4 15h.1M23 9.6h.1M32 6.8h.1M41 9.6h.1M47.6 15h.1", 2.2),

# --- primate: an ape in profile -- brow, muzzle, long arms reaching past the
#     knees, knuckles on the ground. The old drawing was a featureless
#     gingerbread figure, and a knockout band across a round head reads as a
#     visor, which is how the first attempt here became an astronaut.
"primate":
 '<circle cx="32" cy="9.8" r="6.6"/>'
 '<path d="M32 17.8c-5.6 0-9.2 3.8-9.2 8.8 0 2.8 1 5.2 2.6 7l-1 5.4h4.2'
 'l1-4.4h4.8l1 4.4h4.2l-1-5.4c1.6-1.8 2.6-4.2 2.6-7 0-5-3.6-8.8-9.2-8.8z"/>'
 + stroke("M25 21q-6.4 3.4-8 11.6M39 21q6.4 3.4 8 11.6", 3.4)
 + '<circle cx="16.6" cy="33.6" r="2.6"/><circle cx="47.4" cy="33.6" r="2.6"/>'
 + ko("M27.8 6.8q4.2-1.8 8.4 0", 1.5)
 + '<ellipse cx="32" cy="13.2" rx="3.4" ry="2.4" fill="none" '
   'stroke="var(--ko)" stroke-width="1.2"/>'
 + eye(29.4, 9.4, 1.3) + eye(34.6, 9.4, 1.3),

# --- turtle: scutes. A domed oval with legs was a tortoise-shaped blob.
"turtle":
 '<path d="M32 9.6c9.4 0 16.6 5.4 16.6 11.8 0 4.6-3.4 7.6-8.4 7.6H23.8'
 'c-5 0-8.4-3-8.4-7.6C15.4 15 22.6 9.6 32 9.6z"/>'
 '<path d="M48 17.2q5.4-1.4 8.6 1.4-1.6 3.2-5.4 3.6-1.2-3-3.2-5z"/>'
 '<path d="M20 28.6h4l-.8 5.4h-3.6zM40 28.6h4l.4 5.4h-3.6z"/>'
 '<path d="M15.8 24.8q-4.6 1.8-6.4 5.2 4 1 7.4-1.4z"/>'
 + eye(53.4, 18.8, 1.5)
 + ko("M32 10.2v18.6M22.4 14.6q3 7 2.6 14M41.6 14.6q-3 7-2.6 14"
      "M17.2 22.4q7.4-3 14.8-3M46.8 22.4q-7.4-3-14.8-3", 1.3),

# --- cynodont: differentiated teeth and an upright gait, which is what makes
#     the group the story it is. Was a blob with a head.
"cynodont":
 '<path d="M4.4 18.4l10.6-3.6 1.8 6.6-11.4-1z"/>'
 '<path d="M15 15.2c4.6-1.6 9.6-2 14.8-1.2 8 1.2 14.4 4.2 18.6 8.4l-2.6 4.6'
 'c-4.4-3.4-10-5.6-16.8-6.4-4.8-.6-9.6-1.8-14-3.6z"/>'
 '<path d="M18.6 20.6h3.6l-.6 12.6h-3.6zM28 22.4h3.6l.4 10.8h-3.6z'
 'M40 25.6h3.6l1.8 8.2h-3.6zM47 27.4h3.6l2 6.4h-3.6z"/>'
 + stroke("M48.6 24.2q6 1.4 9.4 5.4", 2.2)
 + ko("M5.2 20.2l9.8 .6", 1.2)
 + ko("M7.4 18.8v2.2M10.4 19.2v2.4M13 19.6v2.2", 1.1)
 + eye(13.4, 16.8, 1.4),

# --- reptile: a sprawling lizard with a real gait, not a lozenge on pegs.
"reptile":
 '<path d="M8.6 17.8l9.4-2.4 1.4 5.6-9.8-.6z"/>'
 '<path d="M18.4 16.4c4.4-1.2 9-1.4 13.8-.6 7.6 1.2 13.6 4 17.6 8l-2.4 4.4'
 'c-4.2-3.2-9.6-5.2-16-6-4.6-.6-9-1.6-13-3.2z"/>'
 '<path d="M21.6 20.8l3.4 1-3.2 5.4-3.4-1.8zM31.4 22.6l3.4.8-2.4 5.6-3.6-1.4z'
 'M41.4 25.8l3.2 1.4-3.4 5-3.2-2z"/>'
 + stroke("M48.4 26.6q7 3 9.6 9.4", 2.2)
 + ko("M9.4 19.2l8.4 .4", 1.1)
 + eye(14.4, 16.6, 1.4),
}


def main():
    icons = json.load(open(ICONS))
    icons.update(NEW)
    json.dump(icons, open(ICONS, "w"))
    print(f"redrew {len(NEW)} fauna icons; {len(icons)} icons total")
    print(" ", ", ".join(sorted(NEW)))


if __name__ == "__main__":
    main()
