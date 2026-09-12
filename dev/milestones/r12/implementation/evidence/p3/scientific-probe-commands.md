# Bounded P3 scientific probe commands

Prepared and import/lint checked, not scientifically accepted. Execute after the
coordinator's affected checks pass and the final runtime inventory is frozen.
The final full software gate may follow scientific execution and run during
result review; it must pass before P3 acceptance. Do not overlap Snakemake runs
with software tests that use its working-directory locks. All commands run from the
repository root in its existing Pixi environment. Capture full logs to files.

## GF27 automatic-seed capacity and width

Set `$FinalProjectConfig` to the coordinator's completed final direct-generation
project config. The staging script preserves its project directory so the three
generation variants share exactly the same historical source bytes. It changes
only seed request to `auto`, capacities 21/22/100 and workflow enablement; it
writes all configs into a new scratch directory, leaving source configs intact.

```powershell
$P3Probe = 'dev/milestones/r12/implementation/evidence/p3/probe-generation-capacity.py'
$GF27Work = '.tmp/scratchpad/2026-09-11_0010/gf27-final-configs'
pixi run --as-is python -B $P3Probe stage --config $FinalProjectConfig --work $GF27Work
pixi run --as-is snakemake all -c 3 -s generate_scenarios.smk --configfile "$GF27Work/project_config_capacity_21.yml" *> "$GF27Work/capacity-21.log"
pixi run --as-is snakemake all -c 3 -s generate_scenarios.smk --configfile "$GF27Work/project_config_capacity_22.yml" *> "$GF27Work/capacity-22.log"
pixi run --as-is snakemake all -c 3 -s generate_scenarios.smk --configfile "$GF27Work/project_config_capacity_100.yml" *> "$GF27Work/capacity-100.log"
```

Stop and inspect any nonzero exit before the next command. Obtain the exact
ready manifests from each invocation, then bind `$Manifest21`, `$Manifest22`,
and `$Manifest100`; do not choose a directory by newest timestamp or fallback.

```powershell
pixi run --as-is python -B $P3Probe compare --capacity-21 $Manifest21 --capacity-22 $Manifest22 --capacity-100 $Manifest100 --report dev/milestones/r12/implementation/evidence/p3/gf27-capacity-comparison.json *> "$GF27Work/comparison.log"
```

Acceptance requires equal automatic seeds and scientific generation payloads,
14 complete crosswalks per variant, exact forcing arrays/coordinates/attributes,
correct identifier widths, and three different collection IDs. Every forcing
hash is recorded; a positive perturbation must fail equality. This probe does
not establish the separate old-seed migration or experiment-rename cases; link
those final-code checks separately. No Wflow execution is needed for this matrix.

## GF31 final portable preparation binding

```powershell
pixi run --as-is python -B dev/milestones/r12/implementation/evidence/p3/probe-portable-preparation.py --work .tmp/scratchpad/2026-09-11_0010/gf31-final-physical2 --old-root C:/Users/taner/workspace/_workbench/blueearth-cst-r12/2026-09-10/prechange *> .tmp/scratchpad/2026-09-11_0010/gf31-final-physical2.log
```

The work root must not exist. This copies the frozen model to scratch, compares
predecessor-style and final portable preparation for all four retained source
branches, and relocates only probe-owned fixture inputs so their original paths
are unavailable. It runs preparation, not Wflow or Snakemake. Do not use Python
optimization (`-O`), since the retained fixture includes assertions.

The first `gf31-final-physical` root is preserved after a metadata-only comparison
failure. Independent read-only inspection found all ERA5 values/coordinates and
parsed TOMLs exact. Only `precip.precip_fn`, `pet.pet_fn`, and `temp.temp_fn`
changed from `forcing` to `run_01`, as required by the accepted catalog-selector
migration. The corrected comparator asserts and records exactly those three
old/new pairs, excludes them in memory, then requires every remaining attribute,
coordinate and value to match exactly. It does not drop attributes generally.

Review all four entries in `gf31-final-physical2/comparison.json`, the final
`run_01` selector, exact prepared-array equality, complete parsed-TOML equality
or the precisely recorded locator exclusions, and the positive perturbation
control. Preserve unchanged-ancillary refusal coverage from the final tests.
Copy only compact reviewed evidence into this directory; full disposable logs
and physical fixtures remain in scratch. Retain the ERA5-valued synthetic
elevation and dormant E-OBS scope limitations in the signed verdict.
