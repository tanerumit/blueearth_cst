---
title: Two interchange contract tests are not guarded against a pre-R14 fixture
type: todo-item
status: backlog
effort: 1
area: tests / fixtures
origin: console styling pass (2026-09-17)
queue:
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — tests/test_interchange_contracts.py::test_wg3_integration and ::test_hm7_integration fail on any worktree whose test_case/test_local predates R14. They read scenarios/requests/ and the retained response inventory path, both of which R14 moved; the tree here still has scenario_plans/ and scenario_collections/.
> **Why** — The file already documents this hazard and guards ONE case against it -- the WF1 config snapshot, behind _FIXTURE_PRE_R14 -- because _fixture_present() only answers 'is there a tree here' and never 'does it have this schema'. These two cases need the same guard. Until they do, every full-suite run on a pre-R14 worktree reports two failures that are about the fixture's age, which trains a reader to ignore them.
> **Effort** — small

## Progress

- [ ] <first step>
