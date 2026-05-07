from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from functools import cache
import trimesh


model_path = Path(__file__).parent / Path("pictures/11803_Airplane_v1_l1/11803_Airplane_v1_l1.obj")

SKY = "rgb(110,140,180)"
EARTH = "rgb(120,90,70)"

@cache
def load_aircraft_mesh(model_path: str = str(model_path)) -> trimesh.Trimesh:

    mesh_or_scene = trimesh.load(model_path)

    if isinstance(mesh_or_scene, trimesh.Scene):

        mesh = trimesh.util.concatenate(
            tuple(
                geometry
                for geometry in mesh_or_scene.geometry.values()
            )
        )

    else:
        mesh = mesh_or_scene

    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)

    # =========================================================
    # CENTER MODEL
    # =========================================================

    center = vertices.mean(axis=0)
    vertices = vertices - center

    # =========================================================
    # NORMALIZE MODEL SIZE
    # =========================================================

    extent = vertices.max(axis=0) - vertices.min(axis=0)
    scale = np.max(extent)

    vertices = vertices / scale

    return vertices, faces


def Rx(theta):
    c = np.cos(theta)

def Rx(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])


def Ry(theta):
    c = np.cos(theta)
    s = np.sin(theta)

    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])


def inclination_3d_view(
    pitch_deg: float,
    roll_deg: float,
) -> go.Figure:

    pitch = np.deg2rad(pitch_deg)
    roll = np.deg2rad(roll_deg)

    # =========================================================
    # LOAD AIRCRAFT MODEL
    # =========================================================

    vertices, faces = load_aircraft_mesh()

    # =========================================================
    # ROTATE MODEL
    # =========================================================

    R = Rx(roll) @ Ry(-pitch)

    rotated = (R @ vertices.T).T

    x = rotated[:, 0]
    y = rotated[:, 1]
    z = rotated[:, 2]

    # =========================================================
    # BUILD FIGURE
    # =========================================================

    fig = go.Figure()

    # =========================================================
    # LOCAL LEVEL PLANE
    # =========================================================

    plane_size = 1.5

    plane_vertices = np.array([
        [-plane_size, -plane_size, 0],
        [plane_size, -plane_size, 0],
        [plane_size, plane_size, 0],
        [-plane_size, plane_size, 0],
    ])

    fig.add_trace(go.Mesh3d(
        x=plane_vertices[:, 0],
        y=plane_vertices[:, 1],
        z=plane_vertices[:, 2],

        i=[0, 0],
        j=[1, 2],
        k=[2, 3],

        opacity=0.35,
        color="lightblue",
        showscale=False,
        name="local level"
    ))

    # =========================================================
    # AIRCRAFT
    # =========================================================

    fig.add_trace(go.Mesh3d(
        x=rotated[:, 0],
        y=rotated[:, 1],
        z=rotated[:, 2],

        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],

        opacity=1.0,
        flatshading=True,
        name="aircraft"
    ))

    # =========================================================
    # GRAVITY VECTOR
    # =========================================================

    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0, -1],
        mode="lines",
        line=dict(width=8),
        name="gravity"
    ))

    # =========================================================
    # BODY Z AXIS
    # =========================================================

    body_z = R @ np.array([0, 0, -1])

    fig.add_trace(go.Scatter3d(
        x=[0, body_z[0]],
        y=[0, body_z[1]],
        z=[0, body_z[2]],
        mode="lines",
        line=dict(width=8),
        name="body z"
    ))

    # =========================================================
    # LAYOUT
    # =========================================================

    fig.update_layout(
        title=f"Pitch={pitch_deg:.1f}°, Roll={roll_deg:.1f}°",
        scene=dict(
            aspectmode="data",

            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            ),
            zaxis=dict(
                visible=False
            ),

            camera=dict(
                eye=dict(
                    x=1.5,
                    y=1.5,
                    z=0.8
                )
            )
        ),

        width=900,
        height=700,
        showlegend=True
    )

    return fig


def inclination_gauge(
    pitch_deg: float,
    roll_deg: float
) -> go.Figure:
    """
    Artificial attitude indicator / inclination gauge.

    Parameters
    ----------
    pitch_deg : float
        Aircraft pitch angle in degrees.

        Positive pitch raises the nose.

    roll_deg : float
        Aircraft roll angle in degrees.

        Positive roll banks right wing down.

    Returns
    -------
    go.Figure
        Interactive Plotly figure.
    """

    pitch = np.deg2rad(pitch_deg)
    roll = np.deg2rad(roll_deg)

    fig = go.Figure()

    # =========================================================
    # GAUGE GEOMETRY
    # =========================================================

    radius = 1.0

    # how much horizon moves vertically with pitch
    pitch_scale = 0.015

    horizon_y = -pitch_deg * pitch_scale

    # =========================================================
    # ROTATION MATRIX
    # =========================================================

    c = np.cos(-roll)
    s = np.sin(-roll)

    R = np.array([
        [c, -s],
        [s,  c]
    ])

    # =========================================================
    # HORIZON LINE
    # =========================================================

    xh = np.linspace(-2, 2, 200)
    yh = np.zeros_like(xh) + horizon_y

    horizon = np.vstack([xh, yh])

    horizon_rot = R @ horizon

    # =========================================================
    # SKY POLYGON
    # =========================================================

    sky_x = np.concatenate([
        [-3],
        horizon_rot[0],
        [3],
        [3],
        [-3]
    ])

    sky_y = np.concatenate([
        [3],
        horizon_rot[1],
        [3],
        [3],
        [3]
    ])

    fig.add_trace(go.Scatter(
        x=sky_x,
        y=sky_y,
        fill="toself",
        mode="lines",
        line=dict(width=0),
        fillcolor=SKY,
        showlegend=False
    ))

    # =========================================================
    # EARTH POLYGON
    # =========================================================

    earth_x = np.concatenate([
        [-3],
        horizon_rot[0],
        [3],
        [3],
        [-3]
    ])

    earth_y = np.concatenate([
        [-3],
        horizon_rot[1],
        [-3],
        [-3],
        [-3]
    ])

    fig.add_trace(go.Scatter(
        x=earth_x,
        y=earth_y,
        fill="toself",
        mode="lines",
        line=dict(width=0),
        fillcolor=EARTH,
        showlegend=False
    ))

    # =========================================================
    # HORIZON LINE
    # =========================================================

    fig.add_trace(go.Scatter(
        x=horizon_rot[0],
        y=horizon_rot[1],
        mode="lines",
        line=dict(width=4, color="white"),
        showlegend=False
    ))

    # =========================================================
    # PITCH LADDER
    # =========================================================

    for deg in range(-30, 31, 5):

        if deg == 0:
            continue

        y_local = horizon_y + deg * pitch_scale

        ladder = np.array([
            [-0.15, 0.15],
            [y_local, y_local]
        ])

        ladder_rot = R @ ladder

        positive = deg > 0

        fig.add_trace(go.Scatter(
            x=ladder_rot[0],
            y=ladder_rot[1],
            mode="lines",
            line=dict(
                width=3 if deg % 10 == 0 else 1,
                dash=None if positive else "dash",
                color="white"
            ),
            showlegend=False
        ))

        # =====================================================
        # LABELS
        # =====================================================

        left = R @ np.array([-0.22, y_local])
        right = R @ np.array([0.22, y_local])

        fig.add_trace(go.Scatter(
            x=[left[0], right[0]],
            y=[left[1], right[1]],
            mode="text",
            text=[str(abs(deg)), str(abs(deg))],
            textfont=dict(size=12, color="white"),
            showlegend=False
        ))

    # =========================================================
    # OUTER ROLL SCALE
    # =========================================================

    angles = np.deg2rad(np.linspace(-60, 60, 200))

    fig.add_trace(go.Scatter(
        x=0.95 * np.sin(angles + roll),
        y=0.95 * np.cos(angles + roll),
        mode="lines",
        line=dict(width=3, color="white"),
        showlegend=False
    ))

    # =========================================================
    # ROLL TICKS
    # =========================================================

    for deg in range(-60, 61, 10):

        a = np.deg2rad(deg)

        r0 = 0.88
        r1 = 0.95

        fig.add_trace(go.Scatter(
            x=[r0*np.sin(a + roll), r1*np.sin(a + roll)],
            y=[r0*np.cos(a + roll), r1*np.cos(a + roll)],
            mode="lines",
            line=dict(width=2, color="white"),
            showlegend=False
        ))

    for deg in range(-60, 61, 10):
        a = np.deg2rad(deg)

        r = 0.84

        fig.add_trace(go.Scatter(
            x=[r * np.sin(a + roll)],
            y=[r * np.cos(a + roll)],
            mode="text",
            text=[str(-deg)],
            textfont=dict(size=11, color="white"),
            showlegend=False
        ))

    # =========================================================
    # FIXED AIRCRAFT SYMBOL
    # =========================================================

    fig.add_trace(go.Scatter(
        x=[-0.18, -0.05, 0.0, 0.05, 0.18],
        y=[0.0, 0.0, -0.03, 0.0, 0.0],
        mode="lines",
        line=dict(width=5, color="yellow"),
        showlegend=False
    ))

    # =========================================================
    # FIXED TOP TRIANGLE
    # =========================================================

    fig.add_trace(go.Scatter(
        x=[0],
        y=[0.98],
        mode="markers",
        marker=dict(size=14, symbol="triangle-down", color="yellow"),
        showlegend=False
    ))

    # =========================================================
    # MASK OUTSIDE CIRCLE
    # =========================================================

    theta = np.linspace(0, 2*np.pi, 400)

    fig.add_shape(
        type="circle",
        x0=-radius,
        y0=-radius,
        x1=radius,
        y1=radius,
        line=dict(width=6, color="black")
    )

    # =========================================================
    # LAYOUT
    # =========================================================

    fig.update_layout(
        title=f"Pitch={pitch_deg:.1f}°, Roll={roll_deg:.1f}°",

        xaxis=dict(
            range=[-1.05, 1.05],
            visible=False
        ),

        yaxis=dict(
            range=[-1.05, 1.05],
            visible=False,
            scaleanchor="x"
        ),

        plot_bgcolor="black",

        width=700,
        height=700,

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig
