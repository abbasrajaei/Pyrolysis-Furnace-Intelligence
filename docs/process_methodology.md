# Process and cracking-severity methodology

The Process module connects the combustion and heat-transfer results to the material flowing through the radiant coils. It uses hydrocarbon feed, dilution steam and radiant heat from the connected model, then studies coil inlet temperature, coil outlet temperature (COT), residence time, pressure drop, hydrocarbon partial pressure and a relative time-temperature severity index. The public model is a teaching model. It does not calculate rigorous cracking kinetics, product yields or coke growth.

## Radiant heat split

A pyrolysis coil needs heat for both sensible heating and endothermic cracking. The sensible contribution is estimated as

$$
Q_{\mathrm{sensible}}=\dot{m}_{\mathrm{process}}\,C_p^{\mathrm{eff}}\left(T_{\mathrm{COT}}-T_{\mathrm{in}}\right)
$$

where

$$
\dot{m}_{\mathrm{process}}=\dot{m}_{\mathrm{HC}}+\dot{m}_{\mathrm{steam}}
$$

and the public effective heat capacity is

$$
C_p^{\mathrm{eff}}=3.70\ \mathrm{kJ\,kg^{-1}\,K^{-1}}
$$

This heat capacity is a lumped teaching value for the hot reacting stream. The part of the linked radiant duty not assigned to sensible heating is reported as residual reaction heat:

$$
Q_{\mathrm{reaction,residual}}=Q_{\mathrm{radiant}}-Q_{\mathrm{sensible}}
$$

This is not a rigorous reaction-enthalpy calculation because composition changes continuously through the cracking coil. It is used to show that radiant duty supports both heating and strongly endothermic reactions.

## Coil pressure drop

Each public operating case has a generalised pressure-drop reference. Off-design pressure drop is estimated from

$$
\Delta P=\Delta P_{\mathrm{ref}}
\left(\frac{\dot{m}_{\mathrm{process}}}{\dot{m}_{\mathrm{process,ref}}}\right)^2
\left(\frac{T_{\mathrm{avg}}}{T_{\mathrm{avg,ref}}}\right)
$$

More feed or steam increases process flow and therefore pressure drop. At the same mass flow, a hotter gas has lower density and tends to increase pressure drop. This relation is a first-order teaching estimate, not a detailed compressible-flow or coke-roughness calculation. Start-of-run and end-of-run use separate public anchors.

## Hydrocarbon partial pressure

Dilution steam lowers hydrocarbon partial pressure. The public model uses a generalised ethane-rich hydrocarbon molecular weight:

$$
MW_{\mathrm{HC}}=30.0\ \mathrm{kg\,kmol^{-1}}
$$

The hydrocarbon mole fraction is

$$
y_{\mathrm{HC}}=
\frac{\dot{n}_{\mathrm{HC}}}
{\dot{n}_{\mathrm{HC}}+\dot{n}_{\mathrm{steam}}}
$$

and hydrocarbon partial pressure is estimated from

$$
P_{\mathrm{HC}}=y_{\mathrm{HC}}P_{\mathrm{avg}}
$$

Increasing dilution steam therefore lowers hydrocarbon partial pressure while increasing total process flow and heat demand.

## Residence time

The model calibrates an effective hot-coil volume from the residence-time anchor of the selected public case. Total molar flow is estimated from the hydrocarbon and steam flows. The ideal-gas volumetric rate is

$$
\dot{V}=\frac{\dot{n}RT_{\mathrm{avg}}}{P_{\mathrm{avg}}}
$$

and residence time is

$$
\tau=\frac{V_{\mathrm{eff}}}{\dot{V}}
$$

Pressure drop changes the estimated average coil pressure, so flow, pressure and residence time remain coupled. This is a lumped estimate, not a one-dimensional coil simulation.

## Time-temperature severity

Temperature and residence time are central to thermal cracking. The workbench therefore reports a dimensionless time-temperature index:

$$
I_{\mathrm{TT}}=
100
\left(\frac{\tau}{\tau_{\mathrm{ref}}}\right)
\exp\left[\beta\left(T_{\mathrm{COT}}-T_{\mathrm{COT,ref}}\right)\right]
$$

with

$$
\beta=0.018\ ^\circ\mathrm{C}^{-1}
$$

The selected public operating case is normalised to

$$
I_{\mathrm{TT}}=100
$$

The index shows direction rather than kinetics. Higher COT raises severity strongly, while longer residence time also raises severity. The model does not convert this index into a claimed off-design ethane conversion.

## Conversion, coking and low load

Each public operating case carries a generalised conversion anchor. When COT, feed or steam/feed changes, the software does not calculate a new exact conversion because that would require a validated kinetic mechanism and an axial temperature, pressure and composition solution.

Coking is treated in the same way. The workbench reports whether selected drivers move above or below the teaching reference, but it does not calculate coke thickness, coke growth rate, tube-metal temperature or remaining run length.

Below 75% of the selected normal teaching feed, the interface marks the case as low load. This is a model-validity warning, not a trip or safety limit.

## Model boundary

The Process module supports studies of COT, coil inlet temperature, feed, steam/feed ratio, residence time, pressure drop, hydrocarbon partial pressure and relative severity. It does not claim detailed cracking kinetics, product-yield distribution, local axial temperature or pressure profiles, coke growth, tube life, decoke scheduling or safe operating limits.
