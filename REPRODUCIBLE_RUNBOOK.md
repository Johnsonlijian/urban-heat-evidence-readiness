# Reproducible runbook

## Purpose

This runbook reproduces the public figures from already-derived audit tables. It does not download, redistribute or process raw third-party data.

## Environment

Tested with Python 3.11 on Windows. Figure reproduction uses `matplotlib` and the Python standard library. The optional ERA5 temperature-readability summary also uses `numpy`, `xarray` and `netCDF4`.

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
- `data/A6_era5_readable_temperature_daily.csv`
- `data/A6_era5_readable_temperature_window_summary.csv`
- `data/A6_era5_inventory_physical_crosswalk.csv`
- `data/A7_threshold_sensitivity.csv`
- `data/city_manifest.csv`

The public A1 table replaces local source paths with portable source file names.

## Optional ERA5 temperature-readability summary

The A6 tables document a bounded physical-file readability check. When readable ERA5 files are available locally, the script extracts hourly `t2m`, converts kelvin to degrees Celsius, and summarises daily mean, daily maximum and 95th-percentile 2 m temperature. The current public derived A6 summary covers 54 readable physical files across 12 cities. It is a validation subset and is not used to reclassify the main typology.

The A7 table documents threshold sensitivity for the typology. The evidence-blind rule is fixed at `height_rate_in_sample < 0.001`; the actionable rule is checked at 5%, 10% and 20% height availability.

```bash
python scripts/compute_era5_heat_window_summary.py --project-root .
```

## Reproduce figures

```bash
python scripts/make_figures.py
```

Expected outputs:

- `figures/Figure_1_evidence_ladder.png`
- `figures/Figure_2_height_availability.png`
- `figures/Figure_3_mapped_vs_attribute_readiness.png`
- `figures/Figure_4_typology_matrix_table.png`

## Quality checks

After running the script, confirm that:

- Figure 1 is an evidence-readiness ladder with no clipped boxes or connector lines.
- Figure 2 is sorted from highest to lowest `height` availability.
- Figure 3 has no city-label overlap and no legend over data marks.
- Figure 4 is a table-form typology matrix.

## Data boundary

The repository contains derived audit tables only. To rerun the original raw-data audits, obtain the source datasets from the providers listed in `DATASETS_AND_LINKS.csv` and follow their respective terms of use.
