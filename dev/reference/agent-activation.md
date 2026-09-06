# Agent and skill activation

How roles and skills become available to Claude Code and Codex **in this
repository**, and why the two runtimes differ.

The canonical spec is in the brain repo — `dev/decisions/0003-skill-activation.md`
(§3 D1/D2) and the `brain-agent-system` skill. This note records only how that
spec resolves here, plus the repo-specific consequences. Do not restate the
brain's rules; link to them.

**This file is the tracked record of what is activated here and why.** Owner
ruling, 2026-09-06: `.claude/agent-manifest.yml` stays gitignored per-user
machine state (`.gitignore:171`), consistent with `AGENTS.md`'s rule that the
agent-config directories are per-user. The consequence is that the manifest's
own contents — including the rationale comments in it — exist on one machine
only, so a change to `roles:` or `skills:` is not landed until it is recorded
in the "How it resolves here" section below. A fresh clone gets no activation
at all; that is expected, and `brain refresh --agent-system` is what supplies
it.

## Where activation is declared

| File | Scope | Tracked? | Materializes |
|---|---|---|---|
| `.claude/agent-manifest.yml` | this repo | **no** — `.gitignore:171` | `.claude/agents/`, `.claude/skills/`, `.agents/skills/`, `.codex/agents/*.toml` |
| `brain/config/ai/agent-manifest.yml` | user | yes, in the brain | the same trees under `~/` |
| this file | this repo | yes | nothing — it is the record, not the source |

Every materialized tree above is a **gitignored symlink farm** rebuilt by
`brain refresh --agent-system`, resolving the brain's canonical `artifacts/`
live. A skill or role on disk in the brain is inert until a manifest lists it
or an active role binds it.

`.claude/agent-manifest.yml` has two blocks: `roles:` and `skills:` (the
*manifest-explicit* list). Roles additionally carry their own **`skill_bindings:`**
frontmatter — not `skills:`, which is reserved: Copilot CLI discovers
`.claude/agents/` and types custom-agent `skills:` as `string[]`, so the
brain's list-of-`{name: condition}` under that key made every role fail to
load there (ADR 0003 D6, 2026-08-17). Readers keep `skills:` as a legacy
fallback; new roles use `skill_bindings:`.

Each binding takes one of three forms:

| Spelling | Meaning |
|---|---|
| `- skill` or `- skill: always` | the role always loads it, **and** it joins this repo's main-thread always-on scope |
| `- skill: always (role-only)` | the role always loads it, but it does **not** join main-thread scope |
| `- skill: when …` | situational; the role loads it when the condition holds |

`always (role-only)` exists because a bare `always` used to do two jobs at
once — guarantee the skill for its role, and charge every session in the
repository the skill's description. A specialist requirement is not a reason
to tax the main thread (ADR 0003 D1, 2026-08-25 revision).

## The rule

Activation closure is computed **per platform** — the same manifest resolves to
different sets:

| Binding | Claude | Codex |
|---|---|---|
| manifest-explicit | `.claude/skills/` — main-thread always-on | `.agents/skills/` — root catalog |
| role-bound `always` / bare | `.claude/skills/` — main-thread always-on | per-agent route only |
| role-bound `always (role-only)` | not symlinked — **path-read fallback** | per-agent route only |
| role-bound `when …` | not symlinked — **path-read fallback** | per-agent on-demand route |

Two consequences drive every decision below.

**A `when …` or `(role-only)` binding is reachable on Claude, but only from
inside the role.** Claude has no on-demand catalog route, so the skill is not
symlinked; the brain's `config/ai/AGENTS.md` instead instructs the agent to
resolve an uncatalogued bound skill by path under
`~/workspace/brain/artifacts/skills/` — `_external/<name>/SKILL.md` first, then
`<name>/SKILL.md`. That fallback was **verified live on 2026-08-08**: a
`geospatial-data-analyst` subagent with `climate-projections` absent from its
catalog quoted the rule, probed `_external/` (miss), then the owned tree (hit),
and read the file. `brain status --agent-system --detail` reports these as
informational notices and `claude_fallback_gaps` tests every one on each run, so
a rename cannot silently break the route.

What such a binding does **not** reach is the un-roled main loop, which carries
no role and therefore no binding naming the skill. That is the whole reason the
manifest `skills:` block matters here — see "Why most of this repo runs
un-roled".

**Role-bound skills are invisible to the Codex root agent.** Codex publishes
only the manifest-explicit set to the root catalog; a role's bindings —
including `always` ones — are appended to that role's generated
`.codex/agents/<role>.toml` as `read this skill when … — read: <abs path>`.
Codex *does* have an on-demand read path, so the role route works there.

Listing a skill in `skills:` is not "loading" it. It publishes the skill's name
and `description` into the catalog; the body loads only when the trigger fires.

## When to add a manifest entry

The brain's criteria, applied here:

- **(a)** No active role binds it *promotingly*, and the **un-roled main loop**
  needs it. Promotion buys main-thread always-on availability; it does not buy
  reachability, which the path-read fallback already provides. The 2026-08-08
  ADR revision is explicit that a role's `when …` dependency is not an
  activation claim and its absence from the manifest is not a closure gap.
- **(b)** The Codex *root* agent invokes it directly, even though a role already
  binds it `always`. Costs root-catalog budget, so state the reason in a comment.

Skills a specialist role binds `always` are deliberately **not** relisted for
Claude's sake.

## How it resolves here

Verified 2026-09-06 against the materialized trees — **10 roles, 10
manifest-explicit skills**:

- **Roles (10):** `cst-architect`, `model-builder`, `model-validator`,
  `geospatial-data-analyst`, `critical-thinker`, `dataviz-designer`,
  `python-engineer`, `git-steward`, `technical-writer`, `r-developer`.
- **Manifest-explicit (10):** `design-review-loop`, `design-scoping`, `pixi-env`,
  `python-plotting`, `r-discipline`, `git-workflow`, `python-discipline`,
  `climate-stress-testing`, `cst-run-control`, `snakemake`.
- **Claude main-thread scope (11)** = those 10 **+ `testing-policy`**, the only
  skill an active role binds promotingly that the manifest does not already
  list (`python-engineer` and `r-developer` → `always`).
- **Codex root catalog (10)** = the manifest-explicit set only.

The promoting `always` bindings across the ten roles are just three:
`git-workflow` (`git-steward`), `python-discipline` (`python-engineer`), and
`testing-policy` (`python-engineer`, `r-developer`). Everything else
unconditional is marked `(role-only)` and stays out of main-thread scope by
design: `scientific-workflows` and `reproducible-computing` (`cst-architect`),
`claim-evaluation` (`critical-thinker`), `python-plotting` and
`data-visualization` (`dataviz-designer`), `r-discipline` (`r-developer`).

Of the ten explicit entries, eight are load-bearing under (a) — `pixi-env`,
`design-review-loop`, `design-scoping` are claimed by no active role at all;
`climate-stress-testing`, `cst-run-control`, `snakemake` are bound `when`-only
everywhere; and `python-plotting` and `r-discipline` are bound only
`always (role-only)`, which does not promote, so the manifest is their sole
main-thread route. The remaining two — `git-workflow` and `python-discipline` —
are Claude-redundant and kept under (b), because `.codex/` drives this repo too.

`r-discipline` is the clearest illustration of why the role and the manifest
line are two different fixes rather than one: `r-developer` binds it
`always (role-only)`, so activating the role alone would have left the un-roled
main loop — which makes most of the small R edits here — with no R guidance at
all.

Five skills were removed on 2026-08-12 to bring the catalog down:
`climate-projections`, `hydromt`, `hydromt-wflow`, `python-geospatial`, `wflow`
(1,767 chars). All are specialist-only, bound `when …` by `cst-architect` /
`model-builder` / `model-validator` / `geospatial-data-analyst`, so they still
route per-agent on Codex and stay reachable on Claude by the path-read
fallback.

### Catalog budget

The governed number is the **managed effective catalog** — the union of the
user-scope and project-scope manifest-explicit skills, measured as
`len(name) + len(description)` per skill. Measured 2026-09-06 for a session in
this repository: **9,504 chars across 20 skills** (user scope 5,950/12, this
repo 4,518/10, two overlapping).

That is over the 8,000-char floor Codex documents for an unknown context window
and under `accepted_ceiling` in the brain's tracked
`config/ai/codex-catalog-budget.yml` (10,857 as of 2026-09-06). Crossing the
ceiling is a **failing** finding under `brain status --strict`, so a promotion
that crosses it must first cut or re-declare. Budget is reliability, not
tidiness: past the discovery floor Codex may shorten or omit descriptions, and a
trigger then silently stops firing.

### Why most of this repo runs un-roled

The routing gate dispatches a subagent only for substantial, self-contained work.
Small mid-flow edits, lookups, and thread-dependent follow-ups are handled inline
by the main loop, which carries **no role** — its behavior comes from
`AGENTS.md` plus whichever skills triggered. That is why the explicit `skills:`
list matters so much here: it is the main loop's only domain equipment. A
`when …` or `(role-only)` binding is reachable by path *once a role is active*,
and the main loop has no role to make it active.

## Gotchas

- **Codex root invocation is implicit.** Root routing is decided from injected
  name + description metadata. It is not guaranteed. The deterministic lever is
  naming the skill in `AGENTS.md`, which Codex reads directly.
- **`brain status --agent-system` reports the brain's own scope** when run from
  the brain root — its `catalog_budget` finding is about
  `brain/.claude/agent-manifest.yml`. Pass `--project` to ask about this
  repository.
- **Manifest edits do nothing until refreshed.** A listed-but-not-materialized
  skill is a silent gap, and `brain refresh` is the only thing that closes it.
- **The manifest is not tracked, so the manifest is not the record.** Update
  this file in the same change; nothing else preserves the decision.

## Verifying

```bash
# activate this repo only (targeted repair; the bare form sweeps every project)
brain refresh --agent-system --project /c/Users/taner/workspace/blueearth_cst

# link integrity + the path-read notices, scoped to this repo
python ~/workspace/brain/scripts/status.py --agent-system --detail \
    --project /c/Users/taner/workspace/blueearth_cst

# what this repo declares vs what is on disk (report-only, no brain needed)
python dev/scripts/check_activation.py

# what Claude sees (11) vs what Codex root sees (10)
ls .claude/skills/ ; ls .agents/skills/

# a role's generated on-demand routes
grep "read:" .codex/agents/model-builder.toml
```

`dev/scripts/check_activation.py` is the repo-local half: it checks that this
file's stated counts still match the materialized trees, that its relative links
resolve, and that nothing in `.claude/` dangles. It degrades to a skip when
`.claude/` is absent, so it is safe on a bare checkout. The brain's own
`claude_fallback_gaps` and `claude_unreachable_bound_skills` cover the
role-binding side and are not duplicated here.

## Open

- `pipeline-regression-testing` is bound `when`-only across all nine roles, so
  it is absent from main-thread scope. It is a live surface here
  (`check_baseline*`). Reachable from a role by path; addition to the manifest
  proposed, not decided.
- `weathergenr` was considered and declined — generator work routes through
  `model-builder`, which binds it `when`.
- `AGENTS.md` currently names **no** skills, so criterion (b) for `git-workflow`
  and `python-discipline` rests on implicit routing alone.

## History

- **2026-09-06** — corrected against the materialized trees after an audit found
  this file materially stale: it claimed 14 manifest-explicit skills (there are
  9) and a Claude scope of 19 (it is 10), named the role frontmatter key
  `skills:` (it is `skill_bindings:`, renamed 2026-08-17), described a `when …`
  binding as "unreachable by nobody" (the path-read fallback was verified
  2026-08-08), and called both manifests tracked (this repo's is gitignored).
  Recorded the owner ruling that the manifest stays untracked and this file is
  the record; added `dev/scripts/check_activation.py` so the counts cannot drift
  silently again. Same change activated `r-developer` and promoted
  `r-discipline` — see the entry below.
- **2026-09-06** — `r-developer` added to `roles:` (10 roles) and `r-discipline`
  to `skills:` (10 explicit). Four R workflow scripts under
  `blueearth_cst/weathergen/` and three under `dev/scripts/` had no active
  specialist: `python-engineer` excludes R, and `model-builder` directs general R
  work to `r-developer`, which was inactive — a dangling pointer. The skill line
  is the separate half of the fix: small R edits stay inline with the un-roled
  main loop, which a `when …` binding never reaches. Catalog cost 293 chars
  (9,211 → 9,504), well inside the ceiling.
