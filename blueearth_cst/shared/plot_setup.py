"""Shared plotting setup paths, appearance preferences and renderer identity."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import yaml

PLOTTING_DIR = Path(__file__).resolve().parents[2] / "config/plotting"


def load_style(path: Path | None = None) -> dict[str, Any]:
    """Read appearance preferences; keep Matplotlib validation in the renderer."""
    path = PLOTTING_DIR / "style.yml" if path is None else Path(path)
    try:
        style = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot read plot style {path}: {exc}") from exc
    expected = {"page", "typography", "charts", "evaluation"}
    if not isinstance(style, dict) or set(style) != expected:
        raise ValueError(f"{path}: style requires exactly {sorted(expected)}")
    for name, block in style.items():
        if not isinstance(block, dict) or not block:
            raise ValueError(f"{path}: {name} must be a nonempty mapping")
    numeric = {
        "page": ("figure_width_mm", "raster_dpi", "pdf_fonttype"),
        "typography": ("base", "tick", "legend", "title", "caveat"),
    }
    for section, names in numeric.items():
        for name in names:
            value = style[section].get(name)
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(
                    f"{path}: {section}.{name} must be a positive finite number"
                )
    charts = style["charts"]
    for group in (
        "widths",
        "heights",
        "padding",
        "fonts",
        "lines",
        "markers",
        "rcparams",
        "label_box",
    ):
        if not isinstance(charts.get(group), dict) or not charts[group]:
            raise ValueError(f"{path}: charts.{group} must be a nonempty mapping")
    markers = charts.get("fallback_markers")
    if (
        not isinstance(markers, list)
        or not markers
        or any(not isinstance(value, str) or not value for value in markers)
    ):
        raise ValueError(
            f"{path}: charts.fallback_markers must be a nonempty list of marker strings"
        )
    return style


def setup_digest() -> str:
    """Track appearance files only in renderer params, outside scientific identity."""
    digest = hashlib.sha256()
    for name in ("colors.yml", "style.yml"):
        digest.update(name.encode("utf-8"))
        digest.update((PLOTTING_DIR / name).read_bytes())
    return digest.hexdigest()


STYLE_SETTINGS = load_style()
