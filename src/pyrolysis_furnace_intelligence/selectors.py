from .provenance import Value,calculated,unavailable,number
def second_highest(values):
    if len(values)<2 or any(v.value is None for v in values):return unavailable('All declared sensors required','K')
    if any(v.units!='K' or number(v.value)<=0 for v in values):raise ValueError('Positive Kelvin sensors required')
    rule=Value('second-highest','1','ASSUMPTION','Illustrative rank selector; repeated ranks count')
    return calculated(sorted(v.value for v in values)[-2],'K','Second highest; skin proxy, not bulk COT',*values,rule)
def temperature_selection(values):
    if len(values)!=24:raise ValueError('Teaching topology requires six groups of four sensors')
    zones={z:second_highest(values[i*4:i*4+4]) for i,z in enumerate('ABCDEF')}
    return zones,second_highest(list(zones.values()))
