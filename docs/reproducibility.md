# Reproducibility

The public workbench uses only repository-owned teaching inputs and packaged resources. No external engineering data service or AI provider is needed. Python 3.12 is the CI runtime.

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[test]"
python -m pytest -q
python examples/all_scenarios.py
python examples/fuel_comparison.py
pyrolysis-demo --scenario zone_temperature
python app/app.py
\`\`\`

On Windows activate with \`.venv\\Scripts\\activate\`. The Dash application starts on \`http://127.0.0.1:8050\` by default. The optional \`PORT\` environment variable is used for hosted deployment.

\`requirements-tested.txt\` records the dependency ranges validated by the public CI workflow. The GitHub Actions workflow installs the package from \`pyproject.toml\` on Python 3.12, runs the complete public test suite, then executes the public examples and CLI.

The workbench's sensitivity engine is deterministic. Each sensitivity plot varies one supported input while holding the other current-case inputs fixed. Fuel-component sweeps automatically renormalize the remaining composition. The draft curve is explicitly a fixed-resistance teaching model rather than a plant calibration.

The figure generator remains separate from the runtime engine. Install \`.[figures]\` and run \`python tools/generate_portfolio_figures.py\` if the static portfolio assets are required. The interactive Dash application does not depend on those portfolio figures.

No live AI provider or remote endpoint is required for the workbench. Passing tests establishes software behavior and consistency with declared equations and assumptions, not real-furnace accuracy, safe operation or plant validation.
