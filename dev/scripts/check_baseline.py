"""Record / check fingerprints for the M1 replication baseline.

Walks the formal `rule all` targets across the three Snakefiles and writes
a JSON manifest under dev/baseline/. Fingerprint format follows the
roadmap and the pipeline-regression-testing skill: per-variable summary
stats for netCDF, normalized SHA256 for CSV/YAML, size-only for PNG.

Usage:
    python dev/scripts/check_baseline.py record
    python dev/scripts/check_baseline.py check
    python dev/scripts/check_baseline.py {record,check} --project-dir examples/test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from math import floor, log10
from pathlib import Path

import numpy as np

# Force netCDF4 to load before xarray's lazy backend triggers it. On
# Windows under pixi, xarray's deferred `import netCDF4` inside its
# backend fails with a DLL load error, but a direct top-level import
# succeeds and primes the loader so subsequent imports work.
import netCDF4  # noqa: F401

import xarray as xr
import yaml

PROJECT_DIR_DEFAULT = "examples/test_local"
CLIM_PROJECT = "cmip6"
EXPERIMENT_NAME = "experiment"

MANIFEST_PATH_DEFAULT = Path("dev/baseline/manifest.json")
MANIFEST_VERSION = 1
SIG_FIGS = 10
PNG_TOLERANCE_FRAC = 0.10

# Volatile attrs stripped before fingerprinting netCDF files.
VOLATILE_NC_ATTRS = frozenset({
    "history", "creation_date", "Conventions",
    "software", "software_version",
    "production_date", "creation_time",
    "date_created", "date_modified",
})

# (kind, path-template). Templates are resolved against project_dir.
# Mirrors `rule all` across Snakefile_model_creation,
# Snakefile_climate_projections, Snakefile_climate_experiment.
TARGETS: list[tuple[str, str]] = [
    # Snakefile_model_creation
    ("png",  "{project_dir}/plots/wflow_model_performance/hydro_wflow_1.png"),
    ("png",  "{project_dir}/plots/wflow_model_performance/basin_area.png"),
    ("png",  "{project_dir}/plots/wflow_model_performance/precip.png"),
    ("yaml", "{project_dir}/config/snake_config_model_creation.yml"),
    # Snakefile_climate_projections
    ("nc",   "{clim_project_dir}/annual_change_scalar_stats_summary.nc"),
    ("csv",  "{clim_project_dir}/annual_change_scalar_stats_summary.csv"),
    ("csv",  "{clim_project_dir}/annual_change_scalar_stats_summary_mean.csv"),
    ("png",  "{clim_project_dir}/plots/projected_climate_statistics.png"),
    ("png",  "{clim_project_dir}/plots/precipitation_anomaly_projections_abs.png"),
    ("png",  "{clim_project_dir}/plots/temperature_anomaly_projections_abs.png"),
    ("yaml", "{project_dir}/config/snake_config_climate_projections.yml"),
    # Snakefile_climate_experiment
    ("csv",  "{exp_dir}/model_results/Qstats.csv"),
    ("csv",  "{exp_dir}/model_results/basin.csv"),
    ("yaml", "{project_dir}/config/snake_config_climate_experiment.yml"),
]


def resolve(template: str, project_dir: str) -> str:
    return template.format(
        project_dir=project_dir,
        clim_project_dir=f"{project_dir}/climate_projections/{CLIM_PROJECT}",
        exp_dir=f"{project_dir}/climate_{EXPERIMENT_NAME}",
    )


def round_sig(x: float | None, n: int = SIG_FIGS) -> float | None:
    if x is None:
        return None
    x = float(x)
    if not np.isfinite(x):
        return None
    if x == 0.0:
        return 0.0
    return round(x, n - 1 - int(floor(log10(abs(x)))))


def fingerprint_nc(path: str) -> dict:
    with xr.open_dataset(path) as ds:
        per_var: dict[str, dict] = {}
        for name in sorted(ds.variables):
            arr = ds[name]
            values = np.asarray(arr.values)
            entry: dict = {
                "shape": list(arr.shape),
                "dtype": str(arr.dtype),
            }
            if np.issubdtype(values.dtype, np.number):
                finite = values[np.isfinite(values)]
                entry["count_non_nan"] = int(finite.size)
                if finite.size > 0:
                    entry["min"] = round_sig(float(finite.min()))
                    entry["max"] = round_sig(float(finite.max()))
                    entry["mean"] = round_sig(float(finite.mean()))
                    entry["std"] = round_sig(float(finite.std()))
                else:
                    entry["min"] = entry["max"] = entry["mean"] = entry["std"] = None
            else:
                entry["count_non_nan"] = int(values.size)
                entry["min"] = entry["max"] = entry["mean"] = entry["std"] = None
            attrs = {k: str(v) for k, v in arr.attrs.items() if k not in VOLATILE_NC_ATTRS}
            entry["attrs"] = dict(sorted(attrs.items()))
            per_var[name] = entry
    js = json.dumps(per_var, sort_keys=True, ensure_ascii=False)
    return {
        "type": "netcdf",
        "summary_sha256": hashlib.sha256(js.encode("utf-8")).hexdigest(),
        "summary": per_var,
    }


def fingerprint_csv(path: str) -> dict:
    raw = Path(path).read_bytes()
    text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    norm = b"\n".join(line.rstrip() for line in text.split(b"\n"))
    return {
        "type": "csv",
        "sha256": hashlib.sha256(norm).hexdigest(),
        "size_bytes": len(raw),
    }


def fingerprint_png(path: str) -> dict:
    return {
        "type": "png",
        "exists": True,
        "size_bytes": Path(path).stat().st_size,
    }


def fingerprint_yaml(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    js = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    return {
        "type": "yaml",
        "sha256": hashlib.sha256(js.encode("utf-8")).hexdigest(),
    }


FINGERPRINTERS = {
    "png": fingerprint_png,
    "nc": fingerprint_nc,
    "csv": fingerprint_csv,
    "yaml": fingerprint_yaml,
}


def compute_manifest(project_dir: str) -> tuple[dict, list[str]]:
    out: dict[str, dict] = {}
    missing: list[str] = []
    for kind, template in TARGETS:
        path = resolve(template, project_dir)
        if not Path(path).exists():
            missing.append(path)
            continue
        out[path] = FINGERPRINTERS[kind](path)
    return out, missing


def diff_png(rec: dict, cur: dict) -> list[str]:
    if not cur.get("exists"):
        return ["missing"]
    rec_size, cur_size = rec["size_bytes"], cur["size_bytes"]
    if rec_size == 0:
        return [] if cur_size == 0 else [f"size {cur_size}, expected 0"]
    rel = abs(cur_size - rec_size) / rec_size
    if rel > PNG_TOLERANCE_FRAC:
        return [f"size {cur_size} vs {rec_size} ({rel:.1%} drift > {PNG_TOLERANCE_FRAC:.0%})"]
    return []


NUMERIC_STATS = ("min", "max", "mean", "std")


def _within_tol(r: float | None, c: float | None, tol: float) -> bool:
    if r is None or c is None or tol <= 0:
        return False
    denom = max(abs(r), abs(c), 1e-300)
    return abs(c - r) / denom <= tol


def diff_nc(rec: dict, cur: dict, tolerance: float = 0.0) -> list[str]:
    diffs: list[str] = []
    rec_summary = rec.get("summary", {})
    cur_summary = cur.get("summary", {})
    for var in sorted(set(rec_summary) | set(cur_summary)):
        if var not in rec_summary:
            diffs.append(f"variable {var}: new in current run")
            continue
        if var not in cur_summary:
            diffs.append(f"variable {var}: missing in current run")
            continue
        for stat in ("shape", "dtype", "count_non_nan", "min", "max", "mean", "std", "attrs"):
            r, c = rec_summary[var].get(stat), cur_summary[var].get(stat)
            if r == c:
                continue
            if stat in NUMERIC_STATS and _within_tol(r, c, tolerance):
                continue
            diffs.append(f"variable {var} {stat}: {c} vs {r}")
    return diffs


def diff_hashed(rec: dict, cur: dict) -> list[str]:
    if rec.get("sha256") != cur.get("sha256"):
        return [f"sha256 {cur.get('sha256')} vs {rec.get('sha256')}"]
    return []


def diff_records(rec: dict, cur: dict, tolerance: float = 0.0) -> list[str]:
    if rec["type"] == "png":
        return diff_png(rec, cur)
    if rec["type"] == "netcdf":
        return diff_nc(rec, cur, tolerance)
    return diff_hashed(rec, cur)


def cmd_record(args: argparse.Namespace) -> int:
    manifest, missing = compute_manifest(args.project_dir)
    if missing:
        sys.stderr.write("Missing targets — refusing to record an incomplete manifest:\n")
        for p in missing:
            sys.stderr.write(f"  - {p}\n")
        return 1
    payload = {
        "version": MANIFEST_VERSION,
        "project_dir": args.project_dir,
        "targets": manifest,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Recorded {len(manifest)} target(s) → {args.manifest}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    if not args.manifest.exists():
        sys.stderr.write(f"Manifest not found: {args.manifest}\n")
        sys.stderr.write("Run `check_baseline.py record` first.\n")
        return 2
    recorded = json.loads(args.manifest.read_text())
    rec_targets = recorded["targets"]
    current, missing = compute_manifest(args.project_dir)

    failures: list[tuple[str, list[str]]] = []
    for p in missing:
        if p in rec_targets:
            failures.append((p, ["target missing on disk"]))
    for path, rec in rec_targets.items():
        if path not in current:
            continue
        diffs = diff_records(rec, current[path], args.tolerance)
        if diffs:
            failures.append((path, diffs))
    for path in sorted(set(current) - set(rec_targets)):
        failures.append((path, ["target present but not in manifest"]))

    tol_note = f" (tolerance {args.tolerance:g})" if args.tolerance > 0 else ""
    if not failures:
        print(f"OK — {len(rec_targets)} target(s) match manifest{tol_note}.")
        return 0
    print(f"FAIL — {len(failures)} target(s) differ from manifest{tol_note}:")
    for path, diffs in failures:
        print(f"  {path}")
        for d in diffs:
            print(f"    - {d}")
    return 1


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-dir", default=PROJECT_DIR_DEFAULT,
                        help=f"Project directory (default: {PROJECT_DIR_DEFAULT})")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH_DEFAULT,
                        help=f"Manifest path (default: {MANIFEST_PATH_DEFAULT})")


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    _add_common(sub.add_parser("record", help="Record fingerprints to manifest"))
    check_p = sub.add_parser("check", help="Check current outputs against manifest")
    _add_common(check_p)
    check_p.add_argument("--tolerance", type=float, default=0.0,
                         help="Relative tolerance for netCDF numeric stats "
                              "(default 0 = exact). Use 1e-9 for cross-env comparison.")
    args = p.parse_args()
    sys.exit(cmd_record(args) if args.cmd == "record" else cmd_check(args))


if __name__ == "__main__":
    main()
