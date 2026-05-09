"""
========================
SO3 Educational Page
========================

:Author: Reuven Mol

Interactive educational page for understanding
the geometry and group structure of SO(3).

This page focuses on:

1. orientations as moving frames
2. rotation trajectories on the sphere
3. frame transformations
4. non-commutativity of rotations
5. intuition behind chained rotations
"""

from dash import html, dcc
from north.webapp.content import so3_text
# from north.plots.theme import


# =========================================================
# COMMON CARD STYLE
# =========================================================

CARD_STYLE = {
    "border": "1px solid #333",
    "borderRadius": "10px",
    "padding": "20px",
    "backgroundColor": "#1a1a1a",
    "marginBottom": "20px",
}


GRAPH_STYLE = {
    "height": "750px",
}


CONTROL_STYLE = {
    "padding": "20px",
    "border": "1px solid #333",
    "borderRadius": "10px",
    "backgroundColor": "#1a1a1a",
    "position": "sticky",
    "top": "20px",
}


# =========================================================
# LAYOUT
# =========================================================

layout = html.Div(

    style={
        "backgroundColor": "#111111",
        "color": "white",
        "padding": "20px",
        "fontFamily": "Arial",
    },

    children=[

        # =====================================================
        # PAGE HEADER
        # =====================================================

        html.H1(
            "SO(3) Rotation Explorer",
            style={"textAlign": "center"},
        ),

        html.P(
            (
                "Interactive visual exploration of 3D rotations, "
                "reference frames, and rotational geometry."
            ),
            style={
                "textAlign": "center",
                "marginBottom": "40px",
            },
        ),

        # =====================================================
        # MAIN GRID
        # =====================================================

        html.Div(

            style={
                "display": "grid",
                "gridTemplateColumns": "420px 1fr",
                "gap": "20px",
                "alignItems": "start",
            },

            children=[

                # =================================================
                # CONTROL PANEL
                # =================================================

                html.Div(

                    style=CONTROL_STYLE,

                    children=[

                        html.H2("Rotation Controls"),

                        dcc.Markdown(
                            so3_text.CONTROLS_INTRO,
                            mathjax=True
                        ),

                        html.Hr(),

                        # =========================================
                        # AZIMUTH
                        # =========================================

                        html.H3("Azimuth"),

                        html.P(
                            so3_text.AZIMUTH_TEXT
                        ),

                        dcc.Slider(
                            id="so3-azimuth-slider",
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

                        # =========================================
                        # PITCH
                        # =========================================

                        html.H3("Pitch"),

                        dcc.Markdown(
                            so3_text.PITCH_TEXT,
                            mathjax=True,
                        ),

                        dcc.Slider(
                            id="so3-pitch-slider",
                            min=-45,
                            max=45,
                            step=0.1,
                            value=0,
                            marks={
                                -45: "-45",
                                -20: "-20",
                                0: "0",
                                20: "20",
                                45: "45",
                            },
                        ),

                        html.Br(),

                        # =========================================
                        # ROLL
                        # =========================================

                        html.H3("Roll"),

                        dcc.Markdown(
                            so3_text.ROLL_TEXT,
                            mathjax=True,
                        ),

                        dcc.Slider(
                            id="so3-roll-slider",
                            min=-45,
                            max=45,
                            step=0.1,
                            value=0,
                            marks={
                                -45: "-45",
                                -20: "-20",
                                0: "0",
                                20: "20",
                                45: "45",
                            },
                        ),

                        html.Br(),

                        # =========================================
                        # ENCODER
                        # =========================================

                        html.H3("Encoder"),

                        dcc.Markdown(
                            so3_text.ENCODER_TEXT,
                            mathjax=True,
                        ),

                        dcc.Slider(
                            id="so3-encoder-slider",
                            min=0,
                            max=360,
                            step=0.1,
                            value=0,
                            marks={
                                0: "0",
                                90: "90",
                                180: "180",
                                270: "270",
                                360: "360",
                            },
                        ),

                        html.Hr(),

                        # =========================================
                        # VISIBILITY TOGGLES
                        # =========================================

                        html.H2("Visibility"),

                        dcc.Checklist(

                            id="so3-visibility-checklist",

                            options=[

                                {
                                    "label": " Unit Sphere",
                                    "value": "sphere",
                                },

                                {
                                    "label": " Local-Level Plane",
                                    "value": "plane",
                                },

                                {
                                    "label": " Gravity Vector",
                                    "value": "gravity",
                                },

                                {
                                    "label": " Earth Rotation Vector",
                                    "value": "earth_rate",
                                },

                                {
                                    "label": " Reference Frames",
                                    "value": "frames",
                                },

                                {
                                    "label": " Rotation Trajectories",
                                    "value": "trajectories",
                                },

                                {
                                    "label": " Rotation Axes",
                                    "value": "axes",
                                },

                            ],

                            value=[
                                "sphere",
                                "gravity",
                                "earth_rate",
                                "frames",
                                "trajectories",
                            ],

                            style={
                                "display": "grid",
                                "gap": "10px",
                            }
                        ),
                    ],
                ),

                # =================================================
                # CONTENT COLUMN
                # =================================================

                html.Div(

                    children=[

                        # =========================================
                        # INTRODUCTION
                        # =========================================

                        html.Div(

                            style=CARD_STYLE,

                            children=[

                                html.H2(
                                    "What is SO(3)?"
                                ),

                                dcc.Markdown(
                                    so3_text.SO3_INTRO,
                                    mathjax=True
                                ),

                                html.Div(
                                    id="so3-main-equation",
                                    children=[
                                        html.Div(
                                            "SO(3) equation placeholder",
                                            style={
                                                "padding": "40px",
                                                "textAlign": "center",
                                                "border": "1px dashed #666",
                                            }
                                        )
                                    ]
                                ),
                            ]
                        ),

                        # =========================================
                        # MAIN SPHERE GRAPH
                        # =========================================

                        html.Div(

                            style=CARD_STYLE,

                            children=[

                                html.H2(
                                    "Orientation Sphere"
                                ),

                                dcc.Markdown(
                                    so3_text.ORIENTATION_SPHERE_TEXT,
                                    mathjax=True,
                                ),

                                dcc.Graph(
                                    id="so3-orientation-sphere",
                                    style=GRAPH_STYLE,
                                ),
                            ]
                        ),

                        # =========================================
                        # TRANSFORMATION PIPELINE
                        # =========================================

                        html.Div(

                            style=CARD_STYLE,

                            children=[

                                html.H2(
                                    "Transformation Pipeline"
                                ),

                                dcc.Markdown(
                                    so3_text.PIPELINE_TEXT,
                                    mathjax=True,
                                ),

                                html.Div(
                                    id="so3-pipeline-equation",
                                    children=[
                                        html.Div(
                                            "Pipeline equation placeholder",
                                            style={
                                                "padding": "40px",
                                                "textAlign": "center",
                                                "border": "1px dashed #666",
                                            }
                                        )
                                    ]
                                ),
                            ]
                        ),

                        # =========================================
                        # NON COMMUTATIVITY
                        # =========================================

                        html.Div(

                            style=CARD_STYLE,

                            children=[

                                html.H2(
                                    "Non-Commutativity"
                                ),

                                dcc.Markdown(
                                    so3_text.NON_COMMUTATIVITY_TEXT,
                                    mathjax=True,
                                ),

                                html.Div(

                                    style={
                                        "display": "grid",
                                        "gridTemplateColumns": "1fr 1fr",
                                        "gap": "20px",
                                    },

                                    children=[

                                        html.Div(

                                            style={
                                                "border": "1px solid #333",
                                                "borderRadius": "10px",
                                                "padding": "10px",
                                            },

                                            children=[

                                                html.H3(
                                                    "Rz(ψ) Ry(θ)"
                                                ),

                                                dcc.Graph(
                                                    id="so3-left-order-graph",
                                                    style={
                                                        "height": "600px",
                                                    }
                                                ),
                                            ]
                                        ),

                                        html.Div(

                                            style={
                                                "border": "1px solid #333",
                                                "borderRadius": "10px",
                                                "padding": "10px",
                                            },

                                            children=[

                                                html.H3(
                                                    "Ry(θ) Rz(ψ)"
                                                ),

                                                dcc.Graph(
                                                    id="so3-right-order-graph",
                                                    style={
                                                        "height": "600px",
                                                    }
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),

                        # =========================================
                        # REFERENCES
                        # =========================================

                        html.Div(

                            style=CARD_STYLE,

                            children=[

                                html.H2(
                                    "References and Further Reading"
                                ),

                                dcc.Markdown(
                                    so3_text.REFERENCES_TEXT,
                                    mathjax=True,
                                ),

                                html.Ul(

                                    children=[

                                        html.Li(
                                            html.A(
                                                "SO(3) — Wikipedia",
                                                href="https://en.wikipedia.org/wiki/3D_rotation_group",
                                                target="_blank",
                                                style={"color": "#66b3ff"},
                                            )
                                        ),

                                        html.Li(
                                            html.A(
                                                "Euler Angles — Wikipedia",
                                                href="https://en.wikipedia.org/wiki/Euler_angles",
                                                target="_blank",
                                                style={"color": "#66b3ff"},
                                            )
                                        ),

                                        html.Li(
                                            html.A(
                                                "Direction Cosine Matrix",
                                                href="https://en.wikipedia.org/wiki/Direction_cosine",
                                                target="_blank",
                                                style={"color": "#66b3ff"},
                                            )
                                        ),

                                        html.Li(
                                            html.A(
                                                "Lie Groups for Engineers",
                                                href="https://ethaneade.com/lie.pdf",
                                                target="_blank",
                                                style={"color": "#66b3ff"},
                                            )
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ]
)