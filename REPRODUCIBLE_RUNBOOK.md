# Reproducible runbook

## Purpose

This runbook reproduces the public figures from already-derived audit tables. It does not download, redistribute or process raw third-party data.

## Environment

Tested with Python 3.11 on Windows. The script uses only `matplotlib` and the Python standard library.

```bash
pip install -r requirements.txt
```

## Inputs

Required files:

- `data/A1_overture_completeness_public.csv`
- `data/evidence_readiness_scores.csv`

Supporting derived audit tables:

- `data/A2_era5_inventory.csv`
- `data/A3_osm_file_city_map.csv`
- `data/A5_ghs_city_join.csv`
- `data/city_manifest.csv`

The public A1 table replaces local source paths with portable source file names.

## Reproduce figures

```bash
python scripts/make_figures.py
```

Expected outputs:

- `figures/Figure_1_evidence_stack_table.png`
- `figures/Figure_2_height_availability.png`
- `figures/Figure_3_mapped_vs_attribute_readiness.png`
- `figures/Figure_4_typology_matrix_table.png`

## Quality checks

After running the script, confirm that:

- Figure 1 is a table-form evidence-stack figure.
- Figure 2 is sorted from highest to lowest `height` availability.
- Figure 3 has no city-label overlap and no legend over data marks.
- Figure 4 is a table-form typology matrix.

## Data boundary

The repository contains derived audit tables only. To rerun the original raw-data audits, obtain the source datasets from the providers listed in `DATASETS_AND_LINKS.csv` and follow their respective terms of use.

