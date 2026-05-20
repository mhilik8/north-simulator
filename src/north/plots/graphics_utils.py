"""
==============
graphics utils
==============

:Author: Reuven Mol
"""

import os
from pathlib import Path
import plotly.graph_objects as go
from functools import cache
from PIL import Image
import io
import base64
import numpy as np

PICTURES_PATH: Path = Path(__file__).parent / Path("pictures")

ORIGIN = np.zeros(2)
ORIGIN_3D = np.zeros(3)


def pictures() -> list[str]:
    return [p for p in os.listdir(PICTURES_PATH) if p.endswith(".png") or p.endswith(".jpg")]


@cache
def load_image(name: str) -> Image.Image:
    if name not in pictures():
        raise KeyError(f'{name} is not found in pictures folder')
    path = PICTURES_PATH / name
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
) -> tuple:
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

        - ``r"\vec{g}"``
        - ``r"\vec{\Omega}"``
        - ``r"\hat{X}^b"``

        Plotly renders LaTeX using MathJax.

    color : str
        Arrow and label color.

        Usually taken from ``north.plots.theme``.

    start : ndarray, shape (2,), optional
        Arrow origin in plot coordinates.

        Default is the global origin.

    Returns
    -------
    tuple
        Tuple containing:

        - arrow annotation handle
        - label annotation handle

        Both objects can later be modified in-place for
        efficient plot updates.

    Examples
    --------
    >>> arrow, label = add_arrow(
    ...     fig,
    ...     vec=np.array([0, 1]),
    ...     name=r"\vec{\Omega}",
    ...     color="blue"
    ... )

    >>> arrow.x = 1.0
    >>> label.text = r"$\vec{g}$"
    """

    end = start + vec

    # =========================================================
    # LABEL POSITION
    # =========================================================

    text_loc = start + 1.12 * vec

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

    arrow_annotation = fig.layout.annotations[-1]

    # =========================================================
    # LABEL
    # =========================================================

    fig.add_annotation(
        x=text_loc[0],
        y=text_loc[1],

        text=rf"${name}$" if "\\" in name else name,

        showarrow=False,

        font=dict(
            color=color,
            family="Noto Sans Math",
            size=18
        ),

        xanchor="center",
        yanchor="middle",
    )

    label_annotation = fig.layout.annotations[-1]

    return arrow_annotation, label_annotation


def add_arrow_3d(
    fig: go.Figure,
    vec: np.ndarray,
    name: str,
    color: str,
    start: np.ndarray = ORIGIN_3D,
    *,
    shaft_width: float = 6,
    head_scale: float = 0.18,
    text_scale: float = 1.12,
) -> None:
    r"""
    Add a labeled 3D vector arrow to a Plotly figure.

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

    vec : ndarray, shape (3,)
        3D vector to draw.

    name : str
        Vector label.

    color : str
        Arrow and label color.

    start : ndarray, shape (3,), optional
        Arrow origin in plot coordinates.

        Default is the global origin.

    shaft_width : float, optional
        Width of the arrow shaft.

    head_scale : float, optional
        Relative size of the arrow head.

    text_scale : float, optional
        Relative label offset from the vector tip.

    Returns
    -------
    None
        The figure is modified in-place.
    """

    vec = np.asarray(vec, dtype=float)
    start = np.asarray(start, dtype=float)

    end = start + vec

    norm = np.linalg.norm(vec)

    if norm == 0:
        raise ValueError("Zero-length vector cannot be drawn as an arrow.")

    # =========================================================
    # LABEL POSITION
    # =========================================================

    text_loc = start + text_scale * vec

    # =========================================================
    # ARROW SHAFT
    # =========================================================

    # Leave room for cone head
    cone_length = head_scale * norm
    shaft_end = end - cone_length * vec / norm

    fig.add_trace(
        go.Scatter3d(
            x=[start[0], shaft_end[0]],
            y=[start[1], shaft_end[1]],
            z=[start[2], shaft_end[2]],
            mode="lines",
            line=dict(
                color=color,
                width=shaft_width,
            ),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # =========================================================
    # ARROW HEAD
    # =========================================================

    fig.add_trace(
        go.Cone(
            x=[shaft_end[0]],
            y=[shaft_end[1]],
            z=[shaft_end[2]],

            u=[vec[0]],
            v=[vec[1]],
            w=[vec[2]],

            sizemode="absolute",
            sizeref=cone_length,

            colorscale=[
                [0, color],
                [1, color],
            ],

            showscale=False,
            hoverinfo="skip",
        )
    )

    # =========================================================
    # LABEL
    # =========================================================

    current_annotations = list(fig.layout.scene.annotations)

    current_annotations.append(dict(
                    showarrow=False,
                    x=text_loc[0], y=text_loc[1], z=text_loc[2],
                    text=rf"${name}$" if "\\" in name else name,
                    font=dict(
                        color=color,
                        size=18,
                        family="Noto Sans Math",
                    ),
                ))

    fig.update_layout(
        scene=dict(
            annotations=current_annotations,
        )
    )
