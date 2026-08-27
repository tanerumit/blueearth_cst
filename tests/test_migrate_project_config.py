"""The v1→v2 transforms, each tested where it can go silently wrong.

`scripts/migrate_project_config.py` executes
`config/migrations/v1_to_v2.yml`. The mapping's own completeness is
`test_migration_mapping.py`'s job; this module covers the transforms it names.

The bias throughout: assert the case that would produce a VALID config with the
wrong numbers, because that is the failure a migration tool uniquely enables.
A transform that raises is visible; one that quietly halves a grid is not.
"""

from __future__ import annotations

import pathlib

import pytest

from scripts.migrate_project_config import (
    MigrationError,
    bool_to_enum,
    iso_to_year,
    list_to_named_windows,
    list_to_preference_group,
    load_mapping,
    pair_to_window,
    scalar_to_var_mapping,
    set_path,
    step_num_to_n_levels,
)

#: The v1 SET the rewriter migrates, kept because `test_case/` is v2 now.
#: `tests/data/presplit/` is the PRE-R13 whole-document shape and cannot
#: stand in for it — the rewriter takes a split set.
V1_SPLIT = "tests/data/v1_split"


class TestStepNumToNLevels:
    """`C-31` — the one transform whose failure mode is silent."""

    @pytest.mark.parametrize(
        ("step_num", "n_levels"), [(0, 1), (1, 2), (2, 3), (9, 10)]
    )
    def test_it_adds_exactly_one(self, step_num, n_levels):
        assert step_num_to_n_levels(step_num) == n_levels

    def test_the_seed_grid_is_preserved(self):
        """The falsifier, stated as the shipped values.

        `temp: 1, precip: 2` was a six-member grid. If the rewriter renamed
        without adding, it would become 1x2 = 2 members — a VALID config, a
        third of the runs, and nothing anywhere would report it.
        """
        temp = step_num_to_n_levels(1)
        precip = step_num_to_n_levels(2)
        assert temp * precip == 6

    @pytest.mark.parametrize("bad", [True, False, 1.5, "2", None, -1])
    def test_it_refuses_what_is_not_a_step_count(self, bad):
        with pytest.raises(MigrationError):
            step_num_to_n_levels(bad)


class TestIsoToYear:
    """`C-70` / `C-71` — refusing beats truncating."""

    def test_a_whole_year_window_converts(self):
        assert iso_to_year(
            {"starttime": "2000-01-01T00:00:00", "endtime": "2016-12-31T00:00:00"}
        ) == {"start": 2000, "end": 2016}

    @pytest.mark.parametrize(
        "window",
        [
            {"starttime": "2000-06-01T00:00:00", "endtime": "2016-12-31T00:00:00"},
            {"starttime": "2000-01-01T00:00:00", "endtime": "2016-06-30T00:00:00"},
            {"starttime": "2000-01-01T12:00:00", "endtime": "2016-12-31T00:00:00"},
        ],
    )
    def test_a_part_year_window_is_REFUSED_not_rounded(self, window):
        """No year pair reproduces it, so there is nothing honest to emit.

        Rounding would hand back a run over a different period than the one
        configured, with nothing said — the failure mode a migration must not
        have.
        """
        with pytest.raises(MigrationError, match="whole-year aligned"):
            iso_to_year(window)

    def test_a_missing_endpoint_names_it(self):
        with pytest.raises(MigrationError, match="endtime"):
            iso_to_year({"starttime": "2000-01-01T00:00:00"})


class TestBoolToEnum:
    """`C-32` — the enum comes from the MAPPING, which is why this is data-driven."""

    def test_true_ramps_and_false_steps(self):
        enum = ["transient", "step"]
        assert bool_to_enum(True, enum=enum) == "transient"
        assert bool_to_enum(False, enum=enum) == "step"

    def test_the_other_spelling_works_the_same_way(self):
        """The unresolved pair. Ruling `C-32` must not need a code change."""
        enum = ["transient", "constant"]
        assert bool_to_enum(True, enum=enum) == "transient"
        assert bool_to_enum(False, enum=enum) == "constant"

    def test_the_mapping_is_what_supplies_it(self):
        """Whatever the mapping says today, the transform must accept it."""
        mapping = load_mapping()
        row = next(r for r in mapping["rows"] if r["id"] == "C-32")
        assert bool_to_enum(True, enum=row["enum"]) == "transient"
        assert bool_to_enum(False, enum=row["enum"]) in row["enum"]

    @pytest.mark.parametrize("bad", ["true", 1, None, "transient"])
    def test_a_non_boolean_is_refused(self, bad):
        with pytest.raises(MigrationError):
            bool_to_enum(bad, enum=["transient", "step"])


class TestWindowShapes:
    def test_pair_to_window(self):
        assert pair_to_window([2000, 2014]) == {"start": 2000, "end": 2014}

    @pytest.mark.parametrize("bad", [[2000], [2000, 2014, 2020], 2000, None])
    def test_pair_to_window_refuses_a_shape_it_cannot_read(self, bad):
        with pytest.raises(MigrationError):
            pair_to_window(bad)

    def test_named_windows_carry_their_names(self):
        """`C-61`: the name becomes a figure directory, so dropping it moves output."""
        out = list_to_named_windows({"mid": [2046, 2054], "far": [2070, 2100]})
        assert out == [
            {"start": 2046, "end": 2054, "name": "mid"},
            {"start": 2070, "end": 2100, "name": "far"},
        ]

    def test_named_windows_keep_declaration_order(self):
        """The v1 mapping's order was incidental; the v2 list's is authored."""
        out = list_to_named_windows({"z": [2000, 2010], "a": [2020, 2030]})
        assert [w["name"] for w in out] == ["z", "a"]


class TestMemberAndObservationShapes:
    def test_members_become_a_preference_group(self):
        assert list_to_preference_group(["r1i1p1f1"]) == {"preference": ["r1i1p1f1"]}

    def test_observations_key_by_variable(self):
        assert scalar_to_var_mapping(
            "obs.csv", outvars=["river discharge", "precipitation"]
        ) == {"river discharge": "obs.csv"}

    def test_an_unset_observation_stays_unset(self):
        """`null` is a declared absence and must not become `{discharge: None}`."""
        assert scalar_to_var_mapping(None, outvars=["river discharge"]) is None

    def test_it_refuses_when_the_outvar_is_not_declared(self):
        """The loader would reject the result, so the rewriter refuses first."""
        with pytest.raises(MigrationError, match="model.outvars"):
            scalar_to_var_mapping("obs.csv", outvars=["precipitation"])


class TestCollisionPolicy:
    def test_refuse_is_the_default_and_it_refuses(self):
        doc = {"engine": {"build_config": "existing.yml"}}
        with pytest.raises(MigrationError, match="already exists"):
            set_path(
                doc,
                "engine.build_config",
                "new.yml",
                on_collision="refuse",
                row_id="C-22",
            )

    def test_keep_existing_leaves_the_destination_alone(self):
        doc = {"compute": {"batch_size": 4}}
        set_path(
            doc, "compute.batch_size", 99, on_collision="keep_existing", row_id="C-34"
        )
        assert doc["compute"]["batch_size"] == 4

    def test_intermediate_groups_are_created(self):
        doc = {}
        set_path(
            doc,
            "engine.build_config",
            "x.yml",
            on_collision="refuse",
            row_id="C-22",
        )
        assert doc == {"engine": {"build_config": "x.yml"}}


class TestWholeSetMigration:
    """The mapping applied to a real shipped v1 set.

    These are the cases the unit tests above cannot reach: every one of them is
    about ORDER, and order only goes wrong once several rows touch one tree.
    Both were live bugs, found by running the mapping against
    `test_case/snake_config_rapid.yml` rather than against a fixture built to
    suit it.
    """

    @staticmethod
    def _migrate():
        import yaml

        from scripts.migrate_project_config import migrate_set

        root = pathlib.Path(__file__).resolve().parent.parent
        t1 = yaml.safe_load(
            (root / V1_SPLIT / "snake_config_rapid.yml").read_text(encoding="utf-8")
        )
        t2 = {
            wf: (
                yaml.safe_load(
                    (root / V1_SPLIT / f"snake_config_rapid_{wf}.yml").read_text(
                        encoding="utf-8"
                    )
                )
                or {}
            )
            for wf in (
                "analyze_climate",
                "build_model",
                "analyze_projections",
                "run_stress_test",
            )
        }
        return migrate_set(
            t1,
            t2,
            load_mapping(),
            outvars=["river discharge", "actual evapotranspiration"],
        )

    def test_the_contents_of_shared_survive_its_deletion(self):
        """`C-01` deletes `shared:`; SIX other rows move keys out of it first.

        The bug this pins: ordered by depth alone, `C-01` is the shallowest live
        move in the mapping and ran FIRST — deleting the section before anything
        was extracted. The result was a valid v2 config with no basin, no
        climate window, no outvars and no seed, and nothing reported it. Deletes
        are sorted last for exactly this reason.
        """
        t1, t2, _ = self._migrate()
        assert "shared" not in t1
        # The four keys this config's `shared:` actually declared, each landing
        # where its own row sends it. `seed` is deliberately NOT asserted: the
        # rapid config never set it, and a migration that invented one would be
        # pinning a value the project had chosen to inherit.
        assert t1["basin"]["region"]  # C-10
        assert t1["climate"]["selected"] == "era5"  # C-44
        assert t1["climate"]["window"] == {"start": 2000, "end": 2016}  # C-70
        assert t1["model"]["outvars"]  # C-19

    def test_a_key_the_project_never_declared_is_not_invented(self):
        """The rapid config sets no `shared.seed`, so v2 must not carry one.

        Writing the shipped default here would convert a config that INHERITS a
        value into one that PINS it, and the two diverge the next time the
        default moves — silently, since both are valid.
        """
        _, t2, _ = self._migrate()
        assert "seed" not in t2["run_stress_test"]

    def test_the_t1_top_level_is_exactly_the_closed_set(self):
        """The loader closes T1; a leftover section would be refused at parse."""
        from blueearth_cst.shared.config_composition import T1_TOP_LEVEL

        t1, _, _ = self._migrate()
        assert set(t1) == set(T1_TOP_LEVEL)

    def test_a_section_rename_happens_before_the_keys_inside_it(self):
        """`C-68` renames `stress_test:`; `C-31`/`C-32` move keys within it.

        In register order the nested rows ran first and created
        `climate_perturbations` as a side effect, so `C-68` then collided with a
        destination the migration had just made. Parents sort first, and each
        child's path is rewritten through the renames already applied.
        """
        _, t2, _ = self._migrate()
        wf3 = t2["run_stress_test"]
        assert "stress_test" not in wf3
        perturbations = wf3["climate_perturbations"]
        assert perturbations["temp"]["n_levels"] == 2  # step_num 1 + 1
        assert perturbations["precip"]["n_levels"] == 2
        assert "step_num" not in perturbations["temp"]
        assert perturbations["temp"]["trajectory"] in ("transient", "step", "constant")
        # the mean/max ranges rode along with the section rename
        assert perturbations["temp"]["mean"]["max"]

    def test_the_collapsed_window_is_the_one_the_run_actually_used(self):
        """`C-67`, and the reason the transform keeps retired arithmetic.

        `horizontime_climate: 2050` with `run_length: 8` ran over 2046..2054 —
        NINE calendar years, because the halves snapped outward. A migration
        that emitted 2046..2053, or 2050..2058, would silently change the period
        every existing project simulates.
        """
        _, t2, _ = self._migrate()
        assert t2["run_stress_test"]["simulation_window"] == {
            "start": 2046,
            "end": 2054,
        }
        assert "horizontime_climate" not in t2["run_stress_test"]
        assert "run_length" not in t2["run_stress_test"]


class TestTheTransaction:
    """D-11.2b and D-14.9 — the properties that only a real write can show."""

    @staticmethod
    def _copy_set(tmp_path, stem, source_dir, glob=None):
        """Copy a whole config SET into tmp_path and return its T1 path.

        ``glob`` is explicit because the two shipped sets are named differently:
        `test_case` uses `snake_config_rapid_<workflow>.yml` while
        `config/templates` uses `snake_config.<workflow>.template.yml`, so no
        single prefix pattern finds both.
        """
        root = pathlib.Path(__file__).resolve().parent.parent
        import shutil

        for src in (root / source_dir).glob(glob or f"{stem}*.yml"):
            shutil.copy(src, tmp_path / src.name)
        return tmp_path / f"{stem}.yml"

    def test_every_comment_survives_the_rewrite(self, tmp_path):
        """D-14.9's first falsifier, and the reason this tool uses ruamel.

        A `safe_dump` rewriter passes every other check in this file while
        deleting four fifths of the shipped template. Asserting the count is
        UNCHANGED rather than a fixed number: the design says "86 of the 109
        lines" and the template today has 68 comment lines, so a literal would
        pin a stale figure instead of the property.

        This failed on the first real run — `analyze_projections` lost all five
        of its comments, because ruamel hangs a comment off its key's PARENT
        mapping and every key in that file is renamed.
        """
        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(
            tmp_path,
            "snake_config.template",
            "config/templates",
            glob="snake_config.*.yml",
        )
        before = {
            path.name: path.read_text(encoding="utf-8").count("\n#")
            + path.read_text(encoding="utf-8").startswith("#")
            for path in tmp_path.glob("*.yml")
        }
        migrate_project(t1, write=True)
        for name, count in before.items():
            after = (tmp_path / name).read_text(encoding="utf-8")
            assert after.count("\n#") + after.startswith("#") == count, name

    def test_the_originals_are_kept_as_v1_bak(self, tmp_path):
        """A migration a user wants to undo is one they can undo."""
        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        migrate_project(t1, write=True)
        backups = sorted(p.name for p in tmp_path.glob("*.v1.bak"))
        assert len(backups) == 5, backups
        assert "snake_config_rapid.yml.v1.bak" in backups

    def test_the_migrated_set_composes(self, tmp_path):
        """Validation runs through the LOADER, not a second reader.

        A rewriter that validated with its own parser would be checking its own
        opinion of the shape. This is what caught `C-43` copying the candidate
        list instead of unioning it, which produced `selected: era5` against
        `sources: [chirps]` — valid YAML, refused by the loader.
        """
        from blueearth_cst.shared.config_composition import load_composed_config
        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        migrate_project(t1, write=True)
        composed = load_composed_config(t1)
        assert composed["schema_version"] == 2
        assert composed["climate"]["selected"] in composed["climate"]["sources"]

    def test_the_candidate_list_absorbs_the_selected_source(self, tmp_path):
        """`C-43` is a UNION, not a copy.

        v1's `candidate_sources` listed the datasets OTHER than the privileged
        `clim_historical`; v2 requires `selected` to be a MEMBER of `sources`.
        """
        import yaml

        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        migrate_project(t1, write=True)
        doc = yaml.safe_load(t1.read_text(encoding="utf-8"))
        assert doc["climate"]["selected"] == "era5"
        assert doc["climate"]["sources"] == ["era5", "chirps"]

    def test_rerunning_on_a_v2_set_is_a_reported_no_op(self, tmp_path):
        """D-11.2b item 5. Idempotence, and it says so rather than staying mute."""
        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        migrate_project(t1, write=True)
        again = migrate_project(t1, write=True)
        assert len(again) == 1
        assert "already" in again[0]

    def test_a_partial_set_is_refused_not_finished(self, tmp_path):
        """A set no migration produced is one a human should look at."""
        import yaml

        from scripts.migrate_project_config import MigrationError, migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        doc = yaml.safe_load(t1.read_text(encoding="utf-8"))
        doc["schema_version"] = 99
        t1.write_text(yaml.safe_dump(doc), encoding="utf-8")
        with pytest.raises(MigrationError, match="neither v1"):
            migrate_project(t1, write=True)

    def test_dry_run_writes_nothing(self, tmp_path):
        """The preflight is read-only, and this is what proves it."""
        from scripts.migrate_project_config import migrate_project

        t1 = self._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        before = {p.name: p.read_bytes() for p in tmp_path.glob("*.yml")}
        migrate_project(t1, write=False)
        after = {p.name: p.read_bytes() for p in tmp_path.glob("*.yml")}
        assert after == before
        assert not list(tmp_path.glob("*.v1.bak"))


class TestTheNonPreservingHooks:
    """D-11.5 — the two rows that change what a project computes.

    Every other row is mechanical: the same run, spelled differently. These two
    are not, and the difference between them is whether a correct rewrite
    EXISTS. `C-69`'s does, so it warns and proceeds; `N8`'s does not, so it
    refuses.
    """

    def test_run_historical_false_warns_about_the_metrics_it_gains(self, tmp_path):
        """`C-69`: the gain is the intended behaviour, so warn, do not refuse.

        Refusing would block every project that set it `false` from migrating at
        all, over a change the row exists to make.
        """
        import re

        from scripts.migrate_project_config import migrate_project

        t1 = TestTheTransaction._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        wf3 = tmp_path / "snake_config_rapid_run_stress_test.yml"
        wf3.write_text(
            re.sub(
                r"^run_historical:\s*true",
                "run_historical: false",
                wf3.read_text(encoding="utf-8"),
                flags=re.M,
            ),
            encoding="utf-8",
        )
        report = migrate_project(t1, write=False)
        warning = [line for line in report if "q_wettest_month_mean" in line]
        assert warning, "the gained indicators must be named, not just implied"
        assert "st_0" in warning[0]

    def test_run_historical_true_says_nothing(self, tmp_path):
        """The no-op case. A signal that fires every run is one nobody reads."""
        from scripts.migrate_project_config import migrate_project

        t1 = TestTheTransaction._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        report = migrate_project(t1, write=False)
        assert not [line for line in report if "q_wettest_month_mean" in line]

    def test_a_non_january_water_year_is_refused(self, tmp_path):
        """`N8`: no year pair reproduces the window, so there is nothing to emit.

        The v1 window's bounds are CALENDAR and the v2 key's are WATER years.
        For January they coincide; for anything else a rewrite would shift every
        downstream number by up to a year while looking correct.
        """
        from scripts.migrate_project_config import MigrationError, migrate_project

        t1 = TestTheTransaction._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        t1.write_text(
            t1.read_text(encoding="utf-8").replace(
                "shared:\n", "shared:\n  water_year_start: Oct\n", 1
            ),
            encoding="utf-8",
        )
        with pytest.raises(MigrationError, match="water_year_start: Oct"):
            migrate_project(t1, write=True)

    def test_a_refusal_leaves_the_tree_byte_identical(self, tmp_path):
        """D-11.2b's whole point, and no unit test reaches it.

        `N8` fires part-way through a set. If anything had been written by then,
        the project would be left mixed v1/v2 — a tree the loader rejects
        wholesale, from a command that was trying to help.
        """
        from scripts.migrate_project_config import MigrationError, migrate_project

        t1 = TestTheTransaction._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        t1.write_text(
            t1.read_text(encoding="utf-8").replace(
                "shared:\n", "shared:\n  water_year_start: Oct\n", 1
            ),
            encoding="utf-8",
        )
        before = {p.name: p.read_bytes() for p in sorted(tmp_path.glob("*.yml"))}
        with pytest.raises(MigrationError):
            migrate_project(t1, write=True)
        after = {p.name: p.read_bytes() for p in sorted(tmp_path.glob("*.yml"))}
        assert after == before
        assert not list(tmp_path.glob("*.v1.bak"))
        assert not list(tmp_path.glob(".migrate_staging"))

    def test_january_is_not_refused(self, tmp_path):
        """The month where calendar and water years coincide."""
        from scripts.migrate_project_config import migrate_project

        t1 = TestTheTransaction._copy_set(tmp_path, "snake_config_rapid", V1_SPLIT)
        t1.write_text(
            t1.read_text(encoding="utf-8").replace(
                "shared:\n", "shared:\n  water_year_start: Jan\n", 1
            ),
            encoding="utf-8",
        )
        assert migrate_project(t1, write=False)


class TestExperimentRecords:
    """§11.6 — the records travel WITH the config, or every experiment dies.

    The freeze compares an experiment's recorded settings against the live
    config key by key. Migrate one without the other and EVERY key differs, so
    every already-run experiment becomes permanently unrunnable.
    `RETIRED_EXPERIMENT_KEYS` does not rescue it: its escape covers keys that
    DISAPPEAR, and most of R14's rows are renames.
    """

    def test_the_record_moves_onto_the_v2_spellings(self):
        import ruamel.yaml as ry

        from scripts.migrate_project_config import (
            load_mapping,
            migrate_experiment_record,
        )

        root = pathlib.Path(__file__).resolve().parent.parent
        src = root / V1_SPLIT / "experiment_rapid.yml"
        with src.open(encoding="utf-8") as handle:
            doc = ry.YAML().load(handle)

        migrate_experiment_record(doc, load_mapping(), outvars=["river discharge"])
        section = doc["run_stress_test"]
        assert "stress_test" not in section
        assert "climate_perturbations" in section
        assert "n_realizations" in section
        assert "simulation_window" in section
        assert "horizontime_climate" not in section
        assert "run_length" not in section

    def test_the_record_gains_no_schema_version(self):
        """It is not a project config; stamping it would invent a key.

        The stamp is `C-05`, which applies to the T1 file. Reusing
        `migrate_set` means the stamp happens and must be filtered back out —
        asserted here rather than trusted, because the filter is easy to lose.
        """
        import ruamel.yaml as ry

        from scripts.migrate_project_config import (
            load_mapping,
            migrate_experiment_record,
        )

        root = pathlib.Path(__file__).resolve().parent.parent
        src = root / V1_SPLIT / "experiment_rapid.yml"
        with src.open(encoding="utf-8") as handle:
            doc = ry.YAML().load(handle)
        migrate_experiment_record(doc, load_mapping(), outvars=["river discharge"])
        assert "schema_version" not in doc

    def test_an_untouched_experiment_still_matches_its_migrated_config(self):
        """D-14.8, the falsifier: `_frozen_differences` must come back EMPTY.

        The user changed nothing; only the toolbox's spelling moved. If the
        record and the config are migrated by the same mapping, the freeze sees
        no difference — and that is the property that keeps every existing
        experiment runnable across R14.
        """
        import ruamel.yaml as ry
        import yaml

        from blueearth_cst.experiment.write_experiment_config import (
            _frozen_differences,
        )
        from scripts.migrate_project_config import (
            load_mapping,
            migrate_experiment_record,
            migrate_set,
        )

        root = pathlib.Path(__file__).resolve().parent.parent
        mapping = load_mapping()

        # the live config, migrated
        t1 = yaml.safe_load(
            (root / V1_SPLIT / "snake_config_rapid.yml").read_text(encoding="utf-8")
        )
        t2 = {
            wf: (
                yaml.safe_load(
                    (root / f"{V1_SPLIT}/snake_config_rapid_{wf}.yml").read_text(
                        encoding="utf-8"
                    )
                )
                or {}
            )
            for wf in (
                "analyze_climate",
                "build_model",
                "analyze_projections",
                "run_stress_test",
            )
        }
        _, t2, _ = migrate_set(t1, t2, mapping, outvars=["river discharge"])

        # the experiment record for that same config, migrated
        src = root / V1_SPLIT / "experiment_rapid.yml"
        with src.open(encoding="utf-8") as handle:
            record = ry.YAML().load(handle)
        migrate_experiment_record(record, mapping, outvars=["river discharge"])

        # `enabled` lives in T1's `workflows.<name>` stanza and is folded into
        # the section by COMPOSITION, not by the T2 file — so the live side must
        # carry it too, the way a run would see it. Comparing the raw T2 file
        # against a composed record would report a difference that no run has.
        live = dict(t2["run_stress_test"])
        live["enabled"] = True

        differences = _frozen_differences(
            {"run_stress_test": dict(record["run_stress_test"])},
            {"run_stress_test": live},
        )
        assert differences == [], differences
