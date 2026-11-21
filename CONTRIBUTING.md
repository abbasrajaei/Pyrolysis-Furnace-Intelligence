# Contributing

Use Python 3.12 and an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[test]"
python -m pytest -q
```

Keep engineering calculations in the package and presentation code in the application. Use descriptive names, explicit units and short functions. Explain changes to mathematical basis or provenance; avoid unrelated refactoring in an engineering change.

New numerical functions require tests for a defensible reference or independently checkable equation, invalid inputs, conservation where relevant, and unavailable propagation. Never substitute an unsupported plant value or fitted coefficient for unavailable evidence. A teaching assumption must remain labelled as such in downstream results.

Preserve state authority and fail-closed supervisor validation. New scenarios must distinguish requests, measured/reference quantities and physical allocation. Do not introduce operating commands, safety determinations or unqualified plant-validation claims.

Keep readable data and packaged YAML resources synchronized. Do not contribute confidential documents, original tags, real operating datasets, credentials or proprietary drawings. Public diagrams and examples must be independently authored and publication-safe. Re-run tests and examples before proposing a change.
