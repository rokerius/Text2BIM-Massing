"""Budgets, durable traces and bounded external evaluation."""

import json
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict
from pathlib import Path


class BudgetExceeded(RuntimeError):
    pass


class EvaluationFailed(RuntimeError):
    pass


class LLMFailed(RuntimeError):
    pass


def write_json(path: Path, value):
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(data + "\n")
    temporary.replace(path)


class Trace:
    def __init__(self, root: Path):
        self.root = root
        self.events = []

    def add(self, event: str, **values):
        record = {"event": event, **values}
        self.events.append(record)
        with (self.root / "history.jsonl").open("a") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


class Budget:
    def __init__(self, config):
        self.config, self.started = config, time.monotonic()
        self.llm_calls = 0
        self.evaluations = 0

    def remaining(self):
        return max(0.0, self.config.max_seconds - (time.monotonic() - self.started))

    def check(self):
        if self.remaining() <= 0:
            raise BudgetExceeded("wall_time")

    def llm(self):
        self.check()
        if self.llm_calls >= self.config.max_llm_calls:
            raise BudgetExceeded("llm_calls")
        self.llm_calls += 1

    def evaluation(self):
        self.check()
        if self.evaluations >= self.config.max_evaluations:
            raise BudgetExceeded("evaluations")
        self.evaluations += 1


class BudgetedLLM:
    def __init__(self, llm, budget: Budget, trace: Trace):
        self.llm, self.budget, self.trace = llm, budget, trace
        self.role = "Enhancer"
        self.responses = []

    def complete(self, messages, *, tools=None, stop=None):
        self.budget.llm()
        role = self.role
        call_id = self.budget.llm_calls
        self.trace.add("llm_request", call_id=call_id, role=role, messages=messages, tools=tools)
        try:
            self.budget.check()
            response = self.llm.complete(
                messages, tools=tools, stop=stop, timeout=self.budget.remaining()
            )
        except BudgetExceeded:
            raise
        except Exception as error:
            self.trace.add("llm_error", call_id=call_id, role=role, error=str(error))
            self.budget.check()
            raise LLMFailed(str(error)) from error
        self.responses.append(response)
        self.trace.add("llm_response", call_id=call_id, role=role, response=asdict(response))
        self.budget.check()
        return response

    def generate_one(self, prompt, stop=None):
        response = self.complete([{"role": "user", "content": prompt}], stop=stop)
        if response.tool_calls:
            raise LLMFailed("Unexpected tool calls in text-only response")
        return response.text

    def generate_with_function_call(self, prompt, stop, available_functions, function_description):
        # From Text2BIM OpenAiAgent.generate_with_function_call: tool request,
        # execute supplied functions, append tool outputs, then request final text.
        messages = [{"role": "user", "content": prompt}]
        response = self.complete(messages, tools=function_description, stop=stop)
        if not response.tool_calls:
            return response.text
        messages.append(
            {
                "role": "assistant",
                "content": response.text or None,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": call.arguments,
                        },
                    }
                    for call in response.tool_calls
                ],
            }
        )
        for call in response.tool_calls:
            if call.name not in available_functions:
                return self.generate_one(prompt, stop)
            function_to_call = available_functions[call.name]
            function_args = json.loads(call.arguments)
            result = function_to_call(function_args.get("query"))
            messages.append({"tool_call_id": call.id, "role": "tool", "content": str(result)})
        final = self.complete(messages, stop=stop)
        if final.tool_calls:
            raise LLMFailed("Unexpected recursive function call")
        return final.text


def evaluate_bounded(evaluator, massing, context, timeout):
    import cloudpickle

    from .execution import kill_process

    deadline = time.monotonic() + timeout
    with tempfile.TemporaryDirectory(prefix="text2bim-evaluate-") as folder:
        root = Path(folder)
        input_path, output_path = root / "input.pkl", root / "report.json"
        (root / "paths.json").write_text(json.dumps(sys.path))
        try:
            with input_path.open("wb") as stream:
                cloudpickle.dump((evaluator, massing, context), stream)
        except Exception as error:
            raise EvaluationFailed(f"Cannot transfer evaluator to its process: {error}") from error
        with tempfile.TemporaryFile() as logs:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "text2bim_massing._evaluate_worker",
                    str(input_path),
                    str(output_path),
                    str(root / "paths.json"),
                ],
                stdout=logs,
                stderr=logs,
                start_new_session=True,
            )
            try:
                process.wait(timeout=max(0.001, deadline - time.monotonic()))
                if process.returncode or not output_path.exists():
                    logs.seek(0)
                    raise EvaluationFailed(
                        "Evaluator exited without a valid report: "
                        + logs.read(4000).decode(errors="replace")
                    )
                if output_path.stat().st_size > 8_000_000:
                    raise EvaluationFailed("Evaluator report exceeds size limit")
                message = json.loads(output_path.read_text())
                if not message["ok"]:
                    raise EvaluationFailed(message["error"])
                return message["report"]
            except subprocess.TimeoutExpired as error:
                raise EvaluationFailed("Evaluator timed out") from error
            finally:
                kill_process(process)
