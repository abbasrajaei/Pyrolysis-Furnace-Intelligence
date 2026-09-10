# Technical methodology

All numerical examples use the public teaching dataset. SI units are used except explicitly labelled normal-volume quantities. Model functions do not read any external engineering evidence.

## Fuel and combustion

For a declared mole-fraction mixture, mole fractions must sum to one. The engineering engine rejects incomplete or invalid compositions. The **workbench interface** adds a convenience layer: when the user changes one selected component, all unlocked remaining components are renormalized proportionally so the total remains exactly one. Locked components retain their values. This automatic closure is an interface rule, not a new combustion model.

For one mole of mixture with elemental totals C, H, O and N:

\[
\nu_{O_2,st}=C+H/4-O/2
\]

The dry-air assumption is one mole O2 plus 3.76 mol N2. With declared excess-air fraction e ≥ 0:

\[
n_{air,st}=4.76\nu_{O_2,st},\qquad
n_{air}=n_{air,st}(1+e)
\]

Products are C mol CO2, H/2 mol H2O, eν mol O2 and N/2 + 3.76(1+e)ν mol N2. Wet and dry oxygen use their respective product totals. The model checks C/H/O/N atom residuals. It excludes oxygen-deficient reactions, dissociation, humidity, argon, soot and NOx. Dry oxygen is not interpreted as a direct diagnosis of burner excess air when leakage might exist in a real furnace.

Rounded component molecular masses and lower heating values provide an explicitly pedagogical property basis. Water is vapor in the LHV convention. For mole fractions x:

\[
M_f=\sum_i x_iM_i,\qquad
LHV_m=\frac{\sum_i x_iM_iLHV_i}{M_f},\qquad
\dot m_f=Q_f/LHV_m
\]

Equivalent fuel demand is a fixed chemical-duty calculation; it does not assert equal heat transfer, constant outlet temperature or a measured fuel-flow response.

The declared normal state is 273.15 K and 100000 Pa absolute, with ideal-gas compressibility. Molar density is P/(RT). Lower volumetric heating value is molar density times molar LHV, and:

\[
WI_L=\frac{LHV_V}{\sqrt{M_f/M_{air}}}
\]

This explicit convention prevents ambiguity between mass LHV and normal-volume Wobbe. It is not an installed burner/valve map. The property references are rounded teaching values, not a precision thermophysical database or an uncertainty-qualified property correlation.

## Static heat accounting

The workbench replaces two independent heat-share sliders with a more robust pair of inputs:

- **useful heat recovery**, η;
- **radiant share of useful heat**, r.

Then:

\[
Q_{useful}=\eta Q_f
\]

\[
Q_r=rQ_{useful},\qquad
Q_c=(1-r)Q_{useful}
\]

\[
Q_{residual}=Q_f-Q_r-Q_c
\]

This guarantees a physically consistent static accounting partition for valid inputs 0 ≤ η ≤ 1 and 0 ≤ r ≤ 1.

The baseline teaching case uses 60 MW chemical input, 55/60 useful heat recovery and 27/55 radiant share, reproducing 27 MW radiant duty, 28 MW convection duty and 5 MW residual. The residual is not independently identified as wall loss or stack loss. There is no off-design radiation or convection model.

## Firing allocation

The inlet/outlet ratio a and outlet bottom/sidewall ratio b are defined as physical duty ratios:

\[
Q_o=Q_f/(1+a),\qquad Q_i=Q_f-Q_o
\]

\[
Q_{os}=Q_o/(1+b),\qquad Q_{ob}=Q_o-Q_{os}
\]

Six inlet shares f sum to one; zone j receives Q_i f_j. A separately supplied teaching increment δ to one selected zone is removed equally from the other five zones. The proposed update is rejected as a whole if any share falls outside [0,1]. No clipping or hidden normalization is used. The sum of six zone duties plus outlet bottom and sidewall duty must equal total duty within numerical tolerance.

Synthetic burner counts and equal loading permit illustrative per-burner duty arithmetic. These values are teaching arithmetic, not installed burner limits.

## Temperature selection and process demand

The bounded scenario engine retains an illustrative sensor hierarchy that selects the second-highest of four sensors for each of six zones, then the second-highest of those six selected values. It is not a single global second-highest across all sensors. Tied ranks count separately. Missing sensors make the affected zone and overall result unavailable; no degraded voting is invented.

Zone request direction follows target + bias − selected proxy. It does not generate a numerical firing increment. A bias changes the target, not the measurement. No PID, recovery time or temperature-to-firing process gain is implemented.

Steam base demand is max(actual feed, requested feed) times declared steam/feed ratio. In the interactive workbench, the current feed is used as the selected feed basis. The result is not a delivered-flow prediction and has no temporal realization.

## Draft and excess-air interpretation

An induced-draft fan establishes a pressure field that helps move combustion air and flue gas through system resistance. Real air admission also depends on burner/register position, density, leakage paths and fan operating point. Therefore draft alone is not a plant airflow calibration.

For educational sensitivity only, version 2.0 introduces an optional **fixed-effective-resistance teaching correlation**:

\[
Q_{air,rel}=\sqrt{\frac{|P_{draft}|}{|P_{draft,ref}|}}
\]

with a reference draft of -40 Pa(g) in the synthetic workbench case.

An implied excess-air fraction can then be formed relative to the selected current excess-air basis:

\[
e_{implied}=(1+e_{base})Q_{air,rel}-1
\]

This relation is explicitly labelled **MODEL / ASSUMPTION**. It is useful for exploring the direction and nonlinearity of a square-root pressure/flow relation, not for predicting plant air flow, stack O2, fan power, leakage or safe draft.

## Sensitivity engine

Each sensitivity curve varies one supported independent input over a declared range while holding the other current-case inputs fixed. The curve therefore answers:

> What would the model calculate for Y if X were changed, with this current case as the basis?

The orange point is the current case and the grey point is the retained baseline. These curves are **not time histories**.

Supported sweeps include fuel-component fraction, excess air, chemical duty, heat recovery, radiant share, inlet/outlet firing ratio, bottom/side ratio, feed rate, steam/feed ratio, explicit zone correction and draft pressure. Output choices are limited to relationships implemented by the public model.

Fuel-component sweeps automatically renormalize the other composition components. Zone-correction sweeps remain explicit user-supplied redistribution, not a PID output. Draft sweeps remain labelled model assumptions.

## Engineering Guidance

The persistent guidance rail is deterministic. It reacts to the most recently changed parameter and returns five kinds of information:

1. what changed;
2. why the parameter matters physically;
3. immediate calculated or qualitative consequences;
4. variables an engineer would normally watch;
5. model basis and unavailable conclusions.

The panel may mention qualitative combustion effects such as flame-speed or flashback implications, but it does not convert those statements into numerical predictions. Guidance never changes model state and never issues operating commands.

## Control and scenarios

Three educational states and explicit pressure constraints select functional authority. Total and partial shutdown teaching states select their respective generic authorities and withhold numerical allocation. Concurrent low/high constraints, or undefined manual/constraint arbitration, return UNAVAILABLE. These policies are independently simplified teaching rules, not a recovered installed sequence.

Thirteen named scenarios alter declared inputs or functional interpretation. Before/after comparisons are independent static evaluations, not samples from a time integration.

## Provenance and unavailable behavior

REFERENCE identifies general rounded property inputs. SYNTHETIC identifies teaching conditions. ASSUMPTION identifies explicit modeling conventions. CALCULATED results retain dependency categories and an equation/basis description. UNAVAILABLE always has a null value and a reason. Dependency categories do not constitute a full uncertainty analysis.

## Supervisor architecture

The bounded supervisor remains separate from the deterministic Engineering Guidance panel. The grounding builder recomputes the named scenario and requires exact equality with the supplied snapshot. It then creates evidence IDs, a state digest, limitations and an approved explanation catalogue. Structured provider output must match state, authority, evidence, limitations and approved claims; unsupported numerical plant claims or actuator commands are rejected.

No provider, provider exception or rejected output produces the deterministic fallback. The bundled CatalogueDemo is deterministic contract scaffolding, not AI inference. External endpoint compatibility, unrestricted reasoning and plant validation are outside this release.
