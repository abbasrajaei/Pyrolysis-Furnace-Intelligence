from .workbench import BASE_CASE,evaluate_case

LABELS={
 'duty_mw':'Chemical duty','H2':'H₂ fraction','CH4':'CH₄ fraction','C2H6':'C₂H₆ fraction','N2':'N₂ fraction',
 'excess_air':'Excess air','draft_pa':'Furnace draft','heat_recovery':'Heat recovery','radiant_share':'Radiant share',
 'inlet_outlet_ratio':'Inlet/outlet firing split','bottom_side_ratio':'Bottom/side outlet split',
 'feed_kg_s':'Feed rate','steam_ratio':'Steam/feed ratio','zone':'Zone selection','zone_correction':'Zone correction',
 'pressure_state':'Fuel-pressure authority'
}

RULES={
 'duty_mw':{
   'why':'Chemical duty sets the energy rate that the fuel system must supply.',
   'effects':['Equivalent fuel demand changes in direct proportion at fixed mixture LHV.','Inlet, outlet and zone firing duties scale with total chemical duty.'],
   'watch':['Fuel-system capacity','Burner loading','Process severity limits'],
   'basis':['Fuel demand: CALCULATED','Firing distribution: CALCULATED'],
   'limits':['No COT, conversion, tube-metal temperature or transient response is predicted.']},
 'H2':{
   'why':'Changing H₂ changes mixture molecular weight, mass LHV, volumetric heating value and stoichiometric oxygen demand.',
   'effects':['Equivalent fuel mass flow changes at fixed chemical duty.','Stoichiometric/actual air and lower Wobbe change.'],
   'watch':['Burner interchangeability','Flame speed / flashback margin','Fuel pressure and control range'],
   'basis':['Fuel properties: CALCULATED from rounded references','Air requirement: CALCULATED','Flame behaviour: QUALITATIVE ONLY'],
   'limits':['No flame-speed, flashback, NOx or burner-stability limit is calculated.']},
 'CH4':{'alias':'H2'},'C2H6':{'alias':'H2'},'N2':{
   'why':'Adding inert N₂ dilutes combustible components and changes mixture molecular weight and volumetric energy density.',
   'effects':['Equivalent fuel demand and air requirement change at fixed chemical duty.','Lower Wobbe changes.'],
   'watch':['Fuel-system capacity','Burner interchangeability','Combustion stability'],
   'basis':['Fuel properties: CALCULATED','Combustion air: CALCULATED'],
   'limits':['No stability or extinction limit is calculated.']},
 'excess_air':{
   'why':'Excess air changes the amount of oxygen and nitrogen carried through combustion above the stoichiometric requirement.',
   'effects':['Actual air flow per mole of fuel changes.','Dry and wet O₂ fractions change.'],
   'watch':['Stack loss','Flame quality','CO / incomplete combustion at low air'],
   'basis':['Air and ideal product O₂: CALCULATED','Efficiency impact: QUALITATIVE ONLY'],
   'limits':['Stack temperature, CO, NOx and efficiency penalty are not quantitatively predicted.']},
 'draft_pa':{
   'why':'Furnace draft establishes a pressure difference that helps move combustion air and flue gas through resistance.',
   'effects':['The Sensitivity Lab can show a fixed-resistance relative-airflow teaching curve.','More negative draft can also increase tramp-air ingress in a real furnace.'],
   'watch':['Firebox pressure','Measured O₂ versus useful burner air','Leakage paths and fan margin'],
   'basis':['Displayed draft: SYNTHETIC INPUT','Draft→relative airflow: MODEL / ASSUMPTION'],
   'limits':['No plant fan curve, register position, leakage coefficient or calibrated air flow is available.']},
 'heat_recovery':{
   'why':'The heat-recovery setting allocates what fraction of chemical input is counted as radiant plus convection duty.',
   'effects':['Radiant and convection duties change together.','Residual heat changes by conservation.'],
   'watch':['Convection constraints','Stack temperature / losses','Process heat requirements'],
   'basis':['Static heat accounting: CALCULATED'],
   'limits':['This is not an off-design heat-transfer model.']},
 'radiant_share':{
   'why':'Radiant share redistributes a fixed useful-duty total between radiant and convection sections.',
   'effects':['Radiant duty increases as convection duty decreases, or vice versa.','Total useful duty is unchanged.'],
   'watch':['Local tube heat flux','Convection duty requirements','Process severity'],
   'basis':['Duty redistribution: CALCULATED'],
   'limits':['No local heat-flux, tube-metal temperature or coil kinetics are predicted.']},
 'inlet_outlet_ratio':{
   'why':'The inlet/outlet ratio changes where a fixed total firing duty is allocated.',
   'effects':['Inlet and outlet firing move in opposite directions while total duty is conserved.','Six inlet-zone duties move with inlet firing.'],
   'watch':['Zone balance','Outlet firing margin','Local heat-flux constraints'],
   'basis':['Firing conservation: CALCULATED'],
   'limits':['No flame shape or local tube flux is predicted.']},
 'bottom_side_ratio':{
   'why':'The bottom/side ratio redistributes fixed outlet firing between the two outlet burner groups.',
   'effects':['Bottom and sidewall outlet duties change in opposite directions.','Total outlet firing is conserved.'],
   'watch':['Burner loading','Flame interaction','Local heat distribution'],
   'basis':['Outlet firing split: CALCULATED'],
   'limits':['No installed burner turndown or flame envelope is represented.']},
 'feed_kg_s':{
   'why':'Feed rate is the process-load basis used by the simplified steam-demand relationship.',
   'effects':['Steam base demand changes at fixed steam/feed ratio.'],
   'watch':['Steam availability','Coil pressure drop','Required firing / severity'],
   'basis':['Steam base demand: CALCULATED'],
   'limits':['Feed rate is not coupled to a calibrated COT or conversion model.']},
 'steam_ratio':{
   'why':'Steam/feed ratio multiplies the selected feed basis to set steam base demand.',
   'effects':['Steam demand changes directly with the ratio.'],
   'watch':['Steam availability','Hydrocarbon partial pressure','Coil pressure drop'],
   'basis':['Steam demand: CALCULATED','Cracking effects: QUALITATIVE ONLY'],
   'limits':['No cracking kinetics, yield or coil hydraulic response is calculated.']},
 'zone_correction':{
   'why':'The selected teaching correction redistributes inlet firing while conserving the inlet total.',
   'effects':['The selected zone receives the correction and the other five zones donate equally.','Total inlet and total furnace duty do not change.'],
   'watch':['Maximum zone duty','Neighbouring zones','Temperature balance'],
   'basis':['Redistribution rule: ASSUMPTION','Conservation: CALCULATED'],
   'limits':['A temperature error does not generate this correction automatically.']},
 'zone':{
   'why':'The zone selector chooses where the explicit teaching redistribution is applied.',
   'effects':['Changing the selected zone moves the same requested correction to a different inlet zone.'],
   'watch':['Maximum zone duty','Zone balance'],
   'basis':['Zone selection: SYNTHETIC INPUT'],
   'limits':['Zone boxes are functional groups, not recovered plant geometry.']},
 'pressure_state':{
   'why':'Fuel-pressure state changes which functional authority is allowed to supersede normal fuel-demand control.',
   'effects':['The active authority changes when a pressure constraint is selected.'],
   'watch':['Constraint status','Available control authority','Fuel-system condition'],
   'basis':['Authority logic: FUNCTIONAL TEACHING MODEL'],
   'limits':['No pressure threshold, valve position, trip sequence or recovery trajectory is predicted.']}
}

def guidance(last_changed,current,baseline=None):
    baseline=BASE_CASE if baseline is None else baseline
    key=last_changed or 'duty_mw'
    if key in ('H2','CH4','C2H6','N2'):
        before=baseline['composition'][key];after=current['composition'][key]
    else:
        before=baseline.get(key);after=current.get(key)
    rule=RULES.get(key,RULES['duty_mw'])
    if 'alias' in rule:rule=RULES[rule['alias']]
    result=evaluate_case(current);base_result=evaluate_case(baseline)
    def fmt(v):
        if isinstance(v,float):return f'{v:.4g}'
        return str(v)
    change=f"{LABELS.get(key,key)}: {fmt(before)} → {fmt(after)}"
    deltas={
      'fuel_flow_pct':100*(result['fuel']['equivalent_fuel_kg_s']/base_result['fuel']['equivalent_fuel_kg_s']-1),
      'dry_o2_delta_pctpt':result['combustion']['dry_o2_pct']-base_result['combustion']['dry_o2_pct'],
      'max_zone_pct':100*(result['firing']['max_zone_mw']/base_result['firing']['max_zone_mw']-1),
      'steam_pct':100*(result['process']['steam_demand_kg_s']/base_result['process']['steam_demand_kg_s']-1)
    }
    return {'change':change,'why':rule['why'],'effects':rule['effects'],'watch':rule['watch'],'basis':rule['basis'],'limits':rule['limits'],'deltas':deltas}
