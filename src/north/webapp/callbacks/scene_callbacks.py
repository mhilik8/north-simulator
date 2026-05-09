"""
=========
callbacks
=========

:Author: Reuven Mol

all the callbacks for the webapp
"""

import numpy as np
from dash import Dash, Output, Input
from north.core.state import PhysicalState
from north.core.rotations import SO3
from north.core.earth import earth_rotation_l, earth_gravity_l
from north.plots.plot_latitude import latitude_view
from north.plots.plot_azimuth import azimuth_compass_view, azimuth_world_view
from north.plots.plot_inclination import inclination_3d_view, inclination_gauge

# =========================================================
# HELPERS
# =========================================================

def Rx(theta: float) -> SO3:
    return SO3.exp(np.array([theta, 0.0, 0.0]))



def Ry(theta: float) -> SO3:
    return SO3.exp(np.array([0.0, theta, 0.0]))



def Rz(theta: float) -> SO3:
    return SO3.exp(np.array([0.0, 0.0, theta]))


def register_scene_callbacks(app: Dash) -> None:
    @app.callback(
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

        state = PhysicalState.from_floats(
            np.deg2rad(latitude_deg),
            np.deg2rad(azimuth_deg),
            np.deg2rad(pitch_deg),
            np.deg2rad(roll_deg),
            np.deg2rad(encoder_deg),
        )

        # =====================================================
        # ROTATIONS
        # =====================================================

        R_azimuth = Rz(state.azimuth)
        R_pitch = Ry(-state.pitch)
        R_roll = Rx(state.roll)
        R_encoder = Rz(state.encoder)

        R_total = (
                R_azimuth
                * R_pitch
                * R_roll
                * R_encoder
        )

        # =====================================================
        # EARTH VECTORS
        # =====================================================

        gravity_l = earth_gravity_l()
        omega_l = earth_rotation_l(state.latitude)

        # =====================================================
        # SENSOR FRAME VECTORS
        # =====================================================

        gravity_sensor = R_total.apply(gravity_l)
        omega_sensor = R_total.apply(omega_l)

        # =====================================================
        # FIGURES
        # =====================================================

        latitude_fig = latitude_view(latitude_deg)

        azimuth_fig = azimuth_world_view(azimuth_deg)

        compass_fig = azimuth_compass_view(azimuth_deg)

        inclination_3d_fig = inclination_3d_view(pitch_deg, roll_deg)

        gauge_fig = inclination_gauge(pitch_deg, roll_deg)

        # =====================================================
        # TEXT OUTPUT
        # =====================================================

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
     {gravity_sensor[2]: .6f}]


    Ideal Earth Rotation Vector in Sensor Frame
    -------------------------------------------
    [{omega_sensor[0]: .10f},
     {omega_sensor[1]: .10f},
     {omega_sensor[2]: .10f}] rad/sec
    """

        return (
            latitude_fig,
            azimuth_fig,
            compass_fig,
            inclination_3d_fig,
            gauge_fig,
            text,
        )
