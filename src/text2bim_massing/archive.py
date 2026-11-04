"""Candidate reports are attached to immutable snapshots, never to a mutable scene."""

import json
from dataclasses import dataclass, replace
from pathlib import Path

from .runtime import EvaluationFailed, evaluate_bounded, write_json
from .scene import Scene, SceneSnapshot


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    snapshot: SceneSnapshot
    code: str
    state_json: str = "null"
    report_json: str | None = None

    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "massing": self.snapshot.to_massing(),
            "report": json.loads(self.report_json) if self.report_json is not None else None,
            "code": self.code,
        }


class CandidateArchive:
    def __init__(self, root: Path, evaluator, context, budget, trace):
        self.root, self.evaluator, self.context = root, evaluator, context
        self.budget, self.trace = budget, trace
        self.candidates: dict[str, Candidate] = {}
        self.selected_id: str | None = None

    def commit(self, snapshot: SceneSnapshot, code: str, state=None) -> str:
        self.budget.check()
        snapshot = Scene.from_snapshot(snapshot).snapshot()
        if not snapshot.to_massing():
            raise ValueError("A candidate must contain at least one extrusion")
        candidate_id = f"c{len(self.candidates) + 1:04d}"
        candidate = Candidate(candidate_id, snapshot, code, json.dumps(state, allow_nan=False))
        directory = self.root / "candidates" / candidate_id
        directory.mkdir(parents=True)
        write_json(directory / "snapshot.json", snapshot.to_dict())
        write_json(directory / "massing.json", snapshot.to_massing())
        write_json(directory / "state.json", state)
        (directory / "code.py").write_text(code)
        self.candidates[candidate_id] = candidate
        self.trace.add("commit_candidate", candidate_id=candidate_id)
        return candidate_id

    def evaluate(self, candidate_id: str):
        candidate = self.candidates[candidate_id]
        if candidate.report_json is not None:
            self.trace.add("cached_report", candidate_id=candidate_id)
            return json.loads(candidate.report_json)
        self.budget.evaluation()
        attempt = self.budget.evaluations
        self.trace.add("evaluation_request", candidate_id=candidate_id, attempt=attempt)
        directory = self.root / "candidates" / candidate_id
        try:
            report = evaluate_bounded(
                self.evaluator,
                candidate.snapshot.to_massing(),
                self.context,
                min(self.budget.config.evaluation_timeout, self.budget.remaining()),
            )
        except EvaluationFailed as error:
            self.trace.add(
                "evaluation_error", candidate_id=candidate_id, attempt=attempt, error=str(error)
            )
            write_json(directory / f"error-{attempt}.json", {"error": str(error)})
            self.budget.check()
            raise
        report_json = json.dumps(report, allow_nan=False, sort_keys=True)
        self.candidates[candidate_id] = replace(candidate, report_json=report_json)
        write_json(directory / "report.json", report)
        self.trace.add(
            "evaluation_report", candidate_id=candidate_id, attempt=attempt, report=report
        )
        self.budget.check()
        return json.loads(report_json)

    def select(self, candidate_id: str):
        candidate = self.candidates[candidate_id]
        if candidate.report_json is None:
            raise ValueError("Only an evaluated candidate can be selected")
        self.selected_id = candidate_id
        self.trace.add("select_candidate", candidate_id=candidate_id)
        return candidate_id
