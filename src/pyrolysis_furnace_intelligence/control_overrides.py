from .operating_states import State
from .control_types import Mode
def authority(state=State.NORMAL,mode=Mode.AUTO,low=False,high=False):
    state=State(state);mode=Mode(mode)
    if state==State.TOTAL:return 'shutdown_teaching_authority'
    if state==State.PARTIAL:return 'partial_teaching_authority'
    if low and high:return 'UNAVAILABLE'
    if mode==Mode.MANUAL and (low or high):return 'UNAVAILABLE'
    if low:return 'low_pressure_constraint'
    if high:return 'high_pressure_constraint'
    if mode==Mode.MANUAL:return 'manual_fuel_request'
    if mode==Mode.HELD:return 'UNAVAILABLE'
    return 'fuel_demand_control'
