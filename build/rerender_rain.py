"""RETIRED (3.19). Use bake_rain.py.

This was the first surgical rain writer (the carved-grid round). It predates the
present-day anchor (rain_anchor.py), the polar low-pass and the sea fill
(rain_fill.py), so running it would silently strip all three from every
Phanerozoic keyframe. bake_rain.py mirrors export() exactly and covers all 251.

    ../venv/bin/python bake_rain.py                # every keyframe
    ../venv/bin/python bake_rain.py --ages 0,240   # just these
"""
import sys

if __name__ == "__main__":
    sys.exit("rerender_rain.py is retired: run bake_rain.py (see its docstring)")
