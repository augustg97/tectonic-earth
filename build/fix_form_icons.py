"""Form icons that failed the test -- cover the caption, name the group -- and their fixes.

The form pass (build_silhouettes.py forms) takes the FIRST licensed PhyloPic
silhouette for a form's search term, and the first one is not always the one
that reads at 46 x 31 px: "Cocos nucifera" answers with a coconut rather than a
palm, "Zea mays" with a husked ear rather than a grass, "Crocodylus niloticus"
with a skull, "Phascolarctos" with a koala seen from the front. Those were found
on the contact sheet (verify_icons.py forms) and are pinned here to a candidate
that was LOOKED AT (verify/icons_cands.png), by search term and pick index.

Where nothing on PhyloPic reads at that size -- an orthocone is a hairline, a
chain coral from above is a lattice, a coccosphere is a disc -- the drawing is
made by hand in the 64 x 40 box, currentColor with var(--ko) knockouts, like the
other hand-drawn forms.

Idempotent. Run after build_silhouettes.py forms, then build_webdata.build_life().
"""
import json
import os
import xml.etree.ElementTree as ET

import phylopic

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "life_icons.json")
CREDITS = os.path.join(HERE, "life_credits.json")

#: icon key -> (PhyloPic search term, pick index), chosen by eye from icons_cands.png
PINNED = {
    "crocodile": ("Crocodylus", 0),          # C. moreletii in profile, tail curved
    "seal": ("Arctocephalus", 0),            # a fur seal hauled out, in profile
    "koala": ("Phascolarctos", 2),           # seated, in profile
    "snail": ("Stylommatophora", 1),         # Helix pomatia from the side
    "palm": ("Sabal", 1),                    # a whole palm, not a coconut
    "grass": ("Oryza", 0),                   # a tillering grass with its panicle
    "sirenian": ("Trichechus", 1),           # a manatee from the side
    "oyster": ("Ostrea", 0),                 # filled valve, matching the other shells
    "shark": ("Carcharhinus", 0),            # side view; the old one was from above
}

KO = 'fill="none" stroke="var(--ko)" stroke-linecap="round"'
HAND = {
    "nautiloid": (                      # the orthocone form draws from this key
        '<path d="M3 20 45 14v12z"/><path d="M44.6 14c4.6-.8 8 1.4 9 6-1 4.6-4.4 6.800-9 6z"/>'
        '<path d="M52.4 17.4 61.4 12M53.4 19.4l8.800-1.800M53.4 21l8.800 2.200M52.4 23l8.600 5.400" fill="none" '
        'stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>'
        f'<path d="M14 18.600v2.800M22 17.400v5.200M30 16.200v7.600M38 15.200v9.600" {KO} stroke-width="1.1"/>'
        '<circle cx="48.4" cy="18.4" r="1.2" fill="var(--ko)"/>'),
    "tabulate": (
        '<path d="M5 39q0-25 27-25t27 25z"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="2.300" fill="var(--ko)"/>' for x, y in
                  [(32, 19.5), (24.5, 22), (39.5, 22), (18, 27), (28, 27), (36, 27), (46, 27),
                   (13, 33.5), (22.5, 33.5), (32, 33.5), (41.5, 33.5), (51, 33.5)])),
    "tubeworm": (
        '<path d="M7 39q25-7 50 0z"/>'
        '<path d="M18 37 16.400 15M27.500 37V9.500M37 37l1.600-23M46 37l2.600-16" fill="none" '
        'stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/>'
        '<ellipse cx="16" cy="10.600" rx="2.700" ry="4.800"/><ellipse cx="27.500" cy="5.200" rx="2.700" ry="4.600"/>'
        '<ellipse cx="38.900" cy="9.600" rx="2.700" ry="4.800"/><ellipse cx="49" cy="16.600" rx="2.600" ry="4.400"/>'
        f'<path d="M16.900 22v12M27.500 17v17M37.800 21v13M47.300 27v8" {KO} stroke-width="1"/>'),
    "coccolith": (
        '<circle cx="32" cy="20" r="16.500"/>'
        + "".join(f'<ellipse cx="{x}" cy="{y}" rx="5.400" ry="3.600" transform="rotate({r} {x} {y})" {KO} '
                  f'stroke-width="1.200"/><ellipse cx="{x}" cy="{y}" rx="2" ry="1.100" '
                  f'transform="rotate({r} {x} {y})" fill="var(--ko)"/>' for x, y, r in
                  [(32, 20, 0), (32, 9.5, 0), (32, 30.5, 0), (22.5, 14.5, 60), (41.5, 14.5, -60),
                   (22.5, 25.5, -60), (41.5, 25.5, 60)])),
    "acacia": (
        '<path d="M4 17.500q5-9.500 17-9.500h22q12 0 17 9.500l-3.500 2.700H7.500z"/>'
        '<path d="M30.500 39l1.200-12.500-10-8M33.500 39l-.700-12.500 11-8M32 26.500V19" fill="none" '
        'stroke="currentColor" stroke-width="2.500" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M14 39h36" fill="none" stroke="currentColor" stroke-width="1.400" stroke-linecap="round"/>'),
    "baobab": (
        '<path d="M23.500 39c-2.400-8.500-3-16 0-23.500h17c3 7.500 2.400 15 0 23.500z"/>'
        '<path d="M26 16 17.500 7.500M30 16l-2.500-10M34 16l3-10.500M38 16l9-8M17.500 7.500l-5 .5M17.500 7.500l.5-4.500'
        'M47 8l5.500 1M47 8l-.500-5M27.500 6l-3.500-3M37 5.500l3.500-3" fill="none" stroke="currentColor" '
        'stroke-width="2.100" stroke-linecap="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="2.500"/>' for x, y in
                  [(12, 8), (18, 2.8), (24, 2.800), (27.500, 5.600), (40.500, 2.600), (46.500, 3), (52.800, 9.200)])),
    "cyano": (                           # two trichomes of bead cells, one with a heterocyst
        "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                [(6, 14, 3), (12, 12.2, 3), (18, 11, 3), (24.6, 10.6, 4.3), (31.2, 11, 3), (37.2, 12.2, 3),
                 (43.2, 13.8, 3), (49.2, 15.8, 3), (55.2, 18, 3),
                 (10, 31.5, 3), (16, 30, 3), (22, 29, 3), (28, 28.6, 3), (34, 29, 3), (40.6, 30.2, 4.3),
                 (47.2, 32, 3), (53.2, 34, 3), (59, 36.2, 3)])
        + '<circle cx="24.6" cy="10.6" r="1.7" fill="var(--ko)"/><circle cx="40.6" cy="30.2" r="1.7" fill="var(--ko)"/>'),
    "ray": (                             # a manta from above: wings, cephalic lobes, whip tail
        '<path d="M32 8.500c6 3.500 17 6.500 30 11-11 2.500-20 6.500-26 11.500h-8c-6-5-15-9-26-11.500 13-4.500 24-7.500 30-11z"/>'
        '<path d="M28.300 10.500c-1.800-1.500-2.300-4-1.300-6.500M35.700 10.500c1.800-1.500 2.300-4 1.300-6.500" fill="none" '
        'stroke="currentColor" stroke-width="2.400" stroke-linecap="round"/>'
        '<path d="M32 30.500v10.500" fill="none" stroke="currentColor" stroke-width="1.300" stroke-linecap="round"/>'
        f'<path d="M27 20.500q5 2.500 10 0" {KO} stroke-width="1"/>'),
    # ---- the seventeen forms PhyloPic has nothing for (2026-09-22). Each is the
    # group's textbook outline at 64 x 40: the shape a palaeontologist draws on
    # a whiteboard, not a specimen.
    "belemnite": (                       # squid body with fins, the bullet guard behind
        '<path d="M6 21c9-4 18-6 30-6l20 2c2 .4 2 6.4 0 6.8l-20 2c-12 0-21-2-30-6.8z"/>'
        '<path d="M36 15c-2-4-1-7 1-10M40 15c-1-5 0-8 3-11M44 15.5c0-5 1-8 4-10M48 16c1-4 3-7 6-8" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<path d="M56 18.5 63 21l-7 2.6z"/>'
        f'<path d="M46 17.2 v6.8" {KO} stroke-width="1"/><circle cx="14" cy="20" r="1.4" fill="var(--ko)"/>'),
    "conodont": (                        # an eel-like body with big eyes and the tooth apparatus at the mouth
        '<path d="M8 22c6-9 16-11 28-9 8 1 16 4 22 9-6 5-14 8-22 9-12 2-22 0-28-9z"/>'
        '<circle cx="14" cy="20" r="2.6" fill="var(--ko)"/><circle cx="14.6" cy="20" r="1.1"/>'
        f'<path d="M6 21.5l2.5-2.5M6.5 22.5l3-1M6 23.5l3 0.5" {KO} stroke-width="1"/>'
        '<path d="M2 18l4 3.5-4 3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'
        f'<path d="M30 15v14M38 14v16M46 15.5v13" {KO} stroke-width="0.9"/>'),
    "blastoid": (                        # a bud on a stalk, five ambulacra
        '<path d="M32 4c8 0 13 7 13 15 0 7-5 14-13 16-8-2-13-9-13-16C19 11 24 4 32 4z"/>'
        f'<path d="M32 6v28M22.5 12l6 8v14M41.5 12l-6 8v14M25 26l-3 5M39 26l3 5" {KO} stroke-width="1.5"/>'
        '<path d="M32 35v5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M28 38h8M27 40.5h10" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>'),
    "bryozoan": (                        # a fenestrate fan: a half-disc of lace on a short stem
        '<path d="M32 40c-16 0-26-9-27-24C15 8 24 4 32 4s17 4 27 12c-1 15-11 24-27 24z"/>'
        + "".join(f'<rect x="{x}" y="{y}" width="2.6" height="3.4" rx="1" fill="var(--ko)"/>' for x, y in
                  [(x, y) for y in (10, 16, 22, 28) for x in range(12, 52, 6) if (y == 10 and 22 <= x <= 40) or (y == 16 and 16 <= x <= 46) or (y == 22 and 12 <= x <= 50) or (y == 28 and 16 <= x <= 46)])
        + '<path d="M32 40v-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'),
    "horncoral": (                       # a curved horn seen from the side, the cup facing us
        '<path d="M10 38C12 26 20 14 34 8l6 10c-8 4-14 10-18 20z"/>'
        '<ellipse cx="46" cy="16" rx="11" ry="10"/>'
        f'<ellipse cx="46" cy="16" rx="7.5" ry="6.6" {KO} stroke-width="1.1"/>'
        + "".join(f'<path d="M46 16l{dx} {dy}" {KO} stroke-width="1"/>' for dx, dy in
                  [(0, -9), (6.4, -6.4), (9, 0), (6.4, 6.4), (0, 9), (-6.4, 6.4), (-9, 0), (-6.4, -6.4)])),
    "rudist": (                          # a tall conical valve with a lid, in a thicket of two
        '<path d="M24 40c-2-10-1-22 4-33h6c5 11 6 23 4 33z"/><path d="M27 7h12l-2 3H29z"/>'
        '<path d="M44 40c-1-7 0-14 3-22h5c3 8 4 15 3 22z"/><path d="M46 18h8l-1.5 2.5h-5z"/>'
        f'<path d="M28 14c2 1 4 1 6 0M27 21c2.5 1 5.5 1 8 0M26.5 28c3 1 6 1 9 0M27 35c2.5 1 5.5 1 8 0" {KO} stroke-width="1"/>'
        f'<path d="M47 26c1.5 1 3.5 1 5 0M46.5 33c2 1 4 1 6 0" {KO} stroke-width="1"/>'),
    "stromatoporoid": (                  # a domed, layered mound
        '<path d="M4 38C8 22 18 12 32 12s24 10 28 26z"/>'
        f'<path d="M9 33c8-8 16-11 23-11s15 3 23 11M14 37c6-6 12-8 18-8s12 2 18 8M6 36c9-14 17-19 26-19s17 5 26 19" {KO} stroke-width="1.1"/>'
        '<path d="M2 38h60" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>'),
    "zosterophyll": (                    # forking spiny stems with sporangia up one side
        '<path d="M14 40c4-12 6-22 10-32M24 8c3 6 7 10 12 12M24 8c-3 5-8 8-13 9M36 40c2-10 3-18 6-28M42 12c2 5 6 8 11 9M42 12c-3 4-7 6-11 6" '
        'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="1.9"/>' for x, y in
                  [(19, 24), (20.5, 18), (22, 12), (40, 26), (41, 20), (42.5, 15), (45, 30), (44, 35)])
        + "".join(f'<path d="M{x} {y}l-2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>' for x, y in
                  [(17, 32), (18, 28), (38, 34), (39, 31)])),
    "progymnosperm": (                   # Archaeopteris: a conifer-like trunk with fern-like fronds
        '<path d="M30.5 40V14h3v26z"/>'
        '<path d="M32 14c-8 2-14 0-18-6 6-1 12 1 18 6zM32 14c8 2 14 0 18-6-6-1-12 1-18 6zM32 20c-7 3-12 2-16-3 5-1 10 0 16 3zM32 20c7 3 12 2 16-3-5-1-10 0-16 3z'
        'M32 27c-6 3-10 2-13-2 4-1 8 0 13 2zM32 27c6 3 10 2 13-2-4-1-8 0-13 2zM32 6c-3-2-4-4-3-6 2 1 3 3 3 6zM32 6c3-2 4-4 3-6-2 1-3 3-3 6z"/>'
        f'<path d="M18 9c5 0 9 2 14 5M46 9c-5 0-9 2-14 5M19 18c4 0 8 1 13 2M45 18c-4 0-8 1-13 2" {KO} stroke-width="0.9"/>'),
    "astrapothere": (                    # a heavy body, short trunk, big tusks
        '<path d="M14 36c-2-9 0-18 8-22h20c8 2 12 8 12 16v6h-5v-4H24v4h-5v-4h-5z"/>'
        '<path d="M54 18c4-2 7 0 8 4 0 3-2 5-4 6l-2-1c2-1 3-3 2-5-1-1-3-1-4 0z"/>'
        '<path d="M55 28c1 3 1 6-1 8M59 27c1 3 0 6-2 8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'
        '<circle cx="52" cy="20" r="1.3" fill="var(--ko)"/>'),
    "embrithopod": (                     # Arsinoitherium: rhino body, two great horns side by side
        '<path d="M12 36c-2-10 2-18 10-21h22c8 2 12 8 12 16v5h-5v-4H24v4h-5v-4h-7z"/>'
        '<path d="M52 16c2-6 4-11 5-15 2 4 3 9 3 15zM47 17c1-5 2-9 3-12 2 3 3 7 3 12z"/>'
        '<circle cx="50" cy="21" r="1.3" fill="var(--ko)"/>'),
    "mesosaur": (                        # a long-snouted swimmer with needle teeth, paddles, long tail
        '<path d="M2 24c8-5 16-7 24-7 8-1 14-2 20-5l16-6c-4 6-10 10-16 12-6 3-12 4-20 4-8 1-16 2-24 2z"/>'
        '<path d="M18 22l-6 7M28 20l-4 9M40 16l4 6M36 17l1 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M48 10l2 3M51 9l2 3M54 8l2 3" {KO} stroke-width="0.9"/><circle cx="45" cy="13" r="1.2" fill="var(--ko)"/>'),
    "ostracod": (                        # a bean-shaped bivalved shell with antennae and a leg out
        '<path d="M14 22c0-8 8-14 18-14s18 6 18 14-8 13-18 13-18-5-18-13z"/>'
        f'<path d="M32 9v26" {KO} stroke-width="1.2"/>'
        '<path d="M14 21c-4-4-6-9-5-14M15 24c-5 0-9-2-12-6M34 35c1 3 3 5 6 6M28 35c-1 3-2 5-4 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
        '<circle cx="21" cy="18" r="1.3" fill="var(--ko)"/>'),
    "heteromorph": (                     # an uncoiled ammonite: a loose spiral, a shaft, and a hook back
        '<path d="M22 24c-2-8 2-15 9-17 6-1 12 3 12 9 0 5-4 8-8 8-3 0-5-2-5-4 0-2 2-3 4-3-1-1-3 0-3 2 0 3 3 5 6 5 5 0 9-4 9-9 0-8-7-13-15-11-9 2-13 11-10 21z" />'
        '<path d="M22 24c1 6 4 11 10 13l16 2c5 0 8-3 8-7 0-3-2-5-5-5-2 0-4 2-4 4h3c0-1 1-2 2-2 1 0 2 1 2 3 0 2-2 4-6 4l-16-2c-4-1-7-5-8-10z"/>'
        f'<path d="M25 30l-2 2M28 34l-1 3M34 37l0 3M40 38l0 3" {KO} stroke-width="1"/>'),
    "bamboo": (                          # jointed culms with leaf sprays
        '<path d="M22 40V8M34 40V4M46 40V10" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>'
        f'<path d="M20 30h4M20 20h4M20 12h4M32 30h4M32 20h4M32 12h4M44 30h4M44 20h4" {KO} stroke-width="1.3"/>'
        '<path d="M22 16c-6-2-10-1-14 3 5 1 9 0 14-3zM34 9c-6-3-10-2-14 2 5 2 9 1 14-2zM34 24c6-3 10-2 14 2-5 2-9 1-14-2zM46 15c6-2 10-1 14 3-5 1-9 0-14-3zM22 26c-5-3-9-2-13 2 4 2 8 1 13-2z"/>'),
    "goblet": (                          # Namacalathus: a stalked goblet with windows
        '<path d="M31 40V26h2v14z"/>'
        '<path d="M22 8c0-3 20-3 20 0 1 8-3 16-10 19-7-3-11-11-10-19z"/>'
        f'<ellipse cx="32" cy="8" rx="10" ry="2.6" {KO} stroke-width="1.1"/>'
        + "".join(f'<ellipse cx="{x}" cy="{y}" rx="2.2" ry="2.8" fill="var(--ko)"/>' for x, y in
                  [(26, 15), (32, 17), (38, 15), (29, 22), (35, 22)])
        + '<path d="M24 40h16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>'),
    "agnostid": (                        # two equal shields, tiny, no eyes
        '<path d="M32 4c9 0 14 6 14 14 0 2-1 3-2 4H20c-1-1-2-2-2-4 0-8 5-14 14-14z"/>'
        '<path d="M32 40c9 0 14-6 14-14 0-2-1-3-2-4H20c-1 1-2 2-2 4 0 8 5 14 14 14z"/>'
        f'<path d="M26 8c2 4 2 8 0 12M38 8c-2 4-2 8 0 12M26 36c2-4 2-8 0-12M38 36c-2-4-2-8 0-12M22 22h20" {KO} stroke-width="1.1"/>'
        '<path d="M8 20h8M8 24h8M48 20h8M48 24h8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>'),
    "prototaxites": (
        '<path d="M26 39c-1.200-12-.800-24 1.400-33.500q4.600-3.500 9.200 0C38.800 15 39.200 27 38 39z"/>'
        f'<path d="M27.600 14q4.400 1.600 8.800 0M27 22q5 1.800 10 0M26.800 30q5.200 1.800 10.400 0" {KO} stroke-width="1.100"/>'
        '<path d="M12 39v-5.500m-2 .500 2-2.500 2 2.500M18 39v-4m-1.600.400 1.600-2 1.600 2M47 39v-5m-1.800.500 1.800-2.500 '
        '1.800 2.500M53 39v-3.500m-1.500.400 1.500-2 1.500 2" fill="none" stroke="currentColor" stroke-width="1.200" '
        'stroke-linecap="round"/>'),
}


def main():
    icons = json.load(open(ICONS))
    credits = json.load(open(CREDITS))
    build = phylopic.build_number()
    for key, (term, pick) in PINNED.items():
        path, cand = phylopic.silhouette(term, build, pick=pick)
        if not path:
            print(f"  {key}: nothing for {term!r} pick {pick} -- left as it was")
            continue
        icons[key] = path
        credits[key] = {k: cand[k] for k in ("attribution", "licence", "licence_url", "uuid", "taxon")}
        print(f"  {key:12s} <- {cand['taxon']} [{cand['licence']}]")
    for key, svg in HAND.items():
        svg = svg.replace(".800", ".8").replace(".200", ".2").replace(".400", ".4").replace(".600", ".6")
        ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">' + svg.replace("var(--ko)", "#000") + "</svg>")
        icons[key] = svg
        credits.pop(key, None)
        print(f"  {key:12s} <- hand-drawn")
    json.dump(icons, open(ICONS, "w"))
    json.dump(credits, open(CREDITS, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
