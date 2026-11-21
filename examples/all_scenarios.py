from pyrolysis_furnace_intelligence.scenario_engine import SCENARIOS,run_scenario
from pyrolysis_furnace_intelligence.supervisor_service import assess
for name in SCENARIOS:
    state=run_scenario(name)
    print(name,state['active_authority'],assess(state)['status'])
