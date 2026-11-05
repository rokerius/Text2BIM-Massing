"""JSON-only execution worker. Generated code runs through the original AST interpreter."""

import ast
import contextlib
import io
import json
import math
import sys
import types

from ._vendor.text2bim.python_interpreter import evaluate
from .scene import Scene, SceneSnapshot
from .tools import MassingTools


class LimitedOutput(io.StringIO):
    def __init__(self, limit):
        super().__init__()
        self.limit = limit
        self.used = 0

    def write(self, value):
        self.used += len(value.encode())
        if self.used > self.limit:
            raise ValueError("Execution output limit exceeded")
        return super().write(value)


def encode_state(value, depth=0):
    if depth > 100:
        raise ValueError("Interpreter state is too deeply nested")
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if isinstance(value, types.ModuleType) and value is math:
        return {"kind": "module", "value": "math"}
    if callable(value) and getattr(value, "__module__", None) == "math":
        name = getattr(value, "__name__", "")
        if name and not name.startswith("_") and getattr(math, name, None) is value:
            return {"kind": "math_member", "value": name}
    if type(value) in (list, tuple, set, dict):
        items = value.items() if isinstance(value, dict) else value
        if isinstance(value, dict):
            items = [[encode_state(k, depth + 1), encode_state(v, depth + 1)] for k, v in items]
        else:
            items = [encode_state(item, depth + 1) for item in items]
        return {"kind": type(value).__name__, "value": items}
    raise ValueError(f"Unsupported persistent state type: {type(value).__name__}")


def decode_state(value):
    if not isinstance(value, dict):
        return value
    kind, items = value["kind"], value["value"]
    if kind == "module" and items == "math":
        return math
    if kind == "math_member" and not items.startswith("_"):
        return getattr(math, items)
    if kind == "dict":
        return {decode_state(k): decode_state(v) for k, v in items}
    constructors = {"list": list, "tuple": tuple, "set": set}
    return constructors[kind](decode_state(item) for item in items)


def validate_code(code):
    tree = ast.parse(code)
    forbidden = (
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.Lambda,
        ast.With,
        ast.AsyncWith,
        ast.AsyncFor,
        ast.Await,
        ast.Global,
        ast.Nonlocal,
    )
    for node in ast.walk(tree):
        if isinstance(node, forbidden):
            raise ValueError(f"Unsupported generated construct: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id.startswith("_"):
            raise ValueError("Private names are unavailable")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise ValueError("Private attributes are unavailable")
        if isinstance(node, ast.Import):
            if any(alias.name != "math" for alias in node.names):
                raise ValueError("Only math imports are available")
        if isinstance(node, ast.ImportFrom):
            if (
                node.level
                or node.module != "math"
                or any(a.name.startswith("_") or a.name == "*" for a in node.names)
            ):
                raise ValueError("Only explicit public math imports are available")
        if isinstance(node, ast.ExceptHandler) and node.name and node.name.startswith("_"):
            raise ValueError("Private names are unavailable")
    return tree


def main():
    protocol = sys.stdout

    def send(message):
        protocol.write(json.dumps(message, allow_nan=False) + "\n")
        protocol.flush()

    request = json.loads(sys.stdin.readline())
    output = LimitedOutput(request["max_output_bytes"])
    try:
        if sys.platform.startswith("linux"):
            import resource

            limit = request["memory_limit_mb"] * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        code = request["code"]
        if len(code.encode()) > request["max_code_bytes"]:
            raise ValueError("Generated code exceeds size limit")
        validate_code(code)
        scene = Scene.from_snapshot(SceneSnapshot(request["snapshot"]))
        state = decode_state(request["state"])
        actions, allocated_ids = [], []
        action_bytes = 0
        original_allocate = scene._allocate_id

        def allocate():
            object_id = original_allocate()
            allocated_ids.append(object_id)
            return object_id

        scene._allocate_id = allocate

        def record(name, function):
            def call(*args, **kwargs):
                nonlocal action_bytes
                start = len(allocated_ids)
                journal_start, previous_bytes = len(actions), action_bytes
                revision = scene._revision
                arguments, keywords = encode_state(args), encode_state(kwargs)
                try:
                    # A caught journal failure must leave no unrecorded scene mutation.
                    with scene.transaction():
                        result = function(*args, **kwargs)
                        if scene._revision == revision:
                            return result
                        action = {
                            "name": name,
                            "args": arguments,
                            "kwargs": keywords,
                            "ids": allocated_ids[start:],
                        }
                        size = len(json.dumps(action, allow_nan=False).encode())
                        if action_bytes + size > request["max_state_bytes"]:
                            raise ValueError("Checkpoint operation journal exceeds size limit")
                        actions.append(action)
                        action_bytes += size
                        return result
                except BaseException:
                    del allocated_ids[start:]
                    del actions[journal_start:]
                    action_bytes = previous_bytes
                    raise

            return call

        tools = {
            name: record(name, fn)
            for name, fn in MassingTools(scene, units=request["units"]).as_functions().items()
        }

        def rpc(action, **values):
            send({"event": action, **values})
            response = json.loads(sys.stdin.readline())
            if not response["ok"]:
                raise ValueError(response["error"])
            return response["value"]

        tools.update(
            {
                "commit_candidate": lambda: rpc(
                    "commit",
                    snapshot=scene.snapshot().json,
                    state=encode_state(state),
                    actions=actions,
                ),
                "evaluate": lambda candidate_id: rpc("evaluate", candidate_id=candidate_id),
                "select_candidate": lambda candidate_id: rpc("select", candidate_id=candidate_id),
            }
        )
        for name in (
            "print",
            "len",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "tuple",
            "set",
            "range",
            "enumerate",
            "zip",
            "sum",
            "min",
            "max",
            "abs",
            "round",
            "sorted",
            "reversed",
            "all",
            "any",
        ):
            import builtins

            tools[name] = getattr(builtins, name)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            _, state = evaluate(code, tools, state=state, chat_mode=True)
        encoded = encode_state(state)
        if len(json.dumps(encoded).encode()) > request["max_state_bytes"]:
            raise ValueError("Interpreter state exceeds size limit")
        snapshot = scene.snapshot().json
        if len(snapshot.encode()) > request["max_state_bytes"]:
            raise ValueError("Scene exceeds size limit")
        send(
            {
                "event": "result",
                "ok": True,
                "snapshot": snapshot,
                "state": encoded,
                "actions": actions,
                "stdout": output.getvalue(),
            }
        )
    except BaseException as error:
        send(
            {
                "event": "result",
                "ok": False,
                "error": f"{type(error).__name__}: {str(error)[:4000]}",
                "stdout": output.getvalue(),
            }
        )


if __name__ == "__main__":
    main()
