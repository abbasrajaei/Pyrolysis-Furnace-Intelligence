# Model boundaries

Pyrolysis Furnace Intelligence is an educational engineering workbench. Public operating cases are synthetic or generalised and do not reproduce an operating facility.

## Supported calculations

### Combustion

The combustion layer supports complete-combustion stoichiometry for declared $H_2$, $CH_4$, $C_2H_4$, $C_2H_6$, $C_3H_8$, $CO$, $CO_2$ and $N_2$ mixtures. It closes fuel composition with a selected balance component and calculates molecular weight, mass and volumetric LHV, lower Wobbe Index, stoichiometric oxygen and air, humid-air correction, wet and dry flue-gas composition, fuel demand, public process-load firing, bottom/sidewall firing allocation and one-factor response studies.

Fuel-composition studies can hold fired duty, fuel mass flow or burner pressure difference constant. The burner-pressure study uses the declared Wobbe approximation; it is not a calibrated burner-flow map.

### Heat transfer

The thermal layer closes the lumped furnace balance

$$
Q_{\mathrm{fired}}=
Q_{\mathrm{radiant}}+
Q_{\mathrm{convection}}+
Q_{\mathrm{stack}}+
Q_{\mathrm{other}}
$$

It calculates stack sensible-heat loss, other heat loss, useful heat, overall and box efficiency, radiant and convection duty, average and peak teaching heat flux, public convection-bank heat distribution and one-factor thermal response studies. It uses the current combustion result, so feed, excess air and fuel composition can change the thermal calculation.

### Process

The Process layer uses the connected feed, steam and radiant-heat state to estimate sensible heat, residual reaction heat, coil pressure drop, hydrocarbon partial pressure, residence time and a relative time-temperature severity index. Conversion remains a case anchor rather than an off-design kinetic prediction. Coking is reported only as a directional driver state.

### Retained teaching modules

The repository also contains simplified educational modules for firing allocation, steam demand, pressure-authority states, static scenarios, deterministic engineering guidance and a bounded supervisor contract. These modules cannot change engineering state or issue operating commands.

## Not claimed

The public workbench does not claim CFD velocity or temperature fields, detailed flame shape or flame temperature, flame-speed or flashback prediction, CO or NOx prediction, rigorous cracking yields, quantitative coke growth, local tube heat flux, current tube-metal temperature, tube life, detailed view factors, composition-dependent flue-gas enthalpy from a property package, plant-calibrated fan/register/leakage behaviour, plant-calibrated dynamics, identified PID tuning, valve trajectories, trip or permissive logic, safe-to-continue decisions, APC/BMS replacement, plant-validated optimisation or autonomous AI control.

The response plots are engineering parameter studies, not time trends. Before and Now show two calculated states and do not imply a transient trajectory.

## Thermal boundary

The thermal model uses declared public assumptions for effective flue-gas heat capacity, radiant area, peak-to-average flux ratio, other-loss fraction and convection-bank shares. Changing radiant share redistributes useful heat between radiant and convection sections; it does not predict how a real flame would produce that split.

A defensible tube-metal-temperature calculation would require local heat flux, local process-fluid temperature, process-side heat-transfer coefficients, tube conductivity, coke thickness and conductivity, and local radiation information. These inputs are outside the public model.

## Draft boundary

A retained legacy teaching sensitivity uses a fixed-effective-resistance relation:

$$
Q_{\mathrm{air,rel}}=
\sqrt{
\frac{|P_{\mathrm{draft}}|}
{|P_{\mathrm{draft,ref}}|}
}
$$

This is a teaching assumption only. Real furnace air admission also depends on burner/register position, density, duct and burner resistance, leakage paths and fan operating point. The current combustion workbench therefore does not use draft as a plant-calibrated airflow input.

## Control and guidance boundary

Pressure states in the retained control teaching engine change functional authority only. They do not predict valve position, controller output, trip action or recovery time. Deterministic guidance explains supported calculated consequences and model limits. The bounded supervisor uses a closed evidence catalogue and cannot issue operating commands.
