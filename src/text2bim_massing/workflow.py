"""Text2BIM's PO/Programmer and Reviewer/patch workflows adapted to external evaluation."""

import json
import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path

from ._vendor.text2bim.agents import MyAgent, plan_designer
from ._vendor.text2bim.utils import clean_code_for_chat_extend
from .archive import CandidateArchive
from .config import GenerationTask, RunConfig
from .execution import ProcessExecutor
from .prompts import load_prompts
from .runtime import (
    Budget,
    BudgetedLLM,
    BudgetExceeded,
    EvaluationFailed,
    LLMFailed,
    Trace,
    write_json,
)
from .scene import Scene, SceneSnapshot
from .tools import MassingTools

PLAN_FUNCTION = [
    {
        "type": "function",
        "function": {
            "name": "plan_designer",
            "description": "Generate a structured massing design plan when architectural context is needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Detailed requirements for the plan",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    }
]


@dataclass(frozen=True)
class GenerationResult:
    status: str
    reason: str | None
    selected_candidate: dict | None
    candidates: tuple[dict, ...]
    history: tuple[dict, ...]
    costs: dict
    output_dir: str

    def to_dict(self):
        return deepcopy(asdict(self))


def _review_decision(text):
    try:
        decision = json.loads(text)
    except json.JSONDecodeError:
        _, blocks = clean_code_for_chat_extend(text)
        if len(blocks) != 1:
            raise ValueError("Reviewer must return one JSON decision") from None
        decision = json.loads(blocks[0])
    if not isinstance(decision, dict) or decision.get("action") not in {"finish", "improve"}:
        raise ValueError("Reviewer action must be finish or improve")
    if not isinstance(decision.get("candidate_id"), str) or not isinstance(
        decision.get("guidance"), str
    ):
        raise ValueError("Reviewer must supply candidate_id and guidance strings")
    return decision


def generate(task, evaluator, llm, config=None, output_dir="runs/text2bim") -> GenerationResult:
    """Generate, evaluate and improve massing; retain partial results on budget exhaustion.

    task is a string, GenerationTask, or {instruction, context}. evaluator obeys
    evaluator(massing, context) -> JSON report. llm implements complete(messages,
    tools=None, stop=None, timeout=None), as both supplied transports do.
    """
    config = RunConfig(**config) if isinstance(config, dict) else config or RunConfig()
    if isinstance(task, str):
        task = GenerationTask(task)
    elif isinstance(task, dict):
        task = GenerationTask(**task)
    if not isinstance(task, GenerationTask):
        raise TypeError("task must be an instruction, GenerationTask or task dictionary")
    if not callable(evaluator):
        raise TypeError("evaluator must be callable")
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise FileExistsError(f"Output directory must be empty: {root}")
    context = deepcopy(task.context)
    write_json(root / "task.json", {"instruction": task.instruction, "context": context})
    write_json(root / "config.json", asdict(config))
    write_json(
        root / "provenance.json",
        {
            "text2bim_commit": "b71b83d0d6640e7dfe7af3fda17b40fb3cfd70dc",
            "geometry_source_commit": "607ff1fcf80477787409522d93e18e42ac1436cf",
            "llm_transport": type(llm).__module__ + "." + type(llm).__qualname__,
            "model": getattr(llm, "model", None),
            "evaluator_type": type(evaluator).__module__ + "." + type(evaluator).__qualname__,
        },
    )
    prompts = load_prompts(config.tool_units)
    write_json(root / "prompts.json", prompts)
    trace = Trace(root)
    budget = Budget(config)
    backend = BudgetedLLM(llm, budget, trace)
    archive = CandidateArchive(root, evaluator, context, budget, trace)
    executor = ProcessExecutor(config, remaining=budget.remaining)

    def handle_event(message, code):
        budget.check()
        event = message["event"]
        if event == "commit":
            return archive.commit(
                SceneSnapshot(message["snapshot"]),
                "\n\n".join([*executor.codes, code]),
                message["state"],
            )
        if event == "evaluate":
            return archive.evaluate(message["candidate_id"])
        if event == "select":
            return archive.select(message["candidate_id"])
        raise ValueError(f"Unknown worker event: {event}")

    executor.event_handler = handle_event
    documentation = MassingTools(Scene(), units=config.tool_units).documentation() + (
        "\ncommit_candidate(): commit the current immutable scene snapshot; return candidate ID."
        "\nevaluate(candidate_id): evaluate this archived snapshot or read its cached JSON report."
        "\nselect_candidate(candidate_id): select an already evaluated archive entry without evaluation."
        "\nBuiltins: print, len, str, int, float, bool, list, dict, tuple, set, range, enumerate, zip, "
        "sum, min, max, abs, round, sorted, reversed, all, any. Imports: public math only."
    )
    enhancer = MyAgent(backend, prompts["Enhancer"], documentation, role="Enhancer", log=trace.add)
    programmer = MyAgent(
        backend,
        prompts["Programmer"],
        documentation,
        executor=executor,
        max_repairs=config.max_repairs,
        role="Programmer",
        log=trace.add,
    )
    reviewer = MyAgent(backend, prompts["Reviewer"], documentation, role="Reviewer", log=trace.add)
    status, reason = "budget_exhausted", "iterations"
    iteration = 0
    try:
        if config.max_iterations == 0:
            raise BudgetExceeded("iterations")
        query = (
            task.instruction
            + "\nExternal task context:\n"
            + json.dumps(context, ensure_ascii=False)
        )
        answer = enhancer.chat_with_function_call(
            query,
            "",
            available_functions={
                "plan_designer": lambda query: plan_designer(
                    query, llm=backend, prompt_template=prompts["Architect"]
                )
            },
            function_description=PLAN_FUNCTION,
        )
        # From run_po_coder_agents: PO answer is passed to Programmer, whose chat executes code.
        programmer_task = answer + "\nOriginal task and context:\n" + query
        while iteration < config.max_iterations:
            budget.check()
            iteration += 1
            trace.add("iteration", number=iteration)
            execution, code_result = programmer.chat(programmer_task, "")
            if not execution.success:
                budget.check()
                status, reason = "execution_failed", execution.error
                break
            current = next(
                (
                    candidate
                    for candidate in reversed(list(archive.candidates.values()))
                    if candidate.snapshot.json == executor.snapshot.json
                ),
                None,
            )
            if current is None:
                candidate_id = archive.commit(
                    executor.snapshot, "\n\n".join(executor.codes), executor.state
                )
            else:
                candidate_id = current.candidate_id
            # A missing explicit evaluation cannot turn an unassessed mutable form into success.
            archive.evaluate(candidate_id)
            issues = {
                "task": task.instruction,
                "context": context,
                "scene": executor.snapshot.to_dict(),
                "candidates": [candidate.to_dict() for candidate in archive.candidates.values()],
            }
            decision = None
            for attempt in range(config.max_repairs + 1):
                review_result = reviewer.chat_check(code=code_result, issues=json.dumps(issues))
                try:
                    decision = _review_decision(review_result)
                    archive.select(decision["candidate_id"])
                    break
                except (ValueError, KeyError) as error:
                    trace.add("review_error", error=str(error), attempt=attempt)
                    issues["decision_error"] = str(error)
                    decision = None
            if decision is None:
                status, reason = "review_failed", "No valid evaluated-candidate decision"
                break
            if decision["action"] == "finish":
                status, reason = "completed", None
                break
            chosen = archive.candidates[decision["candidate_id"]]
            executor.snapshot = chosen.snapshot
            executor.state = json.loads(chosen.state_json)
            executor.codes = [chosen.code]
            # Source's review patch request is retained, with the selected immutable state made explicit.
            programmer_task = (
                "The Python code that generates the building with some issues:\n"
                + chosen.code
                + "\nPlease write a patch to solve the issues based on the review suggestions. "
                "Do not write diff but an executable python script in a code block. "
                "You can reuse the variables defined in the original code, but DO NOT rewrite the original code."
                + "\nReview suggestions: "
                + decision["guidance"]
                + "\nSelected evaluated candidate: "
                + json.dumps(chosen.to_dict())
                + "\nSelected scene with stable IDs: "
                + chosen.snapshot.json
                + "\nOriginal task and context:\n"
                + query
            )
    except BudgetExceeded as error:
        status, reason = "budget_exhausted", str(error)
    except EvaluationFailed as error:
        status, reason = "evaluation_failed", str(error)
    except LLMFailed as error:
        status, reason = "llm_failed", str(error)
    except Exception as error:
        status, reason = "failed", f"{type(error).__name__}: {error}"
        trace.add("run_error", error=reason)
    selected = archive.candidates.get(archive.selected_id)
    responses = backend.responses
    usage_known = all(
        response.prompt_tokens is not None and response.completion_tokens is not None
        for response in responses
    )
    input_tokens = sum(response.prompt_tokens or 0 for response in responses)
    output_tokens = sum(response.completion_tokens or 0 for response in responses)
    money = None
    if (
        usage_known
        and len(responses) == budget.llm_calls
        and config.input_price_per_million is not None
        and config.output_price_per_million is not None
    ):
        money = (
            input_tokens * config.input_price_per_million
            + output_tokens * config.output_price_per_million
        ) / 1_000_000
    costs = {
        "llm_calls": budget.llm_calls,
        "evaluations": budget.evaluations,
        "execution_attempts": executor.attempts,
        "iterations": iteration,
        "elapsed_seconds": time.monotonic() - budget.started,
        "prompt_tokens": input_tokens,
        "completion_tokens": output_tokens,
        "usage_complete": usage_known and len(responses) == budget.llm_calls,
        "monetary_cost": money,
    }
    trace.add(
        "run_finished", status=status, reason=reason, selected_candidate_id=archive.selected_id
    )
    result = GenerationResult(
        status,
        reason,
        selected.to_dict() if selected else None,
        tuple(candidate.to_dict() for candidate in archive.candidates.values()),
        tuple(trace.events),
        costs,
        str(root),
    )
    write_json(root / "scene.json", executor.snapshot.to_dict())
    write_json(root / "result.json", result.to_dict())
    if selected:
        write_json(root / "selected_massing.json", selected.snapshot.to_massing())
        (root / "selected_code.py").write_text(selected.code)
    return result
