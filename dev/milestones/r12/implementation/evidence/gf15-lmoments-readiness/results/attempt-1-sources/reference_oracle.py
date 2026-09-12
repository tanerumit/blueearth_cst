"""Independent Decimal references for fixed GF15 readiness controls only.

Constants: NIST DLMF 3.12, digit sequences A000796 and A001620 at OEIS.
Log-Gamma series and positive-real remainder bound: DLMF 5.11.1 and 5.11(ii).
No statistical package or estimator is imported by this reference module.
"""

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction
from math import comb

PI = Decimal(
    "3.141592653589793238462643383279502884197169399375105820974944592307816406"
    "286208998628034825342117067982148086513282306647093844609550582231725359408128"
)
EULER = Decimal(
    "0.577215664901532860606512090082402431042159335939923598805767234884867726"
    "777664670936947063291746749514631447249807082480960504014486542836224173997644"
)
CONSTANT_SOURCES = {
    "pi": "https://oeis.org/A000796/b000796.txt",
    "euler": "https://oeis.org/A001620/b001620.txt",
    "gamma_series_and_bound": "https://dlmf.nist.gov/5.11",
    "constant_truncation_absolute_bound": "1e-138",
}


def bernoulli_numbers(count: int) -> list[Fraction]:
    """Generate exact rational Bernoulli numbers by their defining recurrence."""
    result = [Fraction(1)]
    for n in range(1, count + 1):
        result.append(-sum(comb(n + 1, k) * result[k] for k in range(n)) / (n + 1))
    return result


def gamma_decimal(argument: Decimal) -> tuple[Decimal, dict]:
    """Evaluate positive-real Gamma using recurrence and bounded Stirling terms."""
    if not argument.is_finite() or argument <= 0:
        raise ValueError("Gamma argument must be finite and positive")
    shifted = argument
    recurrence = Decimal(0)
    shifts = 0
    while shifted < 100:
        recurrence += shifted.ln()
        shifted += 1
        shifts += 1
    value = (shifted - Decimal(".5")) * shifted.ln() - shifted
    value += (2 * PI).ln() / 2 - recurrence
    coefficients = bernoulli_numbers(60)
    terms = []
    for k in range(1, 31):
        coefficient = coefficients[2 * k] / (2 * k * (2 * k - 1))
        term = Decimal(coefficient.numerator) / Decimal(coefficient.denominator)
        term /= shifted ** (2 * k - 1)
        # The stricter truncation resolves cancellation in the near-zero controls.
        if abs(term) <= Decimal("1e-60"):
            return value.exp(), {
                "argument": str(argument),
                "shifted_argument": str(shifted),
                "shifts": shifts,
                "terms": terms,
                "omitted_term_bound": str(abs(term)),
                "bound_applies_to": "log Gamma truncation; positive real argument",
            }
        value += term
        terms.append({"k": k, "coefficient": str(coefficient), "term": str(term)})
    raise ArithmeticError("Gamma Stirling remainder budget exhausted")


def tau(shape: Decimal) -> Decimal:
    """Evaluate theoretical GEV L-skewness, preserving its two exact limits."""
    if shape == -1:
        return Decimal(1)
    if not shape:
        return 2 * Decimal(3).ln() / Decimal(2).ln() - 3
    return (
        2
        * (1 - (-shape * Decimal(3).ln()).exp())
        / (1 - (-shape * Decimal(2).ln()).exp())
        - 3
    )


def population_moments(shape: Decimal) -> tuple[list[Decimal], dict]:
    """Derive population moments at location zero and scale one independently."""
    if not shape:
        return [EULER, Decimal(2).ln(), tau(shape)], {"gamma": "exact Gumbel limit"}
    gamma, evidence = gamma_decimal(1 + shape)
    return [
        (1 - gamma) / shape,
        gamma * (1 - (-shape * Decimal(2).ln()).exp()) / shape,
        tau(shape),
    ], evidence


@dataclass(frozen=True)
class Interval:
    """Outward Decimal interval with directed basic and bounded transcendental ops."""

    lo: Decimal
    hi: Decimal

    @classmethod
    def point(cls, value) -> "Interval":
        """Convert a float exactly; integers and Decimals remain exact."""
        exact = (
            Decimal.from_float(value) if isinstance(value, float) else Decimal(value)
        )
        return cls(exact, exact)

    def __add__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        with localcontext() as context:
            context.rounding = ROUND_FLOOR
            lower = self.lo + other.lo
            context.rounding = ROUND_CEILING
            upper = self.hi + other.hi
        return Interval(lower, upper)

    __radd__ = __add__

    def __neg__(self) -> "Interval":
        return Interval(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        return self + (-other)

    def __rsub__(self, other) -> "Interval":
        return Interval.point(other) - self

    def __mul__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        with localcontext() as context:
            context.rounding = ROUND_FLOOR
            lower = min(a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
            context.rounding = ROUND_CEILING
            upper = max(a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
        return Interval(lower, upper)

    __rmul__ = __mul__

    def __truediv__(self, other) -> "Interval":
        other = other if isinstance(other, Interval) else Interval.point(other)
        if other.lo <= 0 <= other.hi:
            raise ArithmeticError("interval division includes zero")
        with localcontext() as context:
            context.rounding = ROUND_FLOOR
            lower = min(a / b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
            context.rounding = ROUND_CEILING
            upper = max(a / b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
        return Interval(lower, upper)

    def ln(self) -> "Interval":
        """Decimal ln is nearest-rounded; adjacent values enclose the true value."""
        if self.lo <= 0:
            raise ArithmeticError("nonpositive interval logarithm")
        return Interval(self.lo.ln().next_minus(), self.hi.ln().next_plus())

    def exp(self) -> "Interval":
        """Decimal exp is nearest-rounded; adjacent values enclose the true value."""
        return Interval(self.lo.exp().next_minus(), self.hi.exp().next_plus())

    def record(self) -> list[str]:
        """Return unrounded enclosure endpoints for serialization."""
        return [str(self.lo), str(self.hi)]


def tau_interval(shape: Decimal) -> Interval:
    """Bound theoretical L-skewness without general Decimal power."""
    if shape == -1:
        return Interval.point(1)
    log2, log3 = Interval.point(2).ln(), Interval.point(3).ln()
    if not shape:
        return 2 * log3 / log2 - 3
    return 2 * (1 - (-shape * log3).exp()) / (1 - (-shape * log2).exp()) - 3


def shape_reference(target: Decimal, precision: int) -> dict:
    """Solve the fixed-control shape equation with the accepted hard budgets."""
    with localcontext() as context:
        context.prec = precision
        lo, hi = Decimal(-1), Decimal(1)
        if not -1 < target < 1:
            raise ArithmeticError("shape target outside strict theoretical range")
        upper_doublings = 0
        while True:
            sign = tau_interval(hi) - target
            if sign.hi <= 0:
                break
            if sign.lo <= 0 or upper_doublings == 6:
                raise ArithmeticError("shape bracket sign/budget unresolved")
            hi *= 2
            upper_doublings += 1
        for iterations in range(257):
            if hi - lo <= Decimal("1e-40"):
                return {
                    "shape": str((lo + hi) / 2),
                    "bracket": [str(lo), str(hi)],
                    "precision": precision,
                    "iterations": iterations,
                    "upper_doublings": upper_doublings,
                }
            if iterations == 256:
                break
            mid = (lo + hi) / 2
            sign = tau_interval(mid) - target
            if sign.lo > 0:
                lo = mid
            elif sign.hi < 0:
                hi = mid
            else:
                raise ArithmeticError("shape bisection sign unresolved")
        raise ArithmeticError("shape bisection budget exhausted")


def parameter_reference(moments: list[float], precision: int) -> dict:
    """Invert fixed rounded moment inputs for validation, never for candidate fits."""
    with localcontext() as context:
        context.prec = precision
        l1, l2, t3 = map(Decimal.from_float, moments)
        evidence = shape_reference(t3, precision)
        c = Decimal(evidence["shape"])
        if not c:
            scale = l2 / Decimal(2).ln()
            location = l1 - EULER * scale
            gamma_evidence = {"gamma": "exact Gumbel limit"}
        else:
            gamma, gamma_evidence = gamma_decimal(1 + c)
            scale = l2 * c / (gamma * (1 - (-c * Decimal(2).ln()).exp()))
            location = l1 - scale * (1 - gamma) / c
        return {
            "parameters": {"c": str(c), "loc": str(location), "scale": str(scale)},
            "shape_evidence": evidence,
            "gamma_evidence": gamma_evidence,
        }


def log_cdf_standard(x: Decimal | Interval, c: Decimal) -> Interval:
    """Evaluate only the forward log-CDF, with outward support extensions."""
    if not c:
        x_interval = x if isinstance(x, Interval) else Interval.point(x)
        return -(-x_interval).exp()
    w = 1 - Interval.point(c) * x
    if w.hi <= 0:
        return Interval.point(0 if c > 0 else Decimal("-Infinity"))
    if w.lo <= 0:
        raise ArithmeticError("support endpoint membership unresolved")
    return -(w.ln() / c).exp()


def cdf_enclosure(
    parameters: dict, probability: float, width: Decimal, precision: int
) -> dict:
    """Bisect the forward CDF under the identical exact float64 parameter tuple."""
    with localcontext() as context:
        context.prec = precision
        c, location, scale = (
            Decimal.from_float(float(parameters[name]))
            for name in ("c", "loc", "scale")
        )
        if scale <= 0 or not all(v.is_finite() for v in (c, location, scale)):
            raise ArithmeticError("invalid quantile reference parameters")
        log_p = Interval.point(probability).ln()
        lo, hi = Decimal(-1), Decimal(1)
        expansions = [0, 0]
        for side in (0, 1):
            while True:
                difference = log_cdf_standard(lo if side == 0 else hi, c) - log_p
                if (side == 0 and difference.hi <= 0) or (
                    side == 1 and difference.lo >= 0
                ):
                    break
                if difference.lo <= 0 <= difference.hi or expansions[side] == 64:
                    raise ArithmeticError("CDF bracket sign/budget unresolved")
                if side == 0:
                    lo *= 2
                else:
                    hi *= 2
                expansions[side] += 1
        for iterations in range(2049):
            physical = location + scale * Interval(lo, hi)
            if physical.hi - physical.lo <= width:
                return {
                    "enclosure": physical.record(),
                    "standard_bracket": [str(lo), str(hi)],
                    "precision": precision,
                    "iterations": iterations,
                    "expansions": expansions,
                }
            if iterations == 2048:
                break
            mid = (lo + hi) / 2
            sign = log_cdf_standard(mid, c) - log_p
            if sign.hi < 0:
                lo = mid
            elif sign.lo > 0:
                hi = mid
            else:
                raise ArithmeticError("CDF bisection sign unresolved")
        raise ArithmeticError("CDF bisection budget exhausted")
