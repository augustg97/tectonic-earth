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
