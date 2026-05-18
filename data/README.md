# Data directory

This directory contains derived audit tables only.

## Files

- `A1_overture_completeness_public.csv`: Overture attribute completeness by city. Local source paths and raw file names are excluded.
- `A2_era5_inventory.csv`: derived inventory of audited ERA5 daily files by city and date. Raw file names are excluded.
- `A3_osm_file_city_map.csv`: derived OSM cache assignment audit. Cache file names are excluded.
- `A5_ghs_city_join.csv`: derived GHS city-join support table.
- `A6_era5_readable_temperature_daily.csv`: daily 2 m temperature summaries for readable physical ERA5 files available in the local project tree; public copy excludes local file names.
- `A6_era5_readable_temperature_window_summary.csv`: city-level summary of the readable ERA5 temperature subset.
- `A6_era5_inventory_physical_crosswalk.csv`: crosswalk between the A2 inventory and physical files found locally for the readability check.
- `city_manifest.csv`: 30-city audit manifest with high-level layer availability.
- `evidence_readiness_scores.csv`: final city-level readiness typology used by the figures.

The A6 tables are a heat-window validation subset. They do not replace the full A2 inventory and should not be read as a complete ERA5 coverage or heat-risk product.

No raw Overture, ERA5, OSM or GHSL files are redistributed here.
