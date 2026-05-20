"""
=====
Scene
=====

:Author: Reuven Mol

an intermediate layer between the Scene class and the plotly graphs.
"""

from dataclasses import dataclass
from north.core.state import PhysicalState
from north.core.scene import Scene, FrameOfReference
from north.plots.graphics_utils import load_image, add_arrow
from north.plots.views import LatitudeView
import numpy as np
import plotly.graph_objects as go


# =========================================================
# LOAD LOCAL EARTH IMAGE
# =========================================================

EARTH_IMAGE = load_image('pictures/earth-latitude-longitude-diagram-vector-illustration.jpg')


@dataclass(frozen=True, slots=True)
class PlotMetadata:
    frame: FrameOfReference
    mapping: str


class ScenePlotter:

    def __init__(self, scene: Scene):
        self.scene = scene
        self.latitude_view = go.Figure()
        self.latitude_metadata = PlotMetadata(FrameOfReference.l, "Y:X,X:-Z")

        # initiate latitude plots
        p = np.array([
            np.cos(self.scene.physical_state.latitude),
            np.sin(self.scene.physical_state.latitude)
        ])  # point on Earth
        """surface point"""
        g, omega = self.vectors(FrameOfReference.l)
        # according to "Y:X,X:-Z" mapping
        g = np.array([-g[2], g[0]])
        omega = np.array([-omega[2], omega[0]])
        self.latitude_view = LatitudeView(p, g, omega, np.rad2deg(self.scene.physical_state.latitude))

    def update(self):
        p = np.array([
            np.cos(self.scene.physical_state.latitude),
            np.sin(self.scene.physical_state.latitude)
        ])  # point on Earth
        """surface point"""
        g, omega = self.vectors(FrameOfReference.l)
        # according to "Y:X,X:-Z" mapping
        g = np.array([-g[2], g[0]])
        omega = np.array([-omega[2], omega[0]])
        self.latitude_view.update(p, g, omega, np.rad2deg(self.scene.physical_state.latitude))

    def vectors(self, frame: FrameOfReference):
        return self.scene.gravity(frame), self.scene.earth_rotation(frame)

    @classmethod
    def from_physical_state(cls, latitude, azimuth, pitch, roll, encoder):
        physical_state = PhysicalState.from_floats(
            np.deg2rad(latitude),
            np.deg2rad(azimuth),
            np.deg2rad(pitch),
            np.deg2rad(roll),
            np.deg2rad(encoder),
        )
        return cls(Scene(physical_state))
