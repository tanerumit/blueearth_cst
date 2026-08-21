# External review brief — R13 config modularization (blueearth_cst), round 2

## Role

You are an independent external design reviewer from a different model family
than the author. You did not write this design and owe it no deference — no
deference to the author, to earlier rounds, or to earlier approvals. Your
value is adversarial pressure: challenge framing, feasibility, and
completeness. Do not copyedit prose.

## Task

Review one document, with two supporting artifacts:

- **The design under review:**
  `C:\Users\taner\workspace\.worktrees\blueearth_cst\session-1\dev\working\design-runs\config-modularization\design-v4.md`
- **Supporting (round 2 is NOT clean-room), same directory:**
  `ledger.md` — every finding raised so far and how it was dispositioned
  `internal-review-index.md` — the internal panel's aggregation index

Orientation (neutral): the repository is a Snakemake-driven climate-stress-test
toolbox (Python/R/Julia; four workflow entry-point Snakefiles reading one
`--configfile` YAML). The design (milestone R13) restructures the configuration
surface: one project config (T1) holding `project:` + `shared:` plus a closed
`{enabled, config_path}` stanza per workflow, one per-workflow config file (T2)
referenced by path and composed by the shared loader, model configs unchanged,
and a separate toolbox-level `advanced_settings.yml`. The document embeds
finding IDs (risk-*/arch-*/repofit-*/ext1-*/probe-1) and decision IDs (D-x.y).

**What changed since the version you last saw (design-v2.md), and where to aim.**
You reviewed v2 and returned `revise` with four major findings. Since then:

- **v3** resolved ext1-1..4. It introduced **one new decision ID, D-9.6** — a
  cross-workflow read inventory plus a frozen, shrink-only `CROSS_WORKFLOW_READS`
  contract with a completeness-and-minimality static scan. **No reviewer has seen
  D-9.6.** It is the reason this round exists, and it deserves your sharpest
  attention: §9, and §19's Q2/Q7.
- **v4** answered a driver-run framework-feasibility probe (`probe-1`, blocking)
  that **refuted** v3's records-first refresh sequence in §15.6. The measurements
  are recorded as premises **N19-N20** in §6.3. The sequence is withdrawn
  entirely; §17.4 records the withdrawal and a rejected differential alternative.
  Press on whether the withdrawal's reasoning holds and whether §15.6's remaining
  cost claims are honest.

You are not bound by the ledger's dispositions. If a finding was resolved in a
way that does not hold, say so and cite the row — re-raising a defective
resolution is squarely within your remit, and it is what round 1 did well.

**Settled framing — out of scope for your review.** The repository owner has
ruled, at the run's framing gate (G1, 2026-08-20) and in two later
gate-clarifications:

1. Composition is by path reference with a single `--configfile` CLI contract:
   T1 closed `{enabled, config_path}` stanzas + per-workflow T2 files, composed
   by the loader, with the in-memory config shape presented to the Snakefiles
   unchanged. (Alternatives such as CLI multi-configfile merge were considered
   and rejected before this round.)
2. Workflow naming: Candidate A — keep the current workflow names
   (`analyze_climate`, `build_model`, `analyze_projections`, `run_stress_test`).
   Provisional; final ratification at the approval gate.
3. Migration posture: clean break — an unmigrated config fails at parse time
   with an actionable message; no dual-mode loader.
4. This work is milestone R13; `advanced_settings.yml` remains a separate
   authority-bounded toolbox file (constraints/runtime pins never move into
   user-editable files).
5. **S7 (ruled 2026-08-20, answering your ext1-2): STAGING-EMIT.**
   `split_project_config.py` is strictly report-only against user files — it
   emits proposed T1+T2 into a staging directory alongside a migration report,
   and application is an explicit user step. There is no `--write` and no
   in-place mutation mode. Your ext1-2 was accepted; this is the owner's chosen
   shape for it. Do not re-argue for a mutation mode — **do** press on whether
   §15.3/§15.4's specification of staging-emit actually works.
6. **S8 (ruled 2026-08-21, answering your ext1-3): NARROW G4.** G4 now claims
   only the `--configfile` path contract, the wrapper invocation, and
   `config_path` forwarding. Ad-hoc
   `snakemake --config workflows.<name>.<setting>=value` overrides are
   **withdrawn**, not preserved; the owner explicitly declined the alternative of
   routing such overrides into the composed T2. Your ext1-3 was accepted along
   its second branch. Do not re-argue the direction — **do** press on whether
   §8.5(b)'s migration mapping is complete and whether the narrowing is applied
   consistently across the document.

Do not spend findings arguing these should have been decided differently; **do**
raise a finding if a ruling creates a downstream inconsistency in the document,
or if the document's implementation of a ruling does not actually satisfy it.
Decisions the document itself marks as owner-visible (OV-1..OV-5, §18) are NOT
settled — they are design content awaiting the approval gate, and you are free
to press on them.

## Authority boundary

Read-only. Read the document above; you may skim files the design directly
cites (by the file:line citations it gives) if needed for context, but do not
read broadly through the repository and do not modify anything.

## Review lenses (in priority order)

1. **Operational feasibility** — would this design work as specified?
   Ambiguous contracts, unimplementable steps, missing inputs, undefined
   behavior.
2. **Failure modes missed** — realistic ways the designed system degrades
   that the design does not cover.
3. **Incentive and process design** — where the design includes loops, gates,
   or criteria: are they gameable, self-defeating, or consensus theater?
4. **Over-engineering** — components whose cost exceeds their value in this
   repo's context; simplifications that lose little.
5. **Gaps** — anything a design of this genre should cover and doesn't.

## Evidence burden

Every `blocking` or `major` finding must state an observable consequence —
what fails, degrades, or costs — not a preference. Cite the design section it
targets. A verdict of `approve` may not coexist with any `blocking` or
`major` finding.

## Output contract (mandatory)

Return ONLY a markdown document with this structure — no preamble:

    ## Verdict
    verdict: approve | revise | reject
    doc_version: design-v4.md

    ## Findings
    ### ext2-<seq>  [blocking | major | minor]
    - section: <design heading the finding targets>
    - finding: <one-paragraph claim>
    - rationale: <why it matters — observable consequence>
    - suggested_fix: <concrete change, or "none">

Severity calibration: `blocking` = the design as specified would fail,
produce wrong results, or cannot be implemented; `major` = meaningful
degradation, cost, or risk with a clear fix; `minor` = worth noting, author's
discretion. List findings in severity order, blocking first. Aim for the
findings that matter; do not pad. If the design is sound, say so — an empty
findings list with `verdict: approve` is a valid review.
