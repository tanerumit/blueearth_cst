---
title: Adopt a manual toolbox versioning policy
type: todo-item
status: active
branch: chore/versioning-policy
effort: 1
area: tooling
queue:
created: 2026-10-01
updated: 2026-10-01
---

> [!note] Overview
> **What** — Document the approved manual Semantic Versioning policy and a release checklist for the toolbox.
> **Why** — Release tags exist, but version bump rules, compatibility promises, and release preparation are not defined.
> **Effort** — Mostly documentation and changelog reconciliation; confirm whether existing version tooling supports authoritative Git tags.

## Progress

- [x] Agree on the policy — owner approved manual Semantic Versioning with authoritative Git release tags.
- [x] Add a concise versioning reference and link it from AGENTS.md and CHANGELOG.md.
- [x] Define compatibility, numerical-change handling, pre-1.0 breaking changes, and explicit stability approval.
- [x] Add the release checklist using existing validation and separate tagging, pushing, and publishing approvals.
- [x] Reconcile Unreleased changelog entries with changes since v0.2.0-alpha.
- [x] Assess tag-based versioning configuration and document any tooling limitation without adding unnecessary automation.
- [x] Check live references, validate the final documentation, and commit the policy changes.

## Approved decisions

Use manual releases tagged vX.Y.Z; ordinary commits and milestone seals do not create releases. Patch releases preserve supported interfaces and scientific methods; compatible features use minor releases. Incompatible changes before 1.0 use minor releases with breaking-change notices; after 1.0 they use major releases. Compatibility covers documented commands, configuration, durable output formats, and scientific calculation methods. Numerical bug fixes may be patches, with documented and validated result changes.

Git release tags are authoritative. Milestone tags are development checkpoints. Existing alpha tags remain historical; future release tags use plain vX.Y.Z. Version 1.0 requires explicit owner acceptance of interface stability. Tag only a verified main commit with owner authorization; pushing and publishing remain separate decisions.

Implemented in 72ae2e2f on chore/versioning-policy. Policy: dev/reference/versioning.md (on the task branch). Configuration validation, local Markdown links, historical changelog preservation, and git diff --check passed. Board check: zero errors; existing editorial warnings. No version adapter was added because the helper requires a file carrier. Next: owner-approved landing; no release or push is authorized.


