import json
from copy import deepcopy
from pathlib import Path

import pytest

from text2bim_massing import GenerationTask, RunConfig, generate
from text2bim_massing.llm import LLMResponse, ToolCall

BUILD = """```python
p=create_polygon([(0,0),(10000,0),(10000,8000),(0,8000)])
s=create_extrusion(p,0,3000)
candidate_id=commit_candidate()
report=evaluate(candidate_id)
select_candidate(candidate_id)
```"""
PATCH = """```python
set_extrusion(s,top_elevation=6000)
candidate_id=commit_candidate()
report=evaluate(candidate_id)
select_candidate(candidate_id)
```"""


class ScriptedLLM:
    """Explicit test transport, never represented as a live LLM run."""

    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def complete(self, messages, *, tools=None, stop=None, timeout=None):
        self.requests.append(deepcopy({"messages": messages, "tools": tools}))
        reply = next(self.replies)
        if isinstance(reply, BaseException):
            raise reply
        if isinstance(reply, LLMResponse):
            return reply
        return LLMResponse(reply, "scripted-test", 10, 5, 15)


def report(massing, context):
    return {"height": massing[0]["top_elevation"] - massing[0]["bottom_elevation"]}


def decision(action="finish", candidate="c0001", guidance="Done"):
    return json.dumps({"action": action, "candidate_id": candidate, "guidance": guidance})


def test_build_evaluate_reviewer_patch_reassess_select_and_persist(tmp_path):
    llm = ScriptedLLM(
        [
            "Build the initial volume",
            BUILD,
            decision("improve", guidance="Increase height"),
            PATCH,
            decision(candidate="c0002"),
        ]
    )
    result = generate(
        GenerationTask("Two floors", {"site_id": 7}), report, llm, output_dir=tmp_path
    )
    assert result.status == "completed", result.reason
    assert len(result.candidates) == 2
    assert result.candidates[0]["report"] == {"height": 3}
    assert result.selected_candidate["report"] == {"height": 6}
    assert result.costs["evaluations"] == 2
    assert result.costs["llm_calls"] == 5
    assert result.costs["prompt_tokens"] == 50
    saved = json.loads((tmp_path / "result.json").read_text())
    assert saved["selected_candidate"] == result.selected_candidate
    for candidate in ("c0001", "c0002"):
        assert (tmp_path / "candidates" / candidate / "snapshot.json").exists()
        assert (tmp_path / "candidates" / candidate / "report.json").exists()
    assert (tmp_path / "prompts.json").exists()
    assert any(e.get("role") == "Reviewer" for e in result.history)


def test_architect_is_only_called_when_enhancer_requests_it(tmp_path):
    function_response = LLMResponse(
        "",
        "scripted-test",
        10,
        5,
        15,
        (ToolCall("call1", "plan_designer", '{"query":"Design a rectangle"}'),),
    )
    llm = ScriptedLLM(
        [function_response, "Architect plan", "Enhanced instructions", BUILD, decision()]
    )
    result = generate("A building", report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    roles = [e["role"] for e in result.history if e["event"] == "llm_request"]
    assert roles == ["Enhancer", "Architect", "Enhancer", "Programmer", "Reviewer"]
    assert any(m["role"] == "tool" for m in llm.requests[2]["messages"])


def test_multiple_architect_requests_keep_upstream_sequential_dispatch(tmp_path):
    requests = (
        ToolCall("a", "plan_designer", '{"query":"first plan"}'),
        ToolCall("b", "plan_designer", '{"query":"second plan"}'),
    )
    llm = ScriptedLLM(
        [
            LLMResponse("", "test", 1, 1, 2, requests),
            "Plan A",
            "Plan B",
            "Enhanced task",
            BUILD,
            decision(),
        ]
    )
    result = generate("Build", report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    roles = [e["role"] for e in result.history if e["event"] == "llm_request"]
    assert roles == ["Enhancer", "Architect", "Architect", "Enhancer", "Programmer", "Reviewer"]


def test_unknown_function_uses_the_original_text_only_fallback(tmp_path):
    llm = ScriptedLLM(
        [
            LLMResponse("", "test", 1, 1, 2, (ToolCall("x", "invented", "{}"),)),
            "Enhanced task",
            BUILD,
            decision(),
        ]
    )
    result = generate("Build", report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    assert llm.requests[1]["messages"] == llm.requests[0]["messages"]
    assert llm.requests[1]["tools"] is None


def test_initial_programmer_receives_the_enhancer_answer_without_a_bypass(tmp_path):
    original = "ORIGINAL_TASK_MARKER"
    llm = ScriptedLLM(["ENHANCED_TASK_MARKER", BUILD, decision()])
    result = generate(original, report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    prompt = llm.requests[1]["messages"][0]["content"]
    assert "ENHANCED_TASK_MARKER" in prompt
    assert original not in prompt


def test_syntax_repair_is_separate_from_evaluated_shape_improvement(tmp_path):
    llm = ScriptedLLM(["Build", "```python\nif :\n```", BUILD, decision()])
    result = generate("A building", report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    assert result.costs["evaluations"] == 1
    assert result.costs["execution_attempts"] == 2
    assert result.costs["llm_calls"] == 4
    assert len(result.candidates) == 1


def test_archive_reports_are_cached_and_agent_can_select_an_older_snapshot(tmp_path):
    changed = PATCH.replace(
        "select_candidate(candidate_id)", "report=evaluate('c0001')\nselect_candidate('c0001')"
    )
    llm = ScriptedLLM(["Build", BUILD, decision("improve"), changed, decision(candidate="c0001")])
    result = generate("Compare candidates", report, llm, output_dir=tmp_path)
    assert result.status == "completed", result.reason
    assert result.costs["evaluations"] == 2
    assert result.selected_candidate["candidate_id"] == "c0001"
    assert result.selected_candidate["massing"][0]["top_elevation"] == 3
    assert result.candidates[1]["massing"][0]["top_elevation"] == 6
    assert any(e["event"] == "cached_report" for e in result.history)


@pytest.mark.parametrize("limit,reason", [(0, "llm_calls"), (2, "llm_calls")])
def test_llm_budget_retains_partial_evaluated_results(tmp_path, limit, reason):
    result = generate(
        "Build", report, ScriptedLLM(["Build", BUILD]), RunConfig(max_llm_calls=limit), tmp_path
    )
    assert result.status == "budget_exhausted" and result.reason == reason
    assert result.costs["llm_calls"] == limit
    if limit == 2:
        assert result.selected_candidate["report"] == {"height": 3}
    assert (tmp_path / "result.json").exists()


def test_evaluation_budget_counts_attempts_and_preserves_previous_selection(tmp_path):
    llm = ScriptedLLM(["Build", BUILD, decision("improve"), PATCH])
    result = generate("Build", report, llm, RunConfig(max_evaluations=1), tmp_path)
    assert result.status == "budget_exhausted" and result.reason == "evaluations"
    assert result.costs["evaluations"] == 1
    assert result.selected_candidate["candidate_id"] == "c0001"
    assert result.candidates[1]["report"] is None


def test_evaluator_failure_is_not_treated_as_programmer_syntax_error(tmp_path):
    def broken(massing, context):
        raise RuntimeError("Evaluator unavailable")

    result = generate("Build", broken, ScriptedLLM(["Build", BUILD]), output_dir=tmp_path)
    assert result.status == "evaluation_failed"
    assert result.costs["evaluations"] == 1 and result.costs["llm_calls"] == 2
    assert result.selected_candidate is None


def test_nontransferable_evaluator_is_saved_as_an_evaluation_failure(tmp_path):
    import threading

    class LockedEvaluator:
        def __init__(self):
            self.lock = threading.Lock()

        def __call__(self, massing, context):
            return {"value": 1}

    result = generate(
        "Build", LockedEvaluator(), ScriptedLLM(["Build", BUILD]), output_dir=tmp_path
    )
    assert result.status == "evaluation_failed"
    assert "Cannot transfer evaluator" in result.reason
    assert result.costs["evaluations"] == 1
    assert (tmp_path / "candidates/c0001/error-1.json").exists()


def test_non_json_report_and_timeout_are_errors(tmp_path):
    def bad(massing, context):
        return {"invalid": float("nan")}

    result = generate("Build", bad, ScriptedLLM(["Build", BUILD]), output_dir=tmp_path / "nan")
    assert result.status == "evaluation_failed"

    def slow(massing, context):
        import time

        time.sleep(10)
        return {}

    result = generate(
        "Build",
        slow,
        ScriptedLLM(["Build", BUILD]),
        RunConfig(evaluation_timeout=0.1),
        tmp_path / "timeout",
    )
    assert result.status == "evaluation_failed" and "timed out" in result.reason


def test_existing_output_is_never_overwritten(tmp_path):
    marker = tmp_path / "existing.txt"
    marker.write_text("keep")
    with pytest.raises(FileExistsError):
        generate("Build", report, ScriptedLLM([]), output_dir=tmp_path)
    assert marker.read_text() == "keep"


def test_llm_failure_records_partial_usage_without_invented_cost(tmp_path):
    llm = ScriptedLLM(["Build", BUILD, RuntimeError("model unavailable")])
    result = generate(
        "Build",
        report,
        llm,
        RunConfig(input_price_per_million=1, output_price_per_million=1),
        tmp_path,
    )
    assert result.status == "llm_failed"
    assert result.costs["llm_calls"] == 3
    assert result.costs["usage_complete"] is False
    assert result.costs["monetary_cost"] is None


def test_evaluated_archive_survives_later_failed_script(tmp_path):
    llm = ScriptedLLM(["Build", BUILD + "\n```python\n1/0\n```"])
    result = generate("Build", report, llm, RunConfig(max_repairs=0), tmp_path)
    assert result.status == "execution_failed"
    assert result.selected_candidate["report"] == {"height": 3}
    assert result.costs["evaluations"] == 1
    assert json.loads((Path(result.output_dir) / "scene.json").read_text())["objects"] == []


def test_uncommitted_edit_cannot_reuse_a_stale_snapshot_report(tmp_path):
    code = BUILD.replace(
        "select_candidate(candidate_id)",
        "select_candidate(candidate_id)\nset_extrusion(s,top_elevation=6000)\nold=evaluate(candidate_id)\nassert old['height']==3",
    )
    result = generate(
        "Build",
        report,
        ScriptedLLM(["Build", code, decision(candidate="c0002")]),
        output_dir=tmp_path,
    )
    assert result.status == "completed", result.reason
    assert result.costs["evaluations"] == 2
    assert result.selected_candidate["report"] == {"height": 6}
    assert result.candidates[0]["report"] == {"height": 3}


def test_wall_budget_is_reported_with_actual_elapsed_time(tmp_path):
    class SlowLLM:
        def complete(self, messages, **kwargs):
            import time

            time.sleep(0.04)
            return LLMResponse("Build", "test", 1, 1, 2)

    result = generate("Build", report, SlowLLM(), RunConfig(max_seconds=0.01), tmp_path)
    assert result.status == "budget_exhausted" and result.reason == "wall_time"
    assert result.costs["elapsed_seconds"] >= 0.04


def test_llm_timeout_at_wall_deadline_is_a_budget_stop(tmp_path):
    class TimeoutLLM:
        def complete(self, messages, **kwargs):
            import time

            time.sleep(0.04)
            raise TimeoutError("deadline")

    result = generate("Build", report, TimeoutLLM(), RunConfig(max_seconds=0.01), tmp_path)
    assert result.status == "budget_exhausted" and result.reason == "wall_time"


def test_malformed_review_does_not_select_an_unassessed_candidate(tmp_path):
    result = generate(
        "Build",
        report,
        ScriptedLLM(["Build", BUILD, decision(candidate="missing")]),
        RunConfig(max_repairs=0),
        tmp_path,
    )
    assert result.status == "review_failed"
    assert result.selected_candidate["candidate_id"] == "c0001"
