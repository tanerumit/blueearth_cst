pkgs <- c(
  "doParallel", "dplyr", "e1071", "fitdistrplus", "foreach",
  "ggplot2", "ncdf4", "parallel", "patchwork", "stats",
  "rlang", "tidyr", "utils", "tibble", "scales",
  "waveslim", "forecast"
)
for (p in pkgs) {
  res <- tryCatch(
    {
      suppressMessages(library(p, character.only = TRUE))
      "OK"
    },
    error = function(e) paste("FAIL:", conditionMessage(e))
  )
  cat(sprintf("%-15s %s\n", p, res))
}
