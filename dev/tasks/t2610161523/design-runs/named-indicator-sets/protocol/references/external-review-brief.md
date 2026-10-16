# External review brief — canonical template

Instantiate the fixed contract once at first external dispatch as `review-brief.md`; preserve its
role, lenses, evidence burden and output contract. Before every dispatch record settled framing
verbatim in the existing `status.md` body, from every applicable G1/return/arbitration ruling;
supply that block with the contract. Framing is status state, never refreshed brief prose.
Re-read orientation facts affected by rulings before dispatch.

Round number, concrete document path, conditional ledger/index inputs and framing are filled at
dispatch. A second full-document round requires an explicit owner-approved continuation with
its unresolved design question, scope, and limit; it never follows automatically from a verdict.
When immutable dispatch-specific overrides are needed, create a conditional
`review-brief-r<N>.md` supplement labelled with overridden slots and effective order. Record
path/SHA256 for every effective component in status: fixed brief plus supplement. The supplement
may override round/document/schema slots explicitly; preserve the severity/verdict contract.
The same severity/verdict contract is supplied to internal reviewers.

Before modifying any digest-cited brief or sketch, verify a pinned commit retrieves exact cited
bytes. Otherwise first create and verify an immutable `review-brief-r<N>.md` or
`scoping-g1-<k>.html` pre-edit snapshot, using the next unused suffix, and record path/hash in
status. Preserve prior snapshots. This recovery trigger is mandatory before editing, including
between rounds without an intervening commit. A digest alone is insufficient; dispatch requires
no pre-gate commit, while ordinary authorized commits remain allowed. Closure must recover every
gate/dispatch digest's bytes in the pinned run, including outside-run sketch bytes preserved there.
Use `run-artifacts.md` for inventory, acceptance and closure retention.

Dispatch mechanics, read-only isolation, and capture belong to
`workflow-driver`'s supported adapter; this file owns only the review
contract. Select the adapter only after checking independence from the author.

The severity definitions and verdict-consistency rule embedded in the
template mirror `findings-and-closure.md` § Severity definitions, which is
canonical — when either changes, update both together.

---

```markdown
# External review brief — <design name>, round <n>

## Role

You are an independent reviewer who did not author this design. The driver
records whether your model family differs from the author's; an owner-approved
same-family fallback is labelled `single-family`. Challenge the method,
evidence, feasibility, and completeness. Treat owner-approved framing as
settled unless new consequential evidence changes its basis. Do not reopen
preferences or copyedit prose.

## Task

Review exactly one document:

- `<absolute path to the latest design-vN.md>`

<one-paragraph orientation: what the design is for, in neutral terms — do not
argue for it. State facts a gate ruling may have changed (commit count, scope,
selected alternative) in dispatch framing or an explicitly identified immutable supplement>

**Settled framing — out of scope for your review.** <supplied verbatim from the dispatch's
`status.md` record, covering every ruling to date — G1, any gate return, and any
arbitration. List each ruling in one line, by content rather than by question ID,
since the ID grammar in `status.md` need not match the design's own numbering.>
Do not spend findings arguing these should have been decided differently; **do**
raise a finding if a ruling creates a downstream inconsistency in the document,
or if the document's implementation of a ruling does not actually satisfy it.
Test the user outcome, ordinary end-to-end journey, meaningful alternatives
including the smallest useful change, and actor/artifact boundary in every
design. Does each stage serve a confirmed need, and would a simpler boundary
meet the same outcome? Report a mismatch and consequence as a framing issue
for the driver's G1 return rule; do not override a ruling.

<initial review: omit the block below — clean-room review>
<owner-approved additional full review only:>
Also read, after forming your own view of the design:

- `<path to ledger.md>` — dispositions of every prior finding
- `<path to internal-review-index.md>` — the internal panel's findings

**Regression duty:** verify that findings marked resolved are actually
resolved in this version, that no accepted fix introduced a new defect, and
that rejections' rationales hold. Re-raise anything that fails — your earlier
findings may be withdrawn only by you, here.
</owner-approved additional full review>

## Authority boundary

Read-only. Read the files listed above; you may skim files the design
directly cites if needed for context, but do not read broadly through the
repository and do not modify anything.

## Review lenses (in priority order)

<domain content = yes: apply scientific validity first, then the other lenses
where consequential; retain the mandatory outcome/journey/alternatives test>
<domain content = no: apply lenses 2–5 and the mandatory decision test>

1. **Scientific and methodological validity** — is the method appropriate to
   the question, the data, and the decision it serves; do the physical,
   statistical, or modelling assumptions hold for this system; is uncertainty
   carried through or silently discarded; can the stated validation falsify the
   design's claims? A design that executes flawlessly and answers the wrong
   question, or rests on an assumption that does not hold here, is `blocking`.
2. **Operational feasibility** — would this design work as specified?
   Ambiguous contracts, unimplementable steps, missing inputs, undefined
   behavior.
3. **Failure modes missed** — realistic ways the designed system degrades
   that the design does not cover.
4. **Over-engineering** — components whose cost exceeds their value in this
   repo's context; unnecessary stages or artifacts; simpler ownership boundaries
   that preserve the confirmed outcome.
5. **Gaps** — anything a design of this genre should cover and doesn't.

## Evidence burden

Every `blocking` or `major` finding must state an observable consequence —
what fails, degrades, or costs — not a preference. Explain the effect on the
selected alternative, user journey, public contract, scientific validity, or
material feasibility, and why the matter cannot safely wait for implementation.
Cite the design section it targets. Put implementation-only concerns in an
acceptance-check recommendation. Your `suggested_fix` is a proposal; the author
may satisfy the underlying requirement another way. A verdict of `approve`
may not coexist with any `blocking` or
`major` finding.

## Output contract (mandatory)

Return ONLY a markdown document with this structure — no preamble:

    ## Verdict
    verdict: approve | revise | reject
    doc_version: <the design-vN.md you reviewed>

    ## Findings
    ### ext<n>-<seq>  [blocking | major | minor]
    - section: <design heading the finding targets>
    - finding: <one-paragraph claim>
    - rationale: <why it matters — observable consequence>
    - suggested_fix: <concrete change, or "none">

Severity calibration: `blocking` = the design as specified would fail,
produce wrong results (including: rests on a domain assumption that does not
hold for this system or data, or answers a question other than the one posed),
or cannot be implemented; `major` = meaningful
degradation, cost, or risk with a clear fix; `minor` = worth noting, author's
discretion. List findings in severity order, blocking first. Aim for the
findings that matter; do not pad. If the design is sound, say so — an empty
findings list with `verdict: approve` is a valid review.
```
