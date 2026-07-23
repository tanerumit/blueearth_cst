"""Milestone full-tree semantic diff for the R06 structural refactor (design §9).

Walks a `project_dir` output tree and compares every file against a reference
tree, dispatching by extension to per-type comparators. This is the *un-manifested
slice* gate: it covers wf2/wf3 staticmaps, `wflow_sbm.toml`, and change-factor
NetCDFs that `check_baseline.py`'s thin `TARGETS` list never fingerprints.

Design contract (dev/r06/structural-refactor-design.md §9, rows ext1-04 / ext2-01
/ ext2-02):

- `.nc`  : ELEMENT-WISE comparator (dims; coordinate labels+order with NO
           realignment; exact NaN masks; per-element `_within_tol`; non-volatile
           attrs) -- NOT the aggregate `fingerprint_nc`/`diff_nc` stats.
- `.toml`: parse-and-normalize compare (structural, key-order/comment-insensitive).
- `.yml`/`.yaml` under `{project_dir}/config/` : the copied-config
           NORMALIZE-THEN-COMPARE policy (ext2-01) -- parse both sides, apply only
           the documented old->new path map to the reference, require everything
           else deep-equal.
- `.csv`, `.png`, discharge `output.csv` : REUSED verbatim from `check_baseline.py`
           (imported, never modified).

`check_baseline.py` is imported and left unchanged (Hard-Constraints scope). The
CSV/PNG/discharge comparators and `VOLATILE_NC_ATTRS` come from it by import.

CLI (self-contained; no snakemake global)::

    python dev/scripts/semantic_tree_diff.py --ref <dir> --cur <dir> [--tolerance 1e-9]

Exit 0 = clean (every file equal under its comparator), 1 = at least one FAIL or
structural mismatch (missing/extra file). A clean self-comparison
(`--ref X --cur X`) is the commit-4 smoke.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import xarray as xr
import yaml

try:  # tomllib is stdlib >=3.11; the pixi env is 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore

# Reuse check_baseline.py comparators by import; NEVER edit that file.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_baseline as cb  # noqa: E402

VOLATILE_NC_ATTRS = cb.VOLATILE_NC_ATTRS

# ---------------------------------------------------------------------------
# Copied-config normalize map (ext2-01). The documented old->new path map that
# commit 2 rewrote INSIDE every orchestration config -- so the copied snapshot
# under {project_dir}/config/ legitimately differs from a pre-R6 recording only
# in exactly these path values. FOUR keys (data_sources_climate is included --
# the design's 3-key list predates the as-built inventory, which also rewrote
# data_sources_climate; see commit 2). Any OTHER difference is a real FAIL.
#
# Each entry: config-key -> {old-path-value: new-path-value, ...}. Only an
# exact OLD-value match is normalized; any other value is left untouched and
# will fail the equality step.
COPIED_CONFIG_PATH_MAP: dict[str, dict[str, str]] = {
    "data_sources": {
        "config/deltares_data.yml": "config/catalogs/deltares_data.yml",
        "config/deltares_data_linux.yml": "config/catalogs/deltares_data_linux.yml",
        "config/deltares_data_climate_projections.yml":
            "config/catalogs/deltares_data_climate_projections.yml",
        "config/deltares_data_climate_projections_linux.yml":
            "config/catalogs/deltares_data_climate_projections_linux.yml",
        "config/cmip6_data.yml": "config/catalogs/cmip6_data.yml",
    },
    "data_sources_climate": {
        "config/cmip6_data.yml": "config/catalogs/cmip6_data.yml",
    },
    "model_build_config": {
        "config/wflow_build_model.yml": "config/templates/wflow_build_model.yml",
    },
    "waterbodies_config": {
        "config/wflow_update_waterbodies.yml":
            "config/templates/wflow_update_waterbodies.yml",
    },
}

# Directories whose contents are compared as ABSENT (non-deterministic wall
# times / timestamps / snakemake metadata) -- never byte-diffed (design §9).
EXCLUDED_DIR_NAMES = frozenset({"logs", "benchmarks", ".snakemake"})

DEFAULT_TOLERANCE = 1e-9


# ---------------------------------------------------------------------------
# Element-wise numeric tolerance (ext2-02). Distinct from check_baseline's
# _within_tol, which returns False for tol<=0; here tol==0 means EXACT (plain
# ==), and tol>0 uses the same relative rule vectorized over arrays.
# ---------------------------------------------------------------------------

def _values_within_tol(ref: np.ndarray, cur: np.ndarray, tol: float) -> np.ndarray:
    """Element-wise boolean mask of |c-r| / max(|r|,|c|,1e-300) <= tol.

    Applied only to the finite (non-NaN) positions; NaN masks are checked
    separately by the caller. tol==0 -> exact equality.
    """
    if tol <= 0:
        return ref == cur
    denom = np.maximum.reduce([np.abs(ref), np.abs(cur), np.full(ref.shape, 1e-300)])
    return np.abs(cur - ref) / denom <= tol


def _compare_array(name: str, ref: np.ndarray, cur: np.ndarray, tol: float) -> list[str]:
    """Positional (NO realignment) element-wise compare of two arrays."""
    diffs: list[str] = []
    if ref.shape != cur.shape:
        return [f"{name}: shape {list(cur.shape)} vs {list(ref.shape)}"]
    if ref.dtype != cur.dtype:
        diffs.append(f"{name}: dtype {cur.dtype} vs {ref.dtype}")
    if np.issubdtype(ref.dtype, np.floating) and np.issubdtype(cur.dtype, np.floating):
        ref_nan = np.isnan(ref)
        cur_nan = np.isnan(cur)
        if not np.array_equal(ref_nan, cur_nan):
            pos = np.argwhere(ref_nan != cur_nan)
            first = tuple(int(i) for i in pos[0]) if pos.size else ()
            return diffs + [f"{name}: NaN mask mismatch at {first}"]
        finite = ~ref_nan
        if finite.any():
            ok = _values_within_tol(ref[finite], cur[finite], tol)
            if not ok.all():
                # locate the first offending finite element in flat order
                finite_idx = np.argwhere(finite)
                bad = finite_idx[np.argmin(ok)]
                p = tuple(int(i) for i in bad)
                diffs.append(
                    f"{name}: value out of tolerance at {p} "
                    f"({cur[tuple(bad)]} vs {ref[tuple(bad)]})"
                )
    else:
        # non-float (int / datetime / string coords) -> exact positional equality
        if not np.array_equal(ref, cur):
            pos = np.argwhere(ref != cur)
            first = tuple(int(i) for i in pos[0]) if pos.size else ()
            diffs.append(f"{name}: value mismatch at {first}")
    return diffs


def compare_nc(ref_path: str, cur_path: str, tol: float = DEFAULT_TOLERANCE) -> list[str]:
    """ELEMENT-WISE NetCDF comparator (design §9 ext2-02).

    Dims (names+sizes), coordinate variables (labels AND stored order, no
    realignment), data variables (shape/dtype, exact NaN masks, per-element
    tolerance), and non-volatile attrs. Summary/aggregate stats are NOT an
    equality criterion here.
    """
    diffs: list[str] = []
    with xr.open_dataset(ref_path) as ref, xr.open_dataset(cur_path) as cur:
        # Dimensions
        if dict(ref.sizes) != dict(cur.sizes):
            diffs.append(f"dims {dict(cur.sizes)} vs {dict(ref.sizes)}")
        # Coordinates: identical sets, compared labels+order (no sort/realign)
        if set(ref.coords) != set(cur.coords):
            diffs.append(
                f"coord set {sorted(cur.coords)} vs {sorted(ref.coords)}"
            )
        else:
            for name in sorted(ref.coords):
                diffs += _compare_array(
                    f"coord {name}",
                    np.asarray(ref.coords[name].values),
                    np.asarray(cur.coords[name].values),
                    tol,
                )
        # Data variables: identical sets, element-wise values
        if set(ref.data_vars) != set(cur.data_vars):
            diffs.append(
                f"variable set {sorted(cur.data_vars)} vs {sorted(ref.data_vars)}"
            )
        else:
            for name in sorted(ref.data_vars):
                diffs += _compare_array(
                    f"var {name}",
                    np.asarray(ref[name].values),
                    np.asarray(cur[name].values),
                    tol,
                )
                diffs += _compare_attrs(
                    f"var {name}", ref[name].attrs, cur[name].attrs
                )
        # Dataset-level attrs
        diffs += _compare_attrs("dataset", ref.attrs, cur.attrs)
    return diffs


def _compare_attrs(scope: str, ref_attrs: dict, cur_attrs: dict) -> list[str]:
    ref_a = {k: str(v) for k, v in ref_attrs.items() if k not in VOLATILE_NC_ATTRS}
    cur_a = {k: str(v) for k, v in cur_attrs.items() if k not in VOLATILE_NC_ATTRS}
    if ref_a != cur_a:
        return [f"{scope} attrs {cur_a} vs {ref_a}"]
    return []


# ---------------------------------------------------------------------------
# TOML: parse-and-normalize structural compare.
# ---------------------------------------------------------------------------

def compare_toml(ref_path: str, cur_path: str) -> list[str]:
    with open(ref_path, "rb") as f:
        ref = tomllib.load(f)
    with open(cur_path, "rb") as f:
        cur = tomllib.load(f)
    if ref != cur:
        return _dict_diff(ref, cur, prefix="")
    return []


def _dict_diff(ref, cur, prefix: str) -> list[str]:
    """First-difference reporter for two parsed structures (dicts/lists/scalars)."""
    if isinstance(ref, dict) and isinstance(cur, dict):
        diffs: list[str] = []
        for k in sorted(set(ref) | set(cur)):
            p = f"{prefix}.{k}" if prefix else str(k)
            if k not in ref:
                diffs.append(f"{p}: new in current")
            elif k not in cur:
                diffs.append(f"{p}: missing in current")
            elif ref[k] != cur[k]:
                diffs += _dict_diff(ref[k], cur[k], p)
        return diffs
    return [f"{prefix or '<root>'}: {cur!r} vs {ref!r}"]


# ---------------------------------------------------------------------------
# Copied-config YAML: normalize-then-compare (ext2-01).
# ---------------------------------------------------------------------------

def _normalize_config_paths(doc):
    """Apply COPIED_CONFIG_PATH_MAP to a parsed config, in place, recursively.

    Only rewrites a key's value when it equals a documented OLD path exactly.
    Any other value is left untouched (and will fail the equality step). Applied
    at any nesting depth so a mapped key inside `project:`/`workflows:` is caught.
    """
    if isinstance(doc, dict):
        for k, v in doc.items():
            if k in COPIED_CONFIG_PATH_MAP and isinstance(v, str):
                doc[k] = COPIED_CONFIG_PATH_MAP[k].get(v, v)
            else:
                _normalize_config_paths(v)
    elif isinstance(doc, list):
        for item in doc:
            _normalize_config_paths(item)
    return doc


def compare_copied_config(ref_path: str, cur_path: str) -> list[str]:
    """Normalize-then-compare for a copied config snapshot (ext2-01).

    Parse both; apply the documented old->new path map to the REFERENCE
    (pre-R6) side; require deep structural equality. Any residual difference --
    an unmapped path, a changed non-path value, a missing/extra key -- FAILs.
    """
    ref = yaml.safe_load(Path(ref_path).read_text())
    cur = yaml.safe_load(Path(cur_path).read_text())
    # Reflexivity guard: identical inputs have no difference by definition. The
    # normalize step is DIRECTIONAL (ref = pre-R6 OLD paths -> NEW), which is not
    # reflexive -- normalizing one side of two identical OLD-path docs would
    # falsely mismatch. This guard makes a self-compare clean without loosening
    # the directional policy for real pre/post comparisons.
    if ref == cur:
        return []
    ref = _normalize_config_paths(ref)
    if ref != cur:
        return _dict_diff(ref, cur, prefix="")
    return []


# ---------------------------------------------------------------------------
# Reused check_baseline.py comparators (imported, unchanged).
# ---------------------------------------------------------------------------

def compare_csv(ref_path: str, cur_path: str) -> list[str]:
    return cb.diff_hashed(cb.fingerprint_csv(ref_path), cb.fingerprint_csv(cur_path))


def compare_png(ref_path: str, cur_path: str) -> list[str]:
    return cb.diff_png(cb.fingerprint_png(ref_path), cb.fingerprint_png(cur_path))


def compare_discharge_csv(ref_path: str, cur_path: str) -> list[str]:
    ref_t, ref_q, _ = cb.read_discharge_series(ref_path)
    cur_t, cur_q, _ = cb.read_discharge_series(cur_path)
    report = cb.compare_discharge(ref_t, ref_q, cur_t, cur_q)
    return [] if report.get("ok") else cb._discharge_report_lines(report)


def compare_hashed(ref_path: str, cur_path: str) -> list[str]:
    """Fallback for unrecognized extensions: normalized-hash (CRLF-stripped) compare."""
    return cb.diff_hashed(cb.fingerprint_csv(ref_path), cb.fingerprint_csv(cur_path))


# ---------------------------------------------------------------------------
# Walker + dispatch.
# ---------------------------------------------------------------------------

def _is_excluded(rel: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in rel.parts)


def _is_copied_config(rel: Path) -> bool:
    """A copied-config snapshot: a YAML directly under a `config/` dir in the tree."""
    return rel.suffix in (".yml", ".yaml") and "config" in rel.parts


def dispatch(rel: Path, ref_path: str, cur_path: str, tol: float) -> list[str]:
    suffix = rel.suffix.lower()
    name = rel.name
    if suffix == ".nc":
        return compare_nc(ref_path, cur_path, tol)
    if suffix == ".toml":
        return compare_toml(ref_path, cur_path)
    if suffix in (".yml", ".yaml") and _is_copied_config(rel):
        return compare_copied_config(ref_path, cur_path)
    if suffix == ".png":
        return compare_png(ref_path, cur_path)
    if suffix == ".csv":
        if name == "output.csv" and "run_default" in rel.parts:
            return compare_discharge_csv(ref_path, cur_path)
        return compare_csv(ref_path, cur_path)
    return compare_hashed(ref_path, cur_path)


def _list_files(root: Path) -> set[Path]:
    out: set[Path] = set()
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root)
            if not _is_excluded(rel):
                out.add(rel)
    return out


def diff_trees(ref_root: str, cur_root: str, tol: float = DEFAULT_TOLERANCE) -> dict:
    """Compare two output trees file-by-file. Returns a report dict with
    `failures` (list of (relpath, [reasons])), `missing`, `extra`, `passed`."""
    ref = Path(ref_root)
    cur = Path(cur_root)
    ref_files = _list_files(ref)
    cur_files = _list_files(cur)

    missing = sorted(str(p) for p in ref_files - cur_files)
    extra = sorted(str(p) for p in cur_files - ref_files)
    failures: list[tuple[str, list[str]]] = []

    for rel in sorted(ref_files & cur_files):
        reasons = dispatch(rel, str(ref / rel), str(cur / rel), tol)
        if reasons:
            failures.append((str(rel), reasons))

    passed = not (missing or extra or failures)
    return {
        "passed": passed,
        "missing": missing,
        "extra": extra,
        "failures": failures,
        "n_compared": len(ref_files & cur_files),
    }


def format_report(report: dict) -> str:
    lines: list[str] = []
    for path in report["missing"]:
        lines.append(f"MISSING (in ref, not cur): {path}")
    for path in report["extra"]:
        lines.append(f"EXTRA (in cur, not ref): {path}")
    for path, reasons in report["failures"]:
        lines.append(f"FAIL {path}")
        for r in reasons:
            lines.append(f"    - {r}")
    status = "CLEAN" if report["passed"] else "MISMATCH"
    lines.append(
        f"{status}: {report['n_compared']} files compared, "
        f"{len(report['failures'])} failed, {len(report['missing'])} missing, "
        f"{len(report['extra'])} extra"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", required=True, help="reference (pre-R6) project_dir tree")
    ap.add_argument("--cur", required=True, help="current (post-R6) project_dir tree")
    ap.add_argument(
        "--tolerance", type=float, default=DEFAULT_TOLERANCE,
        help="relative tolerance for element-wise numeric compare (0 = exact)",
    )
    args = ap.parse_args(argv)
    report = diff_trees(args.ref, args.cur, args.tolerance)
    print(format_report(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
