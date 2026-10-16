# Named indicator sets: review intake

Date: 2026-10-16. Form: software/workflow design specification.
User request: "yes, lets start the indicator-set design review"

## Outcome and boundary

Review the existing design before implementation. The user authorized the previously sketched
multi-agent review, not implementation or publishing. All records belong to main's canonical task
folder under its maintenance exception; no implementation branch is needed for this review.

Settled: operations: [simulations, indicators]; either alone; named indicator_sets; user-facing YAML;
shared registered Python calculations; separate named table exports; machine records and immutable
results beneath the existing experiment _engine/. Indicator-only cannot run simulations.
Preserve current default calculations.

Journey: an author defines indicators and method parameters in YAML; a workflow user selects sets;
the runner validates inputs and uses shared retained responses; each complete set publishes separate
readable tables. A later indicator-only request reuses responses and valid results.
Minimum scope: named sets, default compatibility, independent reuse, reliable publication.
No expression language, dynamic plugin loader, numerical redesign, or cross-set computation cache.
Alternatives: scalar operation is simpler but not the agreed interface; per-set scripts duplicate methods.

Open framing: omitted defaults, custom-path syntax, closed schemas and method contracts, old targets
and metrics/export migration, metadata-only identity, partial publication. The second scientific set
is unspecified; illustrative low-flow choices cannot silently change existing default policies.

## Evidence register

Source checkout: main at 791fd1f9162d675eabc63de48825a6e4b4e74265.
Observations are code inspection, not newly executed WF4 behavior.
Paths below are beneath blueearth_cst/. Reviewer must disposition each premise.

| ID | Premise / exact observation | Reproduction | Precision / confidence |
|---|---|---|---|
| E1 | Two operations constrain runner targets. | experiment/simulation_runner.py | Exact; high. |
| E2 | Export uses one flat destination and current.json. | experiment/metric_export.py | Exact paths; high. |
| E3 | Run/bundle grains and group policies differ. | experiment/metric_registry.py | Contract; high. |
| E4 | Metric identity includes responses, code, environment. | experiment/metric_plan.py | Contract; high. |
| E5 | Indicator-only uses frozen simulation intent. | metrics_only_configuration | Branch; high. |
| E6 | An adapter can preserve default numerics. | Compare reducers with proposed schema. | Hypothesis. |

E5 also reads applicable live indicator settings. E6 needs an explicit coverage map and parity evidence,
not an assertion of completed validation. Dispositions: supported, contested, or untestable as stated.

## Domain and validation

Domain content: yes (aggregation, water years, missingness, references, preservation claims).
Independent claim-evaluation is required before G1. This is not a model predictive-skill study.
No framework probes scheduled; at most two named decision-critical probes if subsequently justified.

- Runnable now: source inspection of declarations, reducers, runner paths and export ownership.
- Pre-change evidence: retain matched responses and current default outputs/settings before implementation.
- Future checks: three operation selections, two sets, absent-response refusal, default parity,
  independent identities, partial failure/retry, legacy-reader migration. Follow the live validation ladder.
- Unavailable now: scientific acceptance for the unspecified second set.

## Derived artifacts

Canonical task note must point to the approved candidate and next action after G2. Preserve the seed
as the discussion draft. No implementation brief or schema generator commissioned.
Retain immutable raw reviews, candidates, protocol bytes and gate decisions in this run.
