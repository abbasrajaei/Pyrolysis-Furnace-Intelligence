from pathlib import Path
import streamlit as st
from pyrolysis_furnace_intelligence.cases import parameter,assumptions
from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS,run_scenario
from pyrolysis_furnace_intelligence.fuels import fuel_properties,fuel_required
from pyrolysis_furnace_intelligence.combustion import complete_combustion
from pyrolysis_furnace_intelligence.burners import burner_loads
from pyrolysis_furnace_intelligence.control_paths import PATHS
from pyrolysis_furnace_intelligence.explanations import explain
from pyrolysis_furnace_intelligence.supervisor_service import assess,CatalogueDemo
from pyrolysis_furnace_intelligence.grounding import grounding_pack
ROOT=Path(__file__).resolve().parents[1]
PAGES=['Overview','Thermal performance','Fuel comparison','Firing distribution','Control architecture','Scenario Lab','AI Engineering Supervisor','Model boundaries']
st.set_page_config(page_title='Pyrolysis Furnace Intelligence',layout='wide')
st.title('Pyrolysis Furnace Intelligence')
st.caption('Educational static engineering model • Declared teaching data • No plant operating authority')
page=st.sidebar.radio('Workspace',PAGES)
scenario=st.sidebar.selectbox('Teaching scenario',list(SCENARIOS),format_func=lambda k:SCENARIOS[k])
s=run_scenario(scenario)
st.sidebar.caption('Events change functional interpretation. They do not simulate elapsed time.')
def metrics():
    c=st.columns(3);c[0].metric('Chemical duty',f"{s['fired_duty']['value']/1e6:.1f} MW")
    c[1].metric('Reference useful duty',f"{s['heat_balance']['useful']['value']/1e6:.1f} MW")
    c[2].metric('Reference efficiency',f"{100*s['heat_balance']['efficiency']['value']:.2f}%")
def explanation():
    for line in explain(s):st.write(line)
if page=='Overview':
    metrics();st.image(str(ROOT/'assets/furnace.svg'));explanation()
    st.write('Six illustrative inlet zones, two process passes, bottom and sidewall firing, and a separate outlet split connect chemical duty to allocation bookkeeping.')
elif page=='Thermal performance':
    metrics();st.bar_chart({'Duty / MW':{'Radiant':parameter('thermal','radiant').value/1e6,'Convection':parameter('thermal','convection').value/1e6,'Residual':s['heat_balance']['loss']['value']/1e6}})
    st.write('Residual heat is the difference between chemical input and useful accounting terms. It is not an identified wall or stack loss.')
    st.json(s['heat_balance']);st.caption('These fixed reference duties are not recomputed from scenario control requests.')
elif page=='Fuel comparison':
    rows=[]
    for case in ('baseline','high_mass_lhv','lower_mass_lhv'):
        p=fuel_properties(case);rows.append({'Fuel':case,'LHV / MJ kg⁻¹':p['lhv'].value/1e6,'Lower Wobbe / MJ Nm⁻³':p['wobbe'].value/1e6,'Equivalent fuel / kg s⁻¹':fuel_required(parameter('thermal','fired'),p['lhv']).value})
    st.dataframe(rows,hide_index=True)
    excess=st.slider('Declared excess-air fraction',0.0,0.5,0.15,0.01)
    chosen=st.selectbox('Combustion composition',['baseline','high_mass_lhv','lower_mass_lhv'])
    combustion=complete_combustion(fuel_properties(chosen)['composition'].value,excess)
    st.json({k:v.to_dict() for k,v in combustion.items()})
    st.caption('Complete ideal combustion. Normal volume: 273.15 K, 100 kPa absolute. Wobbe comparison is not a valve-opening prediction.')
elif page=='Firing distribution':
    if s['allocation']['value'] is None:st.info('UNAVAILABLE: allocation withheld in this teaching state.')
    else:
        a=s['allocation']['value'];st.bar_chart({'Inlet zone duty / MW':{z:v/1e6 for z,v in zip('ABCDEF',a['zones'])}})
        st.dataframe([{'Location':k,'Duty / MW':a[k]/1e6} for k in ('inlet','outlet','outlet_bottom','outlet_sidewall')],hide_index=True)
        st.write('Conservation residual / W:',a['residual'])
        st.json(burner_loads(a,parameter('distribution','bottom_burners').value,parameter('distribution','sidewall_burners').value))
        st.caption('Per-burner values use synthetic counts and equal-loading assumptions. Inlet firing is assigned to bottom burners for this example.')
    st.json(s['zone_requests']);st.write('Directional requests do not automatically change physical shares.')
elif page=='Control architecture':
    st.image(str(ROOT/'assets/control.svg'));st.write('Active authority:',s['active_authority'])
    for name,path in PATHS.items():st.write(name,':',path)
    st.write('No numerical PID, feed-forward, external reset, draft-flow or valve response is implemented.')
elif page=='Scenario Lab':
    st.subheader(SCENARIOS[scenario]);explanation()
    st.write('Verified current snapshot');st.json(s)
    if st.checkbox('Include bounded supervisor analysis'):
        demo=st.checkbox('Use deterministic contract demo (not AI)')
        st.json(assess(s,CatalogueDemo() if demo else None))
elif page=='AI Engineering Supervisor':
    st.subheader('Bounded AI Engineering Supervisor')
    st.write('Verified state → minimized evidence pack → optional provider → validator → accepted response or deterministic fallback.')
    demo=st.checkbox('Use deterministic contract demo (not AI)')
    st.json(assess(s,CatalogueDemo() if demo else None))
    with st.expander('Current evidence pack'):st.json(grounding_pack(s))
    st.write('The demo exercises a software contract. No model intelligence, plant optimization or safety authority is established.')
else:
    st.subheader('Model boundaries')
    st.write('Supported: declared combustion, reference heat accounting, conserved firing allocation, illustrative selection, functional state scenarios and bounded explanations.')
    st.write('Not claimed: CFD, flame prediction, cracking or coking kinetics, tube life, identified dynamics/PID, calibrated valve or draft-airflow response, plant safety assessment, APC/BMS replacement or plant-validated AI optimization.')
    st.json(s['unavailable']);st.json(assumptions())
st.divider();st.caption('Independently reconstructed educational research software. Not a plant operating tool, safety system or commercial digital twin. No validated transient prediction.')
