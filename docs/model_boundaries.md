# Model boundaries

This model explains a generic industrial ethane pyrolysis furnace through declared teaching inputs. Numerical examples are synthetic or rounded general property references. They do not reproduce an operating facility.

## Supported

- Source-inspired static heat accounting using independently selected public duties.
- Complete combustion stoichiometry for explicitly declared H2, CH4, C2H6 and inert N2 compositions.
- Ideal dry-air demand and wet/dry product oxygen fractions.
- Fuel mass-LHV, declared-normal-volume LHV and lower-Wobbe comparisons.
- Conservation of total firing across six inlet zones and outlet bottom/sidewall branches.
- An illustrative hierarchical temperature rank selector.
- Simplified control topology, demand/measurement separation and authority constraints.
- Static event scenarios, deterministic explanations and a bounded supervisor interface.

## Not claimed

CFD; local flame shape or temperature; rigorous cracking kinetics; quantitative coking kinetics; tube-life prediction; current tube-metal temperature prediction; plant-calibrated dynamics; identified PID tuning; calibrated valve response; calibrated draft-airflow relations; plant safety assessment; APC or burner-management replacement; plant-validated AI optimization.

The selected temperature is a skin-control proxy built from synthetic measurements. It is not a measured bulk outlet temperature. The thermal page is reference accounting; it does not recalculate heat absorption after a demand event. Calculated lower Wobbe relies on an explicitly ideal normal-state convention and supplies no burner interchangeability approval.

## Authority and shutdown

NORMAL, PARTIAL_SHUTDOWN_TEACHING and TOTAL_SHUTDOWN_TEACHING are educational state labels. Shutdown teaching states withhold firing allocation. They do not simulate a particular installed protection system, isolation sequence, forced controller outputs, steam ramp, permissive or reset procedure. A state label cannot establish safe continued operation or successful isolation. Simultaneous pressure constraints and undefined manual/override arbitration return UNAVAILABLE.

## Numerical limits

UNAVAILABLE is represented by a null value and an explicit reason. Missing values are never treated as zero. Conservation and atom-balance checks verify the implemented accounting; they do not validate plant behavior. No uncertainty bounds or plant performance accuracy are inferred from test success.

The public supervisor accepts only a closed catalogue with unchanged engine engineering evidence. Its deterministic demonstration is not a language model. A provider may be supplied through the Python interface, but no live external provider is configured or evaluated here. The assistant cannot change the engine or issue operating commands.
