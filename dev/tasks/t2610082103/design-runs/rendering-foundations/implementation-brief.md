# Task Brief — Extract shared rendering fundamentals

Lifecycle: temporary task-owned handoff. Status: ready, dispatch only after status.md records G2 approval.

### Context

Follow repository AGENTS.md, python-discipline, python-plotting and testing-policy. Read the exact reviewed
design-v2.md (SHA256 80602fda7fae0ad1932eb4d618f98de148b950e0090093c0aa9652afd6b1ffaf), status.md,
and baseline/evidence.md. Internal and independent reviews approved with no findings.

### Goal

Implement the design's first extraction, preserving reviewed appearance, scientific values and product
contracts. Use the smallest behavior-preserving move; no additional architecture decisions.

### Non-goals

Export/logging decoupling, caption redesign, scientific methods, shared map-reference production,
prepared-series interfaces, external packaging, R migration and legacy-style modernization.

### Allowed scope

Only the twelve Python paths in design §4, including conditional plot_results.py, and the ownership
reference update in dev/reference/plot-style.md. Up to eleven Python files without the backend fix.
These counts were established by the 2026-10-10 architect inventory; remeasure imports with rg before
editing. Report extra required callers to coordinator rather than omit them or expand scope silently.
Temporary checks/candidate outputs belong in .tmp/scratchpad/shared-rendering/candidate/.

### Required changes (checklist)

- Move the exact listed helpers and tokens; inert package initializer, no backend or domain imports.
- Preserve old WF0 imports as explicit compatibility re-exports; migrate all active fundamentals callers.
- Preserve shared mutable style identity, lazy evaluation imports and older cartographic overrides.
- Probe backend ownership and apply the design's conditional explicit batch Agg selection if needed.
- Remove replaced duplicate definitions; update the plotting ownership reference.

### Commit plan

One atomic extraction plus all callers and compatibility aliases. Coordinator stages explicit authored
paths and commits after verification; worker makes no commits. Keep session-1/chore/minor-fixes pinned.

### Validation

Before edits: confirm G2 identity, completed baseline, unchanged baseline source/input hashes and source
diff. Frozen baseline contains 167 PNGs and declared omissions; never overwrite it.

During edits: touched-file Ruff and the narrowest affected checks. After the final code candidate: run
the focused pytest command in design §5 once, plus test_cli.py if plot_results.py changes; redirect logs
to files. Run final repository lint/format-check once. No automatic full suite or all-five execution for
this figure-only packet; escalate any runtime/configuration/non-figure contract change.

Falsifiers: import probe detects forbidden domain imports/backend mutation; alias/state probe detects
copies or changed defaults; same-input candidate renders detect changed plotted arrays, dimensions,
captions or inventory. Use the baseline's recorded commands with only output-root changes. Supplement
optional subbasins, missing/constant data, long years and multi-period cases as design §5 requires.
Keep checks temporary. Capture axes geometry for short/long captions; distinguish existing geometry
defects from extraction regressions. Do not use image-byte equality as visual acceptance.

### Acceptance criteria

Exact extraction and complete caller migration; passing focused checks; matched input identity;
all affected renders available for coordinator inspection; no unexplained data/style/output delta.
Fresh reviewer checks the diff. A failed falsifier or changed contract reopens the packet; missing data
or environment failures require diagnosis, not silent scope reduction.

### Output requirements

Return changed-file list, removed definitions, commands/results, input/output roots, unresolved risks
and concise evidence. Coordinator retains durable findings and inspects visuals. No invented pass claims.

### Task constraints

One source writer. You are not alone; preserve others' edits. No nested delegation, new dependencies,
production-output writes, board edits, generated-file edits, commits, branch changes, landing or push.
