"""Compose a tiered project config (T1 + per-workflow T2) into today's shape.

R13 splits the monolithic project config into a **T1** project file carrying
closed ``{enabled, config_path}`` workflow stanzas plus **T2** files holding one
workflow's settings each. This module is the loader that puts them back
together, and the enforcement point for the rules that keep them apart.

Source of record: ``dev/milestones/r13/config-tiers-design.md`` (ACCEPTED
2026-08-21). Section references below are to that document; every ``D-`` tag is
one of its decisions.

**The composition invariant (D-8.1) is the whole point.** ``compose_config``
returns a mapping whose shape is identical to the pre-split ``config`` dict:
``config["workflows"]["run_stress_test"]``, ``config["shared"]["basin"]`` and
``config["reporting"]`` resolve exactly as they did, to exactly the same values.
Because that holds, ``effective_config_digest``, ``guarded_sections_digest``, the
experiment freeze, ``resolve_simulation_window`` and every ``get_config`` call
site are unchanged *by construction* — same inputs, same bytes hashed. Two
deviations are declared and only two: the narrowing (§8.1, §10.7) and the
rebinding requirement (D-8.6).

**The shared seam (§9).** A key read by more than one workflow lives in T1, never
in a T2 file. Convention cannot enforce that, and a full key registry would be a
second source of truth that drifts, so the rule is carried by four closed
parse-time checks — D-9.1 (the T1 stanza is closed), D-9.2 (a T2 file may not
declare a T1-owned or foreign-hoisted name), D-9.3 (the same rejection, widened
to every declared T2 file that resolves), D-9.5 (T1's top level is closed) —
plus the static read scan (D-9.6) that governs the one case parse time cannot
see: a value read reaching *across* the section boundary at runtime.

**Design invariants this module obeys (do not relax without a design change):**

1. **Pure.** ``compose_config`` takes an already-parsed mapping plus a path and
   does no I/O beyond reading the T2 files it is told to read. No global state.
   That is what makes it callable outside Snakemake, which the raw-T1 tool
   consumers depend on (D-12.0, §12.0).
2. **Composition moves keys between files; it never creates or drops one.**
   ``effective_config_document`` digests the config *mapping*, so a key that is
   present rather than absent moves ``effective_config_digest`` even when the
   resolved value is identical. Adding one during composition would refuse every
   already-run experiment in the project through ``_frozen_differences``'
   key-union diff. Hence D-8.7: an omitted ``config_path`` composes to ``{}``
   and adds nothing.
3. **``enabled`` is merged back in; ``config_path`` is not** (D-10.1). Dropping
   ``enabled`` would refuse every already-run experiment; adding ``config_path``
   would make run identity depend on where a project stores its files.
4. **Fail loud at parse time.** Every refusal is a ``ValueError`` raised while
   the Snakefile body executes, before the DAG is built, so
   ``pytest tests/test_cli.py`` is their gate. Messages name the resolved
   absolute path, the anchor it was resolved against, and the migration doc.

Stdlib + pyyaml only — no new dependency.
"""

from __future__ import annotations

import os
import re
import tokenize
from collections.abc import Iterable, Mapping, Sequence
from io import StringIO
from pathlib import Path
from typing import Any, NamedTuple

import yaml

# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

#: The user-facing migration guide, named by every refusal this module raises.
MIGRATION_DOC = "docs/migration-config-tiers.md"

#: T1's top level, closed (D-9.5). Closing it is what makes the migration
#: detector complete: a config whose only unmigrated element is a top-level
#: `reporting:` produces no extra key under any `workflows.<name>`, so the
#: stanza check alone would see nothing and the project would run with an
#: undefined precedence between two records of the same section.
T1_TOP_LEVEL: tuple[str, ...] = ("project", "shared", "workflows")

#: The closed `workflows.<name>` stanza (D-9.1). `enabled` is T1-owned;
#: `config_path` is OPTIONAL (D-8.7) and, when present, must resolve.
#: This closure does three jobs at once: it is half the seam enforcement, it is
#: the migration detector (§15.2), and it is what stops a T1 file quietly
#: growing back into today's monolith.
WORKFLOW_STANZA_KEYS: frozenset[str] = frozenset({"enabled", "config_path"})

#: The four workflows, in the fixed pipeline order `scripts/run_workflows.py`
#: drives. Used to attribute a scanned config access to a workflow (D-9.6);
#: composition itself never restates this list — it reads what T1 declares.
WORKFLOW_NAMES: tuple[str, ...] = (
    "analyze_climate",
    "build_model",
    "analyze_projections",
    "run_stress_test",
)

#: Names that belong to `shared:` whether or not the current T1 declares them.
#: Deriving the rejection set from T1 alone has a hole: a T1 omitting the
#: optional `shared.seed` would not reject a `seed:` planted in a T2 file, which
#: is the exact failure the seam rule is written against.
#:
#: COUPLED EDIT: adding a key to `shared:` means adding it here in the same
#: commit — the discipline `_ADVANCED_SETTINGS_SCHEMA` already imposes.
SHARED_SEAM_KEYS: frozenset[str] = frozenset(
    {
        "basin",
        "historical_window",
        "clim_historical",
        "seed",
        "water_year_start",
        "julia_threads",
    }
)

#: Sections that live at the top level of ONE workflow's T2 file and are hoisted
#: back to the composed document's top level (D-10.4). A closed two-entry map,
#: not a general mechanism.
#:
#: `reporting:` is read in exactly one place (`run_stress_test.smk` ->
#: `surface_axes.parse_surfaces`), so the seam rule does not force it into T1.
#: Hoisting rather than nesting is what keeps it OUTSIDE
#: `workflows.run_stress_test` and therefore outside `CONFIG_PROJECTION`, the
#: effective-config digest and the experiment freeze — a deliberate exclusion
#: that lets a caption be corrected without re-running the experiment. Nesting
#: would silently revoke it and turn every caption edit into a frozen-experiment
#: refusal.
HOISTED_SECTIONS: dict[str, tuple[str, ...]] = {"run_stress_test": ("reporting",)}

#: Every sanctioned cross-workflow VALUE read: (reader, owner, key).
#: SHRINK-ONLY: an entry leaves this set by hoisting the key to T1 (S4);
#: nothing is ever added. A new multiply-read key goes to `shared:`.
#: EMPTIED AND RETIRED inside R13 by the hoist phase (D-9.7, commit 8) --
#: from then on the D-9.6 scan asserts zero value reads, with no registry.
CROSS_WORKFLOW_READS: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("run_stress_test", "build_model", "wflow_outvars"),
    }
)

#: Declared IDENTITY comparisons (D-9.6 class 2): whole sections read to be
#: COMPARED against the owning workflow's snapshot, never consumed as settings.
#: These are not S4 value-sharing — the drift guard's entire job is to REFUSE a
#: run when another workflow's section changed under an already-built model, so
#: an edit to the WF1 T2 file is caught loudly at rule 3.01. That is the
#: opposite of the silent coupling the seam rule exists to prevent.
#:
#: (file, section) pairs, enumerated APART from the value reads above so that
#: retiring `CROSS_WORKFLOW_READS` cannot silently absorb one.
IDENTITY_COMPARISONS: frozenset[tuple[str, str]] = frozenset(
    {
        ("run_stress_test.smk", "build_model"),
        ("run_stress_test.smk", "analyze_projections"),
    }
)

#: Declared OWNERLESS reads (D-9.6 class 3): tools and wrappers that own no
#: workflow section and read one anyway. Sanctioned because each composes or
#: reads T1 stanza level for its own purpose rather than consuming another
#: workflow's settings. Section `"*"` means the access reaches the `workflows`
#: mapping without naming a workflow literally (the wrapper's enable-flag loop).
OWNERLESS_SECTION_READS: frozenset[tuple[str, str]] = frozenset(
    {
        ("scripts/run_workflows.py", "*"),
        ("scripts/suggest_experiment_name.py", "run_stress_test"),
        ("scripts/plot_workflow_dag.py", "run_stress_test"),
    }
)


# ---------------------------------------------------------------------------
# Path resolution (D-8.4)
# ---------------------------------------------------------------------------


def _resolve_config_path(raw: object, t1_dir: str, name: str) -> str:
    """Return the absolute path a stanza's ``config_path`` names.

    ``config_path`` is ``expanduser``-ed and, when still relative, resolved
    against **the directory containing T1** — not the CWD, which is how every
    other path key in the same file resolves.

    That asymmetry is deliberate (D-8.4, a reversal of the design's first
    revision). Every other path key references an EXTERNAL input — a data
    catalog, a basin CSV, an output root — whose natural anchor is the
    invocation. ``config_path`` is the only key that references *a fragment of
    the config document itself*: a file the same author wrote at the same time
    and moves as one unit with T1. Anchoring a document's own fragments at the
    document is what makes a project's config set relocatable, which a single
    file got for free. Under CWD resolution the splitter could emit no value
    that both resolves and matches the design's own examples, for the population
    the migration exists to serve — a production ``project_dir`` outside the
    repository tree.
    """
    if not isinstance(raw, (str, os.PathLike)):
        raise ValueError(
            f"workflows.{name}.config_path must be a path string, got "
            f"{type(raw).__name__}. See {MIGRATION_DOC}."
        )
    text = os.path.expanduser(os.fspath(raw))
    if not text.strip():
        raise ValueError(
            f"workflows.{name}.config_path is empty. Omit the key entirely to "
            f"give the workflow no settings. See {MIGRATION_DOC}."
        )
    if not os.path.isabs(text):
        text = os.path.join(t1_dir, text)
    return os.path.normpath(os.path.abspath(text))


def _declared_form(resolved_abs: str) -> str:
    """Return the form of ``resolved_abs`` a Snakemake rule input can carry.

    CWD-relative when one is computable, absolute otherwise. The values of
    ``workflow_config_paths`` become declared rule inputs (D-10.3), so they must
    be resolvable by Snakemake from the working directory.

    On Windows ``os.path.relpath`` RAISES ``ValueError`` across drives, so the
    fallback is a caught exception rather than an assumption that a relative
    form exists. A project on ``D:`` driven from a checkout on ``C:`` is an
    ordinary case here.
    """
    try:
        return os.path.relpath(resolved_abs, os.getcwd())
    except ValueError:
        return resolved_abs


# ---------------------------------------------------------------------------
# Seam checks (D-9.1, D-9.2, D-9.3, D-9.5)
# ---------------------------------------------------------------------------


def _check_t1_top_level(t1: Mapping[str, Any]) -> None:
    """Refuse a T1 top-level key outside ``{project, shared, workflows}`` (D-9.5).

    This is what turns the hoist-collision question into a non-question: a
    leftover top-level ``reporting:`` is a parse error naming the key, so there
    is no precedence rule to define between it and the hoisted one.
    """
    stray = [key for key in t1 if key not in T1_TOP_LEVEL]
    if stray:
        raise ValueError(
            f"T1 project config declares top-level key(s) {sorted(stray)!r}. "
            f"The project file's top level is closed to {list(T1_TOP_LEVEL)!r}: "
            "workflow settings belong in that workflow's own config file, and "
            "`reporting:` belongs at the top level of the run_stress_test file. "
            f"Run `python scripts/split_project_config.py` and see {MIGRATION_DOC}."
        )


def _check_stanza_closed(name: str, stanza: Mapping[str, Any]) -> None:
    """Refuse a ``workflows.<name>`` key outside ``{enabled, config_path}`` (D-9.1).

    Validated for **every stanza present in T1**, whichever workflow it names —
    not only for the workflows this entry point loads. Scoping the closure to
    the loaded set would make a half-split config legal: a project that split
    `build_model` and left the other three inline would run WF1 clean.

    Absence of a whole stanza is **not this check's business**. A popped stanza
    is absent, not malformed, which is what keeps the additive-carve regression
    (`tests/test_cli.py`) green.
    """
    stray = [key for key in stanza if key not in WORKFLOW_STANZA_KEYS]
    if stray:
        raise ValueError(
            f"workflows.{name} declares key(s) {sorted(stray)!r}, but a project "
            f"config's workflow stanza is closed to {sorted(WORKFLOW_STANZA_KEYS)!r}. "
            f"Move those settings into a workflow config file named "
            f"`<project_config_stem>_{name}.yml` beside this file and point "
            f"`workflows.{name}.config_path` at it. Run "
            f"`python scripts/split_project_config.py <this file>` to do it "
            f"mechanically, and see {MIGRATION_DOC}."
        )


def _rejected_in_t2(name: str, t1_shared: Mapping[str, Any]) -> frozenset[str]:
    """Return the names a T2 file for ``name`` may not declare (D-9.2).

    T1-owned sections, every key T1's own `shared:` declares, the frozen
    `SHARED_SEAM_KEYS`, and every hoisted section EXCEPT the ones this workflow
    owns. Deriving the last term from the hoist map rather than a hand-kept list
    is what closes the unguarded direction: a `reporting:` block written at the
    top of `build_model`'s T2 file would otherwise be accepted and merged into
    `workflows.build_model`, which is a guarded section — so a caption edit in
    the wrong file would enter `guarded_sections_digest` and produce a "your
    model was built under different settings" refusal from rule 3.01.
    """
    hoisted_elsewhere = {
        section
        for owner, sections in HOISTED_SECTIONS.items()
        for section in sections
        if owner != name
    }
    return frozenset(
        {"project", "shared", "workflows", "enabled"}
        | set(t1_shared)
        | set(SHARED_SEAM_KEYS)
        | hoisted_elsewhere
    )


def _check_t2_names(
    name: str, body: Mapping[str, Any], path: str, t1_shared: Mapping[str, Any]
) -> None:
    """Refuse a globally-owned name at the top level of a T2 file (D-9.2/D-9.3).

    Reads **key names only** and merges nothing, so the narrowing holds even
    when this runs over a file outside the composed set.
    """
    rejected = _rejected_in_t2(name, t1_shared)
    stray = sorted(key for key in body if key in rejected)
    if not stray:
        return
    hoisted_owners = {
        section: owner
        for owner, sections in HOISTED_SECTIONS.items()
        for section in sections
    }
    fixes = []
    for key in stray:
        if key in hoisted_owners:
            fixes.append(
                f"{key!r} belongs at the top level of the "
                f"{hoisted_owners[key]!r} workflow's config file"
            )
        else:
            fixes.append(f"{key!r} belongs in the project file's `shared:` section")
    raise ValueError(
        f"{path}: the {name!r} workflow config declares {stray!r} at its top "
        "level, but those names are owned outside a single workflow — a key "
        "read by more than one workflow lives in the project file, never in a "
        "workflow file. " + "; ".join(fixes) + f". See {MIGRATION_DOC}."
    )


# ---------------------------------------------------------------------------
# Composition (D-8.5)
# ---------------------------------------------------------------------------


class _Probe(NamedTuple):
    """One declared T2 file, resolved and read once."""

    name: str
    declared: str  # the raw `config_path` value, for messages
    resolved: str  # absolute
    status: str  # "ok" | "missing" | "unparseable" | "not_mapping"
    body: dict[str, Any]
    detail: str


def _probe_t2(name: str, raw: object, t1_dir: str) -> _Probe:
    """Resolve and read one declared T2 file without deciding whether to fail.

    Separating the read from the verdict is what lets the D-9.3 tolerance clause
    exist: the same file is a hard error inside ``R(entry)`` and a logged skip
    outside it, and both need the parse attempt.
    """
    resolved = _resolve_config_path(raw, t1_dir, name)
    if not os.path.isfile(resolved):
        return _Probe(name, os.fspath(raw), resolved, "missing", {}, "")
    try:
        loaded = yaml.safe_load(Path(resolved).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return _Probe(name, os.fspath(raw), resolved, "unparseable", {}, str(exc))
    if loaded is None:
        # An empty file is a workflow with no settings, same as an omitted key.
        return _Probe(name, os.fspath(raw), resolved, "ok", {}, "")
    if not isinstance(loaded, Mapping):
        return _Probe(
            name,
            os.fspath(raw),
            resolved,
            "not_mapping",
            {},
            type(loaded).__name__,
        )
    return _Probe(name, os.fspath(raw), resolved, "ok", dict(loaded), "")


def _raise_for_probe(probe: _Probe, t1_dir: str) -> None:
    """Apply §8.4's failure table to a file this entry point must load."""
    if probe.status == "missing":
        raise ValueError(
            f"workflows.{probe.name}.config_path names a file that does not "
            f"exist: {probe.resolved}\n"
            f"  declared as: {probe.declared!r}\n"
            f"  resolved against: {t1_dir}\n"
            "A relative `config_path` is anchored at the project config file's "
            "own directory, not the working directory. To give this workflow no "
            f"settings at all, delete the `config_path` key. See {MIGRATION_DOC}."
        )
    if probe.status == "unparseable":
        raise ValueError(
            f"workflows.{probe.name}.config_path names a file that is not valid "
            f"YAML: {probe.resolved}\n"
            f"  resolved against: {t1_dir}\n"
            f"  parser said: {probe.detail}"
        )
    if probe.status == "not_mapping":
        raise ValueError(
            f"workflows.{probe.name}.config_path names a file that parses to "
            f"{probe.detail}, not a mapping of settings: {probe.resolved}\n"
            f"  resolved against: {t1_dir}\n"
            "A workflow config file's top level is that workflow's own settings "
            f"at column zero. See {MIGRATION_DOC}."
        )


def _check_no_duplicate_paths(probes: Sequence[_Probe]) -> None:
    """Refuse one T2 file shared by two stanzas of one T1 (§8.4).

    Two workflows sharing one settings file would silently give each the other's
    keys, and the seam rule would have nothing to test against.

    Compared on ``normcase(abspath(...))`` rather than the raw string: a raw
    comparison is evaded by ``./x.yml`` versus ``x.yml``, a trailing separator,
    or a case-only difference on Windows, and no name-level check can substitute
    because with one file on disk there is only one file to compare. Same
    comparison key, and the same reason, as ``copy_config_files``' destination
    collision check. ``resolve()`` is deliberately not used, matching that
    precedent: it follows symlinks, and two deliberate symlinks to one file are
    a user's choice rather than a typo.
    """
    seen: dict[str, str] = {}
    for probe in probes:
        key = os.path.normcase(probe.resolved)
        if key in seen:
            raise ValueError(
                f"workflows.{seen[key]}.config_path and "
                f"workflows.{probe.name}.config_path resolve to the same file: "
                f"{probe.resolved}\n"
                "One workflow config file per workflow — sharing one would give "
                "each workflow the other's settings with nothing to detect it."
            )
        seen[key] = probe.name


def compose_config(
    t1: Mapping[str, Any],
    t1_path: str | os.PathLike,
    entry: str | None = None,
    declared_sections: Sequence[str] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Merge T1 and its T2 files into a config of today's shape.

    Parameters
    ----------
    t1 : Mapping
        The parsed ``--configfile`` mapping, **after** Snakemake has merged any
        ``--config key=value`` overrides into it. Overrides therefore apply to
        T1 and are validated like any other T1 content (D-8.6b).
    t1_path : str or PathLike
        ``workflow.configfiles[0]``. The resolution anchor for every relative
        ``config_path`` (D-8.4).
    entry : str, optional
        The entry point's own workflow key. ``None`` selects the tool-facing
        scope — see ``load_composed_config``.
    declared_sections : Sequence[str], optional
        This Snakefile's ``CONFIG_PROJECTION`` tuple, passed in rather than
        restated here. ``R(entry)`` is derived from it:
        ``{entry} | {s.split(".")[1] for s in declared_sections if s.startswith("workflows.")}``.
        For WF3 that yields ``{run_stress_test, build_model, analyze_projections}``
        because WF3's ``CONFIG_PROJECTION`` is itself derived from
        ``guarded_sections`` — so the loader is one more consumer of the same
        maintained literal rather than a second copy of it.

    Returns
    -------
    (composed_config, workflow_config_paths)
        ``workflow_config_paths`` maps each **loaded** workflow to its resolved
        path, in the form a Snakemake rule input can carry. It is an explicit
        part of the contract: §10.3 declares those paths as rule inputs, §10.5
        registers them in ``CONFIG_REFERENCES``, and §11 hands them to the
        snapshot writer.

    Raises
    ------
    ValueError
        On any seam violation or unresolvable ``config_path``. Every message
        names the resolved absolute path, the anchor, and the migration doc.

    Notes
    -----
    **The caller must bind the result to the Snakefile-global name** ``config``,
    or update the existing mapping in place (D-8.6a). Any other binding is a
    defect: ``check_project_consistency`` takes its live config from
    ``sm.config`` — Snakemake's ``workflow.config`` — not from the Snakefile's
    local name, so a ``composed = compose_config(...)`` refactor would leave the
    drift guard comparing ``{enabled, config_path}`` against the snapshot's full
    section and fail every WF3 run at rule 3.01, after WF1 and WF2 had already
    run, with a message blaming project drift rather than the binding.
    """
    if not isinstance(t1, Mapping):
        raise ValueError(
            f"{t1_path}: the project config must parse to a mapping, got "
            f"{type(t1).__name__}."
        )
    _check_t1_top_level(t1)

    t1_dir = os.path.dirname(os.path.abspath(os.fspath(t1_path))) or os.getcwd()
    shared = t1.get("shared") or {}
    if not isinstance(shared, Mapping):
        raise ValueError(f"{t1_path}: `shared:` must be a mapping if present.")

    workflows = t1.get("workflows") or {}
    if not isinstance(workflows, Mapping):
        raise ValueError(f"{t1_path}: `workflows:` must be a mapping if present.")

    # D-9.1 over EVERY stanza present, then resolve every declared path once.
    probes: list[_Probe] = []
    for name, stanza in workflows.items():
        if not isinstance(stanza, Mapping):
            raise ValueError(
                f"{t1_path}: workflows.{name} must be a mapping carrying "
                f"{sorted(WORKFLOW_STANZA_KEYS)!r}, got {type(stanza).__name__}."
            )
        _check_stanza_closed(name, stanza)
        if "config_path" in stanza:
            probes.append(_probe_t2(name, stanza["config_path"], t1_dir))
    _check_no_duplicate_paths(probes)
    by_name = {probe.name: probe for probe in probes}

    # R(entry). With no entry point, scope is "whatever section a tool indexes":
    # every workflow whose stanza declares a config_path that actually loaded.
    if entry is None:
        loaded_names = {probe.name for probe in probes if probe.status == "ok"}
    else:
        loaded_names = {entry} | {
            section.split(".", 1)[1]
            for section in (declared_sections or ())
            if section.startswith("workflows.")
        }

    # §8.4's failure table applies only inside R(entry). Outside it the D-9.3
    # tolerance clause holds: a workflow's own file must not be able to fail
    # another workflow's parse, which is the inverse of this milestone's goal.
    skipped: list[str] = []
    for probe in probes:
        if probe.status == "ok":
            continue
        if probe.name in loaded_names:
            _raise_for_probe(probe, t1_dir)
        else:
            skipped.append(f"{probe.name} ({probe.status}: {probe.resolved})")

    # D-9.2/D-9.3: the same rejection set, over every T2 file that resolved —
    # inside R(entry) or not. Three of the four entry points have a singleton
    # R(entry), so a check confined to it could never see a shared name planted
    # in another workflow's file.
    for probe in probes:
        if probe.status == "ok":
            _check_t2_names(probe.name, probe.body, probe.resolved, shared)

    composed: dict[str, Any] = {
        key: value for key, value in t1.items() if key != "workflows"
    }
    merged: dict[str, Any] = {}
    workflow_config_paths: dict[str, str] = {}
    for name, stanza in workflows.items():
        section = {key: value for key, value in stanza.items() if key != "config_path"}
        if name in loaded_names:
            probe = by_name.get(name)
            body = dict(probe.body) if probe is not None else {}
            for hoisted in HOISTED_SECTIONS.get(name, ()):
                if hoisted in body:
                    composed[hoisted] = body.pop(hoisted)
            section.update(body)
            if probe is not None:
                workflow_config_paths[name] = _declared_form(probe.resolved)
        merged[name] = section
    composed["workflows"] = merged

    if skipped:
        print(
            "[config_composition] skipped unreadable workflow config(s) outside "
            f"this entry point's scope: {', '.join(skipped)}"
        )
    return composed, workflow_config_paths


def load_composed_config(
    t1_path: str | os.PathLike,
    entry: str | None = None,
    declared_sections: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Parse T1 from disk and return the composed config. Tools pass ``entry=None``.

    The tool-facing entry point (D-12.0). Because ``compose_config`` is a pure
    function of a parsed mapping plus a path, every raw-T1 consumer — the
    ``tree-check`` snapshot tool, the cache pruners, the DAG renderer, the
    conftest fixture — becomes a two-line change: import this and call it
    instead of ``yaml.safe_load``.

    With ``entry=None`` the loaded set is every workflow whose stanza declares a
    ``config_path`` that resolves and parses, which is the right scope for a
    caller that is not an entry point; the D-9.3 tolerance clause then means a
    broken WF3 file does not break a ``tree-check``.
    """
    text = Path(os.fspath(t1_path)).read_text(encoding="utf-8")
    t1 = yaml.safe_load(text) or {}
    composed, _ = compose_config(t1, t1_path, entry, declared_sections)
    return composed


# ---------------------------------------------------------------------------
# The cross-workflow read scan (D-9.6)
# ---------------------------------------------------------------------------

#: Which workflow each entry point owns.
_SNAKEFILE_OWNER: dict[str, str] = {f"{name}.smk": name for name in WORKFLOW_NAMES}

#: Which workflow each package stage owns. `shared/`, `spatial/` and
#: `weathergen/` own no section: they are called from more than one workflow, so
#: any `workflows.<name>` access there is ownerless by construction.
_STAGE_OWNER: dict[str, str] = {
    "climate_analysis": "analyze_climate",
    "model": "build_model",
    "projections": "analyze_projections",
    "experiment": "run_stress_test",
}

_NAMES_ALT = "|".join(WORKFLOW_NAMES)

#: An access that REACHES the `workflows` mapping: `["workflows"]` indexing or a
#: `.get("workflows"` chain.
_WORKFLOWS_ACCESS = re.compile(
    r"""(?: \[ \s* ["']workflows["'] \s* \] | \.get\( \s* ["']workflows["'] )""",
    re.VERBOSE,
)

#: The workflow name that follows such an access, allowing for the `or {}` and
#: default-argument noise real chains carry between the two steps.
_SECTION_AFTER = re.compile(
    rf"""^ [\s\S]{{0,60}}? (?: \[ \s* ["'](?P<a>{_NAMES_ALT})["'] \s* \]
                            | \.get\( \s* ["'](?P<b>{_NAMES_ALT})["'] )""",
    re.VERBOSE,
)

#: A settings key read straight off the section: `section["key"]` / `.get("key"`.
_KEY_AFTER = re.compile(
    r"""^ \s* (?: \[ \s* ["'](?P<a>\w+)["'] \s* \]
                                    | \.get\( \s* ["'](?P<b>\w+)["'] )""",
    re.VERBOSE,
)

#: The house accessor. When the chain is its first argument the key is its
#: second, past the intervening `or {}` / default-argument noise. The trailing
#: `\w*` absorbs the mapping the chain starts from (`get_config(config.get(...`).
_GET_CONFIG_BEFORE = re.compile(r"get_config\(\s*\w*$")
#: Applied ONLY when the chain is `get_config`'s first argument, where the next
#: quoted word is the key by that function's signature. Unanchored because the
#: chain's own `.get(section, {})` default and an `or {}` fallback sit between.
_GET_CONFIG_KEY = re.compile(r"""["'](?P<k>\w+)["']""")
_GET_CONFIG_WINDOW = 120

#: The projection / guard spelling: a string whose ENTIRE content is
#: `workflows.<name>`. Anchoring on both quotes is what separates a section
#: projection from a message: `"workflows.build_model.simulation_window must be
#: a mapping"` and `f"workflows.run_stress_test.{key} must be >= 1"` carry a
#: further dotted segment, so neither matches, while `guarded_sections`'
#: `"workflows.build_model"` does.
_PROJECTION_LITERAL = re.compile(rf"""["']workflows\.(?P<n>{_NAMES_ALT})["']""")


class ScanHit(NamedTuple):
    """One config-section access found on a scanned surface.

    ``reader`` is the workflow the file belongs to, or ``None`` when the file
    owns no section. ``key`` is the settings key read straight off the section,
    or ``None`` when the whole section is taken.
    """

    file: str
    line: int
    reader: str | None
    section: str
    key: str | None


#: Token types that can precede a docstring — i.e. that mean the STRING token
#: starting here opens a statement rather than continuing an expression.
_PROSE_OPENERS = frozenset(
    {tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}
)


def _blank(lines: list[str], start: tuple[int, int], end: tuple[int, int]) -> None:
    """Overwrite a token's span with spaces, preserving every offset."""
    (row_start, col_start), (row_end, col_end) = start, end
    for row in range(row_start, row_end + 1):
        line = lines[row - 1]
        first = col_start if row == row_start else 0
        last = col_end if row == row_end else len(line.rstrip("\n"))
        lines[row - 1] = line[:first] + " " * (last - first) + line[last:]


def _strip_prose(source: str) -> str:
    """Return ``source`` with comments and docstrings blanked, offsets preserved.

    Tokenizing rather than regexing is what keeps a commented-out example from
    reading as a live access — and docstrings need the identical treatment for
    the identical reason. ``provenance.project_config``'s docstring quotes the
    projection tuple verbatim (``"workflows.build_model"``) to explain what a
    projection is; that is prose about a read, not a read, and a scan that could
    not tell them apart would force a prose sentence into a contract
    enumeration.

    A docstring is identified structurally: a STRING token that opens a
    statement and is immediately followed by a line end, i.e. a bare string
    expression. Such a token is never a read.

    Line and column offsets are preserved so a hit still reports the line a
    human would open. A file that will not tokenize — which no surface here is —
    is returned unchanged rather than dropped, so the scan can never go quiet by
    failing to read something.
    """
    try:
        tokens = list(tokenize.generate_tokens(StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return source
    lines = source.splitlines(keepends=True)
    for token in tokens:
        if token.type == tokenize.COMMENT:
            _blank(lines, token.start, token.end)
    code = [token for token in tokens if token.type != tokenize.COMMENT]
    for index, token in enumerate(code):
        if token.type != tokenize.STRING:
            continue
        previous = code[index - 1].type if index else tokenize.ENCODING
        following = code[index + 1].type if index + 1 < len(code) else tokenize.NEWLINE
        if previous in _PROSE_OPENERS and following in (
            tokenize.NEWLINE,
            tokenize.NL,
            tokenize.ENDMARKER,
        ):
            _blank(lines, token.start, token.end)
    return "".join(lines)


def _owner_of(rel: str) -> str | None:
    """Return the workflow a scanned file owns, or ``None``."""
    parts = Path(rel).parts
    if len(parts) == 1:
        return _SNAKEFILE_OWNER.get(parts[0])
    if parts[0] == "blueearth_cst" and len(parts) > 2:
        return _STAGE_OWNER.get(parts[1])
    return None


def _scan_text(rel: str, source: str) -> list[ScanHit]:
    """Return every config-section access in one file."""
    owner = _owner_of(rel)
    text = _strip_prose(source)
    hits: list[ScanHit] = []

    def line_of(offset: int) -> int:
        return text.count("\n", 0, offset) + 1

    for match in _WORKFLOWS_ACCESS.finditer(text):
        tail = text[match.end() :]
        section_match = _SECTION_AFTER.match(tail)
        if section_match is None:
            # The access reaches `workflows` without naming a workflow: a
            # stanza-level read, which is what the wrapper's enable-flag loop
            # does. Recorded rather than dropped, so it must still be declared.
            hits.append(ScanHit(rel, line_of(match.start()), owner, "*", None))
            continue
        section = section_match.group("a") or section_match.group("b")
        rest = tail[section_match.end() :]
        key_match = _KEY_AFTER.match(rest)
        if key_match is not None:
            key = key_match.group("a") or key_match.group("b")
        elif _GET_CONFIG_BEFORE.search(
            text[max(0, match.start() - 40) : match.start()]
        ):
            key_match = _GET_CONFIG_KEY.search(rest[:_GET_CONFIG_WINDOW])
            key = key_match.group("k") if key_match else None
        else:
            key = None
        hits.append(ScanHit(rel, line_of(match.start()), owner, section, key))

    for match in _PROJECTION_LITERAL.finditer(text):
        hits.append(ScanHit(rel, line_of(match.start()), owner, match.group("n"), None))
    return hits


def scan_surfaces(repo_root: str | os.PathLike) -> tuple[str, ...]:
    """Return every runtime-consumer surface the D-9.6 scan reads, repo-relative.

    The four ``.smk`` entry points, ``blueearth_cst/`` and ``scripts/`` — the
    same surface the design's inventory swept, because a permanent scan narrower
    than the inventory cannot certify what the inventory claimed.

    ``dev/scripts/`` stays outside the scan on the repository's own
    invocation-model rule: it is never part of a run, and a ``dev/scripts/``
    tool that acquires a run-path caller must move into the shipped package —
    where the scan sees it.

    **This module excludes itself**, and that is the one exclusion. It is the
    loader: it necessarily carries the access forms as patterns and the section
    names as contract data, so scanning it would report the scanner's own
    grammar as findings. Nothing here reads a config at all — every function
    takes the mapping from its caller — so the exclusion gives up no coverage a
    reviewer of this file would not have to provide anyway.
    """
    root = Path(repo_root)
    found = [f"{name}.smk" for name in WORKFLOW_NAMES]
    for package in ("blueearth_cst", "scripts"):
        for path in sorted((root / package).rglob("*.py")):
            if "__pycache__" in path.parts or path.name == Path(__file__).name:
                continue
            found.append(path.relative_to(root).as_posix())
    return tuple(found)


def scan_cross_workflow_reads(repo_root: str | os.PathLike) -> tuple[ScanHit, ...]:
    """Return every CROSS-workflow config access on the scanned surfaces (D-9.6).

    A hit is cross-workflow when the file does not own the section it reads. The
    caller — ``tests/test_config_composition.py`` — asserts the found set equals
    three separately-declared enumerations: ``CROSS_WORKFLOW_READS`` (value
    reads), ``IDENTITY_COMPARISONS``, and ``OWNERLESS_SECTION_READS``. They are
    separate rather than one merged allowlist so that retiring the first cannot
    silently absorb an entry into the others.

    Both directions are checked there: **completeness**, so an undeclared read
    turns the test red with a message saying *promote the key to* ``shared:``,
    *do not add an entry*; and **minimality**, so a declared entry with no live
    site is equally a failure and no enumeration can drift stale.

    The completeness claim is relative to the access forms above — an access the
    patterns cannot see (a dynamically constructed key) is out of reach, which
    is one reason the parse-time checks stay rather than being subsumed by this.
    """
    root = Path(repo_root)
    hits: set[ScanHit] = set()
    for rel in scan_surfaces(root):
        path = root / rel
        if not path.is_file():
            continue
        for hit in _scan_text(rel, path.read_text(encoding="utf-8")):
            if hit.reader is not None and hit.section == hit.reader:
                continue  # a workflow reading its own section
            hits.add(hit)
    return tuple(sorted(hits))


def partition_hits(
    hits: Iterable[ScanHit],
) -> tuple[
    frozenset[tuple[str, str, str]],
    frozenset[tuple[str, str]],
    frozenset[tuple[str, str]],
]:
    """Split scan hits into the three declared enumerations' comparable shapes.

    Returns ``(value_reads, identity_comparisons, ownerless_reads)`` — the first
    as ``(reader, owner, key)`` triples to compare against
    ``CROSS_WORKFLOW_READS``, the other two as ``(file, section)`` pairs.
    """
    value_reads = {
        (hit.reader, hit.section, hit.key)
        for hit in hits
        if hit.reader is not None and hit.key is not None
    }
    identity = {
        (hit.file, hit.section)
        for hit in hits
        if hit.reader is not None and hit.key is None
    }
    ownerless = {(hit.file, hit.section) for hit in hits if hit.reader is None}
    return frozenset(value_reads), frozenset(identity), frozenset(ownerless)
