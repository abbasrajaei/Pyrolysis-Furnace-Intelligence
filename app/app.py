import os
from copy import deepcopy

from dash import Dash, dcc, html, Input, Output, State, ctx, no_update
import plotly.graph_objects as go

from pyrolysis_furnace_intelligence.workbench import (
    BASE_CASE, PRESETS, COMPONENTS, rebalance_composition, evaluate_case
)
from pyrolysis_furnace_intelligence.sensitivity import (
    INPUTS, OUTPUTS, SUPPORTED, sweep
)
from pyrolysis_furnace_intelligence.guidance import guidance
from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS, run_scenario
from pyrolysis_furnace_intelligence.explanations import explain

PLOT_CONFIG={
    'displaylogo':False,
    'responsive':True,
    'modeBarButtonsToRemove':['lasso2d','select2d']
}

COLORS={
    'blue':'#1f6f85',
    'blue2':'#2d8ca4',
    'teal':'#2b7d70',
    'amber':'#c47b2a',
    'slate':'#8aa2ad',
    'ink':'#173443',
    'grid':'#e2e8ec',
    'bg':'#ffffff'
}

DEFAULT_OUTPUT={
    'h2_fraction':'fuel_flow','ch4_fraction':'fuel_flow','c2h6_fraction':'fuel_flow','n2_fraction':'fuel_flow',
    'excess_air':'dry_o2','chemical_duty':'fuel_flow','heat_recovery':'residual_heat',
    'radiant_share':'radiant_duty','inlet_outlet_ratio':'inlet_firing','bottom_side_ratio':'outlet_bottom',
    'feed_rate':'steam_demand','steam_feed_ratio':'steam_demand','zone_correction':'max_zone',
    'draft_pressure':'relative_airflow'
}

LAST_TO_SENS={
    'H2':'h2_fraction','CH4':'ch4_fraction','C2H6':'c2h6_fraction','N2':'n2_fraction',
    'duty_mw':'chemical_duty','excess_air':'excess_air','draft_pa':'draft_pressure',
    'heat_recovery':'heat_recovery','radiant_share':'radiant_share',
    'inlet_outlet_ratio':'inlet_outlet_ratio','bottom_side_ratio':'bottom_side_ratio',
    'feed_kg_s':'feed_rate','steam_ratio':'steam_feed_ratio','zone':'zone_correction',
    'zone_correction':'zone_correction','pressure_state':'chemical_duty'
}

app=Dash(
    __name__,
    title='Pyrolysis Furnace Intelligence',
    assets_folder=os.path.join(os.path.dirname(__file__),'assets'),
    suppress_callback_exceptions=True
)
server=app.server

def pct(v):
    return f'{100*v:.1f}%'

def kpi(label,value,delta=None):
    delta_class='delta-flat'
    if isinstance(delta,(int,float)):
        if delta>1e-9:delta_class='delta-up'
        elif delta<-1e-9:delta_class='delta-down'
        delta_text=f'{delta:+.2f}% vs baseline'
    else:
        delta_text=delta or ''
    return html.Div([
        html.Div(label,className='kpi-label'),
        html.Div(value,className='kpi-value'),
        html.Div(delta_text,className=f'kpi-delta {delta_class}')
    ],className='kpi')

def figure_layout(fig,title=None):
    fig.update_layout(
        paper_bgcolor='white',plot_bgcolor='white',
        margin=dict(l=48,r=20,t=55 if title else 30,b=48),
        font=dict(family='Inter, Segoe UI, sans-serif',color=COLORS['ink'],size=12),
        hoverlabel=dict(bgcolor='white',font_size=12),
        legend=dict(orientation='h',yanchor='bottom',y=1.01,xanchor='left',x=0),
        title=dict(text=title,x=.01,xanchor='left',font=dict(size=17)),
        xaxis=dict(gridcolor=COLORS['grid'],zeroline=False),
        yaxis=dict(gridcolor=COLORS['grid'],zeroline=False)
    )
    return fig

def sensitivity_figure(input_name,output_name,case,baseline=None,title=None):
    data=sweep(input_name,output_name,case)
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=data['x'],y=data['y'],mode='lines',
        line=dict(color=COLORS['blue'],width=3),
        name='Sensitivity'
    ))
    fig.add_trace(go.Scatter(
        x=[data['current_x']],y=[data['current_y']],mode='markers',
        marker=dict(size=12,color=COLORS['amber'],line=dict(width=2,color='white')),
        name='Current'
    ))
    if baseline is not None:
        b=sweep(input_name,output_name,baseline)
        fig.add_trace(go.Scatter(
            x=[b['current_x']],y=[b['current_y']],mode='markers',
            marker=dict(size=10,color=COLORS['slate'],symbol='diamond'),
            name='Baseline'
        ))
    fig.update_xaxes(title=data['x_label'])
    fig.update_yaxes(title=data['y_label'])
    figure_layout(fig,title or f"{data['x_label']} → {data['y_label']}")
    return fig,data

def zone_figure(result,baseline_result):
    zones=list('ABCDEF')
    fig=go.Figure()
    fig.add_trace(go.Bar(x=zones,y=baseline_result['firing']['zones_mw'],name='Baseline',marker_color=COLORS['slate']))
    fig.add_trace(go.Bar(x=zones,y=result['firing']['zones_mw'],name='Current',marker_color=COLORS['blue']))
    fig.update_layout(barmode='group')
    fig.update_xaxes(title='Inlet firing zone')
    fig.update_yaxes(title='Duty / MW')
    return figure_layout(fig,'Six-zone inlet firing')

def energy_figure(result):
    t=result['thermal']
    residual=max(t['residual_mw'],0)
    fig=go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            pad=18,thickness=22,line=dict(color='white',width=1),
            label=['Chemical input','Radiant duty','Convection duty','Residual'],
            color=[COLORS['ink'],COLORS['blue'],COLORS['teal'],COLORS['slate']]
        ),
        link=dict(
            source=[0,0,0],target=[1,2,3],
            value=[t['radiant_mw'],t['convection_mw'],residual],
            color=['rgba(31,111,133,.35)','rgba(43,125,112,.35)','rgba(138,162,173,.30)']
        )
    ))
    return figure_layout(fig,'Static heat-accounting path')

def composition_figure(case):
    comp=case['composition']
    fig=go.Figure()
    left=0
    palette={'H2':'#2d8ca4','CH4':'#1f6f85','C2H6':'#2b7d70','N2':'#8aa2ad'}
    for name in COMPONENTS:
        fig.add_trace(go.Bar(
            y=['Fuel'],x=[100*comp[name]],orientation='h',
            name=name,marker_color=palette[name],
            text=[f"{name} {100*comp[name]:.1f}%"],textposition='inside'
        ))
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title='Mole fraction / %',range=[0,100])
    return figure_layout(fig,'Fuel composition')

def split_figure(result):
    f=result['firing']
    fig=go.Figure(go.Pie(
        labels=['Inlet','Outlet bottom','Outlet sidewall'],
        values=[f['inlet_mw'],f['outlet_bottom_mw'],f['outlet_sidewall_mw']],
        hole=.58,
        marker=dict(colors=[COLORS['blue'],COLORS['teal'],COLORS['amber']]),
        textinfo='label+percent'
    ))
    fig.update_layout(annotations=[dict(text=f"{sum([f['inlet_mw'],f['outlet_bottom_mw'],f['outlet_sidewall_mw']]):.0f} MW",x=.5,y=.5,font_size=18,showarrow=False)])
    return figure_layout(fig,'Firing distribution')

def comparison_table(current,baseline):
    rows=[
        ('Equivalent fuel / kg s⁻¹',baseline['fuel']['equivalent_fuel_kg_s'],current['fuel']['equivalent_fuel_kg_s']),
        ('Mass LHV / MJ kg⁻¹',baseline['fuel']['lhv_MJ_kg'],current['fuel']['lhv_MJ_kg']),
        ('Dry O₂ / %',baseline['combustion']['dry_o2_pct'],current['combustion']['dry_o2_pct']),
        ('Radiant duty / MW',baseline['thermal']['radiant_mw'],current['thermal']['radiant_mw']),
        ('Residual heat / MW',baseline['thermal']['residual_mw'],current['thermal']['residual_mw']),
        ('Maximum zone / MW',baseline['firing']['max_zone_mw'],current['firing']['max_zone_mw']),
        ('Steam demand / kg s⁻¹',baseline['process']['steam_demand_kg_s'],current['process']['steam_demand_kg_s'])
    ]
    return html.Table([
        html.Thead(html.Tr([html.Th('Variable'),html.Th('Baseline'),html.Th('Current'),html.Th('Change')])),
        html.Tbody([
            html.Tr([
                html.Td(name),html.Td(f'{b:.3f}'),html.Td(f'{c:.3f}'),
                html.Td(f'{((c/b)-1)*100:+.2f}%' if abs(b)>1e-12 else '—')
            ]) for name,b,c in rows
        ])
    ],className='compare-table')

def guidance_panel(g):
    def block(title,body):
        if isinstance(body,list):
            body=html.Ul([html.Li(x) for x in body])
        else:
            body=html.P(body)
        return html.Div([html.H4(title),body],className='guidance-block')
    d=g['deltas']
    return [
        html.Div([
            html.Div('Engineering Guidance',className='guidance-title'),
            html.Span('LIVE',className='basis-chip')
        ],className='guidance-head'),
        html.Div(g['change'],className='guidance-change'),
        block('Why',g['why']),
        block('Immediate consequence',g['effects']),
        html.Div([
            html.Div('Fuel demand',className='comp-name'),
            html.Div(f"{d['fuel_flow_pct']:+.2f}%",className='comp-value'),
            html.Div('vs baseline',className='small')
        ],className='comp-cell'),
        html.Div([
            html.Div('Dry O₂',className='comp-name'),
            html.Div(f"{d['dry_o2_delta_pctpt']:+.2f} pt",className='comp-value'),
            html.Div('vs baseline',className='small')
        ],className='comp-cell'),
        block('Watch',g['watch']),
        html.Div([
            html.H4('Model basis'),
            html.Div([html.Span(x,className='basis-chip') for x in g['basis']])
        ],className='guidance-block'),
        block('Not inferred',g['limits'])
    ]

def page_header(title,subtitle,basis='CALCULATED / SYNTHETIC'):
    return html.Div([
        html.Div([html.H2(title,className='study-title'),html.Div(subtitle,className='study-sub')]),
        html.Span(basis,className='basis-chip')
    ],className='study-header')

def graph(fig):
    return dcc.Graph(figure=fig,config=PLOT_CONFIG,style={'height':'390px'})

app.layout=html.Div([
    dcc.Store(id='composition-store',data=deepcopy(BASE_CASE['composition'])),
    dcc.Store(id='fuel-last-change',data='H2'),
    dcc.Store(id='current-store',data=deepcopy(BASE_CASE)),
    dcc.Store(id='baseline-store',data=deepcopy(BASE_CASE)),
    dcc.Store(id='last-changed-store',data='duty_mw'),
    dcc.Store(id='saved-cases',data=[]),

    html.Div([
        html.Div([
            html.Div('Pyrolysis Furnace Intelligence',className='brand-title'),
            html.Div('Furnace Engineering Workbench',className='brand-subtitle')
        ]),
        html.Div([
            html.Span('INTERACTIVE STUDY',className='badge ok'),
            html.Span('SYNTHETIC PUBLIC MODEL',className='badge'),
            html.Span('NO PLANT AUTHORITY',className='badge model')
        ],className='status-row')
    ],className='topbar'),

    html.Div([
        dcc.Tabs(
            id='workspace-tab',value='overview',className='nav-tabs',
            children=[
                dcc.Tab(label='Furnace Overview',value='overview',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Scenario Studio',value='scenario',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Combustion',value='combustion',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Thermal Performance',value='thermal',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Firing & Zones',value='firing',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Control Response',value='control',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Sensitivity Lab',value='sensitivity',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Case Comparison',value='compare',className='tab',selected_className='tab--selected'),
                dcc.Tab(label='Model Limits',value='limits',className='tab',selected_className='tab--selected')
            ]
        )
    ],className='nav-wrap'),

    html.Div([
        html.Div([
            html.Div([
                html.Div('Study case',className='card-title'),
                html.Div('Preset',className='control-label'),
                dcc.Dropdown(id='preset-select',options=list(PRESETS),value='Baseline',clearable=False),
                html.Div([
                    html.Button('Load preset',id='load-preset',className='btn primary'),
                    html.Button('Reset',id='reset-case',className='btn')
                ],className='action-row'),
                html.Div([
                    html.Button('Set as baseline',id='set-baseline',className='btn'),
                    html.Button('Save case',id='save-case',className='btn')
                ],className='action-row'),
                dcc.Input(id='case-name',placeholder='Case name',type='text',style={'width':'100%','marginTop':'8px'}),
                html.Div(id='save-status',className='small',style={'marginTop':'6px'})
            ],className='card'),

            html.Div([
                html.Div('Operating conditions',className='card-title'),
                html.Div('Chemical duty / MW',className='control-label'),
                dcc.Slider(30,90,1,value=60,id='duty',tooltip={'placement':'bottom'}),
                html.Div('Excess-air fraction',className='control-label'),
                dcc.Slider(0,.40,.01,value=.15,id='excess-air',tooltip={'placement':'bottom'}),
                html.Div('Furnace draft / Pa(g)',className='control-label'),
                dcc.Slider(-100,0,5,value=-40,id='draft',tooltip={'placement':'bottom'}),

                html.Div('Fuel composition',className='section-label'),
                html.Div(id='composition-display',className='comp-grid'),
                html.Div('Adjust component',className='control-label'),
                dcc.Dropdown(id='fuel-component',options=[{'label':k,'value':k} for k in COMPONENTS],value='H2',clearable=False),
                html.Div(id='selected-fuel-current',className='small',style={'marginTop':'5px'}),
                html.Div('Target mole fraction',className='control-label'),
                dcc.Slider(0,1,.01,value=.20,id='fuel-target',tooltip={'placement':'bottom'}),
                dcc.Checklist(
                    id='fuel-locks',
                    options=[{'label':f'Lock {k}','value':k} for k in COMPONENTS],
                    value=[],
                    labelStyle={'display':'inline-block','fontSize':'11px','marginRight':'8px','marginTop':'6px'}
                ),
                html.Div(id='composition-note',className='small',style={'marginTop':'6px'}),

                html.Div('Heat distribution',className='section-label'),
                html.Div('Useful heat recovery',className='control-label'),
                dcc.Slider(.75,.98,.01,value=55/60,id='heat-recovery',tooltip={'placement':'bottom'}),
                html.Div('Radiant share of useful heat',className='control-label'),
                dcc.Slider(.35,.65,.01,value=27/55,id='radiant-share',tooltip={'placement':'bottom'}),

                html.Div('Firing & process',className='section-label'),
                html.Div('Inlet / outlet firing ratio',className='control-label'),
                dcc.Slider(.5,3,.1,value=1.5,id='inout-ratio',tooltip={'placement':'bottom'}),
                html.Div('Outlet bottom / side ratio',className='control-label'),
                dcc.Slider(.25,4,.25,value=1,id='bottomside-ratio',tooltip={'placement':'bottom'}),
                html.Div('Feed / kg s⁻¹',className='control-label'),
                dcc.Slider(4,14,.5,value=8,id='feed',tooltip={'placement':'bottom'}),
                html.Div('Steam / feed ratio',className='control-label'),
                dcc.Slider(.1,.8,.05,value=.35,id='steam-ratio',tooltip={'placement':'bottom'}),
                html.Div('Zone correction',className='control-label'),
                dcc.Dropdown(id='zone-select',options=['None','A','B','C','D','E','F'],value='None',clearable=False),
                dcc.Slider(-.05,.05,.005,value=0,id='zone-correction',tooltip={'placement':'bottom'}),
                html.Div('Fuel-pressure authority',className='control-label'),
                dcc.Dropdown(
                    id='pressure-state',
                    options=['Normal','Low-pressure constraint','High-pressure constraint'],
                    value='Normal',clearable=False
                )
            ],className='card'),

            html.Div([
                html.Div('Scenario / analysis',className='card-title'),
                html.Div('Scenario template',className='control-label'),
                dcc.Dropdown(
                    id='scenario-select',
                    options=[{'label':v,'value':k} for k,v in SCENARIOS.items()],
                    value='normal',clearable=False
                ),
                html.Div('Sensitivity input',className='control-label'),
                dcc.Dropdown(
                    id='sens-x',
                    options=[{'label':v[0],'value':k} for k,v in INPUTS.items()],
                    value='h2_fraction',clearable=False
                ),
                html.Div('Sensitivity output',className='control-label'),
                dcc.Dropdown(id='sens-y',value='fuel_flow',clearable=False)
            ],className='card')
        ],className='left-rail'),

        html.Div(id='page-content'),

        html.Div([
            html.Div(id='guidance-content',className='card')
        ],className='guidance-rail')
    ],className='workspace-grid')
],className='workbench')

@app.callback(
    Output('composition-store','data',allow_duplicate=True),
    Output('fuel-last-change','data'),
    Output('composition-note','children'),
    Input('fuel-target','value'),
    State('fuel-component','value'),
    State('fuel-locks','value'),
    State('composition-store','data'),
    prevent_initial_call=True
)
def adjust_fuel(target,component,locks,composition):
    updated=rebalance_composition(composition,component,target,locks)
    note=f"{component} set to {updated[component]:.3f}; unlocked components automatically renormalized to keep Σx = 1.000."
    return updated,component,note

@app.callback(
    Output('composition-display','children'),
    Output('selected-fuel-current','children'),
    Input('composition-store','data'),
    Input('fuel-component','value')
)
def show_composition(comp,selected):
    cells=[
        html.Div([
            html.Div(k,className='comp-name'),
            html.Div(f"{100*comp[k]:.1f}%",className='comp-value')
        ],className='comp-cell') for k in COMPONENTS
    ]
    return cells,f"Current {selected} = {100*comp[selected]:.1f} mol%. Move the target slider to change it."

@app.callback(
    Output('composition-store','data'),
    Output('duty','value'),
    Output('excess-air','value'),
    Output('draft','value'),
    Output('heat-recovery','value'),
    Output('radiant-share','value'),
    Output('inout-ratio','value'),
    Output('bottomside-ratio','value'),
    Output('feed','value'),
    Output('steam-ratio','value'),
    Output('zone-select','value'),
    Output('zone-correction','value'),
    Output('pressure-state','value'),
    Input('load-preset','n_clicks'),
    Input('reset-case','n_clicks'),
    State('preset-select','value'),
    State('baseline-store','data'),
    prevent_initial_call=True
)
def load_or_reset(_load,_reset,preset,baseline):
    selected=deepcopy(PRESETS[preset] if ctx.triggered_id=='load-preset' else baseline)
    return (
        selected['composition'],selected['duty_mw'],selected['excess_air'],selected['draft_pa'],
        selected['heat_recovery'],selected['radiant_share'],selected['inlet_outlet_ratio'],
        selected['bottom_side_ratio'],selected['feed_kg_s'],selected['steam_ratio'],
        selected['zone'],selected['zone_correction'],selected['pressure_state']
    )

@app.callback(
    Output('current-store','data'),
    Output('last-changed-store','data'),
    Input('composition-store','data'),
    Input('fuel-last-change','data'),
    Input('duty','value'),
    Input('excess-air','value'),
    Input('draft','value'),
    Input('heat-recovery','value'),
    Input('radiant-share','value'),
    Input('inout-ratio','value'),
    Input('bottomside-ratio','value'),
    Input('feed','value'),
    Input('steam-ratio','value'),
    Input('zone-select','value'),
    Input('zone-correction','value'),
    Input('pressure-state','value')
)
def build_case(comp,fuel_last,duty,excess,draft,recovery,rad_share,inout,bottomside,feed,steam,zone,correction,pressure):
    current={
        'duty_mw':float(duty),'composition':comp,'excess_air':float(excess),'draft_pa':float(draft),
        'heat_recovery':float(recovery),'radiant_share':float(rad_share),
        'inlet_outlet_ratio':float(inout),'bottom_side_ratio':float(bottomside),
        'feed_kg_s':float(feed),'steam_ratio':float(steam),'zone':zone,
        'zone_correction':float(correction),'pressure_state':pressure
    }
    trigger=ctx.triggered_id
    mapping={
        'duty':'duty_mw','excess-air':'excess_air','draft':'draft_pa',
        'heat-recovery':'heat_recovery','radiant-share':'radiant_share',
        'inout-ratio':'inlet_outlet_ratio','bottomside-ratio':'bottom_side_ratio',
        'feed':'feed_kg_s','steam-ratio':'steam_ratio','zone-select':'zone',
        'zone-correction':'zone_correction','pressure-state':'pressure_state'
    }
    if trigger in ('composition-store','fuel-last-change'):
        last=fuel_last or 'H2'
    else:
        last=mapping.get(trigger,'duty_mw')
    return current,last

@app.callback(
    Output('baseline-store','data'),
    Input('set-baseline','n_clicks'),
    State('current-store','data'),
    prevent_initial_call=True
)
def set_baseline(_n,current):
    return deepcopy(current)

@app.callback(
    Output('saved-cases','data'),
    Output('save-status','children'),
    Input('save-case','n_clicks'),
    State('case-name','value'),
    State('current-store','data'),
    State('saved-cases','data'),
    prevent_initial_call=True
)
def save_case(_n,name,current,saved):
    saved=list(saved or [])
    label=(name or f'Case {len(saved)+1}').strip()
    saved.append({'name':label,'case':deepcopy(current)})
    return saved[-8:],f"Saved “{label}” for comparison."

@app.callback(
    Output('sens-y','options'),
    Output('sens-y','value'),
    Input('sens-x','value'),
    State('sens-y','value')
)
def sensitivity_outputs(x,current):
    choices=SUPPORTED[x]
    options=[{'label':OUTPUTS[k][0],'value':k} for k in choices]
    return options,current if current in choices else DEFAULT_OUTPUT[x]

@app.callback(
    Output('guidance-content','children'),
    Input('current-store','data'),
    Input('baseline-store','data'),
    Input('last-changed-store','data')
)
def render_guidance(current,baseline,last):
    return guidance_panel(guidance(last,current,baseline))

@app.callback(
    Output('page-content','children'),
    Input('workspace-tab','value'),
    Input('current-store','data'),
    Input('baseline-store','data'),
    Input('last-changed-store','data'),
    Input('scenario-select','value'),
    Input('sens-x','value'),
    Input('sens-y','value'),
    Input('saved-cases','data')
)
def render_page(tab,current,baseline,last,scenario_name,sens_x,sens_y,saved):
    result=evaluate_case(current);base=evaluate_case(baseline)
    fuel_delta=100*(result['fuel']['equivalent_fuel_kg_s']/base['fuel']['equivalent_fuel_kg_s']-1)
    o2_delta=result['combustion']['dry_o2_pct']-base['combustion']['dry_o2_pct']
    zone_delta=100*(result['firing']['max_zone_mw']/base['firing']['max_zone_mw']-1)
    steam_delta=100*(result['process']['steam_demand_kg_s']/base['process']['steam_demand_kg_s']-1)

    if tab=='overview':
        default_x=LAST_TO_SENS.get(last,'chemical_duty')
        default_y=DEFAULT_OUTPUT[default_x]
        sf,_=sensitivity_figure(default_x,default_y,current,baseline,'Response to the parameter you changed')
        return html.Div([
            page_header('Furnace Overview','One-screen operating study: current state, baseline deviation, sensitivity and firing distribution.'),
            html.Div([
                kpi('Equivalent fuel',f"{result['fuel']['equivalent_fuel_kg_s']:.3f} kg/s",fuel_delta),
                kpi('Dry O₂',f"{result['combustion']['dry_o2_pct']:.2f}%",f"{o2_delta:+.2f} percentage points"),
                kpi('Mass LHV',f"{result['fuel']['lhv_MJ_kg']:.2f} MJ/kg"),
                kpi('Heat recovery',f"{result['thermal']['accounting_efficiency_pct']:.1f}%"),
                kpi('Max zone duty',f"{result['firing']['max_zone_mw']:.2f} MW",zone_delta),
                kpi('Steam demand',f"{result['process']['steam_demand_kg_s']:.2f} kg/s",steam_delta)
            ],className='kpi-grid'),
            html.Div([
                html.Div([graph(sf)],className='chart-card'),
                html.Div([graph(zone_figure(result,base))],className='chart-card')
            ],className='two-col'),
            html.Div([
                html.Div([graph(energy_figure(result))],className='chart-card'),
                html.Div([
                    html.Div('Baseline → current',className='panel-title'),
                    html.Div('Every study stays anchored to a comparison state.',className='panel-subtitle'),
                    comparison_table(result,base)
                ],className='chart-card')
            ],className='two-col')
        ])

    if tab=='combustion':
        fuel_input={'H2':'h2_fraction','CH4':'ch4_fraction','C2H6':'c2h6_fraction','N2':'n2_fraction'}.get(last,'h2_fraction')
        fig1,_=sensitivity_figure(fuel_input,'fuel_flow',current,baseline,'Fuel composition → equivalent fuel demand')
        fig2,_=sensitivity_figure(fuel_input,'wobbe',current,baseline,'Fuel composition → lower Wobbe')
        fig3,_=sensitivity_figure('excess_air','dry_o2',current,baseline,'Excess air → dry product O₂')
        return html.Div([
            page_header('Combustion','Explore mixture energy, oxygen requirement and air demand without manually balancing mole fractions.'),
            html.Div([
                kpi('Mass LHV',f"{result['fuel']['lhv_MJ_kg']:.2f} MJ/kg"),
                kpi('Lower Wobbe',f"{result['fuel']['wobbe_MJ_Nm3']:.2f} MJ/Nm³"),
                kpi('Equivalent fuel',f"{result['fuel']['equivalent_fuel_kg_s']:.3f} kg/s",fuel_delta),
                kpi('Stoich. air',f"{result['combustion']['stoich_air_mol_mol']:.3f} mol/mol"),
                kpi('Actual air',f"{result['combustion']['actual_air_mol_mol']:.3f} mol/mol"),
                kpi('Dry O₂',f"{result['combustion']['dry_o2_pct']:.2f}%")
            ],className='kpi-grid'),
            html.Div([
                html.Div([graph(composition_figure(current))],className='chart-card'),
                html.Div([graph(fig1)],className='chart-card')
            ],className='two-col'),
            html.Div([
                html.Div([graph(fig2)],className='chart-card'),
                html.Div([graph(fig3)],className='chart-card')
            ],className='two-col'),
            html.Div('Fuel fractions are always closed to 100% by proportional renormalization of unlocked components. Flame speed, flashback, NOx and burner-stability limits remain qualitative.',className='callout')
        ])

    if tab=='thermal':
        fig1,_=sensitivity_figure('heat_recovery','residual_heat',current,baseline,'Heat recovery → residual heat')
        fig2,_=sensitivity_figure('radiant_share','radiant_duty',current,baseline,'Radiant share → radiant duty')
        return html.Div([
            page_header('Thermal Performance','Static heat accounting with physically consistent useful-duty partition.'),
            html.Div([
                kpi('Chemical input',f"{current['duty_mw']:.1f} MW"),
                kpi('Useful duty',f"{result['thermal']['radiant_mw']+result['thermal']['convection_mw']:.2f} MW"),
                kpi('Radiant',f"{result['thermal']['radiant_mw']:.2f} MW"),
                kpi('Convection',f"{result['thermal']['convection_mw']:.2f} MW"),
                kpi('Residual',f"{result['thermal']['residual_mw']:.2f} MW"),
                kpi('Accounting η',f"{result['thermal']['accounting_efficiency_pct']:.2f}%")
            ],className='kpi-grid'),
            html.Div([
                html.Div([graph(energy_figure(result))],className='chart-card'),
                html.Div([graph(fig1)],className='chart-card')
            ],className='two-col'),
            html.Div([graph(fig2)],className='chart-card'),
            html.Div('The thermal model is an accounting model, not an off-design radiation/convection solver. COT, tube-metal temperature, local flux and cracking kinetics are not inferred.',className='callout warn')
        ])

    if tab=='firing':
        fig1,_=sensitivity_figure('inlet_outlet_ratio','inlet_firing',current,baseline,'Inlet/outlet split → inlet firing')
        fig2,_=sensitivity_figure('zone_correction','max_zone',current,baseline,'Zone correction → maximum zone duty')
        return html.Div([
            page_header('Firing & Zones','Conserved allocation across inlet zones and outlet burner groups.'),
            html.Div([
                kpi('Total firing',f"{current['duty_mw']:.1f} MW"),
                kpi('Inlet firing',f"{result['firing']['inlet_mw']:.2f} MW"),
                kpi('Outlet firing',f"{result['firing']['outlet_mw']:.2f} MW"),
                kpi('Max zone',f"{result['firing']['max_zone_mw']:.2f} MW",zone_delta),
                kpi('Bottom burner',f"{result['firing']['bottom_burner_mw']:.2f} MW"),
                kpi('Conservation',f"{result['firing']['conservation_residual_w']:.1e} W")
            ],className='kpi-grid'),
            html.Div([
                html.Div([graph(zone_figure(result,base))],className='chart-card'),
                html.Div([graph(split_figure(result))],className='chart-card')
            ],className='two-col'),
            html.Div([
                html.Div([graph(fig1)],className='chart-card'),
                html.Div([graph(fig2)],className='chart-card')
            ],className='two-col'),
            html.Div('The selected zone correction is explicit. Temperature error does not automatically generate a numerical firing increment because no identified temperature-to-firing process gain is available.',className='callout')
        ])

    if tab=='control':
        draft_air,_=sensitivity_figure('draft_pressure','relative_airflow',current,baseline,'Draft → relative airflow teaching model')
        draft_ex,_=sensitivity_figure('draft_pressure','implied_excess_air',current,baseline,'Draft → implied excess-air teaching model')
        auth=result['control']['active_authority']
        return html.Div([
            page_header('Control Response','Functional authority and inspectable control consequences without pretending to be a plant DCS.','FUNCTIONAL / MODELLED'),
            html.Div([
                kpi('Active authority',auth.replace('_',' ')),
                kpi('Draft input',f"{current['draft_pa']:.0f} Pa(g)"),
                kpi('Relative airflow model',f"{result['draft_model']['relative_airflow']:.3f} × ref"),
                kpi('Implied excess air',f"{100*result['draft_model']['implied_excess_air']:.1f}%"),
                kpi('Inlet/outlet ratio',f"{current['inlet_outlet_ratio']:.2f}"),
                kpi('Bottom/side ratio',f"{current['bottom_side_ratio']:.2f}")
            ],className='kpi-grid'),
            html.Div([
                html.Div([graph(draft_air)],className='chart-card'),
                html.Div([graph(draft_ex)],className='chart-card')
            ],className='two-col'),
            html.Div([
                html.Div([
                    html.Div('Authority interpretation',className='panel-title'),
                    html.P('Normal fuel-demand authority is superseded when the selected teaching pressure constraint is active. This is a functional authority model only.'),
                    html.Div(f"CURRENT AUTHORITY: {auth}",className='guidance-change')
                ],className='chart-card'),
                html.Div([
                    html.Div('Draft model boundary',className='panel-title'),
                    html.P(result['draft_model']['basis']),
                    html.Div('Real air admission also depends on burner/register position, leakage paths, density and system resistance. The curve is intentionally not presented as plant calibration.',className='callout warn')
                ],className='chart-card')
            ],className='two-col')
        ])

    if tab=='scenario':
        state=run_scenario(scenario_name)
        allocation=state['allocation']['value']
        cards=[
            kpi('Scenario',SCENARIOS[scenario_name]),
            kpi('Operating state',state['operating_state'].replace('_',' ')),
            kpi('Authority',state['active_authority'].replace('_',' ')),
            kpi('Fuel case',state['fuel_case'].replace('_',' ')),
            kpi('Steam demand',f"{state['steam_base_demand']['value']:.2f} kg/s"),
            kpi('Pass balance',state['pass_classification'].replace('_',' '))
        ]
        fig=go.Figure()
        if allocation:
            fig.add_trace(go.Bar(x=list('ABCDEF'),y=[v/1e6 for v in allocation['zones']],marker_color=COLORS['blue']))
            fig.update_yaxes(title='Zone duty / MW');fig.update_xaxes(title='Zone')
        figure_layout(fig,'Scenario firing snapshot')
        return html.Div([
            page_header('Scenario Studio','Start from a named disturbance instead of building every study manually.'),
            html.Div(cards,className='kpi-grid'),
            html.Div([
                html.Div([
                    html.Div('Engineering interpretation',className='panel-title'),
                    *[html.Div(line,className='callout' if i==0 else 'guidance-block') for i,line in enumerate(explain(state))]
                ],className='chart-card'),
                html.Div([graph(fig)] if allocation else [html.Div('Firing allocation is intentionally unavailable in this shutdown teaching state.',className='callout limit')],className='chart-card')
            ],className='two-col'),
            html.Div('Scenario Studio uses thirteen bounded static teaching events. It does not integrate time or predict controller trajectories.',className='callout warn')
        ])

    if tab=='sensitivity':
        fig,data=sensitivity_figure(sens_x,sens_y,current,baseline)
        return html.Div([
            page_header('Sensitivity Lab','Choose any supported input/output pair and inspect the full response curve, current point and baseline.'),
            html.Div([graph(fig)],className='chart-card'),
            html.Div([
                html.Div([
                    html.Div('Engineering basis',className='panel-title'),
                    html.Div(data['basis'],className='guidance-change'),
                    html.P(data['note'] or 'All other declared case inputs are held at their current values during this one-factor sweep.')
                ],className='chart-card'),
                html.Div([
                    html.Div('How to read the curve',className='panel-title'),
                    html.P('The blue line is a one-factor sensitivity sweep. The orange point is the current case. The grey diamond is the baseline. It is not a time trend unless the x-axis is time, and this release contains no time integration.')
                ],className='chart-card')
            ],className='two-col')
        ])

    if tab=='compare':
        cases=[{'name':'Baseline','case':baseline},{'name':'Current','case':current}]+list(saved or [])
        evaluated=[(item['name'],evaluate_case(item['case'])) for item in cases]
        names=[x[0] for x in evaluated]
        fig=go.Figure()
        for label,path in [
            ('Fuel kg/s',('fuel','equivalent_fuel_kg_s')),
            ('Dry O₂ %',('combustion','dry_o2_pct')),
            ('Max zone MW',('firing','max_zone_mw')),
            ('Steam kg/s',('process','steam_demand_kg_s'))
        ]:
            vals=[r[path[0]][path[1]] for _,r in evaluated]
            fig.add_trace(go.Scatter(x=names,y=vals,mode='lines+markers',name=label))
        figure_layout(fig,'Saved-study comparison')
        table_rows=[]
        for name,r in evaluated:
            table_rows.append(html.Tr([
                html.Td(name),
                html.Td(f"{r['fuel']['equivalent_fuel_kg_s']:.3f}"),
                html.Td(f"{r['combustion']['dry_o2_pct']:.2f}"),
                html.Td(f"{r['thermal']['accounting_efficiency_pct']:.2f}"),
                html.Td(f"{r['firing']['max_zone_mw']:.2f}"),
                html.Td(f"{r['process']['steam_demand_kg_s']:.2f}"),
                html.Td(r['control']['active_authority'].replace('_',' '))
            ]))
        table=html.Table([
            html.Thead(html.Tr([html.Th(x) for x in ['Case','Fuel kg/s','Dry O₂ %','η %','Max zone MW','Steam kg/s','Authority']])),
            html.Tbody(table_rows)
        ],className='compare-table')
        return html.Div([
            page_header('Case Comparison','Save operating studies and compare consequences without losing the baseline.'),
            html.Div([graph(fig)],className='chart-card'),
            html.Div([table],className='chart-card'),
            html.Div('Use “Save case” in the left study panel after each investigation. Up to eight saved studies are retained in the current browser session.',className='callout')
        ])

    supported=[
        'Ideal complete combustion for declared H₂ / CH₄ / C₂H₆ / N₂ mixtures',
        'Mass LHV, normal-volume LHV and lower Wobbe teaching calculations',
        'Stoichiometric/actual air and wet/dry product O₂',
        'Static heat accounting with conserved useful-duty partition',
        'Conserved inlet/outlet, bottom/sidewall and six-zone firing allocation',
        'Feed/steam base-demand relationship',
        'Functional fuel-pressure authority states',
        'One-factor sensitivity sweeps for supported relationships',
        'Fixed-resistance draft relative-airflow teaching correlation',
        'Thirteen static scenario templates and deterministic engineering guidance'
    ]
    unavailable=[
        'CFD, local flame shape or local flame temperature',
        'Flame speed, flashback boundary, CO or NOx prediction',
        'Rigorous cracking yield or coking kinetics',
        'Tube-metal temperature, tube life or local radiant flux',
        'Identified furnace time constants or dynamic COT response',
        'Numerical PID tuning, valve characteristic or external-reset dynamics',
        'Calibrated ID-fan curve, register position or leakage-air model',
        'Plant trip, permissive, shutdown or safe-to-continue determination',
        'Plant-validated APC, optimization or autonomous AI control'
    ]
    return html.Div([
        page_header('Model Limits','A strong engineering tool must make its evidence boundary as visible as its calculations.','EXPLICIT BOUNDARIES'),
        html.Div([
            html.Div([
                html.Div('Supported',className='panel-title'),
                html.Ul([html.Li(x) for x in supported])
            ],className='chart-card'),
            html.Div([
                html.Div('Not claimed',className='panel-title'),
                html.Ul([html.Li(x) for x in unavailable])
            ],className='chart-card')
        ],className='two-col'),
        html.Div('The draft sensitivity is explicitly a fixed-resistance teaching correlation, not plant calibration. Qualitative guidance may point to physical consequences that the numerical engine does not calculate.',className='callout warn')
    ])

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8050')),debug=False)
