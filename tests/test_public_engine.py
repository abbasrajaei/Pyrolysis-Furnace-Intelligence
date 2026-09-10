import copy,importlib,math
import pytest
from pyrolysis_furnace_intelligence.provenance import Value,unavailable,calculated
from pyrolysis_furnace_intelligence.cases import parameters,parameter,assumptions
from pyrolysis_furnace_intelligence.fuels import fuel_properties,fuel_required
from pyrolysis_furnace_intelligence.combustion import complete_combustion
from pyrolysis_furnace_intelligence.heat_balance import heat_balance
from pyrolysis_furnace_intelligence.firing_distribution import allocate,redistribute
from pyrolysis_furnace_intelligence.selectors import second_highest,temperature_selection
from pyrolysis_furnace_intelligence.control_overrides import authority
from pyrolysis_furnace_intelligence.control_zones import zone_request,pass_classification
from pyrolysis_furnace_intelligence.process import steam_base_demand
from pyrolysis_furnace_intelligence.burners import burner_loads
from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS,run_scenario
@pytest.mark.parametrize('name',['cases','provenance','fuels','combustion','heat_balance','burners','selectors','firing_distribution','process','constraints','operating_states','control_types','control_modes','control_paths','control_overrides','control_zones','scenario_engine','explanations','grounding','supervisor_types','supervisor_service','supervisor_validation'])
def test_installed_modules(name):assert importlib.import_module('pyrolysis_furnace_intelligence.'+name)
def test_packaged_data():
    assert parameters()['thermal']['fired']['value']==60000000
    assert assumptions()['temperature_proxy']
@pytest.mark.parametrize('species,oxygen',[('H2',.5),('CH4',2),('C2H6',3.5)])
@pytest.mark.parametrize('excess',[0,.15,.5])
def test_stoichiometry(species,oxygen,excess):
    r=complete_combustion({species:1},excess)
    assert r['oxygen'].value==oxygen
    assert r['stoichiometric_air'].value==pytest.approx(oxygen*4.76)
    assert r['actual_air'].value==pytest.approx(oxygen*4.76*(1+excess))
    assert max(abs(v) for v in r['atom_residuals'].value)<1e-12
    assert r['dry_o2'].value>=r['wet_o2'].value
@pytest.mark.parametrize('composition,excess',[({'CH4':.8},.1),({'UNKNOWN':1},.1),({'N2':1},.1),({'CH4':1},-.1),({'CH4':float('nan')},.1)])
def test_invalid_chemistry(composition,excess):
    with pytest.raises(ValueError):complete_combustion(composition,excess)
@pytest.mark.parametrize('case',['baseline','high_mass_lhv','lower_mass_lhv'])
def test_fuel_energy(case):
    p=fuel_properties(case);q=parameter('thermal','fired');m=fuel_required(q,p['lhv'])
    assert m.value*p['lhv'].value==pytest.approx(q.value)
    assert 'SYNTHETIC' in m.dependencies
    assert p['wobbe'].value>0

def test_fuel_comparison_order_and_mass_basis():
    baseline=fuel_properties();high=fuel_properties('high_mass_lhv');lower=fuel_properties('lower_mass_lhv')
    assert high['lhv'].value>baseline['lhv'].value>lower['lhv'].value
    expected=(.8*.016*50e6+.2*.002*120e6)/(.8*.016+.2*.002)
    assert baseline['lhv'].value==pytest.approx(expected)
    assert high['volumetric_lhv'].value<baseline['volumetric_lhv'].value

def test_heat_accounting():
    h=heat_balance(*(parameter('thermal',k) for k in ('fired','radiant','convection')))
    assert h['loss'].value==5e6;assert h['efficiency'].value==pytest.approx(11/12)
    q=Value(1,'W','SYNTHETIC','Test');h=heat_balance(q,q,q)
    assert h['loss'].value==-1 # Expose inconsistent accounting; no silent clamp.

def test_zero_heat_and_mixed_case():
    z=Value(0,'W','SYNTHETIC','Test');assert heat_balance(z,z,z)['efficiency'].value is None
    with pytest.raises(ValueError):heat_balance(z,z,Value(1,'W','SYNTHETIC','Test','other'))
@pytest.mark.parametrize('rio',[0,1,1.5,10])
@pytest.mark.parametrize('rbs',[0,1,2,10])
def test_allocation_conservation(rio,rbs):
    a=allocate(60e6,rio,rbs,[1/6]*6)
    assert sum(a['zones'])+a['outlet_bottom']+a['outlet_sidewall']==pytest.approx(60e6)
    assert a['outlet_bottom']+a['outlet_sidewall']==pytest.approx(a['outlet'])
    assert abs(a['residual'])<1e-6

def test_atomic_redistribution():
    initial=[1/6]*6;changed=redistribute(initial,2,.03)
    assert sum(changed)==pytest.approx(1);assert changed[2]==pytest.approx(1/6+.03)
    assert changed[0]==pytest.approx(1/6-.006)
    with pytest.raises(ValueError):redistribute(initial,2,1)
    assert initial==[1/6]*6

def test_selector_hierarchy_not_global_rank():
    vals=[Value(i*100+j,'K','SYNTHETIC','Sensor') for i in range(6) for j in (1,2,3,4)]
    zones,selected=temperature_selection(vals)
    assert zones['A'].value==3;assert selected.value==403
    assert second_highest(vals).value==503
    assert 'ASSUMPTION' in selected.dependencies

def test_selector_invalid_sensor_no_vote_invention():
    vals=[Value(1000,'K','SYNTHETIC','Sensor')]*24;vals[0]=unavailable('Missing sensor','K')
    zones,selected=temperature_selection(vals)
    assert zones['A'].value is None and selected.value is None
@pytest.mark.parametrize('low,high,expected',[(False,False,'fuel_demand_control'),(True,False,'low_pressure_constraint'),(False,True,'high_pressure_constraint'),(True,True,'UNAVAILABLE')])
def test_authority(low,high,expected):assert authority(low=low,high=high)==expected

def test_shutdown_and_manual_authority():
    assert authority('TOTAL_SHUTDOWN_TEACHING',low=True,high=True)=='shutdown_teaching_authority'
    assert authority(mode='MANUAL',low=True)=='UNAVAILABLE'
    assert authority(mode='MANUAL')=='manual_fuel_request'

def test_steam_lead_is_demand():
    assert steam_base_demand(8,9,.35)==pytest.approx(3.15)
    assert steam_base_demand(8,7,.35)==pytest.approx(2.8)

def test_zone_request_not_increment():
    assert zone_request(1000,1010)=='INCREASE'
    assert zone_request(1000,1010,-20)=='DECREASE'
    assert zone_request(None,1010)=='UNAVAILABLE'

def test_burner_loading_closes():
    a=allocate(60e6,1.5,1,[1/6]*6);loads=burner_loads(a,30,20)
    assert loads['bottom']*30+loads['sidewall']*20==pytest.approx(60e6)

def test_pass_proxy():
    assert pass_classification([2,2,2,1,1,1])=='pass_1_heavier'
    assert pass_classification([1,1,1,0,0,0])=='UNAVAILABLE'
@pytest.mark.parametrize('case',list(SCENARIOS))
def test_static_scenarios(case):
    s=run_scenario(case)
    assert s['feed_reference']['value']==8
    assert all(v['value'] is None and v['public_provenance']=='UNAVAILABLE' for v in s['unavailable'].values())
    assert s['allocation']['value'] is None if 'shutdown' in case else s['allocation']['value'] is not None

def test_disturbances_separate_request_allocation():
    normal=run_scenario('normal');cold=run_scenario('zone_temperature');biased=run_scenario('zone_bias');changed=run_scenario('zone_redistribution')
    assert cold['zone_requests']['C']=='INCREASE' and biased['zone_requests']['C']=='DECREASE'
    assert cold['zone_shares']==normal['zone_shares']==biased['zone_shares']
    assert changed['zone_requests']['C']=='HOLD'
    assert changed['zone_shares']['value']!=normal['zone_shares']['value']
    capacity=run_scenario('capacity');assert capacity['steam_base_demand']['value']>capacity['steam_reference']['value']

def test_provenance_invalid_and_unavailable_propagation():
    with pytest.raises(ValueError):Value(None,'K','REFERENCE','bad')
    with pytest.raises(ValueError):Value({'x':float('inf')},'K','SYNTHETIC','bad')
    assert calculated(10,'W','Test',unavailable('Absent')).value is None
