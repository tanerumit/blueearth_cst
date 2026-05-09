#################### GLOBAL R SETTINGS #########################################

# Trust R's default .libPaths(): user lib first (where weathergenr +
# its native-code dependencies are installed against the system
# toolchain), then the conda site lib. Forcing conda site lib first
# breaks weathergenr's load on Windows because its imports resolve
# from a conda r-base build with an incompatible mingw runtime ABI.
# R3 followup: build weathergenr against the conda toolchain so the
# user-lib dependency goes away.

# General options
options(warn = -1) # Disable warnings

# Disable S3 method overwritten message
Sys.setenv(`_R_S3_METHOD_REGISTRATION_NOTE_OVERWRITES_` = "false")
