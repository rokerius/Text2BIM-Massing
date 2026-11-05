"""Regressions reconstructed from the review; its counterexamples.json was not supplied."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_workflow import BUILD, ScriptedLLM, decision, report

from text2bim_massing import MassingTools, RunConfig, Scene, generate
from text2bim_massing._worker import decode_state
from text2bim_massing.checkpoint import replay_checkpoint


def verify_archive(root):
    for directory in (root / "candidates").iterdir():
        checkpoint = replay_checkpoint(directory / "checkpoint.json")
        assert checkpoint.scene.snapshot().to_dict() == json.loads(
            (directory / "snapshot.json").read_text()
        )
        assert checkpoint.state == decode_state(json.loads((directory / "state.json").read_text()))


def replay_saved_code(result):
    """Run this test's known archive code and return the geometry it actually constructs."""
    scene = Scene()
    namespace = MassingTools(scene, units="mm").as_functions()
    namespace.update(
        __file__=str(Path(result.output_dir) / "selected_code.py"),
        commit_candidate=lambda: "test-replay",
        evaluate=lambda _: {},
        select_candidate=lambda _: None,
    )
    exec(result.selected_candidate["code"], namespace)
    if "checkpoint" in namespace:
        scene = namespace["checkpoint"].scene
    return scene.to_massing()


def test_saved_code_reproduces_snapshot_before_uncommitted_tail(tmp_path):
    code = BUILD.replace(
        "select_candidate(candidate_id)",
        "select_candidate(candidate_id)\nset_extrusion(s,top_elevation=6000)",
    )
    result = generate(
        "Choose the initial candidate",
        report,
        ScriptedLLM(["Build", code, decision(candidate="c0001")]),
        output_dir=tmp_path,
    )
    assert result.status == "completed", result.reason
    assert result.selected_candidate["report"] == {"height": 3}
    assert replay_saved_code(result) == result.selected_candidate["massing"]
    verify_archive(tmp_path)
    assert "set_extrusion(s,top_elevation=6000)" in result.selected_candidate["source_code"]
    process = subprocess.run(
        [sys.executable, str(tmp_path / "selected_code.py")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(process.stdout) == result.selected_candidate["massing"]


def test_restore_keeps_variables_defined_after_commit_in_successful_script(tmp_path):
    code = BUILD.replace("```", "", 1).rsplit("```", 1)[0]
    code = "```" + code + "\nlate_binding_for_patch=s\nvalues_after_commit=[1,2]\n```"
    patch = """```python
assert values_after_commit == [1,2]
set_extrusion(late_binding_for_patch,top_elevation=6000)
candidate_id=commit_candidate()
report=evaluate(candidate_id)
select_candidate(candidate_id)
```"""
    result = generate(
        "Two floors",
        report,
        ScriptedLLM(["Build", code, decision("improve"), patch, decision(candidate="c0002")]),
        RunConfig(max_repairs=0),
        tmp_path,
    )
    assert result.status == "completed", result.reason
    assert result.costs["llm_calls"] == 5
    assert result.costs["evaluations"] == 2
    assert result.selected_candidate["report"] == {"height": 6}
    checkpoint = replay_checkpoint(tmp_path / "candidates/c0001/checkpoint.json")
    assert checkpoint.state["values_after_commit"] == [1, 2]
    assert checkpoint.scene.get(checkpoint.state["late_binding_for_patch"])["top_elevation"] == 3
    verify_archive(tmp_path)


def test_restore_older_loop_checkpoint_discards_abandoned_future_operations(tmp_path):
    code = """```python
p=create_polygon([(0,0),(1000,0),(1000,1000),(0,1000)])
for floor in [1,2]:
    s=create_extrusion(p,0,3000*floor)
    candidate_id=commit_candidate()
    report=evaluate(candidate_id)
    select_candidate(candidate_id)
```"""
    patch = """```python
assert floor==1
set_extrusion(s,top_elevation=9000)
candidate_id=commit_candidate()
report=evaluate(candidate_id)
select_candidate(candidate_id)
```"""
    result = generate(
        "Edit the first candidate",
        report,
        ScriptedLLM(
            [
                "Build",
                code,
                decision("improve", candidate="c0001"),
                patch,
                decision(candidate="c0003"),
            ]
        ),
        output_dir=tmp_path,
    )
    assert result.status == "completed", result.reason
    assert len(result.selected_candidate["massing"]) == 1
    assert result.selected_candidate["report"] == {"height": 9}
    assert result.costs["evaluations"] == 3
    assert result.candidates[0]["checkpoint_boundary"] == "commit"
    verify_archive(tmp_path)
    assert replay_saved_code(result) == result.selected_candidate["massing"]


def test_evaluated_checkpoint_survives_failure_but_does_not_take_rolled_back_state(tmp_path):
    code = (
        BUILD.rsplit("```", 1)[0] + "\nlate_value=99\nset_extrusion(s,top_elevation=6000)\n1/0\n```"
    )
    result = generate(
        "Build", report, ScriptedLLM(["Build", code]), RunConfig(max_repairs=0), tmp_path
    )
    assert result.status == "execution_failed"
    assert result.selected_candidate["report"] == {"height": 3}
    checkpoint = replay_checkpoint(tmp_path / "checkpoint.json")
    assert "late_value" not in checkpoint.state
    assert checkpoint.scene.to_massing() == result.selected_candidate["massing"]
    assert json.loads((tmp_path / "scene.json").read_text())["objects"] == []
    assert result.costs["evaluations"] == 1
    verify_archive(tmp_path)


def test_pure_variable_update_keeps_latest_state_without_an_extra_evaluation(tmp_path):
    first = BUILD.rsplit("```", 1)[0] + "\nvalues_after_commit=[1]\n```"
    patch = "```python\nvalues_after_commit.append(2)\n```"
    result = generate(
        "Update variables",
        report,
        ScriptedLLM(["Build", first, decision("improve"), patch, decision()]),
        output_dir=tmp_path,
    )
    assert result.status == "completed", result.reason
    assert result.costs["evaluations"] == 1
    assert len(result.candidates) == 1
    assert replay_checkpoint(tmp_path / "checkpoint.json").state["values_after_commit"] == [1, 2]
    verify_archive(tmp_path)


def test_checkpoint_replays_captured_arguments_ids_and_math_aliases(tmp_path):
    code = """```python
from math import sqrt
points=[(0,0),(1000,0),(1000,1000),(0,1000)]
p=create_polygon(points)
s=create_extrusion(p,0,3000)
copies=duplicate_obj(s,n=2)
move_obj(copies,xDistance=4000)
rotate_obj(copies,angle=90)
delete_element(copies[0])
candidate_id=commit_candidate()
report=evaluate(candidate_id)
select_candidate(candidate_id)
points[0]=(9000,9000)
aliases=(s,copies)
```"""
    result = generate(
        "Build", report, ScriptedLLM(["Build", code, decision()]), output_dir=tmp_path
    )
    assert result.status == "completed", result.reason
    checkpoint = replay_checkpoint(tmp_path / "checkpoint.json")
    assert checkpoint.state["sqrt"](9) == 3
    assert checkpoint.state["points"][0] == (9000, 9000)
    assert checkpoint.scene.get(checkpoint.state["s"])["polygons"][0][0] == [0, 0]
    assert checkpoint.state["aliases"][0] == checkpoint.state["s"]
    verify_archive(tmp_path)


def test_replay_rejects_a_journal_that_does_not_match_its_snapshot(tmp_path):
    result = generate(
        "Build", report, ScriptedLLM(["Build", BUILD, decision()]), output_dir=tmp_path
    )
    assert result.status == "completed"
    data = json.loads((tmp_path / "checkpoint.json").read_text())
    data["actions"].pop()
    (tmp_path / "corrupt.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="does not match"):
        replay_checkpoint(tmp_path / "corrupt.json")
