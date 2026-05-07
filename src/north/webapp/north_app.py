"""
=====================
North Seeker Dash App
=====================

:Author: Reuven Mol

First educational Dash application.

This application shows the full physical pipeline:

physical state
    -> rotations
    -> Earth vectors
    -> sensor-frame vectors
    -> ideal measurements

The goal is not yet simulation.
The goal is:

1. educational intuition
2. geometry validation
3. convention validation
4. future simulator foundation
"""

from dash import Dash, Output, Input
from north.webapp.pages.scene import layout as scene_layout
from north.webapp.callbacks import update_scene


# =========================================================
# APPLICATION
# =========================================================

app = Dash(__name__)

# =========================================================
# LAYOUT
# =========================================================

app.layout = scene_layout

# =========================================================
# CALLBACKS
# =========================================================

app.callback(
    Output("latitude-graph", "figure"),
    Output("azimuth-graph", "figure"),
    Output("compass-graph", "figure"),
    Output("inclination-3d-graph", "figure"),
    Output("inclination-gauge-graph", "figure"),
    Output("measurement-text", "children"),
    Input("latitude-slider", "value"),
    Input("azimuth-slider", "value"),
    Input("pitch-slider", "value"),
    Input("roll-slider", "value"),
    Input("encoder-slider", "value"),
)(update_scene)
