import pytest

from text2bim_massing import Scene
from text2bim_massing.adapters import SampleMetricAdapter, SampleProcessorAdapter, compile_mesh
from text2bim_massing.geometry import geometry_from_polygons, normalize_polygons

pytestmark = pytest.mark.maslov


def test_ring_conversion_matches_pinned_implementation(maslov, rings):
    converter = maslov["polygons_to_shapely_converter"].PolygonsToShapelyConverter()
    reverse = maslov["shapely_to_polygons_converter"].ShapelyToPolygonsConverter()
    for values in ([rings[0]], rings, [rings[2], rings[0], rings[1]], [rings[1], rings[0]]):
        expected = converter(polygons=[[(float(x), float(y)) for x, y in ring] for ring in values])
        actual = geometry_from_polygons(normalize_polygons(values))
        assert actual.equals(expected)
        assert geometry_from_polygons(reverse(polygons=expected)).equals(actual)


def test_real_mesh_preserves_holes_components_and_vertical_translation(maslov, rings):
    compiler = maslov["mesh_compiler.massing_mesh_compiler"].MassingMeshCompiler()
    scene = Scene()
    solid = scene.create_extrusion(rings, 0, 6)
    mesh = compile_mesh(scene.to_massing(), compiler)
    assert mesh.is_watertight
    assert len(mesh.split()) == 2
    assert mesh.volume == pytest.approx(112 * 6)
    assert mesh.bounds.tolist() == [[0, 0, 0], [24, 10, 6]]
    scene.move(solid, z=13)
    shifted = compile_mesh(scene.to_massing(), compiler)
    assert shifted.is_watertight
    assert shifted.volume == pytest.approx(mesh.volume)
    assert shifted.bounds[:, 2].tolist() == [13, 19]


def test_real_metric_receives_expected_building_wrapper(maslov, rings):
    metric = maslov["sample_metric.building_zero_heights_rate"].BuildingZeroHeightsRate(
        building_key="building"
    )
    scene = Scene()
    scene.create_extrusion(rings, 0, 6)
    report = SampleMetricAdapter(metric, report_key="zero_heights_rate")(scene.to_massing(), {})
    assert report == {"zero_heights_rate": 0.0}


def test_real_processor_receives_building_collection(maslov, rings):
    processor = maslov["sample_processor.shapely_massing_creator"].ShapelyMassingCreator(
        massing_key="building", shapely_massing_key="shapely_building"
    )
    scene = Scene()
    scene.create_extrusion(rings, 0, 6)
    # Select the retained JSON input; the processor's additional Shapely field is internal.
    adapter = SampleProcessorAdapter(processor, report_keys=("building",), layout="buildings")
    report = adapter(scene.to_massing(), {})
    assert report["building"][0]["massing"] == scene.to_massing()


def test_real_mesh_keeps_an_island_inside_a_hole(maslov):
    rings = [
        [[0, 0], [10, 0], [10, 10], [0, 10]],
        [[2, 2], [8, 2], [8, 8], [2, 8]],
        [[4, 4], [6, 4], [6, 6], [4, 6]],
    ]
    scene = Scene()
    scene.create_extrusion(rings, 0, 3)
    compiler = maslov["mesh_compiler.massing_mesh_compiler"].MassingMeshCompiler()
    mesh = compile_mesh(scene.to_massing(), compiler)
    assert mesh.is_watertight
    assert len(mesh.split()) == 2
    assert mesh.volume == pytest.approx(68 * 3)


def test_complete_feedback_workflow_uses_real_maslov_metric(maslov, tmp_path):
    from src.sample_metric.building_floor_count import BuildingFloorCount
    from test_workflow import BUILD, PATCH, ScriptedLLM, decision

    from text2bim_massing import generate

    evaluator = SampleMetricAdapter(
        BuildingFloorCount(building_key="building", floor_height=3.0), report_key="floor_count"
    )
    llm = ScriptedLLM(["Build", BUILD, decision("improve"), PATCH, decision(candidate="c0002")])
    result = generate("Create two floors", evaluator, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    assert [candidate["report"] for candidate in result.candidates] == [
        {"floor_count": 1.0},
        {"floor_count": 2.0},
    ]
    assert result.costs["evaluations"] == 2
