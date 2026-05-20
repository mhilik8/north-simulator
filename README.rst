================
North Simulation
================

Educational navigation, attitude, and gyrocompassing simulator for
exploring the geometry of inertial navigation systems and north-seeking
algorithms.

Overview
========

North Simulation is an interactive educational framework for understanding:

* rigid-body rotations
* coordinate-frame transformations
* SO(3) geometry
* quaternion-based orientation
* gyrocompassing principles
* Earth rotation sensing
* sensor-frame measurements
* navigation conventions
* attitude estimation pipelines

The project combines:

* mathematically rigorous rotation modeling
* interactive visualization
* engineering-oriented intuition
* realistic sensor abstractions
* educational web interfaces

The simulator is designed primarily for:

* engineers
* students
* researchers
* navigation enthusiasts
* inertial-navigation education

Main Concepts
=============

The application models the full north-seeker geometry pipeline::

    physical state
        ↓
    SO(3) transformations
        ↓
    Earth vectors
        ↓
    sensor-frame projections
        ↓
    ideal measurements
        ↓
    sensor models
        ↓
    navigation algorithms

The current architecture separates:

* core mathematics
* physical modeling
* visualization
* simulation
* algorithm plugins

This keeps the project extensible and suitable both for education and
experimentation.

Features
========

Scene Visualization
-------------------

Interactive visualization of:

* Earth gravity vector :math:`\vec{g}`
* Earth rotation vector :math:`\vec{\Omega}`
* local-level frame
* body frame
* sensor frame
* encoder rotation
* azimuth / pitch / roll geometry

SO(3) Exploration
-----------------

Educational tools for understanding:

* rotation groups
* non-commutativity
* exponential coordinates
* frame composition
* geometric intuition on the unit sphere

Quaternion Education
--------------------

Dedicated educational content explaining:

* quaternion algebra
* quaternion kinematics
* navigation applications
* numerical stability
* why quaternions dominate aerospace systems

Sensor Modeling
---------------

Planned support for:

* bias
* scale-factor error
* random walk
* bias instability
* output data rate
* realistic noise generation

Time-Domain Simulation
----------------------

Planned support for:

* trajectory generation
* motion profiles
* algorithm comparison
* Monte-Carlo analysis
* estimator evaluation

Coordinate Conventions
======================

The simulator uses the NED convention:

+------+---------+
| Axis | Meaning |
+======+=========+
| +X   | North   |
+------+---------+
| +Y   | East    |
+------+---------+
| +Z   | Down    |
+------+---------+

Frames currently modeled:

+--------+---------------------------+
| Symbol | Frame                     |
+========+===========================+
| l      | local-level-local-north   |
+--------+---------------------------+
| g      | ground                    |
+--------+---------------------------+
| o      | optics                    |
+--------+---------------------------+
| b      | body                      |
+--------+---------------------------+
| s      | sensor                    |
+--------+---------------------------+

Transformations follow the notation::

    c_a_to_b

meaning:

    transform a vector represented in frame ``a``
    into frame ``b``

Visual Language
================

The application uses a coherent engineering-oriented visual grammar.

Physical Vectors
----------------

+----------------+---------------------------+-------+
| Vector         | Symbol                    | Color |
+================+===========================+=======+
| Gravity        | :math:`\vec{g}`           | Red   |
+----------------+---------------------------+-------+
| Earth Rotation | :math:`\vec{\Omega}`     | Blue  |
+----------------+---------------------------+-------+

Frames of Reference
-------------------

Frames are visualized using:

* orthogonal black axes
* labeled unit vectors
* optional visibility toggles

Transformations
---------------

Rotations are represented geometrically by:

* trajectories on the unit sphere
* rotation-axis visualization
* frame transitions

Installation
============

Clone the repository::

    git clone https://github.com/<your-user>/north-simulation.git
    cd north-simulation

Install locally::

    pip install .

Editable development installation::

    pip install -e .

Optional dependency groups::

    pip install -e .[tests]
    pip install -e .[docs]
    pip install -e .[release]

Running the Web Application
===========================

Example::

    python app.py

or::

    python -m north.webapp.app

Then open::

    http://127.0.0.1:8050

Project Structure
=================

::

    north/
    ├── core/          # rotations, geometry, physical state
    ├── plots/         # plotting backends and graphics helpers
    ├── sensors/       # sensor models
    ├── simulation/    # time-domain simulation
    ├── algorithms/    # navigation algorithms
    ├── webapp/        # Dash educational interface
    └── theme/         # coherent visualise grammar

Development Philosophy
=======================

This project prioritizes:

1. clarity over cleverness
2. geometric intuition over black-box APIs
3. explicit conventions
4. educational value
5. engineering realism

The goal is not only to produce correct code,
but to make navigation geometry understandable.

Planned Roadmap
================

Near-Term
----------

* sensor noise models
* algorithm plugin system
* simulation engine
* quaternion visualization tools
* improved SO(3) graphics

Mid-Term
--------

* EKF demonstrations
* Allan variance analysis
* IMU calibration tools
* realistic gyro models
* Monte-Carlo experiments

Long-Term
---------

* full INS educational pipeline
* GNSS integration examples
* advanced attitude filters
* navigation datasets

Contributing
=============

Contributions are welcome, especially in:

* documentation
* educational explanations
* testing
* visualization
* numerical validation
* navigation algorithms

Before contributing:

* follow existing conventions
* prefer explicit mathematics
* document coordinate systems carefully
* include tests when possible

License
========

This repository is released under a custom
non-commercial educational license.

In short:

* educational usage is allowed
* academic usage is allowed
* research usage is allowed
* commercial usage is forbidden
* government and military usage are treated as commercial usage

See the LICENSE file for full details.

Author
======

Reuven Mol

Hebrew University of Jerusalem

Academic contact::

    reuven.mol@mail.huji.ac.il

Acknowledgements
================

This project draws inspiration from:

* aerospace navigation systems
* inertial navigation literature
* Lie-group robotics
* attitude-estimation research
* educational scientific visualization

References
===========

Recommended topics for readers:

* inertial navigation systems
* SO(3)
* Lie groups
* quaternion kinematics
* gyrocompassing
* Earth-rate sensing
* rigid-body rotations