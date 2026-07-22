"""Bring every remaining illustration up to the detail level of the redrawn ones.

add_land_icons.py and redraw_fauna_icons.py fixed the drawings that failed
identification outright. This is the rest of the set: drawings that were not
wrong, just bare -- a dinosaur that was a body, a neck and two pegs, with no
skull, no foot and no teeth.

Detail here means diagnostic anatomy, not filigree. The icons render at 46x31
CSS pixels, so a hairline is mud; what reads at that size is silhouette, limb
separation, and two or three knockout accents (an eye, a suture, a row of
teeth). Every addition below is something that identifies the group: a
ceratopsian's frill fenestrae, a stegosaur's thagomizer, a placoderm's armour
sutures, a ginkgo leaf's split and venation.

Coordinates are the 64x40 box; ground, where an icon has one, is y=39. Fill is
currentColor; var(--ko) is the knockout colour (defined on .lifeicon in the app
-- it was undefined until 2026-07-21, which made every knockout invisible).
Idempotent.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")


def ko(d, w=1.3):
    return (f'<path d="{d}" fill="none" stroke="var(--ko)" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def st(d, w=2.4):
    return (f'<path d="{d}" fill="none" stroke="currentColor" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def eye(x, y, r=1.7):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--ko)"/>'


NEW = {

# --- theropod: a skull with jaws and teeth, a bird-like foot, and the tail held
#     out as a counterbalance. Was a body, a neck bar and two pegs.
"theropod":
 '<path d="M19 21.6c-6.6.8-13 4-19 9.6l3.2 3.4c5.2-4.8 10.4-7.4 16-8.2z"/>'
 '<path d="M17.6 22.8c0-5.8 6.4-9.8 14.8-9.8h5.6c5.8 0 9.8 3 9.8 7s-3.6 6.8'
 '-9.4 6.8H28.2c-6.8 0-10.6-1.4-10.6-4z"/>'
 '<path d="M45.4 18.4c1.4-4.6 4-8.2 7.8-10.6l2.4 3.4c-2.8 1.8-4.8 4.6-6 7.8z"/>'
 '<path d="M52.4 5.6l9.8-1.4.6 4.2-2.6.6.4 2.4-8.2 1.2z"/>'
 '<path d="M53 12l8.4-1.2.4 2.2-8 1.4z"/>'
 '<path d="M39.6 25c-3 1.4-4.8 3.6-5.4 6.4l3.6.8c.4-2 1.8-3.4 3.6-4.4z"/>'
 '<path d="M26.6 25.6l-2.8 7.6 4 1.4 2.6-7.6zM37.4 25.6l2.8 7.6-4 1.4-2.6-7.6z"/>'
 '<path d="M23 32.4l-1.4 5h4l1.2-4.4zM41 32.4l1.4 5h-4l-1.2-4.4z"/>'
 '<path d="M19.4 36.4h8.2v2.4h-8.2zM36.4 36.4h8.2v2.4h-8.2z"/>'
 + ko("M53.4 9.6l.6 1.8M56.4 9.2l.6 1.8M59.4 8.8l.6 1.8", 1.0)
 + eye(55.6, 7),

# --- sauropod: a deep barrel body with a neck and tail that TAPER, built from
#     two overlapping strokes each -- a constant-width bar reads as a stick with
#     a ball on it, which made the first attempt a frying pan.
"sauropod":
 st("M21 26.4L11.4 30.4", 6.6) + st("M12.8 29.8L1.4 34.4", 3.0)
 + '<ellipse cx="31" cy="24" rx="15" ry="9.8"/>'
 + st("M40 19.6L49.4 8.8", 7.4) + st("M47.8 10.8L56.4 3.6", 4.4)
 + '<path d="M53.6 1c3-1 5.4-.2 7 2.4-2 1.2-3.2 2.6-4 4.2l-5.2-2.4z"/>'
 + '<path d="M20.6 30.4l-2.4 8.6h5l2.2-8.2zM29.4 32.6l-1.6 6.4h5l1.4-6.2z'
   'M38 32.6l1.6 6.4h-5l-1.4-6.2zM45.4 30.4l2.4 8.6h-5l-2.2-8.2z"/>'
 + eye(56.4, 4.6, 1.4),
# --- hadrosaur: the duck bill and the hollow crest, which is the whole reason
#     anyone knows the group.
"hadrosaur":
 '<path d="M17 24.4c0-5.4 6.4-9.4 15-9.4h5c5.4 0 9.2 2.8 9.2 6.6s-3.4 6.4-8.8 '
 '6.4H27c-6.6 0-10-1.6-10-3.6z"/>'
 '<path d="M17.6 23.4c-6.2.6-12 3.4-17.6 8.4l3 3.4c4.8-4.2 9.6-6.6 14.8-7.4z"/>'
 '<path d="M44.4 20.6c1.2-4.4 3.6-8 7-10.4l2.4 3.4c-2.6 1.8-4.4 4.4-5.4 7.4z"/>'
 '<path d="M50.6 8.6c3.8-.6 6.8.4 9 3-2.4 1.4-4 3.2-4.8 5.4l-5.6 1z"/>'
 '<path d="M49 14.6l-6.2 2.4 1.4 3.6 6-1.6z"/>'
 '<path d="M52.4 3.2c3.6.6 5.8 2.6 6.6 6-2.6-.6-5-.4-7.2.6z"/>'
 '<path d="M25.6 27l-2.6 7.6 4 1.4 2.4-7.6zM37.4 27l2.6 7.6-4 1.4-2.4-7.6z"/>'
 '<path d="M21.6 34.2l-1.2 4.6h4l1-4zM41.4 34.2l1.2 4.6h-4l-1-4z"/>'
 + eye(52.6, 12.4, 1.5),

# --- ceratopsian: frill, brow horn, nose horn, parrot beak -- and nothing else,
#     because at 46 px an extra element merges with its neighbour. The frill has
#     to stand clear ABOVE the back or it reads as more body.
"ceratopsian":
 '<path d="M11 27.4c0-5 5.8-8.6 13.6-8.6h6.4c5 0 8.4 2.6 8.4 6s-3.2 5.8-8 '
 '5.8H21C14.8 30.6 11 29.2 11 27.4z"/>'
 + st("M12.4 26.6L2 31.6", 5.0)
 + '<path d="M32.4 11.4c8-3.6 14.8-1.8 20.2 5.4-4.8 6.2-11.4 8.6-19.8 7.4z"/>'
 + '<path d="M49.4 14.6l11.4 2.6-1 3.2-3.8-.6-.4 2.6-8.4-1.2z"/>'
 + '<path d="M56.2 22.4l6.2 1.8-1 2.6c-2.6-.2-4.8-1-6.4-2.4z"/>'
 + '<path d="M47.4 11.6l1.6-8 3.8 1.2-1.2 7.2z"/>'
 + '<path d="M57.6 15.4l4.4-4.6 2.2 2.6-3.8 4.4z"/>'
 + '<path d="M20.4 29.8l-2.4 7.4 3.8 1.4 2.2-7.4zM32.4 29.8l2.4 7.4-3.8 1.4'
   '-2.2-7.4z"/>'
 + ko("M39 9.6q3 5.6 2.2 12.4", 1.3)
 + eye(51, 17.6, 1.4),
# --- stegosaur: two ALTERNATING rows of plates and the four tail spikes. One
#     row of identical triangles is a sail, not a stegosaur. (The old path also
#     had a malformed number run in the third plate.)
"stegosaur":
 '<path d="M13.6 27c0-5.2 6.2-9 15.4-9h10c6.8 0 11.2 3.2 11.2 7.4s-4.4 7.2'
 '-11.2 7.2H29c-9.2 0-15.4-1.4-15.4-5.6z"/>'
 '<path d="M13.8 25.6c-4.6-.6-8.6-2.2-11.8-4.8l2.6-3.2c2.6 2 5.8 3.4 9.4 4z"/>'
 '<path d="M49.4 25.4c4.4.4 8.2 1.8 11.2 4l-2.2 3.4c-2.4-1.8-5.6-3-9.2-3.4z"/>'
 '<path d="M20.4 18.6c-1.8-4.6-1.4-8 1-10 2.6 2 4.2 5.4 4.8 10zM29.6 17.8'
 'c-.8-5.8-.2-9.8 1.6-11.8 2.4 2 3.8 6 4.4 11.8zM39.4 18.2c.2-5 1.2-8.4 2.8'
 '-10.2 1.8 1.8 2.8 5.2 3 10.2z"/>'
 '<path d="M25.4 12.6c-1-3-.6-5.2 1-6.6 1.6 1.4 2.6 3.6 2.8 6.6zM35 12.2'
 'c0-3.4.8-5.8 2.2-7 1.4 1.2 2.2 3.6 2.2 7z"/>'
 '<path d="M57.6 22.6l5.4-4.2 1.2 2.6-5.2 3.4zM58.6 26l6-1.6.4 2.8-6.2 1z'
 'M58.4 29.6l5.8 1.4-.8 2.6-5.6-1.6zM56.6 32.6l4.6 3.4-1.8 2.2-4.4-3.6z"/>'
 '<path d="M20.6 32.6l-2.4 6.8h4l2.2-6.6zM40 32.6l2.4 6.8h-4l-2.2-6.6z"/>'
 + eye(6.4, 19.6, 1.3),

"pterosaur":
 '<path d="M2 14.6l16.4-3.6.6 4.8-16.6 1.4z"/>'
 '<path d="M16.2 9.4l8.6 1.6 1 7-8.8.6z"/>'
 '<path d="M22.4 9.6q6.4-5.6 11.6-4.6-4.6 3.6-7 7.4z"/>'
 '<path d="M23.6 15.4c5.2 0 9.4 3.6 9.4 8.2s-4.2 8.2-9.8 8.2c-3.6 0-6.6-1.4'
 '-8.4-3.6l.4-9.8c1.8-2 4.8-3 8.4-3z"/>'
 '<path d="M28 17.4L57.6 6.4l1.8 4.8q-9.6 6.6-17 17Q34.4 23 28 17.4z"/>'
 '<path d="M17.6 31l-1.4 7h3.4l1.2-6.4zM25.6 31.2l1.4 6.8h-3.4l-1.2-6.2z"/>'
 + st("M28.4 17L57.4 6.6", 2.6)
 + ko("M33 15.4q6 4.6 11.4 11.4M39.6 12.2q5 4.4 9.4 10.4", 1.2)
 + eye(19.6, 13.2, 1.5),
"plesiosaur":
 '<ellipse cx="33" cy="23.4" rx="13" ry="8.6"/>'
 + st("M25 19L15.4 9.6", 6.4) + st("M16.8 11.2L8.4 3.6", 3.6)
 + '<path d="M9.8 5.8c-2-.8-2.8-2.8-2-4.6.8-1.8 2.8-2.6 4.6-1.8l5 2.2-2 4.6z"/>'
 + st("M45 24.6L57.4 26.2", 5.0)
 + '<ellipse cx="25.4" cy="33" rx="3.8" ry="7.6" '
   'transform="rotate(52 25.4 33)"/>'
 + '<ellipse cx="41.6" cy="33" rx="3.8" ry="7.6" '
   'transform="rotate(-52 41.6 33)"/>'
 + '<ellipse cx="25.8" cy="14.6" rx="3.4" ry="6.6" '
   'transform="rotate(-56 25.8 14.6)"/>'
 + '<ellipse cx="41.2" cy="14.6" rx="3.4" ry="6.6" '
   'transform="rotate(56 41.2 14.6)"/>'
 + eye(10.2, 3.6, 1.4),
# --- synapsid: the Dimetrodon sail is individual spines with a web between
#     them, and the jaw carries differentiated teeth -- the whole significance
#     of the group is those teeth.
"synapsid":
 '<path d="M15 26.4c0-4.4 5.4-7.6 13.4-7.6h9c5.6 0 9.4 2.8 9.4 6.4s-3.6 6.2-9 '
 '6.2H28.4c-8 0-13.4-1.4-13.4-5z"/>'
 '<path d="M4.6 20.4l10.8 3.4-.4 4-11.4-3.4z"/>'
 '<path d="M45.6 22.6l9-2.6 1.4 3.6-2.6 1 .6 2.4-8 1.6z"/>'
 '<path d="M46 27.4l8-1.4.4 2c-2.6 1.4-5.4 2-8.4 1.6z"/>'
 '<path d="M18.6 19.4c-.6-6.6.4-11 3-13.4 2.2 2.6 3 7 2.4 13.4zM26 18.6'
 'c-.8-8-.2-13.2 2-15.6 2.2 2.6 3 7.8 2.4 15.6zM33.6 18.6c-.6-8.2.2-13.4 2.4'
 '-15.8 2 2.6 2.8 7.8 2.2 15.8zM41 19.4c-.4-6.6.4-11 2.6-13.6 2 2.6 2.8 7 2.4 '
 '13.6z"/>'
 '<path d="M20 31.4l-2 7h3.8l1.8-6.8zM39.6 31.4l2 7h-3.8l-1.8-6.8z"/>'
 + ko("M48.4 25.6l.6 2M51.4 25.2l.6 2", 1.0)
 + eye(50.4, 22.8, 1.4),

# --- temnospondyl: a broad flat head far wider than the body, sprawling limbs
#     turned out at the elbow, and a swimming tail.
"temnospondyl":
 '<path d="M22 22.6c0-3.6 4.4-6.2 11-6.2h5c4.6 0 7.8 2.4 7.8 5.6s-3.2 5.4-7.4 '
 '5.4H31c-6 0-9-1.4-9-4.8z"/>'
 '<path d="M45.4 16.4c6.4 0 11.2 2.6 11.2 6.2s-4.8 6-11.2 6c-2.6 0-4.8-.6-6.4'
 '-1.6l.4-8.8c1.6-1.2 3.8-1.8 6-1.8z"/>'
 '<path d="M22.4 18.6c-6.4-.6-12.4 1.4-18 6l3.4 3.6c4.2-3.4 8.8-5 13.8-4.6z"/>'
 '<path d="M27.4 27.6q-3.4 4.4-3 8.8 4.2-2 6.4-7.4zM40.4 27.6q3.4 4.4 3 8.8'
 '-4.2-2-6.4-7.4zM27 16.6q-3.4-4-3-8 4.2 1.8 6.4 6.6zM40 16.6q3.4-4 3-8'
 '-4.2 1.8-6.4 6.6z"/>'
 + ko("M45.6 24.6q6 2.2 10.4 0", 1.2)
 + eye(47.4, 19.8, 1.5) + eye(47.4, 25.6, 1.5),

# --- tetrapod: the transitional animal -- a fish tail behind, four limbs with
#     digits below, and a flat head that still has the shape of a lobefin's.
"tetrapod":
 '<path d="M20 21.4c0-4 5-6.8 12.4-6.8h5.6c5 0 8.4 2.6 8.4 6s-3.4 5.8-8 5.8'
 'H29.4c-6.6 0-9.4-1.6-9.4-5z"/>'
 '<path d="M45.4 15c5.6 0 9.8 2.6 9.8 6s-4.2 5.8-9.8 5.8c-2.4 0-4.4-.6-5.8'
 '-1.6l.4-8.6c1.4-1 3.4-1.6 5.4-1.6z"/>'
 '<path d="M20.4 17.6c-4.4-.4-8.6.6-12.6 3l-3.6-6.2-2.6 10.6 2.6 10.4 3.6-6.2'
 'c4 2.4 8.2 3.4 12.6 3z"/>'
 '<path d="M26.6 26.4q-3.6 4-3.6 8.4 4.2-1.6 6.6-6.8zM39.4 26.4q3.6 4 3.6 8.4'
 '-4.2-1.6-6.6-6.8z"/>'
 + st("M23 34.8l-3 2.6M24.6 35.4l-1.4 3.4M26.6 35.4l.6 3.4"
      "M43 34.8l3 2.6M41.4 35.4l1.4 3.4M39.4 35.4l-.6 3.4", 1.4)
 + ko("M45.6 22.6q5.4 1.8 9.2 0", 1.2)
 + eye(47.6, 18.6, 1.5),

# --- lobefin: the fins are on fleshy LOBES -- that is the group, and the reason
#     the limb exists at all -- plus the diamond scale texture.
"lobefin":
 '<path d="M11 20.6c5.6-6.4 13.6-9.8 22-9.8 6 0 11 1.8 14.6 4.4v10.6'
 'c-3.6 2.6-8.6 4.4-14.6 4.4-8.4 0-16.4-3.4-22-9.6z"/>'
 '<path d="M47 15.4l9.6-6.4-2.6 11.6 2.6 11.6-9.6-6.4z"/>'
 '<path d="M25.6 28.8c1.6 2.6 2.2 5 1.8 7.4-3.6-1-5.8-3-6.6-5.8z"/>'
 '<path d="M26.6 34.2q-3.4 2.4-4.6 5.6-3-2.6-2.2-6z"/>'
 '<path d="M38.6 29.4c1.4 2.2 2 4.2 1.6 6.4-3.2-.8-5.2-2.6-5.8-5z"/>'
 '<path d="M39.4 33.4q-3 2-4 4.8-2.6-2.2-2-5.2z"/>'
 '<path d="M28.4 10.6q1-3.4 3.6-5-.6 3-.2 5.2zM40 12.4q2-2.6 5-3.2-1.6 2.4'
 '-2 4.4z"/>'
 + ko("M24.4 12.4q-2 8.4 0 16.4", 1.2)
 + eye(16.4, 18.6, 1.7),

# --- placoderm: head and thorax are bony ARMOUR PLATES with sutures between
#     them, and the "teeth" are shearing blades of the jaw bone itself.
"placoderm":
 '<path d="M8 20.4c0-5.6 6.6-10 15.6-10 6.6 0 12 2.4 14.8 6.2v8c-2.8 3.6-8.2 6'
 '-14.8 6C14.6 30.6 8 26 8 20.4z"/>'
 '<path d="M37.6 15.6c5.6 1 9.8 2.4 12.6 4.2l-.4 2.2c-2.8 1.8-7 3.2-12.4 4.2z"/>'
 '<path d="M49.6 18.4l9.4-4.6-2.2 8 2.6 7.6-9.8-5z"/>'
 '<path d="M22.6 30.2q-.6 4 1 6.4-4.6-1-6.6-5z"/>'
 '<path d="M25.4 10.8q2-3.6 5.4-4.8-1.4 3.2-1.4 5.6z"/>'
 + ko("M8.8 24.4q7 3.4 15 3.4M20.6 11q-1.6 8.4 0 17.4M28.4 12.2q-1.4 7.6 0 15.4"
      "M9.6 16.4q6-3 13.2-3", 1.2)
 + eye(14.6, 18.4, 1.8),
# ---------------------------------------------------------------- batch 2 ---
# Mammals, birds and arthropods. The mammals were all one body-with-four-pegs
# outline differing only in snout length, so a wolf, a horse and a mammoth were
# the same drawing at icon size.

# --- mammal: a generic small mammal -- ear, muzzle, four legs, naked tail.
"mammal":
 '<path d="M14.6 25c0-4.8 4.8-8.4 11.8-8.4h11.4c5.6 0 9.6 3 9.6 6.8s-3.6 6.4-9 '
 '6.4H24.6C18 29.8 14.6 27.8 14.6 25z"/>'
 '<path d="M44.6 17.4c5 0 8.8 2.8 8.8 6.4s-3.8 6.2-8.8 6.2c-2 0-3.8-.5-5.2'
 '-1.4l.4-9.8c1.4-.9 3.2-1.4 4.8-1.4z"/>'
 '<path d="M52.6 20.6l7.2 1.4-.2 3-7.2 1.2z"/>'
 '<path d="M44.4 17.8l-2.2-6.8 6.6 4.2z"/>'
 '<path d="M19.6 29l-2.4 9h4.2l2.2-8.6zM26.6 29.6l-1.8 8.4h4.2l1.6-8z'
 'M35.8 29.6l1.8 8.4h-4.2l-1.6-8zM42.8 29l2.4 9h-4.2l-2.2-8.6z"/>'
 + st("M15 24.4L5.8 19.8", 2.8) + st("M6.8 20.4L1.6 14.8", 1.8)
 + eye(48.4, 21.2, 1.5),

# --- carnivore: a deep chest, long legs, pricked ears, a canine in an open jaw
#     and a brush tail. The teeth are the group.
"carnivore":
 '<path d="M16 24c0-5 5-8.6 12-8.6h11c5.6 0 9.6 3 9.6 7s-3.6 6.6-9 6.6H25.6'
 'C19.4 29 16 27 16 24z"/>'
 '<path d="M43.6 15.4c5.4 0 9.4 3 9.4 7s-4 6.8-9.4 6.8c-2.2 0-4-.6-5.4-1.6'
 'l.4-10.6c1.4-1 3.2-1.6 5-1.6z"/>'
 '<path d="M52.2 19.2l8.4 1.6-.4 2.8-8.4 1z"/>'
 '<path d="M52.4 23.8l7.6-.8.2 2.2-7.6 1.2z"/>'
 '<path d="M41.6 15.6l-1.8-7.6 6.6 5.2zM48.4 15.2l2-6.4 3.4 5.6z"/>'
 '<path d="M19.6 28.4l-2.6 9.6h4.2l2.4-9.2zM26.6 29l-2 9h4.2l1.8-8.6z'
 'M36 29l2 9h-4.2l-1.8-8.6zM43 28.4l2.6 9.6h-4.2l-2.4-9.2z"/>'
 '<path d="M16.4 22.6c-5.6-2-9.8-5.8-12.8-11l3.8-2.2c2.6 4.4 6.2 7.4 10.8 9z"/>'
 '<ellipse cx="5.4" cy="10.4" rx="4.2" ry="3.4" transform="rotate(30 5.4 10.4)"/>'
 + ko("M55 23.4l1 2.6", 1.1)
 + eye(47.4, 19.4, 1.5),

# --- horse: long legs on hooves, a long face, a mane and a switch tail -- the
#     silhouette a browsing mammal does NOT have.
"horse":
 '<path d="M16 21.4c0-4.6 5-8 12-8h10c5.4 0 9.2 2.8 9.2 6.4s-3.4 6-8.6 6H25'
 'C18.8 25.8 16 24.2 16 21.4z"/>'
 + st("M41 18.6L48.6 9.4", 6.4)
 + '<path d="M46.6 9.2l9-6 2.8 4.4-7.4 6.4z"/>'
 + '<path d="M43.4 12.4q4.8-6.2 9.4-8.6-2 5.2-1.6 9.6z"/>'
 + '<path d="M20.6 24.6l-3 13.6h3.4l3.6-13.2zM27.4 25.4l-2.4 12.8h3.4l2.8'
   '-12.6zM35.6 25.4l2.4 12.8h3.4l-2.8-12.6zM41.6 24.6l3 13.6h-3.4l-3.6'
   '-13.2z"/>'
 + '<path d="M16.8 35.4h5.4v2.8h-5.4zM24.2 35.8h5v2.4h-5zM37 35.8h5v2.4'
   'h-5zM43.6 35.4h5.4v2.8h-5.4z"/>'
 + '<path d="M16 20.6c-4.8 1.4-8.4 4.8-10.8 10l3.6 2c1.8-4.2 4.4-6.6 7.6-7.8z"/>'
 + eye(51, 8.6, 1.4),

# --- proboscidean: a domed head standing PROUD of the back, an ear outlined
#     against it, a trunk that reaches the ground and a tusk. Without the trunk
#     reaching down it is a hippo, which is what the first two attempts were.
"proboscidean":
 '<path d="M9 23.4c0-6.6 6.2-11.4 15-11.4h8.4c7 0 12 4.2 12 9.6s-4.6 9.2-11.4 '
 '9.2H20.6C13.4 30.8 9 27.8 9 23.4z"/>'
 '<path d="M39.4 9.4c7.6 0 13 5 13 11.6S47 32.2 39.4 32.2c-1.6 0-3-.2-4.4'
 '-.6V10c1.4-.4 2.8-.6 4.4-.6z"/>'
 + st("M50.6 21.4L57.2 28.4", 5.6) + st("M57 27.4L57 37.2", 3.6)
 + '<path d="M46.2 25.6q9.2.6 14 5.8-1.4 2.4-3.8 1.8-4.8-4-11.4-4.8z"/>'
 + '<path d="M14.6 29.8l-2 9.2h5.6l1.8-8.8zM24 30.4l-1.4 8.6h5.6l1.2-8.4z'
   'M33.6 30.4l1.4 8.6h-5.6l-1.2-8.4zM42.6 29.8l2 9.2h-5.6l-1.8-8.8z"/>'
 + ko("M39.2 10.4q5 5.4 5 10.8 0 5.4-5 10.6", 1.4)
 + eye(46.4, 17.6, 1.5),

# --- marsupial: upright on one huge hind leg with the foot flat on the ground,
#     a thick tail counterbalancing it, and tall ears. The stance is the group.
"marsupial":
 '<path d="M21.6 26.4c-6.4 2-11.8 6.2-16 12.6h6.4c3.2-4 7.4-6.8 12.4-8.2z"/>'
 '<path d="M28.4 12.6c6.4 0 11 4.6 11 11 0 4.4-2 8-5.6 10l-9.6-1.4c-4-2.4-6'
 '-6-6-10.4 0-5.6 4.2-9.2 10.2-9.2z"/>'
 '<path d="M26.6 28.4l5 1.2-2.4 7.4-5-1.4z"/>'
 '<path d="M16.6 34.6h13.6c1.6 0 2.8 1 2.8 2.6s-1.2 2.6-2.8 2.6H16.6z"/>'
 '<circle cx="42" cy="13.4" r="5.2"/>'
 '<path d="M46.2 11l8.6 1.6-.4 3-8.6 1.2z"/>'
 '<path d="M39.4 8.8l-2-7.4 5.8 5.2zM45 8.2l2.6-6.8 2.6 6z"/>'
 '<path d="M37.6 18.6q4.4.8 6.4 3.6-4 1.4-7.4-.2z"/>'
 + ko("M28 22.6q4.2 3 4.4 7.4", 1.4)
 + eye(40, 12, 1.4),

# --- rodent: the ever-growing incisor, a round ear and a long naked tail.
"rodent":
 '<path d="M17 26c0-4.8 4.8-8.4 11.4-8.4h7.4c5.2 0 9 3 9 6.6s-3.6 6.4-8.6 '
 '6.4H26C20 30.6 17 28.8 17 26z"/>'
 '<circle cx="43.6" cy="23.4" r="6.6"/>'
 '<circle cx="42.4" cy="15" r="4"/>'
 '<path d="M49.4 21.6l6.8 1.4-.4 2.8-6.6 1z"/>'
 '<path d="M54.6 24.6l3 3.6-3.6.6z"/>'
 '<path d="M21.6 29.8l-1.8 7.8h3.6l1.6-7.6zM28 30.2l-1.4 7.4h3.6l1.2-7.2z'
 'M35 30.2l1.4 7.4h-3.6l-1.2-7.2z"/>'
 + st("M17.6 25.6L7 22", 2.2) + st("M8 22.4L2.4 27.6", 1.6)
 + ko("M41.6 14.4a2 2 0 0 0 0 1.4", 1.2)
 + eye(46.4, 20.4, 1.5),

# --- bird: a folded wing with flight feathers, a real foot, and tail feathers
#     that separate. Was a body, two pegs and an eye.
"bird":
 '<path d="M21.6 23.4c0-5.6 5.2-9.8 12.6-9.8 4.6 0 8.6 1.6 11 4.2l7.8-4.2'
 '-2.4 6.6 3 3-5.6.6c-1.8 5.2-7 8.6-13.8 8.6-7.4 0-12.6-4-12.6-9z"/>'
 '<path d="M21.8 22.4c-6-1.2-11-3.8-15.4-7.8l8 1.2-5.6-4.8 8.4 2.8'
 '-3.6-5.6 9 6.8z"/>'
 '<path d="M26.4 20c5-1.4 9.4-.6 13.2 2.4-3.2 3.6-6.8 5.6-10.6 6.2-2.4-2.6'
 '-3.2-5.4-2.6-8.6z"/>'
 '<path d="M29.6 31.6l-1.6 6.4h3l1.4-6zM36.6 31.6l1.6 6.4h-3l-1.4-6z"/>'
 + '<path d="M25.6 37.4h7v2.2h-7zM33.6 37.4h7v2.2h-7z"/>'
 + ko("M28.4 21.4q4.6.4 8.4 2.8M27.6 24.4q4.4.6 8 2.8", 1.1)
 + eye(44.6, 19.4, 1.6),

# --- insect: a dragonfly with FOUR wings and their venation, compound eyes and
#     a segmented abdomen. Two bare wings could be any flying thing.
"insect":
 '<path d="M29.4 12.6h5.2l-.6 5.4h-4z"/>'
 '<path d="M30.4 18h3.2l-1 19.4h-1.2z"/>'
 '<circle cx="32" cy="8.6" r="4.4"/>'
 '<path d="M29.6 13.6q-13-5.6-24-4 8 7.4 23 7.8zM34.4 13.6q13-5.6 24-4'
 '-8 7.4-23 7.8z"/>'
 '<path d="M29.8 18.6q-11.6 2-19.6 8 9.4 2.4 19.4-3.4zM34.2 18.6q11.6 2 19.6 8'
 '-9.4 2.4-19.4-3.4z"/>'
 + ko("M12 11.4q8 2.6 15.4 5M14.6 14.8q6.6 1.4 12.6 3"
      "M52 11.4q-8 2.6-15.4 5M49.4 14.8q-6.6 1.4-12.6 3"
      "M14.4 24.4q6.6-1.6 13-2.4M15.6 27.6q5.6-1.6 11.4-2.4"
      "M49.6 24.4q-6.6-1.6-13-2.4M48.4 27.6q-5.6-1.6-11.4-2.4", 1.0)
 + ko("M30.6 21.6h2.8M30.6 25h2.8M30.4 28.4h2.8M30.4 31.8h2.6", 1.1)
 + ko("M29.6 6.6a3 3 0 0 0-.4 3M34.4 6.6a3 3 0 0 1 .4 3", 1.2),

# --- myriapod: many segments, a leg pair on EVERY one, and antennae.
"myriapod": (lambda: "".join(
    '<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="4.2" ry="4.6"/>'.format(
        x=8 + i * 6.4, y=16 + (2.6 if i % 2 else 0)) for i in range(9))
    + '<circle cx="59.6" cy="16.8" r="4.6"/>'
    + "".join(
        '<path d="M{x:.1f} {y:.1f}l-1.6 7.4h2.6l2-7z"/>'.format(
            x=7 + i * 6.4, y=19.4 + (2.6 if i % 2 else 0)) for i in range(9))
    + '<path d="M62 12.6q4-3.4 2-7.6M62.6 14.4q4.6-1.6 5.6-6" fill="none" '
      'stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
    + eye(60.4, 15.4, 1.5))(),

# --- eurypterid: chelicerae in front, compound eyes on the prosoma, swimming
#     paddles, and the telson spike that ends it.
"eurypterid":
 '<path d="M32 2.4c-5.4 0-9.2 3.6-9.2 8 0 2.2.6 4 1.6 5.4h15.2c1-1.4 1.6-3.2 '
 '1.6-5.4 0-4.4-3.8-8-9.2-8z"/>'
 '<path d="M24.4 16.4h15.2l-.8 4.4H25.2zM25.4 22h13.2l-.8 4.4H26.2z'
 'M26.4 27.6h11.2l-.8 4.4H27.2z"/>'
 '<path d="M30.6 33.2h2.8l-.6 6.6h-1.6z"/>'
 '<path d="M22.8 17c-4.4 1.2-7.8 3.4-10.2 6.8l2.4 2.2c2-2.8 4.8-4.6 8-5.4z'
 'M41.2 17c4.4 1.2 7.8 3.4 10.2 6.8l-2.4 2.2c-2-2.8-4.8-4.6-8-5.4z"/>'
 '<ellipse cx="9.6" cy="26.4" rx="6.4" ry="3.4" transform="rotate(38 9.6 26.4)"/>'
 '<ellipse cx="54.4" cy="26.4" rx="6.4" ry="3.4" '
 'transform="rotate(-38 54.4 26.4)"/>'
 '<path d="M27.6 2.6q-3.4-1.6-4.6-4.6 3.6.4 5.8 2.8zM36.4 2.6q3.4-1.6 4.6-4.6'
 '-3.6.4-5.8 2.8z"/>'
 + ko("M25.6 12.6h12.8", 1.2)
 + eye(27.4, 8, 2) + eye(36.6, 8, 2),

# --- anomalocaris: the row of lateral swimming lobes down each side, the two
#     grasping appendages, and stalked eyes.
"anomalocaris": (lambda:
    '<path d="M22 20c0-5 4.4-8.6 11.4-8.6h13.2c5.6 0 9.4 2.8 9.4 6.4v4.4'
    'c0 3.6-3.8 6.4-9.4 6.4H33.4C26.4 28.6 22 25 22 20z"/>'
    + "".join(
        '<path d="M{x:.1f} 11.8q-1.6-4.6-.6-7.4 3.4 2 5 6.6z'
        'M{x:.1f} 28.2q-1.6 4.6-.6 7.4 3.4-2 5-6.6z"/>'.format(x=26 + i * 6.6)
        for i in range(5))
    + '<path d="M55.6 20.6q4.6.4 8 3.4-4 2.4-8.4 1.6z"/>'
    + '<path d="M23 16.6q-7.4-4.2-14.6-2.6 3.2 2.4 4.4 5-3.6 1-6.4 3.4'
      ' 8.4 3 16.6-1.4z"/>'
    + ko("M11.6 16.6l1.4 2.6M15.6 18.4l1.2 2.6M19.4 19.6l1 2.4", 1.1)
    + '<path d="M40 11.6l-1.6-6.4 4.6 4.6zM46 11.6l1.6-6.4-4.6 4.6z"/>'
    + eye(39.4, 5.6, 2) + eye(48, 5.6, 2)
    + ko("M28 15.6q12 4.4 24 0M28 24.4q12-4.4 24 0", 1.2))(),

# --- jellyfish: a bell with its radial canals, four frilled oral arms, and
#     trailing tentacles of different lengths.
"jellyfish":
 '<path d="M32 3.6c9.6 0 16.6 5.8 16.6 12.6 0 2.6-1 4.6-2.8 5.6-1.6-1.6-3.4'
 '-2.4-5.4-2.4s-3.8.8-5.4 2.4c-1 .8-2 1.2-3 1.2s-2-.4-3-1.2c-1.6-1.6-3.4-2.4'
 '-5.4-2.4s-3.8.8-5.4 2.4c-1.8-1-2.8-3-2.8-5.6C15.4 9.4 22.4 3.6 32 3.6z"/>'
 + st("M26 22.4q-1.6 7 .6 12M32 23.6q-1 7.6 1.4 12.8M38 22.4q1.6 7-.6 12", 2.6)
 + st("M20.6 22.6q-4 8.4-2.6 15.6M43.4 22.6q4 8.4 2.6 15.6"
      "M23.4 23.6q-1.6 6.4-.4 11.6M40.6 23.6q1.6 6.4.4 11.6", 1.5)
 + ko("M22.6 8.6q-3.4 3.6-4 8.4M32 5.6q0 6-.4 11.4M41.4 8.6q3.4 3.6 4 8.4", 1.3),
# ---------------------------------------------------------------- batch 3 ---
# Sessile animals, microbes and the plants that were still bare.

# --- sponge: a vase with the osculum open at the top and ostia in the wall.
"sponge":
 '<path d="M20.6 39c-2.2-8.6-2.8-17.2-1.8-25.8 3.4-2 7.4-3 12-3s8.6 1 12 3'
 'c1 8.6.4 17.2-1.8 25.8z"/>'
 '<ellipse cx="30.8" cy="13.2" rx="12.2" ry="3.6" fill="var(--ko)"/>'
 '<path d="M46.6 39c-1.4-5.6-1.8-11.2-1.2-16.8 2.2-1.3 4.8-2 7.8-2s5.6.7 7.8 2'
 'c.6 5.6.2 11.2-1.2 16.8z"/>'
 '<ellipse cx="53" cy="22" rx="7.9" ry="2.3" fill="var(--ko)"/>'
 + ko("M24 20h.2M29 22.6h.2M34.4 19.4h.2M26 27h.2M32.6 29h.2M37 25h.2"
      "M23.4 33h.2M30 34.6h.2M36 32.6h.2M49 28h.2M54.6 30.6h.2M52 34.6h.2", 2.0),

# --- graptolite: the saw-tooth thecae are the fossil -- a bare stick is a twig.
"graptolite": (lambda:
    '<path d="M30.6 3.4h3.6l-.6 34.8h-2.4z"/>'
    + "".join('<path d="M30.8 {y:.1f}l-8.4-2.6.6 6.2z'
              'M33.2 {y2:.1f}l8.4-2.6-.6 6.2z"/>'.format(
                  y=6.4 + i * 6.6, y2=9.7 + i * 6.6) for i in range(5))
    + st("M32.4 3.6V.4", 1.6))(),

# --- stromatolite: the point is the LAMINAE -- millimetre mats stacked into a
#     dome over thousands of years. A plain mound says nothing.
"stromatolite":
 '<path d="M4 39c0-12.4 6-21.4 17.4-21.4S38.8 26.6 38.8 39z"/>'
 '<path d="M38 39c0-8.2 4-14.2 11.6-14.2S61.2 30.8 61.2 39z"/>'
 + ko("M7.4 33.6q14-7 28 0M9.6 28.4q11.8-6.4 23.6 0M12.8 23.6q8.6-5 17 0"
      "M40.6 34.4q9-4.6 18 0M43 29.6q6.6-3.6 13.2 0", 1.3),

# --- microbe: rods with a flagellum, a dividing cell, and cocci -- the shapes
#     a light microscope actually shows.
"microbe":
 '<ellipse cx="18" cy="13" rx="10" ry="4.6" transform="rotate(-20 18 13)"/>'
 '<ellipse cx="40" cy="27" rx="10.6" ry="4.8" transform="rotate(14 40 27)"/>'
 '<circle cx="47.6" cy="11.6" r="5.2"/><circle cx="55.4" cy="15.8" r="3.4"/>'
 '<circle cx="12.4" cy="28.4" r="4.4"/><circle cx="21.2" cy="31.6" r="3"/>'
 + st("M27.4 8.6q6-2.6 6.6-6.6M50.6 30.4q6 2.6 9.6 1.4", 1.6)
 + ko("M14.4 14.6q3.6-2 7.2-3M36.6 28.4q3.8-1.4 7.2-1.6"
      "M47.6 6.6v10M12.4 24.2v8.4", 1.2),

# --- ginkgo: the leaf is a SPLIT fan of dichotomous veins, and the tree carries
#     a fleshy seed. Two plain lobes could be any leaf.
"ginkgo":
 '<path d="M30.6 27.4h2.8V39h-2.8z"/>'
 '<path d="M31 25.4C20.4 25 13.2 18.6 13.2 10.8c0-5.2 3.8-9 8.6-9 4.4 0 7.6 3 '
 '8.4 8.2z"/>'
 '<path d="M33 25.4c10.6-.4 17.8-6.8 17.8-14.6 0-5.2-3.8-9-8.6-9-4.4 0-7.6 3'
 '-8.4 8.2z"/>'
 + ko("M29.4 24.6q-6-7.4-8.6-15.4M27 23.6q-7-5.6-10.8-11.6"
      "M34.6 24.6q6-7.4 8.6-15.4M37 23.6q7-5.6 10.8-11.6M31 24.8V11"
      "M33 24.8V11", 1.1)
 + '<ellipse cx="39.6" cy="31.6" rx="3.6" ry="4.4"/>'
 + st("M33 28.4q4 .6 6 3", 1.5),

# --- moss: a leafy cushion with the sporophytes rising out of it -- thin setae
#     carrying small TILTED capsules. Round heads on bare wires are mushrooms.
"moss": (lambda:
    "".join('<path d="M{x} 39c-.6-4.4.6-7.6 3.6-9.6 2.4 2.4 3.4 5.6 3 9.6z"'
            '/>'.format(x=x) for x in (9, 16.4, 24, 32.4, 40, 47.6))
    + st("M18.4 32.6q-1.6-8.4-.4-14.4M28.4 31.6q1.6-7.8 3.6-12.8"
         "M39.6 33q-1.4-7-1-11.8M50 33.4q1.6-6 3.6-10", 1.5)
    + '<ellipse cx="17.6" cy="16.4" rx="2.4" ry="3.6" '
      'transform="rotate(-22 17.6 16.4)"/>'
    + '<ellipse cx="32.4" cy="16.6" rx="2.3" ry="3.5" '
      'transform="rotate(24 32.4 16.6)"/>'
    + '<ellipse cx="38.4" cy="19" rx="2.2" ry="3.4" '
      'transform="rotate(-18 38.4 19)"/>'
    + '<ellipse cx="54.2" cy="20.6" rx="2.1" ry="3.3" '
      'transform="rotate(26 54.2 20.6)"/>'
    + ko("M16.4 13.6q1.8-1 3.4-.4M31.4 13.8q1.6-1.2 3.2-.6", 1.0))(),

# --- seedfern: a pinnate frond with distinct leaflets AND the seeds it is named
#     for -- the plant that carried ovules on a fern-shaped leaf.
"seedfern": (lambda:
    '<path d="M30.8 39h2.6l-.4-24h-1.8z"/>'
    + "".join(
        '<path d="M32 {y:.1f}c-4.6-.4-8-2-10.2-4.8 3.6-1.6 7 -1 10.2 1.8z'
        'M32 {y:.1f}c4.6-.4 8-2 10.2-4.8-3.6-1.6-7-1-10.2 1.8z"/>'.format(
            y=8.4 + i * 5.2) for i in range(4))
    + '<path d="M32 4.4c-2.6-1.4-4.2-3.4-4.6-6 2.6.6 4.2 2.4 4.6 5.2'
      'c.4-2.8 2-4.6 4.6-5.2-.4 2.6-2 4.6-4.6 6z"/>'
    + '<circle cx="23.6" cy="30.6" r="3"/><circle cx="40.4" cy="30.6" r="3"/>'
    + '<circle cx="32" cy="34.4" r="3"/>'
    + st("M32 31.4l-7.6-.4M32 31.4l7.6-.4M32 31.4v2", 1.3))(),

# --- palm: leaflets on every frond, a ringed trunk and a bunch of fruit.
"palm": (lambda:
    '<path d="M29.6 39h5l-2.2-20h-2z"/>'
    + ko("M29.6 34.4h5M29.8 30.4h4.6M30 26.4h4.2M30.2 22.4h3.8", 1.2)
    + "".join(
        '<path d="M32 19.4q{dx:.1f} {dy:.1f} {dx2:.1f} {dy2:.1f}" fill="none" '
        'stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/>'
        .format(dx=dx * .55, dy=dy * .5, dx2=dx, dy2=dy)
        for dx, dy in [(-20, -1.6), (-14.6, -9), (-6, -13.6), (6, -13.6),
                       (14.6, -9), (20, -1.6)])
    + ko("M23 17.2l-2.4 4.2M15.4 16.4l-2.4 4.2M41 17.2l2.4 4.2"
         "M48.6 16.4l2.4 4.2M26.6 11l-3.6 3.4M37.4 11l3.6 3.4", 1.2)
    + '<circle cx="27" cy="21.6" r="2.4"/><circle cx="37" cy="21.6" r="2.4"/>'
    + '<circle cx="32" cy="23.6" r="2.4"/>')(),

# --- horsetail: jointed stem with a sheath at every NODE, whorled branches, and
#     the spore cone on top. The joints are why it is called Equisetum.
"horsetail": (lambda:
    '<path d="M30 39h4V9h-4z"/>'
    + "".join(
        '<path d="M25.6 {y}h12.8v2.6H25.6z"/>'
        '<path d="M29.6 {y}c-4-1-8-3.6-11.4-7.6M34.4 {y}c4-1 8-3.6 11.4-7.6" '
        'fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round"/>'.format(y=y) for y in (33, 26, 19, 12))
    + '<path d="M32 1c3 0 5.2 2.2 5.2 5 0 2.4-1.2 4.4-2.8 5.6h-4.8'
      'C27.8 10.4 26.6 8.4 26.6 6c0-2.8 2.2-5 5.4-5z"/>'
    + ko("M28.4 4.4h7.2M27.8 7.4h8.4", 1.2))(),

# --- grass: a seed head at the tip of every blade. Grass is defined by its
#     inflorescence, and the silica in it is why grazers grew tall teeth.
"grass": (lambda: (lambda B: "".join(
    '<path d="M{x} 39Q{cx:.1f} {cy:.1f} {tx} {ty}" fill="none" '
    'stroke="currentColor" stroke-width="2.3" stroke-linecap="round"/>'.format(
        x=x, tx=tx, ty=ty, cx=x + (tx - x) * .1, cy=(39 + ty) / 2 - 3)
    for x, tx, ty in B)
    + "".join(
        '<ellipse cx="{tx}" cy="{ty}" rx="2.4" ry="3.6" '
        'transform="rotate({r:.0f} {tx} {ty})"/>'.format(
            tx=tx, ty=ty, r=(tx - x) * 2.2) for x, tx, ty in B)
    )(
    [(8, 15.6, 14.4), (15.4, 9.6, 9.6), (23, 30.4, 16), (30.4, 24.4, 8),
     (38.6, 46, 15), (46, 40, 9.4), (53.4, 58.4, 17)]))(),

# --- flower: stem, leaves, and the stamens at the centre -- an angiosperm is
#     its reproductive organs, which is the whole point of the group.
"flower":
 '<path d="M30.8 22h2.4v17h-2.4z"/>'
 '<path d="M30.8 29.6c-3.6-.4-6.6-2.4-9-6 4-1.4 7-.2 9 3.6z'
 'M33.2 33.6c3.6-.4 6.6-2.4 9-6-4-1.4-7-.2-9 3.6z"/>'
 '<ellipse cx="43.6" cy="14.6" rx="6.4" ry="4.4"/>'
 '<ellipse cx="37.8" cy="5.6" rx="6.4" ry="4.4" transform="rotate(-60 37.8 5.6)"/>'
 '<ellipse cx="26.2" cy="5.6" rx="6.4" ry="4.4" transform="rotate(-120 26.2 5.6)"/>'
 '<ellipse cx="20.4" cy="14.6" rx="6.4" ry="4.4"/>'
 '<ellipse cx="26.2" cy="23.6" rx="6.4" ry="4.4" transform="rotate(-60 26.2 23.6)"/>'
 '<ellipse cx="37.8" cy="23.6" rx="6.4" ry="4.4" transform="rotate(-120 37.8 23.6)"/>'
 '<circle cx="32" cy="14.6" r="5.4"/>'
 + ko("M32 14.6l-3.4-3.4M32 14.6l3.4-3.4M32 14.6V10M32 14.6l-4 1.6"
      "M32 14.6l4 1.6M32 14.6l-2 3.8M32 14.6l2 3.8", 1.2),

# --- cycad: add the seed cone at the crown and leaflets on the fronds.
"cycad": (lambda:
    '<path d="M27.4 39h9.2l-1.6-13h-6z"/>'
    + '<path d="M27.8 35.4h8.4v1.8h-8.4zM28.2 31.4h7.6v1.8h-7.6z'
      'M28.6 27.6h6.8v1.8h-6.8z" fill="var(--ko)"/>'
    + "".join(
        '<path d="M32 26q{dx:.1f} {dy:.1f} {dx2:.1f} {dy2:.1f}" fill="none" '
        'stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/>'
        .format(dx=dx * .55, dy=dy * .48, dx2=dx, dy2=dy)
        for dx, dy in [(-19, -3), (-16, -10), (-10, -16), (-3.5, -19),
                       (3.5, -19), (10, -16), (16, -10), (19, -3)])
    + '<ellipse cx="32" cy="17.6" rx="3.4" ry="5.4"/>'
    + ko("M28.8 15.6h6.4M28.6 18.4h6.8M29.2 21.2h5.6", 1.1))(),
# --- ammonite: a coiled shell with RIBS across the whorl and the spiral itself
#     showing. The old drawing was a 200-point polyline dump of a spiral curve
#     that collapsed to a thin squiggle at icon size -- and this is the second
#     most-used fauna drawing in the data.
"ammonite": (lambda: (lambda m: (
    '<circle cx="26.6" cy="20" r="15.6"/>'
    + '<path d="M40.6 26.6q6 1.4 10.6 6-5 3.4-11.6 2.4z"/>'
    + m.st_tent
    + m.ribs + m.spiral
    + '<circle cx="26.6" cy="20" r="2.2" fill="var(--ko)"/>'))(
    type("m", (), {
        "ribs": '<path d="' + "".join(
            "M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}".format(
                x0=26.6 + __import__("math").cos(a) * 4.4,
                y0=20 + __import__("math").sin(a) * 4.4,
                x1=26.6 + __import__("math").cos(a) * 15.2,
                y1=20 + __import__("math").sin(a) * 15.2)
            for a in [__import__("math").radians(i * 24) for i in range(15)])
            + '" fill="none" stroke="var(--ko)" stroke-width="1.15"/>',
        "spiral": '<path d="' + "M" + " L".join(
            "{x:.1f} {y:.1f}".format(
                x=26.6 + (2.2 + t * 1.85) * __import__("math").cos(t),
                y=20 + (2.2 + t * 1.85) * __import__("math").sin(t))
            for t in [i * 0.22 for i in range(33)])
            + '" fill="none" stroke="var(--ko)" stroke-width="1.5"/>',
        "st_tent": '<path d="M50 29q5.4-1 9.6.6M50.6 31.6q5.4.6 9 3'
                   'M49.4 34q4.6 2 7.6 5" fill="none" stroke="currentColor" '
                   'stroke-width="1.9" stroke-linecap="round"/>',
    })))(),
}


def main():
    import xml.etree.ElementTree as ET
    bad = []
    for k, v in NEW.items():
        try:
            ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">%s</svg>' % v)
        except ET.ParseError as e:
            bad.append(f"{k}: {e}")
    if bad:
        raise SystemExit("refusing to write malformed SVG:\n  "
                         + "\n  ".join(bad))
    icons = json.load(open(ICONS))
    missing = [k for k in NEW if k not in icons]
    icons.update(NEW)
    json.dump(icons, open(ICONS, "w"))
    print(f"detailed {len(NEW)} icons; {len(icons)} total"
          + (f"; NEW KEYS {missing}" if missing else ""))
    print(" ", ", ".join(sorted(NEW)))


if __name__ == "__main__":
    main()
