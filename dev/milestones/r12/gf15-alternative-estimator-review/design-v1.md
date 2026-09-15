# Method Spec — GF15 alternative GEV estimator

Status: proposed; v1, awaiting scientific review and G1  
Date: 2026-09-12  
Authors: cst-architect author agent  
Supersedes: none; original and normalized-B qualifications remain failed  
Lifecycle: maintained-current during review; append-only revision log; after approval, frozen-with-supersession at `dev/milestones/r12/gf15-alternative-estimator-design.md`  
Revisions:
- 2026-09-12: v1 proposes a bounded L-moment qualification; no execution authorized.

### Context and motivation

**Provisionally recommend one normalized, unbiased sample L-moment/PWM GEV candidate for qualification, not adoption.** Its rationale is a different estimation principle with inspectable numerical behavior; passing the unchanged GF15 targets is unknown and appears demanding. No source establishes those targets at n=18.

The [intake](intake.md), E1–E9, fixes authority. Original fitting passed only 3/24 baseline accuracy cells. Normalized B also passed 3/24 and 6/72 eligible relative cells, despite accepting every n=18 baseline fit. B retained 30 accepted-pair translation failures, 70 both-refused pairs and one changed-acceptance pair. Its 974 accepted fits with nonfinite physically mapped log-density have unresolved causes. These observations support investigating both sampling variability and computation; they do not prove that optimizer error explains the accuracy deficit. Sources are the original and B `scientific-handoff.md` files under `dev/milestones/r12/implementation/evidence/gf15/` and `gf15-normalized-qualification/`.

### Scope

Request type: **improve**, limited to a method proposal. Roadmap: unstable/insufficiently accurate return levels → qualify one explicit alternative → determine bounded adequacy or preserve failure → affect WF4 performance analysis only if separately approved.

| Capability slot | Binding and immutable revision | Owner / validation authority |
|---|---|---|
| `performance_analysis` | Proposed L-moment GEV below; lmoments3 1.0.8 wheel digest below; future adapter revision not yet created | python-engineer implementation / model-validator scientific acceptance |
| `orchestrator` | Proposed qualification stage sequence below, design-v1; no Snakemake modification | cst-architect / independent evidence reviewer |

`decision_framing` is not applicable: no assessment decision or criterion changes. `data_adapter`, `ensemble_generator`, `simulation_engine`, and `system_model_validation` are not applicable: no input preparation, weather generation, system simulation, or system-model validation occurs. `impact_model`, `robustness_evaluation`, and `projection_overlay` are not applicable: none of their outputs is declared. Projections remain a terminal plausibility overlay; stochastic perturbations remain stress-test forcing.

This document authorizes no fits, benchmark execution, installation, production change, screening change, or seal. No managed-project run is entering `ready`; namespace claim and run-control conformance are **not applicable to this authoring stage**. A future managed-root run must satisfy cst-run-control before readiness. Current production remains pinned by repository commit `85d0b8b6b4f8b078d96f645b1049ecd477c30998`.

### Assumptions

The fixed fixtures are IID stationary GEV blocks with known generating parameters. They represent neither discharge observations nor independent evidence of pooled-bundle stationarity. Negative fixture values are legitimate and remain untruncated. Population L-moments require finite mean, hence SciPy shape c > −1; all generating shapes satisfy this. Dependence, mixtures, structural misspecification, and nonstationarity remain outside qualification.

The low-flow estimand stays the median (p=.5) of annual seven-day minima, with no sign reversal; peak flow uses p=.9. Existing per-member rolling/block extraction, missingness, calendars, warm-up and pooling remain unchanged. Operational screening remains provisional ratio 1.0 and floor 10; passing a numerical fit or IID cell cannot validate them.

### Inputs and provenance

Authoritative criteria: `dev/milestones/r12/implementation/evidence/gf15/results/criteria.json`. Preserve that file byte-exact; its estimator description identifies the predecessor. A separate candidate manifest declares D1 as the proposed replacement without modifying numerical criteria. Reuse all original retained draws and offsets: c={−.2,0,.2}, n={10,18,30,60}, 1,000 draws/cell, generating location zero and scale one; p={.9,.5}; translated locations μ=ρ−zₚ for ρ={0,.05,.5,2,10}. Provenance identifies PCG64 with `SeedSequence([20260912, shape_index, count])`; do not redraw, clip or substitute observations. These synthetic, dimensionless inputs have no basin, calendar coverage, or external data licence dependency.

Pin Python 3.12.13, NumPy 2.4.6 and SciPy 1.18.0 from the predecessor environment; retain its full provenance and lock digest. Proposed additional package: `lmoments3-1.0.8-py3-none-any.whl`, SHA-256 `984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e`, from [PyPI release metadata](https://pypi.org/project/lmoments3/1.0.8/). Installation is a later approval dependency. The lock currently contains only an xclim constraint, not an installed lmoments3 binding (E9). The downloaded wheel, installed source digests, adapter commit, effective environment and input/criteria hashes must be frozen before execution; documentation labelled “stable” alone is insufficient provenance.

### Method

**D1: Complete candidate.** Fit one three-parameter GEV to each supplied finite float64 sample; repeat independently for every translated sample. The future adapter has the proposed interface `fit_case(sample, probabilities) -> record`, not an existing command. It receives no generating shape, location, scale, truth, ratio or draw identifier. The evaluator owns those, preventing oracle leakage.

1. Refuse invalid dimensionality, any nonfinite supplied value, fewer than four values, or a constant sample. Missing-block filtering remains upstream; never silently filter these fixture inputs. Set a=min(sample), s=max(sample)−a and y=(sample−a)/s. Refuse nonfinite/nonpositive s or nonfinite y. Keep all ties. This positive affine transform is numerical conditioning, not a fitted error denominator.
2. Obtain `lmoments3.lmom_ratios(y, nmom=3)`, yielding l₁, l₂, t₃. The underlying unbiased order-statistic PWM definition is bᵣ=n⁻¹Σᵢ[C(i−1,r)/C(n−1,r)]y₍ᵢ₎, r=0,1,2; l₁=b₀, l₂=2b₁−b₀, t₃=(6b₂−6b₁+b₀)/l₂. This is not a plotting-position variant. [Hosking et al. (1985)](https://www.stat.cmu.edu/technometrics/80-89/VOL-27-03/v2703251.pdf), [sample API/source](https://lmoments3.readthedocs.io/stable/_modules/lmoments3.html).
3. Use `lmoments3.distr.gev.lmom_fit(lmom_ratios=[l1,l2,t3])`; read named keys `c`, `loc`, `scale`. The theoretical shape equation is t₃=2(1−3⁻ᶜ)/(1−2⁻ᶜ)−3, with the continuous c=0 limit. For nonzero c, σᵧ=l₂c/[Γ(1+c)(1−2⁻ᶜ)] and μᵧ=l₁−σᵧ[1−Γ(1+c)]/c. These equations explain the estimator; the pinned library implementation defines its approximation. Its rational branches use t₃=0 and −.8 boundaries; t₃≤−.97 changes the starting value. The iterative branch allows 19 updates with relative shape tolerance 1e−6. The positive-t₃ branch snaps |c|<1e−5 to Gumbel, using Euler constant .57721566. Preserve these disclosed choices; do not silently replace them with a different root solver. [GEV implementation](https://lmoments3.readthedocs.io/stable/_modules/lmoments3/distr.html).
4. Refuse nonfinite L-moments, l₂≤0, |t₃|≥1, estimator exceptions, nonfinite parameters, c≤−1, or σᵧ≤0. The c domain is the finite-mean L-moment domain, not a tuned tail prior. There is no optimizer status flag to infer; successful return alone still faces all checks. No trimming, shrinkage, empirical-quantile fallback, or retry is allowed.
5. Conventional ξ=−c. For each requested p, calculate zₚ=−expm1(c log(−log p))/c, or −log(−log p) when c=0; then qᵧ=μᵧ+σᵧzₚ and q=a+s qᵧ. Use float64 NumPy operations. Refuse p outside (0,1), nonfinite intermediate/returned quantiles, or nonfinite back-mapped μ=a+sμᵧ and σ=sσᵧ. This is the primary quantile route; physical-parameter SciPy PPF is an independent diagnostic, not a fallback. [SciPy sign/distribution convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genextreme.html).

**D2: Record and validity.** Return input/range/normalization data, L-moments, normalized and physical parameters, requested probabilities/quantiles, acceptance, all refusal reasons, warnings and source identity. Baseline fit acceptance is shared across its two requested quantiles; each translated fit requests its designated scalar probability. Record normalized and physical support membership and log-density separately. A PWM endpoint excluding a sample value is a model-fit diagnostic, not automatically computational invalidity; do not retrofit a likelihood refusal into this candidate or B. No scientific suitability claim follows from computational acceptance.

### Parameters and defaults

All controls above are fixed prospectively. There is no user shape bound, prior, restart budget or tunable plotting position. The documented public xclim PWM route requires an lmoments3 distribution instance; `dist="genextreme"` alone does not supply that interface. The direct candidate API preserves exceptions and avoids silently changing the production wrapper. [Official xclim source](https://xclim.readthedocs.io/en/stable/_modules/xclim/indices/stats.html). Production integration would require a separately reviewed adapter and new immutable metric identity under R12 §8.4.

### Validation regime

**D3: Unchanged gates.** Complete coverage is 132,000 fits, 144,000 quantile rows, 144 summary cells and 120,000 translation pairs. Error is eσ=(q̂−q)/σ_generating. Every cell requires valid rate ≥.95 over **all 1,000 draws**, |median(eσ)|≤.10 and P90(|eσ|)≤.50 upper/.25 lower. Report median absolute error too. Use NumPy quantile `method="linear"`; error summaries condition on valid fits and expose that denominator.

At ρ={.5,2,10}, also require |median(e_relative)|≤.10 and P90(|e_relative|)≤.50 upper/.25 lower, where e_relative=(q̂−q)/|q|. At zero it is undefined, recorded as null; .05 is diagnostic. Every translated pair requires unchanged acceptance and |Δeσ|≤1e−6 when both accepted. Both-refused pairs are never numerical passes. No averaging, post hoc exclusion or changed threshold repairs failure.

Proposed sequential handoffs, all execution stages pending separate authorization:

| Stage | Owner and deliverable | Gate / stop rule |
|---|---|---|
| 1/3 implementation readiness | python-engineer: isolated adapter, frozen dependency, effective command, manifest/schema and analytical controls | model-validator accepts equations, sign and package-source match; stop on unavailable dependency or ambiguous source behavior |
| 2/3 bounded qualification | authorized executor: one complete original matrix, raw rows, warnings/refusals, paired comparisons, summaries and timing | stop on corrupted input, coverage or control failure; statistical failures remain visible and the complete matrix is reported |
| 3/3 independent validation | model-validator: independently recomputed counts/errors/criteria and signed handoff | any criterion failure leaves candidate failed and GF15 unresolved; no stage integrates without returned validation |

Controls must falsify: theoretical parameter recovery using population L-moments at c={−.2,0,.2}; the disclosed Gumbel approximation and solver branches; explicit invalid/constant/tied samples; analytical-versus-SciPy quantiles; no RNG use; exact same-environment replay; affine behavior through all fixed translated pairs. All are **planned**, not executed. Reviewer checks use independently calculated moments/quantiles rather than the same fitting routine as its own oracle. Proposed analytical-control tolerance is 1e−5 absolute for recovered shape and for location/scale errors divided by the supplied population scale; quantile-route agreement is 1e−10 times max(1, |qᵧ|). Require exact same-environment replay and unchanged refusal classification. Branch/exception controls must exercise each disclosed branch without changing its defaults. These additional engineering controls cannot relax GF15.

Artifacts include every attempted fit/quantile, per-cell denominators, paired A/B/candidate error summaries, parameter/support diagnostics, immutable criteria copy, source/input/environment digests and independent verdict. Candidate runner and working command do not yet exist. Require an absent output namespace, atomic completion records, single writer and input-hash-checked resume; resume only incomplete fixed chunks under the identical candidate/environment, never overwrite predecessor evidence.

### Uncertainty treatment

B’s n=18 P90 errors span .592–1.553 upper and .484–.558 lower. Improving median bias does not establish concentration. Moreover, at ρ=.5 the relative gate requires P90 scale errors ≤.25 upper/.125 lower and median bias ≤.05, stricter than baseline gates. This follows directly from e_relative=eσ/ρ; it is not a new criterion.

For scale intuition only, a Gumbel location model with known scale and shape has per-observation location information 1/σ²: its score is [1−exp(−(x−μ)/σ)]/σ. The regular efficient normal approximation gives P90 absolute location error about 1.645σ/√18=.388σ. This author-derived asymptotic illustration, even with nuisance parameters known, cautions against promising .25 or .125 accuracy. It is **not** a finite-sample impossibility bound for biased estimators or conditional-on-acceptance summaries. Literature comparisons use different losses and matrices; no credible evidence currently establishes an all-cell pass.

Repeated use of retained draws makes candidate selection adaptive. Freeze this one candidate before execution and label any pass conditional on that development matrix. A separately approved holdout with fresh seeds and the same cells could assess replication; it is additional scope, neither authorized nor run, and cannot replace or erase fixed-matrix failures. No new uncertainty interval, screening floor or real-bundle applicability claim follows here.

### Alternatives considered

**L-moment/PWM (recommended study).** Hosking et al. find favorable small-sample performance in their experiments; Hosking’s L-moment framework explains reduced sensitivity relative to conventional moments. Neither is a universal efficiency guarantee or this benchmark’s qualification. Positive-affine equivariance is mathematical; floating-point implementation still must pass every pair. [Hosking (1990)](https://doi.org/10.1111/j.2517-6161.1990.tb01775.x).

**Maximum product of spacings.** Optimize sums of log CDF spacings, including endpoint spacings. Wong and Li report stable small-sample GEV behavior, including comparisons favorable to PWM. It is preferable if L-moment accuracy is inadequate and a reviewed optimizer/domain contract is acceptable. SciPy `stats.fit(method="mse")` supplies a route but needs explicit finite search bounds; leaving location/scale unspecified fixes them at 0/1. Its stochastic default requires a frozen RNG; repeated-value handling also belongs to the estimator. Those unresolved choices prevent treating MPS as a ready second candidate. [Wong and Li (2006/2007)](https://arxiv.org/abs/math/0702830), [SciPy fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fit.html).

**Generalized maximum likelihood / regularized Bayesian GEV.** Martins and Stedinger use shape-prior information to control implausible small-sample estimates. Prefer this when an independently justified prior and its sensitivity assessment are acceptable. It changes statistical assumptions and cannot silently use the benchmark’s three generating shapes as prior information. Conventional moments also deserve consideration: the paper reports favorable RMSE in a restricted shape range, but RMSE does not establish GF15 P90 performance. Neither alternative is executed or fully specified here. [Martins and Stedinger (2000)](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999wr900330).

### Limitations and open questions

G1 must rule on this specific candidate, including its finite-mean domain, library approximation and diagnostic-only support policy. G2 accepts the converged design; execution requires separate authorization. Package compatibility and runtime properties remain untested. If one complete candidate fails, stop estimator shopping and return the evidence to the owner; considering another estimator or changing scientific scope requires a new reviewed method ruling. A qualification pass still leaves independent replication, real-bundle applicability, screening validation and production integration unresolved.

### References

Primary references linked above: Hosking, Wallis and Wood (1985), *Technometrics* 27(3), 251–261; Hosking (1990), *JRSS B* 52(1), 105–124; Martins and Stedinger (2000), *Water Resources Research* 36(3), 737–744, DOI 10.1029/1999WR900330; Wong and Li, *IMS Lecture Notes–Monograph Series* 52, 272–283, author preprint posted 2007. Software sources were inspected read-only on 2026-09-12. Predecessor scientific verdicts, criteria and provenance remain authoritative; this proposal supersedes none of them.


