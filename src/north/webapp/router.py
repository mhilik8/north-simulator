from dash import html, callback, Output, Input

from north.webapp.pages.scene import layout as scene_layout
from north.webapp.pages.so3 import layout as so3_layout


page_container = html.Div(id="page-container")


@callback(
    Output("page-container", "children"),
    Input("url", "pathname"),
)
def route(pathname):

    if pathname == "/so3":
        return so3_layout

    return scene_layout