import json
from .grounding import canonical
FIELDS={'state_digest','operating_state','active_authority','claims','evidence','limitations','recommendations','provenance','confidence'}
def validate(raw,pack):
    errors=[]
    try:
        if type(raw)!=dict or set(raw)!=FIELDS:raise ValueError('Exact schema required')
        canonical(raw)
        for k in ('state_digest','operating_state','active_authority'):
            if raw[k]!=pack[k]:errors.append(k+' contradicts current engine state')
        for k,source in [('claims','approved_claims'),('evidence','evidence'),('limitations','limitations')]:
            if canonical(raw[k])!=canonical(pack[source]):errors.append(k+' differs from grounded catalogue')
        recs=raw['recommendations']
        if type(recs)!=list or not recs or any(type(r)!=str or r not in pack['approved_recommendations'] for r in recs):errors.append('Unsupported recommendation')
        if raw['provenance']!='AI_REASONED' or raw['confidence']!='BOUNDED_ONLY':errors.append('Unsupported provenance or confidence')
    except (ValueError,TypeError,KeyError,OverflowError,RecursionError):errors.append('Invalid structured response')
    return {'accepted':not errors,'errors':errors,'unsupported_claim_count':len(errors)}
