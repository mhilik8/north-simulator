"""
========
SO3 text
========

the text content for the SO3 page
"""

SO3_INTRO = r"""
# SO(3) and Navigation

Navigation is fundamentally a problem of orientation.

The state of a north-seeking system is not only a collection of angles.
It is a sequence of rotations that map vectors between frames of reference.

This page introduces the geometric structure behind those rotations:

- the rotation group $SO(3)$
- frame transformations
- axis-angle intuition
- non-commutativity of rotations
- encoder-induced motion on the unit sphere
- the relationship between physical vectors and coordinate systems

The goal is not only mathematical correctness.
The goal is geometric intuition.

Throughout this page:

- the unit sphere represents orientation space
- trajectories on the sphere represent rotations
- arrows represent physical vectors
- local frames are shown as orthogonal triads
- transformations are shown as continuous motion

The visual language follows the same conventions used in the Scene page.
"""


CONTROLS_INTRO = r"""
# Controls

The controls define a sequence of rotations applied to the system.

Each slider corresponds to a physical transformation between two frames.

The order matters.

In three-dimensional space, rotations do not commute.
Changing the order of operations changes the final orientation.

The controls therefore define a rotation pipeline:

$$
C = C_{L\to G}
C_{G\to O}
C_{O\to B}
C_{B\to S}
$$

where:

- $L$ is the local-level frame
- $G$ is the geographic frame
- $O$ is the optical frame
- $B$ is the body frame
- $S$ is the sensor frame

The sphere graphics visualize how these transformations move vectors across the unit sphere.
"""


AZIMUTH_TEXT = r"""
# Azimuth Rotation

Azimuth is the rotation around the local vertical axis.

It defines the heading of the system relative to geographic north.

Mathematically, azimuth is represented by a rotation around the local $Z$ axis:

$$
R_z(\psi)
$$

where:

- $\psi$ is the azimuth angle
- positive rotation is clockwise when viewed from above

On the orientation sphere:

- azimuth motion traces a horizontal trajectory
- the trajectory lies on a constant-elevation circle
- the north vector rotates inside the local-level plane

This transformation maps the local-level frame into the geographic frame.
"""


PITCH_TEXT = r"""
# Pitch Rotation

Pitch is the rotation around the lateral axis of the aircraft.

Positive pitch raises the nose upward.

The pitch transformation is represented by:

$$
R_y(\theta)
$$

where $\theta$ is the pitch angle.

Pitch changes the elevation of the body frame relative to the local-level plane.

On the sphere:

- pitch produces a vertical arc
- the motion changes the angle relative to gravity
- the gravity projection on the sensor plane changes continuously

Pitch is especially important because even small inclination errors strongly affect north-seeking performance.
"""


ROLL_TEXT = r"""
# Roll Rotation

Roll is the rotation around the longitudinal body axis.

Positive roll lowers the right wing.

The roll transformation is represented by:

$$
R_x(\phi)
$$

where $\phi$ is the roll angle.

Roll changes the orientation of the motor plane.

On the sphere:

- roll rotates the sensor plane around the body axis
- the motor plane appears as a great-circle trajectory
- gravity and Earth rotation project differently onto the rotating frame

The interaction between roll and encoder motion is one of the central geometric ideas in north seeking.
"""


ENCODER_TEXT = r"""
# Encoder Rotation

The encoder represents the controlled rotation of the sensor itself.

This is the final transformation in the pipeline.

The encoder rotates the sensor frame relative to the body frame:

$$
R_z(\alpha)
$$

where $\alpha$ is the encoder angle.

The encoder rotates clockwise.

When the encoder angle is zero:

- the body frame and sensor frame are aligned
- the sensor measurement axis coincides with the motor reference axis

The rotating sensor transforms constant Earth vectors into periodic measurements.

This modulation is the foundation of many north-seeking algorithms.
"""


ORIENTATION_SPHERE_TEXT = r"""
# Orientation Sphere

The orientation sphere is a geometric visualization of rotational motion.

Every point on the sphere corresponds to the direction of a transformed unit vector.

Instead of visualizing matrices directly, we visualize their action on vectors.

This provides intuition for:

- frame transformations
- axis-angle rotations
- composition of rotations
- non-commutativity
- encoder trajectories
- projection geometry

The sphere also makes it possible to understand rotations as continuous paths.

A transformation is not only a final orientation.
It is a trajectory through orientation space.

This viewpoint becomes especially important when studying:

- gyroscope propagation
- inertial integration
- quaternion kinematics
- Kalman filtering on manifolds
- optimization on $SO(3)$

In navigation systems, the geometry itself is often more important than the coordinates used to represent it.
"""


PIPELINE_TEXT = r"""
# Rotation Pipeline

The north seeker applies several transformations in sequence.

Each transformation maps vectors from one frame into another.

The complete chain is:

$$
C =
R_z(\psi)
R_y(\theta)
R_x(\phi)
R_z(\alpha)
$$

where:

- $\psi$ is azimuth
- $\theta$ is pitch
- $\phi$ is roll
- $\alpha$ is encoder angle

The order is essential.

Applying pitch before roll does not produce the same orientation as applying roll before pitch.

This is one of the defining properties of $SO(3)$.

The sphere graphics show this directly:

- changing the order changes the trajectory
- different paths produce different final vectors
- rotations cannot be treated as ordinary addition

This motivates the use of:

- rotation matrices
- Lie groups
- quaternions
- exponential coordinates

for real navigation systems.
"""


NON_COMMUTATIVITY_TEXT = r"""
# Non-Commutativity

Rotations in three dimensions do not commute.

In general:

$$
R_x(\phi)R_y(\theta)
\neq
R_y(\theta)R_x(\phi)
$$

This means:

- the order of operations matters
- intermediate frames matter
- trajectories through orientation space matter

This property is not a numerical artifact.
It is a geometric property of physical space.

The sphere visualization makes this intuitive.

Two sequences of rotations may:

- start from the same orientation
- use the same angles
- end at different final orientations

This is one of the reasons Euler angles become difficult for:

- inertial navigation
- optimization
- filtering
- long-duration propagation

Quaternions and Lie-group formulations avoid many of these problems by representing orientation globally rather than as sequential angle corrections.
"""


REFERENCES_TEXT = r"""
# References and Further Reading

## Rotations and SO(3)

- Shuster, Malcolm D. — *A Survey of Attitude Representations*
- Chirikjian — *Stochastic Models, Information Theory, and Lie Groups*
- Hall — *Lie Groups, Lie Algebras, and Representations*

## Navigation

- Groves — *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*
- Titterton & Weston — *Strapdown Inertial Navigation Technology*
- Savage — *Strapdown Analytics*

## Quaternions

- Kuipers — *Quaternions and Rotation Sequences*
- Hanson — *Visualizing Quaternions*

## Geometry

- Marsden & Ratiu — *Introduction to Mechanics and Symmetry*
- Abraham & Marsden — *Foundations of Mechanics*

The purpose of this project is not only to implement algorithms.
It is to build geometric intuition for navigation engineers.
"""
