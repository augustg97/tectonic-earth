# Source documents

Verbatim copies of material the dossiers depend on, kept locally so a claim can be
re-checked without re-fetching (and so a broken link later does not orphan a citation).

**Empty as of 2026-07-26** — the first round worked from live fetches, all cited in the
dossiers with a retrieval date. This folder is where the primary literature goes as it is
obtained.

## What belongs here

- Open-access papers and preprints (PDF), named `AuthorYear-short-title.pdf`.
- Published data tables: the PhanDA GMST series, GEOCARBSULF output, eustatic curves,
  hotspot catalogues, LIP inventories.
- Machine-readable model files that the dossiers reference (rotation files, timescale
  CSVs), where licensing allows redistribution.

## What does not

- **Paywalled full texts.** Cite them; do not store them. A DOI and a note of what was
  taken from it is the record.
- Large binaries that duplicate `data/` — the PaleoDEMs and the Merdith rotation set are
  already in the repo's gitignored `data/` folder and should not be copied here.

## Wanted, in priority order

| item | why |
|---|---|
| **Judd, Tierney et al. 2024, *Science* 385 eadk3705 — PhanDA supplementary GMST series** | the reference standard for global temperature; needed to diff against `climate.py` (gap C1) |
| **Torsvik & Cocks, *Earth History and Palaeogeography* (2017)** | the standard treatment of the longitude problem and the LLSVP frame (gap A1/A3) |
| **Steinberger, B. 2000, *JGR* 105 — hotspot catalogue** | coordinates for the plume/seamount fix (gaps D1–D3) |
| **Lyons, Reinhard & Planavsky 2014, *Nature* 506, 307** | the standard oxygenation history |
| **Krause, Mills et al. 2022, *Annu. Rev. Earth Planet. Sci.*** | current Phanerozoic O₂ curve (gap C3) |
| Haq & Schutter 2008; Snedden & Liu 2010 | the eustatic curves we must choose between (gap C7) |
| Merdith et al. 2021 supplementary — does it document its longitude convention? | bears directly on the frame mismatch |
| Any published **PALEOMAP rotation file** | would make the frame correction unnecessary (gap A1) |

## Licensing

Same policy as the rest of the project: store only what may be redistributed —
public domain, CC0, CC-BY, or an author's own posted preprint where that is permitted.
Record the licence alongside the file.
