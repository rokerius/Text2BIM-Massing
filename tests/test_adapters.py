from copy import deepcopy

import pytest

from text2bim_massing import Scene
from text2bim_massing.adapters import (
    SampleMetricAdapter,
    SampleProcessorAdapter,
    as_buildings,
    build_sample,
)


@pytest.mark.parametrize("layout", ["extrusions", "building", "buildings"])
def test_explicit_layouts_and_input_isolation(rings, layout):
    massing = Scene.from_massing(
        [{"polygons": rings, "bottom_elevation": 0, "top_elevation": 6}]
    ).to_massing()
    context = {"site": {"id": "site-1"}, "building": "old-value"}
    before = deepcopy(context)
    sample = build_sample(massing, context, layout=layout, building_id="new-id")
    if layout == "extrusions":
        assert sample["building"] == massing
    elif layout == "building":
        assert sample["building"] == {"id": "new-id", "massing": massing}
    else:
        assert sample["building"] == as_buildings(massing, building_id="new-id")
    sample["site"]["id"] = "changed"
    assert context == before


def test_metric_does_not_mutate_context_or_choose_an_objective(rings):
    massing = Scene().to_massing()
    massing.append({"polygons": rings, "bottom_elevation": 0, "top_elevation": 6})
    context = {"site": {"id": "one"}}
    before = deepcopy(massing)

    def metric(*, sample):
        sample["site"]["id"] = "two"
        sample["candidate"]["massing"].clear()
        return 17.5

    adapter = SampleMetricAdapter(metric, "configured_name", building_key="candidate")
    assert adapter(massing, context) == {"configured_name": 17.5}
    assert massing == before
    assert context == {"site": {"id": "one"}}


def test_processor_returns_only_selected_outputs(rings):
    scene = Scene()
    scene.create_extrusion(rings, 0, 6)

    def processor(*, sample):
        assert isinstance(sample["building"], list)
        sample.update({"report": {"observed": 1}, "internal": object()})
        return sample

    evaluator = SampleProcessorAdapter(processor, report_keys=("report",))
    assert evaluator(scene.to_massing(), {}) == {"report": {"observed": 1}}


def test_non_json_reports_are_rejected():
    with pytest.raises(ValueError):
        SampleMetricAdapter(lambda **kwargs: float("nan"), "metric")([], {})
    with pytest.raises(TypeError, match="dictionary"):
        SampleProcessorAdapter(lambda **kwargs: None, ("metric",))([], {})
    with pytest.raises(ValueError, match="layout"):
        build_sample([], {}, layout="auto")
