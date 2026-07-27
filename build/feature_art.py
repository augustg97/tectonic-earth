"""Schematic illustrations for the cards that have no organism to draw.

Click a rift, an orogen, a flood basalt or an impact crater and the panel is all
text: the biota panels get silhouettes, everything else gets nothing. These are
cross-sections and scenes for the KIND of thing each card describes -- what a
rift valley looks like in section, what an ice sheet does to the crust beneath
it, what a flood basalt province is a picture of.

They are diagrams, not photographs and not reconstructions of a specific place,
and each carries a caption saying so. Drawn once per feature type, with a few
overrides where a named feature is distinctive enough to deserve its own.

Palette is fixed rather than currentColor: these are little scenes with water,
rock and sky in them, and they have to read on the dark panel.

    python3 feature_art.py        # writes ../web/art.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "art.json")

W, H = 300, 118
SKY = "#131c26"
SEA = "#2f5f78"
SEA_D = "#1d3f52"
CRUST = "#6d6152"
CRUST_D = "#4a4238"
MANTLE = "#3a2f2c"
LAND = "#7d8358"
ICE = "#cbdde8"
HOT = "#c4622d"
HOT_L = "#e08b45"
LINE = "#8d99a8"


def _bg():
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="{SKY}"/>'


def _sea(y=54, to=H):
    return f'<rect x="0" y="{y}" width="{W}" height="{to-y}" fill="{SEA}"/>'


ART = {}


def art(key, svg, caption):
    ART[key] = {"svg": _bg() + svg, "caption": caption}


# ---------------------------------------------------------------- tectonic --
art("rift",
    # Dark base first, then the LIGHT shoulders on top, so the down-dropped
    # block reads as a distinct block rather than an outline on flat ground.
    f'<rect x="0" y="44" width="{W}" height="74" fill="{CRUST_D}"/>'
    f'<path d="M0 44h104l18 32V118H0z" fill="{CRUST}"/>'
    f'<path d="M300 44H196l-18 32V118h122z" fill="{CRUST}"/>'
    f'<path d="M0 44h104M196 44h104" stroke="{LAND}" stroke-width="4"/>'
    f'<path d="M104 44l18 32M196 44l-18 32" stroke="{LINE}" stroke-width="1.8"'
    f' fill="none"/>'
    f'<path d="M122 76h56v11h-56z" fill="{SEA}"/>'
    f'<path d="M122 76h56" stroke="#8fc6dc" stroke-width="1.2" opacity=".7"/>'
    f'<path d="M150 118c-11-16-11-28 0-36 11 8 11 20 0 36z" fill="{HOT}"'
    f' opacity=".9"/>'
    f'<path d="M150 106c-5-9-5-15 0-19 5 4 5 10 0 19z" fill="{HOT_L}"/>'
    f'<path d="M56 44l-7-13M80 44l-4-10M244 44l7-13M220 44l4-10" stroke="{LINE}"'
    f' stroke-width="1.4" opacity=".5"/>'
    f'<path d="M28 26h72M200 26h72" stroke="{LINE}" stroke-width="1" opacity=".3"/>'
    f'<path d="M56 20l-7 6 7 6M244 20l7 6-7 6" stroke="{LINE}" stroke-width="1.5"'
    f' fill="none" opacity=".75"/>',
    "Continental rift, in cross-section. The crust stretches and thins, a "
    "central block drops between bounding faults to form a graben, and hot "
    "mantle rises beneath. If stretching continues the floor drops below sea "
    "level and the rift floods.")

art("orogen",
    # The old version was one grey mass with arrows on it, which told you
    # nothing about what had happened. The whole point of a collisional belt is
    # that TWO things came together, so give the two plates different colours,
    # put a suture between them, stack the thrust sheets so the doubling is
    # visible, and show the root -- a range like this is three times deeper
    # than it is tall, and that is the fact the picture should carry.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    # left plate
    f'<path d="M0 60h108l30 22v36H0z" fill="#6f6250"/>'
    f'<path d="M0 72h104M0 86h112M0 100h120" stroke="#8a7b64" stroke-width="1.6"'
    f' opacity=".55"/>'
    # right plate, a different rock
    f'<path d="M300 60H176l-24 22v36h148z" fill="#5c5a52"/>'
    f'<path d="M300 72H180M300 86H172M300 100H164" stroke="#7b796d"'
    f' stroke-width="1.6" opacity=".55"/>'
    # the stack: thrust sheets riding up over the suture
    f'<path d="M96 60l38-22 30 18 32-20 26 24-30 12h-64z" fill="#7d7059"/>'
    f'<path d="M110 46l30-16 26 15 30-17" stroke="#9a8b6e" stroke-width="2"'
    f' fill="none"/>'
    f'<path d="M124 34l22-12 22 13 24-14" stroke="#a8987a" stroke-width="1.7"'
    f' fill="none" opacity=".9"/>'
    # summit line
    f'<path d="M96 60l38-22 30 18 32-20 26 24" stroke="#cfd8e2" stroke-width="2.4"'
    f' fill="none" stroke-linejoin="round"/>'
    # the suture: crushed sea floor caught between them
    f'<path d="M150 36v72" stroke="#2f4a52" stroke-width="4" opacity=".85"/>'
    f'<path d="M150 36v72" stroke="#4d7a86" stroke-width="1.4"'
    f' stroke-dasharray="5 4"/>'
    # the root
    f'<path d="M112 108q38 30 78 0z" fill="#6f6250" opacity=".9"/>'
    f'<path d="M112 108q38 30 78 0" stroke="#8a7b64" stroke-width="1.4"'
    f' fill="none"/>'
    # convergence
    f'<path d="M14 22h54M68 22l-9-6M68 22l-9 6" stroke="#e0a878" stroke-width="2.2"'
    f' fill="none"/>'
    f'<path d="M286 22h-54M232 22l9-6M232 22l9 6" stroke="#e0a878"'
    f' stroke-width="2.2" fill="none"/>',
    "A collisional mountain belt. Two continents converge and neither will "
    "subduct, so the rock between them stacks up along thrust faults -- the "
    "same layers repeated over themselves, which is why these ranges are built "
    "of sheets. The dashed line is the suture, crushed ocean floor caught "
    "between the two. Most of the thickening goes DOWN: the root reaches three "
    "times deeper than the peaks are high, and it is what holds them up.")

art("ocean",
    f'{_sea(30)}'
    f'<rect x="0" y="86" width="{W}" height="32" fill="{CRUST_D}"/>'
    f'<path d="M0 92h110l40-22 40 22h110v-6H190l-40-22-40 22H0z" fill="{CRUST}"/>'
    f'<path d="M150 70v-16" stroke="{HOT}" stroke-width="6"/>'
    f'<path d="M150 118c-9-16-9-30 0-38 9 8 9 22 0 38z" fill="{HOT}" opacity=".8"/>'
    f'<path d="M96 46h-40M56 46l8-5M56 46l8 5M204 46h40M244 46l-8-5M244 46l-8 5"'
    f' stroke="{LINE}" stroke-width="1.6" fill="none"/>'
    f'<path d="M0 30h300" stroke="{LINE}" stroke-width="1" opacity=".3"/>',
    "A mid-ocean ridge, in cross-section. New sea floor is made at the crest "
    "and moves away on both sides, so an ocean basin is youngest and shallowest "
    "in the middle and older and deeper toward its margins.")

art("sea",
    f'<rect x="0" y="66" width="{W}" height="52" fill="{CRUST}"/>'
    f'<path d="M0 66h300v52H0z" fill="{CRUST}"/>'
    f'<path d="M0 58q40 8 76 8h150q38 0 74-9v9H0z" fill="{CRUST}"/>'
    f'<path d="M28 58q46 10 122 10 92 0 122-11v0q-30 13-122 13-78 0-122-12z"'
    f' fill="none"/>'
    f'<path d="M0 40h300v26H0z" fill="{SEA}" opacity=".92"/>'
    f'<path d="M0 40q52 6 92 6h114q46 0 94-7" stroke="{LINE}" stroke-width="1.2"'
    f' fill="none" opacity=".5"/>'
    f'<path d="M40 52h40M110 58h50M200 50h44" stroke="{SEA_D}" stroke-width="2"'
    f' opacity=".7"/>'
    f'<path d="M0 84h300M0 98h300" stroke="{CRUST_D}" stroke-width="1.6"'
    f' opacity=".5"/>'
    f'<path d="M8 30l-4 6 4 6M292 30l4 6-4 6" stroke="{LINE}" stroke-width="1.3"'
    f' fill="none" opacity=".6"/>',
    "An epicontinental sea: shallow water standing ON continental crust rather "
    "than in an ocean basin. A few hundred metres of sea level is enough to "
    "flood a continental interior, and the same rise draining away leaves "
    "marine rock stranded far inland.")

art("island",
    f'{_sea(48)}'
    f'<path d="M0 96h300v22H0z" fill="{CRUST_D}"/>'
    f'<path d="M104 96l46-58 46 58z" fill="{CRUST}"/>'
    f'<path d="M132 58h36l-18-20z" fill="{LAND}"/>'
    f'<path d="M150 38c-4-10-2-16 0-20 3 5 4 11 0 20z" fill="{HOT_L}" opacity=".9"/>'
    f'<path d="M40 48q22 6 44 0M212 48q24 6 48 0" stroke="{LINE}" stroke-width="1.2"'
    f' fill="none" opacity=".45"/>'
    f'<path d="M60 118c8-14 14-22 26-26M240 118c-8-14-14-22-26-26"'
    f' stroke="{HOT}" stroke-width="2" fill="none" opacity=".5"/>',
    "A volcanic island or accreted terrane. Most islands in the deep ocean are "
    "the tops of volcanoes built from the sea floor; when the plate carrying "
    "them reaches a subduction zone they are too buoyant to sink and are "
    "scraped onto the continent instead.")

art("crater",
    # A bowl, not a skyline: ground surface, a wide depression cut into it, an
    # uplifted rim on each side, and a central peak on the crater floor.
    f'<rect x="0" y="48" width="{W}" height="70" fill="{CRUST}"/>'
    f'<path d="M0 48h56l14-12 20 12q60 46 120 0l20-12 14 12h56v70H0z"'
    f' fill="{CRUST}"/>'
    f'<path d="M90 48q60 46 120 0v46q-60 30-120 0z" fill="{CRUST_D}"/>'
    f'<path d="M56 48l14-12 20 12M244 48l-14-12-20 12" fill="{CRUST}"'
    f' stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>'
    f'<path d="M90 48q60 46 120 0" stroke="{LINE}" stroke-width="1.8" fill="none"/>'
    f'<path d="M150 88l-13 12h26z" fill="{CRUST}"/>'
    f'<path d="M150 88l-13 12h26z" fill="none" stroke="{LINE}" stroke-width="1.2"/>'
    f'<path d="M120 96q30 12 60 0" stroke="{MANTLE}" stroke-width="2"'
    f' fill="none" opacity=".6"/>'
    f'<path d="M0 106h300" stroke="{CRUST_D}" stroke-width="1.5" opacity=".55"/>'
    f'<path d="M70 34q-24-10-48-16M230 34q24-10 48-16" stroke="{LINE}"'
    f' stroke-width="1.4" fill="none" opacity=".55"/>'
    f'<path d="M84 28q-18-12-36-20M216 28q18-12 36-20" stroke="{LINE}"'
    f' stroke-width="1.1" fill="none" opacity=".35"/>'
    f'<path d="M150 30V8M143 16l7-8 7 8" stroke="{HOT_L}" stroke-width="2"'
    f' fill="none" opacity=".85"/>',
    "An impact structure in cross-section: an overturned rim, a shattered floor "
    "and, in larger craters, a central peak where the ground rebounded. Ejecta "
    "is thrown far beyond the rim, which is why an impact leaves a layer in the "
    "rock record much wider than the hole itself.")

art("volcanism",
    f'<rect x="0" y="58" width="{W}" height="60" fill="{CRUST_D}"/>'
    f'<path d="M0 58h300v10H0zM0 72h300v9H0zM0 85h300v8H0z" fill="{CRUST}"'
    f' opacity=".85"/>'
    f'<path d="M0 58h300" stroke="{LINE}" stroke-width="1" opacity=".4"/>'
    f'<path d="M138 118V60h24v58z" fill="{HOT}" opacity=".8"/>'
    f'<path d="M132 58q18-16 36 0z" fill="{HOT_L}"/>'
    f'<path d="M150 42c-4-12-2-20 0-26 3 7 4 15 0 26z" fill="{HOT_L}" opacity=".9"/>'
    f'<path d="M120 50q-16-8-30-4M180 50q16-8 30-4" stroke="{LINE}"'
    f' stroke-width="1.3" fill="none" opacity=".5"/>'
    f'<path d="M28 34q26-10 44 2M228 34q26-10 44 2" stroke="{LINE}"'
    f' stroke-width="1.2" fill="none" opacity=".35"/>',
    "A large igneous province. Basalt erupts from long fissures rather than a "
    "single cone and floods out in sheet after sheet, stacking kilometres of "
    "lava over an area the size of a continent. The gas released is why these "
    "eruptions sit next to several mass extinctions.")

# ------------------------------------------------------------- landscapes --
art("desert",
    f'<rect x="0" y="66" width="{W}" height="52" fill="#9a8355"/>'
    f'<path d="M0 78q40-18 78-4t76 2q40-16 76-2t70-6v50H0z" fill="#b0955f"/>'
    f'<path d="M0 92q44-14 84 0t80 2 76-8 60 4v28H0z" fill="#8d7649"/>'
    f'<path d="M0 78q40-18 78-4t76 2q40-16 76-2t70-6" stroke="#c6ab74"'
    f' stroke-width="1.3" fill="none"/>'
    f'<circle cx="248" cy="30" r="13" fill="#e0b269" opacity=".85"/>'
    f'<path d="M20 54q30-8 52 2M92 48q26-8 46 0" stroke="{LINE}" stroke-width="1.1"'
    f' fill="none" opacity=".3"/>',
    "A sand sea, or erg. Deserts sit where descending dry air meets a "
    "continental interior far from any ocean, or in the rain shadow behind a "
    "mountain range; the dunes are the visible part of a much larger sand "
    "transport system.")

art("forest",
    f'<rect x="0" y="86" width="{W}" height="32" fill="#4d4a35"/>'
    f'<path d="M0 86q40-6 74 0t76 0 76-2 74 4v32H0z" fill="#585535"/>'
    + "".join(
        f'<path d="M{x} 90V{70-h}" stroke="#6b5a3e" stroke-width="{3+h//14}"/>'
        f'<path d="M{x} {58-h}c-{12+h//6} {22+h//4} -{6+h//8} {30+h//4} 0 '
        f'{32+h//4}c{6+h//8} -2 {12+h//6} -{10+h//4} 0 -{32+h//4}z" fill="#5f7a46"/>'
        for x, h in ((26, 10), (62, 26), (104, 16), (150, 34), (196, 14),
                     (238, 28), (274, 8)))
    + f'<path d="M0 86h300" stroke="#3d3a2a" stroke-width="1.2" opacity=".6"/>',
    "Closed forest. What grows here depends on rainfall against evaporation, "
    "not latitude alone -- which is why the same rainfall makes taiga in a cold "
    "interior and desert in a warm one. Forests also weather rock and pull "
    "carbon dioxide out of the air.")

art("grassland",
    f'<rect x="0" y="88" width="{W}" height="30" fill="#6e6a3c"/>'
    f'<path d="M0 88q46-8 78 0t74-2 76 2 72-4v34H0z" fill="#7d7844"/>'
    + "".join(
        f'<path d="M{x} 92c-2-{10+(x%7)*2} 2-{16+(x%5)*2} {4+(x%3)} -{20+(x%9)}"'
        f' stroke="#9a9455" stroke-width="1.6" fill="none"/>'
        for x in range(10, 300, 11))
    + f'<circle cx="52" cy="30" r="10" fill="#d8bb6e" opacity=".7"/>',
    "Open grassland. Grasses spread only in the Cenozoic, as the world cooled "
    "and dried; their silica-rich leaves are abrasive, which is why grazing "
    "mammals evolved tall, continuously growing teeth to cope with them.")

art("ice",
    f'<rect x="0" y="82" width="{W}" height="36" fill="{CRUST}"/>'
    f'<path d="M0 96q54 10 150 10t150-10v22H0z" fill="{CRUST_D}"/>'
    f'<path d="M6 84q40-46 144-46T294 84q-56 14-144 14T6 84z" fill="{ICE}"/>'
    f'<path d="M6 84q40-46 144-46T294 84" stroke="#eef6fb" stroke-width="1.6"'
    f' fill="none"/>'
    f'<path d="M60 62q34 8 60 8M150 50q40 10 74 12" stroke="#a9c3d4"'
    f' stroke-width="1.2" fill="none" opacity=".7"/>'
    f'<path d="M0 96q54 10 150 10t150-10" stroke="{LINE}" stroke-width="1.3"'
    f' fill="none" opacity=".5"/>'
    f'<path d="M150 108v8M120 110v6M180 110v6" stroke="{LINE}" stroke-width="1.4"'
    f' opacity=".55"/>',
    "A continental ice sheet. Ice kilometres thick presses the crust down "
    "beneath it and the ground rebounds for thousands of years after the ice "
    "goes -- which is still happening around Hudson Bay and the Baltic today. "
    "Locking water up as ice also drops sea level worldwide.")

art("lake",
    f'<rect x="0" y="62" width="{W}" height="56" fill="{CRUST}"/>'
    f'<path d="M52 62q22 34 98 34t98-34v56H52z" fill="{CRUST_D}" opacity=".6"/>'
    f'<path d="M58 62q24 32 92 32t92-32z" fill="{SEA}"/>'
    f'<path d="M58 62q24 32 92 32t92-32" stroke="{LINE}" stroke-width="1.2"'
    f' fill="none" opacity=".5"/>'
    f'<path d="M0 62h58M242 62h58" stroke="{LAND}" stroke-width="4"/>'
    f'<path d="M22 44l10 18M270 40l-8 22" stroke="{SEA}" stroke-width="2.4"'
    f' fill="none" opacity=".8"/>'
    f'<path d="M96 74h108M112 82h76" stroke="{SEA_D}" stroke-width="2" opacity=".5"/>',
    "A lake basin. Standing fresh water needs a closed depression AND more "
    "water arriving than evaporates, so lakes map onto climate as much as onto "
    "topography -- and most large lakes today sit in basins that ice sheets or "
    "rifting made very recently.")

art("basin",
    # Nested lenses, youngest on top, each reaching further out than the last --
    # the shape a subsiding basin's fill actually makes.
    f'<rect x="0" y="40" width="{W}" height="78" fill="{MANTLE}"/>'
    f'<path d="M0 40h300v78H0z" fill="{CRUST_D}"/>'
    f'<path d="M0 40h300v10q-64 0-98 26T104 92 0 66z" fill="{CRUST}"/>'
    f'<path d="M0 66q60 26 104 26t98-26 98-26v9q-58 0-96 26t-100 0-104-26z"'
    f' fill="#8b7959"/>'
    f'<path d="M14 58q56 24 92 24t88-24 92-22v9q-56 0-90 24t-96 0-86-24z"'
    f' fill="#7a6a4e"/>'
    f'<path d="M34 50q48 22 78 22t76-22 78-20v9q-48 0-78 22t-82 0-72-22z"'
    f' fill="#695b43"/>'
    f'<path d="M0 40h300" stroke="{LAND}" stroke-width="4"/>'
    f'<path d="M0 66q60 26 104 26t98-26 98-26M14 58q56 24 92 24t88-24 92-22"'
    f' stroke="{LINE}" stroke-width="1" fill="none" opacity=".45"/>'
    f'<path d="M150 18v14M143 26l7 8 7-8" stroke="{LINE}" stroke-width="1.5"'
    f' fill="none" opacity=".7"/>'
    f'<path d="M104 22h92" stroke="{LINE}" stroke-width="1" opacity=".3"/>',
    "A sedimentary basin. Crust that subsides collects whatever erodes off the "
    "land around it, layer on layer, and the deepest part of the pile is the "
    "oldest. Basin fills are where most of the fossil record and most oil and "
    "coal are found.")

art("plateau",
    f'<rect x="0" y="70" width="{W}" height="48" fill="{CRUST_D}"/>'
    f'<path d="M58 70h184v48H58z" fill="{CRUST}"/>'
    f'<path d="M58 70q-18 4-30 14T0 100v18h58z" fill="{CRUST}"/>'
    f'<path d="M242 70q18 4 30 14t28 16v18h-58z" fill="{CRUST}"/>'
    f'<path d="M58 70h184" stroke="{LAND}" stroke-width="5"/>'
    f'<path d="M58 70q-18 4-30 14T0 100M242 70q18 4 30 14t28 16" stroke="{LINE}"'
    f' stroke-width="1.4" fill="none" opacity=".65"/>'
    f'<path d="M0 92h300M0 106h300" stroke="{CRUST_D}" stroke-width="1.3"'
    f' opacity=".45"/>'
    f'<path d="M150 62V46M142 52l8-8 8 8" stroke="{LINE}" stroke-width="1.6"'
    f' fill="none" opacity=".7"/>',
    "A plateau: a large area lifted more or less as a block, keeping a flat top "
    "while its edges are cut back by rivers. Thickened crust beneath, or hot "
    "buoyant mantle, holds it up; the flat surface is often an old landscape "
    "carried upward intact.")

art("continent",
    # The point of the picture is the KEEL: thick crust with a cold root
    # reaching far below the thin ocean floor on either side.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    f'<rect x="0" y="34" width="{W}" height="24" fill="{SEA}"/>'
    f'<path d="M0 52h58v10H0zM242 52h58v10h-58z" fill="{CRUST_D}"/>'
    f'<path d="M58 34q30-12 92-12t92 12v34q0 26-40 34t-104 0-40-34z"'
    f' fill="{CRUST}"/>'
    f'<path d="M58 34q30-12 92-12t92 12" stroke="{LAND}" stroke-width="4.5"'
    f' fill="none"/>'
    f'<path d="M86 70q26 40 64 40t64-40q0 30-30 42h-68q-30-12-30-42z"'
    f' fill="{CRUST_D}"/>'
    f'<path d="M58 68q0 26 40 34t104 0 40-34" stroke="{LINE}" stroke-width="1.4"'
    f' fill="none" opacity=".6"/>'
    f'<path d="M58 34v34M242 34v34" stroke="{LINE}" stroke-width="1.2"'
    f' opacity=".5"/>'
    f'<path d="M8 44h34M258 44h34" stroke="#8fc6dc" stroke-width="1.6"'
    f' opacity=".5"/>'
    f'<path d="M104 44q22-6 42 0M164 52q20-6 38 0" stroke="#93995f"'
    f' stroke-width="1.6" fill="none" opacity=".55"/>'
    f'<path d="M0 34h300" stroke="{LINE}" stroke-width="1" opacity=".3"/>',
    "A continent in section. Continental crust is thick and buoyant, with a "
    "cold keel reaching deep into the mantle beneath its oldest core -- which "
    "is why continents survive for billions of years while ocean floor is "
    "recycled within about two hundred million.")

art("region",
    f'<path d="M0 0h300v118H0z" fill="{SKY}"/>'
    f'<path d="M30 92q10-30 44-38t54 6 52-16 60 10 30 20v38H30z" fill="{LAND}"'
    f' opacity=".75"/>'
    f'<path d="M30 92q10-30 44-38t54 6 52-16 60 10 30 20" stroke="{LINE}"'
    f' stroke-width="1.6" fill="none"/>'
    f'<path d="M0 92h300v26H0z" fill="{SEA}" opacity=".8"/>'
    f'<path d="M64 74q26-10 48 0M150 62q26-8 46 2" stroke="#94a06a"'
    f' stroke-width="1.4" fill="none" opacity=".7"/>'
    f'<path d="M12 30h48M12 30l6-5M12 30l6 5" stroke="{LINE}" stroke-width="1.4"'
    f' fill="none" opacity=".55"/>',
    "A named region rather than a single landform: an area defined by what it "
    "had in common -- its climate, its coastline, or the animals and plants "
    "that could move across it.")

art("plume",
    # Mushroom: a straight stem from the deep mantle, a broad head flattened
    # against the base of the plate, and a volcano chain on top that gets older
    # to the left because the plate moved that way over a fixed source.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    f'<rect x="0" y="0" width="{W}" height="26" fill="{SEA}"/>'
    f'<rect x="0" y="26" width="{W}" height="14" fill="{CRUST_D}"/>'
    f'<path d="M150 118V64" stroke="{HOT}" stroke-width="16" opacity=".85"/>'
    f'<path d="M150 118V64" stroke="{HOT_L}" stroke-width="6" opacity=".9"/>'
    f'<path d="M150 40c-40 0-58 12-58 26 0 10 14 4 22-2 12-8 24-8 36 0 8 6 22 12'
    f' 22 2 0-14-18-26-22-26z" fill="{HOT}" opacity=".9"/>'
    f'<path d="M110 46q40-12 80 0" stroke="{HOT_L}" stroke-width="3" fill="none"'
    f' opacity=".9"/>'
    f'<path d="M150 26c-4-9-2-14 0-18 3 5 4 10 0 18z" fill="#f3c07a"/>'
    f'<path d="M138 26h24l-6 8h-12z" fill="{CRUST}"/>'
    f'<path d="M96 26h18l-4 6h-10zM56 26h13l-3 5h-7z" fill="{CRUST}" opacity=".8"/>'
    f'<path d="M150 26v14" stroke="{HOT_L}" stroke-width="3" opacity=".9"/>'
    f'<path d="M186 12h74M260 12l-8-5M260 12l-8 5" stroke="{LINE}"'
    f' stroke-width="1.4" fill="none" opacity=".7"/>'
    f'<path d="M20 16h44" stroke="{LINE}" stroke-width="1" opacity=".3"/>',
    "A mantle plume: a narrow column of hot rock rising from deep in the mantle "
    "with a broad head and a long tail. The plume stays roughly fixed while the "
    "plate slides over it, so the volcanoes it builds form a chain that gets "
    "older away from the active end.")

art("supercontinent",
    f'{_sea(0)}'
    f'<path d="M84 18q52-8 92 10t44 44-30 40-84 4-52-38 8-46 22-14z"'
    f' fill="{LAND}" opacity=".85"/>'
    f'<path d="M84 18q52-8 92 10t44 44-30 40-84 4-52-38 8-46 22-14z"'
    f' fill="none" stroke="{LINE}" stroke-width="1.6"/>'
    f'<path d="M104 24q10 40 26 60t50 30M150 14q-16 40-10 66t34 40"'
    f' stroke="#6a7048" stroke-width="1.4" fill="none" opacity=".8"/>'
    f'<path d="M120 46q30-10 56 4M118 76q34-8 62 6" stroke="#95a06c"'
    f' stroke-width="1.6" fill="none" opacity=".7"/>'
    f'<path d="M20 40q18 8 34 0M18 74q20 8 36 0M248 40q18 8 34 0M246 74q20 8 36 0"'
    f' stroke="{LINE}" stroke-width="1.2" fill="none" opacity=".4"/>'
    f'<path d="M244 20q-14 8-14 20M56 20q14 8 14 20" stroke="#a8571f"'
    f' stroke-width="2" fill="none" opacity=".5"/>',
    "A supercontinent: most of Earth's continental crust gathered into one mass, "
    "with old collision belts running through its interior where separate "
    "continents were welded together. The interior sits far from any ocean, so "
    "it dries out and swings hard between summer and winter.")

art("extinction",
    # A stratigraphic column read from the bottom up: crowded with fossils
    # below the boundary bed, nearly empty above it. That contrast IS the
    # evidence, so it has to be the thing you see.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="#1b232c"/>'
    f'<rect x="40" y="4" width="220" height="110" fill="#5c5344"/>'
    f'<rect x="40" y="4" width="220" height="42" fill="#6f6656"/>'
    f'<rect x="40" y="46" width="220" height="8" fill="#221b17"/>'
    f'<rect x="40" y="46" width="220" height="2.5" fill="#c1553a"/>'
    f'<rect x="40" y="54" width="220" height="60" fill="#7c6f57"/>'
    f'<path d="M40 68h220M40 84h220M40 100h220M40 22h220" stroke="#00000033"'
    f' stroke-width="1.4"/>'
    # dense below the boundary
    + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="4.6" ry="3" fill="#cdbf9c"'
        f' opacity=".9" transform="rotate({(x*7+y*3)%40-20} {x} {y})"/>'
        f'<path d="M{x-3} {y}q3-3 6 0" stroke="#8f8464" stroke-width="1"'
        f' fill="none"/>'
        for x, y in ((62, 62), (96, 74), (140, 64), (186, 76), (230, 62),
                     (78, 92), (124, 100), (170, 92), (214, 104), (58, 106),
                     (108, 62), (154, 84), (198, 62), (244, 88), (86, 62)))
    # sparse above it
    + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="4" ry="2.6" fill="#cdbf9c"'
        f' opacity=".55"/>'
        for x, y in ((92, 32), (196, 16)))
    + f'<rect x="40" y="4" width="220" height="110" fill="none"'
      f' stroke="{LINE}" stroke-width="1.2" opacity=".5"/>'
    + f'<path d="M20 46h14M266 46h14" stroke="#c1553a" stroke-width="1.8"/>'
    + f'<path d="M22 108V60M22 60l-4 6M22 60l4 6" stroke="{LINE}"'
      f' stroke-width="1.3" fill="none" opacity=".55"/>',
    "How an extinction is actually read: as a boundary in the rock. Below it a "
    "rich fossil assemblage, then a thin dark layer, then rock in which most of "
    "those species never appear again. The sharpness of that line is the main "
    "evidence for how fast the event was.")

art("tundra",
    f'<rect x="0" y="70" width="{W}" height="48" fill="#4a4436"/>'
    f'<path d="M0 70q44-5 76 0t74-3 76 3 74-5v50H0z" fill="#5b5642"/>'
    # patterned ground: freeze-thaw sorts the surface into polygons, which is
    # the one thing that makes tundra unmistakable from the air
    + "".join(
        f'<path d="M{x} {y}l16-7 17 7-6 15h-22z" fill="none" stroke="#736d55"'
        f' stroke-width="1.1" opacity=".75"/>'
        for y in (78, 96) for x in range(-6, 300, 33))
    + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.55:.1f}" fill="#6d7a4e"'
        f' opacity=".8"/>' for x, y, r in (
            (34, 86, 9), (96, 102, 7), (158, 84, 8), (214, 100, 6), (268, 88, 9),
            (66, 108, 6), (188, 110, 7), (128, 92, 5)))
    + f'<path d="M0 70q44-5 76 0t74-3 76 3 74-5" stroke="#7d8358"'
      f' stroke-width="2.2" fill="none"/>'
    # meltwater ponds -- the frozen layer below stops it draining away
    + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.42:.1f}"'
              f' fill="#3f6a7c" opacity=".85"/>'
              for x, y, r in ((78, 90, 13), (204, 92, 11), (150, 108, 9),
                              (262, 104, 8), (18, 100, 7)))
    + f'<path d="M0 118h300" stroke="#2c2822" stroke-width="8"/>'
    + f'<path d="M22 56q16-4 30 2M100 50q18-5 32 3M206 54q17-4 31 2"'
      f' stroke="{LINE}" stroke-width="1.1" fill="none" opacity=".3"/>',
    "Tundra. Too cold and the season too short for any tree, so the cover is "
    "moss, sedge, lichen and dwarf shrub over permafrost. The ground freezes "
    "and thaws into polygons, and because the frozen layer beneath will not let "
    "meltwater drain, a landscape with very little rainfall is covered in "
    "shallow pools all summer.")


art("orogen_accretion",
    # Not two continents meeting -- a COLLAGE. Arcs, seamounts and slivers of
    # microcontinent swept together over 300 Myr, each welded on and the next
    # one arriving behind it. The Altaids are the largest of these on Earth.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    f'<rect x="0" y="46" width="{W}" height="72" fill="{SEA}"/>'
    f'<path d="M0 62h300v56H0z" fill="{CRUST_D}"/>'
    + "".join(
        f'<path d="M{x} 62l{w//2} -{h} {w//2} {h}z" fill="{c}"/>'
        f'<path d="M{x} 62l{w//2} -{h} {w//2} {h}" stroke="{LINE}"'
        f' stroke-width="1.2" fill="none" opacity=".6"/>'
        for x, w, h, c in ((2, 46, 20, "#6f6250"), (44, 40, 30, "#5f6357"),
                           (80, 52, 17, "#77694f"), (128, 36, 26, "#5a5a55"),
                           (160, 48, 34, "#6d6152"), (204, 40, 21, "#616454"),
                           (240, 58, 28, "#75674e")))
    + "".join(f'<path d="M{x} 62v40" stroke="#39424a" stroke-width="1.6"'
              f' opacity=".8" stroke-dasharray="4 3"/>'
              for x in (44, 80, 128, 160, 204, 240))
    + f'<path d="M12 24h60M72 24l-9-5M72 24l-9 5" stroke="#e0a878"'
      f' stroke-width="2" fill="none"/>'
    + f'<path d="M288 24h-60M228 24l9-5M228 24l9 5" stroke="#e0a878"'
      f' stroke-width="2" fill="none"/>',
    "An accretionary belt: not two continents meeting but a collage. Island "
    "arcs, seamounts and slivers of microcontinent are swept against a margin "
    "one after another, each welded on before the next arrives, and the dashed "
    "lines are the sutures between them. Built over hundreds of millions of "
    "years, these add more new continental crust than collisions do.")

art("orogen_old",
    # What a range looks like after the mountains have gone: the ROOT, exhumed.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    f'<path d="M0 56h300v62H0z" fill="{CRUST_D}"/>'
    f'<path d="M0 56q34-16 72-8t70 12 76-14 82-4v10q-44-4-82 4t-76 14-70-12-72 8z"'
    f' fill="{CRUST}"/>'
    f'<path d="M0 56q34-16 72-8t70 12 76-14 82-4" stroke="{LAND}"'
    f' stroke-width="4" fill="none"/>'
    # steeply-dipping old fabric, truncated flat by erosion
    + "".join(f'<path d="M{x} 118L{x+26} 58" stroke="#8a7b64" stroke-width="2"'
              f' opacity=".7"/>' for x in range(-24, 300, 20))
    + f'<path d="M0 56q34-16 72-8t70 12 76-14 82-4" stroke="#cfd8e2"'
      f' stroke-width="1.6" fill="none" opacity=".55"/>'
    # ghost of the range that used to be here
    + f'<path d="M28 56l52-40 46 26 56-34 62 44" stroke="{LINE}"'
      f' stroke-width="1.5" fill="none" opacity=".28" stroke-dasharray="6 5"/>'
    + f'<path d="M150 12v-6M120 8h60" stroke="{LINE}" stroke-width="1"'
      f' opacity=".25"/>',
    "An old mountain belt, long after the mountains. The peaks are gone -- the "
    "dashed line is roughly where they were -- and what is exposed now is the "
    "ROOT: rock that was once ten or fifteen kilometres down, its steep fabric "
    "planed off flat. As the range erodes the crust below rebounds upward, "
    "which keeps feeding deeper rock to the surface long after uplift stops.")

art("lake_rift",
    # Deep, steep-sided, long-lived: the opposite of a glacial scrape.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{SKY}"/>'
    f'<rect x="0" y="40" width="{W}" height="78" fill="{CRUST}"/>'
    f'<path d="M0 40h104l16 22v56H0z" fill="{CRUST}"/>'
    f'<path d="M300 40H196l-16 22v56h120z" fill="{CRUST}"/>'
    f'<path d="M104 40l16 22v56h60V62l16-22z" fill="{CRUST_D}"/>'
    f'<path d="M0 40h104M196 40h104" stroke="{LAND}" stroke-width="4"/>'
    f'<path d="M104 40l16 22M196 40l-16 22" stroke="{LINE}" stroke-width="1.8"'
    f' fill="none"/>'
    f'<path d="M120 50h60v58h-60z" fill="#1d3f52"/>'
    f'<path d="M120 50h60v14h-60z" fill="#2f5f78"/>'
    f'<path d="M120 50h60" stroke="#8fc6dc" stroke-width="1.4" opacity=".8"/>'
    f'<path d="M126 96h48M132 104h36" stroke="#0f2a38" stroke-width="2"'
    f' opacity=".8"/>'
    f'<path d="M60 34l-8-12M232 34l8-12" stroke="{LINE}" stroke-width="1.4"'
    f' opacity=".5"/>'
    f'<path d="M28 22h56M216 22h56" stroke="{LINE}" stroke-width="1" opacity=".3"/>',
    "A rift lake. The floor is a dropped fault block, so the water is deep, the "
    "sides are steep and the basin lasts for millions of years -- long enough "
    "for its fish to evolve into whole endemic faunas. Baikal is 1,600 m deep "
    "and 25 million years old; a lake left by an ice sheet is 100 m deep and "
    "lasts ten thousand.")

art("sea_backarc",
    # A sea opened BEHIND an arc by slab rollback -- not a flooded continent.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{MANTLE}"/>'
    f'<rect x="0" y="34" width="{W}" height="30" fill="{SEA}"/>'
    f'<path d="M0 56h96v62H0z" fill="{CRUST}"/>'
    f'<path d="M0 56h96" stroke="{LAND}" stroke-width="4"/>'
    f'<path d="M96 64h96v10H96z" fill="{CRUST_D}"/>'
    f'<path d="M180 64l24-16 22 16z" fill="{CRUST}"/>'
    f'<path d="M204 48c-4-10-2-15 0-19 3 5 4 10 0 19z" fill="{HOT_L}"/>'
    f'<path d="M226 64h74v10h-74z" fill="{CRUST_D}"/>'
    f'<path d="M226 74q24 26 48 44" stroke="{CRUST_D}" stroke-width="11"'
    f' fill="none"/>'
    f'<path d="M120 62c-8-12-8-20 0-26 8 6 8 14 0 26z" fill="{HOT}" opacity=".85"/>'
    f'<path d="M108 46h-30M78 46l8-5M78 46l8 5M132 46h30M162 46l-8-5M162 46l-8 5"'
    f' stroke="{LINE}" stroke-width="1.6" fill="none"/>'
    f'<path d="M266 26l-10 8 10 8" stroke="{LINE}" stroke-width="1.6"'
    f' fill="none" opacity=".7"/>',
    "A back-arc sea. As a sinking slab rolls backwards the arc above it "
    "migrates seaward, and the crust behind is stretched until it splits and "
    "makes new sea floor. The Sea of Japan opened this way in the Miocene, "
    "swinging the whole archipelago out from Asia like a door.")

art("desert_shadow",
    # Dry because something is in the way, not because of latitude.
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="{SKY}"/>'
    f'<rect x="0" y="70" width="{W}" height="48" fill="#9a8355"/>'
    f'<path d="M0 62h60l48-40 40 34 26-14 34 20h92v56H0z" fill="#8d7649"/>'
    f'<path d="M0 62h60l48-40 40 34" fill="#6d7a52"/>'
    f'<path d="M60 62l48-40 40 34 26-14 34 20" stroke="#cfd8e2"'
    f' stroke-width="2.2" fill="none" stroke-linejoin="round"/>'
    # moist air arriving, raining out on the windward side
    + "".join(f'<path d="M{x} {y}q10-7 20 0" stroke="#8fb8cc" stroke-width="1.6"'
              f' fill="none" opacity=".75"/>' for x, y in ((6, 22), (30, 14), (54, 26)))
    + "".join(f'<path d="M{x} 34v12" stroke="#7fb4cc" stroke-width="1.5"'
              f' opacity=".8"/>' for x in (18, 30, 42, 54, 66, 78))
    + f'<path d="M170 18h96M266 18l-9-5M266 18l-9 5" stroke="{LINE}"'
      f' stroke-width="1.5" fill="none" opacity=".55"/>'
    + f'<path d="M180 76q46-12 84 0M196 92q40-10 72 0" stroke="#b0955f"'
      f' stroke-width="1.6" fill="none" opacity=".8"/>',
    "A rain-shadow desert. Moist air is forced up the windward slope, cools, "
    "and rains out before it reaches the top; what comes down the far side has "
    "nothing left in it. This is why the Atacama sits beside the Pacific and is "
    "still the driest place on Earth, and why Patagonia is a desert at the same "
    "latitude as rainforest across the Andes.")


art("oceanic_plateau",
    # A submarine LIP: thick volcanic crust standing kilometres above the abyss
    # but still well below the sea. Sea across the top, a broad flat-topped rise
    # on doubled ocean crust, the deep plain either side.
    f'{_sea(0, 74)}'
    f'<rect x="0" y="74" width="{W}" height="44" fill="{MANTLE}"/>'
    f'<path d="M0 86h300v10H0z" fill="{CRUST_D}"/>'
    f'<path d="M0 92h300v6H0z" fill="{CRUST_D}"/>'
    # the plateau: a broad flat-topped pile of basalt
    f'<path d="M52 86q10-30 44-32 40-2 60 2 44 8 92 4v26H52z" fill="{CRUST}"/>'
    f'<path d="M52 86q10-30 44-32 40-2 60 2 44 8 92 4" stroke="{LINE}"'
    f' stroke-width="1.6" fill="none" opacity=".6"/>'
    # basalt flows stacked in the pile
    f'<path d="M70 70h150M64 78h172" stroke="{CRUST_D}" stroke-width="1.4"'
    f' opacity=".5"/>'
    # still deep underwater: a depth marker down from the surface
    f'<path d="M150 6v46M143 46l7 8 7-8" stroke="#8fc6dc" stroke-width="1.4"'
    f' fill="none" opacity=".6"/>'
    f'<path d="M20 20h60M20 20l6-4M20 20l6 4" stroke="{LINE}" stroke-width="1.3"'
    f' fill="none" opacity=".5"/>',
    "A submarine oceanic plateau -- a large igneous province erupted onto the "
    "sea floor, kilometres of stacked basalt standing high above the abyss but "
    "still well below the surface. Ontong Java is the biggest; it never became "
    "land, and most plateaus like it never do.")

art("microcontinent",
    # A drowned continental fragment: continental crust, once an island, now a
    # shallow bank a few hundred metres down, distinct from the ocean crust
    # around it.
    f'{_sea(0, 60)}'
    f'<rect x="0" y="60" width="{W}" height="58" fill="{MANTLE}"/>'
    f'<path d="M0 78h300v40H0z" fill="{CRUST_D}"/>'
    # thin ocean crust either side, thick continental block in the middle
    f'<path d="M0 82h96v8H0zM204 82h96v8h-96z" fill="{CRUST_D}"/>'
    f'<path d="M96 60q12-8 54-8t54 8v30q0 8-54 8t-54-8z" fill="{LAND}"'
    f' opacity=".55"/>'
    f'<path d="M96 66q12-6 54-6t54 6v24q0 8-54 8t-54-8z" fill="{CRUST}"/>'
    f'<path d="M96 66q12-6 54-6t54 6" stroke="{LAND}" stroke-width="3.5"'
    f' fill="none"/>'
    # just under the waves -- a shallow bank
    f'<path d="M96 60q54 12 108 0" stroke="#8fc6dc" stroke-width="1.4"'
    f' fill="none" opacity=".7"/>'
    f'<path d="M150 8v40M143 42l7 8 7-8" stroke="#8fc6dc" stroke-width="1.4"'
    f' fill="none" opacity=".55"/>'
    f'<path d="M118 76h64M126 84h48" stroke="{CRUST_D}" stroke-width="1.4"'
    f' opacity=".45"/>',
    "A microcontinent: a fragment of continental crust, thicker and older than "
    "the ocean floor around it, left behind when a continent rifted apart. Many "
    "stood as islands when they broke away and have drowned since -- Kerguelen, "
    "the Seychelles, Zealandia -- so what shows now is a shallow bank marooned "
    "in deep ocean.")


# ------------------------------------------- where the type art is wrong ---
# A few families of feature are built by a mechanism the generic diagram gets
# wrong, and there are enough of them to be worth their own drawing.

art("orogen_arc",
    f'{_sea(34, 78)}'
    f'<path d="M0 78h300v40H0z" fill="{MANTLE}"/>'
    f'<path d="M0 60h150v18H0z" fill="{CRUST_D}"/>'
    f'<path d="M0 60q40-6 80 0t70 18" fill="none" stroke="{LINE}"'
    f' stroke-width="1.3" opacity=".5"/>'
    f'<path d="M150 78L300 60v58H150z" fill="{CRUST}"/>'
    f'<path d="M150 78l150-18" stroke="{LINE}" stroke-width="1.5" fill="none"/>'
    f'<path d="M150 78q30 22 60 34t90 6" fill="none" stroke="{CRUST_D}"'
    f' stroke-width="16" opacity=".85"/>'
    f'<path d="M162 60l30-32 26 32z" fill="{CRUST}"/>'
    f'<path d="M206 60l28-26 24 26z" fill="{CRUST}"/>'
    f'<path d="M192 28l-8 10h16z" fill="{LAND}"/>'
    f'<path d="M192 24c-3-8-2-12 0-14 3 3 3 7 0 14z" fill="{HOT_L}"/>'
    f'<path d="M186 96q8-24 20-34M212 100q6-26 18-36" stroke="{HOT}"'
    f' stroke-width="3" fill="none" opacity=".6"/>'
    f'<path d="M140 44l-14 8 14 8" stroke="{LINE}" stroke-width="1.5" fill="none"'
    f' opacity=".7"/>'
    f'<path d="M150 34v-8" stroke="{LINE}" stroke-width="1.2" opacity=".4"/>',
    "A subduction, or Andean-type, mountain belt. Ocean floor sinks beneath the "
    "continental margin, water driven off it makes the mantle above melt, and "
    "the magma builds a volcanic chain along the edge of the continent. No "
    "continents collide here -- the range is made by one plate going down.")

art("ocean_closing",
    f'{_sea(30, 74)}'
    f'<path d="M0 74h300v44H0z" fill="{MANTLE}"/>'
    f'<path d="M0 56h96v18H0z" fill="{CRUST}"/>'
    f'<path d="M0 44q36-4 60 2t36 10" fill="{CRUST}"/>'
    f'<path d="M204 56h96v18h-96z" fill="{CRUST}"/>'
    f'<path d="M300 44q-36-4-60 2t-36 10" fill="{CRUST}"/>'
    f'<path d="M96 66h108v8H96z" fill="{CRUST_D}"/>'
    f'<path d="M204 74q-24 20-40 34" fill="none" stroke="{CRUST_D}"'
    f' stroke-width="11"/>'
    f'<path d="M96 74q24 20 40 34" fill="none" stroke="{CRUST_D}"'
    f' stroke-width="11"/>'
    f'<path d="M124 56h52v10h-52z" fill="{SEA_D}"/>'
    f'<path d="M118 44l14 8-14 8M182 44l-14 8 14 8" stroke="{LINE}"'
    f' stroke-width="1.6" fill="none" opacity=".8"/>'
    f'<path d="M40 30h48M212 30h48" stroke="{LINE}" stroke-width="1.1"'
    f' opacity=".35"/>'
    f'<path d="M70 20l14 8-14 8M230 20l-14 8 14 8" stroke="{LINE}"'
    f' stroke-width="1.4" fill="none" opacity=".6"/>',
    "An ocean closing. Sea floor is destroyed at subduction zones faster than "
    "the ridge can make it, the basin narrows to a strait and then to nothing, "
    "and the continents on either side collide. All that is left afterwards is "
    "a suture -- a line of crushed sea-floor rock inside a mountain belt.")

art("forest_coal",
    f'<rect x="0" y="88" width="{W}" height="30" fill="#3b3227"/>'
    f'<rect x="0" y="98" width="{W}" height="20" fill="#231d18"/>'
    f'<path d="M0 88h300v10H0z" fill="#4a5a4a" opacity=".8"/>'
    + "".join(
        f'<path d="M{x} 92V{56-h}" stroke="#6d6a48" stroke-width="{6+h//12}"/>'
        f'<path d="M{x-2} 92V{56-h}" stroke="#83805a" stroke-width="1.4"'
        f' opacity=".7"/>'
        + "".join(
            f'<path d="M{x} {56-h}q{s*22} -6 {s*30} -16" stroke="#7f9450"'
            f' stroke-width="2" fill="none"/>' for s in (-1, 1))
        + f'<path d="M{x} {56-h}q-4-16 0-26q4 10 0 26z" fill="#7f9450"/>'
        for x, h in ((32, 16), (86, 30), (146, 8), (198, 26), (256, 14)))
    + f'<path d="M8 94h44M70 96h50M150 94h60M232 96h56" stroke="#5d7a70"'
      f' stroke-width="2.4" opacity=".8"/>'
    + "".join(f'<path d="M{x} 92c-2-10 2-16 5-20" stroke="#6f8a4e"'
              f' stroke-width="1.5" fill="none" opacity=".8"/>'
              for x in (14, 58, 118, 172, 226, 282))
    + f'<path d="M0 98h300" stroke="#171310" stroke-width="1.4"/>',
    "A Carboniferous coal swamp. Giant club mosses stood in standing water, and "
    "because that water was stagnant and acidic their remains did not rot -- "
    "they piled up as peat and were buried, which is where nearly all the "
    "world's coal comes from. Burying that much carbon pulled CO2 down and "
    "oxygen up.")

art("forest_devonian",
    f'<rect x="0" y="90" width="{W}" height="28" fill="#4a4433"/>'
    f'<path d="M0 90q46-6 78 0t76-2 74 2 72-4v32H0z" fill="#56503b"/>'
    f'<path d="M60 92V30" stroke="#8a7150" stroke-width="15"/>'
    f'<path d="M56 92V30" stroke="#a3885f" stroke-width="4" opacity=".8"/>'
    f'<ellipse cx="60" cy="28" rx="10" ry="6" fill="#a3885f"/>'
    f'<path d="M232 92V36" stroke="#8a7150" stroke-width="12"/>'
    f'<ellipse cx="232" cy="34" rx="8" ry="5" fill="#a3885f"/>'
    + "".join(
        f'<path d="M{x} 92V{62-h}" stroke="#6b5f3c" stroke-width="3.4"/>'
        + "".join(f'<path d="M{x} {66-h+i*9}q{s*16} -3 {s*24} 6"'
                  f' stroke="#6f8a4e" stroke-width="1.8" fill="none"/>'
                  for i in range(3) for s in (-1, 1))
        + f'<path d="M{x} {62-h}q-5-14 0-22q5 8 0 22z" fill="#7f9450"/>'
        for x, h in ((120, 22), (160, 12), (196, 18), (286, 6)))
    + f'<path d="M0 90h300" stroke="#3a3527" stroke-width="1.2" opacity=".7"/>'
    + f'<path d="M20 96q14-6 26 0M262 98q14-6 26 0" stroke="#6f8a4e"'
      f' stroke-width="1.4" fill="none" opacity=".7"/>',
    "Devonian land, with the two tallest things on it. The bare columns are "
    "Prototaxites -- up to 8 m high and 1 m thick, and probably a fungus rather "
    "than a plant; the leafy trees are Archaeopteris, the first plant with a "
    "real woody trunk and a canopy. Nothing else on land came close to their "
    "height.")

# Named features whose mechanism the type diagram would get wrong.
NAME_ART = {}
for _n in ("Andes", "Cordillera", "Sierra Nevada Arc", "Sevier-Laramide",
           "Famatinian Belt", "Antler Belt", "Sonoma Orogeny"):
    NAME_ART[_n] = "orogen_arc"
for _n in ("Iapetus Ocean", "Rheic Ocean", "Paleo-Tethys", "Ural Ocean",
           "Adamastor Ocean", "Mozambique Ocean", "Tethys Ocean", "Neotethys"):
    NAME_ART[_n] = "ocean_closing"
for _n in ("Euramerican Coal Forests", "Cathaysian Coal Forests",
           "Angaran Flora Belt"):
    NAME_ART[_n] = "forest_coal"
NAME_ART["Gilboa Forest"] = "forest_devonian"
# An oceanic gateway, not water standing on a continent -- the epeiric-sea
# caption would be flatly wrong about what this one was.
NAME_ART["Central American Sea"] = "ocean_closing"

# The biotic-interchange cards. Only where the diagram is honestly ABOUT the
# mechanism: the Great American interchange happens because the Central American
# Seaway closes, the Grande Coupure because the Turgai Strait drains, and
# Lystrosaurus spreads across a hemisphere because Pangaea has no barriers left.
# The Trans-Arctic interchange is a seaway OPENING and gets no figure rather than
# a nearly-right one -- a diagram that argues the opposite of its caption is
# worse than a card with no diagram.
NAME_ART["The Great American Biotic Interchange"] = "ocean_closing"
NAME_ART["The Grande Coupure"] = "ocean_closing"
NAME_ART["The Lystrosaurus Flood"] = "supercontinent"

for _n in ("Ontong Java Plateau", "Manihiki Plateau", "Shatsky Rise",
           "Agulhas Plateau", "Broken Ridge", "Rio Grande Rise", "Walvis Ridge",
           "Mascarene Plateau", "Naturaliste Plateau", "Hess Rise"):
    NAME_ART[_n] = "oceanic_plateau"
for _n in ("Kerguelen Microcontinent", "Mauritia", "Seychelles Microcontinent",
           "Jan Mayen Microcontinent", "Zealandia", "Argoland",
           "East Tasman Plateau", "Greater Adria", "Greater India"):
    NAME_ART[_n] = "microcontinent"


for _n in ("Central Asian Orogenic Belt", "Altai Belt", "Lachlan Orogen",
           "Qilian Belt", "Kunlun Belt", "Tien Shan", "Innuitian Belt",
           "Baikalian Belt", "Timanian Belt", "Verkhoyansk Belt"):
    NAME_ART[_n] = "orogen_accretion"
for _n in ("Appalachians", "Caledonides", "Ural Mountains", "Variscan Belt",
           "Alleghanian Belt", "Acadian Belt", "Taconic Belt", "Grenville Belt",
           "Bohemian Massif", "Iberian Massif", "Massif Central",
           "Sveconorwegian Belt", "Cadomian Belt", "Ouachita Belt",
           "Ellesmerian Belt", "Damara Belt", "Irumide Belt", "Sunsas Belt"):
    NAME_ART[_n] = "orogen_old"
for _n in ("Lake Baikal", "Lake Tanganyika", "East African Rift soda lakes",
           "Lake Titicaca", "Jehol Lakes", "Songliao Palaeolake"):
    NAME_ART[_n] = "lake_rift"
for _n in ("Sea of Japan", "Okhotsk Sea", "Paratethys", "Bearpaw Sea"):
    NAME_ART[_n] = "sea_backarc"
for _n in ("Patagonian Desert", "Atacama Desert", "Gobi Desert",
           "Taklamakan Desert", "Qaidam Basin", "Great Basin Desert"):
    NAME_ART[_n] = "desert_shadow"



# ------------------------------------------------------ per-type mapping ----
TYPE_ART = {
    "rift": "rift", "orogen": "orogen", "ocean": "ocean", "sea": "sea",
    "lake": "lake", "island": "island", "desert": "desert", "forest": "forest",
    "grassland": "grassland", "ice": "ice", "basin": "basin",
    "plateau": "plateau", "continent": "continent", "region": "region", "tundra": "tundra",
    "crater": "crater", "volcanism": "volcanism", "plume": "plume",
    "supercontinent": "supercontinent", "extinction": "extinction",
}


def main():
    missing = sorted({v for v in list(TYPE_ART.values()) + list(NAME_ART.values())
                      if v not in ART})
    if missing:
        raise SystemExit(f"feature_art: mapped to art that does not exist: {missing}")
    data = {"art": ART, "byType": TYPE_ART, "byName": NAME_ART}
    json.dump(data, open(OUT, "w"), separators=(",", ":"))
    size = os.path.getsize(OUT)
    print(f"feature art: {len(ART)} illustrations, {len(TYPE_ART)} type mappings, "
          f"{len(NAME_ART)} name overrides, {size/1024:.0f} kB "
          f"-> {os.path.relpath(OUT, HERE)}")


if __name__ == "__main__":
    main()
