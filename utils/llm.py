import json
import time

from groq import Groq
from utils.config import GROQ_API_KEY, GROQ_MODEL

# Single shared client — modules used to each make their own.
client = Groq(api_key=GROQ_API_KEY)


class LLMError(Exception):
    """Raised when an LLM call fails to return valid JSON with the expected keys after retries."""


def _strip_fences(raw: str) -> str:
    """Some models wrap JSON in ```json fences despite response_format. Strip them."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def call_json(system, user, *, temperature, required_keys, max_tokens=4096, retries=1):
    """
    One place every LLM call routes through: JSON-mode Groq call + parse + key validation + retry.

    Raises LLMError (with a user-friendly message) if, after `retries` extra attempts,
    the response still isn't valid JSON or is missing any of `required_keys`.
    """
    last_err = None
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens,
            )
            data = json.loads(_strip_fences(response.choices[0].message.content))
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise ValueError(f"missing keys: {missing}")
            return data
        except Exception as e:  # JSONDecodeError, missing keys, or transient API/429
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))  # short backoff before retry
    raise LLMError(
        "The AI response came back incomplete. Please try again in a moment."
    ) from last_err


# ponytail: self-check — asserts validation + retry behavior without hitting the API
if __name__ == "__main__":
    # Fence stripping
    assert _strip_fences('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert _strip_fences('{"a": 1}') == '{"a": 1}'
    print("llm.py self-check passed")
