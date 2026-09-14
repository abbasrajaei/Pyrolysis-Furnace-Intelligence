# Model boundaries

Pyrolysis Furnace Intelligence is an independently authored educational engineering workbench. Public numerical operating cases are synthetic or generalised and do not reproduce an operating facility.

## Supported

### Combustion

- Complete-combustion stoichiometry for declared H2, CH4, C2H4, C2H6, C3H8, CO, CO2 and N2 fuel mixtures.
- Automatic fuel-composition closure using a selected balance component.
- Mixture molecular weight, mass LHV, normal-volume LHV, specific gravity and lower Wobbe Index.
- Stoichiometric oxygen and air demand.
- Humid-air correction for the public ambient condition.
- Wet and dry ideal flue-gas composition.
- Fuel flow required for a declared fired duty.
- Fuel studies at constant fired duty, constant fuel mass flow, or constant burner pressure difference using the declared Wobbe approximation.
- Public start-of-run/end-of-run process-load teaching states.
- A source-informed feed plus dilution-steam load index for estimating required firing.
- Low-load warnings when normal load scaling is outside its intended range.
- Bottom/sidewall firing allocation and public teaching burner-loading checks.
- One-factor square-point response studies for supported combustion relationships.

### Heat transfer and thermal efficiency

- A closed lumped furnace energy balance:

$
Q_{fired}
=
Q_{radiant}
+
Q_{convection}
+
Q_{stack}
+
Q_{other}
$

- Stack sensible-heat loss from flue-gas mass flow, a declared effective heat capacity and stack-to-ambient temperature difference.
- Other heat loss as a declared fraction of fired duty.
- Overall useful-heat efficiency.
- Radiant duty from a declared public radiant share.
- Convection recovery as the remaining useful heat after radiant absorption.
- Box efficiency, defined as radiant heat absorbed divided by fired duty.
- Average radiant heat flux from radiant duty and a public effective radiant area.
- Peak teaching heat flux from a declared peak-to-average factor.
- Public convection-duty distribution across HTC-II, HPSSH-II, HPSSH-I, HTC-I, ECO and FPH groups.
- Coupling from the current combustion result into the thermal calculation, including feed, excess-air and fuel-composition effects on stack loss.
- One-factor square-point thermal response studies.

### Other retained educational capabilities

- Conserved firing allocation across illustrative firing branches and zones.
- Steam base-demand calculation from feed and steam/feed ratio.
- Simplified functional pressure-constraint authority states.
- Static teaching scenarios and deterministic context-sensitive engineering guidance.
- A bounded supervisor architecture that cannot change engineering state or issue operating commands.

## Not claimed

The public workbench does not claim to provide:

- CFD velocity, mixing or temperature fields;
- detailed flame shape or flame temperature;
- flame-speed prediction;
- flashback limits;
- CO or NOx prediction;
- rigorous cracking yields or reaction kinetics;
- quantitative coking kinetics;
- local tube heat flux;
- current tube-metal temperature;
- tube-life prediction;
- detailed view factors or burner-to-tube radiation;
- composition-dependent flue-gas enthalpy from a property package;
- detailed convection coefficients;
- plant-calibrated fan, burner-register or leakage-air behaviour;
- plant-calibrated dynamic response;
- identified PID tuning or valve response;
- plant trip/permissive logic;
- safe-to-continue assessment;
- APC/BMS replacement;
- plant-validated optimisation;
- autonomous AI control.

The response graphs are engineering parameter studies, not time trends. The **Before** and **Now** squares show where two states lie on a supported relationship; they do not imply a transient trajectory.

## Heat-transfer boundary

The thermal layer is a lumped engineering balance. The effective flue-gas heat capacity, radiant area, peak/average flux ratio, other-loss fraction and public convection-bank shares are declared public modelling assumptions or source-informed teaching values.

A change in radiant share redistributes useful heat between radiant and convection sections; it does not claim to predict how a real burner or flame would produce that redistribution.

Average and peak teaching heat flux are calculated from the public effective area. They are not local tube-by-tube heat-flux predictions.

The source material makes the physical importance of tube-metal temperature and coking clear, but the available public basis does not support a defensible off-design tube-metal-temperature model. Local heat flux, process-side heat-transfer coefficients, coke thickness/conductivity and local fluid temperature would be required before that calculation should be added.

See docs/heat_transfer_methodology.md for the thermal equations and assumptions.

## Draft boundary

A retained optional draft sensitivity in the legacy teaching engine uses a deliberately simple fixed-effective-resistance relation:

$
Q_{air,rel}
=
\sqrt{
\frac{|P_{draft}|}
{|P_{draft,ref}|}
}
$

This is a **MODEL / ASSUMPTION** for teaching sensitivity only. Real furnace air admission also depends on burner/register position, density, duct and burner resistance, leakage paths and fan operating point. The current combustion cockpit therefore does not use this relation as a plant air-flow calibration.

## Control boundary

Pressure states in the retained control teaching engine alter functional authority only. They do not predict valve position, controller output, trip action or recovery time. Zone-temperature logic may produce a directional request, but numerical redistribution remains an explicit teaching calculation rather than a PID-generated plant response.

## AI and guidance boundary

Deterministic engineering guidance explains calculated consequences, qualitative physical implications, variables to watch and unavailable relationships. Qualitative statements do not become numerical predictions. The bounded supervisor accepts only a closed evidence catalogue and cannot issue operating commands.
