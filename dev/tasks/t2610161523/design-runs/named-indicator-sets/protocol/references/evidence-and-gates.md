# Evidence and gates

Three stage-0 obligations and one handoff obligation, all aimed at the same
failure: a loop that reviews *prose* while the facts, the method, and the gates
it depends on go unchecked. Load at stage 0, and again at the stage-7 handoff.

Stage semantics: `stage-contracts.md`. Grading and closure:
`findings-and-closure.md`.

## Evidence register (stage 0, refreshed at G1)

`intake.md` carries a register of the **empirical premises the design leans on**
— every claim about the repo, the data, or an external store whose falsity would
change a decision. One row each:

| Premise | Source | Exact observation | Precision | Reproduction | Confidence |

Rules:

- **Record the measured delta, never an unqualified identity claim.** "The two
  regions are identical" is not an observation; "max |Δ| = 4e-7 deg over 5
  vertices, compared at 6 dp" is. An identity claim with its tolerance suppressed
  is the one premise class no reviewer can check.
- **Independent reviewers do not give independent evidence.** Every reviewer
  inherits the draft's premises, so a shared false premise survives model
  diversity intact — two vendors agreeing tells you nothing about a fact neither
  re-measured. The register, not the panel, is what protects against this.
- Where a premise is expensive to settle, record it as a **hypothesis with the
  observation that would settle it**, and let a reviewer price the uncertainty
  rather than inherit a guess.

### Premise dispositions (stage 1b)

The register is not only a record; it is the domain lens's checklist. Where
stage 1b runs, the domain reviewer receives the register and returns one
disposition per row:

- `supported` — the observation as recorded justifies the premise for this
  design's purpose;
- `contested` — the premise is wrong, or right only under a condition the
  design does not state → a finding, graded on consequence;
- `untestable as stated` — the row records a belief rather than an
  observation → a finding naming the measurement that would settle it, so the
  author or driver can take it before the next decision gate.

Rows still `contested` or `untestable` after revision require a named
decision-critical observation, targeted verification within budget, or an
owner ruling before G2. An unresolved scientific premise cannot be accepted
by budget exhaustion. A whole-document round is not automatic.

## Domain-content flag (stage 0)

`intake.md` records whether the design carries **domain-scientific content**:
a method choice, a physical or statistical assumption, a data treatment
(aggregation, bias adjustment, gap filling, resampling), an uncertainty claim,
or a validation claim about a modelled or measured quantity. Set it by content,
not by repo: a scheduler refactor in a hydrology repo may carry none, and a
"pure plumbing" change that alters what a downstream statistic sees carries it.
`yes` makes stage 1b mandatory in every shape of the loop and briefs the
  external review as a domain referee; `no` waives stage 1b with the reason logged in `status.md`, and
the settled-framing block tells the external reviewer to omit that lens. When
in doubt, set `yes` — one lens dispatch is cheaper than a converged design that
answers the wrong question.

## Framework-feasibility probes (stage 0/1)

A mechanism whose feasibility depends on **framework execution semantics**
gets a probe only when the result could change the design choice. At intake,
name at most two decision-critical probes, their scope, expected observation,
and stop condition. Direct probes count against this bounded list even when
they use no agent. Mechanical formatting/schema repair has a separate limit:
one scoped repair and recheck per failed deterministic check or stage; a
repeated failure goes to the owner. More probes require an owner-scoped
continuation. Record actual results; do not replace an experiment with prose.

Probe candidates: caches and skip-on-valid paths, resume and idempotence claims,
"no-op by design" behaviour, anything asserting an absence (no network, no
re-download, no job).

## Gate materialization (stage 0)

List each gate in the design's migration or validation plan. Distinguish a
pre-change evidence requirement from a future implementation acceptance check:

- **Runnable now** — name the command when present.
- **Needs a pre-change artifact** (a reference tree, a snapshot, a recorded
  baseline): create it **before implementation changes the measured state**.
  A later commit boundary is too late if working-tree edits have already
  destroyed the baseline. Record the captured version and producing command.
- **Implementation check** — specify the future command or observation and
  acceptance condition; current availability is not required.
- **Runnable but thin** — state the missing coverage and its consequence; widen
  the plan or present eligible risk to G2. A green result cannot claim more
  coverage than the check provides.

## Claim → falsifier at the handoff (stage 7)

Design convergence is not implementation assurance: a converged design has been
argued, not executed. Retain, for **each runtime property the accepted design
claims**, the observation that would falsify it and the command that produces it.
Keep the mapping in the existing design or run handoff record; do not modify
approved bytes to add it after G2. When an implementation assignment is requested
or required by the invoking workflow, `task-brief` carries that mapping into its
validation section. Otherwise link the existing record when authorized implementation
continues. `testing-policy` and project rules own check selection and frequency.

