call activate cst

set CFG=config/workflows/snake_config_model_test.yml

rem Snakefile_model_creation
snakemake -s Snakefile_model_creation --configfile %CFG%  --dag | dot -Tpng > dag_model.png
snakemake --unlock -s Snakefile_model_creation --configfile %CFG%
snakemake all -c 3 -s Snakefile_model_creation --configfile %CFG%

rem Snakefile climate_projections
snakemake -s Snakefile_climate_projections --configfile %CFG% --dag | dot -Tpng > dag_projections.png
snakemake --unlock -s Snakefile_climate_projections --configfile %CFG%
snakemake all -c 3 -s Snakefile_climate_projections --configfile %CFG% --keep-going

rem Snakefile_climate_experiment
snakemake -s Snakefile_climate_experiment --configfile %CFG%  --dag | dot -Tpng > dag_climate.png
snakemake --unlock -s Snakefile_climate_experiment --configfile %CFG%
snakemake all -c 3 -s Snakefile_climate_experiment --configfile %CFG%

rem snakemake -s Snakefile_model_creation all -c 1 --keep-going --until add_gauges --report --dryrun 
rem keep going is when parallel runs to keep going parallel if one series goes wrong
rem dryrun is to tell what it will be doing without actually running
rem until - still the whole workflow but not all jobs 
rem --delete-temp-output - delete the temp files after the run
pause
