## Verdict
verdict: revise
doc_version: design-v2.md

## Findings
### ext1-1  [blocking]
- section: §6.1 Process topology; §8.1 Failure modes and recovery (F4)
- finding: The shared pull-queue topology has no parent-owned assignment or acknowledgement protocol. A slot can dequeue a member and die before its claim reaches the sole ledger writer; the parent can observe the dead process but cannot determine which member vanished from the queue, despite F4 promising that it records and retries that slot’s in-flight member.
- rationale: GF-16 can hang waiting for a result that will never arrive, omit the lost member, or require an unspecified reconciliation pass. This defeats the claimed one-member crash recovery and leaves the core scheduler contract incomplete.
- suggested_fix: Make assignment parent-owned: track `slot_id → member_id`, append `claimed` before dispatch, send work through per-slot queues or an explicit ready/assign protocol, and requeue that recorded assignment when the slot dies. Add a gate that kills a slot immediately after assignment but before child acknowledgement.

### ext1-2  [major]
- section: §6.2 Orchestrator ↔ Julia worker line protocol; §6.5 Logging and benchmark capture
- finding: The prescribed stderr handling is incompatible with per-member logs. A persistent Julia worker receives one stderr file handle at process spawn, so all later members served by that worker write Wflow output into the first member’s log.
- rationale: G4’s per-member visibility is false: diagnostics and failures are attributed to the wrong member, while GF-14 can still pass because it exercises only the first request’s flood.
- suggested_fix: Route output per request: include a log path in each `run` message and have Julia open it and redirect stdout and stderr around that member’s `Wflow.run`, or use a continuously drained pipe whose reader routes output according to the single in-flight request. Gate two sequential members on one worker and verify strict log separation.

### ext1-3  [major]
- section: §5.3 Atomicity, single writer, crash consistency; §5.4 Member state machine
- finding: The corruption rule declares “two succeeded rows” illegal, while the designed invalidation and repair paths legitimately produce `succeeded → quarantined → claimed → succeeded`, both when a member hash changes and when an input or output digest diverges.
- rationale: After a valid GF-12 invalidation or F8 repair, the next fold can classify the legitimate second success as corruption and refuse all future resumes. Step 4 explicitly requires tests for the conflicting rule, so implementation cannot resolve this silently.
- suggested_fix: Define transition validation by explicit execution epochs and make repeated success illegal only without an intervening `quarantined` transition. Specify the hash carried by quarantine rows and add valid-history tests for both same-hash digest repair and changed-hash invalidation.

### ext1-4  [major]
- section: §8.2 The failure-injection gate set (GF-15)
- finding: GF-15 cannot produce its expected observation. After mutating an undeclared member CSV, all declared sweep and reduce inputs and outputs remain present and fresh, so the document’s own §7.2 rules imply that Snakemake runs neither the sweep nor the reduce.
- rationale: The command returns “Nothing to be done”; the promised reduce-time digest failure never occurs. Post-completion member corruption therefore remains undetected on an ordinary re-invocation, contrary to F8 and C-10.
- suggested_fix: Either wire a digest of the live result files listed by `ledger_final.csv` into reduce freshness, accepting the extra parse/reduce cost, or narrow the claim and require an explicit integrity-verification command. Rewrite GF-15 to exercise the chosen mechanism.

### ext1-5  [major]
- section: §9.6 OQ-6 — migration parity strategy and the baseline manifest; §12 Claim → falsifier table (C-7)
- finding: C-7 does not specify how either comparison run is forced to execute, and changing `sweep_workers` alone cannot do so: execution-policy fields are excluded from `member_hash`, and GF-11 explicitly expects such a change to re-enter the sweep and skip every member. The proposed `p=12` versus `p=1` comparison also changes concurrency and oversubscription alongside session depth.
- rationale: The primary falsifier for warm-session numerical identity can become two comparisons of the same previously generated CSVs, falsely verifying A4; if forcibly rerun, any difference is confounded with radically different resource contention.
- suggested_fix: Run two clean, isolated experiment states with identical inputs, using `sweep_workers=1, worker_max_members=1` for one fresh Julia session per member versus `sweep_workers=1, worker_max_members=0` for all members in one session. Capture both result sets before comparison and state the exact reset or isolation commands.

### ext1-6  [major]
- section: §13 Step 4 — The sweep runner and worker pool; §13 Step 8 — Performance floor confirmation
- finding: The binding performance comparison is not like-for-like. New rule 3.08 performs perturbation, downscaling, and simulation, whereas the 228.1-second P3-3 comparand measures only the old 3.10 Wflow batch stage; the cited P3-3 evidence separately assigns about 156 seconds to upstream work.
- rationale: A correct fused implementation can fail merely because its gate charges work absent from the baseline, encouraging implementers to game timing boundaries or reject a genuine improvement. Conversely, the measurement cannot establish G7’s performance claim relative to batching.
- suggested_fix: Time both implementations across the same scientific boundary—from identical baseline/grid readiness through completion of all member CSVs—or compare new 3.08 against the old critical-path span covering perturbation, downscaling, and 3.10 simulation. Keep the held `p × M` budget and report component timings separately.