"""The instructions sent to the real AI with each request description.

The allowed values are copied from the app, because the adapter must not import the app.
A test checks that these copies still match the app's own lists.
"""

CATEGORIES = ["cooling_space", "welfare_visit", "practical_assistance"]
PRIORITIES = ["low", "normal", "high", "urgent"]

SYSTEM_PROMPT = f"""You help heatwave support staff triage support requests.
You only make suggestions. Staff review every suggestion and make every decision.

Reply with one JSON object only, with exactly these keys:
- "summary": one short sentence describing the request
- "missing_info": a list of short strings naming information staff still need (an empty list if none)
- "medical_advice_flag": true if the request asks for a diagnosis, medicine, dose or treatment, otherwise false
- "suggested_category": one of {", ".join(CATEGORIES)}
- "suggested_priority": one of {", ".join(PRIORITIES)}
- "rationale": one or two sentences explaining the category and priority
- "support_option": one short practical next step for staff

Never give medical advice. Do not diagnose, name medicines or doses, or suggest treatment."""

# The exact shape the AI must reply with, sent with every request. "strict" tells the service to follow it
# exactly, so it can only use the allowed categories and priorities. Every answer is still checked anyway.
FIELDS = ["summary", "missing_info", "medical_advice_flag", "suggested_category", "suggested_priority",
          "rationale", "support_option"]

RESPONSE_SCHEMA = {
    "name": "triage_suggestion",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "missing_info": {"type": "array", "items": {"type": "string"}},
            "medical_advice_flag": {"type": "boolean"},
            "suggested_category": {"type": "string", "enum": CATEGORIES},
            "suggested_priority": {"type": "string", "enum": PRIORITIES},
            "rationale": {"type": "string"},
            "support_option": {"type": "string"},
        },
        "required": FIELDS,
        "additionalProperties": False,
    },
}