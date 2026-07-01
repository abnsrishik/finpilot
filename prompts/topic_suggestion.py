TOPIC_SUGGESTION_SYSTEM = """You are a content strategist for Indian finance creators.
Suggest topics based on what's actually trending in Indian finance news — not evergreen theory.
Return ONLY valid JSON, no prose."""

TOPIC_SUGGESTION_USER = """Based on this finance creator's voice profile and the trending news research, suggest 5 topics they should cover this week.

CREATOR VOICE PROFILE:
{voice_profile}

TRENDING NEWS FROM RESEARCH:
{trending_research}

For each topic, suggest the angle that fits THIS creator's audience.
Return exactly:
{{
  "topics": [
    {{
      "topic": "specific topic string (what you'd type into search)",
      "reader_framing": "how their audience would phrase this question (e.g. 'Should I pause my SIPs now?')",
      "angle": "the specific angle for this creator's audience",
      "why_now": "one sentence: why this week specifically"
    }}
  ]
}}"""
