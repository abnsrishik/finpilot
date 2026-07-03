import time
import json
import streamlit as st

from core.voice import analyze_voice
from core.research import research_topic, get_trending_topics
from core.analyzer import select_angle
from core.generator import generate_content
from prompts.topic_suggestion import TOPIC_SUGGESTION_SYSTEM, TOPIC_SUGGESTION_USER
from utils.llm import call_json, LLMError

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinPilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { max-width: 860px; padding-top: 2rem; }
.step-header { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.12em;
               color: #00D4AA; text-transform: uppercase; margin-bottom: 0.25rem; }
.voice-card { background: #1A1F2E; border-radius: 12px; padding: 1.25rem 1.5rem;
              border-left: 3px solid #00D4AA; margin-top: 0.75rem; }
.activity-line { padding: 0.35rem 0; font-size: 0.95rem; }
.stat-box { background: #1A1F2E; border-radius: 10px; padding: 1rem 1.25rem;
            text-align: center; }
.stat-number { font-size: 2rem; font-weight: 700; color: #00D4AA; }
.stat-label { font-size: 0.8rem; color: #888; margin-top: 0.1rem; }
.source-link { font-size: 0.82rem; color: #00D4AA; }
.compare-cell { background: #1A1F2E; border-radius: 8px; padding: 1rem; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── One-click copy helper ─────────────────────────────────────────────────────
import html as _html
import streamlit.components.v1 as components

def copy_button(label: str, text: str, key: str):
    """
    One-click copy that works inside Streamlit's sandboxed component iframe.
    Uses a hidden <textarea> + execCommand('copy') (works in iframes where
    navigator.clipboard is permission-blocked), falling back to the clipboard
    API if execCommand isn't available. Text is embedded as a JS string literal
    via json.dumps — no HTML-escaping (that would corrupt it inside <script>).
    """
    payload = json.dumps(text)  # safe JS string literal: escapes quotes/newlines/backslashes
    components.html(
        f"""
        <button id="{key}" style="background:#00D4AA;color:#0E1117;border:none;
            border-radius:8px;padding:0.5rem 1rem;font-weight:600;cursor:pointer;font-size:0.9rem;">
            {_html.escape(label)}
        </button>
        <span id="{key}_ok" style="color:#00D4AA;margin-left:0.6rem;font-size:0.85rem;"></span>
        <script>
        (function() {{
            const text = {payload};
            const ok = document.getElementById("{key}_ok");
            document.getElementById("{key}").addEventListener("click", function() {{
                // Primary: hidden textarea + execCommand — works in sandboxed iframes.
                const ta = document.createElement("textarea");
                ta.value = text;
                ta.style.position = "fixed";
                ta.style.left = "-9999px";
                document.body.appendChild(ta);
                ta.focus();
                ta.select();
                let done = false;
                try {{ done = document.execCommand("copy"); }} catch (e) {{ done = false; }}
                document.body.removeChild(ta);
                if (done) {{ ok.innerText = "✓ Copied"; return; }}
                // Fallback: clipboard API (works when not iframe-blocked).
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(text)
                        .then(() => ok.innerText = "✓ Copied")
                        .catch(() => ok.innerText = "Select the text and press Ctrl+C");
                }} else {{
                    ok.innerText = "Select the text and press Ctrl+C";
                }}
            }});
        }})();
        </script>
        """,
        height=45,
    )

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("## FinPilot")
st.markdown("*Finance content in your voice. Every week. In 60 sec.*")
st.divider()

# ─── Session state init ────────────────────────────────────────────────────────
for key in ["voice_profile", "research", "angle", "content", "topic_input",
            "topic_suggestions", "generation_time"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 — VOICE SETUP
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-header">Step 1 — Teach it your writing style</div>',
            unsafe_allow_html=True)

content_input = st.text_area(
    label="Paste 3–5 of your past newsletters or posts",
    placeholder="Paste your past writing here — newsletters, LinkedIn posts, anything you've published.\n\nThe more you paste, the better it learns your voice.",
    height=200,
    label_visibility="collapsed",
)

analyze_btn = st.button("Learn My Writing Style →", type="primary", use_container_width=False)

if analyze_btn:
    if not content_input.strip():
        st.error("Paste some of your past content first.")
    else:
        with st.spinner("Reading your writing..."):
            try:
                st.session_state.voice_profile = analyze_voice(content_input)
                # Reset downstream state when voice changes
                for key in ["research", "angle", "content", "topic_suggestions"]:
                    st.session_state[key] = None
            except Exception as e:
                st.error(f"Couldn't analyze your writing: {e}")

if st.session_state.voice_profile:
    v = st.session_state.voice_profile
    vocab = v.get("vocabulary_markers", {})
    phrases = vocab.get("unique_phrases", v.get("unique_phrases", []))

    lines = []
    if v.get("opening_pattern"):
        lines.append(f"<b>How you open:</b> {v['opening_pattern']}")
    if v.get("paragraph_rhythm"):
        lines.append(f"<b>Your rhythm:</b> {v['paragraph_rhythm']}")
    if v.get("conclusion_pattern"):
        lines.append(f"<b>How you close:</b> {v['conclusion_pattern']}")
    if phrases:
        lines.append(f"<b>You often say:</b> <em>{', '.join(repr(p) for p in phrases[:4])}</em>")
    if v.get("audience_type"):
        lines.append(f"<b>Your readers:</b> {v['audience_type']}")
    if v.get("voice_summary"):
        lines.append(f"<br><em>{v['voice_summary']}</em>")

    st.markdown(
        '<div class="voice-card">' +
        "<br><br>".join(lines) +
        "<br><br>✅ Style learned — content will sound like you</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 — TOPIC SELECTION
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-header">Step 2 — Pick this week\'s topic</div>',
            unsafe_allow_html=True)

topic_manual = st.text_input(
    label="What do you want to cover this week?",
    placeholder="e.g. RBI rate hold, SIP vs FD, Budget 2026 impact...",
    label_visibility="collapsed",
)

# Trending topic suggestions
if st.session_state.voice_profile:
    suggest_btn = st.button("📰 Show what your readers are searching for this week",
                            use_container_width=False)
    if suggest_btn and not st.session_state.topic_suggestions:
        with st.spinner("Checking today's finance news..."):
            try:
                trending = get_trending_topics()
                trending_text = "\n".join(
                    f"• {r['title']}: {r.get('content', '')[:150]}"
                    for r in trending["results"][:8]
                )
                result = call_json(
                    TOPIC_SUGGESTION_SYSTEM,
                    TOPIC_SUGGESTION_USER.format(
                        voice_profile=json.dumps(st.session_state.voice_profile, indent=2),
                        trending_research=trending_text,
                    ),
                    temperature=0.5,
                    required_keys=["topics"],
                )
                st.session_state.topic_suggestions = result.get("topics", [])
            except Exception as e:
                st.warning(f"Couldn't load suggestions: {e}")

if st.session_state.topic_suggestions:
    options = [
        f"{t['reader_framing']}"
        for t in st.session_state.topic_suggestions
    ]
    selected_idx = st.radio(
        "Or pick one:",
        range(len(options)),
        format_func=lambda i: options[i],
        label_visibility="visible",
    )
    suggestion_topic = st.session_state.topic_suggestions[selected_idx]["topic"]
else:
    suggestion_topic = None

# Resolve final topic
final_topic = topic_manual.strip() or suggestion_topic

generate_btn = st.button(
    "Generate This Week's Content →",
    type="primary",
    use_container_width=False,
    disabled=(not st.session_state.voice_profile or not final_topic),
)

st.divider()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 — PIPELINE EXECUTION
# ════════════════════════════════════════════════════════════════════════════════
if generate_btn and st.session_state.voice_profile and final_topic:

    st.markdown('<div class="step-header">Working on it</div>', unsafe_allow_html=True)

    activity = st.empty()
    t0 = time.time()

    steps_done = []

    def show_progress(steps):
        activity.markdown(
            "\n".join(steps),
            unsafe_allow_html=True,
        )

    try:
        # Research
        show_progress(["⏳ Reading today's finance news so you don't have to..."])
        research = research_topic(final_topic)
        if research.get("degraded"):
            st.warning(
                "Limited fresh news on this topic right now — generating from general "
                "knowledge. Double-check any specific figures before publishing."
            )
            steps_done.append("⚠️ **Limited fresh news found** — writing from general knowledge")
        else:
            steps_done.append(
                f"✅ **Read today's finance news** — "
                f"scanned {research['source_count']} sources "
                f"({', '.join(s['title'][:30] for s in research['sources'][:3])}...)"
            )
        show_progress(steps_done + ["⏳ Choosing your angle..."])

        # Angle selection
        angle = select_angle(st.session_state.voice_profile, research, final_topic)
        steps_done.append(
            f"✅ **Chose your angle** — {angle['selected_angle']} "
            f"*(picked based on your writing history)*"
        )
        show_progress(steps_done + ["⏳ Writing for every platform..."])

        # Generation
        content = generate_content(st.session_state.voice_profile, research, angle)
        elapsed = time.time() - t0
        steps_done.append(
            "✅ **Done writing** — Newsletter, LinkedIn, Twitter, Email — all ready"
        )

        show_progress(steps_done + [f"\n⏱️ **{elapsed:.0f} seconds** — vs. your usual 5 hours"])

        # Save to session
        st.session_state.research = research
        st.session_state.angle = angle
        st.session_state.content = content
        st.session_state.generation_time = elapsed

    except LLMError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Something went wrong: {e}")

# ════════════════════════════════════════════════════════════════════════════════
# STEP 4 — OUTPUT
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.content:
    content = st.session_state.content
    research = st.session_state.research
    angle = st.session_state.angle
    elapsed = st.session_state.generation_time

    st.markdown('<div class="step-header">Ready to publish</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Newsletter", "LinkedIn", "Twitter / X", "Email"])

    # ── Newsletter ──
    with tab1:
        st.markdown(content["newsletter"])
        st.divider()
        if content["sources"]:
            st.markdown("**Fact-checked against today's news — click to verify:**")
            for i, s in enumerate(content["sources"], 1):
                st.markdown(
                    f'<span class="source-link">{i}. <a href="{s["url"]}" target="_blank">{s["title"]}</a></span>',
                    unsafe_allow_html=True,
                )
        copy_button("Copy Newsletter", content["newsletter"], "copy_nl")

    # ── LinkedIn ──
    with tab2:
        st.markdown(content["linkedin_post"])
        st.divider()
        st.markdown("**Sources:**")
        for i, s in enumerate(content["sources"][:3], 1):
            st.markdown(
                f'<span class="source-link">{i}. <a href="{s["url"]}" target="_blank">{s["title"]}</a></span>',
                unsafe_allow_html=True,
            )
        copy_button("Copy LinkedIn Post", content["linkedin_post"], "copy_li")

    # ── Twitter ──
    with tab3:
        thread = content["twitter_thread"]  # normalized to a list in generator
        for i, tweet in enumerate(thread, 1):
            st.markdown(f"**[{i}/{len(thread)}]** {tweet}")
            st.markdown("")
        thread_text = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(thread, 1))
        copy_button("Copy Thread", thread_text, "copy_tw")

    # ── Email ──
    with tab4:
        st.markdown(f"**Subject line:**")
        st.info(content["email_subject"])
        st.markdown(f"**Preview text:**")
        st.info(content["email_preview"])
        copy_button(
            "Copy Email Subject + Preview",
            f"Subject: {content['email_subject']}\nPreview: {content['email_preview']}",
            "copy_em",
        )

    # Download all
    all_content = f"""# FinPilot Output — {research['topic']}
Angle: {angle['selected_angle']}
Generated in {elapsed:.0f} seconds

---

## NEWSLETTER

{content['newsletter']}

---

## LINKEDIN POST

{content['linkedin_post']}

---

## TWITTER THREAD

{chr(10).join(f"[{i}] {t}" for i, t in enumerate(content['twitter_thread'], 1))}

---

## EMAIL

Subject: {content['email_subject']}
Preview: {content['email_preview']}

---

## SOURCES

{chr(10).join(f"{i+1}. {s['title']} — {s['url']}" for i, s in enumerate(content['sources']))}
"""
    st.download_button(
        "Download All (Markdown)",
        data=all_content,
        file_name=f"finpilot_{research['topic'][:30].replace(' ', '_')}.md",
        mime="text/markdown",
    )

    st.divider()

    # ── Voice comparison ──
    st.markdown('<div class="step-header">Does it sound like you?</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    # Show full opening paragraph, not just 150 chars
    newsletter_paragraphs = [p.strip() for p in content["newsletter"].split("\n\n") if p.strip()]
    opening_para = newsletter_paragraphs[0] if newsletter_paragraphs else content["newsletter"][:200]
    with col1:
        st.markdown('<div class="compare-cell"><b>How you write</b><br><br>' +
                    f"<em>{st.session_state.voice_profile.get('opening_pattern', st.session_state.voice_profile.get('voice_summary', ''))}</em></div>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="compare-cell"><b>Your content this week</b><br><br>' +
                    f"{opening_para}</div>",
                    unsafe_allow_html=True)

    v = st.session_state.voice_profile
    st.markdown(
        f"✅ Opening style matched &nbsp;|&nbsp; "
        f"✅ Data usage ({v.get('data_usage', '')}) matched &nbsp;|&nbsp; "
        f"✅ Audience ({v.get('audience_type', '')}) matched"
    )

    st.divider()

    # ── ROI stats ──
    st.markdown('<div class="step-header">This week\'s numbers</div>',
                unsafe_allow_html=True)

    hours_saved = 5.0
    monthly_hours = hours_saved * 4
    monthly_value = monthly_hours * 500

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{elapsed:.0f}s</div>'
                    f'<div class="stat-label">Time to generate</div></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{hours_saved:.0f}h</div>'
                    f'<div class="stat-label">Saved this content cycle</div></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-number">₹{monthly_value:,.0f}</div>'
                    f'<div class="stat-label">Time value saved / month</div></div>',
                    unsafe_allow_html=True)
