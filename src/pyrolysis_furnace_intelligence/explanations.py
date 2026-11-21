def explain(state):
    lines=[f"Functional state: {state['operating_state']}. Authority: {state['active_authority']}.",
     'Physical values are declared references or teaching inputs; an event does not predict elapsed-time response.']
    event=state['scenario']
    if event in ('fuel_change','high_lhv','lower_lhv'):lines.append('Equivalent fuel demand changes at fixed chemical duty. Neither heat transfer nor outlet temperature is predicted.')
    if event in ('zone_temperature','zone_bias'):lines.append(f"Zone C requests {state['zone_requests']['C']}; no numerical firing correction follows from temperature error.")
    if event=='zone_redistribution':lines.append('A separately declared teaching increment redistributes six shares without changing total duty.')
    if event=='capacity':lines.append('Steam base demand follows the larger actual/requested feed. Delivered feed and steam references remain unchanged.')
    if event=='pressure_override':lines.append('A pressure constraint supersedes normal fuel demand; no valve position or pressure recovery is calculated.')
    if 'shutdown' in event:lines.append('Educational shutdown policy withholds allocation. Isolation, steam delivery and safe operation are not established.')
    if event=='pass_imbalance':lines.append('Pass-output proxies indicate imbalance; they are not measured pass duties and provide no numerical feed-bias gain.')
    if event=='bottom_side':lines.append('Outlet bottom/sidewall allocation changes at fixed outlet duty; local flux and valve response remain unavailable.')
    lines.append('Missing dynamics, actuator maps and safety information remain UNAVAILABLE.')
    return lines
