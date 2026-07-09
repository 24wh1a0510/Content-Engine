"""
app.py — AI Content Engine · Streamlit UI

Provider split:
  Text   → OpenAI GPT-4o mini
  Image  → OpenAI DALL-E 3
  Audio  → OpenAI TTS (tts-1, voice: nova)
  Video  → OpenRouter Wan 2.6 (qwen/wan2.6-t2v)

Run: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# ── Page config — must be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="AI Content Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }

/* Header */
.hero-title { font-size: 2.4rem; font-weight: 700; color: #0F172A; line-height: 1.2; margin-bottom: 0.15rem; }
.hero-sub   { font-size: 1rem; color: #64748B; margin-bottom: 2rem; }
.accent     { background: linear-gradient(135deg,#6366F1,#8B5CF6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }

/* Section headings */
.section-header { font-size:.85rem; font-weight:600; color:#374151; text-transform:uppercase; letter-spacing:.08em; margin-bottom:1rem; padding-bottom:.5rem; border-bottom:2px solid #E5E7EB; }

/* Cards */
.card { background:#FFFFFF; border-radius:14px; padding:1.25rem 1.4rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.05); border:1px solid #F1F5F9; }
.card-title { font-size:.72rem; font-weight:600; text-transform:uppercase; letter-spacing:.1em; color:#94A3B8; margin-bottom:.6rem; }
.card-body  { font-size:.93rem; color:#1E293B; line-height:1.75; }
.card-placeholder { color:#CBD5E1; font-style:italic; }

/* Tagline */
.tagline-text { font-size:1.4rem; font-weight:700; color:#1E293B; line-height:1.4; }

/* Social badges */
.badge { display:inline-block; font-size:.68rem; font-weight:600; text-transform:uppercase; letter-spacing:.07em; padding:2px 9px; border-radius:20px; margin-bottom:5px; }
.badge-tw { background:#E0F2FE; color:#0369A1; }
.badge-ig { background:#FDF2F8; color:#9D174D; }
.badge-li { background:#EFF6FF; color:#1D4ED8; }
.social-block { margin-bottom:.9rem; padding-bottom:.9rem; border-bottom:1px solid #F1F5F9; }
.social-block:last-child { border-bottom:none; margin-bottom:0; padding-bottom:0; }

/* Script box */
.script-box { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:.85rem 1rem; font-size:.88rem; color:#334155; line-height:1.7; font-style:italic; }

/* Sidebar */
[data-testid="stSidebar"] { background:#FAFAFA; border-right:1px solid #F1F5F9; }
.sidebar-brand { font-size:1.1rem; font-weight:700; color:#1E293B; }
.sidebar-sub   { font-size:.78rem; color:#94A3B8; margin-bottom:1rem; }

/* Generate button */
div[data-testid="stButton"] > button {
    width:100%; padding:.75rem 1rem;
    background:linear-gradient(135deg,#6366F1,#8B5CF6);
    color:white !important; font-weight:600; font-size:.92rem;
    border:none; border-radius:10px; cursor:pointer;
    box-shadow:0 4px 14px rgba(99,102,241,.35);
    transition: opacity .15s;
}
div[data-testid="stButton"] > button:hover    { opacity:.88; }
div[data-testid="stButton"] > button:disabled { opacity:.5; cursor:not-allowed; }

/* Progress bar */
.stProgress > div > div > div > div { background:linear-gradient(135deg,#6366F1,#8B5CF6); }

/* Error */
.err { background:#FFF1F2; border:1px solid #FECDD3; border-radius:10px; padding:.85rem 1rem; color:#BE123C; font-size:.87rem; margin-bottom:.75rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
DEFAULTS = {
    "tagline":      None,
    "blog_intro":   None,
    "social_posts": None,
    "hero_path":    None,
    "audio_path":   None,
    "audio_script": None,
    "video_path":   None,
    "errors":       [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚡ AI Content Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Fill in the brief and generate five assets.</div>', unsafe_allow_html=True)
    st.divider()

    product  = st.text_input("🏷️ Product / Brand Name", placeholder="e.g. NovaBrew Coffee")
    audience = st.text_input("🎯 Target Audience",       placeholder="e.g. Remote workers 25–40")
    tone     = st.selectbox("🎨 Brand Tone", ["Playful", "Premium", "Eco", "Modern"])

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Campaign", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Text & Image & Audio → OpenAI\nVideo → OpenRouter (Wan 2.6)")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-title">AI <span class="accent">Content Engine</span></div>
<div class="hero-sub">One Brief In &nbsp;→&nbsp; Five Creative Assets Out</div>
""", unsafe_allow_html=True)

# ── Card render helpers ────────────────────────────────────────────────────────

def plain_card(title: str, body_html: str, placeholder: str = "Waiting for generation…"):
    body = body_html if body_html else f'<span class="card-placeholder">{placeholder}</span>'
    st.markdown(
        f'<div class="card"><div class="card-title">{title}</div>'
        f'<div class="card-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def tagline_card(tagline):
    body = (f'<div class="tagline-text">"{tagline}"</div>'
            if tagline else '<span class="card-placeholder">Your tagline will appear here…</span>')
    st.markdown(
        f'<div class="card"><div class="card-title">💡 Campaign Tagline</div>'
        f'<div class="card-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def social_card(posts):
    if not posts:
        plain_card("📲 Social Media Posts", "", "Twitter · Instagram · LinkedIn posts will appear here…")
        return

    def block(cls, label, text):
        safe = (text or "").replace("\n", "<br>")
        return (f'<div class="social-block">'
                f'<span class="badge {cls}">{label}</span>'
                f'<div style="font-size:.9rem;color:#1E293B;line-height:1.65">{safe}</div>'
                f'</div>')

    inner = (block("badge-tw", "𝕏 Twitter",    posts.get("twitter",   ""))
           + block("badge-ig", "📸 Instagram",  posts.get("instagram", ""))
           + block("badge-li", "💼 LinkedIn",   posts.get("linkedin",  "")))
    st.markdown(
        f'<div class="card"><div class="card-title">📲 Social Media Posts</div>'
        f'<div class="card-body">{inner}</div></div>',
        unsafe_allow_html=True,
    )


def err_card(msg: str):
    st.markdown(f'<div class="err">⚠️ {msg}</div>', unsafe_allow_html=True)

# ── Two-column layout ──────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="section-header">📝 Text Assets</div>', unsafe_allow_html=True)

    tagline_card(st.session_state.tagline)

    blog_html = (st.session_state.blog_intro.replace("\n", "<br>")
                 if st.session_state.blog_intro else "")
    plain_card("📰 Blog Introduction", blog_html, "200-word blog intro will appear here…")

    social_card(st.session_state.social_posts)

with right:
    st.markdown('<div class="section-header">🎨 Visual & Audio Assets</div>', unsafe_allow_html=True)

    # ── Hero Image ─────────────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🎨 Hero Image</div>', unsafe_allow_html=True)
    if st.session_state.hero_path and Path(st.session_state.hero_path).exists():
        st.image(str(st.session_state.hero_path), use_column_width=True)
    else:
        st.markdown(
            '<div class="card-body"><span class="card-placeholder">'
            'AI-generated hero image will appear here…</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Audio Voiceover ────────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🔊 Audio Voiceover (30s Ad)</div>', unsafe_allow_html=True)
    if st.session_state.audio_path and Path(st.session_state.audio_path).exists():
        st.audio(str(st.session_state.audio_path), format="audio/mp3")
        if st.session_state.audio_script:
            st.markdown(
                f'<div class="script-box">📄 Script: {st.session_state.audio_script}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="card-body"><span class="card-placeholder">'
            'AI-generated voiceover audio will appear here…</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Promotional Video ──────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">🎬 Promotional Video</div>', unsafe_allow_html=True)
    if st.session_state.video_path and Path(st.session_state.video_path).exists():
        st.video(str(st.session_state.video_path))
        st.caption(f"Generated with Wan 2.6 via OpenRouter")
    else:
        st.markdown(
            '<div class="card-body"><span class="card-placeholder">'
            'AI-generated promo video will appear here… (takes 1–3 min)</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Errors ─────────────────────────────────────────────────────────────────────
for err in st.session_state.errors:
    err_card(err)

# ── Generation pipeline ────────────────────────────────────────────────────────
if generate_btn:
    if not product.strip():
        st.warning("Please enter a Product / Brand Name.", icon="⚠️"); st.stop()
    if not audience.strip():
        st.warning("Please enter a Target Audience.", icon="⚠️"); st.stop()

    # Reset previous results
    for k in DEFAULTS:
        st.session_state[k] = DEFAULTS[k]

    bar    = st.progress(0)
    status = st.empty()

    def step(pct: int, msg: str):
        bar.progress(pct)
        status.markdown(f"⏳ **{msg}**")

    try:
        from text_gen  import generate_tagline, generate_blog_intro, generate_social_posts
        from image_gen import generate_hero_image
        from audio_gen import generate_voiceover
        from video_gen import generate_promo_video

        # Step 1 — Tagline (OpenAI)
        step(8, "Crafting your campaign tagline…")
        tagline = generate_tagline(product, audience, tone)
        st.session_state.tagline = tagline

        # Step 2 — Blog intro (OpenAI)
        step(22, "Writing the blog introduction…")
        st.session_state.blog_intro = generate_blog_intro(product, audience, tone, tagline)

        # Step 3 — Social posts (OpenAI)
        step(36, "Generating social media posts…")
        st.session_state.social_posts = generate_social_posts(product, audience, tone, tagline)

        # Step 4 — Hero image (OpenAI DALL-E 3)
        step(50, "Generating hero image with DALL-E 3…")
        try:
            st.session_state.hero_path = generate_hero_image(product, audience, tone, tagline)
        except RuntimeError as e:
            st.session_state.errors.append(str(e))

        # Step 5 — Voiceover audio (OpenAI TTS)
        step(65, "Generating voiceover audio…")
        try:
            audio_path, script = generate_voiceover(product, audience, tone, tagline)
            st.session_state.audio_path   = audio_path
            st.session_state.audio_script = script
        except RuntimeError as e:
            st.session_state.errors.append(str(e))

        # Step 6 — Promo video (OpenRouter Wan 2.6) — async, takes longest
        video_info = st.empty()
        step(78, "Submitting video job to OpenRouter (Wan 2.6)…")

        def video_cb(msg: str):
            video_info.info(f"🎬 {msg}")

        try:
            video_path = generate_promo_video(product, audience, tone, tagline, status_callback=video_cb)
            st.session_state.video_path = video_path
            video_info.empty()
        except RuntimeError as e:
            st.session_state.errors.append(str(e))
            video_info.empty()

        # Done
        step(100, "All assets generated!")
        status.success("✅ Campaign generated successfully!")
        bar.empty()
        st.rerun()

    except RuntimeError as e:
        bar.empty(); status.empty()
        st.error(f"Generation failed: {e}", icon="🚫")
    except Exception as e:
        bar.empty(); status.empty()
        st.error(f"Unexpected error: {e}", icon="🚫")