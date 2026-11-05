"""Candidate reports are attached to immutable snapshots, never to a mutable scene."""

import json
from dataclasses import dataclass, replace
from pathlib import Path

from ._worker import encode_state
from .checkpoint import checkpoint_code
from .runtime import EvaluationFailed, evaluate_bounded, write_json
from .scene import Scene, SceneSnapshot


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    snapshot: SceneSnapshot
    source_code: str
    state_json: str = '{"kind":"dict","value":[]}'
    report_json: str | None = None
    actions_json: str = "[]"
    attempt: int = 0
    boundary: str = "commit"
    tool_units: str = "mm"

    @property
    def code(self):
        return checkpoint_code()

    def checkpoint(self):
        actions = json.loads(self.actions_json)
        return {
            "schema": 1,
            "snapshot": self.snapshot.to_dict(),
            "origin_snapshot": Scene().snapshot().to_dict() if actions else self.snapshot.to_dict(),
            "state": json.loads(self.state_json),
            "actions": actions,
            "source_code": self.source_code,
            "boundary": self.boundary,
            "attempt": self.attempt,
            "tool_units": self.tool_units,
        }

    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "massing": self.snapshot.to_massing(),
            "report": json.loads(self.report_json) if self.report_json is not None else None,
            "code": self.code,
            "source_code": self.source_code,
            "checkpoint_boundary": self.boundary,
        }


class CandidateArchive:
    def __init__(self, root: Path, evaluator, context, budget, trace):
        self.root, self.evaluator, self.context = root, evaluator, context
        self.budget, self.trace = budget, trace
        self.candidates: dict[str, Candidate] = {}
        self.selected_id: str | None = None

    def commit(
        self,
        snapshot: SceneSnapshot,
        code: str,
        state=None,
        *,
        actions=None,
        attempt=0,
        boundary="commit",
    ) -> str:
        self.budget.check()
        snapshot = Scene.from_snapshot(snapshot).snapshot()
        if not snapshot.to_massing():
            raise ValueError("A candidate must contain at least one extrusion")
        state = encode_state({}) if state is None else state
        candidate_id = f"c{len(self.candidates) + 1:04d}"
        candidate = Candidate(
            candidate_id,
            snapshot,
            code,
            json.dumps(state, allow_nan=False),
            actions_json=json.dumps(actions or [], allow_nan=False),
            attempt=attempt,
            boundary=boundary,
            tool_units=self.budget.config.tool_units,
        )
        directory = self.root / "candidates" / candidate_id
        directory.mkdir(parents=True)
        self._write_checkpoint(candidate)
        self.candidates[candidate_id] = candidate
        self.trace.add("commit_candidate", candidate_id=candidate_id)
        return candidate_id

    def _write_checkpoint(self, candidate):
        directory = self.root / "candidates" / candidate.candidate_id
        write_json(directory / "snapshot.json", candidate.snapshot.to_dict())
        write_json(directory / "massing.json", candidate.snapshot.to_massing())
        write_json(directory / "state.json", json.loads(candidate.state_json))
        write_json(directory / "checkpoint.json", candidate.checkpoint())
        (directory / "code.py").write_text(candidate.code)
        (directory / "source_code.py").write_text(candidate.source_code)

    def complete_execution(self, executor):
        """Seal continuation variables only for checkpoints at this successful final scene.

        The immutable geometry/report stay untouched. A checkpoint before an
        uncommitted edit keeps its commit-time state and operation-journal prefix.
        """
        for candidate_id, candidate in list(self.candidates.items()):
            if candidate.snapshot != executor.snapshot:
                continue
            candidate = replace(
                candidate,
                state_json=json.dumps(executor.state, allow_nan=False),
                actions_json=json.dumps(executor.actions, allow_nan=False),
                source_code="\n\n".join(executor.codes),
                boundary="script_complete",
                attempt=executor.attempts,
            )
            self.candidates[candidate_id] = candidate
            self._write_checkpoint(candidate)
            self.trace.add("checkpoint_completed", candidate_id=candidate_id)

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
