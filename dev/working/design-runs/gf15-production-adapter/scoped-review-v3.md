---
verdict: approve
doc_version: design-v3.md
reviewed_sha256: 47508c9b6b124d4bd7e0424c1e66a0fb9e6755b4164ab69e50ef10a735eb86d0
counts:
  blocking: 0
  major: 0
  minor: 0
findings: []
scope: >-
  Scoped verification of design-v2.md to design-v3.md, all ten original finding
  dispositions, changed decisions and their evidence premises. Settled G1 Option A
  is preserved. This is design approval for G2 consideration, not implementation
  acceptance, measured production parity, or actual-bundle adequacy.
round_2:
  waiver_supported: true
  blocking_fix_changed_mechanism: false
  rejected_blocking_or_major: false
  rationale: >-
    No original finding is blocking. All three major findings are accepted and
    resolved as design contracts. ext1-1 explicitly offered either alternative (a)
    or (b); v3 adopts every part of (b), while explaining why (a) is not selected.
    This is not rejection of the major finding. The new environment mechanism
    therefore requires this scoped pass, not the blocking-fix round-two trigger.
---

Approve v3 within the approved provisional C integration scope. The delta closes
the original findings without changing the fixed estimator, screening ratio/floor,
retained 8x criteria, source-tree distribution model, or four-column export surface.
No new delta findings arose; no delta-N IDs are allocated.

The review used design-review-loop's scoped verification, verdict, closure and
evidence rules, and claim-evaluation's claim/inference framework. Original review
artifacts, rather than the aggregation index, supplied the authoritative findings.
The v2/v3 text diff, intake, ledger and G1/status record were inspected. This pass
did not repeat the whole scientific review or treat earlier reviewers' agreement
as new empirical evidence.

| Original ID | Original severity | Resolution assessment in v3 |
|---|---|---|
| domain-1 | minor | Resolved and preserved. D2 attaches unbiasedness to raw/back-mapped linear L-moments under sampling assumptions in exact arithmetic; random normalization and float64 recovery add no guarantee. The denial of transfer to fitted parameters, t3 and quantiles remains. |
| domain-2 | minor | Design action resolved and preserved; empirical prerequisite remains outstanding. E7 and D8 require source-qualified independent control parity on every supported platform, unchanged tolerances, exact acceptance/refusal checks and a failing wrong-result mutant. Handoff 4/4 retains the evidence/verdict and outstanding status. |
| risk-1 | minor | Resolved and preserved in D3/D8 and Metrics-only acceptance: an abort is incomplete, names the first failure and every unvisited key, cannot pass migration acceptance, and cannot be converted into acceptance by a separately identified nonpublishing continuation. |
| ext1-1 | major | Resolved through offered alternative (b), part by part: D8 explicitly preserves CSV schema/formatting; handoff 2/4 user documentation and 3/4 migration record must disclose the detached-vintage hazard; the Costs paragraph names the risk; the validation row checks these deliverables. Provenance-context retention is required. Alternative (a) is explicitly not selected, with a G1 return if a standalone export product becomes required. |
| ext1-2 | minor | Resolved. D1 explicitly removes the old constant guard, routes screened constants through C to structured invalid_range, and retains insufficient-block and extraction/compatibility boundaries. The added constant-sample falsifier discriminates the old unstructured guard. The original suggested wording's broad phrase about all pre-fit refusals is properly limited to the fitting boundary; ordinary extraction faults do not need invented FitResults. |
| ext1-3 | minor | Resolved. D4 checks every actual requested probability against the verified declaration before fit_case; a named typed coverage fault aborts publication. It forbids clamping/substitution/domain expansion, leaves generic adapter validation intact, and includes a mismatch falsifier plus separate .9/.5 coverage checks. |
| architecture-1 | major | Resolved as a design contract. D5 specifies one freshly observed bounded resolver, installed estimator hashes, canonical descriptor and digest comparisons, direct-reduction and publication entry checks, and a final check after flush before readiness. Mismatch and resolution failure abort; explicit new requests create new identities; historical reads remain independent. Retained-A/observed-B, unchanged lmoments3 hashes, zero-fit/no-marker, late-mismatch and fresh-B identity falsifiers cover every proposed part. |
| repo-1 | major | Resolved independently at its original severity by the same D5 mechanism. Reusing the retained descriptor is explicitly insufficient; other numerical/native dependencies remain in the observation. The retained-plan test discriminates this specific pre-existing gap without requiring a shared-helper redesign. |
| repo-2 | minor | Resolved. D5 uses the existing importable source tree and tracked resource, with a relocated source-plus-asset test denying original checkout/dev/scratch access. Missing/corrupt assets must fail. No wheel, build backend or packaging manifest is introduced. |
| repo-3 | minor | Resolved. D8 limits the strict new metric-artifact allowance to the selected experiment results namespace, separately records existing invocation bookkeeping and declared attempt logs, and preserves exact collection/simulation/response request/inventory/native bytes. The operational allowance cannot excuse scientific mutation. |

The ledger has a v3 disposition for every original ID and addresses each part of
the offered fixes. Earlier deferred domain rows are historical append-only entries,
followed by accepted design dispositions; they are not current unresolved design
findings. The three major IDs remain major in the history and are not silently
merged or regraded.

Changed-decision and premise assessment:

| Change / premise | Assessment and evidence |
|---|---|
| D1 constant routing | Supported feasibility. metric_registry.py::reduce_bundle currently screens insufficient blocks, then applies np.ptp(sample)==0 before its broad fitting exception wrapper. Removing that guard has the stated structured-refusal consequence without altering extracted blocks. The required mutant distinguishes the two paths. |
| D4 probability binding | Supported design logic. The reducer currently computes a scalar probability from return_period before fitting. Membership in the verified discrete set [.9,.5] can be checked there without coupling peak and low samples or putting benchmark context into the adapter. Exact membership is appropriate for these fixed constants; it is not a claim that the synthetic shape/count/ratio domain describes an actual bundle. The falsifier must select a probability absent from that set, not merely test a numerical interval. |
| D5/D7 live environment | Supported at the source-mechanism level; implementation remains unexecuted. current_metric_request currently calls stage_environment, whereas build_metric_plan reconstructs from request.metric_environment. stage_environment reads installed distribution metadata and Conda dependency records on each call and retains Python/platform fields; it does not use a retained-request cache. Its existing no-R/no-Julia metric projection can be reused locally and extended with verified lmoments3 source identity. reduce_metric_plan and publish_metric_set offer explicit pre-fit seams; publication flushes payloads before atomic_record(marker, manifest), providing the final check seam. |
| D5 portability | Supported source-model premise. pyproject.toml explicitly documents a plain importable directory and no distribution/build tables. Relocating the required source and asset tests the proposed dependency boundary without introducing a packaging product. The relocation/missing/corrupt tests remain future acceptance work. |
| D8 export disclosure | Supported, with the original premise qualified. publish_metric_set already writes indicator table digests and environment/evidence references into sibling metrics.json. A detached bare CSV loses that context and remains estimator-ambiguous. v3 truthfully accepts this residual cost and requires disclosure rather than asserting that the unchanged CSV identifies C. |
| D8 operational writes | Supported by scripts/simulate_system.py: it writes config/runs/invocations/simulation-<id>.json before execution and updates it on completion/failure. Allowing and recording that existing bookkeeping avoids a false migration failure without relaxing scientific immutability. |
| E1-E6 | Their substantive scientific observations and scope claims are unchanged by this delta. No new benchmark rerun, independent holdout, current environment availability, source-parity result or actual-bundle inference is asserted. E5's execution freshness premise is now stated with the bounded resolver and discriminating falsifiers above. E4 still requires current setup inspection. |
| E7 | Outstanding empirical hypothesis, correctly assigned to implementation acceptance rather than presented as an observed result. Independent frozen controls establish the reference only. Per-platform source-qualified parity, fixed tolerances, exact refusal codes and deliberately wrong-result mutants remain the settling evidence. Design approval cannot satisfy this gate. |

The environment check's guarantee is deliberately bounded: it compares observed
metadata/native closure and verified estimator files at specified boundaries. It
does not atomically freeze external package changes or prove every loaded binary
matches disk after concurrent mutation. D5 states the isolated, unchanged execution
environment assumption and denies atomic protection; the proposed tests verify
fresh observation and stale-plan refusal, not qualification of an arbitrary B
environment. This is a coherent claim-to-falsifier boundary.

Residual risks remain explicit: production/platform parity and isolated dependency
setup are unmeasured; the pre-change retained snapshot must be selected before the
first implementation commit; resource inclusion, runtime guards and migration
comparison are unexecuted; a single refusal can prevent complete publication;
detached CSVs can mix estimator vintages. The retained post-results 8x rescore
provides no fresh-data generalization, uncertainty interval, screening validation,
or real-system adequacy. No additional scientific study is needed to approve this
bounded design, but none of those missing assurances follows from approval.

Verification was read-only source and document inspection, the v2/v3 text diff,
and SHA-256 binding of the reviewed v3. No production edits, tests, numerical fits,
environment installs/solves or implementation acceptance were performed. Only
this assigned review artifact was written. Effective reviewer runtime model and
effort were not independently verified and are not reported as measured settings.
