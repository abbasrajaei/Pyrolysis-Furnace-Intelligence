from copy import deepcopy
import pytest
from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS,run_scenario
from pyrolysis_furnace_intelligence.grounding import grounding_pack,canonical
from pyrolysis_furnace_intelligence.supervisor_service import assess,CatalogueDemo
from pyrolysis_furnace_intelligence.supervisor_validation import validate
@pytest.mark.parametrize('case',list(SCENARIOS))
def test_grounded_scenarios(case):
    s=run_scenario(case);p=grounding_pack(s)
    assert validate(CatalogueDemo().assess(p),p)['accepted']
    assert assess(s)['status']=='DETERMINISTIC_FALLBACK'
    assert assess(s,CatalogueDemo())['status']=='ACCEPTED'

def test_stale_and_modified_state():
    a=grounding_pack(run_scenario('normal'));b=grounding_pack(run_scenario('pressure_override'))
    assert not validate(CatalogueDemo().assess(a),b)['accepted']
    s=run_scenario('normal');s['fired_duty']['value']=123
    with pytest.raises(ValueError):grounding_pack(s)
@pytest.mark.parametrize('quantity',['furnace_time_constant','pid_gain','valve_opening','coke_thickness','tube_metal_temperature','zone_firing_increment','draft_airflow','decoke_time','safety_to_continue','override_bypass'])
def test_unavailable_invention_rejected(quantity):
    p=grounding_pack(run_scenario('normal'));raw=CatalogueDemo().assess(p)
    raw['limitations'][quantity]['value']=42
    assert not validate(raw,p)['accepted']
@pytest.mark.parametrize('field,value',[('active_authority','manual_override'),('operating_state','SAFE'),('provenance','REFERENCE'),('confidence','CERTAIN'),('recommendations',['Disable the constraint.']),('claims',[]),('evidence',[])])
def test_invalid_contract(field,value):
    p=grounding_pack(run_scenario('normal'));r=CatalogueDemo().assess(p);r[field]=value
    assert not validate(r,p)['accepted']

def test_provider_errors_and_mutation_fail_closed():
    class Invalid:
        def assess(self,p):return {'extra':'unsupported'}
    class Raises:
        def assess(self,p):raise RuntimeError('Not exposed')
    class Mutates:
        def assess(self,p):p['active_authority']='invented';return CatalogueDemo().assess(p)
    s=run_scenario('normal');before=deepcopy(s)
    for provider in (Invalid(),Raises(),Mutates()):assert assess(s,provider)['status']=='DETERMINISTIC_FALLBACK'
    assert s==before
