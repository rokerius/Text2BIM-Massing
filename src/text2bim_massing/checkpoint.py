"""Replay captured geometry operations without re-running LLM code or an evaluator."""

import json
from dataclasses import dataclass
from pathlib import Path

from .scene import Scene, SceneSnapshot
from .tools import MassingTools


def checkpoint_code():
    """Small executable entrypoint shared by candidate and selected-code exports."""
    return (
        "from pathlib import Path\n"
        "import json\n"
        "from text2bim_massing.checkpoint import replay_checkpoint\n\n"
        'checkpoint = replay_checkpoint(Path(__file__).with_name("checkpoint.json"))\n'
        "print(json.dumps(checkpoint.scene.to_massing(), allow_nan=False))\n"
    )


@dataclass(frozen=True)
class ReplayedCheckpoint:
    scene: Scene
    state: dict


def replay_checkpoint(path) -> ReplayedCheckpoint:
    """Rebuild the exact scene/IDs and restore data variables from an archived checkpoint.

    Only recorded MassingTools calls execute. Original source is provenance, not a
    replay program: failed/uncommitted tails and external evaluations never run.
    """
    from ._worker import decode_state

    data = json.loads(Path(path).read_text())
    if data.get("schema") != 1:
        raise ValueError("Unsupported checkpoint schema")
    scene = Scene.from_snapshot(SceneSnapshot(json.dumps(data["origin_snapshot"])))
    tools = MassingTools(scene, units=data["tool_units"]).as_functions()
    for action in data["actions"]:
        ids = iter(action["ids"])

        def allocate():
            try:
                return next(ids)
            except StopIteration:
                raise ValueError("Checkpoint is missing an allocated object ID") from None

        scene._allocate_id = allocate
        tools[action["name"]](*decode_state(action["args"]), **decode_state(action["kwargs"]))
        if next(ids, None) is not None:
            raise ValueError("Checkpoint has unused allocated object IDs")
    expected = Scene.from_snapshot(SceneSnapshot(json.dumps(data["snapshot"]))).snapshot()
    if scene.snapshot() != expected:
        raise ValueError("Replayed geometry does not match the checkpoint snapshot")
    # The replay allocator is local to this reconstruction; further edits use fresh IDs.
    scene.__dict__.pop("_allocate_id", None)
    state = decode_state(data["state"])
    if not isinstance(state, dict):
        raise ValueError("Checkpoint state must be a dictionary")
    return ReplayedCheckpoint(scene, state)
