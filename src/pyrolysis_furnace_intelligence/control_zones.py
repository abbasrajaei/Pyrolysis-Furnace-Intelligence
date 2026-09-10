from .provenance import number
def zone_request(pv,target,bias=0,enabled=True):
    if not enabled or pv is None:return 'UNAVAILABLE'
    p,t,b=map(number,(pv,target,bias));error=t+b-p
    return 'INCREASE' if error>0 else 'DECREASE' if error<0 else 'HOLD'
def pass_classification(proxies):
    p=[number(x) for x in proxies]
    if len(p)!=6 or min(p)<0:raise ValueError('Six nonnegative proxies required')
    a,b=sum(p[:3]),sum(p[3:])
    if b==0:return 'UNAVAILABLE'
    return 'pass_1_heavier' if a>b else 'pass_2_heavier' if b>a else 'balanced'
