# Technical methodology

Pyrolysis Furnace Intelligence is a public educational engineering workbench. The active interface has two connected layers: **Combustion** and **Heat transfer**. Public operating values are synthetic or generalised. The software does not read proprietary source documents at runtime.

## Combustion layer

The combustion workbench accepts a declared gaseous-fuel composition containing:

\[
H_2,\ CH_4,\ C_2H_4,\ C_2H_6,\ C_3H_8,\ CO,\ CO_2,\ N_2
\]

Fuel mole fractions must close to one. In the interface, when one component is changed a selected balance component is adjusted so the total remains 100%.

For one mole of mixture with elemental totals \(C\), \(H\) and \(O\), theoretical oxygen demand is:

\[
\nu_{O_2,st}=C+\frac{H}{4}-\frac{O}{2}
\]

Actual oxygen and air are calculated from the selected excess-air fraction. The current combustion workbench also includes nitrogen, argon and water carried in with the declared humid ambient-air basis.

The model assumes complete combustion. It does not calculate oxygen-deficient products, dissociation, soot, CO or NOx formation.

### Fuel properties

For mole fractions \(x_i\):

\[
M_f=\sum_i x_iM_i
\]

Mass lower heating value is calculated from rounded public component values:

\[
LHV_m=
\frac{\sum_i x_iM_iLHV_i}{M_f}
\]

For the declared normal-volume basis, volumetric LHV and lower Wobbe Index are then calculated as:

\[
WI_L=\frac{LHV_V}{\sqrt{M_f/M_{air}}}
\]

These values support fuel-comparison studies. They are not an installed burner, valve or fuel-gas-system calibration.

### Fired duty and fuel-flow study basis

The normal operating study uses a public start-of-run or end-of-run teaching case. Process load is represented by a source-informed load index:

\[
L=
\dot m_{HC}
+
k_s\dot m_{steam}
\]

with:

\[
k_s=\frac{1}{3}
\]

The required fired duty scales from the selected public teaching condition:

\[
Q_{required}
=
Q_{ref}
\frac{L}{L_{ref}}
\]

This is an engineering approximation around normal operating conditions, not a rigorous cracking-reaction model. A low-load warning is generated when the selected feed falls below the intended normal-load range.

Fuel-composition studies support three declared bases:

1. **Keep fired duty constant**

\[
\dot m_f=\frac{Q_{fired}}{LHV}
\]

2. **Keep fuel mass flow constant**

Fuel flow remains fixed and fired duty changes with LHV.

3. **Keep burner pressure difference constant**

The workbench uses a Wobbe-based approximation:

\[
\frac{Q_2}{Q_1}
\approx
\frac{WI_2}{WI_1}
\]

This third mode is a fuel-interchangeability study, not a plant burner-flow map.

### Burner allocation

The current combustion page supports a bottom/sidewall firing split while conserving total fired duty:

\[
Q_{bottom}=f_bQ_{fired}
\]

\[
Q_{sidewall}=(1-f_b)Q_{fired}
\]

Public burner counts and loading points are generalised teaching values.

## Heat-transfer and thermal-efficiency layer

The heat-transfer layer uses the **current combustion result**. It does not create an independent furnace. Therefore changes in feed, excess air or fuel composition can propagate into the thermal calculation.

The furnace energy balance is:

\[
Q_{fired}
=
Q_{radiant}
+
Q_{convection}
+
Q_{stack}
+
Q_{other}
\]

### Stack sensible-heat loss

\[
Q_{stack}
=
\frac{
\dot m_{fg}
C_{p,fg}^{eff}
(T_{stack}-T_{ambient})
}
{3.6\times10^6}
\]

where flue-gas flow is in kg/h and the public effective heat capacity is:

\[
C_{p,fg}^{eff}=1.34\ \text{kJ/kg-K}
\]

This is a source-informed lumped value. It is not a composition-dependent flue-gas property package.

### Other heat loss

\[
Q_{other}=f_{loss}Q_{fired}
\]

The public default is 1% of fired duty. This term represents casing/radiation and other unmodelled heat loss separately from stack sensible heat.

### Useful heat and overall efficiency

\[
Q_{useful}
=
Q_{fired}
-
Q_{stack}
-
Q_{other}
\]

\[
\eta_{overall}
=
\frac{Q_{useful}}{Q_{fired}}
\]

### Radiant and convection split

The public heat-transfer page uses a declared radiant share of fired duty:

\[
Q_{radiant}
=
f_{radiant}Q_{fired}
\]

and:

\[
Q_{convection}
=
Q_{useful}
-
Q_{radiant}
\]

The radiant share is a **study assumption**. It is not presented as a direct operator actuator.

Box efficiency is shown as:

\[
\eta_{box}
=
\frac{Q_{radiant}}{Q_{fired}}
\]

### Radiant heat flux

Average teaching heat flux is:

\[
q''_{avg}
=
\frac{Q_{radiant}}{A_{radiant}}
\]

using the public effective area:

\[
A_{radiant}=420\ \text{m}^2
\]

Peak teaching heat flux is:

\[
q''_{peak}=1.14\,q''_{avg}
\]

The area and peak/average factor are public model values. These outputs show heat-loading sensitivity; they are not local tube-by-tube radiation predictions.

### Convection heat recovery

The public convection duty is distributed across the six process/service groups:

| Bank | Public share |
|---|---:|
| HTC-II | 26% |
| HPSSH-II | 15% |
| HPSSH-I | 16% |
| HTC-I | 22% |
| ECO | 12% |
| FPH | 9% |

These rounded shares sum to 100% and preserve the physical multi-service convection-section concept. They do not reproduce proprietary bank rating calculations.

A fuller thermal description is in docs/heat_transfer_methodology.md.

## Cross-module effects

The active workbench is designed so the two layers remain physically connected.

For example, at fixed stack temperature:

\[
EA\uparrow
\rightarrow
\dot m_{fg}\uparrow
\rightarrow
Q_{stack}\uparrow
\rightarrow
\eta_{overall}\downarrow
\]

A fuel-composition change can alter flue-gas flow and therefore stack sensible-heat loss. A feed-rate change alters required firing and, with the same public radiant-share and geometry assumptions, changes radiant duty and heat flux.

The selected combustion hold mode is retained when a fuel-composition study is viewed in the Heat Transfer module.

## Response graphs

The main response graphs are one-factor engineering studies.

The last supported input changed by the user becomes the x-variable. The selected engineering response becomes the y-variable. Every displayed square is recalculated using the same model as the numerical result cards.

The larger **Before** and **Now** squares show two static states. They do not represent a time trajectory.

## Why tube-metal temperature and coking are not calculated

The physical source basis shows that coke retards heat transfer, raises tube-metal temperature and increases radiant-coil pressure drop. It also shows that tube temperature can become an operating limitation.

The public project does not yet calculate a current tube-metal temperature or coking rate because a defensible model would require additional information such as:

- local heat flux;
- local tube and process-fluid temperature;
- process-side heat-transfer coefficient;
- tube thermal conductivity;
- coke thickness and conductivity;
- local radiation/view-factor information.

The workbench therefore stops at heat loading rather than inventing a precise tube-metal-temperature result.

## Draft

Draft is physically connected with burner pressure difference and air admission, but the current combustion cockpit does not use draft as a calibrated quantitative airflow input.

A legacy educational engine retained in the repository includes a fixed-effective-resistance relation:

\[
Q_{air,rel}
=
\sqrt{
\frac{|P_{draft}|}
{|P_{draft,ref}|}
}
\]

It remains explicitly labelled as a teaching assumption and is not used as a plant air-flow calibration.

## Retained firing/control teaching modules

The repository still contains earlier educational modules for firing allocation, temperature selection, pressure-authority states, scenarios, deterministic engineering guidance and a bounded supervisor contract.

These modules are not presented as recovered plant logic. They remain simplified educational structures and do not calculate PID tuning, valve trajectories, trip timing or autonomous control actions.

## Provenance and public-data policy

The public repository distinguishes general property references, synthetic/public teaching conditions, assumptions and calculated values.

Proprietary plant drawings and exact operating datasets are not included in the public model. The figures in assets/ are independently authored conceptual diagrams.

For the full capability boundary, see docs/model_boundaries.md.
