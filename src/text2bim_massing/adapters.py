"""Explicit input layouts for Maslov's existing mesh, metric, and processor components."""

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Literal

from .geometry import normalize_massing

Layout = Literal["extrusions", "building", "buildings"]


def as_building(massing, *, building_id="generated") -> dict:
    return {"id": building_id, "massing": normalize_massing(massing)}


def as_buildings(massing, *, building_id="generated") -> list[dict]:
    return [as_building(massing, building_id=building_id)]


def build_sample(
    massing, context, *, layout: Layout, building_key="building", building_id="generated"
):
    """Copy context and inject the exact layout required by one configured component."""
    sample = deepcopy(context)
    if not isinstance(sample, dict):
        raise TypeError("context must be a dictionary")
    if layout == "extrusions":
        building = normalize_massing(massing)
    elif layout == "building":
        building = as_building(massing, building_id=building_id)
    elif layout == "buildings":
        building = as_buildings(massing, building_id=building_id)
    else:
        raise ValueError(f"Unknown sample layout: {layout}")
    sample[building_key] = building
    return sample


def _json_report(report: dict) -> dict:
    # Reject NaN, Infinity and unserializable values at the evaluator boundary.
    return json.loads(json.dumps(report, allow_nan=False))


@dataclass(frozen=True)
class SampleMetricAdapter:
    """Make one configured SampleMetric obey evaluator(massing, context) -> report."""

    metric: Callable
    report_key: str
    building_key: str = "building"
    layout: Layout = "building"
    building_id: str = "generated"

    def __call__(self, massing, context) -> dict:
        sample = build_sample(
            massing,
            context,
            layout=self.layout,
            building_key=self.building_key,
            building_id=self.building_id,
        )
        return _json_report({self.report_key: float(self.metric(sample=sample))})


@dataclass(frozen=True)
class SampleProcessorAdapter:
    """Return explicitly selected processor outputs, without assuming optimization goals."""

    processor: Callable
    report_keys: tuple[str, ...]
    building_key: str = "building"
    layout: Layout = "extrusions"
    building_id: str = "generated"

    def __post_init__(self):
        if not self.report_keys:
            raise ValueError("At least one processor report key is required")

    def __call__(self, massing, context) -> dict:
        sample = build_sample(
            massing,
            context,
            layout=self.layout,
            building_key=self.building_key,
            building_id=self.building_id,
        )
        result = self.processor(sample=sample)
        if not isinstance(result, dict):
            raise TypeError("SampleProcessor must return a dictionary")
        return _json_report({key: result[key] for key in self.report_keys})


def compile_mesh(massing, compiler: Callable, *, building_id="generated"):
    """Call the actual MassingMeshCompiler supplied by the external repository."""
    return compiler(obj=as_buildings(massing, building_id=building_id))
