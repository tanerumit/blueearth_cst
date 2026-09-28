verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: major
    section: "6.1 Historical evaluation; 6.2 Selection and experiment binding"
    finding: "G1 framing-level: selection ignores the fitness-for-purpose verdict."
    rationale: >-
      The assessment has structural/runtime, evidence-adequacy and fitness
      verdicts, but WF4 selection requires only structural/runtime acceptance
      and a rationale. An assessor could find a revision unfit for first-order
      CST and it could still be selected. Successful execution and an acknowledged
      limitation do not establish defensible hydrological response.
    suggested_fix: >-
      Define how each verdict governs selection. Require affirmative
      purpose-specific fitness for ordinary selection. If evidence is limited,
      define a narrower exploratory use, required process and forcing checks,
      prohibited claims and explicit assessor acceptance. A negative fitness
      verdict must not count as an ordinary selectable result.
  - id: domain-2
    severity: major
    section: "6.1 Historical evaluation; Validation and acceptance criteria"
    finding: "G1 framing-level: scientific acceptance lacks a benchmark and numerical uncertainty plan."
    rationale: >-
      The design names metrics and hydrographs but does not require a naive
      benchmark, regime-stratified numerical results or uncertainty bounds for
      improvement and fitness claims. Aggregate KGE/NSE can improve while drought
      or flood behavior worsens. Short, serially dependent records and discharge
      measurement error can make a small score difference inconclusive. Current
      falsifiers chiefly test attribution and grouping, not hydrological adequacy.
    suggested_fix: >-
      Require a prespecified purpose-specific protocol: eligible stations and
      periods, a defensible naive reference such as seasonal discharge
      climatology plus the automated/parent model, decision-relevant metrics,
      and seasonal/high-flow/low-flow diagnostics with counts. Specify an
      uncertainty method and assumptions, such as hydrological-year block
      bootstrap of paired score differences and observation-error sensitivity.
      Report numerical intervals when supported and insufficient evidence
      otherwise. Add a falsifier where aggregate skill improves but a relevant
      regime or benchmark fails.
  - id: domain-3
    severity: major
    section: "6.1 Historical evaluation; Validation and acceptance criteria"
    finding: "G1 framing-level: same-protocol improvement may still be an observation-guided development result."
    rationale: >-
      The protocol hash controls forcing, stations and period, but it does not
      distinguish scores on repeatedly inspected observations from held-out
      scores. Picking the best of several expert revisions against one record
      can improve that record by search alone. The prose recognizes this, but
      the comparison export and falsifier do not enforce the distinction.
    suggested_fix: >-
      Freeze a purpose-matched temporal or spatial development/held-out split
      before comparisons when independent validation is claimed. Label each
      score development, held-out or exploratory, use identical paired timestamps
      and station support, and retain all tried revisions. Test that a repeatedly
      observation-guided gain cannot be reported as independent validation.
      Where holdout is unavailable, allow development comparison but withhold
      the independent-validation claim.
  - id: domain-4
    severity: minor
    section: "Intake evidence register row 5; 4.3 Identities and seal contents"
    finding: "The existing runtime digest cannot completely capture direct edits."
    rationale: >-
      model_digest.py hashes TOML and path-key targets; unreferenced geometry
      and provenance are omitted. The design correctly adds a full seal inventory,
      so this corrects a premise rather than the proposed seal.
    suggested_fix: >-
      State explicitly that the hypothesis is false for complete direct-edit
      identity. Settle it by adding, editing and deleting an unreferenced file:
      the runtime digest should stay equal while the full seal changes. Separately
      confirm all actual Wflow inputs are covered by runtime reconciliation.
  - id: domain-5
    severity: minor
    section: "Intake evidence register row 6; 4.2 Parentage and editing"
    finding: "HydroMT separate-output parent preservation is not yet demonstrated for this invocation."
    rationale: >-
      The vendored guide documents -o, but no execution establishes that a
      representative update with the pinned plugin preserves parent bytes and
      produces a complete, runnable child. The design already identifies this
      as a probe rather than a demonstrated fact.
    suggested_fix: >-
      Keep the probe as a pre-integration gate: hash the parent before and after
      a native update into an independent draft, inventory the child, verify
      changed config and components, load it with pinned HydroMT and run Wflow.
      A changed parent or incomplete child requires narrowing supported recipes
      or revising the procedure.

## Scientific strengths

- The design distinguishes runtime identity, full revision attribution and scientific validity; it does not infer model quality from a hash or successful execution.
- It freezes forcing, observations, mapping, period and metric definitions, and separates changed forcing or station support from unqualified comparisons.
- It records observation-guided edits, recognizes the need for held-out evidence for independent validation, and retains native responses and limitations.
- Its opt-in revision boundary preserves the automated assessment and direct-edit snapshot without describing either as calibrated or guaranteed recipe-replayable.

## Evidence-premise dispositions

| Intake evidence-register premise | Disposition | Basis / settling observation |
|---|---|---|
| WF1 has an in-place writer chain and terminal reader anchor | supported | `build_model.smk` rule 1.09 declares `.model_final`; downstream readers declare it through `ancient()`. This is source-level evidence, not a runtime race test. |
| WF1 run record is current-only and its hashes are not model-byte identity | supported | `copy_config_files.py` `_RUNS_README` says the record is replaced and that `configuration_inputs_sha256` omits scientific dataset identity. |
| Model digest uses TOML and pointer-derived runtime inputs | supported | `model_file_set()` walks path-valued TOML keys; `model_digest_entries()` hashes targets or records `ABSENT`. This does not establish coverage of every actual engine input. |
| WF4 binds one fixed model root and guards drift | supported | `simulate_and_metrics.smk` fixes `basin_dir`; `write_model_reference.py` records relative path, digest and input entries and refuses a changed existing reference. |
| Existing pointer digest completely captures direct edits | contested | Unreferenced files are outside its set. The full-seal versus unchanged-runtime-digest probe in domain-4 settles the distinction. |
| HydroMT separate output preserves an intact parent | untestable as stated | Vendored documentation supports the command syntax, not behavior of this pinned invocation. The before/after parent inventory and runnable-child probe in domain-5 settles it. |

The proposed workflow is a defensible provisional provenance design, subject to the three major scientific gate changes above. It cannot yet support ordinary fitness selection from a successful historical run or aggregate improvement alone. Historical evidence will retain forcing, observational, structural and climate-transfer uncertainty even after those gates are added.
