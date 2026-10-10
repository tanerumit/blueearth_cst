```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: major
    section: "3.2 One shared producer specification in two DAGs; 4.1; 5; 9.1"
    finding: >-
      Reference validation does not establish that WF0's retained annual map fields
      were prepared from the reference's current input bytes and preparation code.
      The design retains annual_climatology.nc as the rendered field source, adds
      new inputs and code digests to the reference producer, and prescribes rebuilding
      that producer after a same-mtime mutation. It does not specify corresponding
      field-preparation identity validation or invalidation for the retained WF0 fields.
    rationale: >-
      Start with completed WF0 outputs, change an extracted precipitation array while
      preserving its timestamp, then force the prescribed reference rebuild. The
      producer computes new extrema and hashes; WF0 compute can remain up to date
      according to its unchanged inputs' timestamps and parameters. The new JSON
      schedules rendering, its current-input validation succeeds, and old annual
      fields can be published with the new reference_id. Independently, replacement
      of catalog-backed ERA5 orography changes the proposed producer's declared input
      while the existing WF0 compute rule does not declare that file. Source PET
      fields can therefore disagree with newly computed historical reference PET.
      These freshness weaknesses predate the proposal; certifying a fresh shared
      reference beside stale displayed fields is the new failure of the proposed
      provenance claim. It can mislead the user into interpreting the discrepancy
      as scientific variation rather than mixed preparation versions.
    suggested_fix: >-
      Specify a matching per-source preparation identity for retained WF0 map fields,
      covering their consumed data, settings and preparation dependencies, and require
      the renderer to reject a mismatch before saving figures. Declare matching
      catalog/orography and code dependencies on the field-producing rule so ordinary
      changes rebuild both branches. For preserved-timestamp changes, document repair
      that regenerates the affected fields as well as the reference. Add an incremental
      acceptance case with existing WF0 outputs: mutate source bytes with preserved
      timestamps, rebuild only the reference, and require rejection; then perform the
      documented repair and compare fields against fresh preparation. Include a
      catalog-backed orography replacement case. Keep these identities in existing
      field/metadata products where feasible; changing artifact ownership or making
      WF0 mandatory would be a scope-divergent resolution requiring G1 return.
```

Reviewed design SHA256: `b3b6510335d863cfac447d18b56c1c291a7da6bbeaa488afc0d41317c4fb8e2d`.
Source pin: `22fbe441cef67db45130834eab87a31f8e3b6fc7`. Static review only; no execution proof.

The finding follows the split visible in `analyze_climate.smk:416` (compute inputs),
`compute_climate_diagnostics.py:46` (catalog-backed DEM loading), and
`diagnostic_render.py:150` (retained map-field consumption). Section 5 protects the reference,
but does not bind the consumed annual fields to that validated identity.

The approved viewport, pooling population, completeness correction and borrowed-variable roles remain
settled. Counts are correctly described as cells rather than independent samples. Owned-run locking and
atomic publication have bounded guarantees; unsupported direct concurrency is explicitly excluded.
Concrete orography qualification and whole-route hashing/reduction/validation cost remain implementation
evidence obligations, not demonstrated properties. The ordinary journey justifies the shared artifact and
portable drawing boundary; no broader framework or additional artifact is needed to address this finding.

Classification: one major interface/invalidation gap; no blocking finding or scientific estimand change.
The proposed fix preserves approved ownership and scope. A resolution changing either must return to G1.
