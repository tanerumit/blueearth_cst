# Verify weathergenr v1.2.0 is present and loadable in the active R env.
#
# As of M2b, this script is install-disabled: it only checks the install,
# it does not attempt to (re)install. The conda r-base toolchain on
# Windows currently fails to build weathergenr from source against the
# pixi-managed R 4.5; until that's resolved, weathergenr v1.2.0 must be
# installed manually into the user library:
#
#     # Once, in a system R 4.5+ session (NOT the conda one):
#     install.packages("devtools")
#     devtools::install_github("tanerumit/weathergenr", ref = "v1.2.0")
#
# At workflow runtime, src/weathergen/global.R keeps both the conda
# site-lib and the user lib on .libPaths() so the user-installed
# weathergenr remains visible.
#
# M3 followup: build weathergenr against the conda env (likely needs
# m2w64-toolchain in pixi.toml, plus install-into-R_HOME/library) so the
# user-lib dependency goes away and everything lives under a single
# pixi-managed environment.

source("./src/weathergen/global.R")

required_version <- "1.2.0"

if (!requireNamespace("weathergenr", quietly = TRUE)) {
  stop(
    "weathergenr is not installed in any libPath visible to this R env.\n",
    "Install manually (see header of this script for the command).\n",
    "Searched libPaths:\n  ", paste(.libPaths(), collapse = "\n  ")
  )
}

found_version <- as.character(packageVersion("weathergenr"))
if (found_version != required_version) {
  stop(
    "weathergenr is installed at version ", found_version,
    " but the workflow requires ", required_version, ".\n",
    "Reinstall via the manual command in this script's header."
  )
}

cat("--- weathergenr verified ---\n")
cat("Version:    ", found_version, "\n", sep = "")
cat("Location:   ", find.package("weathergenr"), "\n", sep = "")
