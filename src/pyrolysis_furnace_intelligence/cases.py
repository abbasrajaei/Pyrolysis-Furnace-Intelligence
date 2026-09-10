from importlib.resources import files
import yaml
from .provenance import Value
def parameters():return yaml.safe_load(files(__package__).joinpath('resources/public_parameters.yaml').read_text())
def assumptions():return yaml.safe_load(files(__package__).joinpath('resources/model_assumptions.yaml').read_text())
def parameter(section,key):
    e=parameters()[section][key]
    return Value(**{k:v for k,v in e.items() if k!='notes'})
