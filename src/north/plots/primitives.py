"""
==========
Primitives
==========

:Author: Reuven Mol

plotly primitive to ease the view workload
"""

from abc import ABC, abstractmethod
import numpy as np
import plotly.graph_objects as go


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


class Arc(Primitive2d):

    DEFAULT_START = np.array([0, 1])

    def __init__(self, end, label, color, start, radius=0.3):
        if start is None:
            start = self.DEFAULT_START.copy()
        self.start = start
        self.end = end
        self.label = label
        self.color = color
        self.radius = radius
        self.plotly_arc = None
        self.plotly_label = None

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

    def draw(self, fig) -> None:
        # Draw Arc
        arc = self.arc
        fig.add_trace(go.Scatter(
            x=arc[0],
            y=arc[1],
            mode="lines",
            line=dict(width=4, color=self.color),
            showlegend=False
        ))
        self.plotly_arc = fig.data[-1]

        # Draw Label
        fig.add_annotation(
            x=self.text_location[0],
            y=self.text_location[1],
            text=self.label,
            showarrow=False,
            font=dict(color=self.color, family="Noto Sans Math", size=18),
            xanchor="center",
            yanchor="middle",
        )
        self.plotly_label = fig.layout.annotations[-1]

    def update(self, new_start=None, new_end=None, new_label="") -> None:
        if new_start is not None:
            self.start = new_start
        if new_end is not None:
            self.end = new_end
        if new_label:
            self.label = new_label
        # update arc
        arc = self.arc
        self.plotly_arc.x = arc[0]
        self.plotly_arc.y = arc[1]
        # update label position
        label_position = self.text_location
        self.plotly_label.x = label_position[0]
        self.plotly_label.y = label_position[1]
        if new_label:
            self.plotly_label.text = self.label

    @classmethod
    def add_arc(cls, fig, end, label, color, start=None, radius=0.3):
        new_arc = cls(end, label, color, start, radius)
        new_arc.draw(fig)
        return new_arc