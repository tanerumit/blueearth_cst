# Inspect installed weathergenr's exported API and function signatures.
# Used to detect signature drift between generate_weather.R and the package.

suppressMessages(library(weathergenr))

cat("=== weathergenr exports ===\n")
exports <- ls("package:weathergenr")
print(exports)

# Functions used in generate_weather.R
target_fns <- c("read_netcdf", "apply_climate_perturbations", "write_netcdf")

for (fn in target_fns) {
  cat(sprintf("\n=== %s ===\n", fn))
  if (exists(fn, where = "package:weathergenr")) {
    f <- get(fn, envir = asNamespace("weathergenr"))
    cat("Args:\n")
    print(args(f))
  } else {
    cat(sprintf("NOT EXPORTED. Closest matches: %s\n",
                paste(grep(tolower(fn), tolower(exports), value = TRUE), collapse = ", ")))
  }
}
