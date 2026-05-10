"""
========
Azimuth
========

:Author: Reuven Mol

Azimuth visualizations for the north seeker simulator.

This module provides two complementary visualizations:

1. World View
   A top-down external view showing the aircraft heading
   relative to geographic north.

2. Compass View
   A pilot-style heading indicator where the aircraft is fixed
   and the compass rose rotates beneath it.
"""

from pathlib import Path
import base64
import numpy as np
import plotly.graph_objects as go
from north.plots.graphics_utils import rotated_image_uri, add_arrow
from north.plots.theme import (
    BACKGROUND_COLOR,
    CARD_COLOR,
    EARTH_ROTATION_COLOR,
    EARTH_ROTATION_LABEL,
    HIGHLIGHT_COLOR,
    AIRCRAFT_SYMBOL_COLOR,
    EARTH_COLOR
)


# =========================================================
# ASSETS
# =========================================================

COMPASS_ROSE_PATH = Path(__file__).parent / Path("pictures/compass-rose.png")

AIRCRAFT_TOP_PATH = Path(__file__).parent / Path("pictures/airplane-top-view.png")


def _load_base64_image(path: Path) -> str:
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    suffix = path.suffix.lower().replace(".", "")

    return f"data:image/{suffix};base64,{encoded}"


COMPASS_ROSE = _load_base64_image(COMPASS_ROSE_PATH)
AIRCRAFT_TOP = _load_base64_image(AIRCRAFT_TOP_PATH)

# =========================================================
# WORLD VIEW
# =========================================================

def azimuth_world_view(
    azimuth_deg: float
) -> go.Figure:
    """
    Top-down external azimuth visualization.

    Parameters
    ----------
    azimuth_deg : float
        Heading angle in degrees.

        Convention
        ----------
        - 0°   : north
        - 90°  : east
        - 180° : south
        - 270° : west

        Positive rotation is clockwise.

    Returns
    -------
    go.Figure
        Interactive Plotly figure.
    """

    heading = np.deg2rad(azimuth_deg)

    fig = go.Figure()

    # =====================================================
    # COMPASS ROSE BACKGROUND
    # =====================================================

    fig.add_layout_image(
        dict(
            source=COMPASS_ROSE,
            xref="x",
            yref="y",
            x=-1.23,
            y=1.2,
            sizex=2.4,
            sizey=2.4,
            sizing="stretch",
            opacity=0.35,
            layer="below"
        )
    )

    # =====================================================
    # AIRCRAFT IMAGE
    # =====================================================

    rotated_aircraft = rotated_image_uri(str(AIRCRAFT_TOP_PATH), -azimuth_deg)

    fig.add_layout_image(
        dict(
            source=rotated_aircraft,
            xref="x",
            yref="y",

            x=-1.1,
            y=1.1,

            sizex=2.2,
            sizey=2.2,

            sizing="contain",
            opacity=1.0,
            layer="above",
        )
    )

    # =====================================================
    # NORTH ARROW
    # =====================================================

    add_arrow(fig, np.array([0.0, 1.0]), EARTH_ROTATION_LABEL, EARTH_ROTATION_COLOR)

    # =====================================================
    # HEADING VECTOR
    # =====================================================

    heading_vec = np.array([
        np.sin(heading),
        np.cos(heading)
    ])

    add_arrow(fig, heading_vec, r'\hat{X}', HIGHLIGHT_COLOR)

    # =====================================================
    # AZIMUTH ARC
    # =====================================================

    arc_angles = np.linspace(0, heading, 150)

    arc_x = 0.55 * np.sin(arc_angles)
    arc_y = 0.55 * np.cos(arc_angles)

    fig.add_trace(go.Scatter(
        x=arc_x,
        y=arc_y,

        mode="lines",

        line=dict(
            width=4,
            color=HIGHLIGHT_COLOR
        ),

        showlegend=False
    ))

    # =====================================================
    # HEADING LABEL
    # =====================================================

    mid_angle = heading / 2

    fig.add_trace(go.Scatter(
        x=[0.68 * np.sin(mid_angle)],
        y=[0.68 * np.cos(mid_angle)],

        mode="text",

        text=[f"{azimuth_deg:.1f}°"],

        textfont=dict(
            size=16,
            color=HIGHLIGHT_COLOR
        ),

        showlegend=False
    ))

    # =====================================================
    # CENTER POINT
    # =====================================================

    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],

        mode="markers",

        marker=dict(
            size=10,
            color="white"
        ),

        showlegend=False
    ))

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        title=f"Azimuth World View — Heading {azimuth_deg:.1f}°",

        width=600,
        height=600,

        plot_bgcolor=EARTH_COLOR,
        paper_bgcolor=CARD_COLOR,

        xaxis=dict(
            visible=False,
            range=[-1.2, 1.2]
        ),

        yaxis=dict(
            visible=False,
            range=[-1.2, 1.2],
            scaleanchor="x"
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    return fig


# =========================================================
# COMPASS VIEW
# =========================================================

def azimuth_compass_view(
    azimuth_deg: float
) -> go.Figure:
    """
    Pilot-style compass / heading indicator.

    Parameters
    ----------
    azimuth_deg : float
        Aircraft heading in degrees.

    Returns
    -------
    go.Figure
        Interactive Plotly figure.
    """

    fig = go.Figure()

    # =====================================================
    # ROTATING COMPASS ROSE
    # =====================================================

    rotated_rose = rotated_image_uri(str(COMPASS_ROSE_PATH), azimuth_deg)

    fig.add_layout_image(
        dict(
            source=rotated_rose,
            xref="x",
            yref="y",

            x=-1.0,
            y=1.0,

            sizex=2.0,
            sizey=2.0,

            sizing="stretch",
            opacity=0.95,
            layer="below",
        )
    )

    # =====================================================
    # OUTER RING
    # =====================================================

    theta = np.linspace(0, 2*np.pi, 400)

    fig.add_trace(go.Scatter(
        x=np.cos(theta),
        y=np.sin(theta),

        mode="lines",

        line=dict(
            width=5,
            color="white"
        ),

        showlegend=False
    ))

    # =====================================================
    # TICKS
    # =====================================================

    for deg in range(0, 360, 10):

        a = np.deg2rad(deg)

        r0 = 0.88
        r1 = 1.0

        width = 4 if deg % 30 == 0 else 1

        fig.add_trace(go.Scatter(
            x=[r0*np.sin(a), r1*np.sin(a)],
            y=[r0*np.cos(a), r1*np.cos(a)],

            mode="lines",

            line=dict(
                width=width,
                color="white"
            ),

            showlegend=False
        ))

    # =====================================================
    # FIXED AIRCRAFT SYMBOL
    # =====================================================

    fig.add_trace(go.Scatter(
        x=[-0.15, 0.0, 0.15],
        y=[-0.05, 0.15, -0.05],

        mode="lines",

        line=dict(
            width=6,
            color=HIGHLIGHT_COLOR
        ),

        showlegend=False
    ))

    # =====================================================
    # FIXED LUBBER LINE
    # =====================================================

    fig.add_trace(go.Scatter(
        x=[0, 0],
        y=[0.75, 1.02],

        mode="lines",

        line=dict(
            width=5,
            color="yellow"
        ),

        showlegend=False
    ))

    # =====================================================
    # DIGITAL READOUT
    # =====================================================

    fig.add_trace(go.Scatter(
        x=[0],
        y=[-0.55],

        mode="text",

        text=[f"{azimuth_deg:05.1f}°"],

        textfont=dict(
            size=28,
            family="Courier New",
            color="white"
        ),

        showlegend=False
    ))

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        title="Compass View",

        width=600,
        height=600,

        plot_bgcolor="black",
        paper_bgcolor=CARD_COLOR,

        xaxis=dict(
            visible=False,
            range=[-1.1, 1.1]
        ),

        yaxis=dict(
            visible=False,
            range=[-1.1, 1.1],
            scaleanchor="x"
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    return fig
