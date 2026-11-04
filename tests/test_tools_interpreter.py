import pytest

from text2bim_massing import MassingTools, Scene
from text2bim_massing._vendor.text2bim.python_interpreter import InterpretorError, evaluate
from text2bim_massing.geometry import geometry_from_polygons


def test_original_interpreter_drives_millimetre_tools():
    scene = Scene()
    tools = MassingTools(scene, units="mm")
    code = """
profile = create_polygon([(0, 0), (10000, 0), (10000, 10000), (0, 10000)])
solid = create_extrusion(profile, 0, 6000)
copies = duplicate_obj(solid, n=1)
move_obj(copies, xDistance=20000, zDistance=3000)
rotate_obj(solid, 90, center=(0, 0))
"""
    _, state = evaluate(code, tools.as_functions(), state={})
    massing = tools.export_massing()
    assert len(massing) == 2
    assert geometry_from_polygons(massing[0]["polygons"]).area == pytest.approx(100)
    assert geometry_from_polygons(massing[1]["polygons"]).bounds == pytest.approx((20, 0, 30, 10))
    assert massing[1]["bottom_elevation"] == 3
    assert massing[1]["top_elevation"] == 9
    assert tools.get_object(state["solid"])["top_elevation"] == 6000
    assert tools.read_scene()["units"] == "m"
    assert "Tool lengths: mm" in tools.documentation()


def test_syntax_error_is_an_error_and_executes_nothing():
    scene = Scene()
    with pytest.raises(InterpretorError, match="Syntax error"):
        evaluate("create_polygon([(0,0),(1,0),(1,1)])\nif :", MassingTools(scene).as_functions())
    assert scene.snapshot().to_dict()["objects"] == []


def test_runtime_error_can_be_rolled_back_by_scene_transaction():
    scene = Scene()
    before = scene.snapshot()
    with pytest.raises(Exception, match="Evaluation stopped|Unexpected error"):
        with scene.transaction():
            evaluate(
                "profile = create_polygon([(0,0),(1,0),(1,1)])\ncreate_extrusion(profile, 0, 0)",
                MassingTools(scene).as_functions(),
                state={},
            )
    assert scene.snapshot() == before


def test_vertex_reads_and_profile_and_solid_editing(rings):
    scene = Scene()
    tools = MassingTools(scene)
    profile = tools.create_profile(rings)
    assert tools.get_vertex_count(profile) == 4
    assert len(tools.get_polygon_vertex(profile, 0)) == 2
    with pytest.raises(ValueError):
        tools.get_polygon_vertex(profile, -1)
    solid = tools.create_extrusion(profile, 0, 3)
    tools.set_polygon(profile, [rings[2]])
    tools.set_extrusion(solid, polygons=[rings[2]], top_elevation=8)
    assert geometry_from_polygons(tools.export_massing()[0]["polygons"]).area == 16
    assert tools.export_massing()[0]["top_elevation"] == 8
    tools.delete_element([profile, solid])
    assert tools.export_massing() == []


def test_units_must_be_explicitly_supported():
    with pytest.raises(ValueError, match="units"):
        MassingTools(Scene(), units="cm")
