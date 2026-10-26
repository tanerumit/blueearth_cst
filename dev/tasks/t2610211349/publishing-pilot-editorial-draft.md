# P3 editorial replacement packet

Task: t2610211349. Editorial owner: technical-writer, degraded generic runtime.
Requested model/effort: GPT-6.1-Sol medium, per owner; backend not independently observable.
Status: complete proposed replacements for coordinator retention and application by the s2 engineer.
Only this lane-local scratch draft is owned or changed by this packet.

## Authority and application boundaries

Inputs: the current main task's `publishing-pilot-content-specification.md` and the selected source
excerpts in `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-2`, verified clean at
`bed0ae1e823d957218537a531fa61613510e1f6a` before drafting.
The owner's later request permits wording changes to those excerpts; the frozen-wording restriction
therefore no longer applies to this editorial packet.
Publication scope, source ownership, compatibility decisions and migration limits remain unchanged.

Apply the five replacements below only after matching the stated original boundaries.
Fences with four backticks delimit replacement Markdown; they are packet packaging, not source content.
Keep surrounding frontmatter, headings, explicit anchors and unselected text unchanged.
No existing heading is renamed; the Configuration heading and Default indicators title stay in place.
The later owner instruction adds one advanced heading to replacement E, outside the pilot excerpt.
The workflow diagram annex and its static/interactive policy are unchanged.

The engineer must refresh any pilot extraction selectors or test expectations that depend on the old
wording so they include the complete replacement block, including its lists.
The semantic source boundaries below remain the inclusion contract; no implementation-specific selector
change is prescribed here, and no new content beyond the approved excerpts is requested.

## Replacement A: calculate different indicators

Source: `docs/guide/running.md`.
Replace the complete section beginning `## Calculate different indicators from existing simulations`
up to, but not including, the following `## Next` heading.

````markdown
## Calculate different indicators from existing simulations

You can calculate different indicators from completed simulations without rerunning the model.
The selected experiment must have a completed `_engine/simulation.json` record, even for a dry run.

In the simulation settings file:

1. Keep the existing `experiment_name`.
2. Set `operations: [indicators]`.
3. List the sets to publish in `indicator_sets`.

Then run:

```bash
python scripts/simulate_system.py --config <config> --cores 3
```

The runner reads the retained model responses and publishes each selected set to its own
`results/indicator_sets/<set-id>/` folder.
You do not need `--target`; the runner infers it.
The all-workflow runner does the same when the other four workflows are disabled.
See [Reading the outputs](outputs.md) for the result files.

An experiment is tied to its scenario collection, model, and simulation settings.
Use `--new-experiment` when those simulation inputs change.
For a fresh experiment, use `operations: [simulations, indicators]` to run the model before
calculating indicators.
Enabling the other workflows does not override an indicators-only selection.

For compatibility, the legacy `operation: indicators-only` setting still works for one release
with `--target simulations_and_indicators`.
````

## Replacement B: Configuration selection paragraphs

Source: `docs/site/toolbox-reference/workflow-simulate-system.qmd`, inside `## Configuration`.
Replace only the contiguous paragraphs beginning `` `operations` is a nonempty list `` and ending
`calendars, missingness or grain.`
Stop before the paragraph beginning `To retain air temperature`.
Keep the existing `## Configuration` heading, its preceding project-file explanation and YAML example,
and all subsequent text unchanged.

````markdown
1. Choose what to run in `operations`.
   Use a nonempty list of unique entries from `simulations` and `indicators`.
   Their order does not matter.

2. Choose the sets in `indicator_sets`.
   You can use set ids or inline mappings; omitting the setting selects `[default]`.
   Set ids must match `[a-z][a-z0-9_-]*` and be at most 64 characters long.

   The bundled `default` set is defined in `config/indicator_sets/default.yml`.
   It expands to the existing suite for `model.outvars`, using the toolbox defaults when that
   key is absent, or the retained variables when indicators run alone.

3. For a custom set, copy `config/templates/indicator_set.template.yml` and set its `config_path`.
   You can use an absolute path; a relative path resolves against the WF4 file that declares it.
   Selected set files are read once per invocation.

   A custom set selects registered definitions or names one registered calculation under an authored id.
   It never defines arithmetic, units, calendars, missingness or grain.
````

## Replacement C: indicator dictionary introduction

Source: `docs/guide/outputs.md`, immediately after `## Reading an indicator set`.
Replace only the opening paragraph beginning `For post-processing, read CSVs` and ending
`under its own indicator key.`
Keep the heading and following paragraph beginning `Every successful WF4 invocation` unchanged.
The replacement contains multiple paragraphs and a list; include the whole block in the pilot.

````markdown
For post-processing, open the CSVs in `experiments/<name>/results/indicator_sets/<set-id>/`.
There is one folder per selected indicator set: `default` unless the WF4 file names others.

Start with `indicators.csv`.
It has one row per indicator, describing:

- Its title, variable, input and output units, quantity, method and parameters.
- Its grain and group policy, water-year start and block assignment.
- Its partial-block, missingness and validity policies, references, and `block_coverage`.

`block_coverage` lists the blocks for every contributing run/location pair, including observed and
expected days and missing values.
It describes coverage, not sample adequacy.

For an authored indicator, `equivalent_definition` identifies its registered counterpart.
Its numbers equal that definition's, under its own indicator key.
````

## Replacement D: opening tables in Excel or code

Source: `docs/guide/outputs.md`.
Replace the complete subsection beginning `### Opening an indicator table in Excel` up to, but not
including, `### Migrating existing outputs`.

````markdown
### Opening an indicator table in Excel

Run IDs such as `run_01` and group IDs such as `group_01` are prefixed strings, so opening the CSV
normally preserves them as text.
When importing perturbation `st_id` values, explicitly preserve them as text in Excel and code.

When reading lookup tables in pandas, use `dtype=str` to preserve identifiers and
`keep_default_na=False` to retain the empty reference `st_id`.
Indicator `value` columns remain numeric.

Keep these identifier conventions in mind when joining tables:

- Suffix padding is consistent within the owning namespace.
- Groups are numbered independently of run count and selected indicators.
- Matching labels in different collections or indicator sets do not establish matching inputs or membership.
````

## Replacement E: complete Default indicators README

Source: `blueearth_cst/indicators/sets/default/README.md`.
Replace the full file, preserving the `# Default indicators` title.
The full replacement below preserves unique advanced detail locally; it is not the pilot inclusion range.

**Revised pilot inclusion contract:** include from `# Default indicators` up to, but not including,
`## Advanced implementation details`. Include the short ownership statement and advanced-reader link.
Exclude the advanced heading and everything after it from both HTML and PDF, including any appendix.
This replaces the original specification's full-README inclusion for this source only.
Other source excerpts, diagram handling and migration boundaries are unchanged.

The user-facing advanced link is `../../README.md#add-a-calculation`, which resolves from the canonical
default README to the existing indicator-module authoring section.
Keep that source link relative; the publisher must resolve it to the module README before rebasing and
mark its published form as a repository/online advanced reference outside the pilot.
Do not point it to an omitted same-page anchor, create a new manual page or include module internals in
the user-facing sample to make the link appear internal.

````markdown
# Default indicators

The toolbox's registry and calculation scripts define the default indicators and formulas.
See the [advanced authoring contract](../../README.md#add-a-calculation) for implementation details.

Use these conventions when reading results from the default set:

- **Summary statistics:** annual means, maxima, minima, p95, basin totals, rolling-seven-day extrema,
  baseflow ratio and reference month means retain native pandas missingness and partial-block weighting.
- **Water years:** the configured water-year anchor defines the blocks.
  January–December applies only to a January water year.
- **Rolling windows:** seven-day windows require seven nonmissing days.
  They cross water-year boundaries, but never member boundaries.
- **Reference months:** these use pooled monthly sums and explicit reference membership/location.
- **Warm-up:** no new warm-up is removed.
- **Temperature:** the token is `temp` and the units are `degC`.
  `temp_annual_mean` averages daily air temperature within water-year blocks, then averages the block
  means with equal weight.
  It never sums daily values.
  The default preset selects it only when temperature is configured or retained for that simulation.
- **Member groups:** run indicators support equal-weight member means with NaN propagation.
  Return levels pool blocks instead.
- **Return levels:** these use member-local annual maxima or rolling-seven-day annual minima.
  Only finite block values are used.
  The sample is screened using max(ceil(T),10).
  The estimator's source must pass qualification verification.
  Only probabilities allowed by the supplied domain are accepted.
  Fit-block counts differ from retained daily-input counts.

## Advanced implementation details

The [module authoring contract](../../README.md#add-a-calculation) describes registration, formulas,
callable-keyed parameters, fixed assumptions and independent checks.
The following details apply specifically to the default set:

- `registry.py` retains the production default indicator names and declares fixed `ASSUMPTIONS`.
- Units, reference behavior and accepted parameters appear next to each registration and formula.
- `rolling_annual_min` describes the fixed seven-day calculation.
  The old `rolling7_annual_min` selector remains a declarative compatibility alias.
  Annual maximum fits have no unused rolling-window parameter.
````

### Advanced-detail preservation mapping

- Formula ownership and callable-keyed `PARAMETERS` are already covered by the module README's file
  responsibility table and `## Add a calculation`; do not duplicate their file-by-file list in user copy.
- Independent expected values in `checks.py` are already covered by that table and the independent
  `checks.expected(...)` instructions in `## Add a calculation`.
- Fixed `ASSUMPTIONS` are explained in `## Add a calculation`. The default-specific retention of
  production names stays in the local advanced section alongside the existing declaration ownership.
- The location of units, reference behavior and accepted parameters remains in the local advanced section.
- The exact `rolling_annual_min`/`rolling7_annual_min` compatibility pair and absence of an unused maximum-fit
  rolling parameter are not supplied by the generic module contract; retain them in the local advanced
  section, excluded from the pilot.
- All scientific conventions remain in the user-facing bullets: block/missingness/weighting rules,
  seven-day/member boundaries, reference months, warm-up, temperature units and selection, group NaN
  behavior, return-level screening/qualification and fit-block versus daily-input counts.

No new duplicate technical-manual page is needed. The existing module contract supplies generic advanced
guidance; the canonical local default README retains its unique advanced facts.

## Semantic-preservation checklist

Checked by source-to-draft comparison; these checks do not establish independent content accuracy:

- Existing headings and their implicit anchors are preserved; replacement E adds one owner-authorized
  advanced heading, excluded from the pilot. No Quarto labels, frontmatter, chunks or citations change.
- Running command is identical, including `python`, script, `<config>`, `--config` and `--cores 3`.
  Existing experiment selection, completed `_engine/simulation.json` prerequisite (including dry runs),
  fresh-experiment operations, `--new-experiment`, inferred target and one-release legacy target remain.
- Configuration retains both allowed operations, nonempty/unique/order-insensitive list behavior,
  both set-selection forms, omitted `[default]`, exact id regex and 64-character limit.
  Default expansion, both variable fallbacks, custom-set template/path bases, one-read-per-invocation
  behavior and the prohibition on redefining calculation policies remain.
- Output path, one-folder-per-set/default behavior and all dictionary metadata categories remain.
  Coverage retains every run/location pair, observed/expected/missing detail and its non-adequacy limit.
  `equivalent_definition` and equality under the authored key remain.
- Text identifiers, namespace-local padding, independent group numbering, non-equivalence across
  collections/sets, `dtype=str`, `keep_default_na=False`, empty reference `st_id`, numeric `value`
  and text-preserving perturbation imports remain.
- All default reductions and native pandas missingness/partial-block weighting remain; water-year,
  seven-day/member-boundary, reference-month and no-new-warm-up policies remain.
  The first bullet is labelled Summary statistics because it also includes reference month means.
- `temp`, `degC`, `temp_annual_mean`, equal block weighting, no temperature sum and selection prerequisite
  remain. Group NaN propagation and pooled return-level blocks remain distinct.
- Return-level block extraction/filtering, max(ceil(T),10), estimator source qualification and supplied
  probability gating remain; daily-input and fit-block counts remain distinct.
  Short sentences explain finite-block filtering as using only finite block values and probability-domain
  gating as accepting only probabilities allowed by the supplied domain; no domain or filtering rule is added.
  Both rolling selectors, compatibility status and absence of unused maximum-fit window parameter remain.
- Generic implementation detail remains in the existing module README; unique default-set implementation
  facts remain under the local advanced heading, excluded from the pilot. The user excerpt shows no
  file-by-file internals or rolling-selector aliases. Its advanced link targets the existing
  `../../README.md#add-a-calculation` section and must be resolved as an external advanced reference.
- No new result, data availability, runtime, numerical adequacy, surface-construction or compatibility
  claim is introduced. No policy or scientific-method change is requested.

## Application and verification handoff

These are proposed replacements, not applied edits.
The engineer should refresh the pilot from its canonical sources after applying accepted edits, then
inspect numbered-list continuation, bullet indentation, command formatting, source attribution and
internal/external links in HTML and PDF through the existing P3 checks.
Publication must not execute the displayed command or any model/notebook/data acquisition.
This packet narrows Default indicators inclusion to the user-facing range specified in E.
It changes neither pilot asset/compatibility handling nor migration authorization.
Coordinator alone retains task records and owns commits/integration.

## Input identity

SHA-256 of complete source files read from session-2:

```text
docs/guide/running.md
db01a56148ab6f225e527af09c8b8e52d88536a09caad8631badc3bb7bf1dae6
docs/guide/outputs.md
a4d0b38379385e15109190d2a6d13cf917f708e741ad02d589e78673baa48528
docs/site/toolbox-reference/workflow-simulate-system.qmd
71e5dd6756cd46d563349e089d038819f5c9ef489d9a03f2149dfad6e6d8db7e
blueearth_cst/indicators/sets/default/README.md
0cc6ffa9a0cddf62a682e52efda6010361fb5b62f114091c1baa46dc55ccad44
```

## Skills and execution evidence

Reused the fully read canonical technical-writer role and relevant completed guidance from
`scientific-software-documentation` (reader actions, local method ownership and source-based checking),
`project-reference-docs` (stable contracts and boundaries), `testing-policy` (inspection scope),
`project-system` (authorized scratch/handoff) and `task-brief` (bounded replacement packet).

Newly fully read and applied:

- `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/writing-feedback-revision/SKILL.md`
  and triggered `references/revision.md`: revision-only mode, user-directed tone change, claim/qualifier
  fidelity and semantic comparison. `_external` override checked first; none found.
- `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/quarto/SKILL.md`: preserve QMD context,
  ATX heading, list spacing and minimal changed scope. `_external` override checked first; none found.
  No advanced feature syntax, callout, citation, chunk or slide work triggered further references.
  Body prose wraps at 110 characters where needed under the repository convention.

Incomplete applicable skill bodies or triggered references: none known.
No code example was changed, so no new Python implementation/example-repair skill was triggered.
No citation or scientific-evidence appraisal was attempted.

UTC start: **2026-10-26 14:54:56 UTC**.
End/check time is recorded in the closing addendum after artifact verification.
Token input/output/cache totals and cost: unknown.

Scratch preflight: `git check-ignore -v .tmp/tasks/t2610211349/p3-editorial-revision.md` matched
`.gitignore:200:.tmp/`; target did not exist. Parent directories were ordinary directories with no
reported link target. No pre-existing content was overwritten.
No tracked edits, Git mutations, builds, shared task writes, runs or nested agents occurred.

## Completion check

UTC end: **2026-10-26 14:57:49 UTC**; recorded interval: **2m 53s** before this closing annotation.
Verified five replacement Markdown blocks, preserved required headings/command/regex/sample-screening
expression/module link, and no lines exceeding the 110-character convention.
The artifact remains ignored; s1 remains clean/detached and s2 remains clean on its pilot branch.
Source-to-draft semantic comparison is complete; application, rendered layout and executable behavior
remain unverified and belong to the engineer's subsequent authorized P3 checks.

## Owner steering: user-facing inclusion narrowed

Updated draft E and its preservation checklist/mapping after reading the complete existing module README
from session-2. Generic implementation guidance already has an advanced home there; unique default-set
details remain in a separately headed local section. Only the preceding user-facing portion is included
in the pilot. No tracked source has been edited.

Final check UTC: **2026-10-26 17:17:06 UTC**. Verified five replacement blocks, no file-by-file internals
or selector aliases in the user excerpt, and existence of the module README and its `Add a calculation`
heading targeted by the relative advanced link. No lines exceed 110 characters. The scratch packet
remains ignored and s1 remains clean/detached. Rendered link rewriting remains an engineer check.
Reused the previously completed role/skill/reference reads; no new applicable skill or reference was
triggered and no incomplete read is known. No builds, runs, Git mutations or nested agents occurred.
