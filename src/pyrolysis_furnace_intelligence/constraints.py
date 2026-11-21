from .provenance import unavailable
REASONS={
 'cot_prediction':'No heat-transfer or cracking-response model.',
 'furnace_time_constant':'No identified transient response.',
 'pid_gain':'No identified tuning or process gain.',
 'valve_opening':'No installed actuator characteristic.',
 'coke_thickness':'No coking rate or thickness model.',
 'tube_metal_temperature':'No current tube-metal thermal calculation.',
 'zone_firing_increment':'Directional error is not a calibrated firing increment.',
 'draft_airflow':'No calibrated fan or draft-to-airflow relation.',
 'decoke_time':'No coking kinetics or decoke forecast.',
 'safety_to_continue':'Educational model cannot determine plant safety.',
 'override_bypass':'Supervisor cannot change authority or bypass constraints.',
 'feedforward_output':'Feed-forward topology only; no numerical gains or timing.',
 'external_reset':'No numerical anti-windup or external-reset implementation.'}
def unavailable_results():return {k:unavailable(v) for k,v in REASONS.items()}
