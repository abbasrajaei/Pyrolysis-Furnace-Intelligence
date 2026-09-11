# Heat-transfer and thermal-efficiency methodology

## Purpose

The heat-transfer layer connects the combustion calculation to a simple furnace energy balance.

The questions are:

- How much of the fired heat is absorbed in the radiant section?
- How much is recovered in the convection section?
- How much leaves with the stack gas?
- What happens to overall efficiency when stack temperature or excess air changes?
- How does radiant heat loading change average and peak heat flux?
- How does a combustion change propagate into furnace heat recovery?

The public implementation is intentionally a **lumped engineering model**. It is not CFD and it does not calculate local flame radiation or local tube-metal temperature.

## Energy balance

The workbench closes the furnace balance as:

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

The combustion workbench provides the fired duty and flue-gas mass flow.

### Stack sensible-heat loss

The public model calculates:

\[
Q_{stack}
=
\frac{\dot m_{fg}\,C_{p,fg}^{eff}\,(T_{stack}-T_{ambient})}{3.6\times10^6}
\]

for:

- \(\dot m_{fg}\) in kg/h;
- \(C_{p,fg}^{eff}\) in kJ/kg-K;
- temperature difference in K;
- \(Q_{stack}\) in MW.

The public effective flue-gas heat capacity is:

\[
C_{p,fg}^{eff}=1.34\;\text{kJ/kg-K}
\]

This is a **source-informed lumped value**, not a composition-dependent property package. Internal source reconstruction showed that this value closes the documented normal furnace heat balance to normal engineering rounding when used with the documented stack and ambient temperatures. Exact plant reference values are not published in this repository.

### Other heat loss

A separate public teaching assumption accounts for casing/radiation and other unmodelled losses:

\[
Q_{other}=f_{loss}\,Q_{fired}
\]

The default public value is 1% of fired duty.

It is intentionally separate from stack loss so that increasing excess air or stack temperature does not get hidden inside one residual term.

### Useful heat and efficiency

\[
Q_{useful}=Q_{fired}-Q_{stack}-Q_{other}
\]

\[
\eta_{overall}
=
\frac{Q_{useful}}{Q_{fired}}
\]

The useful heat is then divided between radiant absorption and convection recovery.

## Radiant and convection split

The public workbench uses a declared radiant share of fired duty:

\[
Q_{radiant}=f_{radiant}\,Q_{fired}
\]

and:

\[
Q_{convection}=Q_{useful}-Q_{radiant}
\]

The radiant share is a **study input/assumption** in the public model. It is not treated as a direct plant actuator.

The default teaching values are slightly different for start-of-run and end-of-run so the model can represent the idea that furnace heat distribution changes with operating condition without publishing proprietary performance data.

## Radiant heat flux

Average radiant heat flux is calculated from:

\[
q''_{avg}
=
\frac{Q_{radiant}}{A_{radiant}}
\]

The public effective radiant area is:

\[
A_{radiant}=420\;\text{m}^2
\]

Peak heat flux is represented with a public teaching ratio:

\[
q''_{peak}=1.14\,q''_{avg}
\]

These calculations are useful for understanding heat loading.

They are **not** a local burner-to-tube radiation model and should not be interpreted as a prediction of a particular tube location.

## Convection-section recovery

The convection section is represented using the following public teaching distribution of total convection duty:

| Bank | Share of convection duty |
|---|---:|
| HTC-II | 26% |
| HPSSH-II | 15% |
| HPSSH-I | 16% |
| HTC-I | 22% |
| ECO | 12% |
| FPH | 9% |

The shares sum to 100%.

They preserve the physical idea of a multi-service convection section while remaining generalised for the public portfolio.

The process documentation used in developing this project describes a convection-section sequence selected to maximise heat recovery and optimise the process crossover temperature. The public workbench does not reproduce proprietary bank geometry or vendor rating calculations.

## Coupling with combustion

The heat-transfer layer uses the current result from the combustion layer rather than creating an independent furnace.

This creates the following relationships.

### Excess air

\[
EA\uparrow
\rightarrow
\dot m_{fg}\uparrow
\rightarrow
Q_{stack}\uparrow
\rightarrow
\eta_{overall}\downarrow
\]

for a fixed stack temperature.

### Stack temperature

\[
T_{stack}\uparrow
\rightarrow
Q_{stack}\uparrow
\rightarrow
Q_{useful}\downarrow
\rightarrow
\eta_{overall}\downarrow
\]

### Feed rate

The combustion layer converts process load into required firing. Therefore:

\[
\dot m_{feed}\uparrow
\rightarrow
Q_{fired}\uparrow
\rightarrow
Q_{radiant}\uparrow
\rightarrow
q''_{avg}\uparrow
\]

when the heat split and geometry are held constant.

### Fuel composition

Fuel composition changes the combustion-product flow.

At the same fired duty and stack temperature:

\[
Fuel\ composition
\rightarrow
\dot m_{fg}
\rightarrow
Q_{stack}
\rightarrow
\eta_{overall}
\]

The public thermal model uses one effective flue-gas heat capacity, so it captures the first-order mass-flow effect but not the full composition dependence of flue-gas enthalpy.

### Radiant share

\[
f_{radiant}\uparrow
\rightarrow
Q_{radiant}\uparrow
\rightarrow
q''_{avg}\uparrow
\]

while:

\[
Q_{convection}\downarrow
\]

for the same total useful heat.

Changing the split alone does not create additional useful energy.

## Why tube-metal temperature is not calculated

The source material makes the engineering importance clear: coke retards heat transfer, tube-metal temperature rises as the coke layer grows, and tube temperature can become the operating limit.

However, the public source set does not provide enough information for a defensible off-design tube-metal-temperature model. A rigorous calculation would require, among other things:

- local heat flux;
- tube geometry by location;
- inside heat-transfer coefficient;
- coke thickness and conductivity;
- tube thermal conductivity;
- local process-fluid temperature;
- local flame/radiation field.

For this reason the current heat-transfer layer calculates **heat loading**, but does not convert it into a precise tube-metal temperature or coking rate.

## What the module can support

The current model is appropriate for engineering what-if studies such as:

- effect of stack temperature on efficiency;
- effect of excess air on stack loss;
- effect of feed load on fired duty and radiant flux;
- effect of radiant/convection split on heat loading;
- effect of fuel-composition-driven flue-gas flow on heat loss;
- comparison of start-of-run and end-of-run teaching conditions.

## What it does not claim

The module does not claim to predict:

- CFD velocity or temperature fields;
- detailed flame radiation;
- local view factors;
- local tube heat flux;
- tube-metal temperature;
- detailed convection coefficients;
- fouling resistance;
- coking rate;
- tube life;
- burner-to-coil maldistribution;
- plant-specific stack-loss guarantees.

Those limitations are deliberate.
