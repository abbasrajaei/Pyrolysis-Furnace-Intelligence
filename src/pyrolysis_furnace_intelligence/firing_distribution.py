import math
from .provenance import number
def shares_check(shares):
    f=tuple(number(x) for x in shares)
    if len(f)!=6 or min(f)<0 or max(f)>1 or not math.isclose(sum(f),1,abs_tol=1e-12,rel_tol=0):raise ValueError('Six bounded fractions summing to one required')
    return f
def redistribute(shares,zone,increment):
    f=shares_check(shares);d=number(increment)
    if zone not in range(6):raise ValueError('Invalid zone')
    proposed=tuple(v+d if i==zone else v-d/5 for i,v in enumerate(f))
    return shares_check(proposed) # Reject atomically; no clipping or normalization.
def allocate(duty,inlet_outlet,bottom_side,shares):
    f=shares_check(shares);q,a,b=map(number,(duty,inlet_outlet,bottom_side))
    if min(q,a,b)<0:raise ValueError('Nonnegative duty and ratios required')
    outlet=q/(1+a);inlet=q-outlet;side=outlet/(1+b);bottom=outlet-side
    zones=[inlet*v for v in f];res=q-math.fsum(zones+[bottom,side])
    if abs(res)>1e-10*max(q,1):raise ArithmeticError('Conservation failed')
    return dict(inlet=inlet,outlet=outlet,outlet_bottom=bottom,outlet_sidewall=side,zones=zones,residual=res)
