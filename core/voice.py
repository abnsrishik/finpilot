import json
from utils.llm import call_json
from prompts.voice_analysis import VOICE_ANALYSIS_SYSTEM, VOICE_ANALYSIS_USER

# Keys the downstream generator/UI actually read from the profile.
_REQUIRED = ["opening_pattern", "paragraph_rhythm", "vocabulary_markers",
             "audience_type", "voice_summary"]


def analyze_voice(content: str) -> dict:
    """
    Analyze pasted content samples and return a structured voice profile.
    content: raw text of 3-5 past newsletters/posts
    """
    return call_json(
        VOICE_ANALYSIS_SYSTEM,
        VOICE_ANALYSIS_USER.format(content=content),
        temperature=0.3,
        required_keys=_REQUIRED,
    )


# ponytail: CLI test
if __name__ == "__main__":
    print("Paste content samples (end with ---EOF--- on its own line):")
    lines = []
    while True:
        line = input()
        if line.strip() == "---EOF---":
            break
        lines.append(line)
    profile = analyze_voice("\n".join(lines))
    print("\n--- VOICE PROFILE ---")
    print(json.dumps(profile, indent=2))
