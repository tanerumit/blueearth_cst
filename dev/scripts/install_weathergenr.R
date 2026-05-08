# Install weathergenr v1.2.0 from GitHub via pak.
#
# Invoked at env-setup time by:
#     pixi run install-rdeps
# (also pulled in transitively by `pixi run install`).
#
# Where it lands:
#   - Linux/macOS: conda env's R site-lib (.libPaths()[1] under pixi)
#   - Windows:     user-level R lib (~/AppData/Local/R/win-library/<R-version>)
#
# We don't force lib=R_HOME/library because on Windows the conda r-base
# toolchain hits a `Mingw-w64 runtime failure: 32 bit pseudo relocation
# ... out of range` error when byte-compiling weathergenr against
# conda's r-* deps (specifically when the package's namespace is loaded
# with .libPaths() restricted to the conda site-lib). Installing into
# the default .libPaths()[1] dodges that path on Windows by loading
# deps from the user lib (built against system R), and is a no-op on
# Linux where the conda site-lib is .libPaths()[1] by default.
#
# Idempotent: returns early if weathergenr at the right version is
# already present anywhere visible to R.

required_version <- "1.2.0"

if (requireNamespace("weathergenr", quietly = TRUE)) {
  found_version <- as.character(packageVersion("weathergenr"))
  if (found_version == required_version) {
    cat("weathergenr ", found_version, " already installed at\n", sep = "")
    cat("  ", find.package("weathergenr"), "\n", sep = "")
    quit(save = "no", status = 0)
  }
  cat(
    "weathergenr ", found_version, " present but ", required_version,
    " required; reinstalling.\n", sep = ""
  )
}

if (!requireNamespace("pak", quietly = TRUE)) {
  stop("r-pak is missing from the env. Declare it in pixi.toml [dependencies].")
}

pak::pkg_install(
  "tanerumit/weathergenr@v1.2.0",
  ask = FALSE,
  upgrade = FALSE
)

cat("--- weathergenr installed via pak ---\n")
cat("Version:    ", as.character(packageVersion("weathergenr")), "\n", sep = "")
cat("Location:   ", find.package("weathergenr"), "\n", sep = "")
