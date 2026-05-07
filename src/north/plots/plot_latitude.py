from pathlib import Path
import numpy as np
import plotly.graph_objects as go
import base64

# =========================================================
# LOAD LOCAL EARTH IMAGE
# =========================================================


with open(Path(__file__).parent / Path('pictures/earth-latitude-longitude-diagram-vector-illustration.jpg'), "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

img_src = "data:image/jpeg;base64," + encoded


def latitude_view(latitude_deg: float):
    lat = np.deg2rad(latitude_deg)

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=img_src,
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

    # =========================================================
    # SURFACE POINT (IMPORTANT FIX)
    # =========================================================
    p = np.array([np.cos(lat), np.sin(lat)])  # point on Earth

    # =========================================================
    # Ω VECTOR (constant, north pole direction)
    # =========================================================
    omega = np.array([0.0, 1.0])

    # =========================================================
    # GRAVITY VECTOR (toward Earth center, from surface point)
    # =========================================================
    g = -p  # radial inward

    # =========================================================
    # LOCAL HORIZONTAL (tangent direction)
    # =========================================================
    tangent = np.array([-p[1], p[0]])

    # =========================================================
    # ARROW HELPER (annotations)
    # =========================================================
    def add_arrow(start, vec, name, color):
        end = start + vec

        fig.add_annotation(
            x=end[0],
            y=end[1],
            ax=start[0],
            ay=start[1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.3,
            arrowwidth=3,
            arrowcolor=color,
            text="",
        )

        # label at arrow head
        fig.add_trace(go.Scatter(
            x=[end[0]],
            y=[end[1]],
            mode="text",
            text=[name],
            textposition="top center",
            textfont=dict(color=color, size=16),
            showlegend=False
        ))

    # =========================================================
    # DRAW VECTORS (ALL START AT SURFACE POINT)
    # =========================================================

    # gravity
    add_arrow(p, 0.4 * g, "g", "red")

    # earth rotation axis projected in this plane (visual only)
    add_arrow(p, 0.4 * omega, "Ω", "blue")

    t0 = p + tangent * 0.4
    t1 = p - tangent * 0.4

    # local level
    fig.add_trace(go.Scatter(
        x=[t0[0], t1[0]],
        y=[t0[1], t1[1]],
        mode="lines",
        name="Local level",
        line=dict(dash="dash")
    ))

    # =========================================================
    # LAYOUT
    # =========================================================
    fig.update_layout(
        title=f"Latitude view (correct geometry): {latitude_deg:.2f}°",
        xaxis=dict(range=[-1.2, 1.2], zeroline=False),
        yaxis=dict(range=[-1.2, 1.2], zeroline=False),
        yaxis_scaleanchor="x",
        width=700,
        height=700
    )

    return fig