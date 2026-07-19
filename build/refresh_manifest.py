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

from climate import climate_at, system_at
from render import glaciation
from build_frames import period_for, sealevel_for

MAN = "../web/fields/manifest.json"


def main():
    man = json.load(open(MAN))
    changed = 0
    for rec in man:
        age = rec["age"]
        cl = climate_at(age)
        ice_T, sea_T = glaciation(cl)
        ep, per = period_for(age)
        sysd = system_at(age)
        new = {"epoch": ep, "period": per, "sealevel": sealevel_for(age),
               "temp": round(cl["temp"], 3), "veg": round(cl["veg"], 3),
               "iceT": round(ice_T, 2), "seaT": round(sea_T, 2),
               "gmst": sysd["gmst"], "co2": sysd["co2"], "o2": sysd["o2"]}
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
