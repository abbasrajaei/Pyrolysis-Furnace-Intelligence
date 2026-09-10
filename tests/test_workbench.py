import math
import pytest
from pyrolysis_furnace_intelligence.workbench import BASE_CASE,PRESETS,COMPONENTS,rebalance_composition,draft_teaching_model,evaluate_case
from pyrolysis_furnace_intelligence.sensitivity import INPUTS,OUTPUTS,SUPPORTED,sweep
from pyrolysis_furnace_intelligence.guidance import guidance,RULES
from pyrolysis_furnace_intelligence.fuels import mixture_properties

@pytest.mark.parametrize('component,target',[('H2',.4),('CH4',.5),('C2H6',.2),('N2',.1)])
def test_composition_rebalances_automatically(component,target):
    out=rebalance_composition(BASE_CASE['composition'],component,target,())
    assert out[component]==pytest.approx(target)
    assert sum(out.values())==pytest.approx(1)
    assert all(v>=0 for v in out.values())

def test_composition_preserves_unlocked_ratio():
    start={'H2':.2,'CH4':.6,'C2H6':.15,'N2':.05}
    out=rebalance_composition(start,'H2',.4,())
    assert out['CH4']/out['C2H6']==pytest.approx(.6/.15)
    assert out['CH4']/out['N2']==pytest.approx(.6/.05)

def test_locked_component_is_held():
    start={'H2':.2,'CH4':.6,'C2H6':.15,'N2':.05}
    out=rebalance_composition(start,'H2',.4,['CH4'])
    assert out['CH4']==pytest.approx(.6)
    assert sum(out.values())==pytest.approx(1)

def test_all_other_components_locked_clamps_selected():
    start={'H2':.2,'CH4':.6,'C2H6':.15,'N2':.05}
    out=rebalance_composition(start,'H2',.8,['CH4','C2H6','N2'])
    assert out['H2']==pytest.approx(.2)
    assert sum(out.values())==pytest.approx(1)

@pytest.mark.parametrize('name',list(PRESETS))
def test_presets_are_valid(name):
    result=evaluate_case(PRESETS[name])
    assert result['fuel']['equivalent_fuel_kg_s']>0
    assert sum(PRESETS[name]['composition'].values())==pytest.approx(1)
    assert abs(result['firing']['conservation_residual_w'])<1e-5

def test_baseline_reproduces_public_accounting():
    r=evaluate_case(BASE_CASE)
    assert r['thermal']['radiant_mw']==pytest.approx(27)
    assert r['thermal']['convection_mw']==pytest.approx(28)
    assert r['thermal']['residual_mw']==pytest.approx(5)
    assert r['thermal']['accounting_efficiency_pct']==pytest.approx(91.6666666667)
    assert r['firing']['inlet_mw']==pytest.approx(36)

@pytest.mark.parametrize('draft,relative',[(-10,.5),(-40,1),(-90,1.5),(-100,math.sqrt(2.5))])
def test_draft_teaching_model(draft,relative):
    r=draft_teaching_model(draft)
    assert r['relative_airflow']==pytest.approx(relative)
    assert 'Not plant calibrated' in r['basis']

def test_positive_draft_rejected_by_teaching_correlation():
    with pytest.raises(ValueError):draft_teaching_model(10)

@pytest.mark.parametrize('case_name',['Baseline','Hydrogen-rich fuel','High load','Reduced load','Low excess air','High excess air','Zone C redistribution','Low fuel-pressure constraint','High fuel-pressure constraint','Strong induced draft'])
def test_case_outputs_remain_finite(case_name):
    r=evaluate_case(PRESETS[case_name])
    values=[r['fuel']['equivalent_fuel_kg_s'],r['combustion']['actual_air_mol_mol'],r['thermal']['residual_mw'],r['firing']['max_zone_mw'],r['process']['steam_demand_kg_s']]
    assert all(math.isfinite(x) for x in values)

def test_hydrogen_rich_case_changes_fuel_properties():
    b=evaluate_case(PRESETS['Baseline']);h=evaluate_case(PRESETS['Hydrogen-rich fuel'])
    assert h['fuel']['lhv_MJ_kg']>b['fuel']['lhv_MJ_kg']
    assert h['fuel']['equivalent_fuel_kg_s']<b['fuel']['equivalent_fuel_kg_s']
    assert h['fuel']['wobbe_MJ_Nm3']!=pytest.approx(b['fuel']['wobbe_MJ_Nm3'])

def test_heat_partition_is_always_conservative():
    case={**BASE_CASE,'heat_recovery':.9,'radiant_share':.6}
    r=evaluate_case(case)
    total=r['thermal']['radiant_mw']+r['thermal']['convection_mw']+r['thermal']['residual_mw']
    assert total==pytest.approx(case['duty_mw'])

@pytest.mark.parametrize('input_name',list(SUPPORTED))
def test_each_sensitivity_input_has_outputs(input_name):
    assert SUPPORTED[input_name]
    for output_name in SUPPORTED[input_name]:assert output_name in OUTPUTS

@pytest.mark.parametrize('pair',[(x,y) for x,ys in SUPPORTED.items() for y in ys])
def test_supported_sensitivity_curves(pair):
    x,y=pair;data=sweep(x,y,BASE_CASE,points=17)
    assert len(data['x'])==17 and len(data['y'])==17
    assert data['current_y'] is not None
    assert any(v is not None for v in data['y'])
    assert data['basis']

def test_unsupported_sensitivity_pair_is_rejected():
    with pytest.raises(ValueError):sweep('draft_pressure','fuel_flow',BASE_CASE)

def test_draft_sensitivity_is_labelled_model_assumption():
    data=sweep('draft_pressure','relative_airflow',BASE_CASE)
    assert data['basis']=='MODEL / ASSUMPTION'
    assert 'Not plant calibrated' in data['note']

def test_zone_sensitivity_is_not_pid_claim():
    data=sweep('zone_correction','max_zone',BASE_CASE)
    assert 'ASSUMPTION' in data['basis']
    assert 'not a PID' in data['note']

@pytest.mark.parametrize('component',COMPONENTS)
def test_custom_mixture_properties(component):
    comp={k:0 for k in COMPONENTS};comp[component]=1
    if component=='N2':
        with pytest.raises(ValueError):mixture_properties(comp)
    else:
        p=mixture_properties(comp)
        assert p['lhv'].value>0

@pytest.mark.parametrize('key',['duty_mw','H2','CH4','C2H6','N2','excess_air','draft_pa','heat_recovery','radiant_share','inlet_outlet_ratio','bottom_side_ratio','feed_kg_s','steam_ratio','zone','zone_correction','pressure_state'])
def test_guidance_exists_for_operator_changes(key):
    g=guidance(key,BASE_CASE,BASE_CASE)
    assert g['why'] and g['effects'] and g['watch'] and g['basis'] and g['limits']
    assert set(g['deltas'])=={'fuel_flow_pct','dry_o2_delta_pctpt','max_zone_pct','steam_pct'}

def test_hydrogen_guidance_separates_calculated_and_qualitative():
    case=PRESETS['Hydrogen-rich fuel'];g=guidance('H2',case,BASE_CASE)
    assert any('CALCULATED' in x for x in g['basis'])
    assert any('QUALITATIVE' in x for x in g['basis'])
    assert g['deltas']['fuel_flow_pct']<0

def test_pressure_guidance_does_not_claim_valve_position():
    g=guidance('pressure_state',PRESETS['Low fuel-pressure constraint'],BASE_CASE)
    assert any('valve position' in x for x in g['limits'])
