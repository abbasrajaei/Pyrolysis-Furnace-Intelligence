# Public teaching scenarios

All scenarios use the independent public dataset. Temperatures, offsets and corrections below are teaching inputs, not tuning constants.

| ID | Teaching change | Interpretation |
|---|---|---|
| normal | No change | Reference accounting and normal demand authority |
| fuel_change | Switch to high mass-LHV teaching fuel | Fixed-duty property comparison |
| high_lhv | Same high mass-LHV fuel | Mass versus volumetric heating-value lesson |
| lower_lhv | Methane/ethane teaching blend | Larger fixed-duty equivalent mass demand |
| zone_temperature | Zone C sensor group reduced by 12 K | INCREASE request, unchanged physical share |
| zone_bias | Zone C target bias −6 K | DECREASE request, unchanged measurement |
| zone_redistribution | Add 0.03 to Zone C share; subtract 0.006 from each other share | Explicit conserved redistribution, not PID output |
| capacity | Requested feed multiplied by 1.125 | Steam base demand increases; delivered references retained |
| pressure_override | Low-pressure constraint flag | Authority transfer; no valve position |
| partial_shutdown | Partial shutdown teaching policy | Allocation unavailable; no isolation/delivery prediction |
| total_shutdown | Total shutdown teaching policy | Allocation unavailable; no safety-system behavior claim |
| pass_imbalance | Pass 1 zone proxies 1.2 versus pass 2 proxies 1 | Relative classification only |
| bottom_side | Outlet bottom/side ratio becomes 2 | Conserved outlet redistribution |

The six-zone and two-pass grouping is illustrative. Synthetic scenarios do not establish an actual furnace configuration, tuning rule or shutdown sequence.
