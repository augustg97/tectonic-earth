"""The sea's plants and algae before the seagrasses. Every marine card's flora
was "Chlorophyta, Rhodophyta"; these are the calcareous algae and cyanobacteria
that built and bound Palaeozoic and Mesozoic reefs, and the stoneworts of lakes."""
from _lib import E, T, write

E("Dasycladales", "order", "sea", "seaweed", 520, 0, ["cosmo"],
  "Dasyclad green algae, single cells the size of a finger with whorls of branches, calcified enough to be rock-formers in Palaeozoic and Mesozoic shelf limestones; a few, like the mermaid's wineglass, survive.",
  hab=["shelf", "reef", "coast"], lat=[0, 45], cls=("Ulvophyceae", "Dasycladales", ""))
E("Solenopora", "genus", "sea", "seaweed", 470, 140, ["cosmo"],
  "A calcified red alga growing in nodules and crusts on Ordovician to Cretaceous reefs; sliced, its pink and grey banding is the 'beetroot stone' of Jurassic England.",
  hab=["reef", "shelf"], lat=[0, 45], cls=("Florideophyceae", "", "Solenoporaceae"))
E("Girvanella", "genus", "sea", "cyano", 540, 145, ["cosmo"],
  "Tangled tubes of a calcified cyanobacterium, coating shells and grains into oncoids on Cambrian to Jurassic sea floors: the commonest microbial fossil of the Palaeozoic shelf.",
  hab=["shelf", "coast", "reef"], cls=("Cyanophyceae", "", ""))
E("phylloid algae", "informal", "sea", "seaweed", 320, 252, ["na-w", "na-e", "eu", "as-c", "as-e", "tet", "pan"],
  "Leaf-like calcareous algae that grew in thickets on Pennsylvanian and Permian sea floors and built mounds hundreds of metres across -- the reef builders of an age with few corals.",
  hab=["shelf", "reef"], lat=[0, 35], cls=("Ulvophyceae", "Bryopsidales", ""))
E("Corallinales", "order", "sea", "seaweed", 140, 0, ["cosmo"],
  "Coralline red algae, crusts as hard as the rock they grow on, cementing reef rubble into reef; on a modern reef they hold more of the framework together than the corals do.",
  hab=["reef", "coast", "shelf"], cls=("Florideophyceae", "Corallinales", ""))
E("Charophyta", "division", "fresh", "seaweed", 420, 0, ["cosmo"],
  "Stoneworts: green algae of clear fresh water that stand like tiny horsetails and coat themselves in lime; their oospores are the commonest plant fossil of ancient lake beds.",
  hab=["lake", "wetland", "river"], cls=("Charophyceae", "Charales", "Characeae"))
write("x-marine-algae.json")
