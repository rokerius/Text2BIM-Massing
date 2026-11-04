import pytest

from text2bim_massing import RunConfig, Scene
from text2bim_massing.execution import ProcessExecutor

CREATE = "p=create_polygon([(0,0),(1000,0),(1000,1000),(0,1000)])\ns=create_extrusion(p,0,3000)"


def test_process_preserves_ids_variables_math_aliases_and_tuples():
    executor = ProcessExecutor(RunConfig())
    assert executor.execute(CREATE + "\nfrom math import sqrt\nv=(1,2)\nx=sqrt(9)").success
    original = executor.snapshot.to_dict()["objects"]
    assert executor.execute(
        "assert sqrt(x*x)==3\nassert v==(1,2)\nset_extrusion(s,top_elevation=6000)"
    ).success
    assert [obj["id"] for obj in executor.snapshot.to_dict()["objects"]] == [
        obj["id"] for obj in original
    ]
    assert executor.snapshot.to_massing()[0]["top_elevation"] == 6


def test_failed_script_restores_scene_and_mutable_interpreter_state():
    executor = ProcessExecutor(RunConfig())
    assert executor.execute(CREATE + "\nvalues=[1]").success
    before, state = executor.snapshot, executor.state
    result = executor.execute("values.append(2)\nmove_obj(s,xDistance=1000)\n1/0")
    assert not result.success
    assert executor.snapshot == before and executor.state == state
    assert executor.execute("assert values==[1]").success


@pytest.mark.parametrize(
    "code",
    [
        "import os",
        "from pathlib import Path",
        "import math\nx=math.__dict__",
        "open('/tmp/text2bim-not-allowed','w')",
        "x=create_polygon.__self__",
        "def dangerous():\n    pass",
        "from math import *",
    ],
)
def test_worker_limits_available_capabilities(code):
    executor = ProcessExecutor(RunConfig())
    assert not executor.execute(code).success
    assert executor.snapshot == Scene().snapshot()


def test_infinite_loop_is_killed_and_later_attempt_can_run():
    executor = ProcessExecutor(RunConfig(execution_timeout=1.5))
    result = executor.execute("while True:\n    pass")
    assert not result.success and "timed out" in result.error
    assert executor.execute(CREATE).success


def test_generated_output_and_code_size_are_bounded():
    executor = ProcessExecutor(RunConfig(max_output_bytes=100, max_code_bytes=1000))
    assert not executor.execute('print("a"*1000)').success
    assert not executor.execute("#" * 1001).success


def test_restore_snapshot_keeps_ids_and_validates_input(rings):
    scene = Scene()
    scene.create_extrusion(rings, 0, 3)
    snapshot = scene.snapshot()
    assert Scene.from_snapshot(snapshot).snapshot() == snapshot
