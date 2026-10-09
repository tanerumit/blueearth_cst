## Verdict

verdict: approve
doc_version: design-v1.md

Reviewed SHA256: `80602FDA7FAE0AD1932EB4D618F98DE148B950E0090093C0AA9652AFD6B1FFAF`.

The design supports a bounded extraction that preserves existing rendering behavior. Approval is of
the specification, not a claim that visual equivalence or baseline readiness has been demonstrated.
Its explicit before-edit preflight and later acceptance checks remain necessary.

## Findings

None. No blocking, major, or minor defect established in this focused review.

## Reasoning and evidence

- **Dependency boundary:** Section 3.1 names a finite extraction and excludes scientific preparation,
  compositions, and workflow imports. The inspected helpers in
  `blueearth_cst/climate_analysis/diagnostic_figures.py:252` through `:568` use only the proposed
  rendering dependencies and listed tokens. No hidden method change was identified.
- **Compatibility and state:** Sections 3.1–3.2 preserve signatures, default values, and shared
  `STYLE`/`LABEL_BOX` identity while explicitly distinguishing rebinding from mutation.
  `diagnostic_figures.py:131` constructs its preset once; `:252` captures the default width at function
  definition. Verbatim extraction preserves those existing semantics. The separate override contract
  described in `blueearth_cst/shared/plot_style.py:29` remains outside the migration.
- **Backend ownership:** The risk is real and addressed: evaluation currently imports WF0 inside drawing
  functions (`blueearth_cst/shared/plot_evaluation.py:472`, `:1199`), while WF0 selects Agg at `:13`.
  Section 3.2 preserves lazy evaluation imports, requires an import-order probe, and authorizes an
  explicit script-owned fix before pyplot in `blueearth_cst/model/plot_results.py:11` if needed.
  WF2 already selects Agg independently in
  `blueearth_cst/projections/projection_suite_figures.py:5`.
- **Caption parity:** Section 3.3 correctly separates preserved behavior from physical-geometry claims.
  `diagnostic_figures.py:398` increases figure height and adds a super-label; moving it unchanged alone
  would not establish invariant axes geometry. The specification requires measurement and forbids a
  layout redesign being hidden inside this extraction.
- **Bounded acceptance:** Section 5 requires matched, frozen inputs and baseline renders before source
  edits, then inspection of affected families, captions, inventories, plotted arrays, and geometry.
  Dense, missing, optional, and multi-period coverage is explicitly required. Pending execution is
  therefore an open gate, not evidence of a design defect.

## Review limits

Six source files were inspected; this was not an independent repository-wide caller inventory or an
execution review. No workflow or render was run. No claim is made that every retained preview is
discoverable: the design records unreadable scratch and requires active rebinding previews to be
identified and migrated before acceptance. Source edits, baseline results, and their eventual
equivalence need the planned implementation review and coordinator acceptance.

Role: critical-thinker, confirmed by supplied role instructions. Effective model and effort: unverified.
