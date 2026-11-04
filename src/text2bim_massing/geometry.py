"""Validation around Maslov's unchanged ring conversion methods. All lengths are metres."""

from collections.abc import Sequence
from math import isfinite
from numbers import Real
from typing import TypedDict

from shapely.geometry import MultiPolygon, Polygon

from ._vendor.maslov.polygons_to_shapely_converter import PolygonsToShapelyConverter
from ._vendor.maslov.shapely_to_polygons_converter import ShapelyToPolygonsConverter

Polygons = list[list[list[float]]]


class Extrusion(TypedDict):
    polygons: Polygons
    bottom_elevation: float
    top_elevation: float


class GeometryError(ValueError):
    """An operation would create invalid massing geometry."""


def finite_number(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise GeometryError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as error:
        raise GeometryError(f"{name} must be a finite number") from error
    if not isfinite(result):
        raise GeometryError(f"{name} must be a finite number")
    return result


def _sequence(value, name):
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise GeometryError(f"{name} must be a sequence")
    return value


def geometry_from_polygons(polygons: Polygons) -> Polygon | MultiPolygon:
    """Use Maslov's flat-ring semantics: containment subtracts, other rings unite."""
    rings = []
    for ring in _sequence(polygons, "polygons"):
        points = []
        for point in _sequence(ring, "ring"):
            _sequence(point, "point")
            if len(point) != 2:
                raise GeometryError("Every point must have exactly two coordinates")
            points.append((finite_number(point[0], "x"), finite_number(point[1], "y")))
        if points and points[0] == points[-1]:
            points.pop()
        if len(set(points)) < 3:
            raise GeometryError("A ring must have at least three distinct vertices")
        polygon = Polygon(points)
        if polygon.is_empty or not polygon.is_valid or polygon.area <= 0:
            raise GeometryError("Rings must be valid, nonzero-area polygons")
        rings.append(points)
    if not rings:
        raise GeometryError("At least one ring is required")
    geometry = PolygonsToShapelyConverter()(polygons=rings)
    if (
        not isinstance(geometry, (Polygon, MultiPolygon))
        or geometry.is_empty
        or not geometry.is_valid
        or not isfinite(geometry.area)
        or geometry.area <= 0
    ):
        raise GeometryError("The rings do not form valid polygon geometry")
    return geometry


def polygons_from_geometry(geometry: Polygon | MultiPolygon) -> Polygons:
    # GEOS overlays may rotate ring start vertices. Canonicalize once so repeated
    # validation/export does not change an otherwise identical snapshot's representation.
    geometry = geometry.normalize()
    rings = ShapelyToPolygonsConverter()(polygons=geometry)
    # A component may sit inside another component's hole. Maslov's sequential
    # converter must see each containing ring before its descendants; GEOS part
    # order does not guarantee that. Area orders containment, coordinates break ties.
    rings.sort(key=lambda ring: (-Polygon(ring).area, tuple(ring)))
    polygons = [[[float(x), float(y)] for x, y in ring] for ring in rings]
    restored = geometry_from_polygons(polygons)
    if not restored.equals(geometry):
        raise GeometryError("The geometry cannot be represented by Maslov's flat rings")
    return polygons


def normalize_polygons(polygons: Polygons) -> Polygons:
    return polygons_from_geometry(geometry_from_polygons(polygons))


def normalize_extrusion(polygons, bottom_elevation, top_elevation) -> Extrusion:
    bottom = finite_number(bottom_elevation, "bottom_elevation")
    top = finite_number(top_elevation, "top_elevation")
    if top <= bottom:
        raise GeometryError("top_elevation must be greater than bottom_elevation")
    return {
        "polygons": normalize_polygons(polygons),
        "bottom_elevation": bottom,
        "top_elevation": top,
    }


def normalize_massing(massing: list[Extrusion]) -> list[Extrusion]:
    result = []
    for extrusion in _sequence(massing, "massing"):
        if not isinstance(extrusion, dict):
            raise GeometryError("Each extrusion must be a dictionary")
        try:
            result.append(
                normalize_extrusion(
                    extrusion["polygons"], extrusion["bottom_elevation"], extrusion["top_elevation"]
                )
            )
        except KeyError as error:
            raise GeometryError(f"Missing extrusion field: {error.args[0]}") from error
    return result
