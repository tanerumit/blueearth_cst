# Task Brief — Prepare R12 implementation from the accepted design

### Context

Follow repository `AGENTS.md`. The owner accepted
[the v6 design](wf3-simulation-identity-design.md) on 2026-09-10 after Astra
approved its final delta. This is the bounded implementation-preparation task,
not authorization to run or implement the entire program.

The accepted contract has two independently runnable workflows and three logical
stages. Production remains stochastic/Wflow, with CMIP a terminal plausibility
overlay. Internal fingerprints remain mandatory; routine users select an
experiment and scientific settings. The documented Class-B fit-interval deferral
is accepted; neither screening thresholds nor benchmark tolerances are validated
by design approval.

### Goal

Prepare executable phase briefs and a current evidence/validation inventory from
accepted design §§9, 11–13. Make the first implementation step concrete without
changing the accepted method or starting a model run.

### Non-goals

No runtime implementation, model execution, baseline recording, estimator change,
GCM producer, general execution-control platform, or repair of `st_0` comparability.

### Allowed scope

- Permitted: implementation planning documents beside this brief; the R12 backlog
  item; read-only inspection of the accepted design's §9.6 file inventory and
  current code/config/tests.
- Approval-gated: actual implementation and expensive scientific runs; resolve
  their execution scope before dispatching the resulting phase briefs.
- Forbidden: edits to frozen review records, sealed decisions, upstream packages,
  generated catalogs, lockfiles, or the numerical baseline during preparation.

### Progress

Preparation completed 2026-09-10. The [master implementation brief](implementation/master-brief.md)
links four phase briefs and the complete GF-1..32 validation map. The
[readiness record](implementation/readiness.md) distinguishes verified environment
and CLI checks from unimplemented successor tests and unexecuted numerical gates.
The immediate next execution task is P0's synthetic P2b feasibility fixture,
followed by the scoped model-builder pre-change snapshot before numerical rewiring.
No production implementation, synthetic feasibility run, or scientific run was
performed by this preparation task.

### Required changes (checklist)

- [x] Reconcile the source baseline recorded in the design with the current
  checkout; use `git rev-parse HEAD`, `git status --short`, and `rg --files` to
  remeasure the affected file inventory. Record changes in premises explicitly.
- [x] Produce a master implementation brief and bounded phase briefs following
  the accepted landing sequence: logical contract/adapter extraction in current
  WF3, durable handoff in current WF3, then entry-point/config/runner extraction.
  Use the exact sequence and blocking prerequisites in §4.2; do not invent a
  competing migration plan.
- [x] Assign every §9.6 migration surface and §13 ownership handoff to a phase.
  Include future supersession of sealed decisions without editing their records.
- [x] Carry every GF-1 through GF-32 claim and falsifier from §12 into the phase
  index, with its execution command or an explicit command-to-be-implemented
  status. Do not mistake proposed fixtures for checks that already exist.
- [x] Materialize the P2b, operation/target and checkpoint feasibility tasks before
  entry-point extraction; record failure/stop conditions from §§6.8 and 12.
- [x] Plan the pre-change numerical snapshot under current `AGENTS.md` baseline
  constraints. The frozen intake contains old config names and fixture premises;
  use accepted design §9.6 and current repository facts instead of copying them.
- [x] Give scientific/model validation to the §13 domain owners, using Astra for
  scientific and methodological evaluations as the owner requested.

### Validation

This preparation task uses document checks and repository inspection only.
Run `git diff --check`; verify every cited file and phase-brief link exists.
Check coverage of all 32 GF identifiers against accepted §12 and record each
unimplemented command as missing, never passed.

The resulting phase ladder must retain these design falsifiers and frequencies:

| Boundary | Required evidence carried forward |
|---|---|
| Before the first numerical implementation change | Current pre-change snapshot and the §9.6 baseline prerequisites |
| Per affected implementation change | Narrow covering tests; Python lint/format and CLI checks when triggered by `AGENTS.md` |
| Before entry-point extraction | P2b, operation/target feasibility, GF-29/GF-30 fresh single-invocation behavior |
| Numerical migration | GF-9 old/new comparison; GF-27/GF-28 seed/calendar preservation; GF-31 preparation portability |
| Resolution behavior | GF-32 default, advanced and retained metrics-only fixtures; GF-22 no hidden simulation |
| Scientific acceptance | GF-15 separately reviewed criteria and execution; §12.4 stage acceptance by model validators |
| Branch/milestone gates | Exact ladder in §12.4 and current `AGENTS.md`; no full-suite repetition without a new reason |

### Acceptance criteria

Every affected surface has an owner and phase, every runtime claim has a
falsifier, prerequisites precede their dependent edits, and outstanding numerical
or methodological decisions remain visible. Preparation must not assert that
design approval proves runtime or scientific correctness.

### Output requirements

Return the master/phase brief paths, coverage inventory, first executable task,
and unresolved execution decisions. Update the R12 backlog item with those links.

### Task constraints

Keep phase briefs concise by citing the accepted contract. Future execution
must preserve reference-atomic renames, immutable provenance and explicit error
behavior. Use the established tools and model conventions; do not patch upstream.
