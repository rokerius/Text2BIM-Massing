"""Massing counterparts of Text2BIM's polygon and object tools, without story layers."""

import inspect

from .geometry import finite_number
from .scene import Scene


class MassingTools:
    """Keep Text2BIM tool names; lengths use declared units, exports always use metres."""

    def __init__(self, scene: Scene, *, units: str = "m"):
        if units not in {"m", "mm"}:
            raise ValueError("units must be 'm' or 'mm'")
        self.scene, self.units = scene, units
        self._scale = 0.001 if units == "mm" else 1.0

    def _length(self, value):
        return finite_number(value, "length") * self._scale

    def _polygons(self, polygons):
        # Shape validation belongs to geometry.py; scale only after checking each point.
        from .geometry import normalize_polygons

        return [
            [[self._length(x), self._length(y)] for x, y in ring]
            for ring in normalize_polygons(polygons)
        ]

    def create_polygon(self, vertices):
        """Create a single-ring 2D profile from [(x, y), ...]; return its stable ID."""
        return self.scene.create_polygon(self._polygons([vertices]))

    def create_profile(self, polygons):
        """Create a profile from Maslov flat rings, including holes/components; return ID."""
        return self.scene.create_polygon(self._polygons(polygons))

    def set_polygon(self, uuid, polygons):
        """Replace a profile's flat rings without changing its ID or existing extrusions."""
        return self.scene.set_polygon(uuid, self._polygons(polygons))

    def create_extrusion(self, profile_id, bottom_elevation, top_elevation):
        """Extrude a profile between bottom and top elevations; return the solid's ID."""
        return self.scene.create_extrusion(
            profile_id, self._length(bottom_elevation), self._length(top_elevation)
        )

    def set_extrusion(self, uuid, polygons=None, bottom_elevation=None, top_elevation=None):
        """Edit a solid's rings/elevations atomically; omitted fields keep their values."""
        return self.scene.set_extrusion(
            uuid,
            polygons=None if polygons is None else self._polygons(polygons),
            bottom_elevation=None if bottom_elevation is None else self._length(bottom_elevation),
            top_elevation=None if top_elevation is None else self._length(top_elevation),
        )

    def move_obj(self, uuid, xDistance=0, yDistance=0, zDistance=0):
        """Move an ID or list of IDs; 2D profiles only support x/y movement. Return None."""
        self.scene.move(
            uuid, self._length(xDistance), self._length(yDistance), self._length(zDistance)
        )

    def rotate_obj(self, uuid, angle, center=None):
        """Rotate by degrees about center or bounding-box center; return the same ID(s)."""
        center = None if center is None else [self._length(value) for value in center]
        ids = self.scene.rotate(uuid, angle, center)
        return uuid if isinstance(uuid, str) else ids

    def duplicate_obj(self, element_uuid, n=1):
        """Copy an ID or list of IDs n times; return new IDs. Originals retain their IDs."""
        return self.scene.duplicate(element_uuid, n)

    def delete_element(self, uuid):
        """Delete an ID or list of IDs atomically."""
        return self.scene.delete(uuid)

    def get_object(self, uuid):
        """Read an independent copy of an object, with lengths in the tool's units."""
        obj = self.scene.get(uuid)
        obj["polygons"] = [
            [[x / self._scale, y / self._scale] for x, y in ring] for ring in obj["polygons"]
        ]
        for key in ("bottom_elevation", "top_elevation"):
            if key in obj:
                obj[key] /= self._scale
        return obj

    def get_polygon_vertex(self, uuid, at, ring=0):
        """Read a vertex (zero-based at and ring indexes), in the tool's units."""
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (at, ring)):
            raise ValueError("Vertex and ring indexes must be nonnegative integers")
        return tuple(self.get_object(uuid)["polygons"][ring][at])

    def get_vertex_count(self, uuid, ring=0):
        """Read the vertex count of a zero-based ring."""
        if isinstance(ring, bool) or not isinstance(ring, int) or ring < 0:
            raise ValueError("Ring index must be a nonnegative integer")
        return len(self.get_object(uuid)["polygons"][ring])

    def read_scene(self):
        """Read the complete scene state with IDs; all lengths in this state are METRES."""
        return self.scene.snapshot().to_dict()

    def export_massing(self):
        """Export only extrusions in Maslov's format; all lengths are METRES."""
        return self.scene.to_massing()

    def as_functions(self) -> dict:
        names = (
            "create_polygon",
            "create_profile",
            "set_polygon",
            "create_extrusion",
            "set_extrusion",
            "move_obj",
            "rotate_obj",
            "duplicate_obj",
            "delete_element",
            "get_object",
            "get_polygon_vertex",
            "get_vertex_count",
            "read_scene",
            "export_massing",
        )
        return {name: getattr(self, name) for name in names}

    def documentation(self) -> str:
        lines = [f"Tool lengths: {self.units}. Scene/massing exports: m. Angles: degrees."]
        for name, function in self.as_functions().items():
            lines.append(f"{name}{inspect.signature(function)}: {inspect.getdoc(function)}")
        return "\n".join(lines)
