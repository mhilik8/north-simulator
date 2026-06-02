r"""
=========
Rotations
=========

:Author: Reuven Mol

SO(3) rotation group element used for rigid-body orientation and coordinate frame transformations.

Overview
--------
This module defines a minimal SO(3) abstraction based on unit quaternions.

Each SO(3) element represents a 3D rotation (orientation) and supports:

- composition of rotations
- inversion
- vector transformation
- exponential and logarithmic maps

Mathematical Definition
-----------------------
An element R ∈ SO(3) is a 3×3 orthonormal matrix satisfying:

.. math::

    R^T R = I, \quad \det(R) = 1

In this implementation, SO(3) is represented internally using a unit quaternion:

.. math::

    q = [w, x, y, z] \in \mathbb{H}, \quad ||q|| = 1

The mapping between quaternion and rotation matrix is provided via:

.. math::

    R = R(q)

Frame Convention
----------------
Rotations follow the active rotation convention:

- A vector v expressed in frame A is transformed to frame B via:

.. math::

    v_B = R_{BA} v_A

where:

- R_{BA} ∈ SO(3) rotates vectors from frame A → frame B

This convention is consistent across:
- physical state representation
- measurement models
- sensor transformations

Units
-----
All angular quantities are in radians unless otherwise specified.

Notes
-----
- This class is immutable (frozen dataclass).
- All operations return new SO3 instances.
- Numerical stability is inherited from quaternion representation.

Relationship to Quaternion
--------------------------
SO3 is a high-level abstraction built on a quaternion backend.
Quaternion provides the numerical representation, while SO3 provides
semantic group structure and frame-aware operations.
"""

from __future__ import annotations
from dataclasses import dataclass
from north.core.quaternions import Quaternion
import numpy as np


@dataclass(frozen=True, slots=True)
class SO3:
    _q: Quaternion

    def __mul__(self, other: SO3) -> SO3:
        """
        Compose two rotations.

        Parameters
        ----------
        other : SO3
            Rotation to apply after this rotation.

        Returns
        -------
        SO3
            Composed rotation:

            .. math::

                R = R_1 R_2

        Notes
        -----
        Composition follows the active rotation convention:

        v' = (R1 * R2) v
        """
        return SO3(self._q * other._q)

    @property
    def q(self) -> Quaternion:
        return self._q

    @property
    def R(self) -> np.ndarray:
        return self._q.as_rotmat()

    def apply(self, v: np.ndarray) -> np.ndarray:
        """
        Apply rotation to a 3D vector.

        Parameters
        ----------
        v : np.ndarray, shape (3,)
            Vector expressed in the source frame.

        Returns
        -------
        np.ndarray, shape (3,)
            Rotated vector in target frame.
        """
        return self._q.rotate(v)

    def inv(self) -> SO3:
        return SO3(self._q.inv())

    @classmethod
    def exp(cls, v: np.ndarray) -> SO3:
        r"""
        Exponential map from so(3) to SO(3).

        Parameters
        ----------
        v : np.ndarray, shape (3,)
            Rotation vector (axis-angle representation):

            .. math::

                v = \theta \hat{u}

        Returns
        -------
        SO3
            Rotation corresponding to the exponential map:

            .. math::

                R = \exp([v]_\times)
        """
        return cls(Quaternion.exp(v))

    def log(self) -> np.ndarray:
        r"""
        Logarithmic map from SO(3) to so(3).

        Returns
        -------
        np.ndarray, shape (3,)
            Rotation vector:

            .. math::

                v = \log(R)
        """
        return self._q.log()

    @classmethod
    def from_quaternion(cls, q: Quaternion):
        return cls(q)

    @classmethod
    def identity(cls) -> SO3:
        return cls(Quaternion.identity())
