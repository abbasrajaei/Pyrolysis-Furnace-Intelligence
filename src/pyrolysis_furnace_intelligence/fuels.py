from .cases import parameters, parameter
from .provenance import Value, calculated, number

FORMULAS={'H2':(0,2,0,0),'CH4':(1,4,0,0),'C2H6':(2,6,0,0),'N2':(0,0,0,2)}

def composition_check(x):
    if not x or set(x)-set(FORMULAS):
        raise ValueError('Unsupported or missing composition')
    clean={k:(0.0 if abs(number(v))<1e-12 else float(v)) for k,v in x.items()}
    if any(v<-1e-12 for v in clean.values()) or abs(sum(clean.values())-1)>1e-9:
        raise ValueError('Complete fractions must sum to one')
    drift=1.0-sum(clean.values())
    if abs(drift)>0:
        receiver=max(clean,key=clean.get)
        clean[receiver]+=drift
    return clean

def mixture_properties(composition,case='interactive'):
    p=parameters()
    x=composition_check(composition)
    inp=Value(x,'mol/mol','SYNTHETIC','Declared complete teaching composition',case)
    masses={k:p['species'][k]['molar_mass']['value'] for k in x}
    mw=sum(x[k]*masses[k] for k in x)
    energy=sum(x[k]*masses[k]*p['species'][k]['lhv']['value'] for k in x)
    if mw<=0:
        raise ValueError('Fuel molecular weight must be positive')
    lhv=energy/mw
    chem=p['chemistry']
    n=chem['normal_pressure']['value']/(chem['gas_constant']['value']*chem['normal_temperature']['value'])
    r=chem['air_n2_o2']['value']
    air_mw=(.032+r*.028)/(1+r)
    props=[
        Value(mw,'kg/mol','REFERENCE','Rounded component molecular masses'),
        Value(lhv,'J/kg','REFERENCE','Rounded component lower heating values')
    ]
    def v(a,u,b):
        return calculated(a,u,b,inp,*props,parameter('chemistry','normal_temperature'),parameter('chemistry','normal_pressure'))
    return {
        'composition':inp,
        'molecular_weight':v(mw,'kg/mol','Sum of mole fraction times molecular mass'),
        'lhv':v(lhv,'J/kg','Sum(x M LHV) / Sum(x M)'),
        'volumetric_lhv':v(n*energy,'J/Nm3','Ideal normal molar density times molar LHV'),
        'wobbe':v(n*energy/(mw/air_mw)**.5,'J/Nm3','Lower volumetric heating value / sqrt(fuel/air molecular mass)')
    }

def fuel_properties(case='baseline'):
    entry=parameters()['fuels'][case]
    return mixture_properties(entry['value'],case)

def fuel_required(duty,lhv):
    if duty.value is None or lhv.value is None:
        return calculated(None,'kg/s','Q/LHV',duty,lhv)
    q,l=number(duty.value),number(lhv.value)
    if duty.units!='W' or lhv.units!='J/kg' or q<0 or l<=0:
        raise ValueError('Positive LHV and nonnegative W duty required')
    return calculated(q/l,'kg/s','Fixed chemical duty divided by mass LHV; no equal heat-transfer claim',duty,lhv)
