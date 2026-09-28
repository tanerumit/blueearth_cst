# Internal review index

Date: 2026-09-13
Reviewed document: design-v1.md
G1: Option A approved; domain-1/domain-2 actions accepted for revision/handoff.

Verbatim reviews are authoritative; this index preserves every original ID and
severity and does not replace their claims or suggested fixes.

| Concern | Original finding | Severity | Authoritative source | Scope impact |
|---|---|---|---|---|
| Moment interpretation | domain-1 | minor | internal-review-domain.md, finding domain-1 | Wording qualification inside approved fixed method |
| Unexecuted production parity | domain-2 | minor | internal-review-domain.md, finding domain-2; E7 disposition | Preserve already-required implementation prerequisite |
| Incomplete migration comparison | risk-1 | minor | internal-review-risk.md, finding risk-1 | Clarify failed-attempt coverage; no change to abort/publication rules |

Both reviews approve v1: zero blocking and zero major findings. E1–E6 are
supported; E7 is untestable in the current pre-implementation state and must
remain outstanding. All three findings enter the author ledger individually.

## Conflicts

No factual contradiction or severity divergence was identified. The risk lens
explicitly retains the domain actions without duplicating them. No finding
offers a scope-divergent resolution; no G1 return is required before revision.

## Driver premise checks

The accepted candidate and current source records remain unchanged. The risk
finding concerns existing sequential failure propagation in
`metric_plan.py::reduce_metric_plan`; preserving an abort cannot establish
results for later unevaluated keys. It is an acceptance-reporting ambiguity,
not a demonstrated regression in the proposed estimator. New adapter parity
remains unexecuted as both draft and domain review state.

## Full promotion and external round1 — v2

External round1 is preserved verbatim in external-review-r1.md: revise with
ext1-1 major and ext1-2/ext1-3 minor. Non-convergence promoted the run to full;
the architecture and repo-fit reviews inspected v2 independently with settled
G1 framing. Each returns revise. All original IDs/severities remain separate.

| Concern | Original finding | Severity | Authoritative source |
|---|---|---|---|
| Detached CSV provenance | ext1-1 | major | external-review-r1.md, ext1-1 |
| Constant-sample refusal routing | ext1-2 | minor | external-review-r1.md, ext1-2 |
| Requested probability / evidence domain | ext1-3 | minor | external-review-r1.md, ext1-3 |
| Live environment freshness | architecture-1 | major | internal-review-architecture.md, architecture-1 |
| Live environment freshness | repo-1 | major | internal-review-repo-fit.md, repo-1 |
| Existing source-tree distribution | repo-2 | minor | internal-review-repo-fit.md, repo-2 |
| Existing invocation artifacts | repo-3 | minor | internal-review-repo-fit.md, repo-3 |

### Conflicts and premise checks

- architecture-1 and repo-1 agree on mechanism and severity. Keep both rows and disposition each suggested fix separately. Driver source check confirms build_metric_plan reuses request.metric_environment and reduce/publication depend on that reconstruction: pre-existing freshness gap, newly relied upon by the proposed provenance contract.
- ext1-1's detached-CSV hazard is real; its in-tree provenance characterization needs qualification. Driver inspection confirms metric_plan.publish_metric_set already writes metrics.json beside indicator CSVs and binds each table digest. The architecture/repo-fit reviews affirm that manifest/report design. There is no disagreement that a detached bare CSV loses those bindings. The author must preserve both observations and explicitly disposition ext1-1's alternatives; no driver regrading.
- ext1-1 offers a disclosure route preserving the export surface. G1/D1 already preserve the four-column format and D8 treats export_wflow_results.py as a preservation surface. A resolution respecting those constraints is within settled scope; any proposed new export product or changed schema returns to G1 before adoption.
- repo-2's source-tree constraint is explicit in pyproject.toml; no new installable distribution is authorized. A relocated-source resource test stays within scope.
- repo-3 is confirmed by scripts/simulate_system.py's existing config/runs/invocations/simulation-<id>.json record. This is operational bookkeeping, not a change to retained scientific inputs.
- No severity divergence was identified. Fixing observed freshness and clarifying constant/probability/refusal/packaging/invocation contracts can remain within Option A. No change to estimator, 8x policy, provisional screening or applicability claim is warranted by these findings.
