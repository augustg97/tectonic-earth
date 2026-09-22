"""Generic plants and plankton the fill was missing: ferns of every age, tree
ferns, dinoflagellates, and the pseudo-toothed seabirds. Small, but "Chlorophyta,
Rhodophyta" was the flora of every open-ocean card and no card could show a fern."""
from _lib import E, T, write

E("Polypodiopsida", "class", "land", "fern", 360, 0, ["cosmo"],
  "Ferns. The understorey of every forest since the Carboniferous, and the whole canopy of some; for a few thousand years after the Chicxulub impact, fern spores are almost all there is.",
  hab=["forest", "rainforest", "wetland", "alpine", "island", "river"], cls=("Polypodiopsida", "", ""))
E("Cyatheales", "order", "land", "treefern", 200, 0, [T(200, 66, "cosmo"), T(66, 0, "sa", "ca", "au", "nz", "ng", "as-se", "in", "af-e", "af-w", "mg", "oc", "ind")],
  "Tree ferns, with trunks to twenty metres, in wet forests from the Jurassic to the present; the pale forms of Cretaceous polar forests and of today's cloud forests alike.",
  hab=["forest", "rainforest", "island", "wetland"], cls=("Polypodiopsida", "Cyatheales", ""))
E("Osmunda", "genus", "land", "fern", 200, 0, ["cosmo"],
  "Royal ferns, a genus so conservative that a Jurassic rhizome from Sweden is cell for cell like a living one.",
  hab=["wetland", "forest", "river"], cls=("Polypodiopsida", "Osmundales", "Osmundaceae"))
E("Dinoflagellata", "division", "sea", "dinoflagellate", 240, 0, ["cosmo"],
  "Dinoflagellates: armoured plankton whose resting cysts are the sea's fine-grained clock, and whose symbionts make a reef coral's colour and food.",
  hab=["pelagic", "shelf", "reef", "coast"], realms=["sea", "fresh"], cls=("Dinophyceae", "", ""))
E("Pelagornithidae", "family", "air", "seabird", 62, 2.5, ["cosmo"],
  "Pseudo-toothed birds: seabirds with bony spikes along the beak and wingspans to six metres, gliding the oceans from the Palaeocene to the Pliocene.",
  hab=["pelagic", "coast", "island"], realms=["air", "sea"], w=2, pic="Pelagornis", cls=("Aves", "Odontopterygiformes", "Pelagornithidae"))
write("x-ferns-plankton.json")
