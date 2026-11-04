"""Massing geometry and tools for the Text2BIM adaptation."""

from .config import GenerationTask, RunConfig
from .scene import Scene, SceneSnapshot
from .tools import MassingTools

__all__ = [
    "MassingTools",
    "Scene",
    "SceneSnapshot",
    "GenerationTask",
    "RunConfig",
    "GenerationResult",
    "generate",
]
__version__ = "0.1.0"


def __getattr__(name):
    if name in {"GenerationResult", "generate"}:
        from . import workflow

        return getattr(workflow, name)
    raise AttributeError(name)
