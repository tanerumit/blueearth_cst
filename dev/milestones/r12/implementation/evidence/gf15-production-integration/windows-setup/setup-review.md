# Independent review — GF15 production Stage 1, setup half

Reviewer: independent `python-engineer`, dispatched by the driver, blind to the
executing session. Reviewed at `feat/wp3-improvements` HEAD `e426f40d`, the
commit that carried the setup record before this review's corrections.

## Verdict

**ACCEPTED WITH FINDINGS.** No prerequisite failed. Every load-bearing claim in
`stage-1-setup-record.md` was re-executed independently and reproduced. One
factual error in the record's prose (F1) required correction before the record
could be cited as authority for Stage 2; three further findings are scope and
durability notes, none blocking. Stage 2 may proceed **for Windows** with F1
corrected.

## What the reviewer re-executed and reproduced

1. **D7 wheel pin.** The qualified lock's pypi entry is `lmoments3 1.0.8`,
   `sha256 984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e` —
   equal to D7's pin. The pinned wheel URL appears under **both** the `linux-64:`
   and `win-64:` environment blocks. Manifest `d2afe7f9…` and lock `43d11fc5…`
   match `setup-result.json`. Installer metadata `uv-pixi`, wheel tag
   `py3-none-any`.
2. **Installed source digests** re-hashed: both match D7 exactly.
3. **Both projections re-run** under the isolated and the shared production
   interpreter. Current projections identical — zero key differences, zero value
   differences, 220 packages each. Candidate delta in the isolated environment is
   exactly one entry, `python:lmoments3: 1.0.8`, with the python-metadata digest
   moving and the conda digest unchanged. The same candidate call in the **shared**
   environment raises `PackageNotFoundError` for lmoments3 — independent proof the
   shared environment was not mutated.
4. **Manifest delta** by normalized `difflib`: exactly one changed line,
   `+lmoments3 = "==1.0.8"`, inside `[pypi-dependencies]`. Line-ending counts
   confirm the CRLF hazard as recorded.
5. **Config provenance:** both retained originals still hash to `27b5463a…` and
   `474bc844…`, equal to the values registered in `evidence/p3/operations-dedicated-reuse.json`.
   An independent flattened YAML comparison reproduces `retained-config-comparison.json`
   exactly — workflow config zero differing keys, project config exactly two, none
   added or removed. Parsing the materialized project file through
   `simulation_settings` succeeds although the `project_dir` does not yet exist,
   confirming the parse touches no project state.
6. **CLI contract** read from source and confirmed verbatim, including the
   passthrough switch set and that **no `--metrics-only` flag exists anywhere in
   either module and none was introduced**. The reviewer notes the record's
   listing omits the short aliases `-n/-F/-p` but states nothing false.
7. **No mutation:** scoped and full `git status` empty; no lmoments3 in this
   worktree's or the primary checkout's environment or lock; `working/` absent;
   the snapshot unwritten. Imports re-run: all ten modules plus the three native
   submodules load from inside the qualified root.

## Findings and disposition

| ID | Finding | Severity | Disposition |
|---|---|---|---|
| F1 | The record quoted `edf9df1c…` as the cross-environment `installed-python-distribution-metadata` digest. That is the **candidate** value; the measured current-projection digest is `9ba17384828e2d703cd2f5eaa1e64e9d7160410b51b79f598ef238ea5f4e37cb`. Prose only — `setup-result.json` carried the correct value, so the measurement was right and the section was internally incoherent. | moderate | **Fixed.** Digest corrected and the candidate value now named where the delta is described. Confirmed against `setup-result.json` before editing. |
| F2 | The shared-environment projection and the solve logs lived only in disposable scratch, so the durable evidence backed the equivalence claim with prose alone. | low-moderate | **Fixed.** `stage-environment-shared.json`, `lock-solve.log` and `install.log` are now retained beside `setup-result.json`. |
| F3 | The qualification binds lock `43d11fc5…`, not the lock Stage 2 will generate in the repository; a fresh solve there may move packages outside the eight-root closure. | low, Stage 2 obligation | **Recorded.** The record now requires Stage 2 to re-run the projection comparison against the regenerated repository lock rather than inherit this pass. |
| F4 | The record framed D5's source-hash binding as an open Stage 2 decision. D5 already prescribes `resolve_metric_environment()` in `metric_plan.py` adding the hashes on top of `stage_environment`, so it is an implementation instruction, and the `content_identity.py` conditional — with its broader gate — is **not** triggered. | low; narrows Stage 2 | **Fixed.** Downgraded in the record, with D5's own wording quoted. Verified against the design text. |
| F5 | The accepted snapshot's collection anchor resolves into `.tmp`, and the obligation to preserve it existed only as prose in an evidence file. | low here; endangers an accepted gate | **Fixed.** Boarded as watch-item `t2609140745`. |

## Reviewer's answers to the adversarial questions

**Does a both-platform solve discharge D7?** Yes, for the clause it addresses —
D7's setup paragraph asks for a solver-generated lock for win-64/linux-64 with
commands, solver version and artifacts captured, all of which were verified.
D7's parity paragraph and the validation plan's "unavailable Linux execution
remains outstanding, not a Windows-derived pass" are separate obligations, and
the record states them in those terms. The framing is honest and not overclaimed;
under the owner's Windows-only override it suffices to release a Windows Stage 2,
and it is **not** sufficient for cross-platform integration acceptance.

**The placement finding.** Both halves verified: the superseded root did resolve
the conda repack `9a803860…`, which cannot satisfy a wheel SHA-256 pin, and all
six module sources are byte-identical across the two installs. The record's
refusal to propose a D7 change is **right** — relaxing a pin on one observed
byte-identity is a scientific-review matter, not a setup decision, and the
observation must not be read as authorizing the repack. The reviewer added a
mechanism the record lacked: the PyPI install leaves no `conda-meta` record while
the repack does, so placement changes the identity projection independently of
the wheel pin. That mechanism was re-observed by the executor and is now in the
record.

**Is the D5 source-hash gap real?** Real as an observation, overstated as an open
decision — F4.

**Did the old run capture an environment block?** Confirmed no: argv, exit code,
log path, log hash, two config hashes and an mtime-only change list, and nothing
else. "Unknown, not matched" is correct. Today's shell reproducing
`HDF5_USE_FILE_LOCKING=FALSE` is evidence about today's shell only.

**Is the durable root outside scratch and every write target?** Yes — outside both
checkouts, outside `.tmp`, disjoint from the snapshot and from the materialized
`project_dir`.

**Anything claimed as measured but not executed?** None found; F1 was the single
transcription error.

## What this review does not establish

- **Linux.** Nothing was installed or executed on linux-64. Solver resolution of
  the pinned wheel is not a platform qualification; D7 parity and E7 remain
  outstanding and no Linux claim derives from this Windows evidence.
- **Numerical adequacy.** No fit, estimator call, reduction, Wflow, Julia,
  generation or metrics execution was run by either party. Successful imports and
  metadata projections say nothing about whether the L-moment estimator produces
  correct or study-consistent numbers. The 8x accuracy evidence remains
  development-only and establishes neither actual-bundle adequacy nor independent
  validation.
- **Stage 3.** The working copy does not exist, the documented invocation is
  unexecuted, and the collection-anchor dependency is unresolved. Nothing here is
  evidence that the Stage 3 comparison will run or pass.
- **Two items corroborated but not directly re-observable:** that each `pixi`
  invocation cleared `PIXI_PROJECT_MANIFEST` and passed `--manifest-path`
  (corroborated by the clean scoped `git status`, the primary lock lacking
  lmoments3, and the matching scratch/durable lock hashes); and the vendored
  `tools/pixi.exe` version, which the reviewer did not query and which is
  irrelevant, since all recorded work used the verified installed 0.70.2.

No pytest, lint, baseline gate or suite was run by either party, and none was
warranted: the task changed no repository code. The reviewer made no edit,
commit, install, solve or environment modification.
