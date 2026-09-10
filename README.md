# Pyrolysis Furnace Intelligence

## Furnace Engineering Workbench

**Interactive combustion, thermal-performance, firing-distribution and control-scenario analysis for a synthetic industrial pyrolysis furnace.**

Pyrolysis Furnace Intelligence 2.0 is built as an engineering workbench rather than a static dashboard. A user starts from a baseline or preset operating case, changes one or more furnace inputs, and immediately sees the calculated consequences, sensitivity curves, baseline deviation and context-sensitive engineering guidance.

The public model is independently authored and uses synthetic teaching conditions. It is not a plant digital twin, operating tool, safety system or APC/BMS replacement.

## What makes the workbench useful

The interface is organized around the way an engineer investigates a furnace problem:

**baseline → change → consequence → sensitivity → guidance → compare**

The user can:

- load ready-made cases such as hydrogen-rich fuel, high load, reduced load, low/high excess air, zone redistribution, fuel-pressure constraint and strong induced draft;
- change fuel composition without manually forcing mole fractions back to 100% — unlocked components automatically renormalize;
- lock fuel components that should remain fixed while another component is changed;
- vary chemical duty, excess air, draft, heat recovery, radiant share, firing splits, feed, steam/feed ratio and zone correction;
- inspect current values against a retained baseline;
- sweep supported input/output relationships and see the full sensitivity curve plus the current and baseline points;
- save study cases and compare them side-by-side;
- read a persistent **Engineering Guidance** panel explaining what changed, why it matters, what else is affected, what to watch and which conclusions are only qualitative.

## Workbench screens

| Screen | Purpose |
|---|---|
| **Furnace Overview** | Current operating study, KPI deviation, automatic sensitivity and six-zone firing state |
| **Scenario Studio** | Thirteen bounded static operating/disturbance templates |
| **Combustion** | Fuel composition, LHV, lower Wobbe, air requirement and O₂ sensitivity |
| **Thermal Performance** | Chemical input, useful-duty partition, radiant/convection duty and residual heat |
| **Firing & Zones** | Inlet/outlet, bottom/sidewall and six-zone conserved firing distribution |
| **Control Response** | Functional fuel-pressure authority plus bounded draft teaching correlations |
| **Sensitivity Lab** | User-selected supported X → Y engineering parameter sweeps |
| **Case Comparison** | Baseline, current and saved operating-study comparison |
| **Model Limits** | Explicit numerical and physical boundaries |

## Example investigations

A user can ask questions such as:

- If H₂ rises from 20 to 50 mol%, how do mass LHV, lower Wobbe, stoichiometric air and equivalent fuel demand change?
- If excess air rises, what happens to actual air and ideal dry O₂?
- If total firing rises at fixed distribution, how do inlet, outlet and maximum-zone duties change?
- If the inlet/outlet firing ratio changes, how is the same total duty redistributed?
- If Zone C receives an explicit teaching correction, how much do the other five zones donate while inlet firing remains conserved?
- If fuel-pressure authority changes, which functional control authority is active?
- Under the optional fixed-resistance draft teaching model, how does relative airflow vary with furnace draft?

Unsupported questions remain unsupported rather than being filled with plausible-looking numbers.

## Intelligent fuel composition

The workbench never asks the user to manually repair a fuel composition after every change.

For example, starting from:

\`\`\`text
H2   20%
CH4  70%
C2H6 10%
N2    0%
\`\`\`

setting H₂ to 40% automatically renormalizes the unlocked balance while preserving the relative proportions of the other unlocked components. Components may be locked when they should remain fixed.

## Sensitivity curves, not decorative charts

The central plots are one-factor engineering studies. They answer:

> **What happens to Y if I vary X while holding the other current-case inputs fixed?**

Each supported plot contains:

- the full sensitivity curve;
- the **current** operating-study point;
- the retained **baseline** point;
- a basis label such as **CALCULATED**, **ASSUMPTION + CALCULATED**, or **MODEL / ASSUMPTION**.

These curves are not time histories. Version 2.0 does not integrate furnace dynamics.

## Engineering Guidance

The right-hand guidance rail reacts to the parameter being changed.

For a fuel-composition change it can distinguish, for example:

- **calculated:** fuel demand, mixture energy properties, stoichiometric/actual air;
- **qualitative:** flame-speed or burner-operability implications;
- **not predicted:** flashback limit, NOx, flame shape or plant stability margin.

For a draft change it explains the pressure/airflow concept while clearly stating that no plant fan curve, burner-register model or leakage coefficient is available.

This separation is deliberate: engineering reasoning is useful only when its evidence boundary is visible.

## Engineering model

For a declared mixture with elemental totals \(C,H,O,N\), ideal complete combustion uses:

\[
n_{O_2,st}=C+\frac{H}{4}-\frac{O}{2}
\]

and dry-air demand:

\[
n_{air}=4.76\,n_{O_2,st}(1+e)
\]

For fixed chemical duty:

\[
\dot m_f=\frac{Q_{fired}}{LHV_m}
\]

The thermal workbench uses a conserved static partition:

\[
Q_{fired}=Q_{radiant}+Q_{convection}+Q_{residual}
\]

Six-zone and outlet allocation preserves total firing:

\[
Q_{fired}=\sum_{i=A}^{F}Q_i+Q_{outlet,bottom}+Q_{outlet,sidewall}
\]

The optional draft sensitivity uses a clearly labelled fixed-effective-resistance teaching relation:

\[
Q_{air,rel}=\sqrt{\frac{|P_{draft}|}{|P_{draft,ref}|}}
\]

It is not a plant airflow calibration.

## Model boundaries

**Supported:** ideal declared combustion, mixture energy-property comparison, static heat accounting, conserved firing allocation, steam base demand, functional pressure authority, one-factor sensitivity analysis, deterministic guidance and static scenario studies.

**Not claimed:** CFD, local flame temperature/shape, flame-speed prediction, flashback limits, CO/NOx prediction, rigorous cracking or coking kinetics, tube-metal temperature, tube life, local heat flux, identified dynamic COT response, PID tuning, valve characteristics, calibrated fan/register/leakage response, plant safety logic or autonomous control.

See [Model boundaries](docs/model_boundaries.md) and [Methodology](docs/methodology.md).

## Run locally

Python 3.12 is the CI runtime.

\`\`\`bash
git clone https://github.com/abbasrajaei/Pyrolysis-Furnace-Intelligence.git
cd Pyrolysis-Furnace-Intelligence
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[test]"
python app/app.py
\`\`\`

On Windows:

\`\`\`bat
.venv\\Scripts\\activate
python -m pip install ".[test]"
python app/app.py
\`\`\`

Then open:

\`\`\`text
http://127.0.0.1:8050
\`\`\`

The application exposes \`server = app.server\` and includes a \`Procfile\` / \`render.yaml\` for hosted deployment with Gunicorn.

## Validation

The Python 3.12 GitHub Actions workflow installs the public package, runs the complete public engineering/workbench test suite, executes both public examples and the CLI, and verifies the Dash HTTP root.

The current exact test count is recorded by the latest successful workflow run. Passing tests establish software/equation behavior against the declared teaching model; they do not establish real-furnace accuracy or safe operation.

See [Validation](docs/validation.md) and [Reproducibility](docs/reproducibility.md).

## Repository structure

\`\`\`text
app/        Dash engineering workbench + industrial-style CSS
src/        combustion, thermal, firing, control, sensitivity and guidance engine
data/       public synthetic teaching inputs
tests/      public engineering and application test suite
examples/   CLI engineering examples
docs/       methodology, validation, data policy and model boundaries
assets/     portfolio figures retained for GitHub documentation
\`\`\`

## License and citation

Author: **Abbas Rajaei**

Software version: **2.0.0**

Citation metadata: [CITATION.cff](CITATION.cff)  
License: [MIT](LICENSE)
