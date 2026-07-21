"""Add region-specific biota for marine features that fell back to the global
list (so different oceans/seas read the same). Each entry is the well-established
characteristic fauna of that basin at that time, from the fossil record. Merged
into life_data.json under region_taxa; run once, idempotent (overwrites keys).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "life_data.json")

# realm: sea | land | air | fresh ; rank: genus|family|order|class|phylum|...
NEW = {
 # --- Konservat-Lagerstätte: a lagoon, but famous for what it preserved, so it
 #     is deliberately NOT realm-locked to the sea (see MARINE_REGIONS below). ---
 "Solnhofen Lagoon": [
   {"a0":149,"a1":152,"taxa":[
     ["Archaeopteryx","genus","air","The first bird — feathered, clawed and toothed — its wings printed in the lagoon's fine limestone."],
     ["Rhamphorhynchus","genus","air","Long-tailed pterosaur skimming the lagoon; some slabs preserve its wing membrane and throat pouch."],
     ["Compsognathus","genus","land","A chicken-sized coelurosaur dinosaur washed into the lagoon, its last meal a lizard in its gut."],
     ["Mesolimulus","genus","sea","A horseshoe crab preserved at the end of its own death-track across the anoxic mud."],
     ["Ammonoidea","subclass","sea","Ammonites of the open Tethys, sunk into a stagnant, oxygen-starved basin that let nothing decay."]]}],
 # --- Germanic Triassic epicontinental carbonate sea ---
 "Muschelkalk Sea": [
   {"a0":237,"a1":247,"taxa":[
     ["Ceratites","genus","sea","The ammonoid that zones the whole Muschelkalk — its ribbed shells fill the limestone."],
     ["Encrinus","genus","sea","Meadows of stalked crinoids ('sea lilies') whose disarticulated ossicles make crinoidal limestone."],
     ["Nothosaurus","genus","sea","A long-necked, sharp-toothed marine reptile hunting the shallow shelf."],
     ["Placodontia","order","sea","Placodonts — armoured reptiles with flat crushing teeth for shellfish on the sea floor."]]}],
 # --- Cretaceous Western Interior / boreal sub-basins ---
 "Mowry Sea": [
   {"a0":95,"a1":103,"taxa":[
     ["Actinopterygii","class","sea","The Mowry Shale is paved with fish scales — a bloom-and-death sea of small ray-finned fish."],
     ["Radiolaria","class","sea","Silica-shelled plankton so abundant the shale itself is siliceous."],
     ["Inoceramidae","family","sea","Flat, thick-shelled clams carpeting the early Western Interior seabed."]]}],
 "Boreal Sea": [
   {"a0":90,"a1":190,"taxa":[
     ["Belemnitida","order","sea","Bullet-shaped squid relatives swarming the cool northern seas; their guards litter Arctic shales."],
     ["Ichthyosauria","order","sea","Dolphin-shaped reptiles cruising the boreal water column."],
     ["Ammonoidea","subclass","sea","Cold-water ammonite faunas distinct from the warm Tethyan realm to the south."],
     ["Buchia","genus","sea","A small clam so abundant and fast-evolving it dates the whole boreal Jurassic-Cretaceous."]]}],
 "Hudson Seaway": [
   {"a0":66,"a1":100,"taxa":[
     ["Mosasauridae","family","sea","Giant marine lizards, the apex predators of the seaway in its final phase."],
     ["Hesperornis","genus","air","A flightless, toothed diving bird that swam the seaway like a loon."],
     ["Baculites","genus","sea","Straight-shelled ammonites drifting in vast numbers over the muddy floor."],
     ["Enchodus","genus","sea","The 'saber-toothed herring', a fanged predatory fish of the interior sea."]]}],
 "Bearpaw Sea": [
   {"a0":72,"a1":78,"taxa":[
     ["Baculites","genus","sea","The Bearpaw Shale is a Baculites clock — each zone a different straight-shelled ammonite species."],
     ["Placenticeras","genus","sea","A large disc-shaped ammonite, some shells punctured by mosasaur tooth-marks."],
     ["Mosasauridae","family","sea","Mosasaurs patrolling the retreating late-Cretaceous interior sea."],
     ["Ammolite","genus","sea","Not a taxon but a legacy: Bearpaw ammonite shells fossilised as the gem ammolite."]]}],
 # --- Tethyan reef/carbonate realm ---
 "Neotethys": [
   {"a0":100,"a1":270,"taxa":[
     ["Rudistes","order","sea","Cone- and spiral-shelled bivalves that BUILT the Tethyan reefs where corals had once dominated."],
     ["Ammonoidea","subclass","sea","A rich, ornate Tethyan ammonite fauna — the warm-water standard the boreal seas are compared against."],
     ["Scleractinia","order","sea","Reef corals of the shallow Tethyan carbonate platforms."],
     ["Nummulitidae","family","sea","(younger) Coin-sized foraminifera whose shells make the limestone of the Egyptian pyramids."]]},
   {"a0":45,"a1":100,"taxa":[
     ["Nummulitidae","family","sea","Giant single-celled foraminifera building whole limestones across the Paleogene Tethys."],
     ["Rudistes","order","sea","Rudist reefs at their peak before collapsing at the end of the Cretaceous."],
     ["Discoaster","genus","sea","Star-shaped coccolithophore plankton of the warm Paleogene sea."]]}],
 # --- Terminal Ediacaran (Nama Group, Namibia) ---
 "Nama Sea": [
   {"a0":538,"a1":551,"taxa":[
     ["Cloudina","genus","sea","Stacked-cone tube-builder, one of the first animals to make a mineralised skeleton — some bored by predators."],
     ["Namacalathus","genus","sea","A goblet-shaped calcified fossil, an early reef-dweller of the terminal Ediacaran."],
     ["Pteridinium","genus","sea","A large three-vaned Ediacaran frond of the Nama seafloor, a body plan with no living counterpart."],
     ["Rangeomorpha","class","sea","Fractal, fern-like fronds — the last of the soft Ediacaran biota before the Cambrian."]]}],
 # --- Jurassic western-US and European seaways ---
 "Sundance Sea": [
   {"a0":155,"a1":172,"taxa":[
     ["Gryphaea","genus","sea","'Devil's toenails' — thick curved oysters strewn across the Jurassic seabed of western North America."],
     ["Belemnitida","order","sea","Belemnite squid whose bullet guards are the commonest Sundance fossil."],
     ["Ichthyosauria","order","sea","Ichthyosaurs hunting the epicontinental sea that reached down from the Arctic."],
     ["Pentacrinites","genus","sea","Stalked crinoids that rafted on driftwood over the open sea."]]}],
 # --- North American cratonic Sloss sequences ---
 "Tippecanoe Sea": [
   {"a0":418,"a1":490,"taxa":[
     ["Bryozoa","phylum","sea","Lace and twig colonies encrusting the vast, warm Ordovician-Silurian carbonate shelf."],
     ["Brachiopoda","phylum","sea","Strophomenid and orthid lamp-shells dominating the shelly benthos."],
     ["Rugosa","order","sea","Solitary 'horn corals' and colonial tabulates building the first big Paleozoic reefs."],
     ["Crinoidea","class","sea","Dense crinoid gardens whose broken stems make whole beds of limestone."]]}],
 "Kaskaskia Sea": [
   {"a0":360,"a1":418,"taxa":[
     ["Stromatoporoidea","order","sea","Layered sponge-grade reef-builders raising the great Devonian reef complexes."],
     ["Brachiopoda","phylum","sea","Spiriferid brachiopods with their broad winged hinges, the Devonian shelf standard."],
     ["Placodermi","class","sea","Armoured fish — including giant Dunkleosteus-kin — the apex predators of the Devonian sea."],
     ["Rugosa","order","sea","Colonial and horn corals flanking the stromatoporoid reefs."]]}],
 "Absaroka Sea": [
   {"a0":252,"a1":330,"taxa":[
     ["Fusulinida","order","sea","Rice-grain foraminifera so abundant they zone the entire late-Paleozoic cratonic sea."],
     ["Crinoidea","class","sea","The 'age of crinoids' — Carboniferous seafloors were forests of stalked echinoderms."],
     ["Productida","order","sea","Spiny, one-valve-cemented brachiopods carpeting the shelf."],
     ["Chondrichthyes","class","sea","Bizarre Carboniferous sharks and chimaeras — Helicoprion's tooth-whorl among them."]]}],
 # --- Neogene distinctive seas ---
 "Central American Sea": [
   {"a0":3,"a1":40,"taxa":[
     ["Scleractinia","order","sea","Caribbean coral reefs before the Isthmus of Panama split them from the Pacific."],
     ["Carcharocles","genus","sea","Giant megatooth sharks patrolling the warm tropical seaway."],
     ["Sirenia","order","sea","Sea cows grazing sea-grass meadows in the shallow tropical straits."],
     ["Foraminifera","class","sea","Larger foraminifera whose divergence across the closing seaway records the Isthmus forming."]]}],
 "Messinian Salt Basin": [
   {"a0":5,"a1":6,"taxa":[
     ["Cyprideis","genus","sea","A brackish ostracod that boomed as the Mediterranean's chemistry swung wildly during the salinity crisis."],
     ["Cyanobacteria","phylum","sea","Microbial mats and stromatolites on hypersaline flats as the sea evaporated to gypsum and rock salt."],
     ["Dreissena","genus","sea","'Lago Mare' phase — brackish Paratethyan mussels flooding a Mediterranean nearly emptied and freshened before the Atlantic broke back in."]]}],
 "Lake Pannon": [
   {"a0":4,"a1":11,"taxa":[
     ["Congeria","genus","fresh","Endemic mussels of the great brackish lake-sea left behind as the Paratethys shrank."],
     ["Melanopsis","genus","fresh","Brackish-water snails that radiated into dozens of endemic Lake Pannon species."],
     ["Hipparion","genus","land","Three-toed horses on the surrounding grassy shores, washed into the lake beds."]]}],
 # --- Cretaceous-Paleogene epicontinental straits ---
 "West Siberian Sea": [
   {"a0":30,"a1":100,"taxa":[
     ["Inoceramidae","family","sea","Thick clams on the floor of the vast shallow sea flooding the West Siberian basin."],
     ["Selachii","superorder","sea","Sharks whose shed teeth are the commonest vertebrate fossil of the epeiric sea."],
     ["Diatomea","class","sea","(younger) Diatom blooms so vast they left the diatomite of the West Siberian basin."]]}],
 "Trans-Saharan Sea": [
   {"a0":50,"a1":100,"taxa":[
     ["Mosasauridae","family","sea","Mosasaurs of the shallow sea that split Africa, known from superb Moroccan and Malian skeletons."],
     ["Selachii","superorder","sea","A dazzling shark and ray fauna — the phosphate beds of Morocco are built from their teeth."],
     ["Archaeoceti","suborder","sea","(younger) Early whales like Basilosaurus in the warm Eocene straits before the sea withdrew."]]}],
 # --- Modern-facing basins ---
 "South China Sea": [
   {"a0":0,"a1":33,"taxa":[
     ["Scleractinia","order","sea","Coral reefs of the Coral Triangle — the most biodiverse marine region on Earth today."],
     ["Foraminifera","class","sea","Larger reef foraminifera building carbonate sands across the tropical shelf."],
     ["Actinopterygii","class","sea","The richest reef-fish fauna anywhere, radiating through the young sea."]]}],
 "Tasman Sea": [
   {"a0":0,"a1":85,"taxa":[
     ["Cetacea","order","sea","Whales and dolphins of the cool temperate sea opening between Australia and Zealandia."],
     ["Bryozoa","phylum","sea","Cool-water bryozoan and shell gravels rather than tropical coral — the temperate carbonate style."],
     ["Nautilus","genus","sea","The living Nautilus, a survivor of the once-vast shelled-cephalopod dynasties, still haunts these depths."]]}],
 # --- Gulf of Mexico: Cretaceous reef margins, then a deep Cenozoic basin ---
 "Gulf of Mexico": [
   {"a0":66,"a1":170,"taxa":[
     ["Rudistes","order","sea","Rudist bivalves built the great Cretaceous reef rim (the El Abra / Golden Lane banks) around the young Gulf."],
     ["Globotruncanidae","family","sea","Keeled planktonic foraminifera raining onto the deep Gulf floor and into its oil-source chalks."],
     ["Ammonoidea","subclass","sea","Ammonites over the open Gulf, ended abruptly by the Chicxulub impact on its own southeastern rim."]]},
   {"a0":0,"a1":66,"taxa":[
     ["Foraminifera","class","sea","Deep-water foraminifera whose ooze became the source rock for the Gulf's vast oil and gas."],
     ["Bivalvia","class","sea","Rich molluscan shelf faunas along the subsiding northern Gulf margin."],
     ["Carcharocles","genus","sea","Megatooth and other large sharks in the warm Neogene Gulf."]]}],
 # --- Mid-ocean ridges: chemosynthetic hydrothermal-vent ecosystems ---
 "Mid-Atlantic Ridge": [
   {"a0":0,"a1":170,"taxa":[
     ["Rimicaris","genus","sea","Swarming eyeless vent shrimp that dominate Atlantic hydrothermal chimneys, farming bacteria on their shells."],
     ["Bathymodiolus","genus","sea","Vent mussels living on sulphur-eating bacteria in their gills — no sunlight, no photosynthesis."],
     ["Archaea","phylum","sea","Heat- and sulphur-loving microbes at the base of a food web run entirely on chemistry, not light."]]}],
 "East Pacific Rise": [
   {"a0":0,"a1":30,"taxa":[
     ["Riftia","genus","sea","Giant tube worms up to 2 m long, mouthless and gutless, fed by symbiotic bacteria — icons of the 1977 vent discovery."],
     ["Calyptogena","genus","sea","Big white chemosynthetic clams clustered in the warm sulphide flow around Pacific vents."],
     ["Alvinella","genus","sea","The 'Pompeii worm', living on chimney walls in some of the hottest water any animal endures."]]}],
 # --- Paleocene remnant of the Western Interior Sea ---
 "Cannonball Sea": [
   {"a0":58,"a1":62,"taxa":[
     ["Cucullaea","genus","sea","Robust ark-clams crowding the sandy floor of the last Paleocene remnant of the interior sea."],
     ["Selachii","superorder","sea","Sharks and rays recolonising the epeiric sea after the end-Cretaceous crisis."],
     ["Foraminifera","class","sea","Recovering foraminiferal faunas dating the brief Paleocene marine incursion."]]}],
 # --- Jurassic corridors that mixed faunal realms ---
 "Viking Corridor": [
   {"a0":155,"a1":195,"taxa":[
     ["Belemnitida","order","sea","Belemnites of the North Sea seaway that let boreal and Tethyan faunas mingle."],
     ["Ammonoidea","subclass","sea","Ammonites whose mixing across this strait is how the boreal and Tethyan Jurassic are correlated."],
     ["Gryphaea","genus","sea","Coiled oysters strewn through the dark organic muds that became North Sea oil shales."]]}],
 "Hispanic Corridor": [
   {"a0":150,"a1":190,"taxa":[
     ["Ammonoidea","subclass","sea","The corridor itself is defined by ammonites — their sudden trans-Pangaean spread marks the seaway opening."],
     ["Bivalvia","class","sea","Bivalves dispersing between the eastern Pacific and western Tethys through the narrow tropical strait."]]}],
}

# New keys that are STRICTLY marine (realm-locked). Solnhofen (Lagerstätte with
# birds/pterosaurs/dinosaurs) and Lake Pannon (brackish, endemic freshwater
# molluscs + shore mammals) are intentionally left out so their mixed faunas show.
NEW_MARINE = {
 "Muschelkalk Sea","Mowry Sea","Boreal Sea","Bearpaw Sea","Neotethys","Nama Sea",
 "Sundance Sea","Tippecanoe Sea","Kaskaskia Sea","Absaroka Sea","Central American Sea",
 "Messinian Salt Basin","West Siberian Sea","Trans-Saharan Sea","South China Sea",
 "Tasman Sea",
 # Hudson Seaway already in MARINE_REGIONS but carries Hesperornis (air, a diving
 # BIRD that lived in the sea) -- it must NOT be realm-locked, so it is removed
 # from MARINE_REGIONS in life.py instead of listed here.
}


def main():
    d = json.load(open(DATA))
    rt = d.setdefault("region_taxa", {})
    for k, v in NEW.items():
        rt[k] = v
    json.dump(d, open(DATA, "w"), separators=(",", ":"))
    print(f"added/updated {len(NEW)} marine region_taxa entries; "
          f"region_taxa now covers {len(rt)} regions")
    print("strictly-marine additions for MARINE_REGIONS:", sorted(NEW_MARINE))


if __name__ == "__main__":
    main()
