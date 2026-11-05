"""A headless scene with stable IDs and atomic geometry operations."""

import json
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from uuid import uuid4

from shapely import affinity

from .geometry import (
    GeometryError,
    finite_number,
    geometry_from_polygons,
    normalize_extrusion,
    normalize_massing,
    normalize_polygons,
    polygons_from_geometry,
)


@dataclass(frozen=True)
class SceneSnapshot:
    """Immutable serialized state; readers always receive independent dictionaries."""

    json: str

    def to_dict(self) -> dict:
        return json.loads(self.json)

    def to_massing(self) -> list[dict]:
        return [
            {key: obj[key] for key in ("polygons", "bottom_elevation", "top_elevation")}
            for obj in self.to_dict()["objects"]
            if obj["kind"] == "extrusion"
        ]


class Scene:
    """Coordinates and elevations are in metres; polygon profiles are independent objects."""

    def __init__(self):
        self._objects: dict[str, dict] = {}
        self._revision = 0

    @contextmanager
    def transaction(self):
        """Roll back the entire block, including deletions and revision, on failure."""
        before, revision = deepcopy(self._objects), self._revision
        try:
            yield self
        except BaseException:
            self._objects, self._revision = before, revision
            raise

    def snapshot(self) -> SceneSnapshot:
        return SceneSnapshot(
            json.dumps(
                {"units": "m", "revision": self._revision, "objects": list(self._objects.values())},
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

    def get(self, object_id: str) -> dict:
        try:
            return deepcopy(self._objects[object_id])
        except (KeyError, TypeError) as error:
            raise KeyError(f"Unknown scene object: {object_id}") from error

    def _ids(self, object_ids) -> list[str]:
        ids = [object_ids] if isinstance(object_ids, str) else list(object_ids)
        if not ids:
            raise ValueError("At least one object ID is required")
        for object_id in ids:
            self.get(object_id)
        return list(dict.fromkeys(ids))

    def _add(self, kind: str, data: dict) -> str:
        object_id = self._allocate_id()
        self._objects[object_id] = {"id": object_id, "kind": kind, **deepcopy(data)}
        self._revision += 1
        return object_id

    def _allocate_id(self):
        return uuid4().hex

    def create_polygon(self, polygons) -> str:
        return self._add("polygon", {"polygons": normalize_polygons(polygons)})

    def create_extrusion(self, profile, bottom_elevation: float, top_elevation: float) -> str:
        """Capture a profile's current geometry; later profile edits do not change the solid."""
        polygons = self.get(profile)["polygons"] if isinstance(profile, str) else profile
        return self._add(
            "extrusion", normalize_extrusion(polygons, bottom_elevation, top_elevation)
        )

    def set_polygon(self, object_id: str, polygons) -> str:
        obj = self.get(object_id)
        if obj["kind"] != "polygon":
            raise ValueError("set_polygon requires a polygon profile")
        obj["polygons"] = normalize_polygons(polygons)
        self._objects[object_id] = obj
        self._revision += 1
        return object_id

    def set_extrusion(
        self, object_id: str, *, polygons=None, bottom_elevation=None, top_elevation=None
    ) -> str:
        obj = self.get(object_id)
        if obj["kind"] != "extrusion":
            raise ValueError("set_extrusion requires an extrusion")
        data = normalize_extrusion(
            obj["polygons"] if polygons is None else polygons,
            obj["bottom_elevation"] if bottom_elevation is None else bottom_elevation,
            obj["top_elevation"] if top_elevation is None else top_elevation,
        )
        self._objects[object_id] = {**obj, **data}
        self._revision += 1
        return object_id

    def move(self, object_ids, x: float = 0, y: float = 0, z: float = 0) -> list[str]:
        ids = self._ids(object_ids)
        x, y, z = (finite_number(v, name) for v, name in ((x, "x"), (y, "y"), (z, "z")))
        with self.transaction():
            for object_id in ids:
                obj = self.get(object_id)
                if obj["kind"] == "polygon" and z != 0:
                    raise GeometryError("A 2D profile cannot move vertically")
                geometry = affinity.translate(
                    geometry_from_polygons(obj["polygons"]), xoff=x, yoff=y
                )
                polygons = polygons_from_geometry(geometry)
                if obj["kind"] == "extrusion":
                    obj.update(
                        normalize_extrusion(
                            polygons, obj["bottom_elevation"] + z, obj["top_elevation"] + z
                        )
                    )
                else:
                    obj["polygons"] = polygons
                self._objects[object_id] = obj
            self._revision += 1
        return ids

    def rotate(self, object_ids, angle: float, center=None) -> list[str]:
        ids = self._ids(object_ids)
        angle = finite_number(angle, "angle")
        if center is not None:
            if len(center) != 2:
                raise GeometryError("Rotation center must have two coordinates")
            center = tuple(finite_number(value, "center") for value in center)
        with self.transaction():
            for object_id in ids:
                obj = self.get(object_id)
                geometry = affinity.rotate(
                    geometry_from_polygons(obj["polygons"]),
                    angle,
                    origin="center" if center is None else center,
                )
                obj["polygons"] = polygons_from_geometry(geometry)
                self._objects[object_id] = obj
            self._revision += 1
        return ids

    def duplicate(self, object_ids, n: int = 1) -> list[str]:
        ids = self._ids(object_ids)
        if isinstance(n, bool) or not isinstance(n, int) or n < 1:
            raise ValueError("n must be a positive integer")
        copies = []
        with self.transaction():
            for object_id in ids:
                obj = self.get(object_id)
                for _ in range(n):
                    copies.append(
                        self._add(
                            obj["kind"],
                            {key: value for key, value in obj.items() if key not in {"id", "kind"}},
                        )
                    )
        return copies

    def delete(self, object_ids) -> None:
        ids = self._ids(object_ids)
        for object_id in ids:
            del self._objects[object_id]
        self._revision += 1

    def to_massing(self) -> list[dict]:
        return self.snapshot().to_massing()

    @classmethod
    def from_snapshot(cls, snapshot: SceneSnapshot) -> "Scene":
        data = snapshot.to_dict()
        if data.get("units") != "m":
            raise ValueError("Scene snapshots must use metres")
        revision = data["revision"]
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
            raise ValueError("Invalid snapshot revision")
        scene = cls()
        for obj in data["objects"]:
            object_id, kind = obj["id"], obj["kind"]
            if not isinstance(object_id, str) or not object_id or object_id in scene._objects:
                raise ValueError("Snapshot IDs must be unique nonempty strings")
            if kind == "polygon":
                values = {"polygons": normalize_polygons(obj["polygons"])}
            elif kind == "extrusion":
                values = normalize_extrusion(
                    obj["polygons"], obj["bottom_elevation"], obj["top_elevation"]
                )
            else:
                raise ValueError(f"Unknown snapshot object kind: {kind}")
            scene._objects[object_id] = {"id": object_id, "kind": kind, **values}
        scene._revision = revision
        return scene

    @classmethod
    def from_massing(cls, massing) -> "Scene":
        scene = cls()
        for extrusion in normalize_massing(massing):
            scene._add("extrusion", extrusion)
        return scene
