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
from north.plots.views import LatitudeView, AzimuthView, CompassView, Inclination3DView
import numpy as np
import plotly.graph_objects as go


# =========================================================
# LOAD LOCAL EARTH IMAGE
# =========================================================

EARTH_IMAGE = load_image('earth-latitude-longitude-diagram-vector-illustration.jpg')


@dataclass(frozen=True, slots=True)
class PlotMetadata:
    frame: FrameOfReference
    mapping: str


class ScenePlotter:

    def __init__(self, scene: Scene):
        self.scene = scene

        p, g_scale, omega_scale = self.vectors_e_2d()
        self.latitude_metadata = PlotMetadata(FrameOfReference.l, "Y:X,X:-Z")
        self.latitude_view = LatitudeView(p, g_scale, omega_scale, self.latitude)

        # initiate azimuth plots
        self.azimuth_view = AzimuthView(self.azimuth)

        # initiate the compass view
        self.compass_view = CompassView(self.azimuth)

        # initiate the inclination view
        self.inclination_view = Inclination3DView(self.azimuth, self.pitch, self.roll, self.scene.c_g_to_b.q)

    @property
    def latitude(self):
        return np.rad2deg(self.scene.physical_state.latitude)

    @latitude.setter
    def latitude(self, value):
        old = self.scene.physical_state.to_numpy()
        old[0] = np.deg2rad(value)
        self.scene = Scene(PhysicalState(old))

    @property
    def azimuth(self):
        return np.rad2deg(self.scene.physical_state.azimuth)

    @azimuth.setter
    def azimuth(self, value):
        old = self.scene.physical_state.to_numpy()
        old[1] = np.deg2rad(value)
        self.scene = Scene(PhysicalState(old))

    @property
    def pitch(self):
        return np.rad2deg(self.scene.physical_state.pitch)

    @pitch.setter
    def pitch(self, value):
        old = self.scene.physical_state.to_numpy()
        old[2] = np.deg2rad(value)
        self.scene = Scene(PhysicalState(old))

    @property
    def roll(self):
        return np.rad2deg(self.scene.physical_state.roll)

    @roll.setter
    def roll(self, value):
        old = self.scene.physical_state.to_numpy()
        old[3] = np.deg2rad(value)
        self.scene = Scene(PhysicalState(old))

    def update(self):
        # latitude
        p, g_scale, omega_scale = self.vectors_e_2d()
        self.latitude_view.update(p, g_scale, omega_scale, self.latitude)

        # azimuth
        self.azimuth_view.update(self.azimuth)

        # compass
        self.compass_view.update(self.azimuth)

        # inclination 3D
        self.inclination_view.update(self.azimuth, self.pitch, self.roll, self.scene.c_g_to_b.q)

    def vectors(self, frame: FrameOfReference):
        return self.scene.gravity(frame), self.scene.earth_rotation(frame)

    def vectors_e_2d(self):
        # initiate latitude plots
        p = np.array([
            np.cos(self.scene.physical_state.latitude),
            np.sin(self.scene.physical_state.latitude)
        ])  # point on Earth
        """surface point"""
        g_3d, omega_3d = self.vectors(FrameOfReference.l)

        # according to "Y:X,X:-Z" mapping
        l_to_e = np.array([
            [np.cos(self.scene.physical_state.latitude), -np.sin(self.scene.physical_state.latitude)],
            [np.sin(self.scene.physical_state.latitude), np.cos(self.scene.physical_state.latitude)]
        ])
        g_e_2d = l_to_e @ np.array([-g_3d[2], g_3d[0]])
        g_scale = 0.35 * g_e_2d
        omega_e_2d = l_to_e @ np.array([-omega_3d[2], omega_3d[0]])
        omega_normalized = omega_e_2d / np.linalg.norm(omega_e_2d)
        omega_scale = 0.35 * omega_normalized
        return p, g_scale, omega_scale

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
