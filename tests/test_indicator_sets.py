"""Named indicator sets: selection parsing, closed set schema and resolution."""

import textwrap
from pathlib import Path

import pytest

from blueearth_cst.experiment import indicator_sets as sets
from blueearth_cst.experiment import metric_registry as registry
from blueearth_cst.experiment.indicator_sets import IndicatorSetError


def _source(text, set_id="example_subset", bundled=False):
    return sets.SetSource(set_id, Path(f"{set_id}.yml"), bundled, textwrap.dedent(text))


EXAMPLE = """
    schema_version: 1
    id: example_subset
    title: Example discharge subset
    description: Illustrative reuse, not an approved second scientific set.
    selection:
      indicators:
        - definition: q_annual_mean
        - definition: q_mean_annual_7day_min
    """

AUTHORED = """
    schema_version: 1
    id: example_subset
    title: t
    description: d
    selection:
      indicators:
        - id: high_flow
          title: High flow
          description: Alias of the annual p95.
          references: [Author 2020]
          calculation:
            method: annual_summary/1
            parameters: {variable: q, statistic: p95}
    """


def test_registry_covers_every_existing_definition_exactly():
    names = {
        item.name
        for token in ("q", "aet", "gwr", "precip", "snow", "overland_flow")
        for item in registry.declarations([token])
    }
    assert set(registry.DEFINITIONS) == names
    assert len(names) == 16
    for definition, (method, parameters, _) in registry.DEFINITIONS.items():
        assert registry.validate_calculation(method, parameters)[0] == definition
        assert registry.declaration_for(definition).name == definition


@pytest.mark.parametrize(
    ("method", "parameters"),
    [
        ("annual_summary/1", {"variable": "q", "statistic": "median"}),
        ("annual_summary/1", {"variable": "aet", "statistic": "mean"}),
        ("annual_summary/1", {"variable": "q"}),
        ("annual_rolling7_extreme/1", {"extreme": "min", "window": 7}),
        ("annual_min7_mean_ratio/1", {"variable": "q"}),
        ("unknown/1", {}),
    ],
)
def test_calculations_reject_unsupported_extra_or_missing_parameters(
    method, parameters
):
    with pytest.raises(ValueError):
        registry.validate_calculation(method, parameters)


def test_output_units_are_declared_not_inferred():
    units = {
        name: registry.output_units(registry.declaration_for(name))
        for name in registry.DEFINITIONS
    }
    assert units["q_baseflow_index"] == "1"
    assert units["precip_annual_total"] == units["aet_annual_total"] == "mm"
    assert units["snow_annual_max"] == "mm"
    assert units["overland_flow_annual_mean"] == units["q_annual_mean"] == "m3 s-1"


def test_default_preset_delegates_to_registry_declarations():
    path = sets.BUNDLED_ROOT / "default.yml"
    source = sets.SetSource("default", path, True, path.read_text(encoding="utf-8"))
    resolved = sets.resolve_set(source, ["q", "aet"])
    assert resolved.declarations == registry.declarations(["q", "aet"])
    assert all(item.equivalent_definition == "" for item in resolved.indicators)
    with pytest.raises(IndicatorSetError, match="no response variables"):
        sets.resolve_set(source, [])


def test_preset_is_reserved_for_the_bundled_default():
    text = EXAMPLE.replace(
        "  indicators:\n        - definition: q_annual_mean\n        - definition: q_mean_annual_7day_min",
        "  preset: current_default",
    )
    with pytest.raises(IndicatorSetError, match="only the bundled default"):
        sets.resolve_set(_source(text), ["q"])


def test_definition_selectors_reference_registered_declarations():
    resolved = sets.resolve_set(_source(EXAMPLE))
    assert [item.metric for item in resolved.indicators] == [
        "q_annual_mean",
        "q_mean_annual_7day_min",
    ]
    assert resolved.declarations[0] == registry.declaration_for("q_annual_mean")
    assert resolved.indicators[0].authored_references == ()


def test_authored_entry_keeps_registered_calculation_under_its_own_metric_key():
    item = sets.resolve_set(_source(AUTHORED)).indicators[0]
    registered = registry.declaration_for("q_mean_annual_p95")
    assert item.metric == "high_flow"
    assert item.equivalent_definition == "q_mean_annual_p95"
    assert item.authored_references == ("Author 2020",)
    assert item.references == ()
    assert item.declaration.statistic == registered.statistic == "q95"
    assert item.declaration.required_responses == registered.required_responses


@pytest.mark.parametrize(
    ("old", "new", "match"),
    [
        ("id: high_flow", "id: q_annual_mean", "equals a registered definition"),
        ("id: high_flow", "id: High", "must match"),
        ("references: [Author 2020]", "references: ['']", "nonempty strings"),
        ("statistic: p95}", "statistic: p95, units: mm}", "unsupported parameters"),
        ("          title: High flow\n", "", "exactly"),
    ],
)
def test_authored_entry_refusals(old, new, match):
    with pytest.raises(IndicatorSetError, match=match):
        sets.resolve_set(_source(AUTHORED.replace(old, new)))


def test_within_set_duplicate_calculation_contracts_are_refused():
    duplicate = AUTHORED.rstrip(" ") + "        - definition: q_mean_annual_p95\n"
    with pytest.raises(IndicatorSetError, match="share one calculation contract"):
        sets.resolve_set(_source(duplicate))
    repeated = EXAMPLE.rstrip(" ") + "        - definition: q_annual_mean\n"
    with pytest.raises(IndicatorSetError, match="repeats metric"):
        sets.resolve_set(_source(repeated))


@pytest.mark.parametrize(
    ("old", "new", "match"),
    [
        ("schema_version: 1", "schema_version: 2", "schema_version"),
        ("id: example_subset", "id: other", "differs from its selected name"),
        ("title: Example discharge subset", "title: ''", "title"),
        (
            "    - definition: q_annual_mean",
            "    - {definition: q_annual_mean, title: x}",
            "no overrides",
        ),
        (
            "    - definition: q_annual_mean",
            "    - definition: q_unknown",
            "unknown registered",
        ),
        (
            "description: Illustrative",
            "units: mm\n    description: Illustrative",
            "exactly",
        ),
        (
            "title: Example discharge subset",
            "title: a\n    title: b",
            "duplicate YAML key",
        ),
    ],
)
def test_closed_set_schema_refusals(old, new, match):
    with pytest.raises(IndicatorSetError, match=match):
        sets.resolve_set(_source(EXAMPLE.replace(old, new, 1)))


def test_parse_selection_defaults_and_custom_paths(tmp_path):
    custom = tmp_path / "indicator_sets" / "example_subset.yml"
    custom.parent.mkdir()
    custom.write_text(textwrap.dedent(EXAMPLE), encoding="utf-8")
    workflow = tmp_path / "wf4.yml"
    selection = sets.parse_selection(
        {
            "operations": ["indicators", "simulations"],
            "indicator_sets": ["default", "example_subset"],
            "indicator_set_definitions": {
                "example_subset": {"config_path": "indicator_sets/example_subset.yml"}
            },
        },
        workflow,
    )
    assert selection.operations == ("simulations", "indicators")
    assert [s.set_id for s in selection.sets] == ["default", "example_subset"]
    assert (
        selection.sets[0].bundled and selection.sets[0].path.parent == sets.BUNDLED_ROOT
    )
    assert selection.sets[1].path == custom.resolve()
    # The admitted bytes are captured; a later source edit cannot change them.
    custom.write_text("changed", encoding="utf-8")
    assert sets.resolve_set(selection.sets[1]).set_id == "example_subset"
    omitted = sets.parse_selection({}, workflow)
    assert omitted.operations == ("simulations", "indicators")
    assert [s.set_id for s in omitted.sets] == ["default"]


def test_simulations_only_validates_structure_without_opening_sets(tmp_path):
    selection = sets.parse_selection(
        {
            "operations": ["simulations"],
            "indicator_sets": [],
            "indicator_set_definitions": {"later": {"config_path": "missing.yml"}},
        },
        tmp_path / "wf4.yml",
    )
    assert selection.sets == () and not selection.indicators


@pytest.mark.parametrize(
    ("settings", "match"),
    [
        ({"operations": None}, "nonempty list"),
        ({"operations": "indicators"}, "nonempty list"),
        ({"operations": []}, "nonempty list"),
        ({"operations": ["indicators", "indicators"]}, "duplicate"),
        ({"operations": ["metrics"]}, "unknown entries"),
        ({"indicator_sets": None}, "nonempty list"),
        ({"indicator_sets": []}, "nonempty list"),
        ({"indicator_sets": ["default", "default"]}, "duplicate"),
        ({"indicator_sets": ["con"]}, "Windows reserved"),
        ({"indicator_sets": ["../x"]}, "must match"),
        ({"indicator_sets": ["nope"]}, "unknown indicator set"),
        ({"indicator_set_definitions": None}, "mapping"),
        (
            {"indicator_set_definitions": {"default": {"config_path": "x.yml"}}},
            "collides",
        ),
        ({"indicator_set_definitions": {"x": {"config_path": ""}}}, "exactly"),
        ({"indicator_set_definitions": {"x": {"config_path": "a", "y": 1}}}, "exactly"),
        (
            {"operations": ["indicators"], "operation": "metrics-only"},
            "legacy interface",
        ),
        ({"indicator_sets": ["default"], "metrics": ["q"]}, "legacy interface"),
    ],
)
def test_parse_selection_refusals(tmp_path, settings, match):
    with pytest.raises(IndicatorSetError, match=match):
        sets.parse_selection(settings, tmp_path / "wf4.yml")


def test_legacy_operation_maps_to_default_set():
    both = sets.legacy_selection({"operation": "simulate-and-metrics"})
    only = sets.legacy_selection({"operation": "metrics-only"})
    assert both.operations == ("simulations", "indicators") and both.legacy
    assert only.operations == ("indicators",)
    assert [s.set_id for s in only.sets] == ["default"]


def test_required_variables_is_the_union_across_sets():
    resolved = [
        sets.resolve_set(_source(EXAMPLE)),
        sets.resolve_set(
            sets.SetSource(
                "default",
                sets.BUNDLED_ROOT / "default.yml",
                True,
                (sets.BUNDLED_ROOT / "default.yml").read_text(encoding="utf-8"),
            ),
            ["aet", "q"],
        ),
    ]
    assert sets.required_variables(resolved) == ["q", "aet"]
