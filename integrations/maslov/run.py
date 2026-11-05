"""Generate and externally evaluate one building with explicit or source requirements."""

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
from text2bim_massing.geometry import finite_number, geometry_from_polygons
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


def validate_requirement(requirement):
    """Require stated numeric data; zero is unknown, never a hidden pilot default."""
    identifier = requirement.get("id")
    if (
        isinstance(identifier, bool)
        or not isinstance(identifier, (str, int))
        or isinstance(identifier, str)
        and not identifier.strip()
    ):
        raise ValueError("Requirement id must be a nonempty string or integer")
    values = {}
    for key in ("n_floors", "floor_height", "total_area"):
        if key not in requirement:
            raise ValueError(f"Requirement {identifier!r}: missing {key}; no defaults are applied")
        value = finite_number(requirement[key], key)
        if value <= 0:
            raise ValueError(f"Requirement {identifier!r}: {key} must be stated and positive")
        values[key] = value
    if not values["n_floors"].is_integer():
        raise ValueError("n_floors must be an integer for the original floor-count metric")
    return values


def bind_task(context, spec):
    """Construct one task from source data and record every numerical target's origin."""
    mode = spec.get("task_mode", "pilot")
    if mode not in {"pilot", "requirements"}:
        raise ValueError(f"Unknown task_mode: {mode}")
    effective = deepcopy(context)
    if mode == "pilot":
        return GenerationTask(spec["instruction"], effective), {"mode": mode}
    source = effective.get("requirements")
    if not isinstance(source, list) or len(source) != 1 or not isinstance(source[0], dict):
        raise ValueError("requirements mode needs exactly one building requirement")
    geometry_from_polygons(effective["site_contour"])
    # Reuse pure data helpers; no search, defaults or site subdivision is executed.
    from subtractive_additive_massing.brief import BuildingBrief, with_canonical_area

    normalized = with_canonical_area(source)
    values = validate_requirement(normalized[0])
    brief = BuildingBrief.from_requirement(normalized[0])
    targets = {
        "building_id": normalized[0]["id"],
        "n_floors": values["n_floors"],
        "floor_height_m": values["floor_height"],
        "total_area_m2": values["total_area"],
        "building_height_m": finite_number(brief.height, "derived building height"),
        "mean_floor_area_m2": finite_number(brief.footprint, "derived mean floor area"),
    }
    effective["requirements"] = normalized
    binding = {
        "mode": mode,
        "schema": "single_building_requirements_v1",
        "normalizer": "subtractive_additive_massing.brief.with_canonical_area",
        "source_commit": MASLOV_COMMIT,
        "source_requirements": deepcopy(source),
        "effective_requirements": deepcopy(normalized),
        "source_fields": {
            "n_floors": ["requirements[0].n_floors"],
            "floor_height_m": ["requirements[0].floor_height"],
            "total_area_m2": [
                f"requirements[0].{key}"
                for key in ("total_area", "usable_area")
                if source[0].get(key) is not None
            ],
        },
        "derived_fields": {
            "building_height_m": "n_floors * floor_height_m",
            "mean_floor_area_m2": "total_area_m2 / n_floors",
        },
        "defaults_applied": {},
        "targets": targets,
    }
    instruction = spec["instruction"] + "\nTargets resolved from this sample's requirements:\n"
    instruction += json.dumps(targets, ensure_ascii=False, allow_nan=False)
    return GenerationTask(instruction, effective), binding


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
    tasks = [bind_task(context, spec) for context in rows]
    # Reject any unsupported row or bad metric binding before calling the model for the first row.
    evaluators = []
    for task, _ in tasks:
        requirement = task.context.get("requirements")
        building_id = requirement[0]["id"] if requirement else spec["building_id"]
        evaluators.append(ConfiguredMetrics(spec["evaluators"], building_id))
    submission, reports = [], []
    for index, ((task, binding), evaluator) in enumerate(zip(tasks, evaluators, strict=True)):
        context = task.context
        requirement = context.get("requirements")
        building_id = requirement[0]["id"] if requirement else spec["building_id"]
        directory = output / "tasks" / f"{index:04d}"
        result = generate(task, evaluator, client, config, directory)
        write_json(directory / "task_binding.json", binding)
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
                "experiment": spec.get("experiment", "text2bim_adapted_single_building_pilot"),
                "task_mode": spec.get("task_mode", "pilot"),
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
    parser.add_argument(
        "--sample",
        "--dataset",
        dest="dataset",
        type=Path,
        metavar="FILE",
        required=True,
        help="JSON sample or list of samples; no dataset split is required",
    )
    parser.add_argument("--sample-id", action="append", dest="sample_ids")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Validate and save task bindings without LLM calls",
    )
    args = parser.parse_args(argv)
    spec = json.loads(args.config.read_text())
    package = verify_package(spec["package_commit"])
    connect_maslov(args.maslov_repo)
    if (
        spec.get("task_mode") == "requirements"
        and subprocess.run(
            [
                "git",
                "-C",
                str(args.maslov_repo),
                "diff",
                "--quiet",
                "HEAD",
                "--",
                "subtractive_additive_massing/brief.py",
                "subtractive_additive_massing/__init__.py",
            ],
            check=False,
        ).returncode
    ):
        raise ValueError("Maslov data helpers must match the pinned commit")
    dataset_bytes = args.dataset.read_bytes()
    rows = prepare_rows(json.loads(dataset_bytes), args.sample_ids, fallback_id=args.dataset.stem)
    if not spec["llm"].get("model"):
        raise ValueError("An explicit model is required for the experiment")
    # Validate all per-task bindings before the first billable/limited model call.
    RunConfig(**spec["run"])
    bindings = []
    for context in rows:
        task, binding = bind_task(context, spec)
        requirements = task.context.get("requirements")
        building_id = requirements[0]["id"] if requirements else spec["building_id"]
        ConfiguredMetrics(spec["evaluators"], building_id)
        bindings.append({"id": context["id"], **binding})
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory must be empty; this pilot does not resume")
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "runner_config.json", spec)
    write_json(output / "task_bindings.json", bindings)
    write_json(
        output / "experiment_provenance.json",
        {
            "package": package,
            "maslov_commit": MASLOV_COMMIT,
            "dataset": str(args.dataset.resolve()),
            "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "sample_ids": [row["id"] for row in rows],
            "context_fields": ["id", "site_contour", "requirements"],
            "task_mode": spec.get("task_mode", "pilot"),
        },
    )
    if args.prepare_only:
        prepared = {
            "status": "prepared",
            "samples": len(rows),
            "task_mode": spec.get("task_mode", "pilot"),
        }
        write_json(output / "preparation.json", prepared)
        print(json.dumps(prepared))
        return 0
    client = load_llm(spec["llm"])
    try:
        return run_rows(spec, rows, output, client)
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
