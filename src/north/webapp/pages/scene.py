"""
=====
Scene
=====

:Author: Reuven Mol

Main educational physical-scene page.
"""

from dash import dcc, html
from north.webapp.content.scene_text import (
    LATITUDE_TEXT,
    AZIMUTH_TEXT,
    INCLINATION_TEXT,
    ENCODER_TEXT,
    MEASUREMENT_TEXT,
)


# =========================================================
# SHARED STYLE
# =========================================================

CARD_STYLE = {
    "border": "1px solid #333",
    "borderRadius": "10px",
    "padding": "20px",
    "backgroundColor": "#1a1a1a",
    "marginBottom": "25px",
    "overflow": "hidden",
}

GRAPH_STYLE = {
    "height": "600px",
    "width": "100%",
}


# =========================================================
# PAGE LAYOUT
# =========================================================

layout = html.Div(

    style={
        "backgroundColor": "#111111",
        "color": "white",
        "padding": "20px",
        "fontFamily": "Arial",
    },

    children=[

        # =================================================
        # TITLE
        # =================================================

        html.H1(
            "North Seeker Physical Scene Explorer",
            style={"textAlign": "center"},
        ),

        html.P(
            (
                "Interactive educational environment for "
                "gyrocompass geometry and inertial measurements."
            ),
            style={
                "textAlign": "center",
                "marginBottom": "40px",
            },
        ),

        # =================================================
        # STAGE 1 — LATITUDE
        # =================================================

        html.Div(

            style=CARD_STYLE,

            children=[

                html.H2("1. Latitude"),

                dcc.Markdown(LATITUDE_TEXT, mathjax=True),

                html.Br(),

                dcc.Slider(
                    id="latitude-slider",
                    min=-90,
                    max=90,
                    step=0.1,
                    value=32.0,
                    marks={
                        -90: "-90",
                        -45: "-45",
                        0: "0",
                        45: "45",
                        90: "90",
                    },
                ),

                html.Br(),

                dcc.Graph(
                    id="latitude-graph",
                    style=GRAPH_STYLE,
                    mathjax=True,
                    config={"responsive": True},
                ),

            ],
        ),

        # =================================================
        # STAGE 2 — AZIMUTH
        # =================================================

        html.Div(

            style=CARD_STYLE,

            children=[

                html.H2("2. Azimuth"),

                dcc.Markdown(AZIMUTH_TEXT, mathjax=True),

                html.Br(),

                dcc.Slider(
                    id="azimuth-slider",
                    min=0,
                    max=360,
                    step=0.1,
                    value=45,
                    marks={
                        0: "0",
                        90: "90",
                        180: "180",
                        270: "270",
                        360: "360",
                    },
                ),

                html.Br(),

                html.Div(

                    style={
                        "display": "grid",
                        "gridTemplateColumns": "minmax(0, 1fr) minmax(0, 1fr)",
                        "gap": "20px",
                    },

                    children=[

                        dcc.Graph(
                            id="azimuth-graph",
                            style=GRAPH_STYLE,
                            mathjax=True,
                            config={"responsive": True},
                        ),

                        dcc.Graph(
                            id="compass-graph",
                            style=GRAPH_STYLE,
                            mathjax=True,
                            config={"responsive": True},
                        ),
                    ],
                ),
            ],
        ),

        # =================================================
        # STAGE 3 — INCLINATION
        # =================================================

        html.Div(

            style=CARD_STYLE,

            children=[

                html.H2("3. Inclination"),

                dcc.Markdown(INCLINATION_TEXT, mathjax=True),

                html.Br(),

                html.Label("Pitch"),

                dcc.Slider(
                    id="pitch-slider",
                    min=-30,
                    max=30,
                    step=0.1,
                    value=0,
                ),

                html.Br(),

                html.Label("Roll"),

                dcc.Slider(
                    id="roll-slider",
                    min=-45,
                    max=45,
                    step=0.1,
                    value=0,
                ),

                html.Br(),

                html.Div(

                    style={
                        "display": "grid",
                        "gridTemplateColumns": "minmax(0, 1fr) minmax(0, 1fr)",
                        "gap": "20px",
                    },

                    children=[

                        dcc.Graph(
                            id="inclination-3d-graph",
                            style=GRAPH_STYLE,
                            mathjax=True,
                            config={"responsive": True},
                        ),

                        dcc.Graph(
                            id="inclination-gauge-graph",
                            style=GRAPH_STYLE,
                            mathjax=True,
                            config={"responsive": True},
                        ),
                    ],
                ),
            ],
        ),

        # =================================================
        # STAGE 4 — ENCODER
        # =================================================

        html.Div(

            style=CARD_STYLE,

            children=[

                html.H2("4. Encoder"),

                dcc.Markdown(ENCODER_TEXT, mathjax=True),

                html.Br(),

                dcc.Slider(
                    id="encoder-slider",
                    min=0,
                    max=360,
                    step=0.1,
                    value=0,
                ),

                html.Br(),

                dcc.Graph(
                    id="motor-plane-graph",
                    style=GRAPH_STYLE,
                    mathjax=True,
                    config={"responsive": True},
                ),
            ],
        ),

        # =================================================
        # STAGE 5 — MEASUREMENTS
        # =================================================

        html.Div(

            style=CARD_STYLE,

            children=[

                html.H2("5. Ideal IMU Measurements"),

                dcc.Markdown(MEASUREMENT_TEXT, mathjax=True),

                html.Br(),

                html.Pre(
                    id="measurement-text",
                    style={
                        "fontSize": "16px",
                        "lineHeight": "1.6",
                    },
                ),
            ],
        ),
    ],
)
