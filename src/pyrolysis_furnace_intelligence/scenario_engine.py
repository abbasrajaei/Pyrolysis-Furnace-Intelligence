from .cases import parameter
from .provenance import Value,calculated
from .fuels import fuel_properties,fuel_required
from .heat_balance import heat_balance
from .selectors import temperature_selection
from .firing_distribution import allocate,redistribute
from .process import steam_base_demand
from .operating_states import State
from .control_overrides import authority
from .control_modes import distribution_enabled
from .control_zones import zone_request,pass_classification
from .constraints import unavailable_results
SCENARIOS={
 'normal': 'Normal operation', 'fuel_change':'Fuel-property change',
 'high_lhv':'High-heating-value fuel case', 'lower_lhv':'Lower-heating-value fuel case',
 'zone_temperature':'Zone temperature deviation', 'zone_bias':'Zone target bias',
 'zone_redistribution':'Zone firing redistribution', 'capacity':'Capacity increase',
 'pressure_override':'Fuel-pressure override', 'partial_shutdown':'Partial shutdown teaching state',
 'total_shutdown':'Total shutdown teaching state', 'pass_imbalance':'Pass imbalance',
 'bottom_side':'Bottom/side firing redistribution'}
def run_scenario(name='normal'):
    if name not in SCENARIOS:raise ValueError('Unknown scenario')
    state=State.PARTIAL if name=='partial_shutdown' else State.TOTAL if name=='total_shutdown' else State.NORMAL
    active=authority(state,low=name=='pressure_override')
    fuel='high_mass_lhv' if name in ('high_lhv','fuel_change') else 'lower_mass_lhv' if name=='lower_lhv' else 'baseline'
    q,r,c=[parameter('thermal',k) for k in ('fired','radiant','convection')]
    target=parameter('process','target');feed=parameter('process','feed');ratio=parameter('process','steam_ratio')
    temperatures=[Value(target.value-(12 if name=='zone_temperature' and 8<=i<12 else 0),'K','SYNTHETIC','Explicit teaching sensor') for i in range(24)]
    zones,selected=temperature_selection(temperatures)
    shares=parameter('distribution','zone_shares').value
    if name=='zone_redistribution':shares=redistribute(shares,2,.03)
    a=allocate(q.value,parameter('distribution','inlet_outlet_ratio').value,2 if name=='bottom_side' else parameter('distribution','bottom_side_ratio').value,shares) if distribution_enabled(state,active) else None
    requested=feed.value*1.125 if name=='capacity' else feed.value
    demand=steam_base_demand(feed.value,requested,ratio.value)
    props=fuel_properties(fuel)
    teaching=Value('policy','1','ASSUMPTION','Simplified static event policy; no automatic physical transient')
    def val(v,u,b):return calculated(v,u,b,teaching,q)
    result={'scenario':name,'operating_state':state.value,'active_authority':active,
      'fuel_case':fuel,'fired_duty':q.to_dict(),'feed_reference':feed.to_dict(),
      'steam_reference':calculated(feed.value*ratio.value,'kg/s','Reference feed times explicit ratio',feed,ratio).to_dict(),
      'requested_feed':Value(requested,'kg/s','SYNTHETIC','Explicit demand request, not measured flow').to_dict(),
      'steam_base_demand':val(demand,'kg/s','max(actual, requested) feed times ratio; no delivered-flow prediction').to_dict(),
      'fuel_required':fuel_required(q,props['lhv']).to_dict(),
      'selected_proxy':selected.to_dict(),'zone_selected':{z:v.to_dict() for z,v in zones.items()},
      'zone_requests':{z:zone_request(v.value,target.value,-6 if z=='C' and name=='zone_bias' else 0,state==State.NORMAL) for z,v in zones.items()},
      'zone_shares':Value(list(shares),'1','ASSUMPTION' if name=='zone_redistribution' else 'SYNTHETIC','Explicit equal-donor teaching redistribution' if name=='zone_redistribution' else 'Equal teaching shares').to_dict(),
      'allocation':val(a,'W','Physical duty allocation; ratio and equal-share assumptions').to_dict() if a else Value(None,'W','UNAVAILABLE','Allocation withheld in shutdown teaching state').to_dict(),
      'pass_classification':pass_classification([1.2,1.2,1.2,1,1,1] if name=='pass_imbalance' else [1]*6),
      'heat_balance':{k:v.to_dict() for k,v in heat_balance(q,r,c).items()},
      'unavailable':{k:v.to_dict() for k,v in unavailable_results().items()}}
    return result
