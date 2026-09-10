"""Provider guidance for the bounded catalogue contract."""
SYSTEM_PROMPT = '''Use only the current evidence pack. Return the exact assessment fields:
state_digest, operating_state, active_authority, claims, evidence, limitations,
recommendations, provenance, confidence. Copy approved_claims to claims, evidence
to evidence and limitations to limitations without changes. Select at least one
approved recommendation. Set provenance to AI_REASONED and confidence to BOUNDED_ONLY.
No additional statements, numbers, actuator instructions or safety judgments are accepted.
This is a bounded educational explanation, not authority to operate equipment.'''
OUTPUT_FIELDS=('state_digest','operating_state','active_authority','claims','evidence','limitations','recommendations','provenance','confidence')
