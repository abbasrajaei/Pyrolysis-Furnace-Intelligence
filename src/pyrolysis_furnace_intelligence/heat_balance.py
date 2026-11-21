from .provenance import calculated,number,unavailable
def heat_balance(fired,radiant,convection):
    inputs=(fired,radiant,convection)
    if any(v.value is None for v in inputs):return {'efficiency':unavailable('Heat input unavailable'),'loss':unavailable('Heat input unavailable','W')}
    if any(v.units!='W' for v in inputs) or len({v.case for v in inputs})!=1:raise ValueError('Compatible W duties and case required')
    q,r,c=[number(v.value) for v in inputs]
    if min(q,r,c)<0:raise ValueError('Negative duty')
    return {'loss':calculated(q-r-c,'W','Fired minus radiant minus convection; residual, not wall loss alone',*inputs),
        'useful':calculated(r+c,'W','Radiant plus convection duty',*inputs),
        'efficiency':calculated((r+c)/q,'1','Useful divided by chemical input',*inputs) if q else unavailable('Zero duty denominator')}
