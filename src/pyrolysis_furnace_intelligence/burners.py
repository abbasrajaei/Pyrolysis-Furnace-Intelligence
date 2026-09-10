from .provenance import number
def burner_loads(allocation,bottom_count,sidewall_count):
    for count in (bottom_count,sidewall_count):
        if isinstance(count,bool) or int(count)!=count or count<=0:raise ValueError('Positive integer count required')
    return {'bottom':(allocation['inlet']+allocation['outlet_bottom'])/bottom_count,'sidewall':allocation['outlet_sidewall']/sidewall_count}
