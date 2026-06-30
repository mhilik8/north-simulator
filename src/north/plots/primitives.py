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


def find_by_name(fig_sequence, name: str):
    """
    Locate a Plotly graph object by its ``name`` field.

    Scans a sequence of Plotly graph objects and returns the first element
    whose ``name`` matches ``name``. This is the locate-by-name step that
    Plotly performs internally for its selector-based updates
    (``update_traces``, ``update_annotations``, ``update_layout_images``),
    reproduced here so the same mechanism is available for collections Plotly
    exposes no selector for — most importantly ``fig.layout.scene.annotations``,
    the home of 3D labels, which has no ``update_scene_annotations`` counterpart.

    Together with a unique ``name_id`` per primitive, this lets every
    primitive — 2D or 3D, trace-backed or annotation-backed — locate the
    Plotly objects it owns through one uniform mechanism.

    Parameters
    ----------
    fig_sequence : iterable of plotly graph objects
        Any collection of graph objects carrying a ``name`` field, e.g.
        ``fig.data``, ``fig.layout.annotations``,
        ``fig.layout.scene.annotations`` or ``fig.layout.images``.
    name : str
        The ``name_id`` to match. Assumed to identify exactly one object
        (see Notes).

    Returns
    -------
    plotly graph object
        The live object held by the figure — not a copy. Mutating its
        attributes in place mutates the figure, which is the intended use.

    Raises
    ------
    ValueError
        If no element carries the requested name. A missing name is treated
        as a programming error rather than an absence: in a correct program
        every ``name_id`` resolves, so failing loudly surfaces the bug at its
        origin instead of letting a silent no-op propagate downstream.

    Notes
    -----
    The returned reference is live and must not be retained. The object is a
    pointer into the figure; mutate it immediately as a local and let it go.
    Do not store it on ``self`` or otherwise hold it across draws. Plotly's
    annotation collections are tuples, so appending an annotation rebuilds the
    whole tuple and constructs fresh objects, orphaning any reference held from
    before: mutations to the orphan then silently fail to reach the figure.
    (Trace references happen to survive appends, but the rule is kept uniform —
    never retain — so one discipline covers every object type.) The safe shape
    is always::

        obj = find_by_name(seq, name)   # find fresh, each update
        obj.x = ...                     # mutate in place
                                        # discard; never `self.obj = ...`

    Uniqueness is assumed, not enforced. The first match is returned and the
    scan stops; duplicate names are not detected here. Uniqueness of
    ``name_id`` is upheld where names are assigned, on the principle that a
    duplicate is best prevented at its source rather than caught after it has
    already mislabeled an object. Should that contract ever break, this
    function returns the first of the collision — by design, not by accident.
    """
    for g_obj in fig_sequence:
        if g_obj.name == name:
            return g_obj
    raise ValueError(f"No such name found: {name}")


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
        *,
        shaft_width=6,
        head_scale=0.18,
        text_scale=1.12,
        **kwargs,
    ):
        super().__init__(name_id, **kwargs)

        if origin is None:
            origin = self.DEFAULT_ORIGIN.copy()

        self.origin = np.asarray(origin, dtype=float)
        self.vector = np.asarray(vector, dtype=float)
        self.label = label
        self.color = color
        self.shaft_width = shaft_width
        self.head_scale = head_scale
        self.text_scale = text_scale

    # ------------------------------------------------------------------
    # Derived geometry
    # ------------------------------------------------------------------

    @property
    def endpoint(self):
        return self.origin + self.vector

    @property
    def norm(self):
        return np.linalg.norm(self.vector)

    @property
    def cone_length(self):
        return self.head_scale * self.norm

    @property
    def shaft_end(self):
        return self.endpoint - self.cone_length * self.vector / self.norm

    @property
    def text_location(self):
        return self.origin + self.text_scale * self.vector

    @property
    def label_text(self) -> str:
        return rf"${self.label}$" if "\\" in self.label else self.label

    # ------------------------------------------------------------------
    # Name IDs
    # ------------------------------------------------------------------

    @property
    def shaft_name_id(self) -> str:
        return f"{self.name_id}_shaft"

    @property
    def cone_name_id(self) -> str:
        return f"{self.name_id}_cone"

    @property
    def label_name_id(self) -> str:
        return f"{self.name_id}_label"

    # ------------------------------------------------------------------
    # Draw / Update
    # ------------------------------------------------------------------

    def _validate(self):
        if self.norm == 0:
            raise ValueError(f"Arrow3D '{self.name_id}': zero-length vector cannot be drawn.")

    def draw(self, fig: go.Figure) -> None:
        self._validate()

        # Arrow shaft
        fig.add_trace(go.Scatter3d(
            name=self.shaft_name_id,
            x=[self.origin[0], self.shaft_end[0]],
            y=[self.origin[1], self.shaft_end[1]],
            z=[self.origin[2], self.shaft_end[2]],
            mode="lines",
            line=dict(color=self.color, width=self.shaft_width),
            showlegend=False,
            hoverinfo="skip",
        ))

        # Arrow head (cone)
        fig.add_trace(go.Cone(
            name=self.cone_name_id,
            x=[self.shaft_end[0]],
            y=[self.shaft_end[1]],
            z=[self.shaft_end[2]],
            u=[self.vector[0]],
            v=[self.vector[1]],
            w=[self.vector[2]],
            sizemode="absolute",
            sizeref=self.cone_length,
            colorscale=[[0, self.color], [1, self.color]],
            showscale=False,
            hoverinfo="skip",
        ))

        # Label — 3D annotations live in fig.layout.scene.annotations
        # and have no selector support, so we manage them by name manually.
        annotations = list(fig.layout.scene.annotations)
        annotations.append(dict(
            name=self.label_name_id,
            x=self.text_location[0],
            y=self.text_location[1],
            z=self.text_location[2],
            text=self.label_text,
            showarrow=False,
            font=dict(color=self.color, size=18, family="Noto Sans Math"),
        ))
        fig.update_layout(scene=dict(annotations=annotations))

    def update(self, fig: go.Figure, new_vector=None, new_origin=None) -> None:
        if new_vector is not None:
            self.vector = np.asarray(new_vector, dtype=float)
        if new_origin is not None:
            self.origin = np.asarray(new_origin, dtype=float)

        self._validate()

        # Traces support selector-based update
        fig.update_traces(
            selector=dict(name=self.shaft_name_id),
            x=[self.origin[0], self.shaft_end[0]],
            y=[self.origin[1], self.shaft_end[1]],
            z=[self.origin[2], self.shaft_end[2]],
        )
        fig.update_traces(
            selector=dict(name=self.cone_name_id),
            x=[self.shaft_end[0]],
            y=[self.shaft_end[1]],
            z=[self.shaft_end[2]],
            u=[self.vector[0]],
            v=[self.vector[1]],
            w=[self.vector[2]],
            sizeref=self.cone_length,
        )

        # Annotations must be rebuilt — replace the matching entry by name
        annotations = [
            dict(
                name=self.label_name_id,
                x=self.text_location[0],
                y=self.text_location[1],
                z=self.text_location[2],
                text=self.label_text,
                showarrow=False,
                font=dict(color=self.color, size=18, family="Noto Sans Math"),
            ) if ann.name == self.label_name_id else ann
            for ann in fig.layout.scene.annotations
        ]
        fig.update_layout(scene=dict(annotations=annotations))

        current_label = find_by_name(fig.layout.scene.annotations, self.label_name_id)
        current_label.x, current_label.y, current_label.z = self.text_location

    @classmethod
    def add_arrow(cls, fig: go.Figure, name, vector, label, color, origin=None) -> "Arrow3D":
        new_arrow = cls(name, vector, label, color, origin)
        new_arrow.draw(fig)
        return new_arrow


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
