# Model boundaries

Pyrolysis Furnace Intelligence is an independently authored educational engineering workbench. Numerical operating cases are synthetic or use rounded general property references; they do not reproduce an operating facility.

## Supported

- Complete combustion stoichiometry for declared H2, CH4, C2H6 and inert N2 mixtures.
- Automatic fuel-composition closure by proportional renormalization of unlocked components.
- Mass LHV, ideal declared-normal-volume LHV and lower-Wobbe teaching calculations.
- Stoichiometric/actual dry-air demand and wet/dry ideal product oxygen fractions.
- Static conserved heat accounting using chemical input, useful heat recovery and radiant/convection partition.
- Conservation of total firing across six illustrative inlet zones and outlet bottom/sidewall branches.
- Synthetic per-burner loading arithmetic under explicit equal-loading assumptions.
- Steam base-demand calculation from feed and steam/feed ratio.
- Simplified functional pressure-constraint authority states.
- One-factor sensitivity sweeps for supported input/output relationships.
- A fixed-resistance draft teaching correlation in which relative airflow scales with the square root of draft magnitude.
- Thirteen static teaching scenarios, baseline/current case comparison and deterministic context-sensitive engineering guidance.
- Bounded supervisor architecture that cannot change engineering state or issue operating commands.

## Not claimed

CFD; local flame shape or flame temperature; flame-speed prediction; flashback limits; CO or NOx prediction; rigorous cracking yields; quantitative coking kinetics; tube-life prediction; current tube-metal temperature; local heat-flux prediction; plant-calibrated dynamics; identified PID tuning; calibrated valve response; calibrated fan curve; burner-register position; plant leakage-air coefficients; plant trip/permissive logic; safe-to-continue assessment; APC/BMS replacement; plant-validated optimization; autonomous AI control.

The dashboard's sensitivity curves are one-factor engineering studies, not time trends. The current point and baseline show where the selected case lies on a supported relationship; they do not imply a transient trajectory.

## Draft correlation

The optional draft sensitivity uses a deliberately simple fixed-effective-resistance relation:

\[
Q_{air,rel}=\sqrt{\frac{|P_{draft}|}{|P_{draft,ref}|}}
\]

and an implied excess-air fraction derived from the selected current excess-air basis. This is a **MODEL / ASSUMPTION** for teaching sensitivity only. Real furnace air admission also depends on burner/register position, density, duct and burner resistance, leakage paths and fan operating point. Therefore the curve is not a plant airflow calibration and is not used to claim a safe or optimal draft.

## Heat-transfer boundary

The thermal workbench uses a static accounting partition. Changing chemical duty, heat recovery or radiant share does not calculate a new COT, tube-metal temperature, local radiant flux, stack temperature or cracking conversion. Those require additional physical relationships or calibrated data.

## Control boundary

Pressure states alter functional authority only. They do not predict valve position, controller output, trip action or recovery time. Zone temperature logic may produce a directional request, but the numerical zone-correction control in the workbench is an explicit user-supplied teaching redistribution; it is not a PID-generated response.

## AI and guidance boundary

The persistent Engineering Guidance panel is deterministic. It explains calculated consequences, qualitative physical implications, variables to watch and unavailable relationships. Qualitative statements do not become numerical predictions. The bounded supervisor accepts only a closed catalogue with unchanged engine evidence; its deterministic demonstration is not a language model.
