"""Independent single-building pilot; leave Maslov's method and shared launcher unchanged."""

import argparse
import hashlib
import json
import subprocess
from copy import deepcopy
from importlib.metadata import distribution
from pathlib import Path
from urllib.parse import unquote, urlparse

from text2bim_massing import GenerationTask, RunConfig, generate
from text2bim_massing.cli import MASLOV_COMMIT, connect_maslov, load_evaluator, load_llm
from text2bim_massing.runtime import write_json


def verify_package(expected):
    """Accept a pinned VCS install or an editable checkout with identical package sources."""
    if len(expected) != 40 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("package_commit must be a complete Git SHA")
    package = distribution("text2bim-massing")
    origin = json.loads(package.read_text("direct_url.json") or "{}")
    if origin.get("vcs_info", {}).get("commit_id") == expected:
        return {"commit": expected, "installation": "vcs", "version": package.version}
    if origin.get("dir_info", {}).get("editable"):
        checkout = Path(unquote(urlparse(origin["url"]).path))
        command = ["git", "-C", str(checkout)]
        subprocess.run(
            command + ["diff", "--exit-code", expected, "--", "src", "pyproject.toml"],
            check=True,
            capture_output=True,
        )
        untracked = subprocess.check_output(
            command + ["ls-files", "--others", "--exclude-standard", "--", "src"], text=True
        )
        if untracked.strip():
            raise ValueError("Editable package has untracked runtime sources")
        return {
            "commit": expected,
            "installation": "editable-identical",
            "version": package.version,
        }
    raise ValueError("Install text2bim-massing from the configured Git commit")


def prepare_rows(data, sample_ids=None, fallback_id=None):
    """Only public task inputs enter the model; never pass reference building/pred_massing."""
    if isinstance(data, dict):
        data = [dict(data, id=data.get("id", fallback_id))]
    if not isinstance(data, list) or not data:
        raise ValueError("Dataset must be a nonempty JSON row or list of rows")
    prepared, seen = [], set()
    selected = set(sample_ids or [])
    for row in data:
        if not isinstance(row, dict) or row.get("id") is None:
            raise ValueError("Every dataset row must have an id")
        identifier = str(row["id"])
        if identifier in seen:
            raise ValueError(f"Duplicate sample id: {identifier}")
        seen.add(identifier)
        if selected and identifier not in selected:
            continue
        if not isinstance(row.get("site_contour"), list) or not row["site_contour"]:
            raise ValueError(f"Sample {identifier} needs site_contour")
        context = deepcopy({k: row[k] for k in ("id", "site_contour", "requirements") if k in row})
        requirements = context.get("requirements")
        if requirements is not None:
            if (
                not isinstance(requirements, list)
                or len(requirements) != 1
                or not isinstance(requirements[0], dict)
                or requirements[0].get("id") is None
            ):
                raise ValueError("This pilot requires exactly one building requirement with an id")
        prepared.append(context)
    if selected - seen:
        raise ValueError(f"Unknown sample ids: {sorted(selected - seen)}")
    if not prepared:
        raise ValueError("Sample selection is empty")
    return prepared


class ConfiguredMetrics:
    """Reuse configured original metrics; preserve separate report fields without a score."""

    def __init__(self, specs, building_id):
        if not specs:
            raise ValueError("At least one evaluator must be configured")
        self.components = [load_evaluator(dict(s, building_id=building_id)) for s in specs]

    def __call__(self, massing, context):
        report = {}
        for component in self.components:
            partial = component(massing, context)
            if report.keys() & partial.keys():
                raise ValueError("Evaluator report keys must be unique")
            report.update(partial)
        return report


def run_rows(spec, rows, output, client):
    config = RunConfig(**spec["run"])
    submission, reports = [], []
    for index, context in enumerate(rows):
        requirement = context.get("requirements")
        building_id = requirement[0]["id"] if requirement else spec["building_id"]
        evaluator = ConfiguredMetrics(spec["evaluators"], building_id)
        directory = output / "tasks" / f"{index:04d}"
        result = generate(
            GenerationTask(spec["instruction"], context), evaluator, client, config, directory
        )
        candidate = result.selected_candidate
        row = deepcopy(context)
        row["pred_massing"] = (
            [{"id": building_id, "massing": candidate["massing"]}] if candidate else []
        )
        submission.append(row)
        reports.append(
            {
                "id": context["id"],
                "status": result.status,
                "reason": result.reason,
                "candidate_id": candidate["candidate_id"] if candidate else None,
                "metrics": candidate["report"] if candidate else None,
                "costs": result.costs,
                "artifacts": directory.relative_to(output).as_posix(),
            }
        )
        # Persist after each independent task, including a partial/budget result.
        write_json(output / "submit.json", submission)
        write_json(output / "report.json", reports)
        write_json(
            output / "result.json",
            {
                "experiment": "text2bim_adapted_single_building_pilot",
                "samples": len(rows),
                "processed": len(reports),
                "completed": sum(r["status"] == "completed" for r in reports),
                "selected": sum(r["candidate_id"] is not None for r in reports),
                "metric_aggregation": None,
            },
        )
    return 0 if all(r["status"] == "completed" for r in reports) else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("pilot.json"))
    parser.add_argument("--maslov-repo", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--sample-id", action="append", dest="sample_ids")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    spec = json.loads(args.config.read_text())
    package = verify_package(spec["package_commit"])
    connect_maslov(args.maslov_repo)
    rows = prepare_rows(
        json.loads(args.dataset.read_text()), args.sample_ids, fallback_id=args.dataset.stem
    )
    if not spec["llm"].get("model"):
        raise ValueError("An explicit model is required for the experiment")
    # Validate all per-task bindings before the first billable/limited model call.
    RunConfig(**spec["run"])
    for context in rows:
        requirements = context.get("requirements")
        building_id = requirements[0]["id"] if requirements else spec["building_id"]
        ConfiguredMetrics(spec["evaluators"], building_id)
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory must be empty; this pilot does not resume")
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "runner_config.json", spec)
    write_json(
        output / "experiment_provenance.json",
        {
            "package": package,
            "maslov_commit": MASLOV_COMMIT,
            "dataset": str(args.dataset.resolve()),
            "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "sample_ids": [row["id"] for row in rows],
            "context_fields": ["id", "site_contour", "requirements"],
        },
    )
    client = load_llm(spec["llm"])
    try:
        return run_rows(spec, rows, output, client)
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
