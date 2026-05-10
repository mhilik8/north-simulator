"""
===========
Earth Model
===========

:Author: Reuven Mol

Physical constants and reference vectors related to Earth dynamics.

Overview
--------
This module provides Earth-related physical quantities commonly required
for gyrocompass and inertial-navigation simulations.

The module intentionally contains only pure functions and constants.
No mutable state or Earth-model classes are used in order to keep the
simulation core mathematically transparent and easy to reason about.

Frame Convention
----------------
All vectors returned by this module are expressed in the local-level
North-East-Down (NED) frame.

The NED frame axes are defined as:

- X-axis : geographic north
- Y-axis : east
- Z-axis : down

This corresponds to the standard local navigation frame commonly used
in inertial navigation systems and gyrocompass literature.

Units
-----
Unless explicitly stated otherwise:

- angles are expressed in radians
- angular rates are expressed in radians per second
- gravity vectors are normalized to units of ``g``

Notes
-----
The vectors returned by this module represent idealized Earth quantities.

The current implementation intentionally ignores:

- Earth ellipsoid corrections
- local gravity variations
- transport rate
- centrifugal effects
- altitude dependence

These effects may be added later if higher-fidelity simulation becomes
necessary.

References
----------
Earth rotation constants are taken from:

https://hpiers.obspm.fr/eop-pc/models/constants.html
"""

import numpy as np

EARTH_RATE_DEGREES_PER_HOUR = 15.04106687606545  # [deg/hour] from https://hpiers.obspm.fr/eop-pc/models/constants.html
"""
Earth rotation rate in degrees per hour.

This value corresponds to the sidereal rotation rate of Earth.
"""

EARTH_RATE = np.deg2rad(EARTH_RATE_DEGREES_PER_HOUR / 3600)  # [rad/sec]
"""
Earth rotation rate in radians per second.
"""


def earth_rotation_l(latitude: float) -> np.array:
    """
    Calculate the Earth rotation vector in the local-level-local-north NED frame.

    The Earth rotation vector describes the angular velocity of Earth relative to inertial space expressed in the
    local-level-local-north frame.

    In the local-level North-East-Down frame, the vector is:

    .. math::

        \\omega_{ie}^L
        =
        \\Omega
        \\begin{bmatrix}
            \\cos(\\lambda) \\\\
            0 \\\\
            -\\sin(\\lambda)
        \\end{bmatrix}

    where:

    - :math:`\\Omega` is the Earth rotation rate
    - :math:`\\lambda` is the geographic latitude

    Parameters
    ----------
    latitude : float
        Geographic latitude in radians.

        Positive latitude corresponds to the Northern Hemisphere.

    Returns
    -------
    np.ndarray of shape (3,)
        Earth rotation vector expressed in the local-level-local-north NED frame [deg/hour].

    Notes
    -----
    The vector components follow the NED convention:

    .. math::

        [north, east, down]

    Therefore:

    - at the equator:

      .. math::

          \\omega_{ie}^L = [\\Omega, 0, 0]

    - at the North Pole:

      .. math::

          \\omega_{ie}^L = [0, 0, -\\Omega]

    - at the South Pole:

      .. math::

          \\omega_{ie}^L = [0, 0, +\\Omega]

    Examples
    --------
    Calculate the Earth rotation vector at 45 degrees latitude:

    >>> earth_rotation_l(np.deg2rad(45))
    """
    return EARTH_RATE_DEGREES_PER_HOUR * np.array([np.cos(latitude), 0, -np.sin(latitude)])


def earth_gravity_l() -> np.array:
    """
    Return the normalized gravity vector in the local-level-local-north NED frame.

    The gravity vector points in the positive down direction according to the North-East-Down convention.

    The returned vector is:

    .. math::

        g^L =
        \\begin{bmatrix}
            0 \\\\
            0 \\\\
            1
        \\end{bmatrix}

    Returns
    -------
    np.ndarray of shape (3,)
        Normalized gravity vector expressed in the local-level NED frame.

    Notes
    -----
    The gravity vector is normalized to units of ``g`` rather than physical acceleration units such as ``m/sec^2``.

    Accelerometers do not directly measure gravity.

    Under static conditions, an accelerometer measures the reaction force opposing gravity, commonly referred to as
    *specific force*.

    Therefore, under static conditions:

    .. math::

        a_{measured} \\approx -g^L

    This sign difference is a common source of confusion when working with inertial sensors.

    Examples
    --------
    Retrieve the gravity vector:

    >>> earth_gravity_l()
    """
    return np.array([0, 0, 1])
