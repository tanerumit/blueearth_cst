# P3 editorial revision

Owner feedback: content is mostly acceptable, but use user-centric wording, simpler sentences, and
numbered steps or bullets, especially in Configuration and Default indicators.

Further owner direction: do not expose `registry.py`, `calculations.py` or similar implementation
details in the user-facing pilot, even as an author subsection. State briefly that the toolbox's
registry/calculation scripts define the default indicators and formulas, and link to advanced material.
Preserve implementation detail in its canonical advanced/local source; exclude it from pilot inclusion.
The existing indicator-module README is the preferred advanced link if sufficient. No duplicate manual
page is required merely to separate audiences. This supersedes complete-local-README inclusion for P3.

## Execution

Continue the existing technical writer in s1 (draft only), then the existing Python engineer in s2
(apply exact approved draft and rebuild). Both remain GPT-6.1-Sol medium. cst-main owns review,
commits and task records; no worker commits, nested delegation, migration or s3 work.

The writer's lane-local replacement packet will be retained here as
`publishing-pilot-editorial-draft.md` after coordinator review. It is review evidence, not a second
maintained publication source. Selected canonical excerpts remain the publication sources.

## Expanded s2 write scope for this revision

In addition to the existing seven pilot files, permit narrow wording changes to:

- `docs/guide/running.md`: the selected existing-simulation indicator section only.
- `docs/site/toolbox-reference/workflow-simulate-system.qmd`: selected indicator-configuration paragraphs.
- `docs/guide/outputs.md`: the selected table-reading and Excel excerpts only.
- `blueearth_cst/indicators/sets/default/README.md`: the selected complete local conventions account.

Preserve headings/anchors, exact keys/commands/units, prerequisites and scientific qualifications.
Use steps for actions and grouped bullets for conventions; do not turn scientific definitions into
optional advice. No algorithm, configuration behavior, source migration or scientific-approach writing.
Do not independently rewrite the editorial lead's text. Report ambiguity to cst-main.

Update pilot manifest selection boundaries and wording-sensitive checks only as needed. Before using a
new boundary, verify that it selects the full intended revised excerpt exactly once. Retain single-source
generation. Adjust versioned source attribution to identify the revised source candidate accurately.

## Verification and handback

Reuse prior unchanged publishing behavior checks. Run the affected pilot/site-staging checks and scoped
Ruff if Python changes; render HTML/PDF and inspect the changed lists, wrapping and pagination. Confirm
revised excerpts are complete in both outputs and source inputs remain unchanged by rendering. Preserve
existing anchors and check affected links; no need to repeat diagram interaction or unrelated failure
probes when their code and inputs are unchanged. Run no models, notebooks or data acquisition.

Keep outputs and evidence under the existing s2 `.tmp/tasks/t2610211349/p3/` root; keep separate revision
logs and `.tmp/tasks/t2610211349/p3/editorial-return.md` with commands, checks, limitations, UTC timings,
roles/skills and observed/unknown usage. Stop the preview after visual review. Return the artifact path
and completion status, leaving implementation uncommitted for coordinator review.

Fully read any newly applicable skill bodies and triggered references before governed work; reuse
completed applicable reads. Report any incomplete reads. Preserve unrelated work and single-writer ownership.
