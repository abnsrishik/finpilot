# FinPilot

Finance content in your voice. Every week. In 60 seconds.

**Live demo:** [finpilot.streamlit.app](https://finpilot.streamlit.app) *(deploy link — update after deploy)*

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
│   │  ANGLE SELECTION (Claude API)       │                  │
│   │  Input: voice profile + research    │                  │
│   │  Output: selected angle + reasoning │                  │
│   │          + rejected alternatives    │                  │
│   └─────────────┬───────────────────────┘                  │
│                 │                                           │
│                 ▼                                           │
│   ┌─────────────────────────────────────┐                  │
│   │  MULTI-FORMAT GENERATION (Claude)   │                  │
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
│   Voice Profile (Claude, once per session)                  │
│   ──────────────────────────────────────                    │
│   Paste 3-5 past content → tone, structure,                 │
│   vocabulary, audience type extracted                       │
│   → used as context in all 3 downstream calls               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | Streamlit | Fast to build, free hosting |
| AI — generation & analysis | Claude API (claude-sonnet-4-6) | Best structured JSON output, fast |
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
│   ├── voice_analysis.py       # Prompt: extract voice markers
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
git clone https://github.com/yourusername/finpilot
cd finpilot
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY and TAVILY_API_KEY to .env
streamlit run app.py
```

Get API keys:
- Anthropic: https://console.anthropic.com
- Tavily: https://tavily.com (1,000 free searches/month)

---

## How it works

**Step 1 — Voice analysis**
Paste 3–5 past content pieces. Claude extracts: sentence length, tone, vocabulary, opening style, data usage, unique phrases, audience type. Stored in session for all subsequent calls.

**Step 2 — Research**
Tavily runs 3 targeted searches: broad, India-localized, data-focused. Results deduplicated. Key facts extracted. Source list compiled with titles + URLs.

**Step 3 — Angle selection**
Claude receives voice profile + research. Picks the best angle for THIS creator's specific audience. Returns: selected angle, reasoning (specific, not generic), rejected alternatives. This is the "I can't do this with ChatGPT" moment — the system EXPLAINS its reasoning.

**Step 4 — Multi-format generation**
One Claude API call with structured output. Returns JSON: newsletter (500–800w), LinkedIn post (single-sentence-line format), Twitter thread (5–7 tweets), email subject + preview. All voice-matched. All source-grounded.

---

## Cost

~$0.06 per full content run. Negligible.

---

## Built by

Rishik — AI engineering student at SRM University (GPA 9.88), 16 shipped projects.

[GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)
