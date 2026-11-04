"""Codex CLI transport using its saved ChatGPT subscription login."""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .execution import kill_process
from .geometry import finite_number
from .llm import LLMResponse, ToolCall


@dataclass(frozen=True)
class CodexConfig:
    model: str | None = None
    executable: str = "codex"
    timeout: float = 120
    reasoning_effort: str | None = None

    def __post_init__(self):
        if finite_number(self.timeout, "timeout") <= 0:
            raise ValueError("Codex timeout must be positive")
        if self.model is not None and (not isinstance(self.model, str) or not self.model.strip()):
            raise ValueError("Codex model must be a nonempty string when supplied")


class CodexCLIClient:
    """One CLI invocation per completion; no API key is read or copied."""

    def __init__(self, config: CodexConfig | None = None):
        self.config = config or CodexConfig()
        self.executable = shutil.which(self.config.executable)
        if not self.executable:
            raise ValueError("Codex CLI is unavailable; install it and run codex login")
        self.model = self.config.model or "codex-cli-default"
        self.calls = 0
        self.last_response = None
        self.responses = []
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key
            not in {
                "OPENAI_API_KEY",
                "CODEX_API_KEY",
                "OPENAI_BASE_URL",
                "CODEX_ACCESS_TOKEN",
            }
        }
        auth = subprocess.run(
            [self.executable, "login", "status"],
            capture_output=True,
            text=True,
            env=self.environment,
            timeout=10,
        )
        if auth.returncode or "ChatGPT" not in auth.stdout + auth.stderr:
            raise ValueError("Codex must be signed in using ChatGPT: run codex login")

    def complete(self, messages, *, tools=None, stop=None, timeout=None):
        names = [tool["function"]["name"] for tool in tools or []]
        call_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"name": {"type": "string"}, "arguments": {"type": "string"}},
            "required": ["name", "arguments"],
        }
        if names:
            call_schema["properties"]["name"]["enum"] = names
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"},
                "tool_calls": {
                    "type": "array",
                    "items": call_schema,
                    "maxItems": 1 if names else 0,
                },
            },
            "required": ["text", "tool_calls"],
        }
        prompt = (
            "Act only as the language-model completion transport for the conversation below. "
            "Do not inspect files, run shell commands, browse, or use Codex tools. "
            "Return the requested assistant response inside the schema's text field, preserving "
            "all Python/JSON code fences. If external functions are offered, you may instead "
            "request one by filling tool_calls with its name and JSON-encoded arguments. "
            "Otherwise return an empty tool_calls array. Follow the final conversation instruction.\n"
            + json.dumps(
                {"messages": messages, "external_functions": tools or []}, ensure_ascii=False
            )
        )
        self.calls += 1
        self.last_response = None
        with tempfile.TemporaryDirectory(prefix="text2bim-codex-") as folder:
            root = Path(folder)
            (root / "schema.json").write_text(json.dumps(schema))
            command = [
                self.executable,
                "exec",
                "--ignore-user-config",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "--ephemeral",
                "--json",
                "--color",
                "never",
                "--output-schema",
                str(root / "schema.json"),
                "--output-last-message",
                str(root / "response.json"),
            ]
            if self.config.model:
                command.extend(["--model", self.config.model])
            if self.config.reasoning_effort:
                command.extend(
                    ["-c", "model_reasoning_effort=" + json.dumps(self.config.reasoning_effort)]
                )
            command.append("-")
            with tempfile.TemporaryFile() as events, tempfile.TemporaryFile() as errors:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=events,
                    stderr=errors,
                    text=True,
                    cwd=root,
                    env=self.environment,
                    start_new_session=True,
                )
                try:
                    process.communicate(
                        prompt,
                        timeout=self.config.timeout
                        if timeout is None
                        else max(0, min(timeout, self.config.timeout)),
                    )
                except subprocess.TimeoutExpired as error:
                    kill_process(process)
                    raise TimeoutError("Codex completion timed out") from error
                finally:
                    if process.stdin is not None:
                        process.stdin.close()
                if process.returncode:
                    errors.seek(0)
                    raise RuntimeError(
                        "Codex completion failed: " + errors.read(4000).decode(errors="replace")
                    )
                events.seek(0)
                usage = {}
                for line in events:
                    event = json.loads(line)
                    if event.get("type") == "turn.completed":
                        usage = event.get("usage", {})
                    if event.get("type") == "item.completed" and event.get("item", {}).get(
                        "type"
                    ) in {
                        "command_execution",
                        "mcp_tool_call",
                        "web_search",
                        "file_change",
                    }:
                        raise RuntimeError(
                            "Codex used an internal tool instead of returning a completion"
                        )
            data = json.loads((root / "response.json").read_text())
        calls = tuple(
            ToolCall("codex-" + uuid4().hex, call["name"], call["arguments"])
            for call in data["tool_calls"]
        )
        if any(call.name not in names for call in calls):
            raise ValueError("Codex requested an unavailable external function")
        input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
        response = LLMResponse(
            text=data["text"],
            model=self.model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
            if input_tokens is not None and output_tokens is not None
            else None,
            tool_calls=calls,
        )
        self.last_response = response
        self.responses.append(response)
        return response

    def generate_one(self, prompt, stop=None):
        return self.complete([{"role": "user", "content": prompt}], stop=stop).text

    def close(self):
        pass
