"""Public combustion workbench engine.

Generalised teaching conditions; first-principles combustion and clearly labelled
engineering approximations. Not a plant digital twin or safety tool.
"""
from copy import deepcopy
from math import exp, isfinite, sqrt

SPECIES={
"H2":(2.016,120.00,(0,2,0,0)),"CH4":(16.043,50.00,(1,4,0,0)),
"C2H4":(28.054,47.16,(2,4,0,0)),"C2H6":(30.070,47.48,(2,6,0,0)),
"C3H8":(44.097,46.35,(3,8,0,0)),"CO":(28.010,10.11,(1,0,1,0)),
"CO2":(44.009,0.0,(1,0,2,0)),"N2":(28.014,0.0,(0,0,0,2))}
COMPONENTS=tuple(SPECIES)
FUEL_INPUTS={"H2":"Hydrogen","CH4":"Methane","C2H4":"Ethylene","C2H6":"Ethane",
"C3H8":"Propane","CO":"Carbon monoxide","CO2":"Carbon dioxide","N2":"Nitrogen"}
NORMAL_MOLAR_VOLUME=22.414; AIR_MW=28.965; O2_MW=31.999; N2_MW=28.014
AR_MW=39.948; H2O_MW=18.015; CO2_MW=44.009
AIR_O2=.2095; AIR_N2=.7808; AIR_AR=.0093; AIR_OTHER=1-AIR_O2-AIR_N2-AIR_AR
AIR_TEMPERATURE_C=27.; AIR_RELATIVE_HUMIDITY=.87; ATMOSPHERIC_PRESSURE_KPA=101.325
STEAM_LOAD_WEIGHT=1/3; LOW_LOAD_FRACTION=.75
PUBLIC_CASES={
"start_of_run":{"label":"Start of run","feed_kg_s":8.0,"steam_ratio":.30,"fired_duty_mw":60.0},
"end_of_run":{"label":"End of run","feed_kg_s":8.0,"steam_ratio":.30,"fired_duty_mw":59.0}}
DEFAULT_COMPOSITION={"H2":.8000,"CH4":.1950,"C2H4":.0015,"C2H6":.0015,
"C3H8":0.,"CO":.0010,"CO2":0.,"N2":.0010}
DEFAULT_CASE={"operating_case":"start_of_run","feed_kg_s":8.0,"steam_ratio":.30,
"composition":DEFAULT_COMPOSITION,"balance_component":"CH4","excess_air":.10,"bottom_split":.50}
BURNERS={"bottom_count":30,"sidewall_count":30,"minimum_mw_per_burner":.125,
"normal_mw_per_burner":1.0,"design_mw_per_burner":1.25}

def _f(v,name="value"):
    v=float(v)
    if not isfinite(v): raise ValueError(f"{name} must be finite")
    return v

def composition_check(c):
    if not c or set(c)-set(SPECIES): raise ValueError("Unsupported or missing fuel composition")
    x={k:max(0.,_f(c.get(k,0),k)) for k in COMPONENTS}; s=sum(x.values())
    if s<=0 or abs(s-1)>1e-8: raise ValueError("Fuel mole fractions must sum to one")
    x[max(x,key=x.get)]+=1-s
    return x

def rebalance_composition(previous,changed,new_value,balance_component="CH4"):
    old=composition_check(previous)
    if changed not in COMPONENTS or balance_component not in COMPONENTS: raise ValueError("Unsupported component")
    bal=balance_component
    if bal==changed: bal=max((k for k in COMPONENTS if k!=changed),key=lambda k:old[k])
    fixed=sum(v for k,v in old.items() if k not in {changed,bal}); limit=max(0.,1-fixed)
    new=min(max(_f(new_value),0.),limit); out=dict(old); out[changed]=new; out[bal]=1-fixed-new
    out[bal]+=1-sum(out.values())
    return composition_check(out)

def mixture_properties(composition):
    x=composition_check(composition)
    mw=sum(x[k]*SPECIES[k][0] for k in COMPONENTS)
    molar_lhv=sum(x[k]*SPECIES[k][0]*SPECIES[k][1] for k in COMPONENTS)
    lhv=molar_lhv/mw; vol=molar_lhv/NORMAL_MOLAR_VOLUME; sg=mw/AIR_MW
    carbon=sum(x[k]*SPECIES[k][2][0]*12.011 for k in COMPONENTS)
    return {"molecular_weight_kg_kmol":mw,"lhv_MJ_kg":lhv,"volumetric_lhv_MJ_Nm3":vol,
    "specific_gravity":sg,"wobbe_MJ_Nm3":vol/sqrt(sg),"carbon_kg_per_kmol_fuel":carbon}

def saturation_pressure_water_kpa(t):
    return .61078*exp(17.2694*_f(t)/(_f(t)+237.29))

def humidity_mol_per_mol_dry_air(t=AIR_TEMPERATURE_C,rh=AIR_RELATIVE_HUMIDITY,p=ATMOSPHERIC_PRESSURE_KPA):
    rh=_f(rh); p=_f(p); pw=rh*saturation_pressure_water_kpa(t)
    if not 0<=rh<=1 or pw>=p: raise ValueError("Invalid humid-air condition")
    return pw/(p-pw)

def combustion_per_kmol_fuel(composition,excess_air):
    x=composition_check(composition); ea=_f(excess_air)
    if ea<0: raise ValueError("Negative excess air is outside this complete-combustion model")
    atoms=[sum(x[k]*SPECIES[k][2][i] for k in COMPONENTS) for i in range(4)]
    c,h,o,n=atoms; o2st=c+h/4-o/2
    if o2st<=0: raise ValueError("Positive oxygen demand required")
    o2=o2st*(1+ea); dry_air=o2/AIR_O2; humid=humidity_mol_per_mol_dry_air(); water_air=dry_air*humid
    products={"CO2":c,"H2O":h/2+water_air,"O2":o2-o2st,"N2":n/2+dry_air*AIR_N2,"Ar":dry_air*AIR_AR}
    wet_total=sum(products.values()); dry_total=wet_total-products["H2O"]
    wet={k:100*v/wet_total for k,v in products.items()}
    dry={k:(0. if k=="H2O" else 100*v/dry_total) for k,v in products.items()}
    airmw=AIR_O2*O2_MW+AIR_N2*N2_MW+AIR_AR*AR_MW+AIR_OTHER*AIR_MW
    humid_air_mass=dry_air*airmw+water_air*H2O_MW
    flue_mass=products["CO2"]*CO2_MW+products["H2O"]*H2O_MW+products["O2"]*O2_MW+products["N2"]*N2_MW+products["Ar"]*AR_MW
    return {"stoich_oxygen_kmol_per_kmol_fuel":o2st,"stoich_dry_air_kmol_per_kmol_fuel":o2st/AIR_O2,
    "humid_air_mass_kg_per_kmol_fuel":humid_air_mass,"flue_mass_kg_per_kmol_fuel":flue_mass,
    "products_kmol_per_kmol_fuel":products,"wet_flue_pct":wet,"dry_flue_pct":dry,
    "formed_co2_kmol_per_kmol_fuel":c-x["CO2"]}

def required_fired_duty(case):
    name=str(case.get("operating_case","start_of_run"))
    if name not in PUBLIC_CASES: raise ValueError("Unsupported operating case")
    ref=PUBLIC_CASES[name]; feed=_f(case.get("feed_kg_s",ref["feed_kg_s"])); ratio=_f(case.get("steam_ratio",ref["steam_ratio"]))
    if feed<=0 or ratio<0: raise ValueError("Feed must be positive and steam/feed nonnegative")
    steam=feed*ratio; li=feed+STEAM_LOAD_WEIGHT*steam
    refli=ref["feed_kg_s"]*(1+STEAM_LOAD_WEIGHT*ref["steam_ratio"])
    duty=ref["fired_duty_mw"]*li/refli; low=feed<LOW_LOAD_FRACTION*ref["feed_kg_s"]
    return {"required_fired_duty_mw":duty,"hydrocarbon_feed_kg_s":feed,"steam_flow_kg_s":steam,
    "load_index":li,"low_load":low,"status":"Low-load range" if low else "Within normal range"}

def _fuel_flow(duty,lhv): return duty*3600/lhv

def evaluate_case(case=None,before_case=None,hold_constant="fired_duty",changed_input=None):
    c=deepcopy(DEFAULT_CASE); c.update(deepcopy(case or {})); c["composition"]=composition_check(c["composition"])
    props=mixture_properties(c["composition"]); load=required_fired_duty(c); required=float(load["required_fired_duty_mw"])
    fired=required; isfuel=changed_input in COMPONENTS
    if isfuel and before_case is not None and hold_constant in {"fuel_flow","burner_dp"}:
        before=evaluate_case(before_case)
        if hold_constant=="fuel_flow":
            fired=before["fuel"]["fuel_flow_kg_h"]*props["lhv_MJ_kg"]/3600
        else:
            fired=before["firing"]["fired_duty_mw"]*props["wobbe_MJ_Nm3"]/before["fuel"]["wobbe_MJ_Nm3"]
    ff=_fuel_flow(fired,props["lhv_MJ_kg"]); fkmol=ff/props["molecular_weight_kg_kmol"]
    comb=combustion_per_kmol_fuel(c["composition"],c["excess_air"])
    air=fkmol*comb["humid_air_mass_kg_per_kmol_fuel"]; flue=fkmol*comb["flue_mass_kg_per_kmol_fuel"]
    co2=fkmol*comb["formed_co2_kmol_per_kmol_fuel"]*CO2_MW; co2flue=fkmol*comb["products_kmol_per_kmol_fuel"]["CO2"]*CO2_MW
    split=_f(c["bottom_split"])
    if not 0<=split<=1: raise ValueError("Bottom firing split must be 0 to 1")
    bottom=fired*split/BURNERS["bottom_count"]; side=fired*(1-split)/BURNERS["sidewall_count"]; avg=fired/(BURNERS["bottom_count"]+BURNERS["sidewall_count"])
    warning=None
    if max(bottom,side)>BURNERS["design_mw_per_burner"]: warning="Burner loading is above the public teaching design point"
    elif min(bottom,side)<BURNERS["minimum_mw_per_burner"]: warning="Burner loading is below the public teaching minimum point"
    return {"case":c,"process":{**load,"heat_gap_mw":fired-required},
    "fuel":{**props,"fuel_flow_kg_h":ff,"fuel_flow_Nm3_h":fkmol*NORMAL_MOLAR_VOLUME},
    "combustion":{"stoich_oxygen_kmol_per_kmol_fuel":comb["stoich_oxygen_kmol_per_kmol_fuel"],
    "stoich_air_kg_per_kg_fuel":comb["stoich_dry_air_kmol_per_kmol_fuel"]*AIR_MW/props["molecular_weight_kg_kmol"],
    "air_flow_kg_h":air,"flue_flow_kg_h":flue,"dry_o2_pct":comb["dry_flue_pct"]["O2"],
    "wet_o2_pct":comb["wet_flue_pct"]["O2"],"dry_co2_pct":comb["dry_flue_pct"]["CO2"],
    "wet_co2_pct":comb["wet_flue_pct"]["CO2"],"wet_h2o_pct":comb["wet_flue_pct"]["H2O"],
    "co2_formed_kg_h":co2,"co2_flue_kg_h":co2flue,"co2_intensity_kg_MWh":co2/fired if fired else 0},
    "firing":{"required_fired_duty_mw":required,"fired_duty_mw":fired,"bottom_burner_mw":bottom,
    "sidewall_burner_mw":side,"average_burner_mw":avg,"burner_warning":warning},
    "status":{"normal_range":not load["low_load"],"text":load["status"],"burner_warning":warning}}

OUTPUTS={
"fired_duty":("Fired duty","MW",("firing","fired_duty_mw")),
"fuel_flow":("Fuel flow","kg/h",("fuel","fuel_flow_kg_h")),
"lhv":("LHV","MJ/kg",("fuel","lhv_MJ_kg")),
"wobbe":("Wobbe index","MJ/Nm³",("fuel","wobbe_MJ_Nm3")),
"air_flow":("Air flow","t/h",("combustion","air_flow_kg_h")),
"flue_flow":("Flue-gas flow","t/h",("combustion","flue_flow_kg_h")),
"dry_o2":("O₂, dry","%",("combustion","dry_o2_pct")),
"dry_co2":("CO₂, dry","%",("combustion","dry_co2_pct")),
"co2":("CO₂ from combustion","t/h",("combustion","co2_formed_kg_h")),
"co2_intensity":("CO₂ intensity","kg/MWh",("combustion","co2_intensity_kg_MWh")),
"burner_load":("Average burner load","MW/burner",("firing","average_burner_mw")),
"bottom_burner":("Bottom burner load","MW/burner",("firing","bottom_burner_mw")),
"sidewall_burner":("Sidewall burner load","MW/burner",("firing","sidewall_burner_mw"))}
RESPONSE_OPTIONS={"feed_kg_s":["fired_duty","fuel_flow","air_flow","flue_flow","co2","burner_load"],
"steam_ratio":["fired_duty","fuel_flow","air_flow","flue_flow","co2"],
"excess_air":["dry_o2","air_flow","flue_flow","dry_co2"],
"bottom_split":["bottom_burner","sidewall_burner"],
**{k:["co2","fuel_flow","wobbe","lhv","air_flow","flue_flow","co2_intensity"] for k in COMPONENTS}}
DEFAULT_RESPONSE={"feed_kg_s":"fired_duty","steam_ratio":"fired_duty","excess_air":"dry_o2",
"bottom_split":"bottom_burner",**{k:"co2" for k in COMPONENTS}}

def _value(result,name):
    value=result
    for k in OUTPUTS[name][2]: value=value[k]
    value=float(value)
    return value/1000 if name in {"air_flow","flue_flow","co2"} else value

def current_input_value(case,name):
    return float(case["composition"][name]) if name in COMPONENTS else float(case[name])

def input_label(name):
    return {"feed_kg_s":"Feed rate","steam_ratio":"Steam/feed ratio","excess_air":"Excess air",
    "bottom_split":"Bottom firing split",**FUEL_INPUTS}.get(name,"Feed rate")

def input_unit(name):
    if name=="feed_kg_s": return "kg/s"
    if name=="steam_ratio": return "kg/kg"
    return "%" if name in COMPONENTS or name in {"excess_air","bottom_split"} else ""

def sweep_bounds(case,name):
    ref=PUBLIC_CASES[str(case.get("operating_case","start_of_run"))]
    if name=="feed_kg_s": return .60*ref["feed_kg_s"],1.15*ref["feed_kg_s"]
    if name=="steam_ratio": return .15,.60
    if name=="excess_air": return 0.,.35
    if name=="bottom_split": return .25,.75
    if name in COMPONENTS:
        bal=str(case.get("balance_component","CH4")); comp=case["composition"]
        if bal==name: bal=max((k for k in COMPONENTS if k!=name),key=lambda k:comp[k])
        fixed=sum(float(v) for k,v in comp.items() if k not in {name,bal})
        return 0.,max(0.,1-fixed)
    return 0.,1.

def _case_with(case,name,value):
    c=deepcopy(case)
    if name in COMPONENTS: c["composition"]=rebalance_composition(c["composition"],name,value,str(c.get("balance_component","CH4")))
    else: c[name]=value
    return c

def response_sweep(current_case,before_case,changed_input,output_name=None,hold_constant="fired_duty",points=81):
    if changed_input not in RESPONSE_OPTIONS: changed_input="feed_kg_s"
    if output_name not in RESPONSE_OPTIONS[changed_input]: output_name=DEFAULT_RESPONSE[changed_input]
    lo,hi=sweep_bounds(current_case,changed_input); xs=[lo+(hi-lo)*i/(points-1) for i in range(points)]
    ys=[_value(evaluate_case(_case_with(current_case,changed_input,x),before_case,hold_constant,changed_input),output_name) for x in xs]
    before=evaluate_case(before_case); now=evaluate_case(current_case,before_case,hold_constant,changed_input)
    return {"x":xs,"y":ys,"x_before":current_input_value(before_case,changed_input),"x_now":current_input_value(current_case,changed_input),
    "y_before":_value(before,output_name),"y_now":_value(now,output_name),"input":changed_input,
    "input_label":input_label(changed_input),"input_unit":input_unit(changed_input),"output":output_name,
    "output_label":OUTPUTS[output_name][0],"output_unit":OUTPUTS[output_name][1],
    "low_load_boundary":LOW_LOAD_FRACTION*PUBLIC_CASES[str(current_case.get("operating_case","start_of_run"))]["feed_kg_s"] if changed_input=="feed_kg_s" else None}

def simple_explanation(name,before,current,hold_constant="fired_duty"):
    b=current_input_value(before,name if name in RESPONSE_OPTIONS else "feed_kg_s"); n=current_input_value(current,name if name in RESPONSE_OPTIONS else "feed_kg_s")
    d="increased" if n>b else "decreased" if n<b else "did not change"
    if name=="H2": short=f"Hydrogen {d}. This changes fuel heating value, density, Wobbe index, oxygen demand and carbon entering the burners."
    elif name in COMPONENTS: short=f"{FUEL_INPUTS[name]} {d}. The fuel balance changed, so fuel demand, air requirement and CO₂ response also change."
    elif name=="feed_kg_s": short=f"Feed rate {d}. More process material requires more furnace heat at the same steam/feed ratio and operating condition."
    elif name=="steam_ratio": short=f"Steam/feed ratio {d}. The steam must also be heated, so estimated furnace heat demand changes."
    elif name=="excess_air": short=f"Excess air {d}. Air and flue-gas flow and O₂/CO₂ concentrations change; extra air does not create carbon."
    else: short=f"Bottom firing share {d}. Total furnace duty is conserved while duty moves between bottom and sidewall burner groups."
    if name in COMPONENTS:
        short+=(" The process heat requirement is kept constant." if hold_constant=="fired_duty" else
        " Fuel mass flow is kept constant, so fired duty can move." if hold_constant=="fuel_flow" else
        " Burner pressure difference is treated through the Wobbe approximation.")
    paths={"feed_kg_s":["Feed","Heat demand","Fired duty","Fuel flow","Air","Flue gas / CO₂"],
    "steam_ratio":["Steam/feed","Thermal load","Fired duty","Fuel flow"],
    "excess_air":["Excess air","Air flow","Flue-gas flow","O₂ / CO₂ concentration"],
    "bottom_split":["Total firing","Bottom / sidewall split","Burner loading"]}
    return {"short":short,"path":paths.get(name,["Fuel composition","Fuel properties","Fuel flow","Air requirement","Flue gas","CO₂"])}

def comparison_rows(before_case,current_case,hold_constant="fired_duty",changed_input=None):
    before=evaluate_case(before_case); now=evaluate_case(current_case,before_case,hold_constant,changed_input)
    metrics=[("Fuel flow","fuel_flow","kg/h"),("LHV","lhv","MJ/kg"),("Wobbe index","wobbe","MJ/Nm³"),
    ("Air flow","air_flow","t/h"),("Flue-gas flow","flue_flow","t/h"),("CO₂ from combustion","co2","t/h"),
    ("Average burner load","burner_load","MW/burner")]
    rows=[]
    for label,key,unit in metrics:
        b=_value(before,key); n=_value(now,key); pct=None if abs(b)<1e-12 else 100*(n-b)/b
        rows.append({"label":label,"before":b,"now":n,"change_pct":pct,"unit":unit})
    return rows
