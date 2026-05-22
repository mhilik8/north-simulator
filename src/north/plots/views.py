"""
=====
Views
=====

:Author: Reuven Mol

an abstract class of view to wrap up plotly figure
"""

from abc import ABC, abstractmethod

from north.core.quaternions import Quaternion
from north.plots.graphics_utils import (
    load_image, add_arrow, rotated_image_uri, add_arrow_3d, load_aircraft_mesh)
from north.plots.theme import (
    GRAVITY_COLOR, EARTH_ROTATION_COLOR,
    GRAVITY_LABEL, EARTH_ROTATION_LABEL,
    LOCAL_LEVEL_COLOR, HIGHLIGHT_COLOR,
    EARTH_COLOR, CARD_COLOR,
    ZERO_ENCODER_COLOR, SENSOR_COLOR,
    ENCODER_COLOR, BACKGROUND_COLOR
)

import numpy as np
import plotly.graph_objects as go


EARTH_IMAGE = load_image('earth-latitude-longitude-diagram-vector-illustration.jpg')

COMPASS_ROSE = load_image('compass-rose.png')

COMPASS_ROSE_PATH = "compass-rose.png"

AIRCRAFT_TOP_PATH = "airplane-top-view.png"


class View(ABC):
    """
    Base class for all scene views.

    A View owns:
    - one Plotly figure
    - graphical primitives
    - update logic
    """

    def __init__(self):
        self.figure = go.Figure()

    @abstractmethod
    def update(self, *args) -> None:
        raise NotImplementedError


class LatitudeView(View):

    def __init__(self, p, g, omega, latitude):
        super().__init__()

        self.p = p
        self.figure.add_layout_image(
            dict(
                source=EARTH_IMAGE,
                xref="x",
                yref="y",
                x=-1.3,
                y=1.22,
                sizex=2.6,
                sizey=2.6,
                sizing="stretch",
                opacity=0.25,
                layer="below"
            )
        )

        self.gravity_arrow, self.gravity_label = add_arrow(
            self.figure,
            vec=g,
            name=GRAVITY_LABEL,
            color=GRAVITY_COLOR,
            start=p
        )

        self.rotation_arrow, self.rotation_label = add_arrow(
            self.figure,
            vec=omega,
            name=EARTH_ROTATION_LABEL,
            color=EARTH_ROTATION_COLOR,
            start=p
        )

        t0 = p + self.tangent * 0.4
        t1 = p - self.tangent * 0.4

        # local level
        self.figure.add_trace(go.Scatter(
            x=[t0[0], t1[0]],
            y=[t0[1], t1[1]],
            mode="lines",
            name="Local level",
            line=dict(dash="dash", color=LOCAL_LEVEL_COLOR),
        ))

        self.local_level = self.figure.data[-1]

        self.figure.update_layout(
            title=f"Latitude view (correct geometry): {latitude:.2f}°",
            xaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis_scaleanchor="x",
            width=600,
            height=600
        )

    @property
    def tangent(self):
        return np.array([-self.p[1], self.p[0]])

    def update(self, p, g, omega, latitude) -> None:
        self.p = p
        # gravity
        self.gravity_arrow.x = p[0] + 0.4 * g[0]
        self.gravity_arrow.y = p[1] + 0.4 * g[1]
        self.gravity_arrow.ax = p[0]
        self.gravity_arrow.ay = p[1]
        self.gravity_label.x = p[0] + 1.12 * g[0]
        self.gravity_label.y = p[1] + 1.12 * g[1]

        # earth rotation axis projected in this plane (visual only)
        self.rotation_arrow.x = p[0] + 0.4 * omega[0]
        self.rotation_arrow.y = p[1] + 0.4 * omega[1]
        self.rotation_arrow.ax = p[0]
        self.rotation_arrow.ay = p[1]
        self.rotation_label.x = p[0] + 1.12 * omega[0]
        self.rotation_label.y = p[1] + 1.12 * omega[1]

        t0 = p + self.tangent * 0.4
        t1 = p - self.tangent * 0.4

        # local level
        self.local_level.x = [t0[0], t1[0]]
        self.local_level.y = [t0[1], t1[1]]

        # LAYOUT
        self.figure.update_layout(
            title=f"Latitude view (correct geometry): {latitude:.2f}°",
            xaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis=dict(range=[-1.2, 1.2], zeroline=False),
            yaxis_scaleanchor="x",
            width=600,
            height=600
        )


class AzimuthView(View):
    def __init__(self, azimuth):
        super().__init__()

        self.azimuth = azimuth

        self.figure.add_layout_image(
            dict(
                source=COMPASS_ROSE,
                xref="x",
                yref="y",
                x=-1.23,
                y=1.2,
                sizex=2.4,
                sizey=2.4,
                sizing="stretch",
                opacity=0.35,
                layer="below"
            )
        )
        rotated_aircraft = rotated_image_uri(str(AIRCRAFT_TOP_PATH), -self.azimuth)

        self.figure.add_layout_image(
            dict(
                source=rotated_aircraft,
                xref="x",
                yref="y",
                x=-1.1,
                y=1.1,
                sizex=2.2,
                sizey=2.2,
                sizing="contain",
                opacity=1.0,
                layer="above",
            )
        )
        self.rotated_aircraft = self.figure.layout.images[-1]

        north_vector_l = np.array([0.0, 1.0])  # this should move to scene plotter
        self.north_arrow, self.north_label = add_arrow(
            self.figure,
            north_vector_l,
            EARTH_ROTATION_LABEL,
            EARTH_ROTATION_COLOR
        )

        # =====================================================
        # HEADING VECTOR
        # =====================================================

        heading = np.deg2rad(self.azimuth)
        heading_vec = np.array([
            np.sin(heading),
            np.cos(heading)
        ])  # this should move to scene plotter

        self.heading_arrow, self.heading_label = add_arrow(
            self.figure,
            heading_vec,
            r'\hat{X}',
            HIGHLIGHT_COLOR
        )

        # =====================================================
        # AZIMUTH ARC
        # =====================================================

        arc_angles = np.linspace(0, heading, 150)
        arc_x = 0.55 * np.sin(arc_angles)
        arc_y = 0.55 * np.cos(arc_angles)

        self.figure.add_trace(go.Scatter(
            x=arc_x,
            y=arc_y,
            mode="lines",
            line=dict(width=4, color=HIGHLIGHT_COLOR),
            showlegend=False
        ))

        self.azimuth_arc = self.figure.data[-1]

        # =====================================================
        # HEADING LABEL
        # =====================================================

        mid_angle = heading / 2
        arc_label_x = 0.68 * np.sin(mid_angle)
        arc_label_y = 0.68 * np.cos(mid_angle)
        # TODO: change this to annotations instead of scatter
        self.figure.add_trace(go.Scatter(
            x=arc_label_x,
            y=arc_label_y,
            mode="text",
            text=[f"{self.azimuth:.1f}°"],
            textfont=dict(size=16, color=HIGHLIGHT_COLOR),
            showlegend=False
        ))

        self.azimuth_arc_label = self.figure.data[-1]

        # =====================================================
        # CENTER POINT
        # =====================================================

        self.figure.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker=dict(size=10,color="white"),
            showlegend=False
        ))

        # =====================================================
        # LAYOUT
        # =====================================================

        self.figure.update_layout(
            title=f"Azimuth World View — Heading {self.azimuth:.1f}°",
            width=600,
            height=600,
            plot_bgcolor=EARTH_COLOR,
            paper_bgcolor=CARD_COLOR,
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-1.2, 1.2], scaleanchor="x"),
            margin=dict(l=20, r=20, t=60, b=20)
        )

    def update(self, new_azimuth) -> None:
        self.azimuth = new_azimuth

        # aircraft picture
        rotated_aircraft = rotated_image_uri(str(AIRCRAFT_TOP_PATH), -self.azimuth)
        self.rotated_aircraft.source = rotated_aircraft

        # north vector
        north_vector_l = np.array([0.0, 1.0])  # this should move to scene plotter
        self.north_arrow.x = north_vector_l[0]
        self.north_arrow.y = north_vector_l[1]
        self.north_label.a = north_vector_l[0]
        self.north_label.y = north_vector_l[1]

        # heading vector
        heading = np.deg2rad(self.azimuth)
        heading_vec = np.array([
            np.sin(heading),
            np.cos(heading)
        ])  # this should move to scene plotter
        self.heading_arrow.x = heading_vec[0]
        self.heading_arrow.y = heading_vec[1]
        self.heading_label.x = heading_vec[0]
        self.heading_label.y = heading_vec[1]

        # azimuth arc
        arc_angles = np.linspace(0, heading, 150)
        arc_x = 0.55 * np.sin(arc_angles)
        arc_y = 0.55 * np.cos(arc_angles)
        self.azimuth_arc.x = arc_x
        self.azimuth_arc.y = arc_y

        # arc label
        mid_angle = heading / 2
        arc_label_x = 0.68 * np.sin(mid_angle)
        arc_label_y = 0.68 * np.cos(mid_angle)
        self.azimuth_arc_label.x = arc_label_x
        self.azimuth_arc_label.y = arc_label_y


class CompassView(View):
    def __init__(self, azimuth) -> None:
        super().__init__()
        self.azimuth = azimuth

        rotated_rose = rotated_image_uri(str(COMPASS_ROSE_PATH), self.azimuth)

        self.figure.add_layout_image(
            dict(
                source=rotated_rose,
                xref="x",
                yref="y",

                x=-1.0,
                y=1.0,

                sizex=2.0,
                sizey=2.0,

                sizing="stretch",
                opacity=0.95,
                layer="below",
            )
        )
        self.compass_rose = self.figure.layout.images[-1]

        # =====================================================
        # OUTER RING
        # =====================================================

        theta = np.linspace(0, 2 * np.pi, 400)

        self.figure.add_trace(go.Scatter(
            x=np.cos(theta),
            y=np.sin(theta),

            mode="lines",

            line=dict(
                width=5,
                color="white"
            ),

            showlegend=False
        ))

        # =====================================================
        # TICKS
        # =====================================================

        for deg in range(0, 360, 10):
            a = np.deg2rad(deg)

            r0 = 0.88
            r1 = 1.0

            width = 4 if deg % 30 == 0 else 1

            self.figure.add_trace(go.Scatter(
                x=[r0 * np.sin(a), r1 * np.sin(a)],
                y=[r0 * np.cos(a), r1 * np.cos(a)],

                mode="lines",

                line=dict(
                    width=width,
                    color="white"
                ),

                showlegend=False
            ))

        # =====================================================
        # FIXED AIRCRAFT SYMBOL
        # =====================================================

        self.figure.add_trace(go.Scatter(
            x=[-0.15, 0.0, 0.15],
            y=[-0.05, 0.15, -0.05],

            mode="lines",

            line=dict(
                width=6,
                color=HIGHLIGHT_COLOR
            ),

            showlegend=False
        ))

        # =====================================================
        # FIXED LUBBER LINE
        # =====================================================

        self.figure.add_trace(go.Scatter(
            x=[0, 0],
            y=[0.75, 1.02],

            mode="lines",

            line=dict(
                width=5,
                color="yellow"
            ),

            showlegend=False
        ))

        # =====================================================
        # DIGITAL READOUT
        # =====================================================

        self.figure.add_trace(go.Scatter(
            x=[0],
            y=[-0.55],

            mode="text",

            text=[f"{self.azimuth:05.1f}°"],

            textfont=dict(
                size=28,
                family="Courier New",
                color="white"
            ),

            showlegend=False
        ))

        self.digital_read = self.figure.data[-1]

        # =====================================================
        # LAYOUT
        # =====================================================

        self.figure.update_layout(
            title="Compass View",

            width=600,
            height=600,

            plot_bgcolor="black",
            paper_bgcolor=CARD_COLOR,

            xaxis=dict(
                visible=False,
                range=[-1.1, 1.1]
            ),

            yaxis=dict(
                visible=False,
                range=[-1.1, 1.1],
                scaleanchor="x"
            ),

            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

    def update(self, new_azimuth) -> None:
        self.azimuth = new_azimuth

        # update compass rose
        compass_rose = rotated_image_uri(str(COMPASS_ROSE_PATH), self.azimuth)
        self.compass_rose.source = compass_rose

        # update digital read
        self.digital_read.text = [f"{self.azimuth:05.1f}°"]


class Inclination3DView(View):
    def __init__(self, azimuth, pitch, roll, transformation: Quaternion) -> None:
        super().__init__()
        self.azimuth = azimuth
        self.pitch = pitch
        self.roll = roll

        self.show_body_frame = False
        self.show_ground_frame = False

        # LOCAL LEVEL PLANE
        plane_size = 1.5
        plane_vertices = np.array([
            [-plane_size, -plane_size, 0],
            [plane_size, -plane_size, 0],
            [plane_size, plane_size, 0],
            [-plane_size, plane_size, 0],
        ])

        self.figure.add_trace(go.Mesh3d(
            x=plane_vertices[:, 0],
            y=plane_vertices[:, 1],
            z=plane_vertices[:, 2],

            i=[0, 0],
            j=[1, 2],
            k=[2, 3],

            opacity=0.35,
            color=LOCAL_LEVEL_COLOR,
            showscale=False,
            name="local level"
        ))
        # TODO: i want to attached the compass rose on top of this plain
        #  this figure lives in g frame so this should be similar to the compass view

        # =========================================================
        # AIRCRAFT
        # =========================================================

        # load aircraft model
        vertices, faces, colors = load_aircraft_mesh()
        # TODO: load_aircraft_mesh uses cache, but none the less,
        #  these should be attribute of this class

        # ROTATE MODEL
        rotated = np.array([transformation.rotate(v) for v in vertices])

        self.figure.add_trace(go.Mesh3d(
            x=rotated[:, 0],
            y=rotated[:, 1],
            z=rotated[:, 2],

            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],

            opacity=1.0,
            vertexcolor=colors,
            flatshading=True,
            name="aircraft"
        ))

        self.aircraft_3d_mesh = self.figure.data[-1]

        # =========================================================
        # GRAVITY VECTOR
        # =========================================================

        # unit vectors
        x_hat = np.array([1, 0, 0])
        y_hat = np.array([0, -1, 0])
        z_hat = np.array([0, 0, -1])
        # TODO: these are simply the plotly <-> navigation conversation

        gravity_vec = z_hat
        add_arrow_3d(self.figure, gravity_vec, GRAVITY_LABEL, GRAVITY_COLOR)
        add_arrow_3d(self.figure, x_hat, r"\hat{X}^g", GRAVITY_COLOR)
        add_arrow_3d(self.figure, y_hat, r"\hat{Y}^g", GRAVITY_COLOR)

        # =========================================================
        # BODY Z AXIS
        # =========================================================

        if self.show_body_frame:
            # this code is unreachable.
            # keep it until add_arrow_3d will return pointers to the object it generates.
            body_x = transformation.rotate(x_hat)
            body_y = transformation.rotate(y_hat)
            body_z = transformation.rotate(z_hat)

            add_arrow_3d(self.figure, body_x, r"\hat{X}^b", 'black')
            add_arrow_3d(self.figure, body_y, r"\hat{Y}^b", 'black')
            add_arrow_3d(self.figure, body_z, r"\hat{Z}^b", 'black')

        # =========================================================
        # LAYOUT
        # =========================================================

        self.figure.update_layout(
            title=f"Pitch={self.pitch:.1f}°, Roll={self.roll:.1f}°",
            scene=dict(
                aspectmode="data",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                camera=dict(
                    eye=dict(
                        x=1.5,
                        y=1.5,
                        z=0.8
                    )
                )
            ),
            width=600,
            height=600,
        )

    def update(self, new_azimuth, new_pitch, new_roll, transformation: Quaternion) -> None:
        self.azimuth = new_azimuth
        self.pitch = new_pitch
        self.roll = new_roll

        # load aircraft model
        vertices, faces, colors = load_aircraft_mesh()  # remove this after became attributes

        # ROTATE MODEL
        rotated = np.array([transformation.rotate(v) for v in vertices])

        # TODO: when ill add the compass rose on the local-level plane here is where to rotate it

        # update aircraft 3D mesh
        self.aircraft_3d_mesh.x = rotated[:, 0]
        self.aircraft_3d_mesh.y = rotated[:, 1]
        self.aircraft_3d_mesh.z = rotated[:, 2]

        x_hat = np.array([1, 0, 0])
        y_hat = np.array([0, -1, 0])
        z_hat = np.array([0, 0, -1])

        if self.show_ground_frame:
            pass # TODO: toggle the l y and z visibility

        if self.show_body_frame:
            body_x = transformation.rotate(x_hat)
            body_y = transformation.rotate(y_hat)
            body_z = transformation.rotate(z_hat)

            add_arrow_3d(self.figure, body_x, r"\hat{X}^b", 'black')
            add_arrow_3d(self.figure, body_y, r"\hat{Y}^b", 'black')
            add_arrow_3d(self.figure, body_z, r"\hat{Z}^b", 'black')


class InclinationGaugeView(View):
    def __init__(self, azimuth, pitch, roll) -> None:
        super().__init__()
        self.azimuth = azimuth
        self.pitch = pitch
        self.roll = roll
        # TODO: finnish this

    def update(self, new_azimuth, new_pitch, new_roll) -> None:
        # TODO: implement this
        pass


class MotorPlainView(View):
    def __init__(self, encoder, earth_rotation_projection, gravity_projection) -> None:
        super().__init__()
        self.encoder = encoder
        self.earth_rotation_projection = earth_rotation_projection
        self.gravity_projection = gravity_projection

        # OUTER MOTOR CIRCLE
        theta = np.linspace(0, 2 * np.pi, 500)
        self.figure.add_trace(go.Scatter(
            x=np.cos(theta),
            y=np.sin(theta),
            mode="lines",
            line=dict(width=4, color="white"),
            showlegend=False
        ))

        # ZERO ENCODER AXIS
        # this vector is simply the x_b in plotly coordinates
        # TODO: use add_arrow instead
        zero_axis = np.array([1, 0])
        self.figure.add_annotation(
            x=zero_axis[0],
            y=zero_axis[1],
            ax=0,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=4,
            arrowcolor=ZERO_ENCODER_COLOR,
            text="0°",
            font=dict(size=16, color=ZERO_ENCODER_COLOR)
        )

        # SENSOR AXIS
        # this vector is simply the x_s in b projected to xy plain
        # TODO: use add_arrow instead
        sensor_axis = np.array([np.sin(np.deg2rad(encoder)), np.cos(encoder)])
        self.figure.add_annotation(
            x=0.9 * sensor_axis[0],
            y=0.9 * sensor_axis[1],
            ax=0,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=5,
            arrowcolor=SENSOR_COLOR,
            text=r"$\hat{X}^s$",
            font=dict(size=18, color=SENSOR_COLOR)
        )
        self.sensor_axis = self.figure.layout.annotations[-1]

        # SENSOR RECTANGLE
        self.rect = np.array([
            [-0.12, -0.05],
            [0.12, -0.05],
            [0.12, 0.05],
            [-0.12, 0.05],
            [-0.12, -0.05],
        ])
        # TODO: use q_b_to_s to rotate the rectangle instead
        c = np.cos(np.deg2rad(encoder))
        s = np.sin(np.deg2rad(encoder))
        R = np.array([
            [c, -s],
            [s, c]
        ])
        rect_rot = self.rect @ R
        self.figure.add_trace(go.Scatter(
            x=rect_rot[:, 0],
            y=rect_rot[:, 1],
            mode="lines",
            line=dict(width=3, color=SENSOR_COLOR),
            fill="toself",
            fillcolor="rgba(255,255,255,0.05)",
            showlegend=False
        ))
        self.sensor_rectangle = self.figure.data[-1]

        # TRUE NORTH PROJECTION
        # i assume that earth_rotation_projection is omega_b projected to xy
        # TODO: use add_arrow instead
        self.figure.add_annotation(
            x=0.8 * earth_rotation_projection[0],
            y=0.8 * earth_rotation_projection[1],
            ax=0,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=4,
            arrowcolor=EARTH_ROTATION_COLOR,
            text=EARTH_ROTATION_LABEL,
            font=dict(size=18, color=EARTH_ROTATION_COLOR)
        )
        self.earth_rotation_projection_arrow = self.figure.layout.annotations[-1]

        # GRAVITY PROJECTION
        # i assume that gravity_projection is g_b projected to xy
        # TODO: use add_arrow instead
        self.figure.add_annotation(
            x=0.7 * gravity_projection[0],
            y=0.7 * gravity_projection[1],
            ax=0,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=4,
            arrowcolor=GRAVITY_COLOR,
            text=GRAVITY_LABEL,
            font=dict(size=18, color=GRAVITY_COLOR)
        )
        self.gravity_projection_arrow = self.figure.layout.annotations[-1]

        # TODO: this is too complicated for implementation right now.
        #  resume after implement polar sine primitive
        # EARTH RATE SIGNAL
        # if show_earth_rotation_signal:
        #     signal_theta = np.linspace(0, 2 * np.pi, 2000)
        #     signal_amplitude = (
        #             np.cos(signal_theta - north_angle)
        #             * np.cos(latitude)
        #             * np.cos(pitch)
        #     )
        #     signal_r = 0.55 + 0.25 * signal_amplitude
        #     signal_x = signal_r * np.sin(signal_theta)
        #     signal_y = signal_r * np.cos(signal_theta)
        #     fig.add_trace(go.Scatter(
        #         x=signal_x,
        #         y=signal_y,
        #         mode="lines",
        #         line=dict(
        #             width=4,
        #             color=SIGNAL_COLOR
        #         ),
        #         name="earth-rate signal"
        #     ))

        # ENCODER ARC
        arc_angles = np.linspace(0, np.deg2rad(encoder), 200)
        arc_r = 0.35
        self.figure.add_trace(go.Scatter(
            x=arc_r * np.sin(arc_angles),
            y=arc_r * np.cos(arc_angles),
            mode="lines",
            line=dict(width=4, color=ENCODER_COLOR),
            showlegend=False
        ))
        self.encoder_arc = self.figure.data[-1]

        # ENCODER LABEL
        mid = encoder / 2
        self.figure.add_trace(go.Scatter(
            x=[0.45 * np.sin(mid)],
            y=[0.45 * np.cos(mid)],
            mode="text",
            text=[f"{encoder:.1f}°"],
            textfont=dict(size=16, color=ENCODER_COLOR),
            showlegend=False
        ))
        self.encoder_arc_label = self.figure.data[-1]

        # LAYOUT
        self.figure.update_layout(
            title="Motor Plane Geometry",
            width=850,
            height=850,
            plot_bgcolor=BACKGROUND_COLOR,
            paper_bgcolor=CARD_COLOR,
            xaxis=dict(
                visible=False,
                range=[-1.15, 1.15]
            ),
            yaxis=dict(
                visible=False,
                range=[-1.15, 1.15],
                scaleanchor="x"
            ),
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False
        )

    def update(self, new_encoder, new_earth_rotation_projection, new_gravity_projection) -> None:
        self.encoder = new_encoder
        self.earth_rotation_projection = new_earth_rotation_projection
        self.gravity_projection = new_gravity_projection

        encoder_rad = np.deg2rad(self.encoder)

        # update sensor axis
        sensor_axis = np.array([np.sin(encoder_rad), np.cos(encoder_rad)])
        # the sensor_axis vector could be property
        self.sensor_axis.x = sensor_axis[0]
        self.sensor_axis.y = sensor_axis[1]

        # update sensor rectangle
        # TODO: use q_b_to_s to rotate the rectangle instead
        c = np.cos(encoder_rad)
        s = np.sin(encoder_rad)
        R = np.array([
            [c, -s],
            [s, c]
        ])
        rect_rot = self.rect @ R
        self.sensor_rectangle.x = rect_rot[:, 0]
        self.sensor_rectangle.y = rect_rot[:, 1]

        # update projections
        self.earth_rotation_projection_arrow.x = new_earth_rotation_projection[0]
        self.earth_rotation_projection_arrow.y = new_earth_rotation_projection[1]
        self.gravity_projection_arrow.x = new_gravity_projection[0]
        self.gravity_projection_arrow.y = new_gravity_projection[1]

        # update encoder arc
        arc_angles = np.linspace(0, encoder_rad, 200)
        arc_r = 0.35
        self.encoder_arc.x = arc_r * np.sin(arc_angles)
        self.encoder_arc.y = arc_r * np.cos(arc_angles)

        # update arc label
        mid = encoder_rad / 2
        self.encoder_arc_label.x = 0.45 * np.sin(mid)
        self.encoder_arc_label.y = 0.45 * np.cos(mid)

        # LAYOUT
        self.figure.update_layout(
            title="Motor Plane Geometry",
            width=850,
            height=850,
            plot_bgcolor=BACKGROUND_COLOR,
            paper_bgcolor=CARD_COLOR,
            xaxis=dict(
                visible=False,
                range=[-1.15, 1.15]
            ),
            yaxis=dict(
                visible=False,
                range=[-1.15, 1.15],
                scaleanchor="x"
            ),
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False
        )


class SO3SphereView(View):
    def __init__(self, *args) -> None:
        super().__init__()

    def update(self, *args) -> None:
        pass
