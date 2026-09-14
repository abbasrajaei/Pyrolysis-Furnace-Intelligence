# Pyrolysis Furnace Intelligence

**Pyrolysis Furnace Intelligence** is an interactive furnace-engineering workbench that connects combustion, heat transfer and pyrolysis process behaviour in one model. I built it to make the relationships between fuel quality, excess air, firing, heat recovery and process severity visible rather than treating each variable as an isolated calculation. The public model uses generalised teaching conditions and is intended for engineering study, education and portfolio work; it is not a plant digital twin, CFD package, BMS, APC or safety system.

## Software

<p align="center">
  <img src="assets/software-combustion.jpg" width="49%" alt="Combustion workspace">
  <img src="assets/software-thermal-performance.jpg" width="49%" alt="Thermal performance workspace">
</p>

<p align="center"><em>Combustion workspace · Thermal-performance workspace</em></p>

The application has three connected layers. **Combustion** calculates fuel properties, LHV, Wobbe Index, stoichiometric and actual air, flue gas, CO₂ and burner loading. **Heat Transfer** follows fired duty into radiant heat, convection recovery, stack loss, box efficiency, overall efficiency and teaching heat flux. **Process** connects feed, dilution steam, coil temperatures, pressure drop, residence time, hydrocarbon partial pressure and relative time-temperature severity. Each layer uses the same engineering state, so a change made upstream can be followed into its downstream consequences.

## Engineering basis

For gaseous firing, fuel quality affects both heating value and density, so fuel flow alone is not enough to describe heat release:

$$
Q_{fired}=\dot m_{fuel}LHV
\qquad
WI=\frac{HV_v}{\sqrt{SG}}
$$

Combustion air is calculated from stoichiometric oxygen demand and excess air, while the thermal and process layers close the linked energy balances:

$$
Air_{actual}=Air_{stoich}(1+EA)
$$

$$
Q_{fired}=Q_{radiant}+Q_{convection}+Q_{stack}+Q_{other}
\qquad
Q_{radiant}=Q_{sensible}+Q_{reaction,residual}
$$

These relationships let the workbench follow changes in fuel composition, excess air, feed and thermal conditions through fuel demand, flue-gas flow, CO₂, heat recovery, efficiency and process behaviour.

## Why I built it

The project grew from my experience with industrial olefin cracking furnaces and from studying combustion, heat transfer and furnace-control philosophy. Variables that appear separately on a control-room screen—fuel composition, fuel flow, Wobbe Index, excess oxygen, flue gas, firing distribution and process temperature—are parts of one physical system. I wanted a compact tool where changing one variable immediately shows what else moves and why.

## Scope, validation and confidentiality

The model deliberately stops where the public engineering basis becomes too weak. It does not claim CFD, local flame prediction, NOx/CO prediction, local tube heat flux, tube-metal temperature, tube life, detailed cracking yields, coke-growth prediction, dynamic PID trajectories, plant trips or safe-to-operate decisions. Conversion remains a teaching/case anchor rather than a claimed off-design kinetic prediction. More detail is available in [heat-transfer methodology](docs/heat_transfer_methodology.md) and [process methodology](docs/process_methodology.md).

Automated tests check both software behaviour and physical direction: mixture closure, fuel/air/flue-gas balances, hydrogen-rich fuel reducing carbon at constant duty, excess air increasing air and flue-gas flow without creating carbon, feed and steam moving required duty in the expected direction, and firing redistribution conserving total duty. Proprietary plant drawings and plant-specific operating data are not reproduced; public values are generalised or synthetic where necessary.

## Windows desktop

For Windows users, download the latest desktop build from [GitHub Releases](https://github.com/abbasrajaei/Pyrolysis-Furnace-Intelligence/releases/latest). The packaged application runs locally and does not require a separate Python installation. The direct EXE installer is currently unsigned and may trigger a Windows SmartScreen warning; the repository also contains the MSIX prepared for Microsoft Store distribution.

To run from source with the tested Python 3.12 environment:

```bash
git clone https://github.com/abbasrajaei/Pyrolysis-Furnace-Intelligence.git
cd Pyrolysis-Furnace-Intelligence
python -m venv .venv
# activate the environment, then:
python -m pip install ".[test]"
python app/app.py
```

Open `http://127.0.0.1:8050`.

## Privacy and author

Pyrolysis Furnace Intelligence is designed to run locally and does not intentionally collect, transmit, sell or share personal information. See the [Privacy Policy](PRIVACY.md).

**Abbas Rajaei — Chemical / Process Engineer**  
This project is part of my continuing work on industrial combustion, furnace optimisation, process control and decarbonisation of energy-intensive processes.
