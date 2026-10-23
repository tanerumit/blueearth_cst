# Delegated skill-loading investigation

Working evidence, 2026-10-23. This record supports the open task; it does not establish runtime adoption.

## Original trace

Inspected the local Claude project transcript for conversation
`eafeaedc-56d8-45d5-ad9e-bafec530c3f3`, under the session-2 project in `.claude/projects`.
Only timestamped message events were counted; duplicated nested tool records were excluded.

- The handoff explicitly requested the full canonical technical-writer role and applicable bound skills,
  including the external-first resolution rule. Missing role identity was not the immediate problem.
- At 22:10:43 UTC on 2026-10-22, a Read call requested the canonical technical-writer role without a limit.
- At 22:11:11, Bash requested scientific-software-documentation through `head -120`, testing-policy and
  writing-feedback-revision through `head -60`, project-system through `head -90`, and Herdr through
  `head -60`. These are explicit caller-selected limits, independently of possible output truncation.
- At 22:11:15, project-reference-docs was requested from line 40 for 150 lines. At 22:11:18, Herdr was
  requested through line 80 and testing-policy was searched for selected keywords.
- The first documentation edit followed at 22:11:33.
- Following coordinator correction, at 22:12:33–35, Read calls requested testing-policy,
  scientific-software-documentation and writing-feedback-revision without explicit limits, Herdr from
  line 80 onward, and the first 40 lines of project-reference-docs.

This establishes deliberately partial initial requests. It does not prove complete delivery or application
of the later reads. A full project-system recovery read was not found among the inspected skill calls.
Historical file lengths and tool-result coverage still need reconciliation before claiming exact omissions.
The original failure is observed; independent reproduction remains pending.

## Interpretation and candidate correction

The current canonical technical-writer contract contains the relevant skill bindings. Current
agent-routing guidance already requires full role activation and application of bound skills. Inspecting
current files does not prove their exact historical bytes; do not attribute a projection defect from this alone.

The narrow candidate is a handoff clarification in agent-routing, subject to a successful comparison:

> Before the first edit, read each applicable SKILL.md body completely. Use consecutive bounded reads
> when output is truncated; selecting headings or initial lines does not complete the read. Load linked
> references only when their triggers apply. Report any governing body that remains incomplete.

Prefer testing this sentence in a temporary assignment over changing every role or adding a loading framework.
Shared guidance belongs to infrastructure:artifacts/skills/agent-routing/SKILL.md. This task explicitly
does not authorize editing that repository. No shared change has been made.

## Bounded comparison

Use an allocated session and two sequential fresh Claude conversations with the same resolved model,
effort, role, governing files and small documentation assignment. Keep writes confined to task scratch;
disable nested delegation, commits, landing and global configuration changes. Preserve the original task's
role-loading wording in the control; add only the candidate sentence in the treatment.

For each run, inspect actual tool requests and delivered results before its first edit. Record applicable
skills, requested and delivered line coverage, truncation recovery, omitted obligations and checks. Use
file lengths or hashes from the run, not later copies. Report behavior of these two runs without a
general model comparison or causal claim about effort. A treatment pass supports a bounded follow-up,
not a universal fix; repeat only if ambiguity materially affects the proposed guidance change.

The user allocated session-2 on 2026-10-23. Both trials below are complete; shared adoption is pending.

## Fresh comparison results

Both trials used session-2 at `d0802bf054fbb5e0849ec688f6c147300cf2ce9d`, branch
`chore/t2610230016`, and its existing designated Herdr agents pane. Two workers ran sequentially,
with no nested delegation. The coordinator selected technical-writer and instructed canonical role loading;
both traces show that role read. Both fresh startup screens and preflight turns were checked. The runtime
reported Claude Code 2.1.309, Sonnet 5.5, medium effort. The original incident was on 2.1.308, so this is a
current-runtime reproduction, not an exact historical replay. No model or effort comparison was performed.

The exact common assignment is [comparison-prompt.txt](comparison-prompt.txt), replacing `/RUN.md` with
the relevant scratch filename. Treatment appended only the candidate paragraph above. Each scratch copy
started identical to the maintained workflow reference. The control file remained present during treatment;
the assignment prohibited inspecting it and no such read appears in the inspected trace. The task/status
context identified this investigation, so the trials were not blinded. No global settings were changed.

| Trial | Conversation | First skill-body request UTC | First edit UTC |
|---|---|---|---|
| Control | `f946557b-23f3-4b35-af86-42532f3ac1cc` | 17:12:19 | 17:12:41 |
| Treatment | `e821b4da-d12b-4945-b58a-2bb64bed30ee` | 17:14:18 | 17:14:42 |

Times are 2026-10-23. Local transcripts remain under the session-2 `.claude/projects` directory, named
by conversation ID. Control's skill request was tool `toolu_01NhuFK1x7rJD5mWpLG1egJS`; its returned text
was compared against the current canonical first 90 lines for each file. Treatment's four Read results
were parsed by line number and compared with every source line; all matched. SHA-256 values captured
before treatment matched those used for the delivered-text comparison.

| Governing body | Source lines | Control delivered | Treatment delivered |
|---|---:|---:|---:|
| project-reference-docs | 98 | 90 | 98 |
| scientific-software-documentation | 127 | 90 | 127 |
| writing-feedback-revision | 119 | 90 | 119 |
| testing-policy | 154 | 0 | 154 |

These four bindings apply to revising a maintained documentation reference and selecting its checks.
Project placement was prescribed; no new placement/lifecycle decision required project-system.
The document discusses Herdr but workers were not assigned to control it, so no Herdr binding was required.
No source-line mismatch or truncation was found in the treatment body results. The control's complete
tool trace contained no later body-completion reads. This establishes caller-selected partial loading;
it does not establish why the model chose that strategy.

Source SHA-256 values:

```text
project-reference-docs          6710CF8E5BCB1DB73673550E3C4D7D83C38ACDC261188BBAAB0E4D4688B608FF
scientific-software-documentation 015B60E5E95284142B50824DC359A85DB95186E15DFF99B4B75B4EB512267E56
writing-feedback-revision      41358256865EA9C5E16669733B80E80D5660E95AEAAE367130DD7DFF1714E8D0
testing-policy                 DC25DDECACF6B6FB6A52BBAE8F193210586BD97B2C8349C265D15CEFB8EE97D1
```

### Remaining failure and recommendation

Treatment fully loaded the four bodies and the scientific documentation task-guide reference. However,
it did not load writing-feedback-revision's `references/revision.md`. Its return explicitly said the
revision reference trigger did not apply. That contradicts the skill's revision-only router, Workflow
step 5, and reference trigger for revising a document. Therefore, body delivery passed, while complete
application of governing instructions did not. Do not report the treatment as full compliance.

The tested paragraph is a concrete candidate for agent-routing's bounded-handoff rule, with demonstrated
body-loading benefit in one pair. It is not sufficient evidence of a general fix. Do not spread the same
rule across every role, blame medium effort, or add automatic recursive reference loading. A further
targeted refinement could ask the worker to identify applicable linked-reference triggers before editing;
that refinement has not been tested or approved for shared adoption.

Both workers completed the small scratch edit and reported checks. Independent coordinator
`git diff --no-index --check` checks passed for both copies, and session-2's tracked working tree remained
clean. No authoritative documentation change was produced. The treatment checked its added local anchor;
both returns disclosed that other anchors and rendering were not verified. Those limitations do not
invalidate the observed read-coverage comparison. Terminal reports showed about 64 seconds per assignment;
model usage, monetary cost and savings were not measured.

Both task-owned agents exited after completion. Session-2 remains allocated; retain its scratch copies
and the conversation IDs until the proposal is accepted, rejected, or superseded. No shared files were
edited, no branch was landed, and no push occurred.
