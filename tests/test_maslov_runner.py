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
