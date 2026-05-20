"""
=====
Views
=====

:Author: Reuven Mol

an abstract class of view to wrap up plotly figure
"""

from abc import ABC, abstractmethod

from north.plots.graphics_utils import load_image, add_arrow, rotated_image_uri
from north.plots.theme import (
    GRAVITY_COLOR, EARTH_ROTATION_COLOR, GRAVITY_LABEL, EARTH_ROTATION_LABEL, LOCAL_LEVEL_COLOR, HIGHLIGHT_COLOR,
    EARTH_COLOR, CARD_COLOR
)

import numpy as np
import plotly.graph_objects as go

# =========================================================
# LOAD LOCAL EARTH IMAGE
# =========================================================

EARTH_IMAGE = load_image('earth-latitude-longitude-diagram-vector-illustration.jpg')

COMPASS_ROSE = load_image("compass-rose.png")

AIRCRAFT_TOP_PATH = "airplane-top-view.png"

class View(ABC):
    """
    Base class for all scene views.

    A View owns:
    - one Plotly figure
    - graphical primitives
    - update logic
    """

    def __init__(self):
        self.figure = go.Figure()

    @abstractmethod
    def update(self, *args) -> None:
        raise NotImplementedError


class LatitudeView(View):

    def __init__(self, p, g, omega, latitude):
        super().__init__()

        self.p = p
        self.figure.add_layout_image(
            dict(
                source=EARTH_IMAGE,
                xref="x",
                yref="y",
                x=-1.3,
                y=1.22,
                sizex=2.6,
                sizey=2.6,
                sizing="stretch",
                opacity=0.25,
                layer="below"
            )
        )

        self.gravity_arrow, self.gravity_label = add_arrow(
            self.figure,
            vec=g,
            name=GRAVITY_LABEL,
            color=GRAVITY_COLOR,
            start=p
        )

        self.rotation_arrow, self.rotation_label = add_arrow(
            self.figure,
            vec=omega,
            name=EARTH_ROTATION_LABEL,
            color=EARTH_ROTATION_COLOR,
            start=p
        )

        t0 = p + self.tangent * 0.4
        t1 = p - self.tangent * 0.4

        # local level
        self.figure.add_trace(go.Scatter(
            x=[t0[0], t1[0]],
            y=[t0[1], t1[1]],
            mode="lines",
            name="Local level",
            line=dict(dash="dash", color=LOCAL_LEVEL_COLOR),
        ))

        self.local_level = self.figure.layout.data[-1]

        self.figure.update_layout(
            title=f"Latitude view (correct geometry): {latitude:.2f}°",
            xaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis_scaleanchor="x",
            width=600,
            height=600
        )

    @property
    def tangent(self):
        return np.array([-self.p[1], self.p[0]])

    def update(self, p, g, omega, latitude) -> None:
        self.p = p
        # gravity
        self.gravity_arrow.x = p[0] + 0.4 * g[0]
        self.gravity_arrow.y = p[1] + 0.4 * g[1]
        self.gravity_arrow.ax = p[0]
        self.gravity_arrow.ay = p[1]
        self.gravity_label.x = p[0] + 1.12 * g[0]
        self.gravity_label.y = p[1] + 1.12 * g[1]

        # earth rotation axis projected in this plane (visual only)
        self.rotation_arrow.x = p[0] + 0.4 * omega[0]
        self.rotation_arrow.y = p[1] + 0.4 * omega[1]
        self.rotation_arrow.ax = p[0]
        self.rotation_arrow.ay = p[1]
        self.rotation_label.x = p[0] + 1.12 * omega[0]
        self.rotation_label.y = p[1] + 1.12 * omega[1]

        t0 = p + self.tangent * 0.4
        t1 = p - self.tangent * 0.4

        # local level
        self.local_level.x = [t0[0], t1[0]]
        self.local_level.y = [t0[1], t1[1]]

        # LAYOUT
        self.figure.update_layout(
            title=f"Latitude view (correct geometry): {latitude:.2f}°",
            xaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis_scaleanchor="x",
            width=600,
            height=600
        )


class AzimuthView(View):
    def __init__(self, azimuth):
        super().__init__()

        self.azimuth = azimuth

        self.figure.add_layout_image(
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
        rotated_aircraft = rotated_image_uri(str(AIRCRAFT_TOP_PATH), -self.azimuth)

        self.figure.add_layout_image(
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

        north_vector_l = np.array([0.0, 1.0])  # this should move to scene plotter
        add_arrow(self.figure, north_vector_l, EARTH_ROTATION_LABEL, EARTH_ROTATION_COLOR)

        # =====================================================
        # HEADING VECTOR
        # =====================================================

        heading = np.deg2rad(self.azimuth)

        heading_vec = np.array([
            np.sin(heading),
            np.cos(heading)
        ])  # this should move to scene plotter

        add_arrow(self.figure, heading_vec, r'\hat{X}', HIGHLIGHT_COLOR)

        # =====================================================
        # AZIMUTH ARC
        # =====================================================

        arc_angles = np.linspace(0, heading, 150)

        arc_x = 0.55 * np.sin(arc_angles)
        arc_y = 0.55 * np.cos(arc_angles)

        self.figure.add_trace(go.Scatter(
            x=arc_x,
            y=arc_y,
            mode="lines",
            line=dict(width=4, color=HIGHLIGHT_COLOR),
            showlegend=False
        ))

        # =====================================================
        # HEADING LABEL
        # =====================================================

        mid_angle = heading / 2

        self.figure.add_trace(go.Scatter(
            x=[0.68 * np.sin(mid_angle)],
            y=[0.68 * np.cos(mid_angle)],
            mode="text",
            text=[f"{self.azimuth:.1f}°"],
            textfont=dict(size=16, color=HIGHLIGHT_COLOR),
            showlegend=False
        ))

        # =====================================================
        # CENTER POINT
        # =====================================================

        self.figure.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker=dict(size=10,color="white"),
            showlegend=False
        ))

        # =====================================================
        # LAYOUT
        # =====================================================

        self.figure.update_layout(
            title=f"Azimuth World View — Heading {self.azimuth:.1f}°",
            width=600,
            height=600,
            plot_bgcolor=EARTH_COLOR,
            paper_bgcolor=CARD_COLOR,
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-1.2, 1.2], scaleanchor="x"),
            margin=dict(l=20, r=20, t=60, b=20)
        )

    def update(self, ) -> None:
