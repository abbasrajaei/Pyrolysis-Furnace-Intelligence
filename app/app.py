from __future__ import annotations
import os,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"src"
if str(SRC) not in sys.path: sys.path.insert(0,str(SRC))
from dash import Dash,Input,Output,State,ctx,dcc,html,no_update
import plotly.graph_objects as go
from pyrolysis_furnace_intelligence.combustion_workbench import (
 BURNERS,COMPONENTS,DEFAULT_CASE,DEFAULT_RESPONSE,FUEL_INPUTS,OUTPUTS,PUBLIC_CASES,
 RESPONSE_OPTIONS,comparison_rows,evaluate_case,rebalance_composition,response_sweep,simple_explanation)

app=Dash(__name__,title="Pyrolysis Furnace Intelligence",suppress_callback_exceptions=True)
server=app.server
C={"bg":"#07121D","panel":"#0D1B29","line":"#20384D","text":"#F3F7FA","muted":"#9CB0BF",
"blue":"#36A7E9","amber":"#F2A93B","green":"#38C995","yellow":"#F2C14E","before":"#8BA0AE"}

def fmt(v,u):
 v=float(v)
 if u=="kg/h": return f"{v:,.0f}"
 if u in {"t/h","MJ/kg","MJ/Nm³","kg/MWh","MW"}: return f"{v:,.2f}"
 if u=="MW/burner": return f"{v:.3f}"
 if u=="%": return f"{v:.2f}"
 return f"{v:.3f}"

def composition_view(case):
 out=[]
 for k in COMPONENTS:
  v=100*case["composition"].get(k,0)
  out.append(html.Div([html.Span(DISPLAY_FORMULAS[k],className="comp-name",title=FUEL_INPUTS[k]),
   html.Div(html.Div(className="comp-bar-fill",style={"width":f"{min(v,100):.2f}%"}),className="comp-bar"),
   html.Span(f"{v:.2f}%",className="comp-number")],className="comp-row"))
 return html.Div(out,className="composition-list")

def card(label,value,unit):
 return html.Div([html.Div(label,className="result-label"),
  html.Div([html.Span(value,className="result-value"),html.Span(" "+unit,className="result-unit")])],
  className="result-card")

def results(result):
 return html.Div([
  card("Fired duty",f"{result['firing']['fired_duty_mw']:.2f}","MW"),
  card("Fuel flow",f"{result['fuel']['fuel_flow_kg_h']:,.0f}","kg/h"),
  card("LHV",f"{result['fuel']['lhv_MJ_kg']:.2f}","MJ/kg"),
  card("Wobbe index",f"{result['fuel']['wobbe_MJ_Nm3']:.2f}","MJ/Nm³"),
  card("Air flow",f"{result['combustion']['air_flow_kg_h']/1000:.2f}","t/h"),
  card("Flue-gas flow",f"{result['combustion']['flue_flow_kg_h']/1000:.2f}","t/h"),
  card("O₂, dry",f"{result['combustion']['dry_o2_pct']:.2f}","%"),
  card("CO₂ from combustion",f"{result['combustion']['co2_formed_kg_h']/1000:.2f}","t/h"),
  card("Average burner load",f"{result['firing']['average_burner_mw']:.3f}","MW/burner")
 ],className="results-grid")

def compare_view(before,current,hold,changed):
 body=[]
 for row in comparison_rows(before,current,hold,changed):
  p=row["change_pct"]; txt="—" if p is None else f"{p:+.1f}%"
  cls="change-flat" if p is None or abs(p)<1e-10 else ("change-up" if p>0 else "change-down")
  body.append(html.Div([html.Div(row["label"],className="compare-name"),
   html.Div(fmt(row["before"],row["unit"]),className="compare-value"),
   html.Div("→",className="compare-arrow"),
   html.Div(fmt(row["now"],row["unit"]),className="compare-value now"),
   html.Div(row["unit"],className="compare-unit"),
   html.Div(txt,className=f"compare-change {cls}")],className="compare-row"))
 head=html.Div([html.Div(""),html.Div("Before"),html.Div(""),html.Div("Now"),html.Div(""),html.Div("Change")],className="compare-head")\n return html.Div([head,*body],className="compare-body")

def hold_text(v):
 return {"fired_duty":"Keeping fired duty constant","fuel_flow":"Keeping fuel flow constant",
 "burner_dp":"Keeping burner pressure difference constant"}.get(v,"Keeping fired duty constant")

def effect_figure(current,before,changed,response,hold):
 d=response_sweep(current,before,changed,response,hold_constant=hold,points=81)
 x=list(d["x"]); xb=float(d["x_before"]); xn=float(d["x_now"]); xt=d["input_label"]
 if d["input_unit"]=="%": x=[100*v for v in x]; xb*=100; xn*=100
 elif d["input_unit"]: xt+=f" ({d['input_unit']})"
 fig=go.Figure()
 fig.add_trace(go.Scatter(x=x,y=d["y"],mode="lines",line={"color":C["blue"],"width":4},
  hovertemplate=f"{d['input_label']}: %{{x:.2f}}<br>{d['output_label']}: %{{y:.3f}} {d['output_unit']}<extra></extra>"))
 fig.add_trace(go.Scatter(x=[xb],y=[d["y_before"]],mode="markers+text",text=["Before"],textposition="top center",
  marker={"size":13,"color":C["before"],"symbol":"diamond","line":{"width":2,"color":C["text"]}}))
 fig.add_trace(go.Scatter(x=[xn],y=[d["y_now"]],mode="markers+text",text=["Now"],textposition="bottom center",
  marker={"size":15,"color":C["amber"],"line":{"width":2,"color":C["text"]}}))
 if d.get("low_load_boundary") is not None:
  fig.add_vrect(x0=min(x),x1=d["low_load_boundary"],fillcolor=C["yellow"],opacity=.08,line_width=0,
   annotation_text="Low-load range",annotation_position="top left")
 fig.update_layout(margin={"l":62,"r":24,"t":54,"b":58},paper_bgcolor=C["panel"],plot_bgcolor=C["panel"],
  font={"color":C["text"],"family":"Inter, Segoe UI, sans-serif"},
  title={"text":f"{d['output_label']} as {d['input_label'].lower()} changes","x":.01,"xanchor":"left","font":{"size":19}},
  xaxis={"title":xt,"gridcolor":C["line"],"zeroline":False},
  yaxis={"title":f"{d['output_label']} ({d['output_unit']})","gridcolor":C["line"],"zeroline":False},
  showlegend=False,hovermode="x unified",uirevision=f"{changed}-{response}")
 return fig,d

app.layout=html.Div([
 dcc.Store(id="current-store",data=deepcopy(DEFAULT_CASE)),
 dcc.Store(id="before-store",data=deepcopy(DEFAULT_CASE)),
 dcc.Store(id="changed-store",data="H2"),
 html.Header([
  html.Div([html.Div("Pyrolysis Furnace Intelligence",className="brand-title"),
   html.Div("Combustion Workbench",className="brand-subtitle")]),
  html.Div([html.Div("Operating case",className="top-label"),
   dcc.RadioItems(id="operating-case",options=[
    {"label":"Start of run","value":"start_of_run"},{"label":"End of run","value":"end_of_run"}],
    value="start_of_run",inline=True,className="top-radio")],className="top-case"),
  html.Div([html.Button("Why did this happen?",id="why-open",className="btn secondary",n_clicks=0),
   html.Button("Reset",id="reset",className="btn",n_clicks=0)],className="top-actions")
 ],className="topbar"),
 html.Main([
  html.Section([
   html.Div("Inputs",className="section-title"),
   html.Div("Process",className="mini-title"),
   html.Label("Feed rate",className="input-label"),
   html.Div([dcc.Input(id="feed",type="number",value=8.0,min=1,max=12,step=.1,debounce=True),html.Span("kg/s")],className="input-line"),
   html.Label("Steam / feed",className="input-label"),
   html.Div([dcc.Input(id="steam-ratio",type="number",value=.30,min=0,max=1,step=.01,debounce=True),html.Span("kg/kg")],className="input-line"),
   html.Div("Fuel composition",className="mini-title"),
   html.Div(id="composition-view"),
   html.Div([
    html.Div([html.Label("Change",className="input-label"),
     dcc.Dropdown(id="fuel-component",options=[{"label":FUEL_INPUTS[k],"value":k} for k in COMPONENTS],value="H2",clearable=False)]),
    html.Div([html.Label("To",className="input-label"),
     html.Div([dcc.Input(id="fuel-target",type="number",value=80.0,min=0,max=100,step=.1,debounce=True),html.Span("%")],className="input-line compact")])
   ],className="fuel-edit-grid"),
   html.Label("Balance with",className="input-label"),
   dcc.Dropdown(id="balance-component",options=[{"label":FUEL_INPUTS[k],"value":k} for k in COMPONENTS],value="CH4",clearable=False),
   html.Button("Apply fuel change",id="fuel-apply",className="btn primary wide",n_clicks=0),
   html.Div("Combustion",className="mini-title"),
   html.Label("Excess air",className="input-label"),
   html.Div([dcc.Input(id="excess-air",type="number",value=10.0,min=0,max=50,step=.5,debounce=True),html.Span("%")],className="input-line"),
   html.Label("Bottom firing share",className="input-label"),
   html.Div([dcc.Input(id="bottom-split",type="number",value=50.0,min=0,max=100,step=1,debounce=True),html.Span("%")],className="input-line"),
   html.Div("When fuel changes",className="mini-title"),
   dcc.RadioItems(id="hold-constant",options=[
    {"label":"Keep fired duty constant","value":"fired_duty"},
    {"label":"Keep fuel flow constant","value":"fuel_flow"},
    {"label":"Keep burner pressure difference constant","value":"burner_dp"}],
    value="fired_duty",className="hold-radio")
  ],className="panel input-panel"),
  html.Section([
   html.Div([html.Div([html.Div("See the effect",className="section-title"),html.Div(id="graph-context",className="graph-context")]),
    html.Div([html.Div("Show effect on",className="response-label"),dcc.Dropdown(id="response-choice",clearable=False,className="response-dropdown")])],className="graph-head"),
   dcc.Graph(id="effect-graph",config={"displayModeBar":False,"responsive":True},className="effect-graph"),
   html.Div([html.Div("Before",className="legend-pill before-pill"),html.Div("Now",className="legend-pill now-pill"),
    html.Div("The curve is recalculated from the same combustion model used for the results.",className="graph-note")],className="graph-footer")
  ],className="panel graph-panel"),
  html.Section([
   html.Div("Results",className="section-title"),html.Div(id="results-panel"),
   html.Div([html.Div("Before → Now",className="section-title compare-title"),html.Div(id="before-now")],className="compare-section")
  ],className="panel right-panel")
 ],className="main-grid"),
 html.Footer([html.Div(id="status-strip",className="status-left"),html.Div(id="interpretation-strip",className="interpretation")],className="bottom-strip"),
 html.Div([html.Div([
  html.Div([html.Div("Why did this happen?",className="modal-title"),html.Button("×",id="why-close",className="close-btn",n_clicks=0)],className="modal-head"),
  html.Div(id="why-content",className="modal-content")],className="modal-card")],id="why-modal",className="modal-backdrop hidden")
],className="app-shell")

@app.callback(Output("current-store","data"),Output("before-store","data"),Output("changed-store","data"),
 Input("feed","value"),Input("steam-ratio","value"),Input("excess-air","value"),Input("bottom-split","value"),
 Input("operating-case","value"),Input("fuel-apply","n_clicks"),Input("reset","n_clicks"),
 State("fuel-component","value"),State("fuel-target","value"),State("balance-component","value"),State("current-store","data"),
 prevent_initial_call=True)
def update_case(feed,steam,ea,bottom,op,target,_reset,component,balance,current):
 trig=ctx.triggered_id; old=deepcopy(current or DEFAULT_CASE)
 if trig=="reset": return deepcopy(DEFAULT_CASE),deepcopy(DEFAULT_CASE),"H2"
 new=deepcopy(old); changed="feed_kg_s"
 if trig=="feed" and feed is not None: new["feed_kg_s"]=float(feed); changed="feed_kg_s"
 elif trig=="steam-ratio" and steam is not None: new["steam_ratio"]=float(steam); changed="steam_ratio"
 elif trig=="excess-air" and ea is not None: new["excess_air"]=float(ea)/100; changed="excess_air"
 elif trig=="bottom-split" and bottom is not None: new["bottom_split"]=float(bottom)/100; changed="bottom_split"
 elif trig=="operating-case": new["operating_case"]=op; changed="feed_kg_s"
 elif trig=="fuel-target" and component and target is not None:
  new["balance_component"]=balance or "CH4"
  new["composition"]=rebalance_composition(old["composition"],component,float(target)/100,new["balance_component"]); changed=component
 else: return no_update,no_update,no_update
 return new,old,changed

@app.callback(
 Output("feed","value"),Output("steam-ratio","value"),Output("excess-air","value"),Output("bottom-split","value"),
 Output("operating-case","value"),Output("fuel-component","value"),Output("balance-component","value"),Output("hold-constant","value"),
 Input("reset","n_clicks"),prevent_initial_call=True)
def reset_controls(_n):
 c=DEFAULT_CASE
 return c["feed_kg_s"],c["steam_ratio"],100*c["excess_air"],100*c["bottom_split"],c["operating_case"],"H2",c["balance_component"],"fired_duty"

@app.callback(Output("fuel-target","value"),Input("fuel-component","value"),State("current-store","data"))
def sync_target(component,current):
 if not component or not current: return no_update
 return round(100*current["composition"].get(component,0),3)

@app.callback(Output("response-choice","options"),Output("response-choice","value"),Input("changed-store","data"))
def response_options(changed):
 key=changed if changed in RESPONSE_OPTIONS else "feed_kg_s"
 return [{"label":OUTPUTS[x][0],"value":x} for x in RESPONSE_OPTIONS[key]],DEFAULT_RESPONSE[key]

@app.callback(Output("composition-view","children"),Output("effect-graph","figure"),Output("graph-context","children"),
 Output("results-panel","children"),Output("before-now","children"),Output("status-strip","children"),
 Output("interpretation-strip","children"),Output("why-content","children"),
 Input("current-store","data"),Input("before-store","data"),Input("changed-store","data"),
 Input("hold-constant","value"),Input("response-choice","value"))
def render(current,before,changed,hold,response):
 current=current or deepcopy(DEFAULT_CASE); before=before or deepcopy(DEFAULT_CASE)
 changed=changed if changed in RESPONSE_OPTIONS else "feed_kg_s"
 response=response if response in RESPONSE_OPTIONS[changed] else DEFAULT_RESPONSE[changed]
 result=evaluate_case(current,before,hold,changed); fig,d=effect_figure(current,before,changed,response,hold)
 explain=simple_explanation(changed,before,current,hold)
 bx=d["x_before"]*100 if d["input_unit"]=="%" else d["x_before"]; nx=d["x_now"]*100 if d["input_unit"]=="%" else d["x_now"]
 suffix="%" if d["input_unit"]=="%" else (" "+d["input_unit"] if d["input_unit"] else "")
 context=html.Div([html.Span(f"Changed: {d['input_label']}",className="context-strong"),
  html.Span(f"Before {bx:.2f}{suffix} → Now {nx:.2f}{suffix}"),
  html.Span(hold_text(hold) if changed in COMPONENTS else "Other inputs held at their current values")],className="context-lines")
 status=[PUBLIC_CASES[current["operating_case"]]["label"],result["status"]["text"]]
 if result["status"]["burner_warning"]: status.append(result["status"]["burner_warning"])
 path=[]
 for i,item in enumerate(explain["path"]):
  if i: path.append(html.Span("→",className="path-arrow"))
  path.append(html.Span(item,className="path-step"))
 why=html.Div([html.P(explain["short"],className="why-lead"),html.Div(path,className="cause-path"),
  html.Div([html.Div("Key equations",className="modal-subtitle"),
   html.Div("Fired duty = fuel flow × LHV",className="equation"),
   html.Div("O₂ required = C + H/4 − O/2",className="equation"),
   html.Div("Wobbe index = volumetric LHV / √specific gravity",className="equation"),
   html.Div("Actual air = stoichiometric air × (1 + excess air)",className="equation")],className="equation-block"),
  html.Div("This public workbench uses generalised teaching conditions. It does not calculate CFD flame shape, NOx, flashback limits, local tube heat flux or a calibrated draft-to-airflow curve.",className="limit-note")])
 return composition_view(current),fig,context,results(result),compare_view(before,current,hold,changed),"  |  ".join(status),explain["short"],why

@app.callback(Output("why-modal","className"),Input("why-open","n_clicks"),Input("why-close","n_clicks"),
 State("why-modal","className"),prevent_initial_call=True)
def toggle_why(_open,_close,_class):
 return "modal-backdrop" if ctx.triggered_id=="why-open" else "modal-backdrop hidden"

if __name__=="__main__":
 app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8050")),debug=False)
