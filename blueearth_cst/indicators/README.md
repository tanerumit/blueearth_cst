# Independent indicator module

This module consumes retained daily responses and returns in-memory values. It needs Python, NumPy and
pandas; qualified return levels additionally need the production-pinned lmoments3 and SciPy dependencies.
It does not load a model, remove warm-up, select simulation runs, read project configuration or publish files.
WF4 owns those operations. Input metadata states units, interval labels, missingness and location order.

| File | Reader / responsibility |
|---|---|
| `contract.py` | Authors and callers: inputs, declarations, context, results, scalar diagnostic tables |
| `series.py`, `temporal.py` | Adapters: validate aligned daily inputs and explicit references |
| `loader.py`, `validation.py` | Callers: trusted discovery, closed parameters, evaluation and checking |
| `sets/<set>/registry.py` | Authors: indicator names, explicit parameter values, units and assumptions |
| `sets/<set>/calculations.py` | Authors: formulas and callable-keyed `PARAMETERS` |
| `sets/<set>/checks.py` | Authors: independent expected arithmetic and optional diagnostic checks |
| `sets/<set>/README.md` | Authors/users: set-specific interpretation and limitations |
| `extremes.py`, `gev_lmoments.py` | Shared extraction and qualified range-normalized estimator |

## Plain Python

```python
from datetime import timedelta
import numpy as np
import pandas as pd
from blueearth_cst.indicators import ResponseSeries, resolve, evaluate, check

values = np.array([1., 2., 3., 4.])
series = [ResponseSeries(
    run_id="member-1", variable="q", location_id="gauge", location_ordinal=0,
    time=pd.date_range("2001-01-01", periods=len(values)), calendar="standard",
    timestep=timedelta(days=1), time_label="interval_end", units="m3 s-1",
    values=values, missing=np.isnan(values),
)]
indicator = resolve("default", "annual_summary/1", {"variable": "q", "statistic": "mean"})
result = evaluate(indicator, series, anchor="YE-SEP")
receipt = check(indicator, series, result, anchor="YE-SEP")
assert result.values["gauge"] == 2.5
```

`evaluate(..., expected_run_ids=[...], group=True)` averages run indicators with equal member weights and
NaN propagation. Bundle indicators pool member-local blocks and always require explicit qualification data
through `validation=...`. The WF4 adapter supplies its verified declaration; this module never discovers
workflow files. `reference_month_mean/1` requires an explicit resolved reference from
`temporal.resolve_month_reference`; callers supply the configured reference membership/location.

## Add a calculation

Add trusted code under a set package. User YAML selects declarations; it cannot import arbitrary code.
Keep `__init__.py`, `registry.py`, `calculations.py`, `checks.py` and `README.md` in each set.
Put a formula in `calculations.py`; it receives `(declaration, responses, context)` and returns
`IndicatorResult(values=pd.Series(...))`, indexed by location. Add its one parameter specification to local
`PARAMETERS`, keyed by the callable. Every parameter value is explicit in the registration; unknown fields
and missing fields fail before evaluation. Finite numeric constraints can be predicates with explanatory
docstrings; method-specific conditional rules belong in local `validate(function, parameters)`.

Register it with keyword arguments, for example:

```python
Indicator(
    id="daily_median", calculate=daily_median, parameters={},
    input=ResponseRequirement("q", "m3 s-1"), units="m3 s-1",
    description="Median of retained daily discharge values.",
)
```

Add the callable to the local `METHODS` mapping with a readable versioned selector. There is no shared
statistic list to edit and no required legacy equivalent. New registrations use `statistic="local"`
unless preserving an existing scientific statistic. The selected set plus indicator name disambiguate aliases.
`ASSUMPTIONS` declares fixed choices once per set; these are descriptions, never configurable policy objects.
The water-year anchor remains an explicit validated context input. A new group policy requires explicit
review; the supplied default group behavior is equal-weight member means with undefined propagation.

Implement `checks.expected(declaration, responses, context, *, group=False)` independently of production
calculations, returning a location-indexed Series. The generic checker compares values with
`rtol=1e-10, atol=1e-12` and verifies estimator identity for fitted indicators. Optional
`checks.check_result(declaration, responses, result, context, *, group=False)` validates method-owned
metadata or diagnostic tables. Do not calculate an expected answer by calling the production formula.

Diagnostics are tuples of `DiagnosticTable(name, data)` with unique nonempty names, string columns and
scalar string/number/bool/None cells. Native NaN represents an undefined numeric cell. Nested lists,
tuples, dictionaries and complex values are rejected. A nonannual event example defines events as
consecutive daily values strictly above an explicit threshold; missing days break an event. Its scalar is
mean duration in days and its named `events` table records each event duration. No events yields an undefined
scalar, explanatory metadata and an empty table. The isolated authoring fixture in
`tests/test_indicators_module.py` exercises this and daily median without changing the loader/checker.

## Identity and compatibility

Implementation revisions hash actual contributing execution source bytes. Checker modules have separate
hashes and do not change execution identity. The WF4 publication layer versions its exported schemas and
retains historical readers. Moving code changes implementation identity even when numerical values match.
Legacy declarations hash their fixed calculation owner (`default` or `flow_regime`); WF4 requests inventory
only selected calculation packages and their imported dependencies, alongside shared execution code.
Adding or editing an unrelated set does not invalidate existing selections. Changes to shared code or
reused formulas still invalidate dependent selections. Legacy statistic adaptation uses fixed owners so a
new package cannot replace an existing calculation through discovery order.
Compatibility imports remain in `experiment.indicator_registry` and `experiment.gev_lmoments`.
`experiment.response_series` remains byte-identical for retained-response reader identity; its existing
instances satisfy this module's structural input contract.

Calculation errors preserve their exception types, causes and structured estimator refusals, while adding
set/indicator/location context. Undefined returned scalars, unavailable variables, insufficient blocks,
unqualified probabilities and unexpected programming faults remain distinct. Evaluation never converts an
unexpected exception into a successful or scientifically undefined result.
