from dataclasses import dataclass, asdict
from enum import Enum
import math
class Provenance(str,Enum):
    REFERENCE='REFERENCE'
    CALCULATED='CALCULATED'
    ASSUMPTION='ASSUMPTION'
    SYNTHETIC='SYNTHETIC'
    UNAVAILABLE='UNAVAILABLE'
@dataclass(frozen=True)
class Value:
    value: object
    units: str
    public_provenance: str
    engineering_basis: str
    case: str='teaching'
    dependencies: tuple=()
    def __post_init__(self):
        Provenance(self.public_provenance)
        if not self.units or not self.engineering_basis: raise ValueError('Units and basis required')
        if (self.value is None)!=(self.public_provenance=='UNAVAILABLE'):raise ValueError('Null requires UNAVAILABLE and vice versa')
        def check(v):
            if isinstance(v,float) and not math.isfinite(v):raise ValueError('Nonfinite value')
            if isinstance(v,dict):
                for x in v.values():check(x)
            if isinstance(v,(list,tuple)):
                for x in v:check(x)
        check(self.value)
    def to_dict(self):return asdict(self)
def unavailable(reason,units='1'):return Value(None,units,'UNAVAILABLE',reason)
def calculated(v,units,basis,*inputs):
    if any(x.public_provenance=='UNAVAILABLE' for x in inputs):return unavailable('Required input unavailable',units)
    deps=tuple(dict.fromkeys(y for x in inputs for y in (x.public_provenance,*x.dependencies)))
    return Value(v,units,'CALCULATED',basis,dependencies=deps)
def number(v):
    if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v):raise ValueError('Finite scalar required')
    return float(v)
