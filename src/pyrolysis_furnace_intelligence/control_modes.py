from .operating_states import State
def distribution_enabled(state,active_authority):
    return State(state)==State.NORMAL and active_authority!='UNAVAILABLE'
