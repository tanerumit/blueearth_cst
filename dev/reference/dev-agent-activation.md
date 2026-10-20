# Agent and skill activation

Last updated: 2026-10-20

Use this reference when diagnosing missing project roles/skills or changing their activation.
The tracked [agent manifest](../../.agent-system/agent-manifest.yml) owns the role and explicit-skill
lists. This document explains their use; do not maintain a second inventory here.

## Ownership

Project declarations live in `.agent-system/agent-manifest.yml`. Shared activation rules, role bindings
and generated provider adapters are owned by brain-infrastructure's `brain-agent-system` capability.
Resolve its root through the workspace configuration rather than copying those rules into this project.

Provider directories such as `.claude/`, `.agents/` and `.codex/` are configured local projections and
may be linked between worktrees. Editing a manifest alone does not refresh an already-running session.
Use the shared activation workflow for regeneration and inspect a fresh session before claiming adoption.

## When to change declarations

Add a root-discoverable skill when the root agent needs to invoke it directly. A specialist's conditional
skill binding does not by itself make that skill discoverable at the root. Conversely, a role-bound skill
need not be duplicated in the root manifest merely to make it available to that role.

Project `AGENTS.md` supplies local routing constraints and read-when pointers. The user and project
subagent gate decide whether to delegate; an available role is not an instruction to spawn it.
Use the shared activation tooling for provider-specific binding expansion and catalog limits.

For documentation work, the manifest declares editorial, scientific writing/research/review,
and interface-reference specialists. Their responsibilities are described in
[documentation guidance](dev-documentation.md). The writing roles conditionally bind
`scientific-software-documentation`; that does not require another root-catalog entry.

## Verification

`dev/scripts/check_activation.py` reads the manifest and compares declared roles and explicit skills
against the local activation trees. It also checks relative reference links and dangling runtime links.
Absent runtime trees are reported as skipped; a bare checkout still supports the documentation-link check.

```powershell
pixi run python dev/scripts/check_activation.py
```

The infrastructure activation checks own role-derived skill reachability and provider scope. This
repository checker does not duplicate that resolution logic. When a declaration and materialized tree
disagree, determine whether regeneration or a declaration change is intended; do not edit documentation
to hide an unexpected difference.
