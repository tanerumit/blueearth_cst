@echo off
rem Enabled-aware Windows runner; pass --cores N before -- execution flags.
rem Example: scripts\run_snake_test.cmd --cores 3 -- --dry-run
setlocal
pixi run python scripts/run_workflows.py --config test_case/project_config_rapid.yml %*
exit /b %errorlevel%
