import os
from dotenv import load_dotenv

load_dotenv()

def _get(key: str) -> str:
    # Local: .env via dotenv. Streamlit Cloud: st.secrets.
    value = os.getenv(key)
    if not value:
        try:
            import streamlit as st
            value = st.secrets.get(key)
        except Exception:
            pass
    return value

GROQ_API_KEY = _get("GROQ_API_KEY")
TAVILY_API_KEY = _get("TAVILY_API_KEY")

GROQ_MODEL = "llama-3.3-70b-versatile"
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_MAX_RESULTS = 5

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not set")
