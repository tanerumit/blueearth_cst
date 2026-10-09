---
verdict: revise
doc_version: design-v1.md
findings:
  - id: arch-1
    severity: major
    section: "10.7 Collection, simulation and metric identity sketches; 10.3 Source capture, publication transaction and rerun"
    finding: >-
      The closed simulation ready marker binds only the intent and response inventory,
      and the closed intent contains no creator-archive reference. Unlike the collection
      marker, a simulation therefore has no specified readiness edge to its exact
      config/run_record.yml and source archive.
    rationale: >-
      Removing or replacing the experiment creator archive leaves every declared
      simulation-marker reference valid. The invocation has an archive reference, but
      no required traversal from the simulation marker to that creator invocation is
      specified. This makes the archive's integrity depend on an additional reader
      convention outside the selected closed contract, despite P0-01/P0-12 promising
      exact immutable creator evidence. The predecessor freeze_simulation writes its
      snapshot without making it part of simulation identity; the new contract must
      explicitly bind evidence without adding paths to scientific identity.
    suggested_fix: >-
      Add a checked archive FileRef to simulation/2, outside simulation_id, and make
      creator-archive verification a prerequisite of ready publication and reading.
      Test missing sources, changed run-record bytes and same-identity archive
      replacement. This completes the selected framing rather than changing it.
  - id: arch-2
    severity: major
    section: "10.2 Types, versions and canonical digests; 10.3 Source capture, publication transaction and rerun"
    finding: >-
      The rerun overlay stored in the new archive requires source_record:FileRef,
      but its predecessor run record is in the original project. FileRef permits
      only confined relative paths under the owning new project/experiment/record/
      request roots. No predecessor-project anchor or retained predecessor-record
      copy is defined.
    rationale: >-
      For a supported rerun from project A into fresh project B, the predecessor
      record cannot be addressed by the declared FileRef vocabulary without an
      absolute path, parent escape, arbitrary root, or an unspecified copy. Each of
      those conflicts with the stated reference rules or requires an additional
      publication step. external_mappings supplies locator adjustments but does not
      define how a FileRef's anchor changes. This is introduced by the proposed
      archived-rerun contract, not evidence of an existing runtime defect.
    suggested_fix: >-
      Specify how predecessor evidence is retained and anchored in the fresh target,
      or define a separate checked external-evidence reference with explicit binding
      and relocation rules. Choose one mechanism and test A-to-B rerun followed by
      relocation of B with A unavailable. Preserving the existing rerun and
      whole-project relocation promises stays within G1; dropping those promises
      would change settled framing and must return to the owner.
  - id: arch-3
    severity: major
    section: "8.5 Generated Wflow run settings and temporal evidence; 10.2 Types, versions and canonical digests; 10.7 Collection, simulation and metric identity sketches"
    finding: >-
      Native selectors must hold a checked reference to the temporal_preparation
      section of their own response inventory, but no local-section reference type
      is declared. The only declared section-reference type embeds a FileRef with
      the whole document byte hash.
    rationale: >-
      Using SectionRef here places the response inventory's own byte hash inside
      itself, creating a hash fixed-point requirement. Omitting that document hash
      instead violates SectionRef's closed schema and verification rule. Excluding
      response_inventory_sha256 from the inventory's self digest does not remove
      hashes nested in selector references. The current response_inventory.py stores
      separate temporal-file hashes at lines 306-307 and embeds the common object
      at line 340, so eliminating the files creates this new reference boundary.
    suggested_fix: >-
      Declare an intra-document reference containing only the permitted local JSON
      pointer and section digest, validated after the inventory's enclosing digest;
      reserve SectionRef for external documents. Freeze its exact selector keys and
      add canonicalization plus tampered-section fixtures. This preserves the
      selected single retained temporal object and does not change G1 framing.
  - id: arch-4
    severity: minor
    section: "4.2 Candidate run_record.yml; 10.4 Launch history and archive lifetime; 10.5 Static plan, receipt, pointer and workspace exclusion"
    finding: >-
      The timing of the exact generated weather-input YAML checksum needs one
      explicit step. The archive contains generated_inputs and must be installed
      before initialization emits its receipt, while the ordinary generation DAG
      is constructed afterwards. The existing YAML producer is a generation rule.
    rationale: >-
      In generate_scenarios.smk lines 171-183, prepare_weathergen_config renders the
      execution YAML separately from collection initialization at lines 242-263.
      An implementer must decide whether initialization now renders and installs
      that YAML before the archive, or whether the archive may be finalized later.
      The latter affects archive hashes and the promised installation boundary.
    suggested_fix: >-
      State that initialization renders the exact provider YAML from the frozen
      plan, installs it, and verifies its bytes before the creator archive and
      receipt are published, or specify an equally explicit finalization order.
      Add a failure-point check that no receipt references an unfinished archive.
      This is an ordering clarification within the settled framing.
---

Independent architecture/internal-consistency review. Read intake.md, design-v1.md,
status.md G1 framing, repository AGENTS.md, the scientific-workflows and
reproducible-computing skills, and the design-review-loop verdict/severity rules.
No other reviewer output or ledger was read.

The WF3-only module extraction, separately versioned seed projection, P4 additive
staging followed by the P5 switch and explicit pre-P6 WF4 refusal, final ready-marker
ordering, and separately authorized baseline transition are internally consistent
at the stated design level. Numeric auto-seed continuity is correctly not promised.
No finding requires reinstating WF4 dependencies, old-output compatibility, resume,
distributed ownership, or baseline regeneration.

Verification was read-only source inspection of generation_plan.py,
scenario_provider.py, content_identity.py, response_inventory.py,
simulation_record.py and generate_scenarios.smk. No runtime tests or numerical
validation were executed. Shell process startup failed; filesystem reads and this
review-file write used node_repl. No design, runtime code, output tree, or other
review artifact was modified.
