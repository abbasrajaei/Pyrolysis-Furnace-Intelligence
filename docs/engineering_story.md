# Engineering investigation

Industrial furnace experience → combustion questions → first-principles fuel/air accounting → furnace heat balance → conserved firing logic → control reasoning.

Industrial operation and commissioning experience motivated this project: furnace decisions involve combustion, heat recovery, process demand and several interacting control functions. A change that looks sensible at one controller may be constrained elsewhere. A temperature error can create a firing request while a pressure override prevents the normal fuel route from acting. Understanding that distinction is an engineering task before it is a software task.

The investigation began by separating physical relationships from control intent. Fuel composition sets molecular weight, heating value, Wobbe Index and oxygen demand. Feed and steam establish a first process-load estimate. Fired duty then drives fuel and air demand. The current thermal layer closes the furnace heat balance into radiant absorption, convection recovery, stack sensible-heat loss and other loss. Burner allocation determines where firing is distributed. Draft affects the pressure environment for combustion air, but a pressure reading alone is not an airflow calibration.

The next step was to separate what can be calculated from what must remain unknown. Complete declared compositions support atom balances. Compatible heat duties support energy accounting. Explicit physical shares support conservation. A control narrative, however, does not identify furnace time constants, PID gains, installed valve characteristics or coking rates. Those relationships remain unavailable rather than being filled with plausible-looking coefficients.

The public model therefore uses its own teaching dataset. Every value is identified as a reference, calculation, assumption, synthetic input or unavailable result. The scenarios preserve references while changing explicit requests or functional authority. Zone temperature deviation creates a directional request; a separate teaching redistribution is required to change physical shares. Shutdown examples distinguish a functional state from delivered flow or verified isolation.

A bounded supervisor was added after the engineering and scenario layers. It receives only a verified current snapshot. The validator checks its catalogue statements and evidence against that snapshot, and a deterministic explanation remains available when no provider is configured or a response fails validation. This architecture keeps engineering authority in the deterministic model. It does not demonstrate autonomous operation or unrestricted AI reasoning.

## Why variability matters

Better control can reduce avoidable variation around an operating target. Where variability is a material reason for maintaining conservative operating margin, reducing it may allow operation closer to an appropriate constraint. That can reduce unnecessary firing and associated energy use. Each link is conditional: constraints still apply, actuators must have sufficient authority, measurements must be credible, and the control system must be trusted and maintained.

The public model illustrates those interactions but does not quantify fuel savings, emissions reductions or run-length improvement. It contains no historian training set and no calibrated dynamic response. Decarbonization relevance lies in making energy input, heat allocation, control constraints and missing evidence explicit, so that future investigations ask defensible questions rather than presenting unsupported optimization claims.

## What this portfolio demonstrates

The contribution is an inspectable engineering argument: declare the physical basis, preserve conservation, distinguish request from response, expose assumptions, and prevent a software explanation from exceeding its evidence. The same habits apply to fired heaters and other combustion-intensive processes, while their geometry, reactions, fuel systems and constraints require their own models.


## Workbench 2.0

The second public interface was redesigned around an engineering-study workflow rather than a collection of sliders and static charts. A retained baseline, intelligent linked fuel composition, ready-made presets, sensitivity curves, saved-case comparison and a persistent Engineering Guidance rail make the model usable as an investigation tool. The guidance rail reacts to the parameter being changed and separates calculated consequences from qualitative physical implications and unsupported predictions. The numerical engine remains bounded by the same evidence policy: interface quality does not justify additional plant physics.


## Workbench 2.1

Version 2.1 adds a connected Heat Transfer module rather than treating heat accounting as an isolated residual. The current combustion result supplies fired duty and flue-gas flow to the thermal layer. Stack temperature and excess air therefore influence calculated stack sensible-heat loss, while radiant share determines the public radiant/convection split. The interface shows overall efficiency, box efficiency, radiant and convection duty, average/peak teaching heat flux and convection-bank recovery in the same Before → Now investigation style used by the combustion module.

The thermal model deliberately stops before tube-metal temperature and coking-rate prediction. Those quantities require local heat flux, process-side heat-transfer coefficients, coke resistance and local temperature information that the public model does not possess.
