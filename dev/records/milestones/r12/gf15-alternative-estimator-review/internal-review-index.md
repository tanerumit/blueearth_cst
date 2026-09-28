# Internal review index — v1

Both reviews approve design-v1.md as a bounded study proposal. There are no
blocking or major findings. G1 selected the candidate; none of these findings
changes the algorithm, criteria, scope or support policy.

| Concern | Original finding | Severity | Authoritative artifact |
|---|---|---|---|
| Estimator-specific evidence and unbiasedness | domain-1 | minor | [Domain review](internal-review-domain.md), domain-1 |
| Monte Carlo precision and correlated derived rows | domain-2 | minor | [Domain review](internal-review-domain.md), domain-2 |
| Common-acceptance cohorts in paired method comparisons | risk-1 | minor | [Risk review](internal-review-risk.md), risk-1 |

Read each original finding and all suggested-fix parts in its artifact; this
index neither replaces its text nor changes its severity. The author must
disposition all three IDs and preserve the unchanged individual GF15 gates.

## Conflicts

No factual contradiction or severity divergence was found. Domain-2 and risk-1
address related but different issues: statistical independence and selection
of an accepted comparison cohort. Both remain separate findings.

## Scope and provenance

The risk review discloses that its initial status.md read included driver
summaries beyond G1. It did not open prior reviews or the ledger and does not
claim full blinding to metadata. Preserve that disclosure. The external round
will use a fresh process with automatic project context disabled and only its
brief/current design as initial inputs.

## Driver fact checks

These are proposal reporting gaps, not regressions in production behavior.
The estimator remains unexecuted. Existing records permit different acceptance
sets; common-cohort comparisons must therefore identify their denominator.
Nothing in these findings establishes new accuracy evidence or changes a gate.

The lean review shape remains applicable: no blocking finding, no external
non-convergence, and no round-2 trigger has occurred.

## External round 1 and full-panel promotion

The preceding lean-panel assessment is historical. External round 1 reviewed
v2 and returned revise. Preserve external-review-r1.md verbatim and every ID;
full-panel architecture/repo-fit reviews are now running on unchanged v2.

| Concern | Original finding | Severity | Authoritative artifact |
|---|---|---|---|
| Asymptotic-reference interpretation | ext1-1 | major | external-review-r1.md |
| Exception/refusal classification | ext1-2 | major | external-review-r1.md |
| Branch controls and oracle tolerance | ext1-3 | major | external-review-r1.md |
| Frozen predecessor artifacts and join keys | ext1-4 | major | external-review-r1.md |
| Numerical Monte Carlo diagnostics | ext1-5 | major | external-review-r1.md |
| Fit versus quantile refusal semantics | ext1-6 | minor | external-review-r1.md |
| Normalized versus physical L-moments | ext1-7 | minor | external-review-r1.md |
| Quantile oracle independence | ext1-8 | minor | external-review-r1.md |

Potential conflicts under fact check: ext1-1's causal attribution and extension
of a Gumbel reference to non-Gumbel shapes; ext1-5's proposed added uncertainty
computation against the explicit scope boundary. These are not dispositions.
No severity is changed. Reconcile full-panel findings before author revision.

## Full-panel reconciliation on v2

Both added lenses return revise. Their artifacts are immutable.

| Concern | Original findings | Severity | Artifact |
|---|---|---|---|
| Exception boundary | architecture-1; repo-fit-1 | major each | internal-review-architecture.md; internal-review-repo-fit.md |
| Inventory/join readiness | architecture-2; repo-fit-2 | minor each | same respective artifacts |
| Shared baseline acceptance | architecture-3; repo-fit-4 | minor each | same respective artifacts |
| Branch controls | architecture-4; repo-fit-3 | minor each | same respective artifacts |
| Quantile oracle independence | repo-fit-5 | minor | internal-review-repo-fit.md |

Conflicts preserved: architecture contests ext1-1's extrapolation to three shapes
and causal attribution, and ext1-5's assertion that bounded fixed-matrix
qualification contradicts explicitly unquantified Monte Carlo uncertainty.
Repo-fit confirms missing explicit bindings but directly establishes usable
predecessor schemas, contesting ext1-4's unproducibility premise. Neither review
changes the external severities. Author must disposition every original ID.

Driver scope reconciliation: retain the already authorized deterministic study
and its limited claims. Numerical uncertainty diagnostics, attainable-threshold
research and causal excuses for failed cells are not admitted as required
resolutions of this proposal. No new scope or selected alternative is chosen;
G1's scope remains in force. The author may reject unsupported parts with evidence;
any rejected major triggers round 2 and explicit ratification at G2. If the author
finds a necessary material scope change, stop and return to G1 before adopting it.

New factual correction: E6's byte-exact-across-B wording was overstated. The
predecessor audit establishes decoded JSON equality; distinct serializations have
different hashes. Intake now records that correction. Original A criteria remain
the proposed byte-exact authority; no predecessor artifact is altered.

## External round 2 — cap reached

Verbatim external-review-r2.md: revise on v3. All first-round resolutions are
accepted as defensible; new findings remain separately authoritative:

| Concern | ID | Severity |
|---|---|---|
| Float64 resolution versus new flat CDF tolerance | ext2-1 | major |
| Overlapping branch/population control precedence | ext2-2 | minor |
| Mathematical oracle bracket and failure bounds | ext2-3 | minor |

Driver fact checks and proposed owner rulings are in status.md. These concern
new v3 validation contracts, not production or GF15 criterion regressions.
The cap requires arbitration; no third full external review or silent acceptance.

## Arbitration repair verified

Owner accepted ext2-1/2/3 repairs. Frozen v4 confines the changes to D5/D6 and
forced version references. scoped-review-v4.md approves that delta with no
findings; author ledger records all three proposal-level verification closures.
Prior review artifacts and severities remain unchanged. G2 is now pending on v4
and its recorded dispositions; execution readiness remains future work.
