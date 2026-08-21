## Verdict
verdict: revise
doc_version: design-v4.md

## Findings

### ext2-1 [blocking]
- section: §9 Shared-seam enforcement (S4) — D-9.6; §19 Open questions — Q2/Q7
- finding: D-9.6 does not resolve `ext1-1`: it identifies `workflows.build_model.wflow_outvars` as a cross-workflow value read, then sanctions the S4 violation in `CROSS_WORKFLOW_READS` and defers the required hoist outside R13. The `ext1-1` ledger row therefore closes a settled requirement using future work. A frozen, shrink-only exception documents the violation; it does not make “any key read by more than one workflow lives in T1” true.
- rationale: R13 can pass every stated gate while WF3 behavior still depends on a value authored in WF1’s T2 file. On a fresh project, omitting that file selects defaults that may not match WF1’s outputs and can fail later during export. The delivered design therefore fails settled S4 and decision criterion 1.
- suggested_fix: Make the Q7 hoist a required R13 implementation phase. First validate split-only output neutrality; then hoist `wflow_outvars`, move `_WF1_GUARDED` and its pinned literals, verify the explicitly expected digest shift, and require `CROSS_WORKFLOW_READS` to be empty before R13 completion.

### ext2-2 [blocking]
- section: §15.3 D-15.3 — `scripts/split_project_config.py`; §15.4 D-15.4 — What the splitter refuses, and what it verifies
- finding: The staging ownership rule is unsafe. `--staging <dir>` accepts a caller-selected directory while the script “deletes and recreates it on every run.” Nothing requires the target to be absent, tool-marked, or distinct from the T1 directory, its ancestors, or another user directory. This contradicts S7’s report-only safety boundary.
- rationale: A legitimate but mistaken `--staging` argument can recursively delete unrelated user files before emitting the proposal. The migration tool can therefore destroy the state that staging-emit was chosen to protect.
- suggested_fix: Recursively replace only an exact tool-created directory carrying an ownership marker. Otherwise require the target to be absent or empty; reject the source directory and its ancestors; and place custom output in a newly created tool-named child. Add refusal tests for unmarked, non-empty, source, and ancestor targets.

### ext2-3 [major]
- section: §9 Shared-seam enforcement (S4) — D-9.6; §16.1 The gate table
- finding: The specified test does not enforce D-9.6’s claimed completeness or shrink-only behavior. The inventory covers Snakefiles, `blueearth_cst/`, and `scripts/`, but the permanent scan covers only the four `.smk` files. Equality with `CROSS_WORKFLOW_READS` also cannot enforce “nothing is ever added”: adding a read and a matching tuple makes the test green.
- rationale: A Python helper or user-facing script can introduce an undetected cross-workflow read, while a paired registry edit can legitimize the same violation in a Snakefile. S4 would remain dependent on reviewer discipline despite being presented as machine-enforced.
- suggested_fix: After the ext2-1 hoist, assert zero cross-workflow value reads across every authorized runtime-consumer surface, with identity-comparison sites separately enumerated. Define detectable access forms or constrain config access through an exhaustively inspectable API; do not retain an expandable exception registry.

### ext2-4 [major]
- section: §15.5 Mechanical steps for an existing project; §15.6 D-15.5 — The first post-migration run re-computes the project; §17.4 Considered and resolved in place
- finding: N19 justifies withdrawing the records-first `--touch` sequence, but not making immediate full recomputation part of migration for every project. The design acknowledges that existing records remain truthful until another invocation, while §15.5 instructs “Re-run” and §15.6 calls that the only path for every project.
- rationale: Users may spend a full WF1 build plus `RLZ_NUM × ST_NUM` Wflow runs merely to complete a value-equivalent file migration, although the staged round trip and post-application dry-run already verify composition and parseability. This converts pre-existing next-invocation dirtiness into an avoidable immediate migration cost.
- suggested_fix: Separate migration completion from output refresh. Require the round trip and dry-run immediately, but allow existing records to remain historical until the next intended execution. Scope the full-recomputation claim to users who explicitly require freshly shaped snapshots.

### ext2-5 [major]
- section: §8.5 D-8.6(b) — `--config` passthrough; §15.2 D-15.2 — The migration detector
- finding: The five-row migration mapping omits the dotted workflow-setting form explicitly withdrawn by S8: `--config workflows.<name>.<setting>=value`. It covers a mapping-valued `workflows='{"<name>": ...}'` form without stating how Snakemake parses the dotted form, which closure rejects it, what error results, or its replacement. The `ext1-3` ledger claim that every former form is mapped is therefore unsupported.
- rationale: Users of the specifically ruled-out syntax can receive a generic parser or unknown-top-level-key error rather than actionable migration guidance, while the documentation sweep can pass without covering the form that prompted S8.
- suggested_fix: Add explicit rows for every accepted pre-split syntax, including dotted workflow leaves and dotted `project`/`shared` leaves where applicable. State the parsed mapping, exact post-split outcome, and T2-edit or `config_path`-repoint replacement for each.

### ext2-6 [major]
- section: §9 Shared-seam enforcement (S4) — D-9.3
- finding: D-9.3 treats duplicate top-level key spelling across T2 files as cross-workflow sharing, although S4 is defined by consumption rather than spelling. Separate workflows can legitimately own unrelated settings having the same local name; their workflow namespaces distinguish them.
- rationale: Introducing independent settings such as `variables`, `window`, or `output_dir` in two workflows would make every parse fail even when neither workflow reads the other’s value. Maintainers must then invent artificial names or hoist unrelated settings into T1, degrading the intended modular boundary.
- suggested_fix: Remove unconditional cross-T2 spelling rejection or restrict it to explicitly global identities. Enforce actual cross-workflow consumption through the corrected D-9.6 mechanism and retain D-9.2 for known T1-owned and hoisted names.