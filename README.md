# Urban heat-adaptation evidence-readiness audit

This repository contains a public reproducibility package for a 30-city audit of open building and climate-data readiness for urban heat-adaptation screening.

The associated manuscript is framed around a bounded claim: mapped open building footprints are not automatically actionable building-scale heat-adaptation evidence. The repository supports that claim with derived audit tables, figure-generation code and generated figure previews. It does not include active submission files.

## What is included

- Derived audit tables in `data/`.
- Figure-generation code in `scripts/make_figures.py`.
- Generated PNG figure previews in `figures/`.
- A reproducible runbook in `REPRODUCIBLE_RUNBOOK.md`.
- Dataset source links and redistribution boundaries in `DATASETS_AND_LINKS.csv`.
- A short public study summary in `docs/PAPER_SUMMARY.md`.

## What is not included

This repository intentionally excludes raw third-party data, local download archives, NetCDF files, GeoJSON building files, the active manuscript, title page, cover letter, journal submission ZIP files, review drafts, private author or funding metadata, internal logs and sync-conflict copies.

## Core derived result

The public derived tables record 1,454,543 audited Overture building features across 30 city-level files. The Overture `height` field is treated as a sentinel attribute for vertical-form interpretability rather than as a complete heat-risk descriptor. Its city-level non-null availability is highly uneven, with the current audit producing an actionable / proxy-limited / evidence-blind split of 4 / 19 / 7 cities.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\make_figures.py
```

Generated figures are written to `figures/`.

## Repository boundary

The package supports reproducibility of the public audit tables and figures. It is not a heat-risk model, mortality model, indoor-temperature model, microclimate simulation or causal-impact estimate.

## Citation

Please cite the associated paper when it is available. Until then, cite this repository and the original data products listed in `DATASETS_AND_LINKS.csv`.

