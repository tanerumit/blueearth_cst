## Verdict
verdict: revise
doc_version: design-v2.md

## Findings
### ext1-1  [major]
- section: 5. Settled framing (owner rulings — not reopened); 19. Open questions
- finding: The design does not fully implement S4. Q2 acknowledges that an existing cross-workflow read—WF3 reading `workflows.build_model.wflow_outvars`—remains governed only by `guarded_sections`; the loader cannot detect that a key stored in one T2 is read by multiple workflows. Thus the claimed parse-time shared-seam enforcement has a known exception.
- rationale: `wflow_outvars` can remain coupled to the WF1 file while affecting WF3 behavior. Replacing or editing the WF1 T2 can therefore alter WF3 outputs without violating any loader check, contrary to G2/S4 and the promised workflow-module boundary.
- suggested_fix: Inventory existing cross-workflow reads, hoist every multiply-read key—including `wflow_outvars`—to T1, and add an explicit checked cross-workflow-read manifest or equivalent test so future reads cannot bypass S4.

### ext1-2  [major]
- section: 18. Consequences and risks
- finding: The proposed `split_project_config.py --write` mode contradicts the settled clean-break posture, which specifies a report-only migration script. An opt-in mutation mode is still not report-only.
- rationale: Implementing the design as written gives the migration utility authority to rewrite user-owned configuration and create T2 files, exposing comments, formatting, or partially migrated projects to mutation despite the framing gate expressly withholding that authority.
- suggested_fix: Remove `--write`. Have the script validate and emit a migration report plus proposed file contents or a patch, leaving application to an explicit user-controlled step outside the script.

### ext1-3  [major]
- section: 2. Goals / Non-goals; 18. Consequences and risks
- finding: G4 says the CLI contract remains unchanged, but the negative consequences explicitly state that workflow-setting overrides supplied through `snakemake --config key=value` will become parse-time errors. That is a user-visible CLI behavior change not covered by the settled clean-break ruling about config-file shape.
- rationale: Existing automated or exploratory invocations that override workflow settings without editing YAML will fail after migration, even when their T1/T2 files are otherwise valid. The design therefore overstates compatibility and leaves those users without a mechanical replacement.
- suggested_fix: Either specify how supported workflow overrides are routed into the composed T2 section before validation, or narrow G4 explicitly and add an actionable migration mapping for every formerly supported override form.

### ext1-4  [major]
- section: 18. Consequences and risks — Owner-visible at G2
- finding: OV-2 offers `snakemake --touch` as a shortcut around the post-migration WF3 cascade without establishing how the expected new composed snapshots and provenance records are regenerated first. Touching planned outputs changes timestamps, not their contents.
- rationale: A completed experiment can remain associated with old monolithic snapshots or stale configuration digests while Snakemake treats its products as current. Subsequent drift checks may fail, or—worse—the retained run record may claim configuration inputs that no longer correspond to the current T1/T2 set.
- suggested_fix: Remove the shortcut unless the design defines and tests a bounded sequence that first regenerates all affected configuration snapshots and provenance records, proves pre/post effective-configuration equivalence, and touches only downstream computational products.