# Process and cracking-severity methodology

## Purpose

The process layer connects the combustion and heat-transfer calculations to the material flowing through the radiant coils.

The questions are:

- How do feed rate and dilution steam affect residence time and pressure drop?
- How does coil outlet temperature change time-temperature severity?
- How much of the linked radiant heat is used for sensible heating versus the endothermic reaction?
- Why can lower furnace throughput increase over-cracking risk if COT is not reduced?
- Why does more dilution steam lower hydrocarbon partial pressure but also increase pressure drop and heat demand?
- How should coking be represented without pretending to have a full coke-growth model?

The public implementation is a source-informed teaching model. It does not calculate rigorous cracking kinetics or product yields.

## Linked process inputs

The Process module uses the same furnace state as the other workbench modules.

From Combustion it receives hydrocarbon feed rate, steam/feed ratio and required fired duty. From Heat transfer it receives radiant heat absorbed and average radiant heat flux.

The process-only study inputs are coil inlet temperature and coil outlet temperature (COT).

## Radiant sensible/reaction heat split

A pyrolysis coil needs both sensible heat and reaction heat.

The public model first estimates the sensible part:

\[
Q_{sensible}
=
\dot m_{process}
C_p^{eff}
(T_{COT}-T_{in})
\]

where:

\[
\dot m_{process}
=
\dot m_{HC}
+
\dot m_{steam}
\]

The public effective heat capacity is:

\[
C_p^{eff}=3.70\;\text{kJ/kg-K}
\]

This is a lumped teaching value chosen to represent the hot reacting process stream.

The remaining linked radiant heat is displayed as:

\[
Q_{reaction,residual}
=
Q_{radiant}
-
Q_{sensible}
\]

This quantity is deliberately called **residual reaction heat**. It is not a rigorous reaction-enthalpy calculation because composition changes continuously along the cracking coil.

The purpose is to make the main physical point visible: a pyrolysis furnace does not only heat the stream. A large part of the radiant duty supports strongly endothermic cracking reactions.

## Coil pressure drop

The selected operating case contains a generalised pressure-drop reference.

The public off-design teaching relation is:

\[
\Delta P
=
\Delta P_{ref}
\left(
\frac{\dot m_{process}}
{\dot m_{process,ref}}
\right)^2
\left(
\frac{T_{avg}}
{T_{avg,ref}}
\right)
\]

This captures the expected first-order direction: more feed or steam increases process flow; higher flow increases coil pressure drop; hotter gas has lower density and tends to increase pressure drop.

It is not a detailed compressible pipe-flow or coke-roughness model.

Start-of-run and end-of-run have separate public pressure-drop anchors so the effect of progressive furnace run condition can be represented without publishing plant-specific data.

## Hydrocarbon partial pressure

Dilution steam is important because it reduces hydrocarbon partial pressure.

The public model converts hydrocarbon and steam mass flow to molar flow using a generalised ethane-rich feed molecular weight:

\[
MW_{HC}=30.0\;\text{kg/kmol}
\]

The hydrocarbon mole fraction is:

\[
y_{HC}
=
\frac{\dot n_{HC}}
{\dot n_{HC}+\dot n_{steam}}
\]

and the teaching partial-pressure estimate is:

\[
P_{HC}=y_{HC}P_{avg}
\]

This allows the software to show directly that more steam lowers hydrocarbon partial pressure while the additional steam also raises total mass flow and heat demand.

## Residence time

The public model calibrates an effective hot-coil volume from the selected operating-case residence-time anchor.

For a given case, total molar flow is estimated from hydrocarbon and steam flow.

The ideal-gas volumetric rate is:

\[
\dot V
=
\frac{\dot nRT_{avg}}
{P_{avg}}
\]

and:

\[
\tau
=
\frac{V_{eff}}
{\dot V}
\]

The pressure-drop estimate changes average coil pressure, so additional steam does not reduce residence time in direct proportion to the increase in molar flow. This reproduces the correct engineering idea that flow, pressure and residence time are coupled.

The model is still a lumped estimate, not a one-dimensional coil simulation.

## Time-temperature severity

Temperature and residence time are the two central variables controlling thermal cracking.

The workbench therefore displays a dimensionless **time-temperature index**:

\[
I_{TT}
=
100
\left(
\frac{\tau}{\tau_{ref}}
\right)
\exp
\left[
\beta(T_{COT}-T_{COT,ref})
\right]
\]

with:

\[
\beta=0.018\;^\circ C^{-1}
\]

The selected public operating case is normalised to:

\[
I_{TT}=100
\]

This is a transparent teaching indicator, not a kinetic model.

It is used to show direction: higher COT increases thermal severity strongly; longer residence time increases severity; reduced feed can increase residence time and therefore severity if COT is not adjusted.

The model does **not** convert this index into a claimed ethane-conversion prediction.

## Conversion

Each public operating case carries a generalised conversion anchor.

The interface labels it as a **case anchor**.

When the user changes COT, feed rate or steam/feed ratio, the workbench does not calculate a new exact conversion. A rigorous conversion prediction would require a validated cracking kinetic mechanism and an axial temperature/pressure/composition solution.

This boundary is intentional.

## Coking

The process source material used to develop this project shows that coking is strongly connected to time-temperature severity, hydrocarbon partial pressure, radiant heat loading, tube-wall condition, run time, dilution steam and local temperature profile.

The public workbench therefore reports only a qualitative **coking-driver state** such as:

- near teaching reference;
- higher coking drivers;
- lower coking drivers.

It does not calculate coke thickness, coke growth rate, tube-metal temperature or remaining run length.

## Low-load behaviour

At reduced throughput residence time increases and COT normally needs to be reduced. At sufficiently low load, dilution steam also needs to increase.

The public model therefore marks feed below 75% of the selected normal teaching load as a low-load range.

This is not presented as a trip or safety limit. It is a model-validity warning.

## What the module supports

The current process layer supports what-if studies such as:

- effect of COT on time-temperature severity;
- effect of coil inlet temperature on sensible versus reaction heat split;
- effect of feed rate on residence time and pressure drop;
- effect of steam/feed ratio on hydrocarbon partial pressure;
- effect of lower load on over-cracking tendency;
- comparison of start-of-run and end-of-run process anchors;
- propagation of combustion and heat-transfer changes into the process side.

## What it does not claim

The module does not predict:

- detailed ethane cracking kinetics;
- product-yield distribution;
- exact conversion away from the case anchor;
- local axial temperature profile;
- local axial pressure profile;
- coke thickness or growth rate;
- tube-metal temperature;
- tube life or creep;
- run-length remaining;
- decoke scheduling;
- safe operating limits.

Those limitations are deliberate.
