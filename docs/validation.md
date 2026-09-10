# Public validation

The public CI suite runs on Python 3.12 and covers the engineering engine, interactive workbench logic, sensitivity analysis, guidance rules, scenario engine, bounded supervisor contract and Dash application shell. The exact passing test count is reported by the current GitHub Actions run and should be treated as the release evidence.

| Coverage | Check |
|---|---|
| Installation/imports | Package metadata, public modules and packaged resource copies |
| Chemistry | H2, CH4 and C2H6 oxygen demand, excess-air cases, atom balances and dry/wet oxygen |
| Fuel properties | Mixture closure, mass LHV, declared normal-volume basis, lower Wobbe and fixed-duty fuel demand |
| Workbench composition | Automatic renormalization, locked components and valid presets |
| Heat accounting | Conserved useful-duty partition, residual and efficiency |
| Firing | Inlet/outlet, bottom/side and six-zone conservation; infeasible correction rejection |
| Temperature | Hierarchical selector and unavailable propagation |
| Control | Normal/manual authority, low/high/conflicting constraints and shutdown teaching states |
| Draft model | Fixed-resistance relative-airflow teaching correlation and explicit non-calibration label |
| Sensitivity engine | Every supported input/output pair produces a deterministic one-factor curve |
| Guidance | Every operator-facing parameter change has context-sensitive explanation, watch variables, basis and limitations |
| Scenarios | Thirteen bounded static teaching events |
| Supervisor | Current-state grounding, rejection/fallback and authority/schema/provenance boundaries |
| Dash application | Application shell, callback registration and HTTP root response |

Run locally:

\`\`\`bash
python -m pip install ".[test]"
python -m pytest -q
python examples/fuel_comparison.py
python examples/all_scenarios.py
pyrolysis-demo --scenario zone_temperature
python app/app.py
\`\`\`

The Dash HTTP test verifies that the application root can be served. It is not a browser visual/accessibility audit. Sensitivity sweeps are engineering parameter studies, not dynamic time simulations. Unsupported physics remains explicitly outside the model rather than being represented by skipped tests.
