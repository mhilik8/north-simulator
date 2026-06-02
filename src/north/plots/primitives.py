"""
==========
Primitives
==========

:Author: Reuven Mol

plotly primitive to ease the view workload
"""

import io
import base64
from abc import ABC, abstractmethod
import numpy as np
from PIL import Image
import plotly.graph_objects as go
from north.plots.graphics_utils import load_image


class Primitive(ABC):

    def __init__(self, name_id, *arg, **kwarg):
        self.name_id: str = name_id

    @abstractmethod
    def update(self, fig: go.Figure, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def draw(self, fig: go.Figure) -> None:
        pass


class Primitive2d(Primitive, ABC):
    pass


class Primitive3d(Primitive, ABC):
    pass


class Arrow(Primitive2d):

    DEFAULT_ORIGIN = np.array([0, 0])

    def __init__(self, name_id, vector, label, color, origin=None, *args, **kwargs):
        super().__init__(name_id, *args, **kwargs)
        if origin is None:
            origin = self.DEFAULT_ORIGIN.copy()
        self.origin = origin
        self.vector = vector
        self.label = label
        self.color = color

    @property
    def endpoint(self):
        return self.origin + self.vector

    @property
    def text_location(self):
        return self.origin + 1.12 * self.vector

    @property
    def label_text(self) -> str:
        return rf"${self.label}$" if "\\" in self.label else self.label

    @property
    def arrow_name_id(self) -> str:
        return f'{self.name_id}_arrow'

    @property
    def label_name_id(self) -> str:
        return f'{self.name_id}_label'

    def draw(self, fig: go.Figure) -> None:
        # arrow
        fig.add_annotation(
            name=self.arrow_name_id,
            x=self.endpoint[0],
            y=self.endpoint[1],
            ax=self.origin[0],
            ay=self.origin[1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.3,
            arrowwidth=3,
            arrowcolor=self.color,
            text="",
        )

        # label
        fig.add_annotation(
            name=self.label_name_id,
            x=self.text_location[0],
            y=self.text_location[1],
            text=self.label_text,
            showarrow=False,
            font=dict(color=self.color, family="Noto Sans Math", size=18),
            xanchor="center",
            yanchor="middle",
        )

    def update(self, fig: go.Figure, new_vector = None, new_origin = None) -> None:
        if new_vector is not None:
            self.vector = new_vector
        if new_origin is not None:
            self.origin = new_origin

        # redraw later
        fig.update_annotations(
            selector=dict(name=self.arrow_name_id),
            x = self.endpoint[0],
            y = self.endpoint[1],
            ax = self.origin[0],
            ay = self.origin[1],
        )

        fig.update_annotations(
            selector=dict(name=self.label_name_id),
            x = self.text_location[0],
            y = self.text_location[1],
        )

    @classmethod
    def add_arrow(cls, fig: go.Figure, name, vector, label, color, origin=None) -> Arrow:
        new_arrow = cls(name, vector, label, color, origin)
        new_arrow.draw(fig)
        return new_arrow


class Arrow3D(Primitive3d):
    DEFAULT_ORIGIN = np.array([0, 0, 0])

    def __init__(
            self,
            name_id,
            vector,
            label,
            color,
            origin=None,
            *args,
            **kwargs
    ):
        super().__init__(name_id, *args, **kwargs)

        if origin is None:
            origin = self.DEFAULT_ORIGIN.copy()

        self.origin = origin
        self.vector = vector
        self.label = label
        self.color = color


class Arc(Primitive2d):

    DEFAULT_START = np.array([0, 1])

    def __init__(self, name_id, end, label, color, start, radius=0.3, *args, **kwargs):
        super().__init__(name_id, *args, **kwargs)
        if start is None:
            start = self.DEFAULT_START.copy()
        self.start = start
        self.end = end
        self.label = label
        self.color = color
        self.radius = radius

    @property
    def start_angle(self):
        return np.arctan2(self.start[0], self.start[1])

    @property
    def end_angle(self):
        return np.arctan2(self.end[0], self.end[1])

    @property
    def text_location(self):
        angle = (self.start_angle + self.end_angle) / 2
        return (self.radius + 0.12) * np.array([
            np.sin(angle),
            np.cos(angle),
        ])

    @property
    def arc(self):
        ten_milirad = 0.01
        angles = np.arange(self.start_angle, self.end_angle, ten_milirad)
        return self.radius * np.array([
            np.sin(angles),
            np.cos(angles),
        ])

    @property
    def arc_name_id(self) -> str:
        return f'{self.name_id}_arc'

    @property
    def label_name_id(self) -> str:
        return f'{self.name_id}_label'

    def draw(self, fig) -> None:
        # Draw Arc
        arc = self.arc
        fig.add_trace(go.Scatter(
            name=self.arc_name_id,
            x=arc[0],
            y=arc[1],
            mode="lines",
            line=dict(width=4, color=self.color),
            showlegend=False
        ))

        # Draw Label
        fig.add_annotation(
            name=self.label_name_id,
            x=self.text_location[0],
            y=self.text_location[1],
            text=self.label,
            showarrow=False,
            font=dict(color=self.color, family="Noto Sans Math", size=18),
            xanchor="center",
            yanchor="middle",
        )

    def update(self, fig: go.Figure, new_start=None, new_end=None, new_label=None) -> None:
        if new_start is not None:
            self.start = new_start
        if new_end is not None:
            self.end = new_end
        if new_label is not None:
            self.label = new_label
        # update arc
        arc = self.arc
        fig.update_traces(
            selector=dict(name=self.arc_name_id),
            x=arc[0],
            y=arc[1],
        )
        # update label position
        label_position = self.text_location
        if new_label is not None:
            fig.update_annotations(
                selector=dict(name=self.label_name_id),
                x=label_position[0],
                y=label_position[1],
                text=self.label,
            )
        else:
            fig.update_annotations(
                selector=dict(name=self.label_name_id),
                x=label_position[0],
                y=label_position[1],
            )

    @classmethod
    def add_arc(cls, fig, name, end, label, color, start=None, radius=0.3):
        new_arc = cls(name, end, label, color, start, radius)
        new_arc.draw(fig)
        return new_arc


class RotatedImage(Primitive2d):
    def __init__(self, name, image_file_name: str, angle: float, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.image = load_image(image_file_name)
        self.angle = angle

        if 'x' in kwargs:
            self.x = kwargs['x']
        else:
            self.x = -1.0

        if 'y' in kwargs:
            self.y = kwargs['y']
        else:
            self.y = 1.0

        if 'sizex' in kwargs:
            self.sizex = kwargs['sizex']
        else:
            self.sizex = 2.0

        if 'sizey' in kwargs:
            self.sizey = kwargs['sizey']
        else:
            self.sizey = 2.0

    @property
    def image_id_name(self) -> str:
        return f'{self.name_id}_image'

    @property
    def rotated_image(self):
        rotated = self.image.rotate(
            self.angle,
            expand=True,
            resample=Image.Resampling.BICUBIC
        )
        buffer = io.BytesIO()
        rotated.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded}"

    def draw(self, fig: go.Figure) -> None:
        fig.add_layout_image(dict(
            name=self.image_id_name,
            source=self.rotated_image,
            xref="x",
            yref="y",
            x=self.x,
            y=self.y,
            sizex=self.sizex,
            sizey=self.sizey,
            sizing="contain",
            opacity=1.0,
            layer="above",
        ))

    def update(self, fig: go.Figure, new_angle) -> None:
        if np.isclose(new_angle, self.angle):
            return
        self.angle = new_angle
        fig.update_layout_images(
            selector=dict(name=self.image_id_name),
            source=self.rotated_image,
        )
