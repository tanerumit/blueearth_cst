# General R settings and prerequisites
source("./src/weathergen/global.R")

# weathergenr is assumed to be installed in R-environment.
# See dev/scripts/install_weathergenr.R for the install path.
library(yaml)

args <- commandArgs(trailingOnly = TRUE)

# Pass command line options
yaml <- yaml::read_yaml(args[2])
weathergen_input_ncfile <- args[1]

# Parse global parameters from the yaml configuration file
historical_realizations_num <- yaml$generateWeatherSeries$realizations_num
weathergen_output_path <- yaml$generateWeatherSeries$output.path

# Step 1) Read weather data from the netcdf file
ncdata <- weathergenr::read_netcdf(weathergen_input_ncfile)

# Step 2) Generate new weather realizations
stochastic_weather <- weathergenr::generate_weather(
    obs_data         = ncdata$data,
    obs_grid         = ncdata$grid,
    obs_dates        = ncdata$date,
    vars             = yaml$general$variables,
    n_years          = yaml$generateWeatherSeries$sim.year.num,
    start_year       = yaml$generateWeatherSeries$sim.year.start,
    year_start_month = yaml$generateWeatherSeries$month.start,
    n_realizations   = historical_realizations_num,
    warm_var         = yaml$generateWeatherSeries$warm.variable,
    warm_signif      = yaml$generateWeatherSeries$warm.signif.level,
    warm_pool_size   = yaml$generateWeatherSeries$warm.sample.num,
    annual_knn_n     = yaml$generateWeatherSeries$knn.sample.num,
    wet_q            = yaml$generateWeatherSeries$mc.wet.quantile,
    extreme_q        = yaml$generateWeatherSeries$mc.extreme.quantile,
    dry_spell_factor = yaml$generateWeatherSeries$dry.spell.change,
    wet_spell_factor = yaml$generateWeatherSeries$wet.spell.change,
    out_dir          = weathergen_output_path,
    seed             = yaml$generateWeatherSeries$seed,
    parallel         = yaml$generateWeatherSeries$compute.parallel
)

# STEP 3) Save each stochastic realization back to a netcdf file
for (n in 1:historical_realizations_num) {

  # New return: $resampled is a data.frame with columns rlz_1, rlz_2, ...
  rlz_dates <- stochastic_weather$resampled[[paste0("rlz_", n)]]
  day_order <- match(rlz_dates, ncdata$date)

  # Obtain stochastic series by re-ordering historical data
  stochastic_rlz <- lapply(ncdata$data, function(x) x[day_order, ])

  # save to netcdf
  weathergenr::write_netcdf(
        data          = stochastic_rlz,
        grid          = ncdata$grid,
        out_dir       = paste0(weathergen_output_path, "realization_", n, "/"),
        origin_date   = stochastic_weather$dates[1],
        calendar      = "noleap",
        template_path = weathergen_input_ncfile,
        compression   = 4,
        spatial_ref   = "spatial_ref",
        file_prefix   = yaml$generateWeatherSeries$nc.file.prefix,
        file_suffix   = paste0(n, "_cst_0")
  )

}
