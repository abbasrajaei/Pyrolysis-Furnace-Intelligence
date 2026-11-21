from pathlib import Path
from importlib.resources import files
import importlib.metadata

from pyrolysis_furnace_intelligence import __version__


def test_installation_and_resource_copies():
    assert importlib.metadata.version("pyrolysis-furnace-intelligence") == __version__
    root = Path(__file__).resolve().parents[1]
    for name in ("public_parameters.yaml", "model_assumptions.yaml"):
        assert (root / "data" / name).read_bytes() == files(
            "pyrolysis_furnace_intelligence"
        ).joinpath("resources/" + name).read_bytes()
