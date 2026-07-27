# Frame-switch regression gate

```
158 tracked features scored on their own age windows
  improved    58
  unchanged   79
  regressed   21

mean score  old 0.746  ->  new 0.833

regressions by cause:
  TRUE             7
  CANCELLATION     3
  DEM-LIMITED      3
  PRE-EXISTING     8

TRUE regressions - the only class that should block a ship:
  Newark Rift Valleys                rift       1.00 -> 0.20
  Red Sea Rift                       rift       0.67 -> 0.00
  Gulf of California                 rift       0.50 -> 0.00
  Cimmerian Belt                     orogen     0.86 -> 0.43
  West Antarctic Rift                rift       0.64 -> 0.27
  Kerguelen Microcontinent           island     0.75 -> 0.50
  Rhodope Massif                     orogen     0.62 -> 0.46

GATE: ship if TRUE == 0, or if every TRUE case has been inspected and has a
recorded reason. Everything else is a pre-existing error becoming visible, which
is a reason to FIX THE FEATURE, not to keep the compensating error.
```

| feature | type | old | new | verdict | cause |
|---|---|---|---|---|---|
| Newark Rift Valleys | rift | 1.00 | 0.20 | regressed | TRUE |
| Mediterranean | sea | 0.67 | 0.00 | regressed | DEM-LIMITED |
| Red Sea Rift | rift | 0.67 | 0.00 | regressed | TRUE |
| Gulf of California | rift | 0.50 | 0.00 | regressed | TRUE |
| South China Sea | sea | 0.50 | 0.00 | regressed | DEM-LIMITED |
| Gulf of Mexico | sea | 0.44 | 0.00 | regressed | PRE-EXISTING |
| Cimmerian Belt | orogen | 0.86 | 0.43 | regressed | TRUE |
| Mascarene Plateau | region | 0.40 | 0.00 | regressed | PRE-EXISTING |
| West Antarctic Rift | rift | 0.64 | 0.27 | regressed | TRUE |
| Sea of Japan | sea | 0.67 | 0.33 | regressed | DEM-LIMITED |
| Michigan Basin | basin | 0.30 | 0.00 | regressed | PRE-EXISTING |
| Kerguelen Microcontinent | island | 0.75 | 0.50 | regressed | TRUE |
| East Tasman Plateau | island | 0.33 | 0.11 | regressed | PRE-EXISTING |
| Argoland | island | 0.40 | 0.20 | regressed | PRE-EXISTING |
| Broken Ridge | region | 0.20 | 0.00 | regressed | PRE-EXISTING |
| Walvis Ridge | region | 0.23 | 0.08 | regressed | PRE-EXISTING |
| Rhodope Massif | orogen | 0.62 | 0.46 | regressed | TRUE |
| Tasman Sea | sea | 0.11 | 0.00 | regressed | PRE-EXISTING |
| Cimmeria | continent | 0.58 | 0.50 | regressed | CANCELLATION |
| Tethyan Himalaya | region | 1.00 | 0.92 | regressed | CANCELLATION |
| Lachlan Orogen | orogen | 0.86 | 0.84 | regressed | CANCELLATION |
| North America | continent | 1.00 | 1.00 | unchanged |  |
| South America | continent | 1.00 | 1.00 | unchanged |  |
| Africa | continent | 1.00 | 1.00 | unchanged |  |
| Eurasia | continent | 1.00 | 1.00 | unchanged |  |
| Australia | continent | 1.00 | 1.00 | unchanged |  |
| India | continent | 1.00 | 1.00 | unchanged |  |
| Rocky Mountains | orogen | 1.00 | 1.00 | unchanged |  |
| Atlas | orogen | 1.00 | 1.00 | unchanged |  |
| Laurasia | continent | 1.00 | 1.00 | unchanged |  |
| Cordillera | orogen | 1.00 | 1.00 | unchanged |  |
| Pangaea | continent | 1.00 | 1.00 | unchanged |  |
| Central Pangaean Mts | orogen | 1.00 | 1.00 | unchanged |  |
| Ural Mountains | orogen | 1.00 | 1.00 | unchanged |  |
| Variscan Belt | orogen | 1.00 | 1.00 | unchanged |  |
| Avalonia | continent | 1.00 | 1.00 | unchanged |  |
| Taconic Belt | orogen | 1.00 | 1.00 | unchanged |  |
| Trans-Saharan Sea | sea | 1.00 | 1.00 | unchanged |  |
| Karoo Basin | basin | 1.00 | 1.00 | unchanged |  |
| Songliao Basin | basin | 1.00 | 1.00 | unchanged |  |
| Navajo Erg | desert | 0.00 | 0.00 | unchanged |  |
| Gobi Erg | desert | 1.00 | 1.00 | unchanged |  |
| Angaran Flora Belt | forest | 1.00 | 1.00 | unchanged |  |
| Glossopteris Flora | forest | 1.00 | 1.00 | unchanged |  |
| Amazon Rainforest | forest | 1.00 | 1.00 | unchanged |  |
| Great Plains | grassland | 1.00 | 1.00 | unchanged |  |
| Eurasian Steppe | grassland | 1.00 | 1.00 | unchanged |  |
| African Savanna | grassland | 1.00 | 1.00 | unchanged |  |
| Tibetan Alpine Tundra | tundra | 1.00 | 1.00 | unchanged |  |
| East Antarctic Ice Sheet | ice | 1.00 | 1.00 | unchanged |  |
| Hun Superterrane | island | 1.00 | 1.00 | unchanged |  |
| Greater India | island | 1.00 | 1.00 | unchanged |  |
| Parana Basin | basin | 1.00 | 1.00 | unchanged |  |
| Solimoes Basin | basin | 1.00 | 1.00 | unchanged |  |
| Congo Basin | basin | 1.00 | 1.00 | unchanged |  |
| Ethiopian Highlands | region | 1.00 | 1.00 | unchanged |  |
| Cameroon Line | orogen | 1.00 | 1.00 | unchanged |  |
| Ontong Java Plateau | region | 0.00 | 0.00 | unchanged |  |
| Manihiki Plateau | region | 0.00 | 0.00 | unchanged |  |
| Agulhas Plateau | region | 0.00 | 0.00 | unchanged |  |
| Mauritia | island | 0.00 | 0.00 | unchanged |  |
| Qinling-Dabie Belt | orogen | 1.00 | 1.00 | unchanged |  |
| Tibetan Plateau | plateau | 1.00 | 1.00 | unchanged |  |
| Colorado Plateau | plateau | 1.00 | 1.00 | unchanged |  |
| Altiplano | plateau | 1.00 | 1.00 | unchanged |  |
| Old Red Sandstone Continent | region | 1.00 | 1.00 | unchanged |  |
| Wallacea | region | 0.50 | 0.50 | unchanged |  |
| Benue Trough | rift | 0.33 | 0.33 | unchanged |  |
| Rhine Graben | rift | 1.00 | 1.00 | unchanged |  |
| East African Rift | rift | 1.00 | 1.00 | unchanged |  |
| Baikal Rift | rift | 1.00 | 1.00 | unchanged |  |
| Hispanic Corridor | sea | 1.00 | 1.00 | unchanged |  |
| Boreal Sea | sea | 1.00 | 1.00 | unchanged |  |
| Songliao Palaeolake | lake | 1.00 | 1.00 | unchanged |  |
| Jehol Lakes | lake | 1.00 | 1.00 | unchanged |  |
| Lake Baikal | lake | 1.00 | 1.00 | unchanged |  |
| Lake Vostok | lake | 1.00 | 1.00 | unchanged |  |
| Lake Tanganyika | lake | 1.00 | 1.00 | unchanged |  |
| Zagros Mts | orogen | 1.00 | 1.00 | unchanged |  |
| Greater Caucasus | orogen | 1.00 | 1.00 | unchanged |  |
| Carpathians | orogen | 1.00 | 1.00 | unchanged |  |
| Apennines | orogen | 1.00 | 1.00 | unchanged |  |
| Sonoma Orogeny | orogen | 1.00 | 1.00 | unchanged |  |
| Rio Grande Rift | rift | 1.00 | 1.00 | unchanged |  |
| Basin and Range | rift | 1.00 | 1.00 | unchanged |  |
| West Siberian Sea | sea | 1.00 | 1.00 | unchanged |  |
| Arabian Desert | desert | 1.00 | 1.00 | unchanged |  |
| Kalahari Desert | desert | 1.00 | 1.00 | unchanged |  |
| Australian Desert | desert | 1.00 | 1.00 | unchanged |  |
| Patagonian Desert | desert | 1.00 | 1.00 | unchanged |  |
| Sichuan Basin | basin | 1.00 | 1.00 | unchanged |  |
| Qaidam Basin | basin | 1.00 | 1.00 | unchanged |  |
| West Siberian Basin | basin | 1.00 | 1.00 | unchanged |  |
| Kunlun Belt | orogen | 0.88 | 0.88 | unchanged |  |
| Okhotsk Sea | sea | 0.75 | 0.75 | unchanged |  |
| Yakutat Terrane | island | 1.00 | 1.00 | unchanged |  |
| Hangai Uplift | orogen | 1.00 | 1.00 | unchanged |  |
| Ethiopian Highlands | plateau | 1.00 | 1.00 | unchanged |  |
| East African Plateau | plateau | 1.00 | 1.00 | unchanged |  |
| Brazilian Shield | region | 0.98 | 1.00 | unchanged |  |
| Tien Shan | orogen | 0.97 | 1.00 | improved |  |
| Junggar Basin | basin | 0.97 | 1.00 | improved |  |
| Appalachians | orogen | 0.96 | 1.00 | improved |  |
| Deccan Plateau (basement) | region | 0.95 | 1.00 | improved |  |
| Verkhoyansk Belt | orogen | 0.94 | 1.00 | improved |  |
| Shatsky Rise | region | 0.00 | 0.07 | improved |  |
| Ordos Basin | basin | 0.92 | 1.00 | improved |  |
| Fennoscandian Shield | region | 0.91 | 1.00 | improved |  |
| Maracaibo Basin | basin | 0.90 | 1.00 | improved |  |
| Rio Grande Rise | region | 0.11 | 0.22 | improved |  |
| Pyrenees | orogen | 0.89 | 1.00 | improved |  |
| Sierras Pampeanas | orogen | 0.89 | 1.00 | improved |  |
| Bohemian Massif | orogen | 0.89 | 1.00 | improved |  |
| Iberian Massif | orogen | 0.89 | 1.00 | improved |  |
| Antarctica | continent | 0.88 | 1.00 | improved |  |
| Sierra Nevada Arc | orogen | 0.88 | 1.00 | improved |  |
| Williston Basin | basin | 0.88 | 1.00 | improved |  |
| Caledonides | orogen | 0.87 | 1.00 | improved |  |
| Anatolide-Tauride Block | continent | 0.31 | 0.46 | improved |  |
| Ellesmerian Belt | orogen | 0.84 | 1.00 | improved |  |
| Himalaya | orogen | 0.83 | 1.00 | improved |  |
| Guiana Shield | region | 0.82 | 1.00 | improved |  |
| Altai Belt | orogen | 0.80 | 1.00 | improved |  |
| Alborz Belt | orogen | 0.80 | 1.00 | improved |  |
| Pontide Arc | orogen | 0.80 | 1.00 | improved |  |
| Massif Central | orogen | 0.80 | 1.00 | improved |  |
| Oaxaquia | island | 0.60 | 0.80 | improved |  |
| Lhasa Terrane | island | 0.77 | 1.00 | improved |  |
| Annamia | continent | 0.76 | 1.00 | improved |  |
| Baltica | continent | 0.75 | 1.00 | improved |  |
| Cape Fold Belt | orogen | 0.73 | 1.00 | improved |  |
| Kolyma-Omolon Terrane | island | 0.62 | 0.88 | improved |  |
| Greenland | region | 0.71 | 1.00 | improved |  |
| Kaskaskia Sea | sea | 0.67 | 1.00 | improved |  |
| South China | continent | 0.65 | 1.00 | improved |  |
| Qilian Belt | orogen | 0.60 | 0.98 | improved |  |
| Kazakhstania | continent | 0.20 | 0.60 | improved |  |
| Innuitian Belt | orogen | 0.60 | 1.00 | improved |  |
| Deccan Traps | plateau | 0.57 | 1.00 | improved |  |
| Tarim Block | continent | 0.47 | 0.95 | improved |  |
| Amuria | continent | 0.52 | 1.00 | improved |  |
| Alps | orogen | 0.50 | 1.00 | improved |  |
| Atacama Desert | desert | 0.50 | 1.00 | improved |  |
| Wrangellia Terrane | island | 0.33 | 0.89 | improved |  |
| Sibumasu | island | 0.40 | 1.00 | improved |  |
| Patagonian Batholith | region | 0.38 | 1.00 | improved |  |
| Greater Adria | island | 0.36 | 1.00 | improved |  |
| Antarctic Nothofagus Forest | forest | 0.33 | 1.00 | improved |  |
| Zealandia | island | 0.11 | 0.78 | improved |  |
| Armorica | island | 0.10 | 0.80 | improved |  |
| North China | continent | 0.26 | 1.00 | improved |  |
| Namib | desert | 0.25 | 1.00 | improved |  |
| Famatinian Belt | orogen | 0.20 | 1.00 | improved |  |
| Central Asian Orogenic Belt | orogen | 0.00 | 0.83 | improved |  |
| Andes | orogen | 0.14 | 1.00 | improved |  |
| Sauk Sea | sea | 0.00 | 1.00 | improved |  |
| Central American Sea | sea | 0.00 | 1.00 | improved |  |
| Perunica | island | 0.00 | 1.00 | improved |  |
