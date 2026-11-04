import json
from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from text2bim_massing import Scene
from text2bim_massing.geometry import GeometryError, geometry_from_polygons, normalize_polygons


def test_holes_components_roundtrip_and_units(rings):
    scene = Scene()
    profile = scene.create_polygon(rings)
    solid = scene.create_extrusion(profile, -2, 4)
    extrusion = scene.to_massing()[0]
    geometry = geometry_from_polygons(extrusion["polygons"])
    assert geometry.geom_type == "MultiPolygon"
    assert len(geometry.geoms) == 2
    assert sum(len(p.interiors) for p in geometry.geoms) == 1
    assert geometry.area == 112
    assert extrusion["bottom_elevation"] == -2
    assert extrusion["top_elevation"] == 4
    restored = Scene.from_massing(json.loads(json.dumps(scene.to_massing())))
    assert geometry_from_polygons(restored.to_massing()[0]["polygons"]).equals(geometry)
    # Profiles are snapshots, not live dependencies of an already created solid.
    scene.move(profile, x=100)
    assert scene.get(solid)["polygons"] == extrusion["polygons"]


@pytest.mark.parametrize(
    "polygons",
    [
        [],
        [[[0, 0], [1, 1]]],
        [[[0, 0], [1, 1], [2, 2]]],
        [[[0, 0], [2, 2], [0, 2], [2, 0]]],
        [[[0, 0], [1, 0], [1, float("nan")]]],
        [[[0, 0], [1, 0], [1, float("inf")]]],
        [[[0, 0, 0], [1, 0], [1, 1]]],
        [[[0, 0], [True, 0], [1, 1]]],
        "polygon",
    ],
)
def test_invalid_geometry_cannot_change_scene(polygons):
    scene = Scene()
    before = scene.snapshot()
    with pytest.raises(GeometryError):
        scene.create_polygon(polygons)
    assert scene.snapshot() == before


@pytest.mark.parametrize("bottom,top", [(0, 0), (2, 1), (0, float("inf")), (True, 4)])
def test_invalid_elevations_are_atomic(rings, bottom, top):
    scene = Scene()
    profile = scene.create_polygon(rings)
    before = scene.snapshot()
    with pytest.raises(GeometryError):
        scene.create_extrusion(profile, bottom, top)
    assert scene.snapshot() == before


def test_edit_rotate_move_and_copy_keep_ids(rings):
    scene = Scene()
    solid = scene.create_extrusion(rings, 0, 6)
    copies = scene.duplicate(solid, n=2)
    assert len(set([solid, *copies])) == 3
    original = scene.get(solid)
    assert scene.rotate(solid, 90, center=(0, 0)) == [solid]
    assert scene.move(solid, x=5, y=7, z=3) == [solid]
    transformed = scene.get(solid)
    assert geometry_from_polygons(transformed["polygons"]).bounds == pytest.approx((-5, 7, 5, 31))
    assert transformed["bottom_elevation"] == 3
    assert transformed["top_elevation"] == 9
    assert scene.set_extrusion(solid, top_elevation=12) == solid
    assert scene.get(copies[0])["polygons"] == original["polygons"]
    scene.delete(copies)
    assert len(scene.to_massing()) == 1
    assert scene.get(solid)["id"] == solid


def test_batch_and_outer_transaction_rollback(rings):
    scene = Scene()
    solid = scene.create_extrusion(rings, 0, 6)
    profile = scene.create_polygon(rings)
    before = scene.snapshot()
    with pytest.raises(GeometryError):
        scene.move([solid, profile], z=2)
    assert scene.snapshot() == before
    with pytest.raises(KeyError):
        scene.delete([solid, "missing"])
    assert scene.snapshot() == before
    with pytest.raises(GeometryError):
        with scene.transaction():
            scene.duplicate(solid)
            scene.delete(profile)
            scene.set_extrusion(solid, top_elevation=-1)
    assert scene.snapshot() == before


def test_state_reads_and_export_do_not_mutate_scene(rings):
    scene = Scene()
    solid = scene.create_extrusion(rings, 0, 6)
    snapshot = scene.snapshot()
    state = snapshot.to_dict()
    state["objects"][0]["polygons"].clear()
    exported = scene.to_massing()
    exported[0]["polygons"].clear()
    obj = scene.get(solid)
    obj["polygons"].clear()
    assert scene.snapshot() == snapshot
    with pytest.raises(FrozenInstanceError):
        snapshot.json = "{}"
    scene.move(solid, x=1)
    assert snapshot.to_massing() != scene.to_massing()


def test_profile_edit_closed_rings_and_invalid_update(rings):
    scene = Scene()
    profile = scene.create_polygon([rings[0] + [rings[0][0]]])
    assert len(scene.get(profile)["polygons"][0]) == 4
    assert scene.set_polygon(profile, rings) == profile
    before = scene.snapshot()
    with pytest.raises(GeometryError):
        scene.set_polygon(profile, [])
    assert scene.snapshot() == before
    with pytest.raises(ValueError):
        scene.set_extrusion(profile, top_elevation=1)
    assert scene.snapshot() == before


def test_input_geometry_is_not_retained_by_reference(rings):
    original = deepcopy(rings)
    scene = Scene()
    scene.create_extrusion(rings, 0, 3)
    rings[0][0][0] = 100
    assert geometry_from_polygons(scene.to_massing()[0]["polygons"]).equals(
        geometry_from_polygons(original)
    )


def test_normalization_is_idempotent_for_holed_multipart_geometry(rings):
    polygons = normalize_polygons(rings)
    assert normalize_polygons(polygons) == polygons


def test_nested_island_with_its_own_hole_survives_normalization():
    rings = [
        [[0, 0], [10, 0], [10, 10], [0, 10]],
        [[2, 2], [8, 2], [8, 8], [2, 8]],
        [[4, 4], [6, 4], [6, 6], [4, 6]],
        [[4.5, 4.5], [5.5, 4.5], [5.5, 5.5], [4.5, 5.5]],
    ]
    normalized = normalize_polygons(rings)
    geometry = geometry_from_polygons(normalized)
    assert geometry.area == 67
    assert len(geometry.geoms) == 2
    assert sum(len(poly.interiors) for poly in geometry.geoms) == 2
    assert normalize_polygons(normalized) == normalized
    scene = Scene()
    solid = scene.create_extrusion(normalized, 0, 3)
    scene.rotate(solid, 37)
    assert geometry_from_polygons(scene.to_massing()[0]["polygons"]).area == pytest.approx(67)
