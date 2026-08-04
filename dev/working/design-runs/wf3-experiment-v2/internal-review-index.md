# Internal review — aggregation index (stage 2)

Driver-written index over the three immutable lens reviews of `design-v1.md`:
`internal-review-risk.md` (19 findings), `internal-review-architecture.md` (16),
`internal-review-repo-fit.md` (17). **52 findings: 8 blocking, 22 major, 22
minor; all three verdicts `revise`.** Grouping is by concern and by reference
only — each original ID keeps its own filed severity and text, and the per-lens
files are authoritative for every claim. Nothing here re-grades or deletes.

## Concern groups

| # | Concern | Findings (severity) |
|---|---|---|
| C1 | Fixture arithmetic and gate observations (K=12, no `cst_0`, `aggregate_rlz: true`) | arch-1 (B), risk-9 (M) |
| C2 | Manifest freshness boundary — generation-side inputs invisible to `member_hash`/reuse | risk-1 (B), arch-3 (B), arch-7 (M), repo-fit-10 (m) |
| C3 | Manifest computability — `st_csv_digest` produced downstream of its consumer | arch-2 (B) |
| C4 | `allow_partial` under `aggregate_rlz` — holes under-average, zero-fill, or crash; partial sweep freezes | arch-15 (B), risk-2 (B), repo-fit-6 (M), risk-5 (M) |
| C5 | Per-member logging/benchmarks — `merge_logs` flat-file short-circuit; TOTAL double-count | arch-4 (B), repo-fit-4 (M), arch-11 (m) |
| C6 | Resume/recovery executability — stale `sweep.lock` vs GF-2; `threads: workflow.cores`; Windows kill/replace semantics; completeness-record identity + finalization order | repo-fit-1 (B), repo-fit-2 (M), repo-fit-14 (m), risk-8 (M) |
| C7 | Experiment lock scope — claimed at sweep start, stages 1/2/4 unguarded | risk-6 (M) |
| C8 | Worker robustness — stderr drainage/hang, codec, pool depth & recycling (A4 at scale) | risk-7 (M), repo-fit-17 (m), risk-4 (M) |
| C9 | Gate/falsifier operands — C-7 dead post-re-baseline; floor comparand + placement; n=2 envelope; manifest byte-identity vs `created_at`; C-11 string cells | risk-3 (M), risk-10 (M), risk-14 (m), risk-15 (m), repo-fit-12 (m) |
| C10 | Unowned/unscoped work and named test breakage — in-slot refactors, guard-fusion tests, baseline-scope cardinality, `staticmaps` input, spawn semantics, retired-key mechanism, tool homes, parse-time digest | arch-9 (M), repo-fit-5 (M), repo-fit-7 (M), repo-fit-8 (M), repo-fit-3 (M), repo-fit-11 (m), repo-fit-9 (m), repo-fit-15 (m), repo-fit-13 (m) |
| C11 | Contract/doc deltas — retired rule identities in seam docs; date-CSV move vs R07 ruling; RT_*; WG-3 key mislabel; undeclared reads; completeness-record populations; OQ-1 deferral consistency | arch-8 (M), risk-11 (M), arch-10 (m), arch-14 (m), repo-fit-16 (m), arch-12 (m), risk-18 (m) |
| C12 | Ledger semantics detail — transition legality, fold ordering, relative paths, reduce digest verification, orphan transients, C-13 falsifier, missing F4/F8/F12 gates + `service:` alternative | arch-13 (m), risk-17 (m), arch-16 (m), risk-12 (M), risk-19 (m), risk-13 (m), risk-16 (m) |

## Conflicts section (required)

**Factual contradictions:** none found. The closest pair is complementary, not
contradictory: repo-fit's "What holds" verifies that `merge_benchmarks`' glob
absorbs per-member TSVs unchanged, while arch-11 files that this very
absorption double-counts the sweep in the TOTAL row — both readings are
correct and both are preserved.

**Severity divergences** (each ID is dispositioned at its own filed severity;
the divergence itself is the signal):

1. **Fixture arithmetic** — arch-1 `blocking` vs risk-9 `major`. Same defect
   (K=14 vs the fixture's K=12); arch grades it blocking because GF-6/GF-7 are
   the gates that make the ratified OQ-4 posture testable.
2. **`merge_logs` short-circuit** — arch-4 `blocking` vs repo-fit-4 `major`.
   Same mechanism (`merge_logs.py:106-111`), same suggested fix direction
   (orchestrator log inside the member part-dir).
3. **`allow_partial` under aggregation** — arch-15 and risk-2 `blocking` vs
   repo-fit-6 `major`. All three agree the reduce body cannot express a hole
   as written; they differ on observed failure shape (under-averaged cell /
   `pd.concat([])` crash / zero-filled row) — all three shapes are real and
   the revision must handle all of them.

## Driver notes for the revision (sequencing, not content)

- **Gate-return items (presented to the owner before the revision):**
  (a) risk-18's proposal to carve `verbose = TRUE` out of the G1 OQ-1
  deferral — it is a call-site edit, so it touches the ruling's letter even
  though it is value-neutral (warning-only); (b) arch-1/risk-9's resolution
  fork — recompute all fixture numbers at K=12 (scope-preserving) vs flipping
  the fixture to `run_historical: true` (baseline-slice change). Owner rulings
  recorded in `status.md` before stage 3 dispatch.
- Cross-references the author should honor: C2's fixes interact (arch-3 wants
  `seed_r` in `member_hash` + baseline digest at sweep start; risk-1 adds the
  reuse-condition framing and the template digest; arch-2 constrains where the
  WG-2 digest can come from). C4's fixes must survive C1's corrected
  arithmetic. C9's risk-3 redefinition of C-7 (paired same-input comparison)
  is what makes A4's falsifier real — §9.6's parity table depends on it.
