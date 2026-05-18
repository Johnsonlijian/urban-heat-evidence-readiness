"""Compute a bounded ERA5 2 m temperature heat-window summary.

The manuscript's A2 table is a file-level inventory. This script performs a
separate readability and heat-indicator check on physical ERA5 files currently
present in the local project tree. Some downloaded files are ZIP containers
with an embedded NetCDF member, so the reader handles both plain NetCDF and
ZIP-wrapped NetCDF inputs.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr


PROJECT_DEFAULT = Path(__file__).resolve().parents[1]
ERA5_NAME_RE = re.compile(r"(?P<city>.+?)_era5_(?P<date>\d{8})\.nc$", re.I)
EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "github_reproducibility_urban_climate",
    "submission_urban_climate_2026-05-15",
}


def is_candidate(path: Path) -> bool:
    if path.suffix.lower() != ".nc":
        return False
    if not ERA5_NAME_RE.match(path.name):
        return False
    lower_parts = {part.lower() for part in path.parts}
    return not any(part.lower() in lower_parts for part in EXCLUDE_PARTS)


def open_dataset(path: Path):
    """Open a plain NetCDF file or a ZIP-wrapped NetCDF file."""
    tmpdir = None
    try:
        if zipfile.is_zipfile(path):
            tmpdir = Path(tempfile.mkdtemp(prefix="era5_zip_"))
            with zipfile.ZipFile(path) as zf:
                members = [name for name in zf.namelist() if name.lower().endswith(".nc")]
                if not members:
                    raise ValueError("ZIP container has no .nc member")
                zf.extract(members[0], tmpdir)
                target = tmpdir / members[0]
        else:
            target = path
        ds = xr.open_dataset(target, engine="netcdf4")
        return ds, tmpdir
    except Exception:
        if tmpdir is not None:
            shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def celsius(values: xr.DataArray) -> xr.DataArray:
    units = str(values.attrs.get("units", "")).strip().lower()
    if units in {"k", "kelvin"}:
        return values - 273.15
    return values


def file_record(path: Path) -> dict[str, object]:
    match = ERA5_NAME_RE.match(path.name)
    if not match:
        raise ValueError(f"Cannot parse ERA5 filename: {path.name}")
    city = match.group("city")
    date = datetime.strptime(match.group("date"), "%Y%m%d").date().isoformat()
    record: dict[str, object] = {
        "city": city,
        "date": date,
        "filename": path.name,
        "readable": False,
        "error": "",
    }
    tmpdir = None
    ds = None
    try:
        ds, tmpdir = open_dataset(path)
        if "t2m" not in ds.data_vars:
            raise ValueError("t2m variable not found")
        t2m = celsius(ds["t2m"])
        record.update(
            {
                "readable": True,
                "time_steps": int(t2m.sizes.get("valid_time", t2m.sizes.get("time", 0))),
                "lat_points": int(t2m.sizes.get("latitude", 0)),
                "lon_points": int(t2m.sizes.get("longitude", 0)),
                "mean_t2m_c": round(float(t2m.mean(skipna=True).values), 3),
                "max_t2m_c": round(float(t2m.max(skipna=True).values), 3),
                "p95_t2m_c": round(float(t2m.quantile(0.95, skipna=True).values), 3),
            }
        )
    except Exception as exc:
        record["error"] = repr(exc)
    finally:
        if ds is not None:
            ds.close()
        if tmpdir is not None:
            shutil.rmtree(tmpdir, ignore_errors=True)
    return record


def summarise(records: list[dict[str, object]]) -> list[dict[str, object]]:
    by_city: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in records:
        by_city[str(row["city"])].append(row)
    summary = []
    for city, rows in sorted(by_city.items()):
        readable = [row for row in rows if row.get("readable")]
        dates = sorted(str(row["date"]) for row in readable)
        max_values = np.array([float(row["max_t2m_c"]) for row in readable], dtype=float)
        mean_values = np.array([float(row["mean_t2m_c"]) for row in readable], dtype=float)
        if readable:
            summary.append(
                {
                    "city": city,
                    "physical_files_found": len(rows),
                    "readable_temperature_files": len(readable),
                    "first_readable_date": dates[0],
                    "last_readable_date": dates[-1],
                    "mean_daily_mean_t2m_c": round(float(mean_values.mean()), 3),
                    "p95_daily_max_t2m_c": round(float(np.quantile(max_values, 0.95)), 3),
                    "max_daily_max_t2m_c": round(float(max_values.max()), 3),
                    "hot_days_tmax_ge_30c": int((max_values >= 30.0).sum()),
                    "hot_days_tmax_ge_35c": int((max_values >= 35.0).sum()),
                    "source_scope": "readable physical ERA5 files present in local project tree",
                }
            )
        else:
            summary.append(
                {
                    "city": city,
                    "physical_files_found": len(rows),
                    "readable_temperature_files": 0,
                    "first_readable_date": "",
                    "last_readable_date": "",
                    "mean_daily_mean_t2m_c": "",
                    "p95_daily_max_t2m_c": "",
                    "max_daily_max_t2m_c": "",
                    "hot_days_tmax_ge_30c": "",
                    "hot_days_tmax_ge_35c": "",
                    "source_scope": "readability check failed",
                }
            )
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def inventory_crosswalk(root: Path, records: list[dict[str, object]], physical_files: list[Path]) -> list[dict[str, object]]:
    inv_path = root / "outputs" / "A2_era5_inventory.csv"
    if not inv_path.exists():
        return []
    with inv_path.open(newline="", encoding="utf-8") as handle:
        inv_rows = list(csv.DictReader(handle))
    physical_names = {path.name for path in physical_files}
    readable_names = {str(row["filename"]) for row in records if row.get("readable")}
    cities = sorted({row["city"] for row in inv_rows} | {str(row["city"]) for row in records})
    crosswalk = []
    for city in cities:
        inv_city = [row for row in inv_rows if row["city"] == city]
        physical_city = [row for row in records if row["city"] == city]
        crosswalk.append(
            {
                "city": city,
                "A2_inventory_days": len(inv_city),
                "A2_inventory_files_found_as_physical": sum(1 for row in inv_city if row["filename"] in physical_names),
                "A2_inventory_files_readable_as_temperature": sum(1 for row in inv_city if row["filename"] in readable_names),
                "physical_era5_files_present": len(physical_city),
                "readable_temperature_files_present": sum(1 for row in physical_city if row.get("readable")),
            }
        )
    return crosswalk


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_DEFAULT)
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    root = args.project_root.resolve()
    out_dir = args.out_dir.resolve() if args.out_dir else root / "outputs"
    candidates = sorted(path for path in root.rglob("*.nc") if is_candidate(path))
    records = [file_record(path) for path in candidates]
    daily_rows = [
        {key: value for key, value in row.items() if key != "error"}
        for row in records
        if row.get("readable")
    ]
    summary_rows = summarise(records)
    error_rows = [
        {key: value for key, value in row.items() if key in {"city", "date", "filename", "readable", "error"}}
        for row in records
        if not row.get("readable")
    ]

    write_csv(out_dir / "A6_era5_readable_temperature_daily.csv", daily_rows)
    write_csv(out_dir / "A6_era5_readable_temperature_window_summary.csv", summary_rows)
    write_csv(out_dir / "A6_era5_readability_errors.csv", error_rows)
    write_csv(out_dir / "A6_era5_inventory_physical_crosswalk.csv", inventory_crosswalk(root, records, candidates))

    print(f"Scanned {len(candidates)} candidate physical ERA5 files")
    print(f"Readable temperature files: {len(daily_rows)}")
    print(f"Cities with readable temperature files: {len([row for row in summary_rows if row['readable_temperature_files']])}")
    print(out_dir / "A6_era5_readable_temperature_window_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
