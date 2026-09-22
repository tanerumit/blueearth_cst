# Output schema contract review — intake

Date: 2026-09-21
Target: `dev/working/complete-run-output-schema.md` on `refactor/workflow-layouts`
Genre: decision record (the nearest design-document genre for a multi-stage migration contract)

## Request and authority

The owner requests completion of P0, review of its selected contract, explicit acceptance before runtime edits, then P1–P7 in dependency order. This run covers P0 design and review only. The owner's stated framing fixes a clean output contract for fresh projects; no old-output compatibility readers; strict WF3 independence from WF4 elevation and preparation; the canonical SHA-256 digest-to-integer automatic-seed formula with a new WF3-only material version; possible numeric auto-seed changes; scientific comparison under a matched explicit seed. No upstream changes, resume, incidental baseline regeneration, output-tree rewriting, landing or push.

The master brief's P0 human acceptance is G2. The user supplied the problem, constraints, comparison policy and selected direction explicitly, so those are the recorded G1 framing authority; scientific review may challenge a material premise and return it to the owner before revision. No runtime implementation is authorized by this intake.

## Design decisions to settle

Versioned record and digest projections; exact source capture, coherent archive publication and crash recovery; absolute and relative rerun references; invocation coverage and parent failures; static plan pin, receipt, pointer and workspace collision policy; WF3-only seed material and module/code-inventory boundary; collection identity and shared WF4 elevation resolution; fresh-output break and baseline transition. Map each decision to P1–P6 and its first emission phase.

## Decision and success criteria

The contract must be independently implementable, reject ambiguous or mixed readiness, keep WF3 free of WF4 inputs and code, retain exact loaded source bytes, and make every emitted reference resolvable after a permitted project relocation. A fresh WF0–WF4 project must validate against it. Match scientific series under explicit seed; test the new auto-seed projection separately and allow numeric differences from v1.

## Evidence register

| ID | Premise requiring evidence | Falsifier / planned observation | Evidence status and closure |
|---|---|---|---|
| E1 | WF3 v1 seed material currently includes WF4 preparation dependencies. | Inspect `generation_plan.py` source projection and inventoried files. | Observed in the v1 code inspection; [domain review](internal-review-domain.md) records the source evidence. |
| E2 | Changing only WF4 inputs/code leaves the v2 auto seed and collection ID fixed. | Mutation tests at P4 and P7, including elevation bytes/settings and WF4-only code. | Hypothesis; P4/P7 must execute source-aware mutations. |
| E3 | Scientific generation remains equivalent under matched explicit seed. | Clean pre-change WF3 run and P5/P7 post-change series comparison with stated tolerance. | Unverified; [reference probes](prechange-reference-probes.md) stopped in WF3 3.02 before seed resolution. P0 capture and P5/P7 comparison remain open. |
| E4 | Archives capture bytes actually loaded and publish coherently. | P1 byte, race and crash-injection tests. | Hypothesis; P1 must execute tests. |
| E5 | Frozen plan controls the DAG and cannot be redirected by pointer replacement. | P5 cold/prepared/reuse DAGs, stale-source and competing-init tests. | Hypothesis; P5 must execute tests. |
| E6 | New references survive permitted project relocation and detect changed bytes. | P4/P6 relocation and mutation tests. | Hypothesis; P4/P6 must execute tests and real HydroMT resolution. |
| E7 | No old-output reader is needed for fresh projects; baseline transition is explicit. | Reader inventory and deliberate baseline replacement gate before checks. | Design policy supported; reader sweep and baseline transition remain P2/P5/P6/post-P6 evidence. |

This design includes domain-scientific content: seed and collection identity, scenario lineage, source treatment, and numerical continuity claims. The domain reviewer must disposition E1–E7 as supported, contested, or untestable as stated.

## Derived artifacts

| Artifact | Refresh after G2 |
|---|---|
| `dev/working/output-schema-implementation/master-brief.md` and P1–P7 briefs | Regenerate phase interfaces, versions, checks and gates from accepted design. |
| `dev/decisions/0011-preserve-config-sources-with-run-records.md` | Align decision status and settled archive details without erasing history. |
| `dev/working/t2609191457-wf3-static-planning.md` | Align the settled WF3 plan boundary and note supersession where needed. |
| `dev/working/complete-run-output-schema.md` | Replace working proposal with the accepted reviewed contract at G2. |

## Gate materialization

G1 framing is recorded from this explicit owner instruction. G2 requires the reviewed contract, finding ledger, clean pre-change reference, and the owner's explicit acceptance. The P1–P7 runtime sequence cannot start before G2.
