from .fuels import FORMULAS,composition_check
from .cases import parameter
from .provenance import Value,calculated,number
def complete_combustion(composition,excess_air=.15):
    x=composition_check(composition);e=number(excess_air)
    if e<0:raise ValueError('Oxygen-deficient chemistry is unsupported')
    c,h,o,n=[sum(v*FORMULAS[k][i] for k,v in x.items()) for i in range(4)]
    need=c+h/4-o/2
    if need<=0:raise ValueError('Positive oxygen demand required')
    ratio=parameter('chemistry','air_n2_o2');r=ratio.value
    prod={'CO2':c,'H2O':h/2,'O2':need*e,'N2':n/2+need*(1+e)*r}
    formulas={'CO2':(1,0,2,0),'H2O':(0,2,1,0),'O2':(0,0,2,0),'N2':(0,0,0,2)}
    incoming=[c,h,o+2*need*(1+e),n+2*need*(1+e)*r]
    residual=[sum(prod[k]*formulas[k][i] for k in prod)-incoming[i] for i in range(4)]
    dep=Value(x,'mol/mol','SYNTHETIC','Declared complete teaching composition');ea=Value(e,'1','SYNTHETIC','Explicit excess air fraction')
    def v(a,u,b):return calculated(a,u,b,dep,ea,ratio)
    wet=sum(prod.values());dry=wet-prod['H2O']
    return {'oxygen':v(need,'mol/mol','C + H/4 - O/2 mol O2 per mol fuel'),
        'stoichiometric_air':v(need*(1+r),'mol/mol','Dry air per mol fuel'),
        'actual_air':v(need*(1+r)*(1+e),'mol/mol','Stoichiometric air times (1 + excess air)'),
        'products':v(prod,'mol/mol','Complete combustion products per mol fuel'),
        'dry_o2':v(prod['O2']/dry,'mol/mol','O2 / dry products; not a leakage diagnosis'),
        'wet_o2':v(prod['O2']/wet,'mol/mol','O2 / wet products'),
        'atom_residuals':v(residual,'mol/mol','Outgoing minus incoming C,H,O,N atoms')}
