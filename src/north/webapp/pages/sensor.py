"""
==============
Sensor Page
==============

:Author: Reuven Mol
"""

from dash import html, dcc
from north.webapp.content.sensor_text import *

layout = html.Div([

    html.H1("Sensor and Noise Models"),

    dcc.Markdown(SENSOR_INTRO),

    html.Hr(),

    html.Div([
        html.H2("Ideal Sensor"),
        dcc.Graph(
            id="ideal-sensor-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Bias"),
        dcc.Graph(
            id="bias-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Noise"),
        dcc.Graph(
            id="noise-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Scale Factor"),
        dcc.Graph(
            id="scale-factor-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Misalignment"),
        dcc.Graph(
            id="misalignment-graph",
            style={"height": "500px"}
        ),
    ]),

    dcc.Markdown(REFERENCES_TEXT),

], style={
    "padding": "20px",
    "maxWidth": "1400px",
    "margin": "auto",
})
