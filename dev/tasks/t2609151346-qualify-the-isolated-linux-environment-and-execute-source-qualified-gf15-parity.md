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

## This is why `main`'s CI is RED, and what that costs

Observed 2026-09-15 on run `34971087417` (the `feat/wp3-improvements` merge),
and on every ubuntu leg since the estimator landed. Windows passes; ubuntu fails
with exactly one test:

```
tests/test_gev_lmoments.py::test_quantile_controls_reproduce_the_retained_bit_patterns
AssertionError: positive_.50
assert '3ffe6fa8c7aa7b6c' == '3ffe6fa8c7aa7b6a'
```

Two ULP in a float64 quantile. The retained controls in
`results/attempt-2/numerical-controls.json` are compared as BIT PATTERNS, and
they were frozen on Windows, so the test is asserting cross-platform bit
identity that the estimator has never been qualified for. The failure is the
bounded Windows acceptance showing up as a red gate -- it is not a regression,
and no commit since the seal caused it.

**The cost is not the red badge, it is what the red badge hides.** While ubuntu
fails for a known accepted reason, a GENUINELY new ubuntu failure lands as the
same red X and nobody looks twice. AGENTS.md's "after a push, read the run it
triggered" is the rule that makes a local `test-fast` safe, and that rule is
currently unenforceable on the ubuntu leg.

So this item now blocks two things, not one: Linux qualification of the
estimator, AND the usefulness of CI's ubuntu leg for every other change.

### Interim gate: SKIP off win32 (landed 2026-09-15)

Owner ruled to fix the ubuntu failure. Two tests in `tests/test_gev_lmoments.py`
now carry `_UNQUALIFIED_PLATFORM`, a `skipif(sys.platform != "win32")` whose
reason names this item:

- `test_quantile_controls_reproduce_the_retained_bit_patterns` -- the failing one.
- `test_quantile_controls_discriminate_against_mutants` -- which was passing off
  win32 FOR THE WRONG REASON. It counts controls whose bits do not match, so the
  platform's own libm noise satisfied `failures > 0` and it discriminated
  nothing while reporting green.

**A ULP tolerance was considered and rejected**, though it looks like the more
sophisticated option. Two reasons. It needs a bound that cannot be determined
from Windows -- the assertion sits inside the loop, so the observed evidence is
one control of 44 and the worst-case deviation is unknown; any number picked
here is extrapolation, and too tight a bound costs a CI round-trip to learn one
more data point. More importantly, a tolerance variant under the same test name
is a DIFFERENT assertion wearing the bit-exact one's name, reporting green on
the very platform where this item records the estimator as unqualified. The
skip states the true thing and prints it in the CI summary.

Deliberately NOT touched: `test_branch_controls_reproduce_the_pinned_inversion`
passes bit-exactly on ubuntu today. That is evidence the inversion IS
bit-reproducible there, not luck to be corrected, and replacing a working exact
assertion with anything weaker is strictly less coverage.

No control, no estimator code and no retained evidence was modified. On win32
the module asserts exactly what it asserted at the seal -- verified as 57 passed
before and after, with no skips appearing.

**When this item lands, delete both skips.** `_UNQUALIFIED_PLATFORM` exists only
to be removed; nothing else about those tests needs to change.

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
