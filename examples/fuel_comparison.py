from pyrolysis_furnace_intelligence.fuels import fuel_properties,fuel_required
from pyrolysis_furnace_intelligence.cases import parameter
for case in ('baseline','high_mass_lhv','lower_mass_lhv'):
    p=fuel_properties(case)
    print(case,p['lhv'].value,p['wobbe'].value,fuel_required(parameter('thermal','fired'),p['lhv']).value)
