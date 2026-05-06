# Install weathergenr from the user's GitHub fork into the active R env.
#
# Pre-M1 helper. weathergenr is not on conda-forge, so the conda env file
# can't declare it. M2 (per dev/roadmap.md) will replace this with a
# pinned commit/tag or a vendored source tree.
#
# Run via:
#     conda run -n cst Rscript --vanilla dev/scripts/install_weathergenr.R

if (!requireNamespace("devtools", quietly = TRUE)) {
  stop(
    "r-devtools is missing from the env. Install via:\n",
    "  conda install -n cst -c conda-forge r-devtools -y"
  )
}

devtools::install_github(
  "tanerumit/weathergenr",
  ref = "master",
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
