"""Inject snake-config values into the hydromt build config.

hydromt 1.3 dropped `--opt key=value` and `--region` on the CLI, so
snake-config values that previously came in as flags
(setup_basemaps.region, setup_basemaps.res) are merged into a runtime
copy of the static `steps:`-format build-config template here.
"""
import ast
from pathlib import Path

import yaml


def merge_build_config(template_path, out_path, model_resolution, model_region):
    """Merge region/resolution into the template's setup_basemaps step.

    Parameters
    ----------
    template_path : str | os.PathLike
        The static ``steps:``-format hydromt build-config template.
    out_path : str | os.PathLike
        Where to write the merged runtime config (parents created).
    model_resolution : float | str
        Value for ``setup_basemaps.res`` (coerced to float).
    model_region : dict | str
        Value for ``setup_basemaps.region``. May be a Python-dict-literal
        string (as it arrives from the snake config, e.g.
        ``"{'subbasin': [9.666, 0.4476], 'uparea': 100}"``); parsed via
        ``ast.literal_eval`` so it serializes as proper YAML.

    Raises
    ------
    RuntimeError
        If the template has no ``setup_basemaps`` step under ``steps:``.
    """
    template_path = Path(template_path)
    out_path = Path(out_path)

    if isinstance(model_region, str):
        model_region = ast.literal_eval(model_region)

    with template_path.open("r") as f:
        cfg = yaml.safe_load(f)

    # steps is a list of single-key dicts: [{"setup_basemaps": {...}}, ...]
    steps = cfg.get("steps", [])
    basemaps_step = next(
        (s for s in steps if isinstance(s, dict) and "setup_basemaps" in s), None
    )
    if basemaps_step is None:
        raise RuntimeError(f"{template_path} has no setup_basemaps step under steps:")
    kwargs = basemaps_step["setup_basemaps"] or {}
    kwargs["region"] = model_region
    kwargs["res"] = float(model_resolution)
    basemaps_step["setup_basemaps"] = kwargs

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        from src.snake_utils import log_row, tee_to_log

        with tee_to_log(sm.log[0]):
            merge_build_config(
                template_path=sm.input.template,
                out_path=sm.output.merged,
                model_resolution=sm.params.model_resolution,
                model_region=sm.params.model_region,
            )
            log_row(
                f"Prepared hydromt build config "
                f"(res={sm.params.model_resolution}, region={sm.params.model_region}) "
                f"-> {sm.output.merged}",
                module="config",
            )
