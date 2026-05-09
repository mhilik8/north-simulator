from dash import html, dcc

navbar = html.Div(
    style={
        "display": "flex",
        "gap": "20px",
        "padding": "15px",
        "backgroundColor": "#1a1a1a",
        "borderBottom": "1px solid #333",
    },
    children=[

        dcc.Link(
            "Scene",
            href="/",
            style={"color": "white"},
        ),

        dcc.Link(
            "SO3",
            href="/so3",
            style={"color": "white"},
        ),
    ]
)