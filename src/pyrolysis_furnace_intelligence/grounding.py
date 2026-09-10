import hashlib,json
from .explanations import explain
from .scenario_engine import run_scenario

def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
def grounding_pack(state):
    # Accept only a verified result of the closed teaching-scenario engine.
    truth=run_scenario(state['scenario'])
    if canonical(state)!=canonical(truth):raise ValueError('State is not an unchanged engine result')
    digest=hashlib.sha256(canonical(state).encode()).hexdigest()
    evidence=[{'evidence_id':f'E{i:03d}','quantity':k,'result':v} for i,(k,v) in enumerate(state.items(),1)]
    return {'schema_version':'1','state_digest':digest,'operating_state':state['operating_state'],
      'active_authority':state['active_authority'],'evidence':evidence,
      'approved_claims':[{'claim_id':f'C{i:02d}','text':text,'evidence_ids':[e['evidence_id'] for e in evidence], 'provenance':'AI_REASONED'} for i,text in enumerate(explain(state),1)],
      'limitations':state['unavailable'],
      'approved_recommendations':['Review declared inputs and assumptions.','Retain engine authority; no actuation is authorized.','Obtain missing engineering evidence before a numerical decision.']}
