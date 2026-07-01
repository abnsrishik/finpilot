import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# llama-3.3-70b-versatile: best free Groq model for structured JSON + content
GROQ_MODEL = "llama-3.3-70b-versatile"

# Tavily search settings
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_MAX_RESULTS = 5

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in .env")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not set in .env")
