# Public validation

The public CI suite runs on Python 3.12 and currently reports **279 passed, 0 failed**. It also runs the public example scripts, CLI example and Dash HTTP-root smoke test.

The validation suite now covers the connected Combustion and Heat Transfer workbenches as well as the retained educational firing/control modules.

| Coverage | Check |
|---|---|
| Installation/imports | Package metadata, version 2.1.0, public modules and packaged resource copies |
| Fuel composition | Composition closure, balance-component behaviour and supported fuel species |
| Combustion chemistry | Stoichiometric oxygen, humid combustion air, wet/dry products and physical product checks |
| Fuel properties | Molecular weight, mass LHV, volumetric LHV, lower Wobbe Index and fuel-flow response |
| Combustion study basis | Constant fired duty, constant fuel flow and Wobbe-based constant burner-pressure-difference studies |
| Process load | Feed and steam/load relationship, start/end teaching states and low-load warning |
| Burner allocation | Bottom/sidewall conservation, loading response and warning behaviour |
| Combustion response graph | Supported input/output sweeps, square-point presentation and Before/Now points |
| Thermal energy balance | Fired = radiant + convection + stack + other loss |
| Stack loss | Higher stack temperature and higher flue-gas flow increase calculated sensible-heat loss |
| Thermal efficiency | Stack loss and other loss propagate correctly into useful heat and overall efficiency |
| Radiant loading | Radiant share changes radiant/convection split and average/peak teaching heat flux |
| Convection recovery | Public bank shares close exactly to total convection duty |
| Cross-module coupling | Feed, excess air and fuel-composition changes propagate from combustion into the thermal calculation |
| Cross-module hold basis | Constant-duty / constant-fuel-flow fuel-study basis is preserved in the Heat Transfer module |
| Module navigation | Combustion and Heat Transfer pages and their module-specific controls/callbacks are registered |
| Firing/control teaching modules | Firing conservation, temperature selection, pressure authority and static scenario behaviour |
| Guidance/supervisor | Deterministic guidance and bounded supervisor contract |
| Dash application | Application shell, callback registration and HTTP root response |

Run locally:

~~~bash
python -m pip install ".[test]"
python -m pytest -q
python examples/fuel_comparison.py
python examples/all_scenarios.py
pyrolysis-demo --scenario zone_temperature
python app/app.py
~~~

The Dash HTTP smoke test verifies that the application root can be served. It is **not** a browser visual/accessibility test.

The response graphs are one-factor engineering parameter studies, not dynamic time simulations. Every point on the active combustion and thermal response graphs is recalculated from the same deterministic model used for the result cards.

Unsupported physics remains explicitly outside the model rather than being represented by invented values. See docs/model_boundaries.md and docs/heat_transfer_methodology.md.
