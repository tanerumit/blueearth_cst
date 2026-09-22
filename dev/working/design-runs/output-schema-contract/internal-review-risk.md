---
verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: blocking
    section: "10.3 Rerun; 10.7 Collection, simulation and metric identity sketches"
    finding: >-
      Metric identity cannot satisfy the stated path-adjustment invariance with
      the specified digest. Section 10.3 regenerates path-bearing execution
      TOMLs in a fresh rerun target and says those adjustments do not change
      scientific identity. Section 10.7 requires exact TOML hashes in the full
      response inventory, hashes that entire record except its self-digest,
      and includes the resulting response_inventory_sha256 in metric_set_id.
      Changing an absolute execution path therefore changes metric_set_id even
      when simulation identity, native response values and scientific selectors
      are unchanged.
    rationale: >-
      This is a direct contradiction between the identity promise and its
      prescribed calculation, rather than an untested implementation detail.
      Renaming or relocating a rerun target can create a scientifically distinct
      metric identity solely through execution evidence. The predecessor
      response_inventory.py already places toml_sha256 inside native_selector
      and hashes the complete inventory; retaining that mechanism does not meet
      the new path-neutral identity claim.
    suggested_fix: >-
      Define a versioned scientific response-inventory projection for the
      metric identity, retaining exact TOML and full-inventory hashes as checked
      evidence. Bind all scientific response, selector, transformation and clock
      semantics in the projection. Add a fixture with identical native responses
      and semantics but regenerated TOMLs in two fresh project roots; scientific
      IDs must match while evidence hashes differ. Weakening the identity promise
      instead would change a selected constraint and must return to G1.
  - id: risk-2
    severity: major
    section: "10.5 Static plan; 10.7 Collection identity and reuse"
    finding: >-
      The closed plan schema does not settle which intent is pinned on
      reuse_ready when current request evidence differs from the preserved
      creator evidence. Sections 10.5 and 10.7 deliberately allow locator,
      comment and explicit-versus-auto differences to select one collection,
      while requiring the original intent/archive to remain unchanged. Yet the
      plan and receipt have a single intent_sha256, plan documents must equal
      intent documents, and initialization is described through archive/intent
      installation without a reuse-specific binding rule.
    rationale: >-
      A comment-only configuration edit or equivalent explicit seed can produce
      different full intent documents with the same collection_id. One reasonable
      implementation would compare the candidate full intent with the creator
      and reject valid reuse; another would pin current evidence while claiming
      that hash identifies the preserved creator intent. The latter breaks the
      receipt-to-artifact chain. The existing invocation-local archive policy
      provides the necessary place for attempt evidence but does not define this
      equality boundary.
    suggested_fix: >-
      Specify the reuse branch explicitly: identify whether plan.intent and the
      receipt intent_sha256 bind the validated creator intent, and separately
      identify the current candidate projection/evidence used to prove semantic
      equivalence. State the exact full-document and semantic comparisons and
      prohibit installation into a ready creator archive. Test two requests with
      different full evidence and one collection ID, verifying both successful
      reuse and truthful attribution of current versus creator evidence.
  - id: risk-3
    severity: major
    section: "10.3 Archive transaction recovery"
    finding: >-
      The recovery table defines rollback and unpublished outcomes, but the
      closed journal state enum contains only prepared, old_detached,
      new_installed and committed. Rollback records abandonment only in
      invocation diagnostics; it does not specify a terminal journal transition
      or journal removal. The first-publication unpublished case has the same
      gap. Readers are required to recover or refuse every unfinished transaction.
    rationale: >-
      After restoring a valid previous archive, a second reader can still see
      the unfinished journal and repeat recovery or refuse it. A subsequent
      writer has no defined rule for superseding that journal while diagnostic
      staging is retained. Thus a successful recovery is not yet guaranteed to
      return the archive to an ordinary readable and writable state. This is
      especially consequential for the selected latest-only WF0-WF2 lifecycle,
      where replacement is normal.
    suggested_fix: >-
      Define the durable terminal representation of rolled-back and unpublished
      transactions, including retained staging ownership and the admission rule
      for the next publication. Test recovery followed by a second reader,
      another recovery pass, and a new writer; the same interruption must not
      leave permanent unfinished state or discard preserved diagnostic evidence.
  - id: risk-4
    severity: major
    section: "10.3 Exact source capture; 10.5 Plan pin and execution"
    finding: >-
      The contract guarantees immutable captured configuration buffers, but
      does not establish the equivalent consumption boundary for the scientific
      files that determine the plan and seed. Section 10.5 checks every declared
      source before initialization, then says generated inputs use the captured
      snapshot. It does not say whether historical_climate and basin_cells are
      immutable staged bytes actually read by R, or live files reached through
      the generated YAML. A project OS lock excludes cooperating launches, not
      edits to external or otherwise unowned source files.
    rationale: >-
      A required scientific file can change after pre-initialization verification
      but before the provider opens it. With the live-path interpretation, the
      published seed/intent may describe the previously hashed bytes while the
      generated series used different bytes. Same-mtime pre-initialization tests
      do not exercise this interval. The design's exact-use claim is stronger
      than the stated verification point.
    suggested_fix: >-
      Define how the pin owns the actual scientific bytes throughout consumption:
      use verified immutable snapshots or an explicitly equivalent immutable
      input mechanism, and bind the provider's execution paths to those bytes.
      Add a mutation injected after initialization and before provider read;
      execution must consume the pinned bytes or refuse publication. Specify
      which actors the local lock protects against so this guarantee is not
      inferred from project-lock ownership alone.
---

The clean-output break, strict WF3 independence and unchanged digest-to-integer
seed formula are treated as settled framing. The principal claim examined is
that exact execution evidence can remain complete while scientific identity,
readiness and rerun resolution remain unambiguous.

Findings are ranked by damage to that claim. Risk-1 is a specified contradiction;
risk-2 through risk-4 are consequential contract gaps, not evidence that an
implementation has already failed. The review independently read the intake,
design and G1 record; it did not read the domain review or ledger. No scientific
runs or crash experiments were executed.

The explicit invocation coverage limits, unknown outcome after termination,
creator-versus-attempt archive policy, pointer-independent execution, immutable
ready outputs and separately authorized baseline transition withstand this lens.
The additive P4 boundary and explicit pre-P6 WF4 refusal make the intended phase
limitations visible; no additional phase-boundary finding is raised.

All recommended fixes preserve the selected architecture and scope. The only
scope-divergent alternative identified is weakening path-neutral scientific
identity in response to risk-1; that requires a G1 ruling, not an author-selected
revision. Runtime lock behavior, platform crash durability and scientific
comparison remain empirical obligations already identified by the design.
