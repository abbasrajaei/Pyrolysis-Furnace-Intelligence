# Engineering investigation

Industrial furnace experience → combustion questions → process/control reconstruction → first-principles accounting → conserved firing logic → static scenarios → bounded engineering reasoning.

Industrial operation and commissioning experience motivated this project: furnace decisions involve combustion, heat recovery, process demand and several interacting control functions. A change that looks sensible at one controller may be constrained elsewhere. A temperature error can create a firing request while a pressure override prevents the normal fuel route from acting. Understanding that distinction is an engineering task before it is a software task.

The investigation began by separating physical relationships from control intent. Fuel mass flow and heating value define chemical input. Radiant and convection duties describe where useful heat is accounted for. Burner and zone allocations determine how a fixed total is divided. Process demand and steam demand have related but distinct roles. Draft affects the pressure environment for combustion air, but a pressure reading alone is not an airflow calibration.

The next step was to separate what can be calculated from what must remain unknown. Complete declared compositions support atom balances. Compatible heat duties support energy accounting. Explicit physical shares support conservation. A control narrative, however, does not identify furnace time constants, PID gains, installed valve characteristics or coking rates. Those relationships remain unavailable rather than being filled with plausible-looking coefficients.

The public model therefore uses its own teaching dataset. Every value is identified as a reference, calculation, assumption, synthetic input or unavailable result. The scenarios preserve references while changing explicit requests or functional authority. Zone temperature deviation creates a directional request; a separate teaching redistribution is required to change physical shares. Shutdown examples distinguish a functional state from delivered flow or verified isolation.

A bounded supervisor was added after the engineering and scenario layers. It receives only a verified current snapshot. The validator checks its catalogue statements and evidence against that snapshot, and a deterministic explanation remains available when no provider is configured or a response fails validation. This architecture keeps engineering authority in the deterministic model. It does not demonstrate autonomous operation or unrestricted AI reasoning.

## Why variability matters

Better control can reduce avoidable variation around an operating target. Where variability is a material reason for maintaining conservative operating margin, reducing it may allow operation closer to an appropriate constraint. That can reduce unnecessary firing and associated energy use. Each link is conditional: constraints still apply, actuators must have sufficient authority, measurements must be credible, and the control system must be trusted and maintained.

The public model illustrates those interactions but does not quantify fuel savings, emissions reductions or run-length improvement. It contains no historian training set and no calibrated dynamic response. Decarbonization relevance lies in making energy input, heat allocation, control constraints and missing evidence explicit, so that future investigations ask defensible questions rather than presenting unsupported optimization claims.

## What this portfolio demonstrates

The contribution is an inspectable engineering argument: declare the physical basis, preserve conservation, distinguish request from response, expose assumptions, and prevent a software explanation from exceeding its evidence. The same habits apply to fired heaters and other combustion-intensive processes, while their geometry, reactions, fuel systems and constraints require their own models.
