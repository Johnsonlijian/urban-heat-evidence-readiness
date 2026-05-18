# Data directory

This directory contains derived audit tables only.

## Files

- `A1_overture_completeness_public.csv`: Overture attribute completeness by city. Local source paths and raw file names are excluded.
- `A2_era5_inventory.csv`: derived inventory of audited ERA5 daily files by city and date. Raw file names are excluded.
- `A3_osm_file_city_map.csv`: derived OSM cache assignment audit. Cache file names are excluded.
- `A5_ghs_city_join.csv`: derived GHS city-join support table.
- `city_manifest.csv`: 30-city audit manifest with high-level layer availability.
- `evidence_readiness_scores.csv`: final city-level readiness typology used by the figures.

No raw Overture, ERA5, OSM or GHSL files are redistributed here.
