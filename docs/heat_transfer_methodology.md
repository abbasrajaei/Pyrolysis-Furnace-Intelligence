# Heat-transfer and thermal-efficiency methodology

The Heat Transfer module connects the current combustion result to a lumped furnace energy balance. It follows fired duty and flue-gas flow into radiant absorption, convection recovery, stack loss and overall efficiency. The model is intended for engineering what-if studies. It is not CFD and does not calculate local flame radiation, tube-metal temperature or coking rate.

## Furnace energy balance

The model closes the heat balance as

$$
Q_{\mathrm{fired}}=
Q_{\mathrm{radiant}}+
Q_{\mathrm{convection}}+
Q_{\mathrm{stack}}+
Q_{\mathrm{other}}
$$

Stack sensible-heat loss is calculated from

$$
Q_{\mathrm{stack}}=
\frac{\dot{m}_{\mathrm{fg}}\,C_{p,\mathrm{fg}}^{\mathrm{eff}}
\left(T_{\mathrm{stack}}-T_{\mathrm{ambient}}\right)}
{3.6\times10^6}
$$

with $\dot{m}_{\mathrm{fg}}$ in kg/h, $C_{p,\mathrm{fg}}^{\mathrm{eff}}$ in kJ/(kg·K) and $Q_{\mathrm{stack}}$ in MW. The public effective flue-gas heat capacity is

$$
C_{p,\mathrm{fg}}^{\mathrm{eff}}=1.34\ \mathrm{kJ\,kg^{-1}\,K^{-1}}
$$

This is a source-informed lumped value, not a composition-dependent property package.

Other heat loss is represented as a declared fraction of fired duty:

$$
Q_{\mathrm{other}}=f_{\mathrm{loss}}Q_{\mathrm{fired}}
$$

The public default is 1% of fired duty. Keeping this term separate from stack loss makes the effect of excess air and stack temperature visible.

Useful heat and overall efficiency are then

$$
Q_{\mathrm{useful}}=
Q_{\mathrm{fired}}-Q_{\mathrm{stack}}-Q_{\mathrm{other}}
$$

$$
\eta_{\mathrm{overall}}=
\frac{Q_{\mathrm{useful}}}{Q_{\mathrm{fired}}}
$$

## Radiant and convection split

The public model uses a declared radiant share of fired duty:

$$
Q_{\mathrm{radiant}}=f_{\mathrm{radiant}}Q_{\mathrm{fired}}
$$

The remaining useful heat is assigned to convection:

$$
Q_{\mathrm{convection}}=Q_{\mathrm{useful}}-Q_{\mathrm{radiant}}
$$

The radiant share is a study assumption, not a direct plant actuator. Box efficiency is

$$
\eta_{\mathrm{box}}=
\frac{Q_{\mathrm{radiant}}}{Q_{\mathrm{fired}}}
$$

## Radiant heat flux

Average teaching heat flux is calculated from

$$
q''_{\mathrm{avg}}=
\frac{Q_{\mathrm{radiant}}}{A_{\mathrm{radiant}}}
$$

using the public effective radiant area

$$
A_{\mathrm{radiant}}=420\ \mathrm{m^2}
$$

Peak teaching heat flux is estimated as

$$
q''_{\mathrm{peak}}=1.14\,q''_{\mathrm{avg}}
$$

These values show heat-loading sensitivity. They are not local burner-to-tube or tube-by-tube heat-flux predictions.

## Convection recovery

The public model distributes total convection duty across six service groups: HTC-II 26%, HPSSH-II 15%, HPSSH-I 16%, HTC-I 22%, ECO 12% and FPH 9%. The shares sum to 100% and preserve the multi-service convection-section concept without reproducing proprietary bank geometry or vendor rating calculations.

## Coupling with combustion

The Heat Transfer module uses the current combustion state. At fixed stack temperature, increasing excess air increases flue-gas flow and therefore stack loss:

$$
EA\uparrow
\;\Rightarrow\;
\dot{m}_{\mathrm{fg}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{stack}}\uparrow
\;\Rightarrow\;
\eta_{\mathrm{overall}}\downarrow
$$

Increasing stack temperature has the same first-order effect on stack loss:

$$
T_{\mathrm{stack}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{stack}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{useful}}\downarrow
\;\Rightarrow\;
\eta_{\mathrm{overall}}\downarrow
$$

At the same heat split and geometry, higher process load increases required firing, radiant duty and average heat flux:

$$
\dot{m}_{\mathrm{feed}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{fired}}\uparrow
\;\Rightarrow\;
Q_{\mathrm{radiant}}\uparrow
\;\Rightarrow\;
q''_{\mathrm{avg}}\uparrow
$$

Fuel composition can change flue-gas flow and therefore stack loss. The public thermal model uses one effective flue-gas heat capacity, so it captures this first-order mass-flow effect without claiming a full composition-dependent enthalpy calculation.

## Model boundary

A defensible tube-metal-temperature model would need local heat flux, tube geometry, process-side heat-transfer coefficients, tube conductivity, coke thickness and conductivity, local fluid temperature and the local radiation field. Those inputs are not available in the public model, so the workbench stops at heat loading. It does not claim CFD fields, local view factors, local tube heat flux, tube-metal temperature, detailed convection coefficients, fouling resistance, coking rate, tube life or plant-specific stack-loss guarantees.
