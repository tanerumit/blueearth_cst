# Install weathergenr from the user's GitHub fork into the active R env.
#
# Canonical R-side install for M2. Invoked once per fresh env via the
# pixi task `pixi run install-rdeps`; not used at workflow runtime.
# weathergenr is not on conda-forge, so the env file can't declare it
# directly. The decision to pin via this script (vs. vendor under
# vendor/weathergenr/) is documented in dev/m02_decisions.md.
#
# Manual invocation (for debugging):
#     pixi run install-rdeps
#     # or, equivalently:
#     pixi run Rscript --vanilla dev/scripts/install_weathergenr.R

if (!requireNamespace("devtools", quietly = TRUE)) {
  stop(
    "r-devtools is missing from the env. Install via:\n",
    "  conda install -n cst -c conda-forge r-devtools -y"
  )
}

devtools::install_github(
  "tanerumit/weathergenr",
  ref = "v1.2.0",
  upgrade = "never",
  quiet = FALSE
)

# Record what got installed for reproducibility / future pinning.
desc <- packageDescription("weathergenr")
cat("\n--- weathergenr installed ---\n")
cat("Version:    ", as.character(packageVersion("weathergenr")), "\n", sep = "")
cat("RemoteSha:  ", if (is.null(desc$RemoteSha)) "(not recorded)" else desc$RemoteSha, "\n", sep = "")
cat("RemoteRef:  ", if (is.null(desc$RemoteRef)) "(not recorded)" else desc$RemoteRef, "\n", sep = "")
cat("RemoteRepo: ", if (is.null(desc$RemoteRepo)) "(not recorded)" else desc$RemoteRepo, "\n", sep = "")
