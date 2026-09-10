# Bounded AI Engineering Supervisor

The engine owns state. The supervisor can explain that state but cannot change it.

The data path is verified static scenario → grounding pack → optional provider → exact validator → accepted catalogue assessment or deterministic fallback. Grounding includes only the current scenario, public teaching values, generic evidence IDs, public assumptions and unavailable reasons. Evidence IDs are scoped to their pack. A state digest is derived only from public state.

The provider interface is `SupervisorProvider.assess(pack) -> dict`. The required fields and instructions are in `supervisor_prompts.py`. An assessment carries state digest, operating state, active authority, claims, evidence, limitations, recommendations, provenance and confidence. The validator requires exact engine evidence and approved claims. The provider cannot add free-form plant claims or new numerical values. AI_REASONED labels the explanation channel, not a new engineering measurement; the engineering data retain their own public provenance.

The default application has no configured AI provider and shows deterministic explanations. A labelled deterministic contract demo is available for inspecting the interface. It must not be presented as a model reasoning result. To integrate a provider programmatically, implement the protocol and pass an instance to `assess(state, provider)`. Credentials, transport, model selection and endpoint translation are outside this repository. No vendor adapter or live AI service is required or tested.

Missing providers, exceptions, malformed schemas, changed numerical evidence, changed authority, omitted limitations, unsupported claims and unauthorized recommendations lead to fallback. Stale or modified engine snapshots fail grounding rather than being treated as valid input. No runtime command in this project writes to a controller.

The closed catalogue deliberately limits expressive freedom. Contract acceptance is not proof of unrestricted reasoning, model intelligence, safe operation or an optimization benefit. No previous internal benchmark artifacts or results are part of this public release's validation claims.
