from copy import deepcopy
from .grounding import grounding_pack
from .supervisor_validation import validate
from .explanations import explain
class CatalogueDemo:
    """Deterministic contract demonstration; this is not an AI reasoning model."""
    def assess(self,pack):
        return {k:deepcopy(pack[k]) for k in ('state_digest','operating_state','active_authority','evidence','limitations')} | {
          'claims':deepcopy(pack['approved_claims']),'recommendations':pack['approved_recommendations'][:1],
          'provenance':'AI_REASONED','confidence':'BOUNDED_ONLY'}
def assess(state,provider=None):
    pack=grounding_pack(state)
    fallback={'status':'DETERMINISTIC_FALLBACK','explanation':explain(state)}
    if provider is None:return fallback|{'reason':'No AI provider configured.'}
    try:raw=provider.assess(deepcopy(pack))
    except Exception:return fallback|{'reason':'Provider failed.'}
    result=validate(raw,pack)
    if not result['accepted']:return fallback|{'reason':'Assessment rejected.','validation':result}
    return {'status':'ACCEPTED','assessment':raw,'validation':result,'provider_label':'DETERMINISTIC_CONTRACT_DEMO' if isinstance(provider,CatalogueDemo) else 'OPTIONAL_PROVIDER'}
