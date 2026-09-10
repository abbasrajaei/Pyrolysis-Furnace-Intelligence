# Public validation

The independent public suite reports **128 passed, 0 failed, 0 skipped** on Python 3.12. The count is generated from this repository's own tests, not inherited from another model or earlier development stage.

The check used a clean virtual environment without system-site packages, a regular package installation from the public configuration, and a separate copy containing only public files. The test interpreter imported the installed package from site-packages. A Python audit hook denied reads of the development workspace. The same restriction applied to the public examples and application server.

| Coverage | Check |
|---|---|
| Installation/imports | Package metadata, public modules, installed resource copies |
| Chemistry | H2, CH4 and C2H6 oxygen demand, excess-air cases, atom balances, dry/wet oxygen |
| Fuel properties | Mass-weighted LHV, fixed-duty energy closure, mass/volume distinction |
| Heat accounting | Residual and efficiency, zero duty, inconsistent and mixed-case handling |
| Firing | Split conservation, equal-donor redistribution, infeasible update rejection |
| Temperature | Hierarchical versus global rank, invalid sensor propagation |
| Control | Normal/manual authority, low/high/conflicting constraints, shutdown teaching state |
| Process/scenarios | Steam demand versus delivery, directional request versus allocation, thirteen scenarios |
| Provenance | Invalid metadata/value combinations and unavailable propagation |
| Supervisor | Current-state grounding, stale state, invented unavailable values, authority/schema/provenance/recommendation rejection, fallback |
| Application | Eight Streamlit AppTest views and Scenario Lab supervisor/shutdown interaction |

Both public example files and the installed command-line entry point completed successfully. The application server returned HTTP 200 for its health and root routes while bound only to loopback. AppTest verifies application execution and widgets; HTTP checks verify server startup. Neither is a full browser visual/accessibility audit. Browser screenshots were unavailable in this environment, so no screenshot evidence is claimed.

Run the checks locally from the repository directory after installing the test extra:

```bash
python -m pytest -q
python examples/fuel_comparison.py
python examples/all_scenarios.py
pyrolysis-demo --scenario zone_temperature
python -m streamlit run app/app.py --server.address 127.0.0.1
```

The declared dependency ranges support installation; `requirements-tested.txt` records exact third-party versions used for this run. To recreate those versions, install that file and then install this project with `python -m pip install --no-deps .`.

No unsupported physics is represented as a skipped validation that might pass later without additional evidence. The suite explicitly verifies that unavailable relationships stay unavailable. Passing these checks establishes software behavior and consistency with declared equations, not real-furnace accuracy, safe operation, external-provider compatibility or AI reasoning quality. Python versions other than 3.12 were not exercised.
