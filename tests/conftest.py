import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

MASLOV_COMMIT = "607ff1fcf80477787409522d93e18e42ac1436cf"


def pytest_addoption(parser):
    parser.addoption("--maslov-repo", default=os.environ.get("MASSING_GENERATION_REPO"))


@pytest.fixture
def rings():
    return [
        [[0, 0], [10, 0], [10, 10], [0, 10]],
        [[2, 2], [2, 4], [4, 4], [4, 2]],
        [[20, 0], [24, 0], [24, 4], [20, 4]],
    ]


@pytest.fixture(scope="session")
def maslov(request):
    value = request.config.getoption("--maslov-repo")
    if not value:
        pytest.skip("Set MASSING_GENERATION_REPO or --maslov-repo for pinned integration tests")
    repo = Path(value).resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    assert actual == MASLOV_COMMIT, f"Expected pinned Maslov checkout, found {actual}"
    # Reject modified target code rather than silently testing a different implementation.
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", "src"], check=False
    )
    assert result.returncode == 0, "Target src/ must match the pinned commit"
    sys.path.insert(0, str(repo))
    modules = {}
    for name in (
        "polygons_to_shapely_converter",
        "shapely_to_polygons_converter",
        "mesh_compiler.massing_mesh_compiler",
        "sample_metric.building_zero_heights_rate",
        "sample_processor.shapely_massing_creator",
    ):
        modules[name] = importlib.import_module("src." + name)
    yield modules
    sys.path.remove(str(repo))
