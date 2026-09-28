---
verdict: approve
doc_version: design-v4.md
scope: [ext2-1, ext2-2, ext2-3]
findings: []
---

# GF15 v4 scoped independent verification

Date: 2026-09-12. Reviewer: model-validator. Frozen design SHA-256:
`90CE735AF1C15AFB964194C78A24F47ECC0BC7F62D315D0FE5D22F70F6792EE9`.

Approve the owner-authorized v3-to-v4 repair at design level. All three finding
contracts are resolved; no blocking, major or minor delta finding remains.
This is a scoped verification, not a third full external review, G2 approval,
implementation-readiness acceptance or authorization to execute the candidate.

| Original ID | Resolution assessment | Evidence and limit |
|---|---|---|
| ext2-1 major | Resolved in proposal | D6 compares the actual adapter float64 quantile with a forward-CDF-derived enclosure under the same exact float64 parameters and probability. It retains the normalized quantile tolerance, independently checks physical parameters, bounds reference error, and freezes per-row evidence. No probability-space threshold or additional ulp allowance survives. Implementation and passage remain unexecuted Stage 1 requirements. |
| ext2-2 minor | Resolved | D5 explicitly gives original population gates precedence, computes the two nonzero population shape discrepancies first and completes all three population controls before freezing characterization. The overlapping tau(.2) shape result is gated; no tau(-.2) branch-table entry is invented. No original tolerance is changed. |
| ext2-3 minor | Resolved | D5 specifies the exact mathematical lower endpoint, initial upper endpoint, six deterministic doublings, a justified maximum endpoint, 256-step bisection limit and diagnostic stop behavior. It distinguishes the closed oracle bracket from the strict fitted finite-mean domain. This is fixed-control validation only. |

The complete file comparison confines changes to D5/D6 and forced version,
status and revision references. D1/D2 estimator and acceptance contracts, D3
GF15 criteria, support-policy scope and uncertainty treatment are unchanged.
The latest ledger dispositions accurately describe proposal repairs pending
this verification; the owner-arbitration section supplies the authority for
these three changes. Prior external findings are not regraded by this review.

## Mathematical and implementation assessment

**Independence and coordinates.** Bisection using forward-CDF signs does not
reuse the adapter inverse expression or SciPy PPF. Conditioning on the same
recorded float64 tuple separates quantile implementation error from D5's
parameter approximation error. Exact float conversion includes p: the binary
value used for .9 must not silently become exact decimal .9. The physical
reference uses the recorded rounded physical parameters; dividing physical
error and enclosure width by positive s gives the specified normalized units.
This checks the conditional quantile and affine mapping, not fitted accuracy.

**CDF and endpoints.** Substitution xi=-c gives w=1-c*x and
log F=-exp(log(w)/c) for nonzero c on support, with log F=-exp(-x)
at c=0. Thus xi>0 has a lower endpoint with F=0, and xi<0 has an upper
endpoint with F=1, exactly as v4 states. Both CDFs increase with x.
Endpoint extension provides bracketing signs without taking log of w<=0.
The rounding-cell rule permits only supported nearest-rounding explanations
that also meet the quantile bound; it neither excuses an arbitrary unsupported
value nor introduces a new per-fit sample-support refusal.

**Brackets and conditioning.** For all fixed shape controls, t3 is strictly
between -1 and 1. The exact tau(-1)=1 lower sign and v4's algebraic
tau(64)<-.98 upper sign enclose every fixed target. The maximum starting width
is 65; 65/2^256 is less than 1e-75, well below the 1e-40 termination target.
The c=0 continuous limit remains part of the existing oracle contract.

The CDF x bracket is also generous for its specified p=.5,.9 and c>-1.
Writing a=-log(-log p)>0 for this analytical feasibility argument gives
x=integral from 0 to a of exp(-c*t) dt. Therefore 0<x<exp(a)-1<9
over that domain. An upper endpoint of 16 already suffices in exact arithmetic;
64 permitted doublings cannot create the old fixed-control representability
obstruction. This derivation is a bracket assessment, not permission for the
reference implementation to compute its root through the inverse formula.
The 2,048 bisection budget is generous for ordinary fixed-control parameter
scales, but actual rounded tuples and interval conditioning still require
Stage 1 evidence. In particular, very small nonzero c and endpoint cancellation
require careful arithmetic; the design correctly supplies a stop rather than
an unsupported universal convergence guarantee.

**Enclosure and error budget.** Two valid overlapping enclosures, each of
width at most 1e-30*M, have a hull no wider than 2e-30*M, where
M=max(1,abs(returned normalized quantile)). Relative to T=1e-10*M this
is at most 2e-20*T. Using maximum endpoint distance for pass and minimum
distance for fail is conservative for every enclosed root. The remaining
case is explicitly unresolved, so reference uncertainty cannot manufacture
a pass or silently enlarge the tolerance. Display rounding is outside the
gate. The same logic applies after physical errors and widths are divided
by s. Large probability residuals caused by steep density are now diagnostics,
which resolves the identified false-refusal mechanism.

**Declared environment.** Python's standard-library Decimal supplies exact
float conversion, directed basic arithmetic, correctly rounded ln/exp, and
adjacent representable Decimal values. These suffice to implement the stated
outward intervals without another package. The implementation must actually
compose bounds through ln/exp and signed arithmetic; merely changing context
rounding does not direct ln/exp, and treating general Decimal power as an
exactly rounded primitive would not establish the specified enclosure.
These are consequences of the existing enclosure requirement, not additional
design repairs. [Python 3.12 Decimal documentation](https://docs.python.org/3.12/library/decimal.html)
documents the required primitives and power caveat. The live documentation
renders as 3.12.14; this verifies the API contract, not execution under the
prospectively pinned 3.12.13 environment.

## Evidence boundary and handoff

Reviewed the complete v3/v4 delta, the three original round-2 findings, latest
ledger rows and binding owner arbitration. Independently checked the algebra,
budget ratios and bracket bounds above. SHA-256 inspection matches the supplied
frozen v4 digest. No candidate fit, retained-data benchmark, package installation,
numerical oracle implementation, production change or full code suite was run.
The earlier driver Decimal probe is bounded evidence for the superseded
probability-space defect; it is not evidence that v4 controls have passed.
Verification posture: rapid, proposal-only; prospective numerical contract
reviewed analytically, existing scientific results unaffected.

Stage 1 must still implement and independently review interval propagation,
exact conversions, endpoint comparisons and normalized physical widths; freeze
the actual tuples and both precision passes; and demonstrate all original
population gates and new controls. An unresolved interval sign, exhausted
budget or near-threshold ambiguity may conservatively stop readiness. No
evidence here establishes their incidence, runtime cost or actual package
control passage. Such stops remain readiness failures, never candidate sample
refusals or authority to widen tolerances.

The approved delta is a falsifiable, implementable validation specification
for the fixed controls, with the original scientific scope preserved. It does
not establish candidate fit-for-purpose status, GF15 success, sampling-error
bounds, fresh-seed stability or adequacy for dependent/nonstationary basin
data; those limitations remain unchanged. No assurance from an unimplemented
reference is claimed.
