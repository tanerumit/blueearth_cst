

# GENERAL STRESS TEST PARAMETERS ###############################################

# General R settings and prerequisites
source("./src/weathergen/global.R")

args <- commandArgs(trailingOnly = TRUE)

# Pass command line options
# Config file
yaml <- yaml::read_yaml(args[2])
# Stochastic weather realization to be perturbed
rlz_fn <- args[1]
rlz_input <- weathergenr::read_netcdf(rlz_fn, keep_leap_day = FALSE)
# Climate stress file
cst_data <- read.csv(args[3])


# General stress test parameters
output_path    <- yaml$imposeClimateChanges$output.path
nc_file_prefix <- yaml$imposeClimateChanges$nc.file.prefix
nc_file_suffix <- yaml$imposeClimateChanges$nc.file.suffix

# temp_change_type / precip_change_type [boolean]
temp_change_transient   <- yaml$temp$transient_change
precip_change_transient <- yaml$precip$transient_change


# PARAMETERS CHANGING PER RUN ##################################################

# Apply climate changes to baseline weather data stored in the nc file.
# `diagnostic = FALSE` makes the return shape compatible with write_netcdf
# directly (a list of data.frames, one per grid cell — same as the old
# imposeClimateChanges return).
rlz_future <- weathergenr::apply_climate_perturbations(
   data               = rlz_input$data,
   grid               = rlz_input$grid,
   date               = rlz_input$date,
   precip_mean_factor = cst_data$precip_mean,
   precip_var_factor  = cst_data$precip_variance,
   temp_delta         = cst_data$temp_mean,
   temp_transient     = temp_change_transient,
   precip_transient   = precip_change_transient,
   compute_pet        = TRUE,
   qm_fit_method      = "mme",
   diagnostic         = FALSE
)

# Save to netcdf file
weathergenr::write_netcdf(
   data          = rlz_future,
   grid          = rlz_input$grid,
   out_dir       = output_path,
   origin_date   = rlz_input$date[1],
   calendar      = "noleap",
   template_path = rlz_fn,
   compression   = 4,
   spatial_ref   = "spatial_ref",
   file_prefix   = nc_file_prefix,
   file_suffix   = nc_file_suffix
)


################################################################################
