# Reproducibility

The public engineering model uses only repository-owned teaching inputs and packaged resources. No external engineering data service or AI provider is needed. Python 3.12 is the verified runtime; other declared-compatible versions have not been tested.

For exact third-party versions from the engineering validation run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python -m pip install --no-deps .
python -m pytest -q
python examples/all_scenarios.py
python examples/fuel_comparison.py
pyrolysis-demo --scenario zone_temperature
python -m streamlit run app/app.py --server.address 127.0.0.1
```

The repository's test extra also permits installation from declared dependency ranges. The Python 3.12 CI workflow performs a regular installation and runs the same public tests and examples; no deployment is configured. A committed workflow is not evidence that a remote CI run has completed.

The figure generator is separate from the runtime engine. Install `.[figures]` and run `python tools/generate_portfolio_figures.py`. It reads only public model results and writes five PNGs plus `assets/figure_data.json`. Numbers are reproducible; rendered pixels can vary with Matplotlib and font versions. The SVGs are independently authored conceptual architecture, not model geometry.

The public test suite has 128 cases and zero skipped tests. Unsupported numerical relationships have explicit unavailable assertions. Streamlit AppTest checks view execution; loopback HTTP checks verify server startup. Neither is a browser visual/accessibility audit. No live AI provider or remote endpoint compatibility is part of these claims.
