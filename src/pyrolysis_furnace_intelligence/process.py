from .provenance import number
def steam_base_demand(actual,requested,ratio):
    a,r,s=map(number,(actual,requested,ratio))
    if min(a,r,s)<0:raise ValueError('Nonnegative feed and ratio required')
    return max(a,r)*s
