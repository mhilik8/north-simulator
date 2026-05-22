"""
=================
Motor Plane Plot
=================

:Author: Reuven Mol

Vectorized visualization of the spinning sensor plane.

The plot shows:

1. Sensor measurement axis
2. Encoder rotation
3. Earth-rate projection signal
4. True north projection
5. Gravity projection
6. Encoder zero reference

All geometry is fully vectorized.
"""

import numpy as np
import plotly.graph_objects as go

from north.plots.theme import *


# =========================================================
# COLORS
# =========================================================

SENSOR_COLOR = "blue"
ENCODER_COLOR = "#ffcc00"
NORTH_COLOR = EARTH_ROTATION_COLOR

GRAVITY_PROJECTION_COLOR = GRAVITY_COLOR

SIGNAL_COLOR = "#00ffaa"

ZERO_ENCODER_COLOR = "#ffffff"


# =========================================================
# HELPERS
# =========================================================

def unit(angle_rad: float) -> np.ndarray:
    """
    2D unit vector from angle.

    Angle convention:
    - 0 rad points north
    - positive rotation clockwise
    """

    return np.array([
        np.sin(angle_rad),
        np.cos(angle_rad)
    ])


# =========================================================
# MAIN PLOT
# =========================================================

def motor_plane_view(
    encoder_deg: float,
    azimuth_deg: float = 0.0,
    pitch_deg: float = 0.0,
    roll_deg: float = 0.0,
    latitude_deg: float = 0.0,
    show_earth_rotation_signal: bool = False,
) -> go.Figure:
    """
    Plot spinning motor plane geometry.

    Parameters
    ----------
    encoder_deg : float
        Encoder angle [deg].

    azimuth_deg : float
        Heading angle [deg].

    pitch_deg : float
        Pitch angle [deg].

    roll_deg : float
        Roll angle [deg].

    latitude_deg : float
        Latitude [deg].

    Returns
    -------
    go.Figure
    """

    encoder = np.deg2rad(encoder_deg)
    azimuth = np.deg2rad(azimuth_deg)
    pitch = np.deg2rad(pitch_deg)
    roll = np.deg2rad(roll_deg)
    latitude = np.deg2rad(latitude_deg)

    fig = go.Figure()

    # =====================================================
    # OUTER MOTOR CIRCLE
    # =====================================================

    theta = np.linspace(0, 2*np.pi, 500)

    fig.add_trace(go.Scatter(
        x=np.cos(theta),
        y=np.sin(theta),
        mode="lines",
        line=dict(
            width=4,
            color="white"
        ),
        showlegend=False
    ))

    # =====================================================
    # ZERO ENCODER AXIS
    # =====================================================

    zero_axis = unit(0)

    fig.add_annotation(
        x=zero_axis[0],
        y=zero_axis[1],

        ax=0,
        ay=0,

        xref="x",
        yref="y",
        axref="x",
        ayref="y",

        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=4,
        arrowcolor=ZERO_ENCODER_COLOR,

        text="0°",
        font=dict(
            size=16,
            color=ZERO_ENCODER_COLOR
        )
    )

    # =====================================================
    # SENSOR AXIS
    # =====================================================

    sensor_axis = unit(encoder)

    fig.add_annotation(
        x=0.9 * sensor_axis[0],
        y=0.9 * sensor_axis[1],

        ax=0,
        ay=0,

        xref="x",
        yref="y",
        axref="x",
        ayref="y",

        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=5,
        arrowcolor=SENSOR_COLOR,

        text=r"$\hat{X}^s$",
        font=dict(
            size=18,
            color=SENSOR_COLOR
        )
    )

    # =====================================================
    # SENSOR RECTANGLE
    # =====================================================

    rect = np.array([
        [-0.12, -0.05],
        [0.12, -0.05],
        [0.12,  0.05],
        [-0.12,  0.05],
        [-0.12, -0.05],
    ])

    c = np.cos(encoder)
    s = np.sin(encoder)

    R = np.array([
        [c, -s],
        [s,  c]
    ])

    rect_rot = rect @ R

    fig.add_trace(go.Scatter(
        x=rect_rot[:, 0],
        y=rect_rot[:, 1],
        mode="lines",
        line=dict(
            width=3,
            color=SENSOR_COLOR
        ),
        fill="toself",
        fillcolor="rgba(255,255,255,0.05)",
        showlegend=False
    ))

    # =====================================================
    # TRUE NORTH PROJECTION
    # =====================================================

    if azimuth_deg:
        north_angle = azimuth

        north_vec = unit(north_angle)

        fig.add_annotation(
            x=0.8 * north_vec[0],
            y=0.8 * north_vec[1],

            ax=0,
            ay=0,

            xref="x",
            yref="y",
            axref="x",
            ayref="y",

            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=4,
            arrowcolor=NORTH_COLOR,

            text=EARTH_ROTATION_LABEL,

            font=dict(
                size=18,
                color=NORTH_COLOR
            )
        )

    # =====================================================
    # GRAVITY PROJECTION
    # =====================================================

    if pitch or roll:
        gravity_angle = azimuth + np.pi/2 + roll * 0.5

        gravity_vec = unit(gravity_angle)

        fig.add_annotation(
            x=0.7 * gravity_vec[0],
            y=0.7 * gravity_vec[1],

            ax=0,
            ay=0,

            xref="x",
            yref="y",
            axref="x",
            ayref="y",

            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=4,
            arrowcolor=GRAVITY_PROJECTION_COLOR,

            text=GRAVITY_LABEL,

            font=dict(
                size=18,
                color=GRAVITY_PROJECTION_COLOR
            )
        )

    # =====================================================
    # EARTH RATE SIGNAL
    # =====================================================

    if show_earth_rotation_signal:
        signal_theta = np.linspace(0, 2*np.pi, 2000)
        signal_amplitude = (
            np.cos(signal_theta - north_angle)
            * np.cos(latitude)
            * np.cos(pitch)
        )
        signal_r = 0.55 + 0.25 * signal_amplitude
        signal_x = signal_r * np.sin(signal_theta)
        signal_y = signal_r * np.cos(signal_theta)

        fig.add_trace(go.Scatter(
            x=signal_x,
            y=signal_y,
            mode="lines",
            line=dict(
                width=4,
                color=SIGNAL_COLOR
            ),
            name="earth-rate signal"
        ))

    # =====================================================
    # ENCODER ARC
    # =====================================================

    arc_angles = np.linspace(0, encoder, 200)

    arc_r = 0.35

    fig.add_trace(go.Scatter(
        x=arc_r * np.sin(arc_angles),
        y=arc_r * np.cos(arc_angles),

        mode="lines",

        line=dict(
            width=4,
            color=ENCODER_COLOR
        ),

        showlegend=False
    ))

    # =====================================================
    # ENCODER LABEL
    # =====================================================

    mid = encoder / 2

    fig.add_trace(go.Scatter(
        x=[0.45 * np.sin(mid)],
        y=[0.45 * np.cos(mid)],

        mode="text",

        text=[f"{encoder_deg:.1f}°"],

        textfont=dict(
            size=16,
            color=ENCODER_COLOR
        ),

        showlegend=False
    ))

    # =====================================================
    # CLOCKWISE DIRECTION LABEL
    # =====================================================

    fig.add_trace(go.Scatter(
        x=[-0.85],
        y=[-0.9],

        mode="text",

        text=["CW"],

        textfont=dict(
            size=16,
            color="white"
        ),

        showlegend=False
    ))

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        title="Motor Plane Geometry",

        width=850,
        height=850,

        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=CARD_COLOR,

        xaxis=dict(
            visible=False,
            range=[-1.15, 1.15]
        ),

        yaxis=dict(
            visible=False,
            range=[-1.15, 1.15],
            scaleanchor="x"
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),

        showlegend=False
    )

    return fig
