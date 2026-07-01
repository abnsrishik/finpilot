VOICE_ANALYSIS_SYSTEM = """You are analyzing a finance content creator's writing to extract a structural blueprint.
Your job is NOT to describe their vocabulary or tone in abstract terms.
Your job is to describe HOW THEY THINK ON THE PAGE — step by step, pattern by pattern.
A ghostwriter reading your output should be able to replicate the structure without ever reading the originals.
Return ONLY valid JSON, no prose."""

VOICE_ANALYSIS_USER = """Read these content samples from a finance creator carefully.
Extract a structural blueprint — not surface features, but HOW they construct arguments and move through ideas.

CONTENT SAMPLES:
{content}

Return this exact JSON structure:

{{
  "opening_pattern": "Describe EXACTLY how they start pieces. Be specific: do they open with a question? A surprising number? A news headline restated? A common misconception they then challenge? A personal observation? Give an example opening sentence that fits their pattern.",

  "tension_build": "How do they create interest after the opening? Do they state the problem immediately? Build context first? Use a 'but here's what most people miss' pivot? How many sentences before they get to the main point?",

  "evidence_style": "How do they introduce data and research? Do they state the insight BEFORE the number, or AFTER? Do they use phrases like 'Here is what the data says' or do they drop numbers without preamble? Do they explain what each number means or leave it to the reader?",

  "paragraph_rhythm": "Describe the actual sentence pattern. Example: '2-3 short sentences (under 15 words each), then one longer analytical sentence (25-35 words), then a one-sentence paragraph as a pause.' Be specific about length and rhythm.",

  "transition_style": "How do they move between sections? Single-word paragraphs? 'But here is the thing:'? Numbered sections? Subheadings? Blank lines? Quote the type of transition phrase they typically use.",

  "uncertainty_handling": "When they are not sure of something, what do they say? Do they hedge ('this could be wrong')? Do they state confidently? Do they present both sides? Do they use phrases like 'my read is' or 'I could be wrong here'?",

  "conclusion_pattern": "How do they end pieces? Open question for the reader? Firm takeaway? Bulleted summary? A single line? CTA? No CTA? Describe the last paragraph structure specifically.",

  "analogy_usage": "Do they use analogies to explain complex concepts? If yes, what type — everyday life comparisons, historical comparisons, sports metaphors? If no, what do they use instead?",

  "vocabulary_markers": {{
    "sentence_length": "short (under 15 words avg) | medium (15-25) | long (25+) | mixed",
    "formality": "formal | casual | conversational | authoritative",
    "jargon_level": "explains all terms | uses terms without explaining | mixed",
    "unique_phrases": ["list", "of", "phrases", "they", "actually", "use", "repeatedly"]
  }},

  "audience_assumption": "What does this creator assume their reader already knows? What do they always explain? What do they never explain?",

  "audience_type": "retail investors | traders | students | professionals | mixed",

  "voice_summary": "Write 3-4 sentences describing HOW THIS CREATOR THINKS ON THE PAGE — written as a directive to a ghostwriter. Example: 'Open every piece with a question that challenges a common assumption. Build context for 2-3 paragraphs before introducing your main argument. Always explain what a number means before giving the number. End without a CTA — let the insight speak for itself.'"
}}"""
