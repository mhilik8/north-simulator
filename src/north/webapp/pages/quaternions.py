"""
=================
Quaternions Page
=================

:Author: Reuven Mol
"""

from dash import html, dcc
from north.webapp.content.quaternion_text import *

layout = html.Div([

    html.H1("Quaternions for Navigation"),

    dcc.Markdown(QUATERNION_INTRO),

    html.Hr(),

    html.Div([
        html.H2("Quaternion Geometry"),
        dcc.Graph(
            id="quaternion-geometry-graph",
            style={"height": "600px"}
        ),
    ]),

    html.Div([
        html.H2("Euler vs Quaternion"),
        dcc.Graph(
            id="euler-vs-quaternion-graph",
            style={"height": "600px"}
        ),
    ]),

    html.Div([
        html.H2("Quaternion Composition"),
        dcc.Graph(
            id="quaternion-composition-graph",
            style={"height": "600px"}
        ),
    ]),

    html.Div([
        html.H2("Interpolation"),
        dcc.Graph(
            id="slerp-graph",
            style={"height": "600px"}
        ),
    ]),

    dcc.Markdown(REFERENCES_TEXT),

], style={
    "padding": "20px",
    "maxWidth": "1400px",
    "margin": "auto",
})
