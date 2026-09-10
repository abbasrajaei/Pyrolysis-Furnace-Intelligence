from pathlib import Path
import streamlit as st

from pyrolysis_furnace_intelligence.cases import parameter, parameters, assumptions
from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS, run_scenario
from pyrolysis_furnace_intelligence.fuels import fuel_properties, fuel_required
from pyrolysis_furnace_intelligence.combustion import complete_combustion
from pyrolysis_furnace_intelligence.heat_balance import heat_balance
from pyrolysis_furnace_intelligence.firing_distribution import allocate, redistribute
from pyrolysis_furnace_intelligence.burners import burner_loads
from pyrolysis_furnace_intelligence.control_overrides import authority
from pyrolysis_furnace_intelligence.process import steam_base_demand
from pyrolysis_furnace_intelligence.provenance import Value
from pyrolysis_furnace_intelligence.control_paths import PATHS
from pyrolysis_furnace_intelligence.explanations import explain
from pyrolysis_furnace_intelligence.supervisor_service import assess, CatalogueDemo
from pyrolysis_furnace_intelligence.grounding import grounding_pack

ROOT=Path(__file__).resolve().parents[1]
PAGES=['Overview','Thermal performance','Fuel comparison','Firing distribution','Control architecture','Scenario Lab','AI Engineering Supervisor','Model boundaries']

st.set_page_config(page_title='Pyrolysis Furnace Intelligence', layout='wide')
st.title('Pyrolysis Furnace Intelligence')
st.caption('Interactive educational furnace simulator • Synthetic teaching data • No plant operating authority')

page=st.sidebar.radio('Workspace', PAGES)
scenario=st.sidebar.selectbox('Teaching scenario', list(SCENARIOS), format_func=lambda k:SCENARIOS[k])
s=run_scenario(scenario)
st.sidebar.caption('Events change functional interpretation. They do not simulate elapsed time.')

def metrics():
    c=st.columns(3)
    c[0].metric('Chemical duty',f"{s['fired_duty']['value']/1e6:.1f} MW")
    c[1].metric('Reference useful duty',f"{s['heat_balance']['useful']['value']/1e6:.1f} MW")
    c[2].metric('Reference efficiency',f"{100*s['heat_balance']['efficiency']['value']:.2f}%")

def explanation():
    for line in explain(s):
        st.write(line)

def teaching_value(value, units, basis):
    return Value(value, units, 'SYNTHETIC', basis, 'interactive_teaching')

def custom_lhv(composition):
    p=parameters()
    mw=0.0
    molar_energy=0.0
    for species, fraction in composition.items():
        if fraction <= 0:
            continue
        m=p['species'][species]['molar_mass']['value']
        l=p['species'][species]['lhv']['value']
        mw += fraction*m
        molar_energy += fraction*m*l
    if mw <= 0:
        raise ValueError('Fuel molecular weight must be positive')
    return molar_energy/mw

if page=='Overview':
    st.subheader('Interactive engineering sandbox')
    st.write('Change the teaching inputs below and the combustion, fuel demand, heat accounting, firing distribution and control interpretation update immediately.')

    c1,c2,c3=st.columns(3)
    duty_mw=c1.slider('Chemical duty / MW',30.0,90.0,60.0,1.0)
    excess_air=c2.slider('Excess-air fraction',0.0,0.40,0.15,0.01)
    draft_pa=c3.slider('Furnace draft / Pa(g)',-100.0,0.0,-40.0,5.0)

    st.markdown('#### Fuel composition — mole fraction')
    f1,f2,f3,f4=st.columns(4)
    x_h2=f1.slider('H₂',0.0,1.0,0.20,0.05)
    x_ch4=f2.slider('CH₄',0.0,1.0,0.80,0.05)
    x_c2h6=f3.slider('C₂H₆',0.0,1.0,0.00,0.05)
    x_n2=f4.slider('N₂',0.0,1.0,0.00,0.05)
    composition={'H2':x_h2,'CH4':x_ch4,'C2H6':x_c2h6,'N2':x_n2}
    total_x=sum(composition.values())

    st.markdown('#### Heat distribution')
    h1,h2=st.columns(2)
    radiant_fraction=h1.slider('Radiant share of chemical input',0.20,0.70,0.45,0.01)
    convection_fraction=h2.slider('Convection share of chemical input',0.20,0.70,0.47,0.01)

    st.markdown('#### Firing distribution and process demand')
    a1,a2,a3,a4=st.columns(4)
    inlet_outlet_ratio=a1.slider('Inlet / outlet firing ratio',0.5,3.0,1.5,0.1)
    bottom_side_ratio=a2.slider('Outlet bottom / side ratio',0.25,4.0,1.0,0.25)
    feed_kg_s=a3.slider('Feed / kg s⁻¹',4.0,14.0,8.0,0.5)
    steam_ratio=a4.slider('Steam / feed mass ratio',0.10,0.80,0.35,0.05)

    z1,z2,z3=st.columns(3)
    correction_zone=z1.selectbox('Zone correction',['None','A','B','C','D','E','F'])
    correction=z2.slider('Explicit zone share correction',-0.05,0.05,0.00,0.005)
    pressure_state=z3.selectbox('Fuel-pressure authority',['Normal','Low-pressure constraint','High-pressure constraint'])

    if abs(total_x-1.0)>1e-9:
        st.error(f'Fuel mole fractions must sum to 1.000. Current total = {total_x:.3f}. No combustion calculation is performed.')
    else:
        duty=teaching_value(duty_mw*1e6,'W','Interactive chemical-duty input')
        lhv_value=teaching_value(custom_lhv(composition),'J/kg','Rounded public component LHVs combined on a declared mole-fraction basis')
        fuel_flow=fuel_required(duty,lhv_value)
        combustion=complete_combustion(composition,excess_air)

        radiant=teaching_value(duty.value*radiant_fraction,'W','Interactive radiant accounting share')
        convection=teaching_value(duty.value*convection_fraction,'W','Interactive convection accounting share')
        thermal=heat_balance(duty,radiant,convection)

        shares=[1/6]*6
        if correction_zone!='None' and abs(correction)>0:
            try:
                shares=list(redistribute(shares,'ABCDEF'.index(correction_zone),correction))
            except ValueError:
                st.error('The requested zone correction would make the six-zone distribution infeasible.')
        alloc=allocate(duty.value,inlet_outlet_ratio,bottom_side_ratio,shares)
        pressure_low=pressure_state=='Low-pressure constraint'
        pressure_high=pressure_state=='High-pressure constraint'
        active_authority=authority(low=pressure_low,high=pressure_high)
        steam_demand=steam_base_demand(feed_kg_s,feed_kg_s,steam_ratio)

        m=st.columns(5)
        m[0].metric('Equivalent fuel',f"{fuel_flow.value:.3f} kg/s")
        m[1].metric('Stoich. air',f"{combustion['stoichiometric_air'].value:.3f} mol/mol fuel")
        m[2].metric('Dry O₂',f"{100*combustion['dry_o2'].value:.2f} %")
        m[3].metric('Residual heat',f"{thermal['loss'].value/1e6:.2f} MW")
        m[4].metric('Steam demand',f"{steam_demand:.2f} kg/s")

        left,right=st.columns(2)
        with left:
            st.markdown('##### Heat accounting')
            st.bar_chart({'MW':{
                'Radiant':radiant.value/1e6,
                'Convection':convection.value/1e6,
                'Residual':thermal['loss'].value/1e6
            }})
            if thermal['loss'].value<0:
                st.warning('Radiant + convection exceed chemical input. The model exposes the inconsistent accounting rather than hiding it.')
        with right:
            st.markdown('##### Six-zone inlet firing')
            st.bar_chart({'MW':{z:v/1e6 for z,v in zip('ABCDEF',alloc['zones'])}})
            st.caption(f"Inlet = {alloc['inlet']/1e6:.2f} MW • Outlet = {alloc['outlet']/1e6:.2f} MW • Conservation residual = {alloc['residual']:.3e} W")

        t1,t2,t3=st.tabs(['Combustion','Firing & control','Model limits'])
        with t1:
            st.json({
                'composition':composition,
                'LHV_MJ_per_kg':lhv_value.value/1e6,
                'actual_air_mol_per_mol_fuel':combustion['actual_air'].value,
                'wet_O2_percent':100*combustion['wet_o2'].value,
                'dry_O2_percent':100*combustion['dry_o2'].value
            })
        with t2:
            st.write('Active functional authority:',active_authority)
            st.write(f"Outlet bottom firing = {alloc['outlet_bottom']/1e6:.2f} MW")
            st.write(f"Outlet sidewall firing = {alloc['outlet_sidewall']/1e6:.2f} MW")
            st.write('Furnace draft input:',f'{draft_pa:.0f} Pa(g)')
            st.info('Draft is displayed as a teaching input only. No draft-to-airflow, fan-curve or flame-shape calculation is implemented.')
        with t3:
            st.write('Changing chemical duty does not predict a new COT, cracking conversion, coke thickness, tube-metal temperature or valve position.')
            st.write('Zone correction is an explicit teaching redistribution. A temperature error does not automatically generate a firing increment.')
            st.write('The simulator is static: it does not integrate time or predict transient furnace response.')

    st.image(str(ROOT/'assets/furnace.svg'))
    st.caption('The public schematic is conceptual and not to scale.')

elif page=='Thermal performance':
    metrics()
    st.bar_chart({'Duty / MW':{'Radiant':parameter('thermal','radiant').value/1e6,'Convection':parameter('thermal','convection').value/1e6,'Residual':s['heat_balance']['loss']['value']/1e6}})
    st.write('Residual heat is the difference between chemical input and useful accounting terms. It is not an identified wall or stack loss.')
    st.json(s['heat_balance'])
    st.caption('These fixed reference duties are not recomputed from scenario control requests.')

elif page=='Fuel comparison':
    rows=[]
    for case in ('baseline','high_mass_lhv','lower_mass_lhv'):
        p=fuel_properties(case)
        rows.append({'Fuel':case,'LHV / MJ kg⁻¹':p['lhv'].value/1e6,'Lower Wobbe / MJ Nm⁻³':p['wobbe'].value/1e6,'Equivalent fuel / kg s⁻¹':fuel_required(parameter('thermal','fired'),p['lhv']).value})
    st.dataframe(rows,hide_index=True)
    excess=st.slider('Declared excess-air fraction',0.0,0.5,0.15,0.01)
    chosen=st.selectbox('Combustion composition',['baseline','high_mass_lhv','lower_mass_lhv'])
    combustion=complete_combustion(fuel_properties(chosen)['composition'].value,excess)
    st.json({k:v.to_dict() for k,v in combustion.items()})
    st.caption('Complete ideal combustion. Normal volume: 273.15 K, 100 kPa absolute. Wobbe comparison is not a valve-opening prediction.')

elif page=='Firing distribution':
    if s['allocation']['value'] is None:
        st.info('UNAVAILABLE: allocation withheld in this teaching state.')
    else:
        a=s['allocation']['value']
        st.bar_chart({'Inlet zone duty / MW':{z:v/1e6 for z,v in zip('ABCDEF',a['zones'])}})
        st.dataframe([{'Location':k,'Duty / MW':a[k]/1e6} for k in ('inlet','outlet','outlet_bottom','outlet_sidewall')],hide_index=True)
        st.write('Conservation residual / W:',a['residual'])
        st.json(burner_loads(a,parameter('distribution','bottom_burners').value,parameter('distribution','sidewall_burners').value))
        st.caption('Per-burner values use synthetic counts and equal-loading assumptions. Inlet firing is assigned to bottom burners for this example.')
    st.json(s['zone_requests'])
    st.write('Directional requests do not automatically change physical shares.')

elif page=='Control architecture':
    st.image(str(ROOT/'assets/control.svg'))
    st.write('Active authority:',s['active_authority'])
    for name,path in PATHS.items():
        st.write(name,':',path)
    st.write('No numerical PID, feed-forward, external reset, draft-flow or valve response is implemented.')

elif page=='Scenario Lab':
    st.subheader(SCENARIOS[scenario])
    explanation()
    st.write('Verified current snapshot')
    st.json(s)
    if st.checkbox('Include bounded supervisor analysis'):
        demo=st.checkbox('Use deterministic contract demo (not AI)')
        st.json(assess(s,CatalogueDemo() if demo else None))

elif page=='AI Engineering Supervisor':
    st.subheader('Bounded AI Engineering Supervisor')
    st.write('Verified state → minimized evidence pack → optional provider → validator → accepted response or deterministic fallback.')
    demo=st.checkbox('Use deterministic contract demo (not AI)')
    st.json(assess(s,CatalogueDemo() if demo else None))
    with st.expander('Current evidence pack'):
        st.json(grounding_pack(s))
    st.write('The demo exercises a software contract. No model intelligence, plant optimization or safety authority is established.')

else:
    st.subheader('Model boundaries')
    st.write('Supported: declared combustion, reference heat accounting, conserved firing allocation, illustrative selection, functional state scenarios and bounded explanations.')
    st.write('Not claimed: CFD, flame prediction, cracking or coking kinetics, tube life, identified dynamics/PID, calibrated valve or draft-airflow response, plant safety assessment, APC/BMS replacement or plant-validated AI optimization.')
    st.json(s['unavailable'])
    st.json(assumptions())

st.divider()
st.caption('Independently reconstructed educational research software. Not a plant operating tool, safety system or commercial digital twin. No validated transient prediction.')
