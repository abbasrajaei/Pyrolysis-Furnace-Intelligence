# Technical methodology

Pyrolysis Furnace Intelligence uses one connected furnace state across three layers: Combustion, Heat Transfer and Process. Public operating values are synthetic or generalised, and the software does not read proprietary source documents at runtime.

## Combustion

The fuel model supports $H_2$, $CH_4$, $C_2H_4$, $C_2H_6$, $C_3H_8$, $CO$, $CO_2$ and $N_2$. Mole fractions close to one, with a selected balance component adjusted when another component changes.

For elemental totals $C$, $H$ and $O$, stoichiometric oxygen demand is

$$
\nu_{O_2,\mathrm{st}}=C+\frac{H}{4}-\frac{O}{2}
$$

The model assumes complete combustion and applies the selected excess-air fraction. It includes nitrogen, argon and water from the declared humid-air basis, but it does not calculate dissociation, soot, CO formation or NOx.

For fuel mole fractions $x_i$, mixture molecular weight and mass lower heating value are

$$
M_f=\sum_i x_iM_i
$$

$$
LHV_m=
\frac{\sum_i x_iM_iLHV_i}{M_f}
$$

The lower Wobbe Index is

$$
WI_L=\frac{LHV_V}{\sqrt{M_f/M_{\mathrm{air}}}}
$$

These equations support fuel-comparison studies. They are not a burner, valve or fuel-gas-system calibration.

## Process load and firing

The normal study uses a public start-of-run or end-of-run case. Process load is represented by

$$
L=\dot{m}_{\mathrm{HC}}+k_s\dot{m}_{\mathrm{steam}}
$$

with

$$
k_s=\frac{1}{3}
$$

Required fired duty scales from the selected teaching case:

$$
Q_{\mathrm{required}}=
Q_{\mathrm{ref}}
\frac{L}{L_{\mathrm{ref}}}
$$

This is a normal-load engineering approximation, not a cracking-kinetics model. The interface warns when feed falls below the intended range.

Fuel-composition studies can hold fired duty, fuel mass flow or burner pressure difference constant. At constant fired duty,

$$
\dot{m}_f=\frac{Q_{\mathrm{fired}}}{LHV}
$$

At constant burner pressure difference, the public study uses the Wobbe approximation

$$
\frac{Q_2}{Q_1}\approx\frac{WI_2}{WI_1}
$$

The bottom/sidewall split conserves total fired duty:

$$
Q_{\mathrm{bottom}}=f_bQ_{\mathrm{fired}}
$$

$$
Q_{\mathrm{sidewall}}=(1-f_b)Q_{\mathrm{fired}}
$$

Public burner counts and loading limits are generalised teaching values.

## Heat transfer

The Heat Transfer layer uses fired duty and flue-gas flow from Combustion. The furnace balance is

$$
Q_{\mathrm{fired}}=
Q_{\mathrm{radiant}}+
Q_{\mathrm{convection}}+
Q_{\mathrm{stack}}+
Q_{\mathrm{other}}
$$

Stack sensible-heat loss is

$$
Q_{\mathrm{stack}}=
\frac{\dot{m}_{\mathrm{fg}}C_{p,\mathrm{fg}}^{\mathrm{eff}}
\left(T_{\mathrm{stack}}-T_{\mathrm{ambient}}\right)}
{3.6\times10^6}
$$

with

$$
C_{p,\mathrm{fg}}^{\mathrm{eff}}=1.34\ \mathrm{kJ\,kg^{-1}\,K^{-1}}
$$

Useful heat and overall efficiency are

$$
Q_{\mathrm{useful}}=
Q_{\mathrm{fired}}-Q_{\mathrm{stack}}-Q_{\mathrm{other}}
$$

$$
\eta_{\mathrm{overall}}=
\frac{Q_{\mathrm{useful}}}{Q_{\mathrm{fired}}}
$$

Radiant and convection duty are

$$
Q_{\mathrm{radiant}}=f_{\mathrm{radiant}}Q_{\mathrm{fired}}
$$

$$
Q_{\mathrm{convection}}=
Q_{\mathrm{useful}}-Q_{\mathrm{radiant}}
$$

Average and peak teaching heat flux are

$$
q''_{\mathrm{avg}}=
\frac{Q_{\mathrm{radiant}}}{A_{\mathrm{radiant}}}
$$

$$
q''_{\mathrm{peak}}=1.14\,q''_{\mathrm{avg}}
$$

using the public effective area $A_{\mathrm{radiant}}=420\ \mathrm{m^2}$. These are heat-loading indicators, not local tube-by-tube radiation predictions.

## Process layer

The Process layer takes the current feed and steam condition from Combustion and the radiant result from Heat Transfer. It estimates sensible heat, residual reaction heat, pressure drop, hydrocarbon partial pressure, residence time and a relative time-temperature severity index. The equations and boundaries are documented in [process methodology](process_methodology.md).

## Linked effects

The three layers remain connected. For example, at fixed stack temperature,

$$
EA\uparrow
\;\Rightarrow\;
\dot{m}_{\mathrm{fg}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{stack}}\uparrow
\;\Rightarrow\;
\eta_{\mathrm{overall}}\downarrow
$$

A feed-rate change alters required firing and therefore radiant duty and heat flux. A fuel-composition change can alter fuel demand, air demand and flue-gas flow, which then changes the thermal balance. The response plots are one-factor engineering studies: every square is recalculated from the same deterministic model as the numerical results, while Before and Now are two static states rather than a time trajectory.

## Boundary

The workbench does not infer missing plant physics. Draft is not used as a calibrated airflow input, and tube-metal temperature, coking rate, cracking yields, PID dynamics, valve trajectories and plant trip logic remain outside the public numerical model. See [model boundaries](model_boundaries.md) for the full scope.
