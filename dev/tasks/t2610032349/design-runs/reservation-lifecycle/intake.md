# Reservation lifecycle intake

Request (verbatim): "Can we start the implementation on this branch?"

## Framing and existing decisions

Target: blueearth_cst, session-1, feat/minor-improvements. The owner authorized implementation of
the combined task brief on this branch; landing and pushing remain separate decisions.
The normative behavior is in `../../experiment-naming-plan.md`; the phase map is `../../task-brief.md`.
Preserve those settled choices. The review fills schema/publication/ownership gaps, rather than
reopening explicit creation versus continuation or adding project-folder version management.

Problem: existing dated-name allocation does not supply numbered families, retained allocation history
or a binding before expensive producers. Changed scenarios must not acquire an interrupted identity.
Criteria: predictable selection, early refusal, exact input attribution, recoverable crashes, no
deleted-number reuse, no preview reservation, compatible legacy reads and minimal new machinery.
Success: a self-contained reviewed contract implementing every naming-plan matrix row.
Non-goals: numerical algorithms, Wflow checkpoints, native-response repair, model revisions, multi-user
network locking, folder migration or adoption of unlanded WF3 changes.

## Scope and missing normative detail

Inventory current consumers. Specify closed allocation/reservation schemas; pending/resolved state;
effective scientific request projection and automatic-seed recovery; ledger transaction order;
interrupted-publication recovery; lock ownership; exact legacy precedence; runner handoff and preview.
Verify the plan's proposed output placement. Reconcile current main's WF3 run IDs, not another lane.
Give each new mechanism a cheap falsifier and separate proven facts from hypotheses.

## User journey and artifacts

A user chooses an output root and base/pin. Plain execution selects the highest identity or first one;
explicit creation reserves another. Record intent before producers; resolve exact collection/runs
after generation; bind simulation before native responses. Compatible retries keep the identity and
valid completed runs. Incompatible retries identify differences and offer original-input recovery or
explicit creation. Dry runs preview without allocation. Metadata does not replace scientific identity.

The source plan embeds the proposed tree and acceptance matrix; carry them self-contained into the
reviewed design with corrections justified against live code. No HTML sketch is needed for this CLI.

## Evidence register

| Premise | Source | Observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|
| Simulation intent guards reuse | simulation_record.py:464 | Canonical mismatch raises | Exact code | Read 450–489 | High |
| Runner already has project ownership | run_workflows.py:925 | project-execution archive lock | Exact code | rg archive_lock | High |
| WF3 owns seed projection | generation_plan.py | Closed seed classification exists | Exact code | Read SEED_FIELDS | High |
| Scaffold output is separate | create_case.py | Outputs derive from runs/slug/active | Exact code | Read _prepare | High |
| Partial-run safe reuse | Naming plan | Hypothesis pending probes | Unmeasured | Fixture/probe required | Open |

These code observations were made on 6998d0fd, 2026-10-10. Author must refresh and extend this evidence
inside the design without modifying this intake. Do not assume automatic seeds are random per retry:
inspect current resolution/request machinery and prove the proposed recovery preserves it.

Domain-scientific content: yes. Exact realized-input attribution and seed/response identity acceptance
are scientific reproducibility claims. A pre-G1 domain lens is required; no physical-method change.

## Derived-artifact register and gate materialization

Required: intake, status and draft. Conditional: inventory, domain/risk reviews, index, ledger,
external brief/review and revisions. Reviewed versions are immutable; status owns gate authority.
Task brief and plan links derive from accepted status, never an author's self-declared acceptance.

Focused allocator/runner tests and Ruff are installed Pixi commands. Full/e2e commands are declared in
pixi.toml, but executable environment/data readiness must be probed before expensive acceptance.
Existing numerical baseline is stale and is not a naming gate. No pre-change scientific snapshot has
been taken; any proposed numerical comparison must capture matched inputs before runtime changes.
P1 scaffold-only work can proceed independently without changing scientific inputs.

## Authority

Author may write only design-v1.md and consumer-inventory.md in this run. Read repository and canonical
skill definitions; no runtime edits, commits, external writes or nested delegation. Do not edit the
source plan; review versions supplement it pending acceptance. Driver owns status and gate requests.
