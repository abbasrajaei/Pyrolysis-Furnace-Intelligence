# Technical methodology

All numerical examples use the public teaching dataset. SI units are used except explicitly labelled normal-volume quantities. Model functions do not read any external engineering evidence.

## Fuel and combustion

For a declared mole-fraction mixture, mole fractions must sum to one. Unsupported species, negative fractions and incomplete compositions are rejected; missing components are not silently normalized.

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

\[
 Q_{useful}=Q_r+Q_c,\quad Q_{residual}=Q_f-Q_r-Q_c,\qquad
 _eta=\frac{Q_r+Q_c}{Q_f}
\]

Note: the absolute symbol above is intended as the Greek eta (efficiency).

The synthetic example uses 60 MW chemical input, 27 MW radiant and 28 MW convection duty. It gives 5 MW residual and 91.67% accounting efficiency. The residual is not independently identified as wall loss or stack loss. Negative residuals remain visible; zero firing makes efficiency unavailable. Different case labels cannot be mixed silently. There is no off-design radiation or convection model.

## Firing allocation

The inlet/outlet ratio a and outlet bottom/sidewall ratio b are defined as physical duty ratios:

\[
 Q_o=Q_f/(1+a),\qquad Q_i=Q_f-Q_o,\quad
 Q_{os}=Q_o/(1+b),\quad Q_{ob}=Q_o-Q_{os}
\]

Six inlet shares f sum to one; zone j receives Q_i f_j. A separately supplied teaching increment delta to one zone is removed equally from the other five zones. The proposed update is rejected as a whole if any share falls outside [0,1]. No clipping or hidden normalization is used. The sum of six zone duties plus outlet bottom and sidewall duty must equal total duty within numerical tolerance.

Synthetic burner counts and equal loading permit illustrative per-burner duty arithmetic. All inlet duty is assigned to bottom burners for this specific teaching assumption. The diagram is not a burner-location or coil-layout specification.

## Temperature selection and process demand

The illustrative sensor hierarchy selects the second-highest of four sensors for each of six zones, then the second-highest of those six selected values. It is not a single global second-highest across all sensors. Tied ranks count separately. Missing sensors make the affected zone and overall result unavailable; no degraded voting is invented.

Zone request direction follows target + bias − selected proxy. It does not generate a numerical firing increment. A bias changes the target, not the measurement. No PID, recovery time or temperature-to-firing process gain is implemented.

Steam base demand is max(actual feed, requested feed) times declared steam/feed ratio. It is distinct from delivered steam and has no rate-limited temporal realization. Pass balance uses explicit output proxies; a proxy classification is not measured pass duty or a numerical feed-bias controller.

## Draft and excess-air interpretation

An induced-draft fan establishes a pressure field that draws air through burner openings and leakage paths. Air admission also depends on register position and flow resistance. A more negative pressure can increase unwanted leakage; oxygen measured downstream can therefore include air that did not participate at the burner. Excess air increases flue-gas quantity in the declared combustion calculation, but this model does not calculate the resulting stack loss, fan power or flame shape. The declared draft value is an illustrative input, not a calibrated airflow or efficiency predictor.

## Control and scenarios

Three educational states and explicit pressure constraints select functional authority. Total and partial shutdown teaching states select their respective generic authorities and withhold numerical allocation. Concurrent low/high constraints, or undefined manual/constraint arbitration, return UNAVAILABLE. These policies are independently simplified teaching rules, not a recovered installed sequence.

Thirteen named scenarios alter declared inputs or functional interpretation. Before/after comparisons are independent static evaluations, not samples from a time integration. Fuel-property change and the high-LHV scenario intentionally share one teaching fuel; they are different teaching entry points, not independent physical benchmarks. The pressure scenario uses the low-pressure constraint; the public tests separately exercise both pressure directions.

## Provenance and unavailable behavior

REFERENCE identifies general rounded property inputs. SYNTHETIC identifies teaching conditions. ASSUMPTION identifies explicit modeling conventions. CALCULATED results retain dependency categories and an equation/basis description. UNAVAILABLE always has a null value and a reason. Dependency categories do not constitute a full sensitivity analysis. Pure scalar allocation helpers are mathematical utilities; the scenario layer supplies their public context and assumptions.

## Supervisor architecture

The grounding builder recomputes the named scenario and requires exact equality with the supplied snapshot. It then creates evidence IDs, a state digest, limitations and an approved explanation catalogue. A provider receives a copy, so it cannot mutate the authoritative pack. Structured output must match state, authority, evidence, limitations and all approved claims; recommendations must come from the approved list. No free-form numerical plant claim or actuator command is accepted.

No provider, a provider exception or rejected output produces the deterministic explanation. The bundled CatalogueDemo is deterministic contract scaffolding, not AI inference. The provider-neutral Python protocol allows an optional implementation without making any external provider a runtime dependency. External endpoint compatibility, unrestricted reasoning and plant validation are outside this release.
