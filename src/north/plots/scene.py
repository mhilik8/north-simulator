"""
=====
Scene
=====

:Author: Reuven Mol

an intermediate layer between the Scene class and the plotly graphs.
"""

from north.core.scene import Scene, FrameOfReference
from north.core.state import PhysicalState
import numpy as np


class ScenePlotter:

    def __init__(self, scene: Scene, frame: FrameOfReference):
        self.scene = scene
        self.frame = frame

    @classmethod
    def from_physical_state(cls, latitude, azimuth, pitch, roll, encoder):
        physical_state = PhysicalState.from_floats(
            np.deg2rad(latitude),
            np.deg2rad(azimuth),
            np.deg2rad(pitch),
            np.deg2rad(roll),
            np.deg2rad(encoder),
        )
        return cls(Scene(physical_state), FrameOfReference.s)

    def vectors(self):
        return self.scene.gravity(self.frame), self.scene.earth_rotation(self.frame)
