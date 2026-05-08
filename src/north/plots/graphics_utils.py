"""
==============
graphics utils
==============

:Author: Reuven Mol
"""
from pathlib import Path
import plotly.graph_objects as go
from functools import cache
from PIL import Image
import io
import base64
import numpy as np

ORIGIN = np.zeros(2)


@cache
def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")


def rotated_image_uri(path: str, angle_deg: float) -> str:
    """
    Load image, rotate it, and return base64 URI.
    """

    img = load_image(path)

    rotated = img.rotate(
        angle_deg,
        expand=True,
        resample=Image.Resampling.BICUBIC
    )

    buffer = io.BytesIO()

    rotated.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{encoded}"


def add_arrow(
        fig: go.Figure,
        vec: np.ndarray,
        name: str,
        color: str,
        start: np.ndarray = ORIGIN,
) -> None:
    r"""
    Add a labeled 2D vector arrow to a Plotly figure.

    This utility is part of the North visual grammar system.

    Visual Rules
    ------------
    * Physical vectors are always represented by arrows.
    * Vector labels are attached near the arrow head.
    * Labels may contain LaTeX math expressions.
    * The arrow color and label color are always identical.
    * The vector direction is encoded geometrically only,
      never by text orientation.

    Parameters
    ----------
    fig : go.Figure
        Target Plotly figure.

    vec : ndarray, shape (2,)
        2D vector to draw.

    name : str
        Vector label.

        The label may contain LaTeX expressions, for example:

        - ``r"$\vec{g}$"``
        - ``r"$\vec{\Omega}$"``
        - ``r"$\hat{X}^b$"``

        Plotly renders LaTeX using MathJax.

    color : str
        Arrow and label color.

        Usually taken from ``north.plots.theme``.

    start : ndarray, shape (2,), optional
        Arrow origin in plot coordinates.

        Default is the global origin.

    Returns
    -------
    None
        The figure is modified in-place.

    Examples
    --------
    >>> add_arrow(
    ...     fig,
    ...     vec=np.array([0, 1]),
    ...     name=r"\vec{\Omega}",
    ...     color="blue"
    ... )

    >>> add_arrow(
    ...     fig,
    ...     vec=np.array([1, 0]),
    ...     name=r"\hat{X}^b",
    ...     color="black"
    ... )
    """

    end = start + vec

    # label positioning
    text_loc = start + 1.1 * vec
    text_pos = 'middle center'
    if vec[0] == 0.0:
        if vec[1] >= 0.0:
            text_pos = "bottom center"
        else:
            text_pos = "top center"
    elif vec[1] == 0.0:
        if vec[0] == 0.0:
            text_pos = "middle right"
        else:
            text_pos = "middle left"
    elif vec[0] > 0 and vec[1] > 0:
        text_pos = 'bottom right'
    elif vec[0] < 0 < vec[1]:
        text_pos = 'top left'
    elif vec[0] < 0 and vec[1] < 0:
        text_pos = 'bottom left'
    elif vec[0] > 0 > vec[1]:
        text_pos = 'bottom right'

    # =========================================================
    # ARROW
    # =========================================================

    fig.add_annotation(
        x=end[0],
        y=end[1],

        ax=start[0],
        ay=start[1],

        xref="x",
        yref="y",
        axref="x",
        ayref="y",

        showarrow=True,

        arrowhead=3,
        arrowsize=1.3,
        arrowwidth=3,
        arrowcolor=color,

        text="",
    )

    # =========================================================
    # LABEL
    # =========================================================

    fig.add_trace(go.Scatter(
        x=[text_loc[0]],
        y=[text_loc[1]],
        mode="text",
        text=[rf"${name}$" if "\\" in name else name],
        textposition=text_pos,
        textfont=dict(color=color, size=16),
        showlegend=False,
    ))
