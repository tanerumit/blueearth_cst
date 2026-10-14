# Worktree footprint and session runtime evidence

Date: 2026-10-15 (local). Task owner: session-2, `chore/worktree-runtime`, allocated explicitly by
the user. Primary and session-3 source base: `0ed71555d0e10bfecd6726450b713fccbe0cec45`.
Motivating session-1: `4514354f0d88e2dea232aca7b029d0d61803b87d`, `chore/minor-tweaks`.
No pre-existing footprint task note was found; this record retains the requested evidence without
adding a board item or changing another task's ownership.
Implementation commit: `6068b17b225d8f7b125148c5c88df31316b34c4d`.
Candidate Git tree: `21a8728ebcba8bf16c9e6f0f1f2e3ca3033aac8b`.

## Decision and scope

Keep all three reusable slots and independent Git worktrees. Stop automatic full provisioning by
setting `worktree_provision: []`. Keep both fixture seeds and all existing installation/output trees.
Provide an explicit development-check borrower helper, with isolated execution retained for dependency
changes, installation testing, incompatible contracts, and full workflow qualification. Landing still
requires approval. No environment, fixture, output or worktree was deleted, copied over, or linked.
No dependency version, lock file or scientific calculation changed. `pixi.toml` changes are comments.

The authoritative operator instructions are in `docs/site/setup/install.md`, "Session runtimes".
`dev/scripts/session_runtime.py` is development tooling, with no workflow/run-path caller.
The helper checks contract compatibility before invoking Pixi, then uses `--as-is --executable`:
no solver, install, task expansion or change to the borrowing working directory. It checks the actual
Python import root before launching the requested check. Runtime installation remains the lender's
exclusive responsibility, with no updates during borrowing. This is cooperative ownership, not an
ACL-enforced immutable installation or a sandbox for arbitrary child code.

## Measurements

All byte counts below are decimal bytes; directory entries and NTFS metadata are not file data.
Read-only scans excluded linked directories. In particular `.agents`, `.claude`, and `.codex` in
session-1 resolve to primary configuration and were not traversed. No scan-only destination was
created by Robocopy `/L`.

| Contributor in session-1 | Files | Logical bytes | Interpretation |
|---|---:|---:|---|
| Present tracked checkout | 2,953 | 171,015,323 | 3,176 index paths; sparse exclusions |
| `.pixi` | 94,630 | 5,259,068,945 | 10,968 directories; mostly linked native package data |
| `test_case/test_local` | 413 | 145,007,388 | Copied baseline/fixture; retained independently |
| `test_case/basin_map_fixture` | 12 | 230,286 | Irreplaceable map input fixture; retained |
| All `test_case` | 1,380 | 799,229,642 | Also includes configs and other accumulated run outputs |
| `.snakemake` | 9,287 | 85,321,436 | Workflow metadata/logs, independent per checkout |
| `.tmp` | 388,713 | 6,225,271,248 | Partial census; retained test/run/artifact state |
| `.tmp/pytest` | 370,714 | 2,995,215,893 | Partial census, included in `.tmp` above |
| `.tmp/scratchpad` | 17,892 | 3,229,933,306 | Partial census, included in `.tmp` above |

The `.tmp` scan reports 355,349 directories, including 97 in Robocopy's FAILED directory column;
file failures are zero. The pytest/scratchpad subscans report 76/20 failed directories respectively.
Treat these byte/file counts as observed lower bounds, not complete totals. Reparse exclusions and
retained test directory structures prevent a whole-tree completeness claim. No inaccessible or
unclassified state was removed. Table rows overlap; do not sum them as a worktree total.

The exact `.pixi` census used Windows `GetFileInformationByHandleEx(FileStandardInfo)` for allocation
and hard-link count, not just logical lengths. Result, with zero query errors:

```json
{"files":94630,"logical":5259068945,"allocated_path_sum":5444906736,"hardlinked_files":89149,"private_allocated":187824640}
```

Thus 89,149 files have multiple hard links; 5,481 are singly linked. The private allocation is
187.8 MB, much smaller than the 5.445 GB allocation summed over paths. An earlier
`GetCompressedFileSizeW` probe returned logical lengths for these uncompressed files and is **not**
used as cluster-allocation evidence. Its file-ID census found no duplicate identities within this
prefix. Links to the machine package cache and other prefixes explain sharing across roots.
`fsutil hardlink list .../session-1/.pixi/envs/default/Lib/site-packages/numpy/__init__.py` identified
the same file in the Rattler cache, primary, and all three session prefixes.

Machine-wide resources, measured separately with `/L` and no failed directories:

| Resource | Files | Logical bytes |
|---|---:|---:|
| `%LOCALAPPDATA%/rattler/cache` | 304,173 | 18,654,348,736 |
| `~/.julia` including juliaup, packages, artifacts and compiled state | 14,899 | 2,390,762,694 |

These are shared machine resources, not additional private copies per session. Do not add linked
prefix bytes to the cache as if independently allocated. No cache was pruned.

Reproduction commands (substitute the exact contributor path for `<source>`):

```powershell
robocopy <source> <ignored-scan-only-destination> /L /E /XJ /SL /BYTES /NFL /NDL /NJH /R:0 /W:0
git -C <session-1> ls-files -z
fsutil hardlink list <session-1>/.pixi/envs/default/Lib/site-packages/numpy/__init__.py
```

Robocopy returned 1 for list-only differences; its summary is the evidence, not a claim that files
were copied. The one-off allocation probe is retained in this record's ignored `.tmp/allocation_probe.py`.
Tracked size was summed only over present `git ls-files` entries. Two broad Python walks were stopped
because of the retained test-tree cost and replaced by bounded contributor scans; no partial output
from those walks was used.

## Options and expected reduction

| Option | Assessment |
|---|---|
| Fewer reusable slots | Reduces capacity; does not address the cause, and deletion is outside scope |
| Conditional/explicit provisioning | Adopted; artifact-only work needs no environment |
| Lightweight environment | Another lock/qualification burden; avoid another dependency set |
| Compatible stable runtime | Adopted for checks; coordinate owner and reject incompatible contracts |
| Detached environments | Relocates workspace prefixes; does not deduplicate them |
| Share fixture directories | Rejected here: baseline/output mutation and provenance need independent copies |
| Remove retained scratch | Large potential; needs separate retention review and deletion authorization |

Measured current data support an estimate of about 94,600 fewer file entries and 11,000 fewer
directories per future unprovisioned/borrowing session, avoiding roughly 188 MB of private file
allocation for an equivalent prefix, plus unmeasured filesystem metadata. The 5.26 GB logical prefix
size is **not** the expected marginal storage saving. Three such omitted prefixes would represent
about 284,000 file entries and 563 MB of private data, an estimate rather than a measured new setup.
Current reclaimed bytes/files: **zero**, because existing state was preserved. The 6.23 GB of retained
scratch is a separate, larger cleanup opportunity, not an implemented saving.

Upstream context: [Pixi environments](https://pixi.prefix.dev/dev/workspace/environment/) explains
cache hard links/reflinks and fallback copying;
[Pixi run](https://pixi.sh/latest/reference/cli/pixi/run/) documents executable mode and `--as-is`.
Installed Pixi version: 0.70.2. The implementation was checked against its local `--help` and actual cwd.

## Runtime investigation

- Python 3.12 is provided by Pixi. `pyproject.toml` has no packaging/build manifest; the project is not
  installed editable. The two `.pth` files found are setuptools' distutils hook and relative PyWin32
  paths, not links to a project checkout. The helper forces session `PYTHONPATH`, disables user-site
  imports/bytecode writes, and prints/asserts the resolved project package path.
- `pixi.toml` owns Python/R dependencies and activation; `pixi.lock` owns their resolved packages.
  The helper compares parsed TOML, normalized lock text and installer/activation script text. Raw
  hashes differed for session-1 because of line endings; normalized contracts match. Initial raw-hash
  incompatibility interpretation was corrected before implementation acceptance.
- Windows activation can copy `ffi.dll`/`cairo.dll` aliases. Borrowing rejects missing aliases before
  activation; only the owner completes provisioning. HDF5/gcsfs/TLS activation settings are retained.
- R's out-of-lock `weathergenr` v2.0.1 is installed by the idempotent pinned GitHub installer into the
  active Pixi library. Native R dependencies come from Conda. Real probes load the package; the stock
  checker only asks its version. Borrowing clears ambient R library overrides and uses `--vanilla`.
- Julia +1.11.7 is juliaup-managed. `--project=.` selects the borrowing checkout; Project/Manifest
  must match the lender. Package/artifact storage is already machine-wide under `~/.julia`. Borrowing
  prepends a per-session writable depot while retaining the existing user and system depots.
  A trailing empty depot component expands system depots but omits the user depot, so the helper
  explicitly retains `~/.julia` when no override is configured. Julia installation tests must instead
  select a fresh session-only depot before instantiation.
- Pixi named tasks run at the selected manifest root. Executable mode was observed to retain the
  borrowing cwd; invoking the primary named task would check the wrong checkout. Borrowed execution
  is for explicit executable commands, never named tasks or installers. Nested Pixi updates are disabled.
- Matplotlib, XDG/Cartopy, Numba, PROJ and Ruff writes go under the borrowing `.tmp/session-runtime`.
  Pytest already has per-invocation `.tmp/pytest/run-*` roots. External P-drive/global data are not
  environment contents and are not relocated. Full workflows remain on isolated runtimes under the
  validation ladder; this task makes no borrowed end-to-end or numerical equivalence claim.

## Verification and retained logs

Logs below are relative to the owning session's `.tmp/scratchpad/worktree-runtime/`. The lending
runtime was primary's existing `.pixi/envs/default`; no install command ran against it. Checks used
the source paths printed by the helper, not just the recorder's cwd. Session-3 remained detached at
its original commit, with only task-owned ignored outputs added.

| Check | Result | Log/evidence |
|---|---|---|
| All-worktree environment check | Four pass outside sandbox | Console; restricted Julia got EBADF |
| Borrowed session-2 scoped checks | 61 passed, 363.11 s | `session-2-scoped.log` |
| Concurrent session-3 scoped checks | 52 passed, 349.92 s | session-3 `session-3-scoped.log` |
| Final session-2 helper + fixtures | 12 passed, 6.60 s | `final-session-2.log` |
| Concurrent final session-3 fixtures | 2 passed, 4.69 s | session-3 `final-session-3.log` |
| Both R/Julia context probes | Pass; paths asserted | Each session's `context-session-*.log` |
| Incompatible scratch manifest | Rejected before Pixi; no `.pixi` | Console and six rejection tests |
| Own isolated session-2 interpreter/import probe | Both paths resolve to session-2 | Console |
| Dependency metadata before/after | 1,177 hashes unchanged | `dependency-{before,after}.json` |
| Upstream provisioning config reader | `[]` | Console; supported empty list |
| `pixi run --as-is lint` | Pass | `lint.log` |
| `pixi run --as-is format-check` | Pass, 462 files already formatted | `format-check.log` |
| `git diff --check` | Pass | Console |

All pytest runs above have zero skips. Exact larger-check commands (after the documented borrower
invocation and `--`):

```powershell
python -m pytest tests/test_session_runtime.py tests/test_cli.py tests/test_spatial_geoms_parity.py -q -rs
python -m pytest tests/test_cli.py tests/test_spatial_geoms_parity.py -q -rs
```

The local-installation inventory command was
`pixi run --as-is python dev/scripts/check_env.py --all`. The isolated proof used
`pixi run --as-is python -B -c ...` and asserted that `sys.prefix` and `blueearth_cst.__file__` both
resolve inside session-2. The incompatible temporary manifest changes only its R pin from 4.4 to
4.5; a child that would fail if executed was never reached. No incompatible dependency was installed.

Final two fixture node IDs, executed in both checkouts (no missing-fixture skips):

```text
tests/test_spatial_geoms_parity.py::test_the_relationships_hold_on_a_really_built_project
tests/test_spatial_geoms_parity.py::test_the_incomparable_layers_really_are_incomparable_on_the_fixture
```

The final helper tests additionally reject wrong-checkout imports, wrong interpreters, and incompatible
contracts before requested checks execute; they preserve child exit status and handle CRLF/comments.
The larger CLI runs preceded a small helper-only follow-up for TOML comparison and local cache/depot
handling; the final 12/2 checks cover that delta. Workflow sources/calculations did not change.

R printed existing Windows `C.UTF-8` locale warnings; library loading and assertions passed.
The stock environment checker is useful for local installation inventory, not sufficient to prove
borrowing roots or loaded R/Julia packages; it invokes `Pkg.status()`, which also accesses registries.
The targeted context probes supply the missing claims. Metadata equality is installation evidence,
not a forensic hash of every package byte or a guarantee against arbitrary code mutating dependencies.

No test-fast landing gate, full suite, all-five execution, numerical baseline, Linux execution or push
CI was run: this is development-only tooling/configuration with scoped checks, not a landing or a
workflow qualification. The live validation ladder still selects any later integrated batch gates.

## Handoff

Implementation stays in session-2 for approval-based landing; primary only owns this retained evidence.
No shared infrastructure was modified. No infrastructure change is required: empty provisioning lists
and executable-mode borrowing are already available. A reusable launcher runtime-profile feature or
an explicit stable-runtime exception in shared provisioning guidance would be a separately authorized
upstream enhancement, not a dependency of this project-local implementation.

Before adopting the new default for fresh sessions, land the implementation with the required batch
gate and explicit approval. Do not delete existing environments to realize the estimate without a
separate retention/ownership decision. Preserve the two fixture seeds and independent run trees.
