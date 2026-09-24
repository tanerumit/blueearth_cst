---
title: Make WF3 planning static before Snakemake
type: todo-item
status: backlog
effort: 2
area: wf3 scenarios
queue:
created: 2026-09-19
updated: 2026-09-19
---

> [!note] Overview
> **What** — Resolve the scenario collection into a validated immutable preflight manifest before Snakemake builds the WF3 DAG, then derive all downstream jobs from that manifest.
> **Why** — Checkpoint expansion currently prevents the opening console plan from reporting exact downstream job counts; keeping the dynamic checkpoint also makes dry-run planning provisional.
> **Effort** — Large architectural change: separate pure planning from collection mutation, define a durable manifest contract, and migrate the dynamic WF3 checkpoint DAG without weakening freshness, reuse, or concurrency guarantees.

## Progress

- 2026-09-24: plan freeze and checkpoint removal landed on main (`c83ead70`); WF3 overview reports exact counts. Remainder (drop `after checkpoint` console state, migration note, fresh/reuse count proof) folded into the wf3 generation bundle, step 3 of `dev/drafts/wf3-generation-bundle-plan.md`.

- [ ] Specify and version the preflight manifest: collection identity, reuse decision, scenario rows, expected outputs, and every input digest needed to detect staleness.
- [ ] Separate collection planning into a side-effect-free command that writes the manifest atomically before Snakemake starts.
- [ ] Replace `prepare_collection_sources` checkpoint expansion with static rule inputs and fan-out derived only from the validated manifest.
- [ ] Define concurrency, interruption, and resume behavior when manifests or retained collections already exist.
- [ ] Update direct WF3 and `run_workflows.py` entry points so both produce or require the same preflight manifest.
- [ ] Prove fresh-generation and retained-collection-reuse DAGs report exact upfront job counts and preserve current outputs.
- [ ] Document the migration and remove the provisional `after checkpoint` console state once no WF3 rules depend on dynamic expansion.

## Decision

Prefer a static preflight manifest over parse-time estimation or a wrapper-only two-phase run. One immutable plan should be authoritative for both console reporting and execution; duplicating checkpoint logic merely to estimate counts would create a second decision path that can drift from Snakemake.
