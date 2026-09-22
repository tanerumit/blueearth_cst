# Scoped verification of design v3

- Document reviewed: [design-v3.md](design-v3.md), delta from [design-v2.md](design-v2.md)
- Scope: [ext1-1–ext1-3](external-review-r1.md) only
- Role/mode: python-engineer, review
- Verdict: **PASS WITH NOTES** for this design delta. No new blocker or major finding.

| Finding | Verification against contract and current producer | Result |
|---|---|---|
| ext1-1 | §10.2.1 names the formerly open archive, request, plan, output, environment, simulation, response and metric payloads; assigns required fields, order, null/presence and H versus B rules. §10.7 binds these profiles to record IDs. The generator argument names and six sections match `GENERATOR_SEED_FIELDS` in `blueearth_cst/experiment/generation_plan.py`. Open physical values are hashed as whole values within explicitly named data namespaces; unknown control fields refuse. | Closed as a design specification. Canonical vectors and executable parsers remain P4/P6 evidence. |
| ext1-2 | §10.5 now requires an independent typed projection of the exact installed YAML plus actual positional CLI source/member arguments, equality against the frozen plan/intent, and checks before consumption and publication. This fits `build_weathergen_config` in `blueearth_cst/experiment/prepare_weathergen_config.py` and the five-argument bindings in `blueearth_cst/weathergen/generate_weather.R` and `impose_climate_change.R`. The latter derives member prefix/suffix from its output argument, so the separate output mapping check is necessary and stated. | Closed as a contract. P5 must demonstrate Python/R YAML interpretation equivalence, especially absent versus null optional arguments, and reject deliberately self-consistent bad mappings. |
| ext1-3 | §10.6 enumerates every excluded key in the current `GENERATOR_SEED_FIELDS` classification and assigns individual or interaction mutations. It requires actual provider execution with fixed snapshots and explicit seed, zero-tolerance decoded comparison including member/date association, repeated parallel/core runs, and promotion or refusal on scientific differences. | Closed as a conditional acceptance gate. No exclusion is empirically validated yet; P5/P7 cannot claim scientific acceptance until the matrix passes or the P0 contract is amended and reaccepted. |

This review checked only the v2→v3 resolution of the three external majors. It did not run the generator, establish the clean predecessor reference, verify canonical digest vectors, or grant G2 owner acceptance. Those remain separately required.
