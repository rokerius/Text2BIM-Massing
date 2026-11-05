import json
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from text2bim_massing.llm import LLMResponse

ROOT = Path(__file__).resolve().parents[1]
runner = SimpleNamespace(**runpy.run_path(str(ROOT / "integrations/maslov/run.py")))


def test_input_preserves_requirement_ids_and_excludes_reference_geometry():
    row = {
        "id": 7,
        "site_contour": [[[0, 0], [10, 0], [10, 10]]],
        "requirements": [{"id": "office", "floor_count": 2}],
        "building": "DO_NOT_LEAK",
        "pred_massing": "DO_NOT_LEAK",
    }
    prepared = runner.prepare_rows([row])[0]
    assert set(prepared) == {"id", "site_contour", "requirements"}
    assert prepared["requirements"] == row["requirements"]
    prepared["requirements"][0]["id"] = "changed"
    assert row["requirements"][0]["id"] == "office"


@pytest.mark.parametrize("requirements", [[], [{"id": 1}, {"id": 2}], [{}]])
def test_unsupported_requirements_are_rejected_before_generation(requirements):
    with pytest.raises(ValueError, match="exactly one building"):
        runner.prepare_rows([{"id": 7, "site_contour": [[0]], "requirements": requirements}])


def test_sample_selection_does_not_silently_drop_ids():
    row = {"id": 7, "site_contour": [[0]]}
    with pytest.raises(ValueError, match="Unknown sample ids"):
        runner.prepare_rows([row], ["missing"])
    with pytest.raises(ValueError, match="Duplicate sample id"):
        runner.prepare_rows([row, row])
    assert runner.prepare_rows({"site_contour": [[0]]}, fallback_id="file")[0]["id"] == "file"


@pytest.mark.parametrize(
    "patch",
    [
        {"n_floors": 0},
        {"n_floors": 2.5},
        {"floor_height": 0},
        {"floor_height": True},
        {"floor_height": "3.5"},
        {"total_area": -1},
        {"total_area": float("nan")},
        {"total_area": float("inf")},
        {"id": True},
        {"id": " "},
    ],
)
def test_unknown_or_invalid_requirements_never_receive_pilot_defaults(patch):
    with pytest.raises(ValueError):
        runner.validate_requirement(
            {"id": 0, "n_floors": 2.0, "floor_height": 3.5, "total_area": 160, **patch}
        )


@pytest.mark.parametrize("missing", ["n_floors", "floor_height", "total_area"])
def test_missing_numerical_requirement_is_rejected(missing):
    requirement = {"id": 0, "n_floors": 2.0, "floor_height": 3.5, "total_area": 160}
    del requirement[missing]
    with pytest.raises(ValueError, match="missing " + missing):
        runner.validate_requirement(requirement)


def test_explicit_pilot_mode_and_unknown_mode():
    row = {"id": "pilot", "site_contour": [[[0, 0], [2, 0], [2, 2]]]}
    task, binding = runner.bind_task(row, {"task_mode": "pilot", "instruction": "Build"})
    assert task.instruction == "Build"
    assert task.context == row
    assert binding == {"mode": "pilot"}
    with pytest.raises(ValueError, match="Unknown task_mode"):
        runner.bind_task(row, {"task_mode": "typo", "instruction": "Build"})
    with pytest.raises(ValueError, match="exactly one building"):
        runner.bind_task(row, {"task_mode": "requirements", "instruction": "Build"})


@pytest.mark.maslov
def test_alias_normalization_reuses_original_helper_and_records_sources(maslov):
    from copy import deepcopy

    spec = json.loads((ROOT / "integrations/maslov/requirements.json").read_text())
    context = {
        "id": "sample",
        "site_contour": [[[0, 0], [20, 0], [20, 20], [0, 20]]],
        "requirements": [
            {
                "id": 0,
                "n_floors": 2.0,
                "floor_height": 3.5,
                "usable_area": 160,
                "building_function": "Office",
            }
        ],
    }
    original = deepcopy(context)
    task, binding = runner.bind_task(context, spec)
    assert context == original
    assert task.context["requirements"] == [
        {
            "id": 0,
            "n_floors": 2.0,
            "floor_height": 3.5,
            "total_area": 160,
            "building_function": "Office",
        }
    ]
    assert binding["source_requirements"] == original["requirements"]
    assert binding["source_fields"]["total_area_m2"] == ["requirements[0].usable_area"]
    assert binding["targets"]["building_height_m"] == 7
    assert binding["targets"]["mean_floor_area_m2"] == 80
    assert binding["defaults_applied"] == {}
    context["requirements"][0]["total_area"] = 999
    with pytest.raises(ValueError, match="disagree"):
        runner.bind_task(context, spec)


@pytest.mark.maslov
def test_dataset_preparation_saves_provenance_without_constructing_llm(
    maslov, tmp_path, monkeypatch
):
    repo = Path(maslov["polygons_to_shapely_converter"].__file__).parents[1]
    source = repo / "experiments/sandbox/subtractive_additive/inputs/coma_1627_single.json"

    def forbidden(_):
        raise AssertionError("Preparation must not construct an LLM client")

    # Test task preparation independently of how the suite's package was installed.
    # Exact VCS/editable pin validation has its own drift test and live-run verification.
    monkeypatch.setitem(
        runner.main.__globals__,
        "verify_package",
        lambda expected: {"commit": expected, "installation": "test"},
    )
    monkeypatch.setitem(runner.main.__globals__, "load_llm", forbidden)
    output = tmp_path / "prepared"
    args = [
        "--config",
        str(ROOT / "integrations/maslov/requirements.json"),
        "--maslov-repo",
        str(repo),
        "--sample",
        str(source),
        "--output",
        str(output),
    ]
    assert runner.main([*args, "--prepare-only"]) == 0
    bindings = json.loads((output / "task_bindings.json").read_text())
    source_data = json.loads(source.read_text())
    assert bindings[0]["source_requirements"] == source_data["requirements"]
    assert bindings[0]["targets"]["n_floors"] == 14
    assert bindings[0]["targets"]["floor_height_m"] == 3.714
    assert json.loads((output / "preparation.json").read_text())["status"] == "prepared"
    assert not (output / "submit.json").exists()
    # An unsupported second row fails before creating output or touching the model.
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            [
                source_data,
                {
                    **source_data,
                    "id": "unknown",
                    "requirements": [{**source_data["requirements"][0], "n_floors": 0}],
                },
            ]
        )
    )
    invalid_output = tmp_path / "invalid-output"
    with pytest.raises(ValueError, match="n_floors must be stated"):
        runner.main(
            [
                "--config",
                args[1],
                "--maslov-repo",
                str(repo),
                "--dataset",
                str(invalid),
                "--output",
                str(invalid_output),
            ]
        )
    assert not invalid_output.exists()


def test_editable_package_pin_rejects_runtime_drift(tmp_path, monkeypatch):
    checkout = tmp_path / "package"
    (checkout / "src").mkdir(parents=True)
    source = checkout / "src/runtime.py"
    source.write_text("# pinned\n")
    (checkout / "pyproject.toml").write_text("# pinned\n")
    command = ["git", "-C", str(checkout)]
    subprocess.run(command + ["init", "-q"], check=True)
    subprocess.run(command + ["add", "."], check=True)
    subprocess.run(
        command
        + ["-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "pin"],
        check=True,
    )
    commit = subprocess.check_output(command + ["rev-parse", "HEAD"], text=True).strip()
    metadata = SimpleNamespace(
        version="test",
        read_text=lambda name: json.dumps(
            {"dir_info": {"editable": True}, "url": checkout.as_uri()}
        ),
    )
    monkeypatch.setitem(runner.verify_package.__globals__, "distribution", lambda name: metadata)
    assert runner.verify_package(commit)["commit"] == commit
    source.write_text("# changed\n")
    with pytest.raises(subprocess.CalledProcessError):
        runner.verify_package(commit)
    source.write_text("# pinned\n")
    (checkout / "src/untracked.py").write_text("# changed\n")
    with pytest.raises(ValueError, match="untracked runtime"):
        runner.verify_package(commit)


@pytest.mark.maslov
def test_independent_tasks_original_metrics_and_submission_ids(maslov, tmp_path):
    spec = json.loads((ROOT / "integrations/maslov/pilot.json").read_text())
    spec["run"]["max_iterations"] = 1
    replies = iter(
        [
            "Create one massing inside the site.",
            "```python\np=create_polygon([(0,0),(1000,0),(1000,1000),(0,1000)])\n"
            "s=create_extrusion(p,0,6000)\n```",
            '{"action":"finish","candidate_id":"c0001","guidance":"done"}',
        ]
        * 2
    )

    class ScriptedClient:
        def complete(self, messages, **kwargs):
            return LLMResponse(next(replies), "scripted-test", 1, 1, 2)

    rows = runner.prepare_rows(
        [
            {
                "id": i,
                "site_contour": [[[-1, -1], [2, -1], [2, 2], [-1, 2]]],
                "requirements": [{"id": f"building-{i}"}],
            }
            for i in (7, 8)
        ]
    )
    assert runner.run_rows(spec, rows, tmp_path, ScriptedClient()) == 0
    submission = json.loads((tmp_path / "submit.json").read_text())
    assert [r["pred_massing"][0]["id"] for r in submission] == ["building-7", "building-8"]
    reports = json.loads((tmp_path / "report.json").read_text())
    assert [r["candidate_id"] for r in reports] == ["c0001", "c0001"]
    assert all(r["metrics"] == {"floor_count": 2.0, "site_match": 1.0} for r in reports)
    assert all(r["costs"]["evaluations"] == 1 for r in reports)
    assert all(r["costs"]["llm_calls"] == 3 for r in reports)
    assert (tmp_path / "tasks/0000/task.json").is_file()
    assert (tmp_path / "tasks/0001/task.json").is_file()


@pytest.mark.maslov
def test_requirements_workflow_uses_each_rows_targets_and_reviewer_feedback(maslov, tmp_path):
    spec = json.loads((ROOT / "integrations/maslov/requirements.json").read_text())
    rows = runner.prepare_rows(
        [
            {
                "id": "first",
                "site_contour": [[[-1, -1], [12, -1], [12, 10], [-1, 10]]],
                "requirements": [
                    {"id": 0, "n_floors": 2.0, "floor_height": 3.5, "usable_area": 160}
                ],
                "building": "DO_NOT_LEAK",
            },
            {
                "id": "second",
                "site_contour": [[[-1, -1], [12, -1], [12, 10], [-1, 10]]],
                "requirements": [
                    {"id": "different-id", "n_floors": 4, "floor_height": 3.25, "total_area": 320}
                ],
                "pred_massing": "DO_NOT_LEAK",
            },
        ]
    )
    build = "```python\np=create_polygon([(0,0),(10000,0),(10000,8000),(0,8000)])\ns=create_extrusion(p,0,{height})\n```"
    replies = iter(
        [
            "First building, two floors with 3.5 m per floor.",
            build.format(height=3500),
            '{"action":"improve","candidate_id":"c0001","guidance":"Actual errors are 0.5; raise top to 7 m"}',
            "```python\nset_extrusion(s,top_elevation=7000)\n```",
            '{"action":"finish","candidate_id":"c0002","guidance":"both errors zero"}',
            "Second building, four floors with 3.25 m per floor.",
            build.format(height=13000),
            '{"action":"finish","candidate_id":"c0001","guidance":"both errors zero"}',
        ]
    )
    prompts = []

    class ScriptedClient:
        def complete(self, messages, **kwargs):
            prompts.append(json.dumps(messages))
            return LLMResponse(next(replies), "scripted-test", 1, 1, 2)

    assert runner.run_rows(spec, rows, tmp_path, ScriptedClient()) == 0
    records = json.loads((tmp_path / "report.json").read_text())
    assert (
        records[0]["metrics"]
        == records[1]["metrics"]
        == {"floor_count_error": 0.0, "usable_area_error": 0.0, "site_match": 1.0, "id_iou": 1.0}
    )
    assert [r["costs"]["evaluations"] for r in records] == [2, 1]
    assert [r["candidate_id"] for r in records] == ["c0002", "c0001"]
    first = json.loads((tmp_path / "tasks/0000/result.json").read_text())
    assert first["candidates"][0]["report"]["floor_count_error"] == 0.5
    assert first["candidates"][0]["report"]["usable_area_error"] == 0.5
    submission = json.loads((tmp_path / "submit.json").read_text())
    assert [r["pred_massing"][0]["id"] for r in submission] == [0, "different-id"]
    assert submission[0]["requirements"][0]["total_area"] == 160
    bindings = [
        json.loads((tmp_path / f"tasks/{i:04d}/task_binding.json").read_text()) for i in range(2)
    ]
    assert [b["targets"]["building_height_m"] for b in bindings] == [7.0, 13.0]
    assert [b["targets"]["total_area_m2"] for b in bindings] == [160.0, 320.0]
    assert all("DO_NOT_LEAK" not in prompt for prompt in prompts)
    assert "building_height_m" in prompts[0]


@pytest.mark.maslov
@pytest.mark.parametrize("base", [0.0, 11.5])
def test_original_area_metric_keeps_holes_components_and_vertical_translation(maslov, base):
    spec = json.loads((ROOT / "integrations/maslov/requirements.json").read_text())
    context = {
        "id": "geometry-check",
        "site_contour": [[[-1, -1], [30, -1], [30, 20], [-1, 20]]],
        "requirements": [{"id": 0, "n_floors": 2, "floor_height": 3.5, "total_area": 224}],
    }
    task, _ = runner.bind_task(context, spec)
    evaluator = runner.ConfiguredMetrics(spec["evaluators"], 0)
    report = evaluator(
        [
            {
                "polygons": [
                    [[0, 0], [10, 0], [10, 10], [0, 10]],
                    [[2, 2], [4, 2], [4, 4], [2, 4]],
                    [[20, 0], [24, 0], [24, 4], [20, 4]],
                ],
                "bottom_elevation": base,
                "top_elevation": base + 7,
            },
        ],
        task.context,
    )
    assert report == {"floor_count_error": 0, "usable_area_error": 0, "site_match": 1, "id_iou": 1}
