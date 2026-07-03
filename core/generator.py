from utils.llm import call_json
from prompts.content_generation import CONTENT_GENERATION_SYSTEM, CONTENT_GENERATION_USER


def _safe(s: str) -> str:
    """Escape braces so str.format() doesn't choke on URLs or titles."""
    return str(s).replace("{", "{{").replace("}", "}}")


def generate_content(voice: dict, research: dict, angle: dict) -> dict:
    """
    One LLM call → 4 content formats simultaneously.
    Returns: {newsletter, linkedin_post, twitter_thread, email_subject, email_preview, sources}
    """
    source_list = "\n".join(
        f"{i+1}. [{s['title']}]({s['url']})"
        for i, s in enumerate(research["sources"][:6])
    )

    research_context = (
        f"Summary: {research['summary']}\n\n"
        f"Key Facts:\n" + "\n".join(f"• {f}" for f in research["key_facts"])
    )

    sources_str = "\n".join(
        f"• {s['title']} — {s['url']}"
        for s in research["sources"][:6]
    )

    # Pull structured fields from the new voice profile schema
    vocab = voice.get("vocabulary_markers", {})

    prompt = CONTENT_GENERATION_USER.format(
        # Structural blueprint fields
        opening_pattern=_safe(voice.get("opening_pattern", "Start with a relevant observation about the topic.")),
        tension_build=_safe(voice.get("tension_build", "Build context for 1-2 paragraphs before the main argument.")),
        evidence_style=_safe(voice.get("evidence_style", "State the insight, then provide the supporting data.")),
        paragraph_rhythm=_safe(voice.get("paragraph_rhythm", "2-3 medium sentences per paragraph.")),
        transition_style=_safe(voice.get("transition_style", "Use a short transition sentence between sections.")),
        uncertainty_handling=_safe(voice.get("uncertainty_handling", "State uncertainty directly when present.")),
        conclusion_pattern=_safe(voice.get("conclusion_pattern", "End with a clear takeaway for the reader.")),
        analogy_usage=_safe(voice.get("analogy_usage", "Use analogies when helpful to explain complex ideas.")),
        # Vocabulary
        sentence_length=_safe(vocab.get("sentence_length", "medium")),
        formality=_safe(vocab.get("formality", "conversational")),
        jargon_level=_safe(vocab.get("jargon_level", "explains key terms")),
        unique_phrases=_safe(", ".join(f'"{p}"' for p in vocab.get("unique_phrases", [])[:5])),
        # Audience
        audience_assumption=_safe(voice.get("audience_assumption", "Reader is familiar with basic investing concepts.")),
        audience_type=_safe(voice.get("audience_type", "retail investors")),
        voice_summary=_safe(voice.get("voice_summary", "Write clearly and specifically for retail investors.")),
        # Content
        topic=_safe(research["topic"]),
        selected_angle=_safe(angle["selected_angle"]),
        angle_reasoning=_safe(angle["reasoning"]),
        research_context=_safe(research_context),
        sources=_safe(sources_str),
        source_list_placeholder=_safe(source_list),
    )

    # When research came back empty, tell the model not to fabricate specific figures.
    if research.get("degraded"):
        prompt += ("\n\n=== IMPORTANT ===\nNo fresh news sources were available for this topic. "
                   "Write from general knowledge only. Do NOT invent specific numbers, dates, "
                   "percentages, or quotes. Keep claims general and note where the reader should verify current data.")

    content = call_json(
        CONTENT_GENERATION_SYSTEM,
        prompt,
        temperature=0.7,
        required_keys=["newsletter", "linkedin_post", "twitter_thread",
                       "email_subject", "email_preview"],
        max_tokens=4096,
    )

    # Normalize twitter_thread to a list once, so every consumer (UI + download) is consistent.
    thread = content["twitter_thread"]
    if isinstance(thread, str):
        content["twitter_thread"] = [t.strip() for t in thread.split("\n") if t.strip()]

    content["sources"] = research["sources"][:6]
    return content


# ponytail: CLI test — runs full pipeline end-to-end
if __name__ == "__main__":
    import sys, pathlib, time
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
    from core.voice import analyze_voice
    from core.research import research_topic
    from core.analyzer import select_angle

    print("Paste content samples (end with ---EOF---):")
    lines = []
    while True:
        line = input()
        if line.strip() == "---EOF---":
            break
        lines.append(line)

    topic = input("Topic: ")
    t0 = time.time()

    print("Analyzing voice...")
    voice = analyze_voice("\n".join(lines))
    print(f"  → {voice.get('voice_summary', '')[:100]}...")

    print("Researching...")
    research = research_topic(topic)
    print(f"  → {research['source_count']} sources")

    print("Selecting angle...")
    angle = select_angle(voice, research, topic)
    print(f"  → {angle['selected_angle']}")

    print("Generating content...")
    content = generate_content(voice, research, angle)

    print(f"\n✅ Done in {time.time() - t0:.0f}s\n")
    print("=== NEWSLETTER (first 500 chars) ===")
    print(content["newsletter"][:500])
    print("\n=== LINKEDIN POST ===")
    print(content["linkedin_post"])
    print("\n=== TWITTER THREAD ===")
    for i, tweet in enumerate(content["twitter_thread"], 1):
        print(f"[{i}] {tweet}")
    print(f"\n=== EMAIL ===")
    print(f"Subject: {content['email_subject']}")
    print(f"Preview: {content['email_preview']}")
