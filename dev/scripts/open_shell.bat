@echo off
REM Launch PowerShell at the project root with the `cst` conda env activated.
REM Double-clickable; also works from cmd.

set "PROJECT_DIR=%~dp0"
set "CONDA_HOOK=%USERPROFILE%\AppData\Local\miniconda3\shell\condabin\conda-hook.ps1"

start "blueearth_cst" pwsh.exe -NoExit -ExecutionPolicy Bypass -Command ^
  "Set-Location -LiteralPath '%PROJECT_DIR%'; & '%CONDA_HOOK%'; conda activate cst"
