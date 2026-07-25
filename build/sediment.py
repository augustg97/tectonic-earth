"""Sediment thickness -- what makes an abyssal PLAIN a plain.

On a real bathymetric chart the sea floor divides into two kinds of surface, and
the boundary between them is sharp: rough crust, combed with abyssal hills, and
dead-flat plain. That contrast carries as much of the picture as the depth does,
and we had almost none of it -- one proximity fade standing in for a process.

The process is sediment burial, and it is worth modelling properly because it is
a competition between two quantities we now both have:

  ACCUMULATION. Pelagic ooze rains out of the water column everywhere at roughly
  1-2 m/Myr, several times that under the equatorial upwelling belt where
  productivity is high and again under the sub-polar silica belt. So pelagic
  thickness is essentially rate(latitude) x crustal age -- which is why it needed
  a real age field to compute at all. Terrigenous sediment is a different animal:
  turbidity currents carry continental debris down the slope and pond it against
  the margin, building the continental rise and, beyond it, the abyssal plains,
  kilometres thick and falling off over several hundred kilometres.

  RELIEF. Abyssal hills stand 50-300 m above the crust that carries them.

Where accumulation exceeds relief the hills are buried and the floor is flat --
genuinely flat, with a sharp edge where the sediment wedge thins out. Where it
does not, the fabric shows. That single ratio is the whole model, and it puts the
plains where the real ones are: against every passive margin, and nowhere in the
middle of a young ocean.

Two things follow from it, and both were previously faked:
  * the floor is RAISED where sediment fills it, so a plain is shallower than the
    crust beneath it -- an abyssal plain is a fill terrace, not bare basalt;
  * the fabric is SUPPRESSED there, rather than fading with distance from land.
"""
import numpy as np

# Pelagic accumulation, m/Myr. Open-ocean red clay is slow; the equatorial
# upwelling belt and the sub-polar silica belt are several times faster, which
# is why the Pacific carries a distinct band of thicker sediment on the equator.
# Calibrated against the published global total-sediment-thickness grids, not
# by eye. The targets those set: a global mean near 450 m, deep Pacific 100-500,
# Atlantic 500-1500, continental rises several km, and -- the number that
# matters most here -- abyssal PLAINS covering something like a fifth of the
# ocean floor, with abyssal HILLS the commonest surface on Earth by area. A
# first pass at this buried 90% of the ocean and gave a median of 1189 m, which
# would have made plains the default and hills the exception: the exact inverse
# of the real sea floor.
PELAGIC_BASE = 1.0        # m/Myr: open-ocean red clay
PELAGIC_EQ = 3.0          # extra on the equatorial high-productivity belt
PELAGIC_SUBPOLAR = 1.4    # extra on the silica belt

# Terrigenous wedge: thickness against the margin and how far it reaches. A real
# continental rise is 100-500 km wide, not a thousand, and the fall-off has to
# be that steep or every basin turns into one continuous plain.
TERRIG_MAX = 3500.0       # m at the foot of the slope
TERRIG_DECAY = 3.0        # deg e-folding; ~330 km

# Burial is a threshold, not a gradient: either the sediment is deeper than the
# hills or it is not. Hills stand 50-300 m, so a few hundred metres begins to
# smother them and a kilometre finishes the job.
BURIAL_START = 350.0      # m: fabric starts to go
BURIAL_FULL = 1050.0      # m: a true plain
FILL_FACTOR = 0.35        # how much of a sediment pile shows as shallower floor


def pelagic_rate(lat1d):
    """m/Myr as a function of latitude -- productivity, not geography."""
    la = np.abs(lat1d)
    eq = PELAGIC_EQ * np.exp(-(lat1d / 11.0) ** 2)
    sp = PELAGIC_SUBPOLAR * np.exp(-((la - 55.0) / 14.0) ** 2)
    return (PELAGIC_BASE + eq + sp)[:, None]


def thickness(age_myr, dland_deg, lat1d, river=None):
    """Sediment thickness in metres.

    `dland_deg` is distance to the nearest land, already smoothed -- a raw
    distance transform's level sets follow the pixel lattice and would give the
    wedge right-angled edges.  `river`, if given, is a 0..1 field of fluvial
    discharge reaching the coast, which is what actually decides whether a margin
    builds a great fan or a starved one: the Bengal and Amazon fans exist because
    those rivers do, and a margin with no river behind it stays thin.
    """
    pel = pelagic_rate(lat1d) * np.clip(age_myr, 0.0, None)
    supply = 1.0 if river is None else (0.45 + 1.15 * np.clip(river, 0.0, 1.0))
    ter = TERRIG_MAX * supply * np.exp(-np.clip(dland_deg, 0.0, None) / TERRIG_DECAY)
    return pel + ter


def burial(sed_m):
    """0 = bare crust, 1 = fabric completely buried and the floor is a plain.

    Deliberately steep. The edge of a real abyssal plain is sharp -- you can
    trace it on a chart -- because burial is a threshold, not a gradient: either
    the sediment is deeper than the hills or it is not.
    """
    return np.clip((sed_m - BURIAL_START) / (BURIAL_FULL - BURIAL_START), 0.0, 1.0)
