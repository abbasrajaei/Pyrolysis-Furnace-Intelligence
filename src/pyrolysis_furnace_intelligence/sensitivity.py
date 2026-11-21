from copy import deepcopy
import math
from .workbench import BASE_CASE,evaluate_case,rebalance_composition

INPUTS={
    'h2_fraction':('H₂ mole fraction',0.0,0.80),
    'ch4_fraction':('CH₄ mole fraction',0.0,1.00),
    'c2h6_fraction':('C₂H₆ mole fraction',0.0,0.80),
    'n2_fraction':('N₂ mole fraction',0.0,0.50),
    'excess_air':('Excess-air fraction',0.0,0.40),
    'chemical_duty':('Chemical duty / MW',30.0,90.0),
    'heat_recovery':('Useful heat recovery',0.75,0.98),
    'radiant_share':('Radiant share of useful heat',0.35,0.65),
    'inlet_outlet_ratio':('Inlet / outlet firing ratio',0.5,3.0),
    'bottom_side_ratio':('Outlet bottom / side ratio',0.25,4.0),
    'feed_rate':('Feed / kg s⁻¹',4.0,14.0),
    'steam_feed_ratio':('Steam / feed ratio',0.10,0.80),
    'zone_correction':('Selected zone share correction',-0.05,0.05),
    'draft_pressure':('Furnace draft / Pa(g)',-100.0,-10.0)
}

OUTPUTS={
    'fuel_flow':('Equivalent fuel / kg s⁻¹','fuel.equivalent_fuel_kg_s'),
    'mass_lhv':('Mass LHV / MJ kg⁻¹','fuel.lhv_MJ_kg'),
    'wobbe':('Lower Wobbe / MJ Nm⁻³','fuel.wobbe_MJ_Nm3'),
    'stoich_air':('Stoichiometric air / mol mol⁻¹','combustion.stoich_air_mol_mol'),
    'actual_air':('Actual air / mol mol⁻¹','combustion.actual_air_mol_mol'),
    'dry_o2':('Dry O₂ / %','combustion.dry_o2_pct'),
    'radiant_duty':('Radiant duty / MW','thermal.radiant_mw'),
    'convection_duty':('Convection duty / MW','thermal.convection_mw'),
    'residual_heat':('Residual heat / MW','thermal.residual_mw'),
    'inlet_firing':('Inlet firing / MW','firing.inlet_mw'),
    'outlet_firing':('Outlet firing / MW','firing.outlet_mw'),
    'outlet_bottom':('Outlet bottom firing / MW','firing.outlet_bottom_mw'),
    'outlet_sidewall':('Outlet sidewall firing / MW','firing.outlet_sidewall_mw'),
    'max_zone':('Maximum zone firing / MW','firing.max_zone_mw'),
    'steam_demand':('Steam demand / kg s⁻¹','process.steam_demand_kg_s'),
    'relative_airflow':('Relative airflow / reference','draft_model.relative_airflow'),
    'implied_excess_air':('Implied excess-air fraction','draft_model.implied_excess_air')
}

FUEL_OUTPUTS=['fuel_flow','mass_lhv','wobbe','stoich_air','actual_air','dry_o2']
SUPPORTED={
    'h2_fraction':FUEL_OUTPUTS,
    'ch4_fraction':FUEL_OUTPUTS,
    'c2h6_fraction':FUEL_OUTPUTS,
    'n2_fraction':FUEL_OUTPUTS,
    'excess_air':['actual_air','dry_o2'],
    'chemical_duty':['fuel_flow','radiant_duty','convection_duty','residual_heat','inlet_firing','outlet_firing','max_zone'],
    'heat_recovery':['radiant_duty','convection_duty','residual_heat'],
    'radiant_share':['radiant_duty','convection_duty'],
    'inlet_outlet_ratio':['inlet_firing','outlet_firing','max_zone'],
    'bottom_side_ratio':['outlet_bottom','outlet_sidewall'],
    'feed_rate':['steam_demand'],
    'steam_feed_ratio':['steam_demand'],
    'zone_correction':['max_zone'],
    'draft_pressure':['relative_airflow','implied_excess_air']
}
COMPONENT_INPUTS={'h2_fraction':'H2','ch4_fraction':'CH4','c2h6_fraction':'C2H6','n2_fraction':'N2'}

def _get(result,path):
    value=result
    for key in path.split('.'):
        value=value[key]
    return value

def _case_with_input(base,input_name,value):
    c=deepcopy(base)
    if input_name in COMPONENT_INPUTS:
        comp=COMPONENT_INPUTS[input_name]
        c['composition']=rebalance_composition(c['composition'],comp,value,())
    elif input_name=='excess_air':c['excess_air']=value
    elif input_name=='chemical_duty':c['duty_mw']=value
    elif input_name=='heat_recovery':c['heat_recovery']=value
    elif input_name=='radiant_share':c['radiant_share']=value
    elif input_name=='inlet_outlet_ratio':c['inlet_outlet_ratio']=value
    elif input_name=='bottom_side_ratio':c['bottom_side_ratio']=value
    elif input_name=='feed_rate':c['feed_kg_s']=value
    elif input_name=='steam_feed_ratio':c['steam_ratio']=value
    elif input_name=='zone_correction':
        c['zone']='C';c['zone_correction']=value
    elif input_name=='draft_pressure':c['draft_pa']=value
    else:raise ValueError('Unsupported sensitivity input')
    return c

def current_x(case,input_name):
    if input_name in COMPONENT_INPUTS:return case['composition'][COMPONENT_INPUTS[input_name]]
    mapping={'excess_air':'excess_air','chemical_duty':'duty_mw','heat_recovery':'heat_recovery','radiant_share':'radiant_share','inlet_outlet_ratio':'inlet_outlet_ratio','bottom_side_ratio':'bottom_side_ratio','feed_rate':'feed_kg_s','steam_feed_ratio':'steam_ratio','zone_correction':'zone_correction','draft_pressure':'draft_pa'}
    return case[mapping[input_name]]

def sweep(input_name,output_name,case=None,points=61):
    if output_name not in SUPPORTED.get(input_name,[]):
        raise ValueError('Unsupported input/output sensitivity pair')
    base=deepcopy(BASE_CASE if case is None else case)
    lo,hi=INPUTS[input_name][1:]
    xs=[lo+(hi-lo)*i/(points-1) for i in range(points)]
    ys=[];path=OUTPUTS[output_name][1]
    for x in xs:
        try:
            y=_get(evaluate_case(_case_with_input(base,input_name,x)),path)
            ys.append(float(y) if y is not None and math.isfinite(float(y)) else None)
        except ValueError:
            ys.append(None)
    current=current_x(base,input_name)
    current_y=_get(evaluate_case(_case_with_input(base,input_name,current)),path)
    basis='CALCULATED';note=''
    if input_name=='draft_pressure':
        basis='MODEL / ASSUMPTION'
        note='Fixed-resistance teaching correlation: relative airflow ∝ sqrt(|draft|). Not plant calibrated.'
    elif input_name=='zone_correction':
        basis='ASSUMPTION + CALCULATED'
        note='Explicit equal-donor redistribution; not a PID-generated correction.'
    elif input_name in COMPONENT_INPUTS:
        note='Selected component is swept while all other unlocked components renormalize proportionally.'
    return {'x':xs,'y':ys,'current_x':current,'current_y':current_y,'x_label':INPUTS[input_name][0],'y_label':OUTPUTS[output_name][0],'basis':basis,'note':note}
