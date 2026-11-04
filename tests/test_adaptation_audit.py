import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "adaptation_audit", ROOT / "tools/audit_adaptation.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_full_adaptation_coverage_and_diffs_are_current():
    files, upstream = audit.run(ROOT)
    assert files > 70
    assert upstream == 44


@pytest.mark.parametrize("units,width,top", [("mm", 30000, 9000), ("m", 30, 9)])
def test_architect_keeps_few_shot_and_original_rationality_instruction(units, width, top):
    from text2bim_massing.prompts import load_prompts

    prompt = load_prompts(units)["Architect"]
    source = audit.source_text(
        ROOT,
        "text2bim",
        "tool_agent/muti_agent_prompt/floor_plan_designer_chat_prompt_few_shots.txt",
    )
    if units == "m":
        source = source.replace("millimeter units", "meter units")
    assert source[source.index("Make your design") : source.index("Here is a sample")] in prompt
    assert "Here is a sample conversation:" in prompt
    assert f"Use a {width}{units}" in prompt
    assert f"Top elevation: {top}{units}" in prompt
    assert prompt.endswith(source[source.index("The user now provides") :])


def test_audit_rejects_a_runtime_change_without_a_reviewed_record(tmp_path):
    import shutil

    # Use the reviewed inventory, not the developer's environments or run artifacts.
    for relative in audit.inventory(ROOT):
        source, target = ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    target = tmp_path / "src/text2bim_massing/workflow.py"
    target.write_text(target.read_text() + "\n# unreviewed change\n")
    with pytest.raises(ValueError, match="Unreviewed changes"):
        audit.run(tmp_path)


def test_audit_rejects_an_unclassified_new_file(tmp_path):
    import json
    import shutil

    for relative in audit.inventory(ROOT):
        source, target = ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (tmp_path / "new_module.py").write_text("pass\n")
    records = json.loads((tmp_path / audit.SPEC).read_text())
    with pytest.raises(ValueError, match="undocumented=.*new_module"):
        audit.validate(tmp_path, records)
