"""Enabled-aware wrapper over the three CST Snakefiles (design §7).

Reads a full-orchestration `--configfile` YAML, checks each
`workflows.<name>.enabled` flag, and invokes `snakemake -s Snakefile_<name>
--configfile <cfg> ...` for exactly the enabled workflows, in the fixed order
model_creation -> climate_projections -> climate_experiment.

This is the evolution of the run_snake_test.cmd / run_snake_docker.sh runners --
a *runner over* the three Snakefiles, NOT a fourth Snakemake entry point. The
Snakefiles do not read `enabled:`; the flag governs this wrapper only.

Contract (pinned, design §7 (a)-(g)):

 (a) Full-orchestration configs only: a `workflows:` section with all three
     subsections each carrying an `enabled:` key. The single-workflow
     projections configs (no `workflows:` section) are direct `snakemake -s`
     inputs, not wrapper inputs.
 (b) A missing `workflows:` section or a missing `<name>.enabled` subkey is a
     HARD ERROR (nonzero exit, message naming the absent key) -- never a silent
     default to true.
 (c) Each `enabled:` value must PARSE to a real boolean (isinstance(v, bool) on
     the post-yaml.safe_load value). YAML 1.1 resolves unquoted
     true/false/yes/no/on/off to booleans, so all those spellings are accepted;
     quoted strings ("true"), integers (1/0), or any non-bool are REJECTED.
 (d) Enabled workflows run in fixed order; on the first nonzero snakemake exit
     the wrapper STOPS and returns that exit code (does not continue).
 (e) --cores N (default 3) is forwarded to every invocation; args after a `--`
     sentinel are appended verbatim to every invocation. --configfile is
     supplied by the wrapper.
 (f) Per-workflow flags are preserved from a hardcoded map matching the runners:
     --keep-going on climate_projections only.

Disabling a workflow neither deletes its prior outputs nor guarantees downstream
freshness: the wrapper invokes each Snakefile independently with no
prerequisite-freshness check -- identical to invoking a single Snakefile
directly today. A user who disables a prerequisite owns the staleness of what
downstream consumes.

Usage::

    python scripts/run_workflows.py --config config/workflows/snake_config_model_test.yml
    python scripts/run_workflows.py --config <cfg> --cores 4 -- --dry-run
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import yaml

# Fixed run order (model -> projections -> experiment). Each maps to its
# Snakefile and the per-workflow flags preserved verbatim from the runners
# (design §7(f)): --keep-going on climate_projections only.
WORKFLOW_ORDER = ("model_creation", "climate_projections", "climate_experiment")

SNAKEFILE = {
    "model_creation": "Snakefile_model_creation",
    "climate_projections": "Snakefile_climate_projections",
    "climate_experiment": "Snakefile_climate_experiment",
}

PER_WORKFLOW_FLAGS = {
    "model_creation": [],
    "climate_projections": ["--keep-going"],
    "climate_experiment": [],
}

# Repo root = parent of scripts/. Snakefiles and config paths are repo-root
# relative and the wrapper is invoked from repo root, mirroring the runners.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigError(Exception):
    """Raised for a config that violates the wrapper's contract (a)-(c)."""


def read_enabled_flags(config_path: str) -> dict[str, bool]:
    """Parse and validate the per-workflow enabled flags (contract (a)-(c)).

    Raises ConfigError on: no `workflows:` section, a missing `<name>` or
    `<name>.enabled` key, or an `enabled:` value that does not parse to a bool.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict) or "workflows" not in cfg:
        raise ConfigError(
            f"{config_path}: no 'workflows:' section -- this is not a full "
            f"orchestration config. The single-workflow projections configs are "
            f"direct 'snakemake -s' inputs, not wrapper inputs."
        )
    workflows = cfg["workflows"]
    if not isinstance(workflows, dict):
        raise ConfigError(f"{config_path}: 'workflows:' is not a mapping")

    flags: dict[str, bool] = {}
    for name in WORKFLOW_ORDER:
        if name not in workflows or not isinstance(workflows[name], dict):
            raise ConfigError(
                f"{config_path}: missing 'workflows.{name}' section "
                f"(required for a full orchestration config)"
            )
        section = workflows[name]
        if "enabled" not in section:
            raise ConfigError(
                f"{config_path}: missing 'workflows.{name}.enabled' key"
            )
        value = section["enabled"]
        if not isinstance(value, bool):
            raise ConfigError(
                f"{config_path}: 'workflows.{name}.enabled' must parse to a "
                f"boolean (got {value!r} of type {type(value).__name__}); use an "
                f"unquoted true/false (yes/no/on/off also accepted), not a "
                f"quoted string or integer"
            )
        flags[name] = value
    return flags


def build_command(
    name: str, config_path: str, cores: int, extra: list[str]
) -> list[str]:
    """Assemble the snakemake argv for one workflow (contract (e)/(f))."""
    return [
        "snakemake",
        "all",
        "-c", str(cores),
        "-s", SNAKEFILE[name],
        "--configfile", config_path,
        *PER_WORKFLOW_FLAGS[name],
        *extra,
    ]


def run(config_path: str, cores: int, extra: list[str]) -> int:
    """Invoke each enabled workflow in fixed order; stop on first nonzero exit
    and return that code (contract (d)). Returns 0 if all enabled workflows
    succeed (or all are disabled)."""
    flags = read_enabled_flags(config_path)
    for name in WORKFLOW_ORDER:
        if not flags[name]:
            print(f"[run_workflows] skipping {name} (enabled: false)")
            continue
        cmd = build_command(name, config_path, cores, extra)
        print(f"[run_workflows] {name}: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        if result.returncode != 0:
            print(
                f"[run_workflows] {name} exited {result.returncode}; stopping "
                f"(later workflows not invoked)."
            )
            return result.returncode
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run the enabled CST workflows in fixed order.",
    )
    ap.add_argument(
        "--config", required=True,
        help="path to a full-orchestration snake config (config/workflows/...)",
    )
    ap.add_argument(
        "--cores", type=int, default=3,
        help="cores forwarded to every snakemake invocation (default: 3)",
    )
    ap.add_argument(
        "extra", nargs=argparse.REMAINDER,
        help="args after `--` are appended verbatim to every invocation",
    )
    args = ap.parse_args(argv)

    # argparse.REMAINDER captures the leading `--` sentinel; strip it.
    extra = args.extra
    if extra and extra[0] == "--":
        extra = extra[1:]

    try:
        return run(args.config, args.cores, extra)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
