"""Re-derive the manifest's climate/system metadata without re-rendering.

The field textures depend on elevation and the rainfall solve; the readout
numbers (GMST, CO2, O2, sea level, ice thresholds) are metadata that ride
along in the manifest. Editing only the SYSTEM curves therefore does not
invalidate a single pixel -- but the manifest still carries whatever the
tables said when each keyframe was written, which after a mid-build edit is a
mixture. This rewrites every record's metadata from the current tables so the
whole series is internally consistent again.
"""
import json, os

import numpy as np

import build_fields as bf
import ice_audit
from climate import climate_at, system_at
from render import glaciation, snowball_at
from build_frames import period_for, sealevel_for


def ice_fraction(age, ice_T, sea_T):
    """How much ice the app will ACTUALLY draw at this age.

    The readout used to infer "ice polar caps" from the threshold alone -- any
    value warmer than the ice-free sentinel counted -- which meant it announced
    ice caps at 41 keyframes that drew none. A threshold is an intention; this
    is the outcome. Returns (land ice as a fraction of land, sea ice as a
    fraction of ocean), or (0, 0) if the field is missing.
    """
    base = ("fut_%04d" % abs(age)) if age < 0 else (
        "pre_%04d" % age if age > 540 else "phan_%04d" % age)
    z, rf = ice_audit.fields(base, H=256, W=512)
    if z is None:
        return 0.0, 0.0
    land, li, si, gl, sn, T = ice_audit.ice_masks(z, rf, age, ice_T, sea_T)
    h, w_ = z.shape
    wgt = np.cos(np.radians(np.linspace(90, -90, h)[:, None] * np.ones((1, w_))))
    la = (wgt * land).sum()
    sa = wgt.sum() - la
    return (float((wgt * li).sum() / la) if la else 0.0,
            float((wgt * si).sum() / sa) if sa else 0.0)

MAN = "../web/fields/manifest.json"


def main():
    man = json.load(open(MAN))
    changed = 0
    for rec in man:
        age = rec["age"]
        # The FILENAMES are re-derived too, not just the metadata. Elevation
        # moved from WebP to AVIF and this file rewrites every record; if it
        # carried the old name forward the app would fetch a texture that is no
        # longer there and the globe would come up blank, with nothing in the
        # build saying why. build_fields owns the naming; ask it.
        tag = "fut" if age < 0 else ("pre" if age > 540 else "phan")
        ef = bf.elev_name(tag, age)
        rec["e"] = ef
        rec["r"] = bf.sibling(ef, "r")
        rec["m"] = bf.sibling(ef, "m")
        cl = climate_at(age)
        ice_T, sea_T = glaciation(cl)
        ep, per = period_for(age)
        sysd = system_at(age)
        li, si = ice_fraction(age, ice_T, sea_T)
        new = {"epoch": ep, "period": per, "sealevel": sealevel_for(age),
               "temp": round(cl["temp"], 3), "veg": round(cl["veg"], 3),
               "iceT": round(ice_T, 2), "seaT": round(sea_T, 2),
               "snowball": round(snowball_at(cl), 3),
               "iceLand": round(li, 4), "iceSea": round(si, 4),
               "gmst": sysd["gmst"], "co2": sysd["co2"], "o2": sysd["o2"],
               "sol": sysd["sol"]}
        if any(rec.get(k) != v for k, v in new.items()):
            changed += 1
        rec.update(new)
    json.dump(man, open(MAN, "w"), separators=(",", ":"))
    print(f"manifest: {len(man)} keyframes, {changed} refreshed")
    for probe in (0, 90, 300, 445, 540, 655, 690, -100):
        r = next((m for m in man if m["age"] == probe), None)
        if r:
            print(f"  {probe:>5} Ma  {r['gmst']:6.1f} C  {r['co2']:6.0f} ppm  "
                  f"{r['o2']:5.1f}% O2  sea {r['sealevel']:+5d} m  "
                  f"ice below {r['iceT']:.0f} C")


if __name__ == "__main__":
    main()
