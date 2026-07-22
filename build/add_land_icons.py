"""Redraw the plant/fungus icons that were too crude to identify, and add the
one organism that no existing drawing could stand in for.

The audit that prompted this found Malvinokaffric FLORA drawing a reptile. That
was a rules bug and is fixed. This is the other half: three of the drawings the
flora now maps to were a blob on a stick (broadleaf), four stacked triangles
(conifer) and a plain toadstool (fungus) -- fine as pictograms, useless as
identification. Coordinates are the icon set's 64x40 box, ground at y=39.

Idempotent: run as many times as you like.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")

NEW = {

# A deciduous angiosperm tree: root-flared trunk, two visible limbs, and a
# three-lobed crown with a scalloped underside instead of one round blob.
"broadleaf":
 '<path d="M28.8 39q1.2-3 1.2-8l-.6-9h5.2l-.6 9q0 5 1.2 8z"/>'
 '<path d="M32 31.5l-6.2-5.2M32 28.2l6.2-4.6" fill="none" stroke="currentColor"'
 ' stroke-width="1.8" stroke-linecap="round"/>'
 '<path d="M32 3c5.4 0 9.9 2.8 11.5 6.9 4.6.4 8.1 3.6 8.1 7.6 0 4.4-4 7.9-9.1 '
 '7.9H21.5c-5 0-9.1-3.5-9.1-7.9 0-4 3.5-7.2 8.1-7.6C22.1 5.8 26.6 3 32 3z"/>'
 '<path d="M17.4 24.6q4.3 4.6 8.6 0zM27.7 24.6q4.3 4.6 8.6 0zM38 24.6q4.3 4.6 '
 '8.6 0z"/>',

# A spruce: four whorls with concave, drooping undersides -- the silhouette that
# actually separates a conifer from a stack of triangles -- and a bare trunk. A
# seed cone was drawn here too and cut: same fill as the tree, so it read as a
# bite taken out of the branch rather than a cone.
"conifer":
 '<path d="M30.5 39h3l-.5-5.5h-2z"/>'
 '<path d="M32 22.5L45.5 36Q32 31.4 18.5 36Z"/>'
 '<path d="M32 14.5L42.5 27Q32 23 21.5 27Z"/>'
 '<path d="M32 7.5L39.8 18.6Q32 15.1 24.2 18.6Z"/>'
 '<path d="M32 2.2L36.8 11.2Q32 8.6 27.2 11.2Z"/>',

# A gilled mushroom, which is the point -- a cap with no gills is a parasol.
# Cap, gill band knocked out into teeth, ring on the stem, and a second smaller
# fruiting body, because fungi almost never appear singly.
"fungus":
 '<path d="M29.1 39q1.2-6.8 1-13.6h3.8q-.2 6.8 1 13.6z"/>'
 '<path d="M28 25.6h8v2.4h-8z"/>'
 '<path d="M20.6 19.4h22.8v2.7H20.6z"/>'
 '<path d="M23.2 19.4h1.4v2.7h-1.4zM27 19.4h1.4v2.7H27zM30.8 19.4h1.4v2.7h-1.4z'
 'M34.6 19.4h1.4v2.7h-1.4zM38.4 19.4h1.4v2.7h-1.4z" fill="var(--ko)"/>'
 '<path d="M32 4.4c8.8 0 15.4 6.2 15.9 12.1.2 1.8-1.1 2.9-3.6 2.9H19.7c-2.5 0'
 '-3.8-1.1-3.6-2.9C16.6 10.6 23.2 4.4 32 4.4z"/>'
 '<path d="M12.5 39q.8-4.8.7-9.2h2.4q-.1 4.4.7 9.2z"/>'
 '<path d="M14.4 22.8c4.7 0 8.2 3.4 8.4 5.9.1 1-.5 1.5-1.7 1.5H7.7c-1.2 0-1.8'
 '-.5-1.7-1.5.2-2.5 3.7-5.9 8.4-5.9z"/>',

# Prototaxites has no stand-in. It was a tapering trunk up to eight metres tall
# standing over a landscape whose plants were knee-high, and drawing it as a
# mushroom loses the only thing anyone remembers about it -- the scale. The
# knee-high forks at its feet are the whole illustration.
"prototaxites":
 '<path d="M24.6 39q-.4-10.4 1.4-19.8Q27.6 12 29.9 7.8q.9-1.9 2.1-1.9t2.1 1.9'
 'q2.3 4.2 3.9 11.4Q39.8 28.6 39.4 39z"/>'
 '<path d="M29.6 16.4q-1.5 10.6-1.2 20.6M34.4 16.4q1.5 10.6 1.2 20.6" '
 'fill="none" stroke="var(--ko)" stroke-width="1"/>'
 '<path d="M13 39V26.4M13 30.6l-4-3.8M13 30.6l4-3.8M13 34.8l-3-2.8M13 34.8l3'
 '-2.8" fill="none" stroke="currentColor" stroke-width="2" '
 'stroke-linecap="round"/>'
 '<path d="M51.4 39V28.6M51.4 32.2l-3.4-3.2M51.4 32.2l3.4-3.2M51.4 35.8l-2.6'
 '-2.4M51.4 35.8l2.6-2.4" fill="none" stroke="currentColor" stroke-width="2" '
 'stroke-linecap="round"/>',
}


def main():
    icons = json.load(open(ICONS))
    added = [k for k in NEW if k not in icons]
    redrawn = [k for k in NEW if k in icons]
    icons.update(NEW)
    json.dump(icons, open(ICONS, "w"))
    print(f"icons: {len(icons)} total; added {added}; redrawn {redrawn}")


if __name__ == "__main__":
    main()
