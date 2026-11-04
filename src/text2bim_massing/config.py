"""Configuration and explicit task context for one independent generation run."""

from dataclasses import dataclass, field

from .geometry import finite_number


@dataclass(frozen=True)
class GenerationTask:
    instruction: str
    context: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.instruction, str) or not self.instruction.strip():
            raise ValueError("A nonempty task instruction is required")
        if not isinstance(self.context, dict):
            raise TypeError("Task context must be a dictionary")


@dataclass(frozen=True)
class RunConfig:
    max_iterations: int = 3
    max_llm_calls: int = 20
    max_evaluations: int = 6
    max_seconds: float = 300
    execution_timeout: float = 15
    evaluation_timeout: float = 60
    max_repairs: int = 2
    tool_units: str = "mm"
    max_code_bytes: int = 65536
    max_output_bytes: int = 65536
    max_state_bytes: int = 2_000_000
    memory_limit_mb: int = 1024
    input_price_per_million: float | None = None
    output_price_per_million: float | None = None

    def __post_init__(self):
        for name in (
            "max_iterations",
            "max_llm_calls",
            "max_evaluations",
            "max_repairs",
            "max_code_bytes",
            "max_output_bytes",
            "max_state_bytes",
            "memory_limit_mb",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        for name in ("max_code_bytes", "max_output_bytes", "max_state_bytes", "memory_limit_mb"):
            if getattr(self, name) == 0:
                raise ValueError(f"{name} must be positive")
        for name in ("max_seconds", "execution_timeout", "evaluation_timeout"):
            if finite_number(getattr(self, name), name) <= 0:
                raise ValueError(f"{name} must be positive")
        for name in ("input_price_per_million", "output_price_per_million"):
            value = getattr(self, name)
            if value is not None and finite_number(value, name) < 0:
                raise ValueError(f"{name} must be nonnegative")
        if self.tool_units not in {"m", "mm"}:
            raise ValueError("tool_units must be m or mm")
