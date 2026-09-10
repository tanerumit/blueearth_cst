```yaml
verdict: approve
doc_version: design-v5.md
scope: v4-to-v5 delta resolving ext1-1 through ext1-4
```

The scoped delta resolves all four original major findings at design stage. No new blocking, major, or minor finding was identified. This verdict approves the revised contracts; it does not establish implementation feasibility, numerical equivalence, or scientific acceptance of unexecuted benchmark criteria.

The captured `v4-v5.diff` matches the two design files, and v4’s SHA-256 matches the recorded revision input. Review was confined to the permitted documents, v5 ledger dispositions, necessary design interactions, and directly cited factual sources. No edits, delegation, tests, or scientific runs were performed.

| Original ID | Resolution status | Verification and evidence |
|---|---|---|
| **ext1-1 — major** | **Resolved at design stage** | §§7.5–7.6 distinguish estimator benchmarking from screening-policy validation. Generating-scale-normalized error removes location dependence from the error denominator; translated paired samples separately test numerical equivariance. The `rho` matrix is justified as sensitivity coverage, without claiming representative discharge regimes. Zero relative error denominators are explicitly undefined, near-zero applicability remains unvalidated, and fit refusals retain the full sampling denominator. §§7.4 and 8.4 persist these limitations and include evidence declarations in metric identity. A benchmark pass cannot validate `1.0`/`10` or establish actual-bundle adequacy. Numerical tolerances remain proposals requiring the stated scientific approval and execution. |
| **ext1-2 — major** | **Resolved at design stage** | §5.4a assigns ownership to every identified preparation input and packages catalog semantics, PET selection, forcing elevation, and ancillary files. Baseline `downscale_climate_forcing.py`, `prepare_climate_data_catalog.py`, and rule 3.14 substantiate the CHIRPS sidecar, non-CHIRPS catalog-orography, reader, and PET premises. §§5.5–5.7, 6.3–6.4, and 8.2 carry the context through validation, durable retention, the neutral adapter, and content identity. Computing the relative-path representation before collection creation avoids a circular dependency. GF-31 explicitly tests consumption without original stores/catalogs and preserves coverage of the supported branches. |
| **ext1-3 — major** | **Resolved at design stage** | §§5.2 and 8.4a specify separate checkpoints for source-dependent collection identity and response-dependent metric identity. Request keys are scheduling identifiers; final scientific identities retain their content dependencies. Checkpoint input functions expose exact downstream targets, with plan verification, stale-input refusal/rebuilding, and published-output preservation. §§6.8 and 9.5 retain independent workflow execution and prohibit simulation producers in metrics-only mode. GF-29/GF-30 explicitly start without determining artifacts and require one invocation, exact output identification, and direct/runner coverage. Repository composition remains explicitly untested. |
| **ext1-4 — major** | **Resolved at design stage** | §§7.1 and 7.4 derive expected keys independently from selected declarations, grains, evaluated runs, bundle memberships, and required locations. Validation requires global uniqueness and exact equality across emitted tables, independently rederives the persisted expectation, and separately checks metric-specific value validity. Missing locations or failed fits cannot shrink applicability. §9.2 applies the contract to later consumption; GF-10 supplies omission and duplication fixtures that retain complete unit/index and overall design coverage, including metrics-only publication. |

The checkpoint proposal uses documented public DAG reevaluation through checkpoint input functions. Its output-preservation provision also corresponds to documented `update(...)` behavior. These sources establish available mechanisms, while GF-29/GF-30 must establish their successful composition here. [Snakemake checkpoints](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#data-dependent-conditional-execution), [output preservation](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#updating-existing-output-files).

The interactions preserve the agreed boundaries: collection consumption remains portable; preparation metadata supplies physical inputs without exposing stochastic scenario fields; planning records confer no readiness; metrics-only work remains independent of live model execution; and CMIP remains terminal. No unchanged methodological decision was reopened.

**New findings:** None. No original external finding survives this scoped verification.

**Still-required gates, separate from design defects:**

- **Orchestration:** P2b, §6.8, and GF-29/GF-30 must demonstrate fresh execution, operation/target enforcement, stale-plan handling, direct filenames, forced reruns, immutable reuse, and honest partial dry-runs.
- **Preparation portability:** GF-31 must compare actual prepared forcing and result-affecting TOML settings after removing access to original stores/catalogs, covering CHIRPS, CHIRPS-global, non-CHIRPS elevation, and E-OBS PET.
- **Result integrity:** GF-10 must exercise missing, duplicate, extra, and invalid-value cases during fresh and metrics-only publication.
- **Scientific acceptance:** GF-15 requires prior approval of numerical criteria, then the complete seeded benchmark and translation diagnostics. Screening-policy validity remains unestablished regardless of benchmark success.
- **Migration and integration:** GF-9, GF-27/GF-28, the rapid execution, documented repository checks, and separate stage acceptance records remain required under §12.4.

The historical Class-B fit-interval deferral remains a distinct **G2 owner ruling**. This approval neither closes nor ratifies it.