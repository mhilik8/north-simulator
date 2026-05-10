"""
=====
Scene
=====

:Author: Reuven Mol

an intermediate layer between the Scene class and the plotly graphs.
"""

from north.core.scene import Scene, FrameOfReference
from north.core.state import PhysicalState


class ScenePlotter:

    def __init__(self, scene: Scene, frame: FrameOfReference):
        self.scene = scene
        self.frame = frame

    @classmethod
    def from_physical_state(cls, physical_satate: PhysicalState):
        return cls(Scene(physical_satate), FrameOfReference.s)

    def vectors(self):
        return self.scene.gravity(self.frame), self.scene.earth_rotation(self.frame)
