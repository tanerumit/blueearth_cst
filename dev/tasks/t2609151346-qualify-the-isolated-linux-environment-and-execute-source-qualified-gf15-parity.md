---
title: Qualify the isolated Linux environment and execute source-qualified GF15 parity
type: todo-item
status: backlog
effort: 1
area: wf3 / platform
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — Provision a local WSL2/Linux environment, qualify an isolated pixi
> install there against the D7 source pins, and execute source-qualified E7
> parity for the GF15 return-level estimator `gf15-lmoments-c/1` on linux-64.
> **Why** — This is the **one D8 handoff 2/4 obligation R12 sealed without**.
> The estimator carries *bounded Windows acceptance only*; cross-platform
> acceptance requires source-qualified parity on every supported platform, and
> Windows evidence cannot satisfy it. Until this lands, any Linux run of WF4
> produces return levels from an unqualified estimator build.
> **Effort** — medium

## Status

**Outstanding, not failed.** Nothing was ever installed or executed on linux-64.
Owner deferred it on 2026-09-14, authorized Windows-only continuation, and ruled
it out of scope for the sealing session on 2026-09-15. It is boarded here so the
obligation outlives `t2609100916`, which closed with this line unticked.

## Why it is not just "run the tests on Linux"

D7 pins a **wheel** SHA-256, and the adapter verifies the installed
`lmoments3` `__init__.py` and `distr.py` digests before every fit
(`blueearth_cst/experiment/gev_lmoments.py`). A same-version conda-forge repack
is explicitly **unqualified** — that is why the Windows work used a separate
`windows-environment-pypi/` root with `lmoments3` in `[pypi-dependencies]`
rather than `[dependencies]`. The Linux environment has to reproduce that
property, not merely install the package.

Note also that `test_case/*_linux.yml` and `config/catalogs/*_linux.yml` exist
because data-catalog paths differ on Linux (AGENTS.md), and Julia is
juliaup-managed rather than in the pixi env.

## Acceptance

The Windows precedent is `evidence/gf15-production-integration/e7-parity-verdict.md`:
an independent `model-validator` verdict on exact fixed-tolerance parity,
refusal and diagnostic behaviour, with a wrong-result mutant that demonstrably
fails. Linux needs the same, at the same standard. Round one of the Windows
review **rejected** on a real warnings-retention defect, so a rubber-stamp pass
is not the expected outcome.

## Refs

- Accepted design D7/D8: `dev/milestones/r12/gf15-production-adapter-design.md`
- Windows Stage 1 environment record:
  `dev/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/`
- Integration verdict and its explicit exclusions:
  `dev/milestones/r12/implementation/evidence/gf15-production-integration/integration-verdict.md`

## Progress

- [ ] Provision WSL2/Linux with juliaup-managed Julia on PATH
- [ ] Build an isolated linux-64 pixi env with the D7-pinned `lmoments3` WHEEL,
      and record the installed `__init__.py` / `distr.py` digests
- [ ] Confirm the projection equality of `stage_environment` across platforms,
      or record precisely where it differs
- [ ] Execute the E7 parity matrix on linux-64 and retain the results separately
      from the Windows ones
- [ ] Obtain an independent model-validator verdict for linux-64
- [ ] Update `integration-verdict.md` and the validation map; only then may
      cross-platform acceptance be claimed
