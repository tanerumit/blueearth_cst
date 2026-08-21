# External review brief — R13 config modularization (blueearth_cst), round 1

## Role

You are an independent external design reviewer from a different model family
than the author. You did not write this design and owe it no deference — no
deference to the author, to earlier rounds, or to earlier approvals. Your
value is adversarial pressure: challenge framing, feasibility, and
completeness. Do not copyedit prose.

## Task

Review exactly one document:

- `C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2\dev\working\design-runs\config-modularization\design-v2.md`

Orientation (neutral): the repository is a Snakemake-driven climate-stress-test
toolbox (Python/R/Julia; four workflow entry-point Snakefiles reading one
`--configfile` YAML). The design (milestone R13) restructures the configuration
surface: one project config (T1) holding `project:` + `shared:` plus a closed
`{enabled, config_path}` stanza per workflow, one per-workflow config file (T2)
referenced by path and composed by the shared loader, model configs unchanged,
and a separate toolbox-level `advanced_settings.yml`. It is version 2, revised
against a 52-finding internal panel; the document embeds finding IDs
(risk-*/arch-*/repofit-*) and decision IDs (D-x.y). This round is CLEAN-ROOM:
review the design document only — you do not receive the panel's files or the
ledger, and your judgment must be your own.

**Settled framing — out of scope for your review.** The repository owner has
ruled, at the run's framing gate (G1, 2026-08-20):

1. Composition is by path reference with a single `--configfile` CLI contract:
   T1 closed `{enabled, config_path}` stanzas + per-workflow T2 files, composed
   by the loader, with the in-memory config shape presented to the Snakefiles
   unchanged. (Alternatives such as CLI multi-configfile merge were considered
   and rejected before this round.)
2. Workflow naming: Candidate A — keep the current workflow names
   (`analyze_climate`, `build_model`, `analyze_projections`, `run_stress_test`).
   Provisional; final ratification at the approval gate.
3. Migration posture: clean break — an unmigrated config fails at parse time
   with an actionable message; no dual-mode loader; a report-only
   `split_project_config.py` migration script.
4. This work is milestone R13; `advanced_settings.yml` remains a separate
   authority-bounded toolbox file (constraints/runtime pins never move into
   user-editable files).

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
    doc_version: design-v2.md

    ## Findings
    ### ext1-<seq>  [blocking | major | minor]
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
