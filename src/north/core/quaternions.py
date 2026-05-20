"""
===========
Quaternions
===========

:Author: Reuven Mol


"""
from __future__ import annotations
from typing import Union, Type, NamedTuple
import numpy as np

ArrayLike = Union[np.ndarray, list, tuple]


class EulerAngles(NamedTuple):
    roll: np.float64
    pitch: np.float64
    yaw: np.float64

    def __add__(self, other):
        return EulerAngles(self.roll+other.roll, self.pitch+other.pitch, self.yaw+other.yaw)

    @property
    def matrix(self):
        """Tait-Bryan ZYX"""

        cr = np.cos(self.roll)
        sr = np.sin(self.roll)
        cp = np.cos(self.pitch)
        sp = np.sin(self.pitch)
        cy = np.cos(self.yaw)
        sy = np.sin(self.yaw)
        return np.matrix(((cy*cp, cy*sp*sr -cr*sy,  sy*sr + cy*cr*sp),
                          (cp*sy, cy*cr + sy*sp*sr, cr*sy*sp -cy*sr ),
                          (-sp,   cp*sr,            cp*cr           )), dtype=np.float64)


class Quaternion:
    """
    Hamilton quaternion representing a rotation from frame m to frame n.

    Convention
    ----------
    - q represents rotation from m → n.
    - Angular velocity omega is expressed in m frame.
    - Update rule:
        q_new = q ⊗ exp(0.5 * omega * dt)

    Notes
    -----
    - Internally stored as ndarray shape (4,)
      [w, x, y, z]
    - Supports float32 and float64 explicitly.
    - All angular quantities are in radians.
    """

    __slots__ = ("q", "dtype")

    def __init__(
        self,
        w: float,
        x: float,
        y: float,
        z: float,
        dtype: Type[np.floating] = np.float64,
    ) -> None:
        self.dtype: Type[np.floating] = dtype
        self.q: np.ndarray = np.array([w, x, y, z], dtype=dtype)

    # ------------------------------------------------------------------
    # Basic Properties
    # ------------------------------------------------------------------

    @property
    def w(self) -> np.floating:
        """Return the real part of the quaternion."""
        return self.q[0]

    @property
    def vec(self) -> np.ndarray:
        """Return vector (imaginary) part."""
        return self.q[1:4]

    def as_ndarray(self) -> np.ndarray:
        """Return copy of quaternion as ndarray shape (4,)."""
        return self.q.copy()

    def copy(self) -> "Quaternion":
        """Return deep copy."""
        return Quaternion(*self.q, dtype=self.dtype)

    # ------------------------------------------------------------------
    # Norm and Normalization
    # ------------------------------------------------------------------

    def norm(self) -> np.floating:
        """Return quaternion Euclidean norm."""
        return np.linalg.norm(self.q)

    def normalize(self) -> "Quaternion":
        """Normalize quaternion in-place."""
        self.q /= self.norm()
        return self

    def normalized(self) -> "Quaternion":
        """Return normalized copy."""
        return self.copy().normalize()

    # ------------------------------------------------------------------
    # Conjugate and Inverse
    # ------------------------------------------------------------------

    def conj(self) -> "Quaternion":
        """
        Return quaternion conjugate.

        For unit quaternions this equals the inverse.
        """
        return Quaternion(
            self.w,
            -self.q[1],
            -self.q[2],
            -self.q[3],
            dtype=self.dtype,
        )

    def inv(self) -> "Quaternion":
        """
        Return quaternion inverse.
        """
        return self.conj() / (self.norm() ** 2)

    # ------------------------------------------------------------------
    # Operators
    # ------------------------------------------------------------------

    def __mul__(self, other: Union["Quaternion", float]) -> "Quaternion":
        """
        Hamilton product or scalar multiplication.
        """
        if isinstance(other, Quaternion):
            w1, x1, y1, z1 = self.q
            w2, x2, y2, z2 = other.q

            return Quaternion(
                w1*w2 - x1*x2 - y1*y2 - z1*z2,
                w1*x2 + x1*w2 + y1*z2 - z1*y2,
                w1*y2 - x1*z2 + y1*w2 + z1*x2,
                w1*z2 + x1*y2 - y1*x2 + z1*w2,
                dtype=self.dtype,
            )
        else:
            return Quaternion(*(self.q * other), dtype=self.dtype)

    def __rmul__(self, other: float) -> "Quaternion":
        return self.__mul__(other)

    def __truediv__(self, scalar: float) -> "Quaternion":
        return Quaternion(*(self.q / scalar), dtype=self.dtype)

    def __add__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(*(self.q + other.q), dtype=self.dtype)

    def __sub__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(*(self.q - other.q), dtype=self.dtype)

    def __repr__(self) -> str:
        return (
            f"Quaternion({self.w:.6f}, "
            f"{self.q[1]:.6f}, "
            f"{self.q[2]:.6f}, "
            f"{self.q[3]:.6f}, "
            f"dtype={self.dtype.__name__})"
        )

    # ------------------------------------------------------------------
    # Rotation Operations
    # ------------------------------------------------------------------

    def rotate(self, v: ArrayLike) -> np.ndarray:
        """
        Rotate 3D vector from m frame to n frame.

        Parameters
        ----------
        v : array-like, shape (3,)
            Vector expressed in m frame.

        Returns
        -------
        ndarray, shape (3,)
            Rotated vector expressed in n frame.
        """
        v = np.asarray(v, dtype=self.dtype)
        vq = Quaternion(0.0, *v, dtype=self.dtype)
        qr = self * vq * self.conj()
        return qr.vec

    def as_rotmat(self) -> np.ndarray:
        """
        Convert quaternion to 3x3 rotation matrix (m → n).

        Returns
        -------
        ndarray, shape (3,3)
        """
        w, x, y, z = self.q

        return np.array(
            [
                [1 - 2*(y*y + z*z), 2*(x*y - z*w),     2*(x*z + y*w)],
                [2*(x*y + z*w),     1 - 2*(x*x + z*z), 2*(y*z - x*w)],
                [2*(x*z - y*w),     2*(y*z + x*w),     1 - 2*(x*x + y*y)],
            ],
            dtype=self.dtype,
        )

    # ------------------------------------------------------------------
    # Lie Group Maps
    # ------------------------------------------------------------------

    @classmethod
    def exp(
        cls,
        phi: ArrayLike,
        dtype: Type[np.floating] = np.float64,
    ) -> Quaternion:
        """
        Exponential map from so(3) to SO(3).

        Parameters
        ----------
        phi : array-like, shape (3,)
            Rotation vector (radians).
        dtype : numpy floating type
            float32 or float64.

        Returns
        -------
        Quaternion
        """
        phi = np.asarray(phi, dtype=dtype)
        theta = np.linalg.norm(phi)

        if theta < 1e-12:
            return cls(1.0, 0.0, 0.0, 0.0, dtype=dtype)

        axis = phi / theta
        return cls(
            np.cos(theta / 2),
            *(np.sin(theta / 2) * axis),
            dtype=dtype,
        )

    def log(self) -> np.ndarray:
        """
        Logarithm map from SO(3) to so(3).

        Returns
        -------
        ndarray, shape (3,)
            Rotation vector (radians).
        """
        v = self.vec
        norm_v = np.linalg.norm(v)

        if norm_v < 1e-12:
            return np.zeros(3, dtype=self.dtype)

        theta = 2 * np.arctan2(norm_v, self.w)
        return theta * v / norm_v

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def identity(
        cls,
        dtype: Type[np.floating] = np.float64,
    ) -> "Quaternion":
        """Return identity quaternion."""
        return cls(1.0, 0.0, 0.0, 0.0, dtype=dtype)

    @classmethod
    def from_gyro(
        cls,
        omega_m: ArrayLike,
        dt: float,
        dtype: Type[np.floating] = np.float64,
    ) -> "Quaternion":
        """
        Construct incremental quaternion from angular velocity.

        Parameters
        ----------
        omega_m : array-like, shape (3,)
            Angular velocity in m frame [rad/s].
        dt : float
            Time step [s].
        dtype : numpy floating type

        Returns
        -------
        Quaternion
            delta quaternion exp(0.5 * omega_m * dt)
        """
        omega_m = np.asarray(omega_m, dtype=dtype)
        return cls.exp(0.5 * omega_m * dt, dtype=dtype)
