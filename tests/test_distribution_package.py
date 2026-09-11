from pathlib import Path
from importlib.resources import files
import importlib.metadata

def test_installation_and_resource_copies():
    assert importlib.metadata.version('pyrolysis-furnace-intelligence')=='2.2.0'
    root=Path(__file__).resolve().parents[1]
    for name in ('public_parameters.yaml','model_assumptions.yaml'):
        assert (root/'data'/name).read_bytes()==files('pyrolysis_furnace_intelligence').joinpath('resources/'+name).read_bytes()
