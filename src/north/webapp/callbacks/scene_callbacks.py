"""
=========
callbacks
=========

:Author: Reuven Mol

all the callbacks for the webapp
"""

from dash import Dash, Output, Input
from north.plots.plot_latitude import latitude_view
from north.plots.plot_azimuth import azimuth_compass_view, azimuth_world_view
from north.plots.plot_inclination import inclination_3d_view, inclination_gauge_view
from north.plots.plot_motor_plain import motor_plane_view
from north.plots.scene import ScenePlotter


def register_scene_callbacks(app: Dash) -> None:
    @app.callback(
        Output("latitude-graph", "figure"),
        Output("azimuth-graph", "figure"),
        Output("compass-graph", "figure"),
        Output("inclination-3d-graph", "figure"),
        Output("inclination-gauge-graph", "figure"),
        Output("motor-plane-graph", "figure"),
        Output("measurement-text", "children"),
        Input("latitude-slider", "value"),
        Input("azimuth-slider", "value"),
        Input("pitch-slider", "value"),
        Input("roll-slider", "value"),
        Input("encoder-slider", "value"),
    )
    def update_scene(
            latitude_deg,
            azimuth_deg,
            pitch_deg,
            roll_deg,
            encoder_deg,
    ):
        # =====================================================
        # PHYSICAL STATE
        # =====================================================

        current_scene = ScenePlotter.from_physical_state(
            latitude_deg,
            azimuth_deg,
            pitch_deg,
            roll_deg,
            encoder_deg
        )

        # =====================================================
        # FIGURES
        # =====================================================

        #latitude (e -> l)
        latitude_fig = latitude_view(latitude_deg)

        # azimuth (l -> g)
        azimuth_fig = azimuth_world_view(azimuth_deg)
        compass_fig = azimuth_compass_view(azimuth_deg)

        # inclination (g -> b, include o as sub transformation)
        inclination_3d_fig = inclination_3d_view(pitch_deg, roll_deg)
        gauge_fig = inclination_gauge_view(pitch_deg, roll_deg)

        # motor plane
        motor_fig = motor_plane_view(encoder_deg)

        # =====================================================
        # TEXT OUTPUT
        # =====================================================

        gravity_sensor, omega_sensor = current_scene.vectors()

        text = f"""
    Physical State
    --------------
    Latitude : {latitude_deg:8.3f} deg
    Azimuth  : {azimuth_deg:8.3f} deg
    Pitch    : {pitch_deg:8.3f} deg
    Roll     : {roll_deg:8.3f} deg
    Encoder  : {encoder_deg:8.3f} deg


    Ideal Gravity Vector in Sensor Frame
    ------------------------------------
    [{gravity_sensor[0]: .6f},
     {gravity_sensor[1]: .6f},
     {gravity_sensor[2]: .6f}] g


    Ideal Earth Rotation Vector in Sensor Frame
    -------------------------------------------
    [{omega_sensor[0]: .10f},
     {omega_sensor[1]: .10f},
     {omega_sensor[2]: .10f}] deg/hour
    """

        return (
            latitude_fig,
            azimuth_fig,
            compass_fig,
            inclination_3d_fig,
            gauge_fig,
            motor_fig,
            text,
        )
