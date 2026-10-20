# Forcing unit admission

Last updated: 2026-10-20

Use this reference when changing historical climate catalogs or interpreting generated forcing.
The authoritative binding and admission logic are
`blueearth_cst/climate_analysis/prepare_climate_data_catalog.py::resolved_unit_interpretation`.

## Reviewed variables

The daily binding covers `precip`, `temp`, `temp_min`, `temp_max`, `press_msl`, `kin` and `kout`.
The adapter is rejected if a reviewed conversion is missing or changed, if an extra conversion affects
a reviewed variable, or if another native variable is renamed onto a reviewed name.
Unconsumed variables may be present; catalog shape alone is not a scientific compatibility requirement.

CHIRPS has a separate exact precipitation/time-shift check and requires no precipitation scaling.
It inherits the reviewed ERA5 auxiliaries through the existing extraction path.
Do not relax that branch merely because the general daily binding permits surplus variables.

## Provenance and verification

The returned `UnitInterpretation` records the binding revision, units and evidence identifying the selected
source and catalog/extraction hashes. Keep exact conversion values and revision strings in the owning code.
Review the arithmetic before changing them; source attributes alone do not prove the values' units.

`tests/test_prepare_climate_data_catalog.py` exercises admission and rejection.
[The retained forcing-unit investigation](../records/milestones/r12/implementation/evidence/p1-forcing-units.md)
preserves the numerical/source evidence. Apply the [validation ladder](validation-ladder.md) when a change
can alter values.
