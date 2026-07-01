import json
from groq import Groq
from utils.config import GROQ_API_KEY, GROQ_MODEL
from prompts.angle_selection import ANGLE_SELECTION_SYSTEM, ANGLE_SELECTION_USER

client = Groq(api_key=GROQ_API_KEY)


def select_angle(voice: dict, research: dict, topic: str) -> dict:
    """
    Given voice profile + research, select the best content angle.
    Returns: {selected_angle, reasoning, audience_connection, rejected_angles}
    """
    key_facts_str = "\n".join(f"• {f}" for f in research["key_facts"])

    prompt = ANGLE_SELECTION_USER.format(
        voice_profile=json.dumps(voice, indent=2),
        topic=topic,
        research_summary=research["summary"],
        key_facts=key_facts_str,
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": ANGLE_SELECTION_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return json.loads(response.choices[0].message.content)


# ponytail: CLI test
if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
    from core.voice import analyze_voice
    from core.research import research_topic

    print("Paste content samples (end with ---EOF---):")
    lines = []
    while True:
        line = input()
        if line.strip() == "---EOF---":
            break
        lines.append(line)

    topic = input("Topic: ")
    voice = analyze_voice("\n".join(lines))
    research = research_topic(topic)
    angle = select_angle(voice, research, topic)

    print("\n--- SELECTED ANGLE ---")
    print(f"Angle: {angle['selected_angle']}")
    print(f"Reasoning: {angle['reasoning']}")
    print(f"Audience connection: {angle['audience_connection']}")
    for r in angle.get("rejected_angles", []):
        print(f"  ✗ {r['angle']} — {r['why_rejected']}")
