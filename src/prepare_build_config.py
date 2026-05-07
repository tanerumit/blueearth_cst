"""Inject snake-config values into the hydromt build config.

hydromt 1.3 dropped `--opt key=value` overrides on the CLI, so values
that vary per snake-config (currently just setup_basemaps.res) are
merged into a runtime copy of the static template here.
"""
import yaml
from pathlib import Path

template_fn = Path(snakemake.input.template)
out_fn = Path(snakemake.output.merged)
model_resolution = snakemake.params.model_resolution

with template_fn.open("r") as f:
    cfg = yaml.safe_load(f)

cfg.setdefault("setup_basemaps", {})["res"] = float(model_resolution)

out_fn.parent.mkdir(parents=True, exist_ok=True)
with out_fn.open("w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
