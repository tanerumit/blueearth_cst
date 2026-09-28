# R14 — external review round 1, verbatim

> Reviewer: `gpt-5.6-sol` via headless `codex exec`, 2026-08-24, against
> `config-shape-design.md` DRAFT v2 at `90fba308`. Captured verbatim and
> IMMUTABLE — dispositions live in `config-shape-review-record.md`, never here.

---

## Verdict
verdict: revise
doc_version: config-shape-design.md DRAFT v2

## Findings
### ext1-1 [blocking]
- section: 11.2 The rewriter (`C-38`)
- finding: The specification is not self-contained: the migration is “driven by the register,” but the normative old-path → new-path mapping, deletion/default semantics, and exception metadata for the 85 indexed changes are absent. The document instead requires implementers and reviewers to recover them from `config-shape-scoping.md`, despite declaring that implementation should stay in this specification.
- rationale: The rewriter cannot be implemented or its completeness reviewed from this document. An omitted or inconsistent mapping can silently drop, misplace, or default a user value, while still producing syntactically valid v2 configuration.
- suggested_fix: Add a normative, exhaustive migration appendix or versioned machine-readable mapping containing each row’s old path, new path, operation, value transformation, collision policy, default behavior, and exception hook.

### ext1-2 [blocking]
- section: 14.3 The stale-spelling sweep, and `C-37`
- finding: The proposed gate—grep every retired spelling and fail on any hit outside `dev/milestones/**`—cannot pass. The migration mapping, v1 fixture required by D-13.3, migration note, compatibility tests, and diagnostic messages must intentionally contain retired spellings.
- rationale: A correct implementation necessarily fails its mandatory rename gate. Implementers must either weaken the check ad hoc or omit required migration and documentation artifacts, making the gate unusable or gameable.
- suggested_fix: Define an explicit allowlist of legacy-bearing artifacts and contexts, then check active configuration, code identifiers, commands, and live documentation separately. Require every allowed hit to have a classified reason and make unknown classifications fail closed.

### ext1-3 [blocking]
- section: 14.2 The baseline, scoped correctly
- finding: D-14.3 only requires provenance resolution before G6 “depends on it,” and §17 explicitly says it blocks the G6 claim rather than implementation. That is too late for a pre-change numerical reference: implementation may begin before establishing whether the shared, untracked fixture and current manifest represent an uncontaminated R13 state.
- rationale: Once implementation changes numerical paths or regenerates the shared fixture, a trustworthy before-state may be unrecoverable locally. The central numerical-neutrality claim could then be accepted against a contaminated or post-change baseline.
- suggested_fix: Make provenance resolution a hard pre-implementation gate. In a clean isolated R13 checkout, identify the producing commit and environment, reconcile `t2608220920`, regenerate or independently verify the four data targets, and record immutable hashes plus provenance before the first R14 implementation commit.

### ext1-4 [major]
- section: 11.2 The rewriter (`C-38`)
- finding: The one-shot, multi-file migration has no transactional contract. It does not specify preflight validation, destination-collision behavior, staging, rollback, backups, interruption recovery, or idempotence, despite renaming and rewriting an entire config set plus stamping `schema_version: 2`.
- rationale: A refusal encountered after writes, an existing destination filename, or process interruption can leave a project with mixed v1/v2 files or overwritten content. The loader will then refuse the project, and rerunning an undefined partially completed migration may compound the damage.
- suggested_fix: Require a read-only preflight over the complete set, refuse all exceptions and collisions before writing, stage outputs separately, atomically replace only after validation, preserve recoverable backups, and define rerun behavior for v1, complete v2, and partial states.

### ext1-5 [major]
- section: 11.3 One bundle
- finding: The design treats the digest break as a refusal paid “once” but does not specify how an already-run experiment becomes runnable afterward. Rewriting project configuration alone leaves its frozen experiment record in the old shape, so the same key-union difference can recur on every attempt.
- rationale: Existing experiments may become permanently unusable under their current names rather than experiencing a single migration event. Users lack a defined way to resume, intentionally fork, archive, or acknowledge the identity transition without deleting provenance-bearing artifacts manually.
- suggested_fix: Specify the post-migration lifecycle for frozen experiments: either migrate their identity records with an auditable v1→v2 equivalence, require an explicit acknowledged reset/fork command that preserves prior records, or state that new experiment identities are mandatory and provide the exact recovery workflow.

### ext1-6 [major]
- section: 14.1 The ladder for this milestone
- finding: The numerical-neutrality gate covers only four outputs from one baseline configuration. It does not verify semantic equivalence across all four migrated `test_case` sets, conditional defaults, renamed rule parameters, or the two intentional behavior changes; `test-full` is not specified as an old-versus-new numerical comparison.
- rationale: A migration error affecting only rapid, Linux, WF2-fast, a non-default setting, or one exception path can pass every listed gate while changing results beyond the two permitted cases.
- suggested_fix: Add pre/post-migration equivalence tests over every shipped config set at the resolved-config and rule-parameter seams, plus targeted execution assertions for `C-69` and the `N8` refusal. Keep the four-target baseline as the high-value end-to-end check, not the sole falsifier of the general claim.