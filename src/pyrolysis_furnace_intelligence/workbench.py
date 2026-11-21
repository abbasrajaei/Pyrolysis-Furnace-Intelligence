from copy import deepcopy
from math import sqrt
from .provenance import Value
from .fuels import mixture_properties,fuel_required
from .combustion import complete_combustion
from .heat_balance import heat_balance
from .firing_distribution import allocate,redistribute
from .burners import burner_loads
from .process import steam_base_demand
from .control_overrides import authority

COMPONENTS=('H2','CH4','C2H6','N2')

BASE_CASE={
    'duty_mw':60.0,
    'composition':{'H2':0.20,'CH4':0.80,'C2H6':0.0,'N2':0.0},
    'excess_air':0.15,
    'draft_pa':-40.0,
    'heat_recovery':55/60,
    'radiant_share':27/55,
    'inlet_outlet_ratio':1.5,
    'bottom_side_ratio':1.0,
    'feed_kg_s':8.0,
    'steam_ratio':0.35,
    'zone':'None',
    'zone_correction':0.0,
    'pressure_state':'Normal'
}

PRESETS={
    'Baseline':deepcopy(BASE_CASE),
    'Hydrogen-rich fuel':{**deepcopy(BASE_CASE),'composition':{'H2':0.50,'CH4':0.45,'C2H6':0.05,'N2':0.0}},
    'High load':{**deepcopy(BASE_CASE),'duty_mw':75.0,'feed_kg_s':10.0},
    'Reduced load':{**deepcopy(BASE_CASE),'duty_mw':45.0,'feed_kg_s':6.0},
    'Low excess air':{**deepcopy(BASE_CASE),'excess_air':0.05},
    'High excess air':{**deepcopy(BASE_CASE),'excess_air':0.25},
    'Zone C redistribution':{**deepcopy(BASE_CASE),'zone':'C','zone_correction':0.03},
    'Low fuel-pressure constraint':{**deepcopy(BASE_CASE),'pressure_state':'Low-pressure constraint'},
    'High fuel-pressure constraint':{**deepcopy(BASE_CASE),'pressure_state':'High-pressure constraint'},
    'Strong induced draft':{**deepcopy(BASE_CASE),'draft_pa':-70.0}
}

def rebalance_composition(previous,changed,new_value,locked=()):
    old={k:float(previous.get(k,0.0)) for k in COMPONENTS}
    if changed not in COMPONENTS:
        return old
    locked=set(locked or ())
    locked.discard(changed)
    fixed=sum(old[k] for k in locked)
    new=max(0.0,min(float(new_value),max(0.0,1.0-fixed)))
    adjustable=[k for k in COMPONENTS if k!=changed and k not in locked]
    if not adjustable:
        new=1.0-fixed
        out={**old,changed:new}
        return out
    remaining=max(0.0,1.0-fixed-new)
    old_total=sum(old[k] for k in adjustable)
    out={**old,changed:new}
    if old_total>0:
        for k in adjustable:
            out[k]=remaining*old[k]/old_total
    else:
        for k in adjustable:
            out[k]=remaining/len(adjustable)
    for k in locked:
        out[k]=old[k]
    # Remove floating-point residue without changing the intended closure rule.
    for k in out:
        if abs(out[k])<1e-12:
            out[k]=0.0
    drift=1.0-sum(out.values())
    receiver=max(adjustable,key=lambda k:out[k]) if adjustable else changed
    out[receiver]+=drift
    for k in out:
        if out[k]<-1e-12:
            raise ValueError('Composition rebalance produced a negative fraction')
        if out[k]<0:
            out[k]=0.0
    return out

def draft_teaching_model(draft_pa,reference_draft_pa=-40.0,baseline_excess_air=0.15):
    d=float(draft_pa);ref=float(reference_draft_pa)
    if d>0 or ref>=0:
        raise ValueError('Teaching draft model requires nonpositive furnace pressure and negative reference draft')
    relative=sqrt(abs(d)/abs(ref)) if ref else 0.0
    implied_excess=(1+float(baseline_excess_air))*relative-1
    return {
        'relative_airflow':relative,
        'implied_excess_air':implied_excess,
        'basis':'Fixed-resistance teaching correlation: relative airflow proportional to sqrt(|draft|/|reference draft|). Not plant calibrated.'
    }

def evaluate_case(case):
    c=deepcopy(BASE_CASE);c.update(deepcopy(case))
    composition={k:float(c['composition'].get(k,0)) for k in COMPONENTS}
    props=mixture_properties(composition,'interactive')
    duty=Value(float(c['duty_mw'])*1e6,'W','SYNTHETIC','Interactive chemical-duty input','interactive')
    fuel=fuel_required(duty,props['lhv'])
    combustion=complete_combustion(composition,float(c['excess_air']))
    recovery=float(c['heat_recovery']);rad_share=float(c['radiant_share'])
    if not 0<=recovery<=1 or not 0<=rad_share<=1:
        raise ValueError('Heat recovery and radiant share must be between zero and one')
    radiant=Value(duty.value*recovery*rad_share,'W','SYNTHETIC','Interactive recovered-heat split','interactive')
    convection=Value(duty.value*recovery*(1-rad_share),'W','SYNTHETIC','Interactive recovered-heat split','interactive')
    thermal=heat_balance(duty,radiant,convection)
    shares=[1/6]*6
    if c.get('zone') in 'ABCDEF' and abs(float(c.get('zone_correction',0)))>0:
        shares=list(redistribute(shares,'ABCDEF'.index(c['zone']),float(c['zone_correction'])))
    allocation=allocate(duty.value,float(c['inlet_outlet_ratio']),float(c['bottom_side_ratio']),shares)
    loads=burner_loads(allocation,30,20)
    pressure=c['pressure_state']
    auth=authority(low=pressure=='Low-pressure constraint',high=pressure=='High-pressure constraint')
    steam=steam_base_demand(float(c['feed_kg_s']),float(c['feed_kg_s']),float(c['steam_ratio']))
    draft=draft_teaching_model(float(c['draft_pa']),-40.0,float(c['excess_air']))
    return {
        'inputs':c,
        'fuel':{
            'lhv_MJ_kg':props['lhv'].value/1e6,
            'wobbe_MJ_Nm3':props['wobbe'].value/1e6,
            'molecular_weight_g_mol':props['molecular_weight'].value*1000,
            'equivalent_fuel_kg_s':fuel.value
        },
        'combustion':{
            'stoich_air_mol_mol':combustion['stoichiometric_air'].value,
            'actual_air_mol_mol':combustion['actual_air'].value,
            'dry_o2_pct':100*combustion['dry_o2'].value,
            'wet_o2_pct':100*combustion['wet_o2'].value
        },
        'thermal':{
            'radiant_mw':radiant.value/1e6,
            'convection_mw':convection.value/1e6,
            'residual_mw':thermal['loss'].value/1e6,
            'accounting_efficiency_pct':100*thermal['efficiency'].value
        },
        'firing':{
            'inlet_mw':allocation['inlet']/1e6,
            'outlet_mw':allocation['outlet']/1e6,
            'outlet_bottom_mw':allocation['outlet_bottom']/1e6,
            'outlet_sidewall_mw':allocation['outlet_sidewall']/1e6,
            'zones_mw':[v/1e6 for v in allocation['zones']],
            'max_zone_mw':max(allocation['zones'])/1e6,
            'conservation_residual_w':allocation['residual'],
            'bottom_burner_mw':loads['bottom']/1e6,
            'sidewall_burner_mw':loads['sidewall']/1e6
        },
        'process':{'steam_demand_kg_s':steam},
        'control':{'active_authority':auth},
        'draft_model':draft
    }
