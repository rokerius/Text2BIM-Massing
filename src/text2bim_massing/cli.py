"""JSON-configured generation entrypoint with optional pinned Maslov checkout."""

import argparse
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

from .adapters import SampleMetricAdapter, SampleProcessorAdapter
from .config import GenerationTask, RunConfig
from .runtime import write_json
from .workflow import generate

MASLOV_COMMIT = "607ff1fcf80477787409522d93e18e42ac1436cf"


def load_evaluator(spec):
    module_name, attribute = spec["factory"].split(":", 1)
    factory = getattr(importlib.import_module(module_name), attribute)
    kind = spec.get("kind", "callable")
    if kind == "callable":
        if spec.get("kwargs"):
            return factory(**spec["kwargs"])
        return factory
    component = factory(**spec.get("kwargs", {}))
    common = {key: spec[key] for key in ("building_key", "layout", "building_id") if key in spec}
    if kind == "metric":
        return SampleMetricAdapter(component, report_key=spec["report_key"], **common)
    if kind == "processor":
        return SampleProcessorAdapter(component, report_keys=tuple(spec["report_keys"]), **common)
    raise ValueError(f"Unknown evaluator kind: {kind}")


def connect_maslov(path):
    repo = Path(path).resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != MASLOV_COMMIT:
        raise ValueError(f"Expected Maslov commit {MASLOV_COMMIT}, found {actual}")
    if subprocess.run(
        ["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", "src"], check=False
    ).returncode:
        raise ValueError("Maslov src/ must match the pinned commit")
    sys.path.insert(0, str(repo))


def load_llm(spec):
    spec = dict(spec)
    provider = spec.pop("provider", "openai")
    if provider == "codex":
        from .codex_client import CodexCLIClient, CodexConfig

        return CodexCLIClient(CodexConfig(**spec))
    if provider == "openai":
        from .llm import LLMConfig, OpenAIClient

        spec.setdefault("model", os.environ.get("TEXT2BIM_MODEL") or os.environ.get("OPENAI_MODEL"))
        if "base_url" not in spec and os.environ.get("OPENAI_BASE_URL"):
            spec["base_url"] = os.environ["OPENAI_BASE_URL"]
        return OpenAIClient(LLMConfig(**spec))
    raise ValueError(f"Unknown LLM provider: {provider}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="text2bim-massing")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("generate", help="Generate and externally evaluate massing")
    run.add_argument("--config", required=True, type=Path)
    tasks = run.add_mutually_exclusive_group(required=True)
    tasks.add_argument("--task")
    tasks.add_argument("--task-file", type=Path)
    run.add_argument("--context", type=Path)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--maslov-repo", default=os.environ.get("MASSING_GENERATION_REPO"))
    args = parser.parse_args(argv)
    client = None
    try:
        spec = json.loads(args.config.read_text())
        if args.maslov_repo:
            connect_maslov(args.maslov_repo)
        evaluator = load_evaluator(spec["evaluator"])
        if args.task_file:
            data = json.loads(args.task_file.read_text())
            task = GenerationTask(**data)
        else:
            context = json.loads(args.context.read_text()) if args.context else {}
            task = GenerationTask(args.task, context)
        client = load_llm(spec.get("llm", {}))
        result = generate(task, evaluator, client, RunConfig(**spec.get("run", {})), args.output)
        write_json(args.output / "runner_config.json", spec)
        print(
            json.dumps(
                {
                    "status": result.status,
                    "reason": result.reason,
                    "output_dir": result.output_dir,
                    "selected_candidate_id": result.selected_candidate["candidate_id"]
                    if result.selected_candidate
                    else None,
                    "costs": result.costs,
                },
                ensure_ascii=False,
            )
        )
        return (
            0 if result.status == "completed" else 2 if result.status == "budget_exhausted" else 1
        )
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        ImportError,
        subprocess.SubprocessError,
    ) as error:
        print(f"text2bim-massing: {error}", file=sys.stderr)
        return 1
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
