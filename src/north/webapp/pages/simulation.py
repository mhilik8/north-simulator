"""
=================
Simulator Page
=================

:Author: Reuven Mol
"""

from dash import html, dcc
from north.webapp.content.simulator_text import *

layout = html.Div([

    html.H1("Time Domain Simulation"),

    dcc.Markdown(SIMULATOR_INTRO),

    html.Hr(),

    html.Div([
        html.H2("Trajectory"),
        dcc.Graph(
            id="trajectory-graph",
            style={"height": "600px"}
        ),
    ]),

    html.Div([
        html.H2("Sensor Outputs"),
        dcc.Graph(
            id="sensor-output-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("North Estimation"),
        dcc.Graph(
            id="north-estimation-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Algorithm Comparison"),
        dcc.Graph(
            id="algorithm-comparison-graph",
            style={"height": "500px"}
        ),
    ]),

    html.Div([
        html.H2("Error Analysis"),
        dcc.Graph(
            id="error-analysis-graph",
            style={"height": "500px"}
        ),
    ]),

    dcc.Markdown(REFERENCES_TEXT),

], style={
    "padding": "20px",
    "maxWidth": "1400px",
    "margin": "auto",
})
