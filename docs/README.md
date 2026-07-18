# Tectonic Earth

Interactive deep-time reconstruction of Earth's surface, 1000 Ma to +250 Myr.

A WebGL terrain engine interpolates per-keyframe elevation and rainfall
fields, so coastlines migrate continuously rather than cross-fading, and
relief is shaded per pixel. Climate (winds, moisture advection, orographic
rain shadows, monsoons) is derived rather than painted on.

## Running locally

It is a static site — any web server will do:

```sh
python3 -m http.server 8000
```

then open <http://localhost:8000>.

## Data sources

- Paleogeography & elevation — Scotese & Wright (2018), *PALEOMAP PaleoDEMs*, CC-BY 4.0
- Present plate motions — NNR-MORVEL56 (Argus, Gordon & DeMets, 2011)
- Plate boundaries — Bird (2003), *PB2002*

Pre-540 Ma and future frames are authored reconstructions and are
illustrative rather than exact.
