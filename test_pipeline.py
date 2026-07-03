"""
Pre-demo smoke test. Run this before every demo/Loom:

    python test_pipeline.py

Runs the full pipeline on a canned sample + fixed topic and asserts every stage
returns the keys the app depends on. Catches a bad deploy or SDK breakage BEFORE
a prospect does. Needs GROQ_API_KEY + TAVILY_API_KEY set (same as the app).
"""
from core.voice import analyze_voice
from core.research import research_topic
from core.analyzer import select_angle
from core.generator import generate_content

SAMPLE = """The market fell 2% today. Most people panicked.
Here is what I did instead: nothing.
Volatility is the price of admission for long-term returns.
If you are investing for 10 years, a 2% day is noise.
My read: stay the course, keep your SIPs running."""

TOPIC = "RBI rate hold impact on SIP investors"


def main():
    print("1/4 voice...")
    voice = analyze_voice(SAMPLE)
    for k in ["opening_pattern", "paragraph_rhythm", "vocabulary_markers",
              "audience_type", "voice_summary"]:
        assert k in voice, f"voice missing {k}"

    print("2/4 research...")
    research = research_topic(TOPIC)
    for k in ["sources", "key_facts", "summary", "source_count", "degraded"]:
        assert k in research, f"research missing {k}"

    print("3/4 angle...")
    angle = select_angle(voice, research, TOPIC)
    for k in ["selected_angle", "reasoning"]:
        assert k in angle, f"angle missing {k}"

    print("4/4 generate...")
    content = generate_content(voice, research, angle)
    for k in ["newsletter", "linkedin_post", "twitter_thread",
              "email_subject", "email_preview", "sources"]:
        assert k in content, f"content missing {k}"
    assert isinstance(content["twitter_thread"], list), "twitter_thread must be a list"
    assert content["newsletter"].strip(), "newsletter is empty"

    print(f"\n✅ PIPELINE OK — {'DEGRADED (no fresh sources)' if research['degraded'] else research['source_count']} sources, "
          f"{len(content['twitter_thread'])} tweets. Safe to demo.")


if __name__ == "__main__":
    main()
