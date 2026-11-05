"""Run one transactional code attempt in a fresh process, preserving only accepted JSON state."""

import json
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

from ._worker import encode_state
from .config import RunConfig
from .scene import Scene, SceneSnapshot


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    error: str | None = None
    stdout: str = ""


def kill_process(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


class ProcessExecutor:
    def __init__(self, config: RunConfig, *, event_handler=None, remaining=None, on_success=None):
        self.config = config
        self.snapshot = Scene().snapshot()
        self.state = encode_state({})
        self.event_handler = event_handler
        self.remaining = remaining or (lambda: float("inf"))
        self.attempts = 0
        self.codes: list[str] = []
        self.actions: list[dict] = []
        self.on_success = on_success

    def execute(self, code: str) -> ExecutionResult:
        self.attempts += 1
        request = {
            "code": code,
            "snapshot": self.snapshot.json,
            "state": self.state,
            "units": self.config.tool_units,
            "max_code_bytes": self.config.max_code_bytes,
            "max_output_bytes": self.config.max_output_bytes,
            "max_state_bytes": self.config.max_state_bytes,
            "memory_limit_mb": self.config.memory_limit_mb,
        }
        if len(code.encode()) > self.config.max_code_bytes:
            return ExecutionResult(False, "Generated code exceeds size limit")
        deadline = time.monotonic() + min(self.config.execution_timeout, self.remaining())
        with tempfile.TemporaryDirectory(prefix="text2bim-exec-") as cwd:
            environment = {
                key: os.environ[key] for key in ("PATH", "SYSTEMROOT") if key in os.environ
            }
            environment.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
            with tempfile.TemporaryFile() as errors:
                process = subprocess.Popen(
                    [sys.executable, "-I", "-m", "text2bim_massing._worker"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=errors,
                    env=environment,
                    cwd=cwd,
                    start_new_session=True,
                )
                selector = selectors.DefaultSelector()
                selector.register(process.stdout, selectors.EVENT_READ)
                buffer = b""
                try:
                    process.stdin.write((json.dumps(request, allow_nan=False) + "\n").encode())
                    process.stdin.flush()
                    while True:
                        remaining = min(deadline - time.monotonic(), self.remaining())
                        if remaining <= 0:
                            return ExecutionResult(False, "Execution timed out")
                        if not selector.select(min(remaining, 0.1)):
                            continue
                        chunk = os.read(process.stdout.fileno(), 65536)
                        if not chunk:
                            errors.seek(0)
                            return ExecutionResult(
                                False,
                                "Worker exited: " + errors.read(4000).decode(errors="replace"),
                            )
                        buffer += chunk
                        if (
                            len(buffer)
                            > self.config.max_state_bytes * 4 + self.config.max_output_bytes
                        ):
                            return ExecutionResult(False, "Worker response exceeds size limit")
                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            message = json.loads(line)
                            if message["event"] == "result":
                                if not message["ok"]:
                                    return ExecutionResult(
                                        False, message["error"], message["stdout"]
                                    )
                                # Validate before accepting either scene or interpreter variables.
                                snapshot = Scene.from_snapshot(
                                    SceneSnapshot(message["snapshot"])
                                ).snapshot()
                                self.snapshot, self.state = snapshot, message["state"]
                                self.actions.extend(message["actions"])
                                self.codes.append(code)
                                if self.on_success is not None:
                                    self.on_success()
                                return ExecutionResult(True, stdout=message["stdout"])
                            started = time.monotonic()
                            try:
                                if self.event_handler is None:
                                    raise ValueError(
                                        "Candidate tools require a generation workflow"
                                    )
                                value = self.event_handler(message, code)
                                response = {"ok": True, "value": value}
                            except (ValueError, KeyError) as error:
                                response = {"ok": False, "error": str(error)}
                            deadline += time.monotonic() - started
                            process.stdin.write(
                                (json.dumps(response, allow_nan=False) + "\n").encode()
                            )
                            process.stdin.flush()
                finally:
                    selector.close()
                    kill_process(process)
                    process.stdin.close()
                    process.stdout.close()
