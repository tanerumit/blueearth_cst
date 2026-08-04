---
run: wf3-experiment-v2
target-repo: blueearth_cst
genre: workflow-spec
author-binding: cst-architect
started: 2026-08-01
variant: full
stage: 6a-arbitration-revision
external-rounds-completed: 2
dispatches:
  opus: 6  # +scoped verification pass (6a delta)
  fable: 2  # r2 revision + 6a arbitration revision (ext2-2..5 fault
            # prior-round resolutions — tier trigger both times)
cost:
  expensive-checks: 0
  doc-lines: 1903 (v1) -> 2969 (v2) -> 3195 (v3)
findings:
  unique: 65
  re-raised: 9  # ext1-2..6 each fault a v2 resolution of a panel finding
                # (risk-7, arch-13, risk-12, risk-3, risk-10);
                # ext2-2..5 fault compositions of r2 fixes (risk-8/risk-6
                # identity check, allow_partial artifact, quarantine lever,
                # epoch legality × orphan pruning)
gates:
  G1: approved 2026-08-01
  G2: pending
flags: [rejected-major-part-pending-G2, fable-escalation-r2]
  # rejected-major-part: risk-7 part 3 (data-derived wall-clock ceiling)
  # rejected by author with rationale; parts 1-2 accepted. Needs G2
  # ratification — NOTE ext1-2 faults exactly those accepted parts.
  # fable-escalation-r2: ext1-2..6 fault prior-round resolutions → the
  # stage-6 revision spawn runs on Fable per the tier policy.
round-2:
  dispatched: yes
  triggers-checked: [mechanism-changed, rejected-blocking-major, new-decision-ids,
                     probe-missing-or-contradicted]
  fired: [mechanism-changed, new-decision-ids]
  # mechanism-changed: ext1-1's blocking fix replaced the scheduling mechanism
  # (shared mp.Queue -> parent-owned assignment over per-slot pipes).
  # new-decision-ids: GF-19/GF-20, C-21/C-22, §14.14, new protocol surface,
  # _worker_<id>.log artifact, --verify command, extended override set.
  # rejected-blocking-major: NOT fired (ext1-4 was a branch selection, not a
  # rejection; risk-7 part 3 is a prior-round flag already pending G2).
  # probe-missing-or-contradicted: NOT fired (PR-1..7 stand; the new
  # mechanisms rest on stdlib semantics with falsifiers C-21/C-22 added).
---

# Auxiliary artifacts (outside the run schema)

- `v2-change-summary.md` — plain-language explanation of the v1→v2 changes,
  written by the stage-3 author agent on direct owner request AFTER its
  stage deliverables. Derived, non-normative (design-vN.md wins on any
  disagreement); regenerate or delete if the design changes at G2. Not a
  stage output — do not treat as unrecognized on resume.

# Stage log

- [done] 0-intake — outputs: intake.md (scope authority:
  dev/workflows/wf3-climate-experiment-v2-intake.md @ edc0689; evidence
  register P1–P9; gate-materialization table; derived-artifact register).
  design-scoping dialogue already ran pre-loop (committed scoping intake).
- [done] 1-draft — outputs: design-v1.md (1903 lines; 6 probes PR-1..PR-6;
  P6 settled MEASURED on installed weathergenr v1.2.0 — intake P6 row
  corrected; 2 self-caught blocking inconsistencies fixed pre-delivery).
  Structural checks passed (genre sections present, alternatives 14.1+
  non-empty, version series intact).
- [done] G1 — approved 2026-08-01 (provisional alternative: the drafted
  4-stage manifest+ledger architecture). RULINGS (settled framing for all
  subsequent stages):
  | Item | Ruling |
  |---|---|
  | OQ-1 precip_variance | **DEFERRED ENTIRELY — no call-site change this milestone.** Axis stays inert (variance follows mean², installed weathergenr v1.2.0 behavior). `precip_variance` field RETAINED in WG-2 / manifest / long-table schema so later activation is cheap. Activation (`scale_var_with_mean=FALSE`) is a later owned task; the design must record it as a named followup and document the inertness loudly in the contract docs. Design §9.1's provisional recommendation (a) is superseded by this ruling. |
  | Drift guard | Three-layer interpretation RATIFIED (3.00b comparator folded into manifest rule + sweep-start re-verification). |
  | OQ-4 reduce posture | Fail-loud default + `allow_partial: true` escape hatch; **no minimum-completeness threshold**. |
  | response_long.csv | JOINS the baseline manifest at the single re-record. |
  | Milestone id | **R9** confirmed (prefix `r09:`, home `dev/workflows/`). |
- [done] 2-internal-panel — outputs: internal-review-risk.md (19: 2B/10M/7m),
  internal-review-architecture.md (16: 5B/5M/6m), internal-review-repo-fit.md
  (17: 1B/7M/9m), internal-review-index.md (12 concern groups; conflicts: 0
  factual contradictions, 3 severity divergences). All verdicts revise on
  design-v1.md. 52 findings total: 8 blocking / 22 major / 22 minor.
- [done] gate-return — owner ruled 2026-08-01: (a) risk-18 carve-out ALLOWED —
  `verbose = TRUE` may be passed at the R call site (warning-only, value-
  neutral); the OQ-1 deferral otherwise stands (axis inert, no
  scale_var_with_mean change). (b) arch-1/risk-9: RECOMPUTE AT K=12 —
  scope-preserving; fixture config untouched (run_historical stays false, no
  cst_0 members on fixture, aggregate_rlz true).
- [done] 3-revision-r1 — outputs: design-v2.md (2969 lines; DRAFT v2 header;
  +55% over v1, growth concentrated in §5/§8.2/§12/§13, flagged for G2),
  ledger.md (52 rows, all 52 accepted; 0 rejected blocking; risk-7 part 3
  rejected within an accepted row → G2 ratification flag; 10 further per-part
  rejections with rationale inside accepted rows). Structural checks passed:
  52/52 IDs have rows, version series append-only. Key new mechanisms:
  fifth reuse condition over recorded input digests; st_params_digest
  replacing st_csv_digest; cell-complete allow_partial; workflow-lifetime
  experiment lock (onstart/onsuccess/onerror, PR-7 probed); 3.08 as shell:
  rule; C-7 as paired same-input comparison; sweep_incomplete.json retry
  path; floor comparand = 228.1 s sweep-stage makespan at end of step 4;
  gates GF-12..GF-18; claims C-17..C-20, C-7s; followups R9-F1, R9-F2.
- [done] 4-external-r1 — outputs: external-review-r1.md (doc_version:
  design-v2.md; verdict REVISE; 1 blocking + 5 major, 0 minor). Clean-room
  round via codex exec (codex-cli 0.145.0, --sandbox read-only,
  -c approval_policy=never); post-run `git status --short` clean except the
  untracked run dir → read-only intent held. ext1-1 queue assignment/ack
  protocol gap; ext1-2 per-member stderr routing (faults risk-7 fix);
  ext1-3 transition-legality vs legitimate repair histories (faults arch-13
  fix); ext1-4 GF-15 unexecutable — Snakemake never re-enters (faults
  risk-12 fix); ext1-5 C-7 cannot force re-execution + confounded operands
  (faults risk-3 fix); ext1-6 floor comparand not like-for-like (faults
  risk-10 fix).
- [done] 5-convergence-r1 — NOT CONVERGED (verdict revise; 1B/5M open) →
  stage 6. Fable escalation trigger met: external review faulted five
  prior-round resolutions.
- [done] 6-revision-r2 — outputs: design-v3.md (3195 lines, DRAFT v3; Fable
  spawn), ledger.md rows ext1-1..ext1-6 (all 6 accepted; ext1-4 resolved via
  the reviewer's second branch, first branch priced+rejected in §14.14;
  risk-7 part-3 rejection STANDS under the new ext1-2 mechanism, still
  G2-flagged). Structural checks: 58/58 ledger rows, version series intact.
  Round-2 trigger check: FIRED (mechanism-changed on the blocking fix;
  new-decision-ids) → round 2 dispatched, no waiver.
- [done] 4-external-r2 — outputs: external-review-r2.md (doc_version:
  design-v3.md; verdict REVISE; 2 blocking + 5 major). Read-only intent held
  (git status clean except untracked run dir). All 7 findings target the v3
  mechanisms: ext2-1 no cst_0 branch in the fused lifecycle; ext2-2
  invocation_id scope contradiction; ext2-3 stale completeness.csv after
  retry-to-complete; ext2-4 quarantine self-nested move; ext2-5 orphan
  pruning vs epoch legality; ext2-6 unchecked file.rename publication;
  ext2-7 floor gated on one timing pair.
- [done] 5-convergence-r2 — NOT CONVERGED; external cap (2) reached →
  round-cap arbitration. Driver premise verification: ext2-1..5 confirmed
  (ext2-1/2/3/4 against the v3 text, ext2-5 confirmed-plausible), ext2-6
  confirmed-plausible with the unchecked-rename mechanism PRE-EXISTING in
  generate_weather.R, ext2-7 premise true but graded against P3-3's n=1
  precedent. ext2-1..5 graded regression; ext2-6 mixed; ext2-7 pre-existing
  practice newly load-bearing as a gate.
- [done] arbitration — owner ruled 2026-08-01, all seven ACCEPTED, FIX
  REQUIRED:
  | ext2-1..6 | accepted as presented (baseline cst_0 lifecycle + synthetic
  gate; lock-minted invocation_id authoritative, finalization vs succeeded
  ids distinguished; stale completeness removed on full-completeness reduce
  + GF-13 extension; explicit quarantine inventory; orphan legality
  decoupled from live artifacts (or tombstones); checked atomic publication
  for the per-realization CSVs/plots) |
  | ext2-7 | accepted via the counterbalanced protocol: ≥3 AB/BA pairs on
  the fixture, all spans + dispersion reported, gate on the median |
- [open] 6a-arbitration-revision — fresh author spawn on FABLE (ext2-2..5
  fault prior-round resolutions → tier trigger); deliverable design-v4.md
  confined to ext2-1..7 + forced cross-refs + revision log; ledger rows
  ext2-1..7 citing the rulings; then driver scope-check + scoped
  verification pass over new decision IDs; then G2 under arbitration
  authority — the cap stands, no further external rounds.
  RECOVERY LOG: first 6a spawn terminated on a Fable session limit
  (resource exhaustion, resets 20:10 CET) having only made the v4 copy
  (verified byte-identical to v3, 0 ledger rows — no content lost). Owner
  directed continuation; same-thread resume dispatched (rung 1) after the
  limit lifted, with an on-disk state inventory in the resume message.
  Second interruption: mid-stream stall (retryable transport) after the
  design edits, before the ledger append; second same-thread resume scoped
  to the ledger remainder succeeded.
- [done] 6a-arbitration-revision — outputs: design-v4.md (3420 lines, DRAFT
  v4), ledger.md +7 rows (ext2-1..7, all citing owner arbitration
  2026-08-01; 65 rows total, append-only intact). Driver SCOPE CHECK
  PASSED: 47 diff hunks map to 24 sections, all on the author's declared
  list, each traceable to an arbitrated finding or forced cross-ref. New
  decision IDs: GF-21..24 (+GF-2/GF-13 extended), C-23..27 (+C-12/C-17
  restated), ledger_final id split (succeeded_ vs finalization_),
  publish_file helper, ExperimentLockMissingError, quarantine-generation
  layout, legal-history category, baseline transient set, defined-absent
  null semantics.
- [done] scoped-verification-6a — outputs: scoped-verification-6a.md.
  VERDICT: PASS (0 blocking, 0 major, 7 minor sv-1..sv-7 — author's
  discretion; candidates for finalize). All seven rulings implemented
  substantively; premises repo-verified; no new contradictions. Reviewer's
  advisor call failed (overloaded) — single-reviewer pass, noted.
- [open] G2 — presenting: approve design-v4; ratify risk-7 part-3
  rejection; sv-minor handling; body budget (1903→3420 lines).
