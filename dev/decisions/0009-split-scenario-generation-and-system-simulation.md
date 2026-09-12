# ADR 0009 — Split scenario generation and system simulation

- **Status:** accepted and implemented; P3 validation passed on 2026-09-12
- **Date:** 2026-09-11
- **Maintenance:** frozen-with-supersession after the R12 landing
- **Source:** owner-accepted R12 v6 and the 2026-09-10 mandatory-runner ruling

### Context

The former WF3 combined stochastic generation, model execution and reduction.
An experiment name consequently selected generation state, and changing metric
requirements could reach simulation producers. The accepted R12 design separates
the scientific handoffs and requires exact, independently validated reuse.

### Decision

`generate_scenarios.smk` is WF3. It prepares historical climate without a model,
resolves the source-time seed and publishes an immutable scenario collection.
`simulate_system.smk` is WF4, with two fixed modules selected by the configured
operation. Its mandatory runner validates actual targets before one Snakemake
invocation. Metrics remain an operation of WF4.

The convenience order is analyze_climate → generate_scenarios → build_model →
simulate_system → analyze_projections. Generation and model construction are
independent prerequisites of simulation. Projections remain a plausibility
overlay and never select the stress-test scenarios.

Five closed workflow stanzas reference separate settings files. Migration pins
each old resolved seed, including legacy `auto`. New `auto` derives from a
versioned generation projection and source content, excluding experiment names
and identifier capacity. Ordinary paths retain their existing run-directory
anchor; `config_path` remains relative to the project file.

Collections retain forcing and preparation inputs; simulations retain native
responses and their immutable request; metric sets retain explicit unit
membership. Ready artifacts are validated before reuse. Existing output trees
are not renamed or implicitly upgraded.

### Consequences

The former entry point and stanza are retired without a wrapper. Users migrate
configuration and generate a new collection before creating a new simulation.
Routine selection reads one exact generation plan; an explicit manifest permits
source-free collection reuse. Metrics-only requires complete retained responses
and defines no model or simulation producers.

The landing requires the P3 execution matrix, source/seed falsifiers, complete
row crosswalk, Class-A/B agreement and Class-C shared-reference mean agreement,
followed by the final software gate. GF-15 benchmark qualification remains a
separate decision; operational fits are not evidence of screening adequacy.

### Alternatives considered

Keeping the combined entry point would reduce migration work but preserve the
cross-stage dependencies this decision removes. A third metrics workflow would
make reduction independently invocable but duplicate the simulation selection
surface; the accepted operation split provides isolation within WF4.

Bare Snakemake target validation was rejected after the P0 bypass probe. A thin
mandatory runner is preferable until a public, tested Snakemake mechanism can
enforce the complete operation/target matrix before DAG execution.

### Related

- [Accepted design](../milestones/r12/wf3-simulation-identity-design.md)
- [P3 implementation brief](../milestones/r12/implementation/phase-3-workflow-extraction.md)
- [Workflow migration](../../docs/migration-workflow-names.md)
- [Retained handoffs](../../docs/wf3-retained-handoffs.md)

This supersedes the former WF3 ownership and path clauses identified as C24,
C25 and C28 by R12. Their sealed records remain unchanged.
