"""Explicit-figure export without workflow logging or pyplot state."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def export_figure(fig: Figure, path: str | os.PathLike[str], **kwargs) -> None:
    """Create destination parents and save the supplied figure.

    Save options and exceptions pass through unchanged. The caller owns the
    figure's size, style, backend and lifetime.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig.savefig(path, **kwargs)
