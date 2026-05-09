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

from dash import Dash, html, dcc
from north.webapp.router import page_container
from north.webapp.components.navbar import navbar
from north.webapp.callbacks.scene_callbacks import register_scene_callbacks


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
)


app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    page_container,
])

register_scene_callbacks(app)
