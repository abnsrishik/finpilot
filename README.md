# FinPilot

Finance content in your voice. Every week. In 60 seconds.

**Live demo:** [tryfinpilot.streamlit.app](https://tryfinpilot.streamlit.app)

---

## The problem

Indian finance creators spend 5–8 hours per content cycle:
- 2–3 hours researching (reading news, tracking markets)
- 2–3 hours writing (drafting newsletter)
- 1–2 hours repurposing (reformatting for LinkedIn, Twitter, email)

ChatGPT helps with one step. FinPilot handles the entire pipeline.

---

## What it does

One topic → autonomous research → angle selection → 4 content formats. In your voice.

```
┌─────────────────────────────────────────────────────────────┐
│                        FINPILOT                             │
│                                                             │
│   TOPIC INPUT                                               │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────┐                  │
│   │  RESEARCH (Tavily API)              │                  │
│   │  Query 1: "{topic}"                 │                  │
│   │  Query 2: "{topic} India 2026"      │                  │
│   │  Query 3: "{topic} impact data"     │                  │
│   │  → deduped sources, key facts       │                  │
│   └─────────────┬───────────────────────┘                  │
│                 │                                           │
│                 ▼                                           │
│   ┌─────────────────────────────────────┐                  │
│   │  ANGLE SELECTION (Groq API)         │                  │
│   │  Input: voice profile + research    │                  │
│   │  Output: selected angle + reasoning │                  │
│   │          + rejected alternatives    │                  │
│   └─────────────┬───────────────────────┘                  │
│                 │                                           │
│                 ▼                                           │
│   ┌─────────────────────────────────────┐                  │
│   │  MULTI-FORMAT GENERATION (Groq)     │                  │
│   │  One API call → structured JSON     │                  │
│   │                                     │                  │
│   │  ┌──────────┐  ┌──────────────────┐ │                  │
│   │  │Newsletter│  │  LinkedIn Post   │ │                  │
│   │  │500-800w  │  │  Single-line fmt │ │                  │
│   │  └──────────┘  └──────────────────┘ │                  │
│   │  ┌──────────┐  ┌──────────────────┐ │                  │
│   │  │ Twitter  │  │   Email Subject  │ │                  │
│   │  │ 5-7 tweets  │  + Preview text  │ │                  │
│   │  └──────────┘  └──────────────────┘ │                  │
│   └─────────────────────────────────────┘                  │
│                                                             │
│   Voice Profile (Groq, once per session)                    │
│   ──────────────────────────────────────                    │
│   Paste 3-5 past content → opening pattern,                 │
│   paragraph rhythm, transition style extracted              │
│   → used as context in all 3 downstream calls               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | Streamlit | Fast to build, free hosting |
| AI — generation & analysis | Groq API (Llama 3.3 70B) | Free tier, fast, reliable JSON output |
| AI — research | Tavily API | Built for AI research, real-time news |
| State | Streamlit session_state | Spec demo — no database needed |
| Deployment | Streamlit Community Cloud | Free, auto-deploys from GitHub |

---

## Project structure

```
finpilot/
├── app.py                      # Streamlit UI — single page, 4 zones
├── core/
│   ├── voice.py                # analyze_voice(content) -> dict
│   ├── research.py             # research_topic(topic) -> dict
│   ├── analyzer.py             # select_angle(voice, research, topic) -> dict
│   └── generator.py            # generate_content(voice, research, angle) -> dict
├── prompts/
│   ├── voice_analysis.py       # Prompt: extract structural voice blueprint
│   ├── angle_selection.py      # Prompt: select best angle + reasoning
│   ├── content_generation.py   # Prompt: 4-format structured JSON output
│   └── topic_suggestion.py     # Prompt: trending topics from research
├── utils/
│   └── config.py               # API key loading
├── requirements.txt
├── .env.example
└── .streamlit/config.toml      # Dark theme
```

---

## How to run

```bash
git clone https://github.com/abnsrishik/finpilot
cd finpilot
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY and TAVILY_API_KEY to .env
streamlit run app.py
```

Get API keys:
- Groq: https://console.groq.com (free tier — no credit card)
- Tavily: https://tavily.com (1,000 free searches/month)

---

## How it works

**Step 1 — Voice analysis**
Paste 3–5 past content pieces. The model extracts a structural blueprint: opening pattern (how the creator starts every piece), paragraph rhythm (short punchy vs. long build), transition style (how ideas connect), conclusion pattern (what they always leave the reader with). Stored in session for all subsequent calls.

**Step 2 — Research**
Tavily runs 3 targeted searches: broad, India-localized, data-focused. Results deduplicated. Key facts extracted. Source list compiled with titles + URLs.

**Step 3 — Angle selection**
The model receives voice profile + research. Picks the best angle for THIS creator's specific audience. Returns: selected angle, reasoning (specific, not generic), rejected alternatives. This is the "I can't do this with ChatGPT" moment — the system EXPLAINS its reasoning.

**Step 4 — Multi-format generation**
One API call with structured output. Returns JSON: newsletter (500–800w), LinkedIn post (single-sentence-line format), Twitter thread (5–7 tweets), email subject + preview. All voice-matched. All source-grounded.

---

## Cost

~$0.02 per full content run on Groq free tier.

---

## Built by

Rishik — AI engineering student at SRM University (GPA 9.88), 16 shipped projects.

[GitHub](https://github.com/abnsrishik) | [LinkedIn](https://linkedin.com/in/yourprofile)
