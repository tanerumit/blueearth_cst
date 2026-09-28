#!/usr/bin/env bash
# Gate 5 tree-shape check: pre-R14 reference tree vs the Gate 5 rebuild.
REF="C:/Users/taner/workspace/blueearth_cst/test_case/test_local"   # run at 0d256a41
CUR="test_case/test_local"                                          # run at 9bfdda5c

pixi run python dev/scripts/semantic_tree_diff.py --ref "$REF" --cur "$CUR" \
  --no-path-map \
  --map "config/runs/snake_config_analyze_projections.yml=config/runs/project_config_analyze_projections.yml" \
  --map "config/runs/snake_config_build_model.yml=config/runs/project_config_build_model.yml" \
  --map "experiments/experiment/config/snake_config_run_stress_test.yml=experiments/experiment/config/project_config_run_stress_test.yml" \
  --allow "experiments/experiment/config/catalogs/data_catalog_run_stress_test.yml" \
  --allow-content "config/runs/README.md" \
  --allow-content "config/runs/analyze_projections/run_record.yml" \
  --allow-content "config/runs/build_model/run_record.yml" \
  --allow-content "config/runs/journal.jsonl" \
  --allow-content "config/runs/project_config_analyze_projections.yml" \
  --allow-content "config/runs/project_config_build_model.yml" \
  --allow-content "experiments/experiment/config/README.md" \
  --allow-content "experiments/experiment/config/experiment.yml" \
  --allow-content "experiments/experiment/config/model_reference.yml" \
  --allow-content "experiments/experiment/config/project_config_run_stress_test.yml" \
  --allow-content "experiments/experiment/config/run_record.yml" \
  --allow-content "experiments/experiment/results/run_metadata.json" \
  --allow-content "models/hydrology/wflow/evaluation/run_metadata.json" \
  --allow-content "data/climate/projections/cmip6/summary/provenance.json" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM4-8_historical_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM4-8_ssp245_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM4-8_ssp585_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM5-0_historical_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM5-0_ssp245_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_INM_INM-CM5-0_ssp585_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_NOAA-GFDL_GFDL-ESM4_historical_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_NOAA-GFDL_GFDL-ESM4_ssp245_r1i1p1f1.nc" \
  --allow-content "data/climate/projections/cmip6/scalar/cmip6_NOAA-GFDL_GFDL-ESM4_ssp585_r1i1p1f1.nc"
