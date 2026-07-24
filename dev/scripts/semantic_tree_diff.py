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

`check_baseline.py` is imported for its comparators; its own P3-1 edits (the
TARGETS repoint, G1 scope amendment) live in that file, not here. The
CSV/PNG/discharge comparators and `VOLATILE_NC_ATTRS` come from it by import.

P3-1 layer (dev/p31/experiment-structure-design.md §6a, commit 5):

- **Path map** -- an ORDERED list of directory-prefix rewrite rules on
  project-root-relative paths (NOT a per-file table; the prefix form also covers
  in-toml pointer targets that are `temp()`-deleted and exist in neither tree).
  Ref (old-layout) relpaths are translated old->new before pairing with the
  current tree, so a pure move is content-diffed instead of degrading to a
  MISSING+EXTRA pair.
- **Allowlist gate contract (risk-4)** -- after translation and content-diffing
  of translated pairs, the residual MISSING and EXTRA sets must be EMPTY modulo
  an explicitly enumerated allowlist (each entry justified in
  dev/p31/migration_experiment-structure.md). A nonempty unexplained
  MISSING/EXTRA is a gate FAILURE, not a pass.
- **Path-aware toml comparator (§6a step 3, ext1-3)** -- for each path-valued
  toml field: (1) lexical resolve against its own toml's dir (normpath+join,
  never `.resolve()`); (2) translate to project-root-relative by stripping that
  side's root; (3) apply the prefix map to the REF side's target; (4) compare --
  equal => the pointer move is behavior-neutral (PASS), different => a real
  failure naming the field (a mis-repoint is caught, not hidden).

CLI (self-contained; no snakemake global)::

    python dev/scripts/semantic_tree_diff.py --ref <dir> --cur <dir> [--tolerance 1e-9]
        [--experiment-name experiment] [--dataset-key era5_20000101_20201231]
        [--no-path-map] [--allow <relpath> ...]

Exit 0 = clean (every file equal under its comparator, residual MISSING/EXTRA
empty modulo the allowlist), 1 = at least one FAIL or unexplained
missing/extra file. A clean self-comparison (`--ref X --cur X`) is the smoke.
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
# P3-1 path map (design §6a step 2, ext1-3). An ORDERED list of rewrite rules
# on project-root-relative POSIX paths. Two rule kinds:
#   - directory-prefix rule: old ends with "/" -- rewrites any path under it
#     (load-bearing for temp() targets that exist in NEITHER tree, e.g. the
#     per-realization forcing inmaps consumed by path_forcing);
#   - exact-file rule: old does not end with "/" -- rewrites that one relpath.
# First match wins. Direction is OLD (pre-P3-1 reference) -> NEW (current).
# ---------------------------------------------------------------------------

def build_p31_path_map(
    experiment_name: str, dataset_key: str | None
) -> list[tuple[str, str]]:
    """The P3-1 old->new relocation rules for one experiment (design §6a).

    Covers the five content-bearing relocation classes: results CSVs + the
    experiment subtree (rule 3), the wf3 config snapshot (rule 1), the run-dir
    tomls/output CSVs (rule 2), and the keyed extraction netCDF (rule 4,
    only when the dataset key is known).
    """
    rules: list[tuple[str, str]] = [
        (
            "config/snake_config_climate_experiment.yml",
            f"experiments/{experiment_name}/config/snake_config_climate_experiment.yml",
        ),
        (
            f"hydrology_model/run_climate_{experiment_name}/",
            f"experiments/{experiment_name}/model_runs/",
        ),
        (
            f"climate_{experiment_name}/",
            f"experiments/{experiment_name}/",
        ),
    ]
    if dataset_key:
        rules.append(
            ("climate_historical/raw_data/", f"climate_historical/{dataset_key}/")
        )
    return rules


def build_p31_allowlist(
    experiment_name: str, dataset_key: str | None
) -> list[str]:
    """EXTRA-by-design current-tree relpaths (risk-4 presence exemptions ONLY).

    Justifications live in dev/p31/migration_experiment-structure.md: the
    per-experiment guard sentinel and the key-level guard artifact are new
    gate outputs with no pre-P3-1 counterpart; neither carries scientific
    content. There is no wf3 plots producer, so nothing is MISSING-by-design.
    """
    allow = [f"experiments/{experiment_name}/.project_consistency_ok"]
    if dataset_key:
        allow.append(f"climate_historical/{dataset_key}/.guard_ok")
    return allow


def apply_path_map(rel: str, path_map: list[tuple[str, str]] | None) -> str:
    """Translate one project-root-relative path through the ordered rule list."""
    rel = rel.replace("\\", "/")
    if not path_map:
        return rel
    for old, new in path_map:
        if old.endswith("/"):
            if rel.startswith(old):
                return new + rel[len(old):]
        elif rel == old:
            return new
    return rel


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
# TOML: parse-and-normalize structural compare, with the P3-1 path-aware
# pointer-field comparator (design §6a step 3, ext1-3).
# ---------------------------------------------------------------------------

# Path-valued run-toml fields resolved relative to the toml's own directory.
# The three fields the design names as legitimately changing string value are
# path_static / path_forcing / path_input; path_output and csv.path are
# included for the same treatment (their targets moved WITH the run dir, so
# raw strings are unchanged and the normalized compare is equally a PASS).
TOML_PATH_FIELDS: tuple[tuple[str, ...], ...] = (
    ("input", "path_forcing"),
    ("input", "path_static"),
    ("state", "path_input"),
    ("state", "path_output"),
    ("csv", "path"),
)


def _get_nested(doc: dict, keys: tuple[str, ...]):
    node = doc
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node


def _set_nested(doc: dict, keys: tuple[str, ...], value) -> None:
    node = doc
    for k in keys[:-1]:
        node = node[k]
    node[keys[-1]] = value


def _project_relative_target(toml_path: str, field_val: str, root: str) -> str:
    """§6a step 3 (1)+(2): lexical resolve against the toml's own dir, then
    strip that side's project root. Pure string arithmetic (normpath+join, NOT
    `.resolve()`), so it works after `temp()` targets are deleted."""
    v = field_val.replace("\\", "/")
    if os.path.isabs(v):
        resolved = os.path.normpath(v)
    else:
        toml_dir = os.path.dirname(os.path.abspath(toml_path))
        resolved = os.path.normpath(os.path.join(toml_dir, v))
    rel = os.path.relpath(resolved, os.path.abspath(root))
    return rel.replace("\\", "/")


def compare_toml(
    ref_path: str,
    cur_path: str,
    ref_root: str | None = None,
    cur_root: str | None = None,
    path_map: list[tuple[str, str]] | None = None,
) -> list[str]:
    """Structural toml compare. When both project roots are given, the known
    path-valued fields are compared in a PROJECT-ROOT-RELATIVE namespace with
    the old->new path map applied to the ref side (§6a step 3): equal mapped
    targets => behavior-neutral pointer move (PASS); different => a real
    failure naming the field. Without roots: raw parsed-dict equality."""
    with open(ref_path, "rb") as f:
        ref = tomllib.load(f)
    with open(cur_path, "rb") as f:
        cur = tomllib.load(f)

    diffs: list[str] = []
    if ref_root is not None and cur_root is not None:
        for field in TOML_PATH_FIELDS:
            rv = _get_nested(ref, field)
            cv = _get_nested(cur, field)
            if not (isinstance(rv, str) and isinstance(cv, str)):
                continue  # absent on a side -> handled by the raw dict diff
            ref_target = _project_relative_target(ref_path, rv, ref_root)
            cur_target = _project_relative_target(cur_path, cv, cur_root)
            mapped_ref = apply_path_map(ref_target, path_map)  # step 3
            dotted = ".".join(field)
            if mapped_ref != cur_target:  # step 4
                diffs.append(
                    f"{dotted}: project-relative target {cur_target!r} vs ref "
                    f"{ref_target!r} (mapped -> {mapped_ref!r}) -- mis-repoint"
                )
            # Neutralize the field for the raw compare either way: an unequal
            # target is already reported above; an equal one is a PASS.
            _set_nested(ref, field, "<path-field-compared>")
            _set_nested(cur, field, "<path-field-compared>")

    if ref != cur:
        diffs += _dict_diff(ref, cur, prefix="")
    return diffs


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
# P3-1 commit-5b layer: cross-root path normalization for YAML string leaves.
#
# The milestone diff compares trees generated under DIFFERENT project roots,
# and several wf3-written YAMLs legitimately embed that root inside string
# values: the config snapshots record `project.project_dir` (the root itself),
# the weathergen configs carry root-prefixed output paths, and the experiment
# data catalog carries absolute `uri`s. Under a cross-root comparison every
# such leaf differs by construction -- the same behavior-neutral pointer-move
# class ext1-3 solved for the run tomls, in YAML. Parse-level adjudication of
# the 2026-07-23 milestone diff confirmed ALL leaf diffs in these files are
# path-only (dev/p31/baseline_diffs.md). Mechanism mirroring the toml
# comparator: each side's own root token becomes `<PROJECT_ROOT>` and the ref
# side's project-relative remainder goes through the old->new path map; equal
# normalized docs => behavior-neutral move (PASS); any non-path leaf diff
# still FAILs.
# ---------------------------------------------------------------------------

def _root_token_variants(root: str) -> list[str]:
    """Forward-slash string forms under which a tree's own project root can
    appear inside a written value: as given, and absolute. Longest first so
    the absolute form wins when both would match."""
    p = Path(root)
    forms = {p.as_posix()}
    try:
        forms.add(p.resolve().as_posix())
    except OSError:
        pass
    return sorted(forms, key=len, reverse=True)


def _normalize_path_leaf(
    val: str, variants: list[str], path_map: list[tuple[str, str]] | None
) -> str:
    """Rewrite a string leaf that IS or is PREFIXED BY this side's project
    root; every other leaf is returned untouched (and fails the equality step
    if it diverges). Prefix-or-equality only -- no mid-string rewriting."""
    s = val.replace("\\", "/")
    for v in variants:
        if s == v:
            return "<PROJECT_ROOT>"
        if s.startswith(v + "/"):
            rest = s[len(v) + 1:]
            return "<PROJECT_ROOT>/" + apply_path_map(rest, path_map)
    return val


def _normalize_tree_root_paths(doc, variants, path_map):
    if isinstance(doc, dict):
        return {
            k: _normalize_tree_root_paths(v, variants, path_map)
            for k, v in doc.items()
        }
    if isinstance(doc, list):
        return [_normalize_tree_root_paths(v, variants, path_map) for v in doc]
    if isinstance(doc, str):
        return _normalize_path_leaf(doc, variants, path_map)
    return doc


def compare_yaml(
    ref_path: str,
    cur_path: str,
    rel: Path,
    ref_root: str | None = None,
    cur_root: str | None = None,
    path_map: list[tuple[str, str]] | None = None,
) -> list[str]:
    """Structural YAML compare: reflexivity guard, then the R6 directional
    copied-config normalization (config-dir snapshots only), then -- when both
    project roots are known -- the cross-root path-leaf normalization above.
    The path map is applied to the REF side only (old->new direction)."""
    ref = yaml.safe_load(Path(ref_path).read_text())
    cur = yaml.safe_load(Path(cur_path).read_text())
    if ref == cur:
        return []
    if _is_copied_config(rel):
        ref = _normalize_config_paths(ref)
        if ref == cur:
            return []
    if ref_root is not None and cur_root is not None:
        ref = _normalize_tree_root_paths(ref, _root_token_variants(ref_root), path_map)
        cur = _normalize_tree_root_paths(cur, _root_token_variants(cur_root), None)
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
    if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
        return True
    # Run-log FILES outside the excluded logs/ dirs (hydromt.log, the Wflow
    # run-dir log.txt, run_default/log.txt): same non-content-bearing class as
    # the excluded dirs -- timestamp-laden by nature, never value-comparable.
    return rel.suffix.lower() == ".log" or rel.name == "log.txt"


def _is_copied_config(rel: Path) -> bool:
    """A copied-config snapshot: a YAML directly under a `config/` dir in the tree."""
    return rel.suffix in (".yml", ".yaml") and "config" in rel.parts


def dispatch(
    rel: Path,
    ref_path: str,
    cur_path: str,
    tol: float,
    ref_root: str | None = None,
    cur_root: str | None = None,
    path_map: list[tuple[str, str]] | None = None,
) -> list[str]:
    suffix = rel.suffix.lower()
    name = rel.name
    if suffix == ".nc":
        return compare_nc(ref_path, cur_path, tol)
    if suffix == ".toml":
        return compare_toml(ref_path, cur_path, ref_root, cur_root, path_map)
    if suffix in (".yml", ".yaml"):
        return compare_yaml(ref_path, cur_path, rel, ref_root, cur_root, path_map)
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


def diff_trees(
    ref_root: str,
    cur_root: str,
    tol: float = DEFAULT_TOLERANCE,
    path_map: list[tuple[str, str]] | None = None,
    allowlist: list[str] | None = None,
) -> dict:
    """Compare two output trees file-by-file. Returns a report dict with
    `failures` (list of (relpath, [reasons])), `missing`, `extra`, `allowed`,
    `passed`.

    P3-1 semantics (§6a): every ref relpath is translated through `path_map`
    (old->new) before pairing with the current tree, so a mapped move is
    content-diffed (ref bytes vs cur bytes) rather than reported as
    MISSING+EXTRA. Residual MISSING/EXTRA entries matching `allowlist` are
    reported separately as `allowed` and do not fail the gate; any other
    residual entry FAILS it (risk-4)."""
    ref = Path(ref_root)
    cur = Path(cur_root)
    ref_files = _list_files(ref)
    cur_files = _list_files(cur)

    # Translate ref relpaths old->new (POSIX keys); keep the original for I/O.
    translated: dict[str, Path] = {}
    for p in ref_files:
        key = apply_path_map(p.as_posix(), path_map)
        if key in translated:  # two ref files mapping onto one target
            raise ValueError(
                f"path map collision: {translated[key]} and {p} both map to {key}"
            )
        translated[key] = p
    cur_keys = {p.as_posix(): p for p in cur_files}

    allow = set(allowlist or [])
    raw_missing = sorted(set(translated) - set(cur_keys))
    raw_extra = sorted(set(cur_keys) - set(translated))
    allowed = sorted(
        [f"MISSING allowed: {k}" for k in raw_missing if k in allow]
        + [f"EXTRA allowed: {k}" for k in raw_extra if k in allow]
    )
    missing = [
        (k if translated[k].as_posix() == k
         else f"{translated[k].as_posix()} (expected at {k})")
        for k in raw_missing if k not in allow
    ]
    extra = [k for k in raw_extra if k not in allow]
    failures: list[tuple[str, list[str]]] = []

    for key in sorted(set(translated) & set(cur_keys)):
        rel_ref = translated[key]
        rel_cur = cur_keys[key]
        reasons = dispatch(
            rel_cur, str(ref / rel_ref), str(cur / rel_cur), tol,
            ref_root=ref_root, cur_root=cur_root, path_map=path_map,
        )
        if reasons:
            label = (key if rel_ref.as_posix() == key
                     else f"{rel_ref.as_posix()} -> {key}")
            failures.append((label, reasons))

    passed = not (missing or extra or failures)
    return {
        "passed": passed,
        "missing": missing,
        "extra": extra,
        "allowed": allowed,
        "failures": failures,
        "n_compared": len(set(translated) & set(cur_keys)),
    }


def format_report(report: dict) -> str:
    lines: list[str] = []
    for path in report["missing"]:
        lines.append(f"MISSING (in ref, not cur): {path}")
    for path in report["extra"]:
        lines.append(f"EXTRA (in cur, not ref): {path}")
    for entry in report.get("allowed", []):
        lines.append(f"ALLOWED ({entry})")
    for path, reasons in report["failures"]:
        lines.append(f"FAIL {path}")
        for r in reasons:
            lines.append(f"    - {r}")
    status = "CLEAN" if report["passed"] else "MISMATCH"
    lines.append(
        f"{status}: {report['n_compared']} files compared, "
        f"{len(report['failures'])} failed, {len(report['missing'])} missing, "
        f"{len(report['extra'])} extra, "
        f"{len(report.get('allowed', []))} allowlisted"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", required=True, help="reference (pre-move) project_dir tree")
    ap.add_argument("--cur", required=True, help="current (post-move) project_dir tree")
    ap.add_argument(
        "--tolerance", type=float, default=DEFAULT_TOLERANCE,
        help="relative tolerance for element-wise numeric compare (0 = exact)",
    )
    ap.add_argument(
        "--experiment-name", default="experiment",
        help="experiment_name for the P3-1 path map (default: experiment)",
    )
    ap.add_argument(
        "--dataset-key", default=None,
        help="historical-store dataset key, e.g. era5_20000101_20201231 "
             "(enables the climate_historical/raw_data/ -> <key>/ rule and the "
             ".guard_ok allowlist entry)",
    )
    ap.add_argument(
        "--no-path-map", action="store_true",
        help="disable the P3-1 path map + built-in allowlist (identical-relpath "
             "keying only, the pre-P3-1 behavior)",
    )
    ap.add_argument(
        "--allow", action="append", default=[],
        help="extra allowlisted MISSING/EXTRA relpath (repeatable; every entry "
             "must be justified in the migration note)",
    )
    args = ap.parse_args(argv)
    if args.no_path_map:
        path_map, allowlist = None, list(args.allow)
    else:
        path_map = build_p31_path_map(args.experiment_name, args.dataset_key)
        allowlist = build_p31_allowlist(args.experiment_name, args.dataset_key)
        allowlist += list(args.allow)
    report = diff_trees(args.ref, args.cur, args.tolerance,
                        path_map=path_map, allowlist=allowlist)
    print(format_report(report))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
