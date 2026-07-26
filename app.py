"""
Resume Gap Pro — Main Streamlit Navigation Shell.
Premium dark editorial design with Syne + DM Sans typography.
"""
import os
import warnings
warnings.filterwarnings("ignore")
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass
import streamlit as st

st.set_page_config(
    page_title="Resume Gap Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/resume-gap-pro",
        "Report a bug": "https://github.com/resume-gap-pro/issues",
        "About": "Resume Gap Pro — AI-Powered Career Gap Analyser for Indian Placements",
    },
)

# ─── Session State ────────────────────────────────────────────────────────────
_defaults = {
    "analysis": None, "resume_text": "", "sections": {}, "jd_text": "",
    "role_title": "", "roadmap": "", "lang": "English", "history": [],
    "resume_skills": {}, "jd_data": {}, "ats_result": {}, "section_scores": {},
    "salary_data": {}, "peer_data": {}, "retrieved_courses": {},
    "format_issues": [], "company": None, "interview_date": None,
    "interview_session": None, "interview_performance": [],
    "interview_phase": "asking", "last_result": None,
    "rewritten_resume": {}, "cover_letter_text": "", "linkedin_data": {},
}
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

:root {
  --bg: #08080c;
  --surface: #0e0e16;
  --surface2: #12121c;
  --border: #1e1e2e;
  --border2: #252538;
  --text: #f0f0f8;
  --muted: #6b6b8a;
  --accent: #7c6af7;
  --accent2: #a78bfa;
  --cyan: #22d3ee;
  --green: #4ade80;
  --amber: #fbbf24;
  --red: #f87171;
  --pink: #f472b6;
}

* { box-sizing: border-box; }

body, .stApp { background: var(--bg) !important; }
.main .block-container {
  padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 1280px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--surface) !important; border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown div { color: #6b6b8a !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div {
  background: var(--surface2) !important; border-color: var(--border2) !important; color: #94a3b8 !important;
}
section[data-testid="stSidebar"] .stSelectbox label { color: #4a4a6a !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

/* Buttons */
.stButton > button {
  font-weight: 600 !important; border-radius: 10px !important;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #7c6af7, #a78bfa) !important;
  border: none !important; color: white !important;
  box-shadow: 0 4px 20px rgba(124,106,247,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-3px) !important; box-shadow: 0 10px 30px rgba(124,106,247,0.55) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--surface2) !important; border: 1px solid var(--border2) !important; color: #94a3b8 !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--accent) !important; color: var(--accent2) !important; }

/* Metric cards */
div[data-testid="metric-container"] {
  background: var(--surface2) !important; border: 1px solid var(--border2) !important;
  border-radius: 14px !important; padding: 18px !important;
  box-shadow: 0 2px 16px rgba(0,0,0,0.35); transition: all 0.25s ease;
}
div[data-testid="metric-container"]:hover {
  border-color: var(--accent) !important; box-shadow: 0 8px 28px rgba(124,106,247,0.2) !important;
  transform: translateY(-2px);
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-size: 1.8rem !important; font-weight: 800 !important; color: var(--text) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
  font-size: 0.75rem !important; color: var(--muted) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px; background: var(--surface2); border-radius: 12px; padding: 5px; border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important; padding: 8px 16px; font-size: 12.5px !important;
  font-weight: 500; border: none !important; color: var(--muted) !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface) !important; border: 1px solid var(--border2) !important;
  color: var(--accent2) !important; font-weight: 600 !important;
}

/* File uploader */
[data-testid="stFileUploader"] section {
  border: 2px dashed var(--border2) !important; border-radius: 14px !important;
  background: var(--surface2) !important; transition: all 0.2s;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploader"] span { color: #4a4a6a !important; }

/* Text areas */
.stTextArea textarea {
  border-radius: 10px !important; background: var(--surface2) !important;
  border: 1px solid var(--border2) !important; color: var(--text) !important;
}
.stTextArea textarea:focus {
  border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(124,106,247,0.15) !important;
}
.stTextArea label, .stTextInput label, .stSelectbox label { color: #6b6b8a !important; }

/* Text inputs */
.stTextInput input {
  background: var(--surface2) !important; border: 1px solid var(--border2) !important;
  border-radius: 9px !important; color: var(--text) !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; }

/* Progress */
.stProgress > div > div { border-radius: 99px !important; background: var(--surface2) !important; }
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--cyan)) !important; border-radius: 99px !important;
}

/* Pills */
.skill-pill { display:inline-block; padding:4px 13px; border-radius:20px; font-size:12px; font-weight:600; margin:3px 2px; }
.pill-green  { background:#05140d; color:#4ade80; border:1px solid #166534; }
.pill-red    { background:#150505; color:#f87171; border:1px solid #7f1d1d; }
.pill-amber  { background:#150a01; color:#fbbf24; border:1px solid #78350f; }
.pill-blue   { background:#040d1e; color:#93c5fd; border:1px solid #1e3a8a; }
.pill-purple { background:#0f0525; color:#c4b5fd; border:1px solid #4c1d95; }

/* Score circle */
.score-circle { width:150px; height:150px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; flex-direction:column; font-size:2.4rem; font-weight:900; margin:0 auto 12px; }
.score-green { background:linear-gradient(135deg,#22c55e,#16a34a); color:#fff; box-shadow:0 8px 32px rgba(34,197,94,0.4); }
.score-amber { background:linear-gradient(135deg,#f59e0b,#d97706); color:#fff; box-shadow:0 8px 32px rgba(245,158,11,0.4); }
.score-red   { background:linear-gradient(135deg,#ef4444,#dc2626); color:#fff; box-shadow:0 8px 32px rgba(239,68,68,0.4); }

/* Expanders */
.streamlit-expanderHeader {
  font-weight: 600 !important; background: var(--surface2) !important;
  border-radius: 10px !important; color: #94a3b8 !important; border: 1px solid var(--border2) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; }
.stAlert { border-radius: 10px !important; }
[data-testid="stStatus"] { border-radius: 12px !important; background: var(--surface2) !important; border-color: var(--border2) !important; }

/* Headings */
h1, h2, h3, h4 { color: var(--text) !important; }
hr { border-color: var(--border) !important; margin: 20px 0 !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:24px 16px 16px; border-bottom:1px solid #1e1e2e; margin-bottom:8px;'>
      <div style='display:flex;align-items:center;gap:10px;'>
        <span style='font-size:1.5rem;'>🎯</span>
        <div>
          <div style='font-size:1rem;font-weight:800;color:#f0f0f8;letter-spacing:-0.3px;'>Resume Gap Pro</div>
          <div style='font-size:0.67rem;color:#3a3a5c;'>AI Career Coaching</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#2a2a3e;padding:4px;margin-bottom:4px;'>Navigation</p>", unsafe_allow_html=True)
    for icon, label in [("🔍","Gap Analysis"),("✍️","Resume Rewriter"),("🎤","Mock Interview"),("⚖️","Compare JDs"),("👥","Team Analyser"),("📊","Dashboard")]:
        st.markdown(f"<div style='padding:7px 10px;border-radius:7px;color:#5a5a7a;font-size:0.82rem;margin-bottom:2px;'>• {icon} {label}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    lang = st.selectbox(
        "🌐 Output Language",
        ["English","Hindi","Telugu","Tamil","Kannada","Bengali"],
        index=["English","Hindi","Telugu","Tamil","Kannada","Bengali"].index(st.session_state.lang),
        key="lang_selector",
    )
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()

    with st.expander("🔑 Gemini API Key"):
        curr_key = os.getenv("GOOGLE_API_KEY", "")
        sb_key = st.text_input("API Key", value=curr_key, type="password", key="sidebar_key_input", placeholder="AIzaSy...")
        if st.button("Save Key", key="save_sb_key"):
            os.environ["GOOGLE_API_KEY"] = sb_key.strip()
            st.success("API Key saved for session!")
            st.rerun()

    with st.expander("ℹ️ How it works"):
        st.markdown("**1 — Upload & Paste** Resume PDF + JD\n\n**2 — AI Runs** RAG extracts gaps, scores\n\n**3 — Your Plan** Roadmap + interview prep")

    st.markdown("<div style='font-size:0.65rem;color:#2a2a3e;text-align:center;padding-top:8px;border-top:1px solid #1e1e2e;margin-top:6px;'>Streamlit · Gemini · FAISS · spaCy<br>© 2024 Resume Gap Pro</div>", unsafe_allow_html=True)

    if st.session_state.analysis:
        score = st.session_state.analysis.get("match_score", 0)
        color = "#4ade80" if score >= 70 else "#fbbf24" if score >= 40 else "#f87171"
        st.markdown(f"""<div style='margin-top:12px;background:#12121c;border:1px solid #252538;border-radius:12px;padding:14px;text-align:center;'>
          <div style='font-size:0.65rem;color:#3a3a5c;margin-bottom:4px;'>LAST ANALYSIS</div>
          <div style='font-size:2rem;font-weight:900;color:{color};'>{int(score)}%</div>
          <div style='font-size:0.7rem;color:#4a4a6a;'>{st.session_state.role_title or "—"}</div>
        </div>""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#08080c 0%,#0e0814 45%,#08080c 100%);
     border-bottom:1px solid #1e1e2e;padding:72px 24px 60px;margin:0 -4rem;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-100px;left:-100px;width:500px;height:500px;
       background:radial-gradient(circle,rgba(124,106,247,0.1) 0%,transparent 70%);pointer-events:none;'></div>
  <div style='position:absolute;top:0;right:-80px;width:360px;height:360px;
       background:radial-gradient(circle,rgba(34,211,238,0.06) 0%,transparent 70%);pointer-events:none;'></div>
  <div style='max-width:860px;margin:0 auto;position:relative;z-index:1;'>
    <div style='display:inline-flex;align-items:center;gap:8px;background:rgba(124,106,247,0.1);
         border:1px solid rgba(124,106,247,0.25);padding:5px 16px;border-radius:99px;margin-bottom:26px;'>
      <span style='width:7px;height:7px;border-radius:50%;background:#7c6af7;
           animation:pulse-dot 2s infinite;display:inline-block;'></span>
      <span style='font-size:0.7rem;font-weight:700;color:#a78bfa;letter-spacing:1px;text-transform:uppercase;'>
        AI-Powered · RAG · Real-time
      </span>
    </div>
    <h1 style='font-size:4rem;font-weight:800;color:#f0f0f8;letter-spacing:-2px;line-height:1.05;margin:0 0 16px;'>
      Know Exactly<br>
      <span style='background:linear-gradient(135deg,#7c6af7,#22d3ee);-webkit-background-clip:text;
           -webkit-text-fill-color:transparent;background-clip:text;'>Where You Stand.</span>
    </h1>
    <p style='font-size:1.05rem;color:#6b6b8a;max-width:500px;line-height:1.8;margin-bottom:36px;'>
      Upload your resume, paste a JD — get a complete AI gap analysis with
      personalised roadmap, ATS score, salary estimate, and mock interview.
      Built for <strong style='color:#94a3b8;'>Indian placement season</strong>.
    </p>
    <div style='display:flex;gap:36px;flex-wrap:wrap;'>
      <div><div style='font-size:1.9rem;font-weight:900;color:#7c6af7;'>20</div><div style='font-size:0.73rem;color:#3a3a5c;'>AI features</div></div>
      <div><div style='font-size:1.9rem;font-weight:900;color:#22d3ee;'>60+</div><div style='font-size:0.73rem;color:#3a3a5c;'>Free courses</div></div>
      <div><div style='font-size:1.9rem;font-weight:900;color:#4ade80;'>800+</div><div style='font-size:0.73rem;color:#3a3a5c;'>Peer profiles</div></div>
      <div><div style='font-size:1.9rem;font-weight:900;color:#f472b6;'>Free</div><div style='font-size:0.73rem;color:#3a3a5c;'>API tier works</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── CTA + Feature cards ──────────────────────────────────────────────────────
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

cta_col, cards_col = st.columns([1, 2], gap="large")
with cta_col:
    st.markdown("""
    <h3 style='font-size:1.1rem;color:#f0f0f8;margin-bottom:8px;'>Ready to find your gaps?</h3>
    <p style='font-size:0.82rem;color:#4a4a6a;margin-bottom:18px;'>Takes 30–60 seconds. No account needed.</p>
    """, unsafe_allow_html=True)
    if st.button("🔍  Start Gap Analysis  →", type="primary", use_container_width=True):
        st.switch_page("pages/01_analysis.py")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("📊  Placement Dashboard", use_container_width=True):
        st.switch_page("pages/06_dashboard.py")

with cards_col:
    features = [
        ("🔍","#7c6af7","Gap Analysis","Maps your skills vs JD with semantic AI"),
        ("🗺️","#22d3ee","RAG Roadmap","Week plans using 60+ real free courses"),
        ("🎤","#f472b6","Mock Interview","Adaptive AI on your exact gaps"),
        ("🤖","#4ade80","ATS Scorer","Keyword density + format checks"),
        ("💰","#fbbf24","Salary Estimate","LPA range: now vs after upskilling"),
        ("📊","#a78bfa","Peer Rank","Percentile vs 800+ peers same role"),
        ("⚖️","#22d3ee","Multi-JD Compare","Find your best-fit role fast"),
        ("👥","#4ade80","Team Analyser","Skill heatmap + role assignment"),
    ]
    row1 = features[:4]
    row2 = features[4:]
    for row in [row1, row2]:
        cols = st.columns(4)
        for col, (icon, color, title, desc) in zip(cols, row):
            with col:
                st.markdown(f"""<div style='background:#0e0e16;border:1px solid #1e1e2e;border-radius:12px;
                     padding:15px 13px;height:116px;position:relative;overflow:hidden;'>
                  <div style='position:absolute;top:-18px;right:-18px;width:60px;height:60px;
                       border-radius:50%;background:{color}15;'></div>
                  <div style='font-size:1.3rem;margin-bottom:7px;'>{icon}</div>
                  <div style='font-size:0.8rem;font-weight:700;color:#e2e8f0;margin-bottom:3px;'>{title}</div>
                  <div style='font-size:0.71rem;color:#3a3a5c;line-height:1.4;'>{desc}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─── How it works ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='background:#0e0e16;border:1px solid #1e1e2e;border-radius:16px;padding:28px 32px;'>
  <p style='font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#2a2a3e;margin-bottom:20px;'>How it works</p>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;'>
    <div style='padding:0 24px 0 0;border-right:1px solid #1e1e2e;'>
      <div style='font-size:2.2rem;font-weight:900;color:#1e1e2e;margin-bottom:8px;'>01</div>
      <div style='font-size:0.86rem;font-weight:600;color:#cbd5e1;margin-bottom:6px;'>Upload &amp; Paste</div>
      <div style='font-size:0.78rem;color:#3a3a5c;line-height:1.65;'>Drop your resume PDF and paste the full JD. The more complete the JD, the sharper the analysis.</div>
    </div>
    <div style='padding:0 24px;border-right:1px solid #1e1e2e;'>
      <div style='font-size:2.2rem;font-weight:900;color:#1e1e2e;margin-bottom:8px;'>02</div>
      <div style='font-size:0.86rem;font-weight:600;color:#cbd5e1;margin-bottom:6px;'>AI Pipeline Runs</div>
      <div style='font-size:0.78rem;color:#3a3a5c;line-height:1.65;'>spaCy NLP + FAISS hybrid RAG extracts skills, computes gaps, scores ATS compatibility, retrieves courses.</div>
    </div>
    <div style='padding:0 0 0 24px;'>
      <div style='font-size:2.2rem;font-weight:900;color:#1e1e2e;margin-bottom:8px;'>03</div>
      <div style='font-size:0.86rem;font-weight:600;color:#cbd5e1;margin-bottom:6px;'>Get Your Plan</div>
      <div style='font-size:0.78rem;color:#3a3a5c;line-height:1.65;'>Gemini 1.5 Flash generates a personalised roadmap. Export to calendar, practice in adaptive mock interview.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
