import json
from groq import Groq
from utils.config import GROQ_API_KEY, GROQ_MODEL
from prompts.voice_analysis import VOICE_ANALYSIS_SYSTEM, VOICE_ANALYSIS_USER

client = Groq(api_key=GROQ_API_KEY)


def analyze_voice(content: str) -> dict:
    """
    Analyze pasted content samples and return a structured voice profile.
    content: raw text of 3-5 past newsletters/posts
    """
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": VOICE_ANALYSIS_SYSTEM},
            {"role": "user", "content": VOICE_ANALYSIS_USER.format(content=content)},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)


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
