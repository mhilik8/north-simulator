"""
=====
Scene
=====

:Author: Reuven Mol

High-level geometric representation of the north-seeker physical scene.

The :class:`Scene` class acts as the central geometry engine of the
application. It computes all coordinate transformations and derived
vectors from a given :class:`PhysicalState`.

The class provides a clean abstraction layer between:

- physical truth
- navigation geometry
- frame transformations
- plotting backends
- sensor simulation

Notes
-----
Frames of reference
^^^^^^^^^^^^^^^^^^^

The simulator uses five coordinate frames:

``l`` : local-level-local-north
    Navigation frame using the NED convention.

``g`` : ground
    Ground-aligned frame after azimuth rotation.

``o`` : optics
    Optical frame after pitch rotation.

``b`` : body
    Aircraft body frame after roll rotation.

``s`` : sensor
    Sensor frame after encoder rotation.

Navigation convention
^^^^^^^^^^^^^^^^^^^^^

The local-level frame ``l`` uses the NED convention:

- +X : north
- +Y : east
- +Z : down

The coordinate system is right-handed.

Transformation convention
^^^^^^^^^^^^^^^^^^^^^^^^^

Transformation names follow the convention::

    c_a_to_b

meaning:

    "apply on a vector represented in frame ``a``
    and return the same vector represented in frame ``b``"

Example
^^^^^^^

If ``v_l`` is a vector expressed in the local-level frame::

    v_b = c_l_to_b.apply(v_l)

Rotation sequence
^^^^^^^^^^^^^^^^^

The orientation pipeline is composed from four elementary rotations:

1. ``l_to_g``
    Rotation around ``z_l`` (azimuth / heading)

2. ``g_to_o``
    Rotation around ``y_g`` (pitch)

3. ``o_to_b``
    Rotation around ``x_o`` (roll)

4. ``b_to_s``
    Rotation around ``z_b`` (motor encoder)

The full sensor orientation is therefore::

    c_l_to_s =
        c_b_to_s
        * c_o_to_b
        * c_g_to_o
        * c_l_to_g

Internally all rotations are represented using :class:`SO3`.

Notes on plotting
^^^^^^^^^^^^^^^^^

The :class:`Scene` class contains only navigation geometry and
physical relationships.

Plotting-specific conventions such as:

- Plotly axis swaps
- left/right handed conversions
- 2D projections
- rendering offsets

should be implemented in visualization adapters such as
``ScenePlotly``.

This separation keeps the core navigation logic independent from
graphics backends.

Examples
--------
Create a scene from a physical state::

    state = PhysicalState(...)
    scene = Scene(state)

Transform gravity into body frame::

    g_b = scene.earth_gravity_b

Transform Earth rotation into sensor frame::

    omega_s = scene.earth_rotation_s
"""

from enum import Enum
from typing import Callable
import numpy as np
from north.core.state import PhysicalState
from north.core.earth import earth_rotation_l, earth_gravity_l
from north.core.rotations import SO3


class FrameOfReference(Enum):
    l = 'local-level-local-north'
    g = 'ground-frame'
    o = 'optics-frame'
    b = 'body-frame'
    s = 'sensor-frame'


class Scene:
    """
    Geometric representation of the north-seeker physical scene.

    The :class:`Scene` class converts a :class:`PhysicalState`
    into a complete hierarchy of coordinate transformations and
    physically meaningful vectors.

    The class acts as the central geometry engine of the simulator.

    It computes:

    - frame-to-frame rotations
    - Earth vectors in multiple frames
    - sensor orientation
    - body orientation
    - navigation-frame relationships

    Notes
    -----
    Frame hierarchy
    ^^^^^^^^^^^^^^^

    The simulator uses the following frame sequence::

        l -> g -> o -> b -> s

    where:

    ``l``
        Local-level-local-north frame (NED).

    ``g``
        Ground frame after azimuth rotation.

    ``o``
        Optics frame after pitch rotation.

    ``b``
        Body frame after roll rotation.

    ``s``
        Sensor frame after encoder rotation.

    Transformation convention
    ^^^^^^^^^^^^^^^^^^^^^^^^^

    Transformations are named::

        c_a_to_b

    meaning:

        "transform a vector represented in frame ``a``
        into frame ``b``"

    Example::

        v_b = c_l_to_b.apply(v_l)

    Rotation sequence
    ^^^^^^^^^^^^^^^^^

    The orientation pipeline is composed from four elementary
    rotations:

    1. azimuth
        Rotation around ``z_l``

    2. pitch
        Rotation around ``y_g``

    3. roll
        Rotation around ``x_o``

    4. encoder
        Rotation around ``z_b``

    All rotations are internally represented using :class:`SO3`.

    Notes on units
    ^^^^^^^^^^^^^^

    All internal angles are assumed to be in radians.

    Earth vectors are normalized unless otherwise stated.

    Parameters
    ----------
    physical_state : PhysicalState
        Full physical state of the north-seeker system.

        The state contains:

        - latitude
        - azimuth
        - pitch
        - roll
        - encoder position

    Attributes
    ----------
    physical_state : PhysicalState
        Current physical state associated with the scene.

    See Also
    --------
    PhysicalState
        Low-level state container.

    SO3
        Rotation representation used internally.

    Examples
    --------
    Create a scene::

        state = PhysicalState(...)
        scene = Scene(state)

    Compute body-frame gravity::

        g_b = scene.earth_gravity_b

    Compute sensor-frame Earth rotation::

        omega_s = scene.earth_rotation_s

    Compute local-to-sensor transformation::

        c_l_to_s = scene.c_l_to_s
    """

    def __init__(self, physical_state: PhysicalState):
        self.physical_state: PhysicalState = physical_state
        self._cached_transformation: dict[str: SO3] = dict()

    def get_transformation(self, name: str, create: Callable) -> SO3:
        if name in self._cached_transformation:
            return self._cached_transformation[name]
        t = create()
        self._cached_transformation[name] = t
        return t

    @property
    def c_l_to_g(self) -> SO3:
        """
        Local-level to ground transformation.

        Returns
        -------
        SO3
            Rotation from local-level frame ``l`` into
            ground frame ``g``.

        Notes
        -----
        This transformation represents the azimuth rotation.

        Rotation axis:
            ``z_l``

        Positive azimuth follows navigation heading convention.
        """
        return self.get_transformation(
            "c_l_to_g", lambda: SO3.exp(np.array((0.0, 0.0, -self.physical_state.azimuth))))

    @property
    def c_g_to_o(self) -> SO3:
        """
        Ground to optics transformation.

        Returns
        -------
        SO3
            Rotation from ground frame ``g`` into
            optics frame ``o``.

        Notes
        -----
        This transformation represents pitch rotation.

        Rotation axis:
            ``y_g``
        """
        return self.get_transformation(
            "c_g_to_o", lambda: SO3.exp(np.array((0.0, -self.physical_state.pitch, 0.0))))

    @property
    def c_o_to_b(self) -> SO3:
        """
        Optics to body transformation.

        Returns
        -------
        SO3
            Rotation from optics frame ``o`` into
            body frame ``b``.

        Notes
        -----
        This transformation represents roll rotation.

        Rotation axis:
            ``x_o``
        """
        return self.get_transformation(
            "c_o_to_b", lambda: SO3.exp(np.array((-self.physical_state.roll, 0.0, 0.0))))

    @property
    def c_b_to_s(self) -> SO3:
        """
        Body to sensor transformation.

        Returns
        -------
        SO3
            Rotation from body frame ``b`` into
            sensor frame ``s``.

        Notes
        -----
        This transformation represents encoder rotation.

        Rotation axis:
            ``z_b``

        Positive encoder rotation is clockwise when viewed
        from the positive axis direction.
        """
        return self.get_transformation(
            "c_b_to_s", lambda: SO3.exp(np.array((0.0, 0.0, -self.physical_state.encoder))))

    @property
    def c_g_to_b(self) -> SO3:
        """
        Ground to body transformation.

        Returns
        -------
        SO3
            Composite transformation from ``g`` to ``b``.
        """
        return self.get_transformation("c_g_to_b", lambda: self.c_o_to_b * self.c_g_to_o)

    @property
    def c_l_to_o(self) -> SO3:
        """
        Local-level to optics transformation.

        Returns
        -------
        SO3
            Composite transformation from ``l`` to ``o``.
        """
        return self.get_transformation("c_l_to_o", lambda: self.c_g_to_o * self.c_l_to_g)

    @property
    def c_l_to_b(self) -> SO3:
        """
        Local-level to body transformation.

        Returns
        -------
        SO3
            Composite transformation from ``l`` to ``b``.
        """
        return self.get_transformation("c_l_to_b", lambda: self.c_g_to_b * self.c_l_to_g)

    @property
    def c_l_to_s(self) -> SO3:
        """
        Local-level to sensor transformation.

        Returns
        -------
        SO3
            Composite transformation from ``l`` to ``s``.

        Notes
        -----
        This is the complete orientation pipeline of the
        north-seeker system.
        """
        return self.get_transformation("c_l_to_s", lambda: self.c_b_to_s * self.c_l_to_b)

    def gravity(self, frame: FrameOfReference) -> np.ndarray:
        gravity_l = earth_gravity_l()
        if frame is FrameOfReference.l:
            return gravity_l
        if frame is FrameOfReference.g:
            return gravity_l  # because gravity is invariant to azimuth rotation
        if frame is FrameOfReference.o:
            return self.c_g_to_o.apply(gravity_l)
        if frame is FrameOfReference.b:
            return self.c_l_to_b.apply(gravity_l)
        if frame is FrameOfReference.s:
            return self.c_l_to_s.apply(gravity_l)

    def earth_rotation(self, frame: FrameOfReference) -> np.ndarray:
        earth_rate = earth_rotation_l(self.physical_state.latitude)
        if frame is FrameOfReference.l:
            return earth_rate
        if frame is FrameOfReference.g:
            return self.c_l_to_g.apply(earth_rate)
        if frame is FrameOfReference.o:
            return self.c_l_to_o.apply(earth_rate)
        if frame is FrameOfReference.b:
            return self.c_l_to_b.apply(earth_rate)
        if frame is FrameOfReference.s:
            return self.c_l_to_s.apply(earth_rate)

    def update_position(self, new_position: float) -> None:
        """
        Update encoder position.

        Parameters
        ----------
        new_position : float
            New encoder angle in radians.

        Notes
        -----
        This method updates only the encoder degree of freedom
        while preserving all other physical-state parameters.

        The method is useful for:

        - motor sweeps
        - time-domain simulation
        - animation
        - algorithm evaluation
        """
        state = self.physical_state.to_numpy()
        state[-1] = new_position
        self.physical_state = PhysicalState(state)
        self._cached_transformation = {k: v for k, v in self._cached_transformation.items() if not k.endswith("_to_s")}
