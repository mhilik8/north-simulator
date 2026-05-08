"""
=====
Theme
=====

:Author: Reuven Mol

Define and centralize the visual grammar of the north-seeker simulation and educational application.

Overview
--------
This module contains all global visual conventions used throughout the application.
The purpose of this module is not merely aesthetic, but semantic.

The graphical language of the application is designed such that:

- every physical entity has a unique and persistent visual identity,
- identical colors always represent identical physical meanings,
- symbols are mathematically consistent across plots,
- and users can develop intuition without repeatedly decoding visuals.

The visual grammar therefore acts as an extension of the mathematical model itself.

Notes
-----
The visualization philosophy of the project prioritizes:

1. Physical intuition
2. Semantic consistency
3. Educational clarity

over:
- artistic freedom,
- arbitrary styling,
- or plot-specific customization.

As a result, all visualization modules are expected to import colors, labels, and styling rules from this module rather
than defining their own local styles.

Visual Conventions
------------------

Physical Vectors
^^^^^^^^^^^^^^^^

Two primary Earth-bound physical vectors appear throughout the system.

Gravity Vector
~~~~~~~~~~~~~~

The Earth gravity vector is represented by:

.. math::

    \vec{g}

Visual rules:
- Always colored red.
- Always drawn as an arrow.
- Label attached near arrow head.
- Usually normalized to unit magnitude.
- Units throughout the application are expressed in multiples of:

  .. math::

      g

Earth Rotation Vector
~~~~~~~~~~~~~~~~~~~~~

The Earth rotation vector is represented by:

.. math::

    \vec{\Omega}

Visual rules:
- Always colored blue.
- Always drawn as an arrow.
- Label attached near arrow head.
- Often normalized for geometric intuition.
- Physical units are typically:

  .. math::

      \frac{deg}{hour}

- In some visualizations the magnitude may be preserved to emphasize projection effects.

Frames of Reference
^^^^^^^^^^^^^^^^^^^

Frames are represented as orthogonal triads:

.. math::

    (\hat{X}, \hat{Y}, \hat{Z})

Visual rules:
- Axes are always black.
- Each axis is represented as an arrow.
- Labels are attached near arrow heads.
- Frame superscripts denote frame identity:

  .. math::

      \hat{X}^b, \hat{Y}^l, \hat{Z}^s

where:
- :math:`b` denotes body frame,
- :math:`l` denotes local-level-local-north frame,
- :math:`s` denotes sensor frame,
- etc.

Local-Level Plane
^^^^^^^^^^^^^^^^^

The local-level plane is a fundamental geometric object and is
represented visually as:

- translucent red plane,
- usually accompanied by a compass rose,
- typically centered on the active reference frame origin.

Transformations
^^^^^^^^^^^^^^^

Rotational transformations are represented geometrically as
trajectories traced on the unit sphere.

Specifically:
- the transformed body x-axis trajectory is shown,
- the rotation axis may optionally be displayed,
- transformations emphasize the manifold structure of:

  .. math::

      SO(3)

rather than only matrix algebra.

Aircraft Representation
^^^^^^^^^^^^^^^^^^^^^^^

When aircraft graphics are used:
- preference is given to commercial four-engine aircraft,
- low-poly vector-compatible models are preferred,
- orientation cues should remain visually clear even at small scales.

Implementation Notes
--------------------
This module intentionally contains only constants and lightweight helpers.

It should remain:
- dependency-light,
- globally importable,
- and stable across the entire application.

Examples
--------
Using semantic colors inside a plotting module:

>>> fig.add_trace(go.Scatter(
...     x=[0, 1],
...     y=[0, 0],
...     line=dict(color=GRAVITY_COLOR)
... ))

Using standard labels:

>>> annotation_text = GRAVITY_LABEL
"""

# ============================================================
# COLORS
# ============================================================

GRAVITY_COLOR = "#d62728"
"""
Canonical color for the Earth gravity vector.

Represents:

.. math::

    \vec{g}

The color red was chosen to emphasize:
- weight,
- verticality,
- and Earth-bound directionality.
"""

EARTH_ROTATION_COLOR = "#1f77b4"
"""
Canonical color for the Earth rotation vector.

Represents:

.. math::

    \vec{\Omega}

Blue was selected to visually distinguish rotational/inertial
phenomena from gravitational phenomena.
"""

FRAME_COLOR = "#111111"
"""
Canonical color for frame-of-reference axes.

Frames are intentionally rendered in neutral dark colors so that
physical vectors remain visually dominant.
"""

LOCAL_LEVEL_COLOR = "rgba(255,0,0,0.15)"
"""
Canonical color for the local-level plane.

The plane is rendered semi-transparent to preserve visibility of
objects and vectors behind it while maintaining geometric context.
"""

TRAJECTORY_COLOR = "#ffcc00"
"""
Canonical color for rotational trajectories on the unit sphere.

Used to visualize:
- rotational paths,
- group actions,
- and SO(3) manifold intuition.
"""

# ============================================================
# LABELS
# ============================================================

GRAVITY_LABEL = r"\vec{g}"
"""
Canonical LaTeX label for the gravity vector.
"""

EARTH_ROTATION_LABEL = r"\vec{\Omega}"
"""
Canonical LaTeX label for the Earth rotation vector.
"""

# ============================================================
# UI COLORS
# ============================================================

BACKGROUND_COLOR = "#111111"
"""
Global application background color.
"""

CARD_COLOR = "#1a1a1a"
"""
Background color for cards, panels, and grouped controls.
"""

AIRCRAFT_SYMBOL_COLOR = "#f0f0f0"
"""
Canonical color for aircraft symbols and vehicle indicators.
"""

HIGHLIGHT_COLOR = "#ffcc00"
"""
Highlight color for:
- active rotations,
- headings,
- trajectories,
- interactive emphasis.
"""

SKY_COLOR = "rgb(110,140,180)"  # used by inclination gauge
EARTH_COLOR = "rgb(120,90,70)"  # used by inclination gauge
