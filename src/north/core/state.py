"""
==============
Physical State
==============

:Author: Reuven Mol

Representation of the instantaneous physical configuration of a north-seeking system.

Overview
--------
The ``PhysicalState`` class stores the minimal set of physical parameters required to fully describe the orientation
configuration of the gyrocompass mechanism relative to the local-level frame.

The state is intentionally represented using five intuitive mechanical angles rather than a generic orientation
representation such as a quaternion or rotation matrix.
This preserves physical intuition and matches the actual mechanical structure of the system.

The five angles are:

1. latitude
    Geographic latitude of the platform.

2. azimuth
    Rotation of the gimbal frame relative to local north on local level plain.

3. pitch
    Rotation of the optical frame relative to the local level plain.

4. roll
    Rotation of the body frame relative to the optical frame.

5. encoder
    Rotation of the sensing frame around the motor axis.

Coordinate Frames
-----------------
The simulator uses the following frame convention:

.. math::

    L \\rightarrow G \\rightarrow O \\rightarrow B \\rightarrow S

Where:

- ``L`` : Local-level-Local_north frame using NED convention
- ``G`` : Ground bound Azimuth rotation.
- ``O`` : Optical frame
- ``B`` : Body frame
- ``S`` : Sensing frame

The total orientation of the sensor frame relative to the local-level-local-North frame is therefore:

.. math::

    C_{LS}
    =
    C_{LG}
    C_{GO}
    C_{OB}
    C_{BS}

Angle Conventions
-----------------
All angles are internally stored in **radians**.

Positive rotations follow the right-hand rule.

The angles correspond to the following elementary rotations:

.. math::

    C_{LG} = R_z(\\psi)

.. math::

    C_{GO} = R_y(\\theta)

.. math::

    C_{OB} = R_x(\\phi)

.. math::

    C_{BF} = R_z(\\alpha)

Where:

- :math:`\\psi` is the azimuth angle
- :math:`\\theta` is the pitch angle
- :math:`\\phi` is the roll angle
- :math:`\\alpha` is the encoder angle

Internal Representation
-----------------------
Internally, all angles are stored in a one-dimensional immutable NumPy array with shape ``(5,)``.

The storage order is:

.. math::

    [
        latitude,
        azimuth,
        pitch,
        roll,
        encoder
    ]

The internal array is intentionally hidden behind semantic properties to preserve readability and prevent index-based
programming throughout the simulator codebase.

Immutability
------------
``PhysicalState`` instances are immutable.

This is an intentional design decision intended to:

- simplify simulation history tracking
- avoid accidental state mutation
- improve debugging
- support deterministic replay
- encourage explicit state transitions

Examples
--------
Constructing a state from floats:

>>> state = PhysicalState.from_floats(
...     latitude=0.5,
...     azimuth=1.2,
...     pitch=0.1,
...     roll=-0.2,
...     encoder=2.0,
... )

Accessing individual angles:

>>> state.pitch
0.1

Converting to a dictionary:

>>> state.to_dict()
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True, slots=True)
class PhysicalState:
    """
    Immutable representation of the physical orientation state of the
    north-seeking mechanism.

    Parameters
    ----------
    _angles : ndarray of shape (5,)
        Internal storage vector containing all state angles in radians.

    Notes
    -----
    The internal storage order is:

    .. math::

        [
            latitude,
            azimuth,
            pitch,
            roll,
            encoder
        ]

    The internal NumPy array is immutable and should not be modified
    directly.
    """
    _angles: np.ndarray
    """internal array to store all angles of the physical state"""

    def __post_init__(self):
        if self._angles.shape != (5,):
            raise ValueError(f"Expected 5 angles, got {len(self._angles)}")
        angles = np.asarray(self._angles).copy()
        angles.setflags(write=False)
        object.__setattr__(self, "_angles", angles)

    def __str__(self):
        return ", ".join([
            f"latitude:{self.latitude}",
            f"azimuth:{self.azimuth}",
            f"pitch:{self.pitch}",
            f"roll:{self.roll}",
            f"encoder:{self.encoder}"
        ])

    @property
    def dtype(self):
        return self._angles.dtype

    @property
    def latitude(self):
        """latitude of the physical state"""
        return self._angles[0]

    @property
    def azimuth(self):
        """azimuth of the physical state"""
        return self._angles[1]

    @property
    def pitch(self):
        """pitch of the physical state"""
        return self._angles[2]

    @property
    def roll(self):
        """roll of the physical state"""
        return self._angles[3]

    @property
    def encoder(self):
        """the real position where the motor turn the sensor in the motor plain of the physical state"""
        return self._angles[4]

    def to_dict(self) -> dict[str, float]:
        return {
            "latitude": self.latitude,
            "azimuth": self.azimuth,
            "pitch": self.pitch,
            "roll": self.roll,
            "encoder": self.encoder
        }

    @classmethod
    def from_floats(cls, latitude: float, azimuth: float, pitch: float, roll: float, encoder: float) -> PhysicalState:
        """
        Construct a physical state from scalar angle values.

        Parameters
        ----------
        latitude : float
            Geographic latitude in radians.

        azimuth : float
            Azimuth angle in radians.

        pitch : float
            Pitch angle in radians.

        roll : float
            Roll angle in radians.

        encoder : float
            Encoder angle in radians.

        Returns
        -------
        PhysicalState
            Immutable physical state instance.

        Notes
        -----
        All input angles are assumed to already be expressed in radians.
        No angle wrapping or normalization is currently performed.
        """
        return cls(np.array([latitude, azimuth, pitch, roll, encoder]))

    @classmethod
    def from_str(cls, input_str: str) -> PhysicalState:
        parsed_angles = [float(s.split(":")[1]) for s in input_str.split(", ")]
        return cls(np.array(parsed_angles))

    @classmethod
    def from_dict(cls, input_dict: dict[str, float]) -> PhysicalState:
        return cls(np.array([
                input_dict["latitude"],
                input_dict["azimuth"],
                input_dict["pitch"],
                input_dict["roll"],
                input_dict["encoder"],
            ]))

    def change_dtype(self, new_dtype: np.dtype) -> PhysicalState:
        """
        Change the dtype of the physical state by creating a new copy with different dtype.

        Parameters
        ----------
        new_dtype : np.dtype
            the new dtype of the new physical state.

        Return
        ------
        PhysicalState
            a copy of the physical state with dtype `new_dtype`.
        """
        return PhysicalState(self._angles.astype(new_dtype))


if __name__ == "__main__":
    my_ps = PhysicalState.from_floats(1.0, 2.0, 3.0, 4.0, 0.5)
    print(my_ps.dtype)
    print(my_ps.to_dict())
