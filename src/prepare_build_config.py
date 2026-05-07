"""Inject snake-config values into the hydromt build config.

hydromt 1.3 dropped `--opt key=value` and `--region` on the CLI, so
snake-config values that previously came in as flags
(setup_basemaps.region, setup_basemaps.res) are merged into a runtime
copy of the static `steps:`-format build-config template here.
"""
import ast
import yaml
from pathlib import Path

template_fn = Path(snakemake.input.template)
out_fn = Path(snakemake.output.merged)
model_resolution = snakemake.params.model_resolution
model_region = snakemake.params.model_region

# model_region in the snake config is a Python-dict-literal string like
# "{'subbasin': [9.666, 0.4476], 'uparea': 100}". Parse via ast.literal_eval
# so we can serialize as proper YAML.
if isinstance(model_region, str):
    model_region = ast.literal_eval(model_region)

with template_fn.open("r") as f:
    cfg = yaml.safe_load(f)

# steps is a list of single-key dicts: [{"setup_basemaps": {...}}, ...]
steps = cfg.get("steps", [])
basemaps_step = next(
    (s for s in steps if isinstance(s, dict) and "setup_basemaps" in s), None
)
if basemaps_step is None:
    raise RuntimeError(
        f"{template_fn} has no setup_basemaps step under steps:"
    )
kwargs = basemaps_step["setup_basemaps"] or {}
kwargs["region"] = model_region
kwargs["res"] = float(model_resolution)
basemaps_step["setup_basemaps"] = kwargs

out_fn.parent.mkdir(parents=True, exist_ok=True)
with out_fn.open("w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
