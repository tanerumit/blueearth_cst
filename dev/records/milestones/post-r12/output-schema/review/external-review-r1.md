## Verdict
verdict: revise
doc_version: design-v2.md

## Findings
### ext1-1 [major]
- section: §10.2 Types, versions and canonical digests; §10.7 Collection, simulation and metric identity sketches
- finding: Several records declared closed still contain undefined nested schemas or digest inputs, including `referenced_inputs`, `generated_inputs`, `rerun`, `simulator`, embedded simulation documents, plan output entries and `return_level_validation_sha256`.
- rationale: Independent writers cannot determine the same canonical object, ordering or H-versus-B operation. Readers also cannot enforce the stated fail-closed policy. Two implementations could produce different identities from equivalent inputs or accept an unclassified scientific field.
- suggested_fix: Define exhaustive schemas and canonical projections for every identity-bearing nested object, including required keys, ordering, null rules and digest operation. Version inherited predecessor payloads explicitly rather than referring only to their existing contents.

### ext1-2 [major]
- section: §10.5 Static plan, receipt, pointer and workspace exclusion; §10.7 Collection, simulation and metric identity sketches
- finding: The installed `weather_generation_input.yml` is byte-hashed but has no normative semantic equivalence check against the frozen plan and collection intent.
- rationale: A renderer or mapping defect could place a different seed, source snapshot or scientific setting in the YAML consumed by R. The resulting series could still be published with internally valid file hashes under a `collection_id` computed from different intended settings.
- suggested_fix: Define a closed semantic projection for the generated YAML. Parse the exact installed bytes and require that projection to equal the plan’s generation configuration, resolved seed and pinned source references before provider execution and again before publication. Validate output paths separately from scientific fields.

### ext1-3 [major]
- section: §10.6 WF3-only seed material and module contract; §10.9 Evidence, assumptions and acceptance
- finding: Settings excluded from seed and collection identity are classified by assertion, without an acceptance test showing that they cannot change decoded scientific outputs.
- rationale: In particular, changing `parallel` or `n_cores` could alter RNG streams, member ordering or generated values while preserving the same `collection_id`. The proposed matched-explicit-seed comparison does not require mutations across these excluded settings.
- suggested_fix: Add a mutation matrix for every excluded generator field. Require exact equality of decoded values, coordinates, masks, member associations and date selections for execution-only fields. Permit documented container-byte differences for encoding fields such as compression, and promote any field that changes scientific content into the seed and collection identity projections.