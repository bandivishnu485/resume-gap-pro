"""Page 4 — Multi-JD Comparator."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.resume_parser import ResumeParser
from pipeline.skill_extractor import SkillExtractor
from pipeline.gap_analyzer import GapAnalyzer

st.set_page_config(page_title="Compare JDs — Resume Gap Pro", page_icon="⚖️", layout="wide")

from app import _defaults
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
body,.stApp{background:#08080c!important;}
.main .block-container{padding-top:0!important;max-width:1280px!important;}
section[data-testid="stSidebar"]{background:#0e0e16!important;border-right:1px solid #1e1e2e!important;}
section[data-testid="stSidebar"] .stMarkdown *{color:#4a4a6a!important;}
.stButton>button{font-weight:600!important;border-radius:10px!important;transition:all .2s!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#7c6af7,#a78bfa)!important;border:none!important;color:white!important;box-shadow:0 4px 20px rgba(124,106,247,.4)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;}
.stButton>button[kind="secondary"]{background:#12121c!important;border:1px solid #252538!important;color:#94a3b8!important;}
div[data-testid="metric-container"]{background:#12121c!important;border:1px solid #252538!important;border-radius:14px!important;padding:16px!important;transition:all .2s;}
div[data-testid="metric-container"]:hover{border-color:#7c6af7!important;transform:translateY(-2px);}
.stTextArea textarea,.stTextInput input{background:#12121c!important;border:1px solid #252538!important;border-radius:9px!important;color:#f0f0f8!important;}
.stTextArea label,.stTextInput label{color:#6b6b8a!important;}
.streamlit-expanderHeader{background:#12121c!important;border:1px solid #252538!important;border-radius:10px!important;color:#94a3b8!important;font-weight:600!important;}
[data-testid="stFileUploader"] section{border:2px dashed #252538!important;border-radius:14px!important;background:#12121c!important;}
[data-testid="stFileUploader"] section:hover{border-color:#7c6af7!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden;}
.stAlert{border-radius:10px!important;}
hr{border-color:#1e1e2e!important;}
h1,h2,h3{color:#f0f0f8!important;}
</style>
""", unsafe_allow_html=True)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#08080c,#0e0814);border-bottom:1px solid #1e1e2e;
     padding:40px 0 32px;margin:0 -4rem 32px;'>
  <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#22d3ee;margin-bottom:8px;'>Strategy</div>
  <h1 style='font-size:2.4rem;font-weight:800;color:#f0f0f8;letter-spacing:-1px;margin:0 0 8px;'>
    Multi-JD Comparator
  </h1>
  <p style='font-size:0.9rem;color:#6b6b8a;margin:0;'>
    Compare up to 5 job descriptions against your resume to find where you're most competitive right now.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Resume status ──────────────────────────────────────────────────────────────
resume_text   = st.session_state.get("resume_text", "")
resume_skills = st.session_state.get("resume_skills", {})

if not resume_text:
    st.markdown("""
    <div style='background:#12121c;border:1px solid #252538;border-radius:12px;padding:18px 20px;margin-bottom:16px;'>
      <div style='font-size:0.82rem;color:#6b6b8a;'>No resume in session — upload one below, or run Gap Analysis first.</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"], key="cmp_resume")
    if uploaded:
        parser = ResumeParser()
        raw = parser.extract_text(uploaded.read())
        clean = parser.clean_text(raw)
        secs = parser.extract_sections(clean)
        ext = SkillExtractor()
        resume_skills = ext.extract_from_resume(secs)
        st.session_state.resume_text, st.session_state.resume_skills, st.session_state.sections = clean, resume_skills, secs
        st.success("✅ Resume loaded!")
        st.rerun()
else:
    skill_count = len(resume_skills.get("all", []))
    st.markdown(f"""
    <div style='background:#052e16;border:1px solid #166534;border-radius:10px;padding:10px 16px;margin-bottom:16px;display:flex;justify-content:space-between;'>
      <span style='color:#4ade80;font-size:0.82rem;font-weight:600;'>✅ Resume loaded</span>
      <span style='color:#166534;font-size:0.78rem;'>{len(resume_text.split())} words · {skill_count} skills detected</span>
    </div>
    """, unsafe_allow_html=True)

if not resume_skills.get("all"):
    st.stop()

# ── JD inputs ──────────────────────────────────────────────────────────────────
st.markdown("<h3 style='color:#f0f0f8;margin-bottom:14px;'>📋 Add Job Descriptions</h3>", unsafe_allow_html=True)
if "jd_count" not in st.session_state:
    st.session_state.jd_count = 2

jds_data = []
for i in range(st.session_state.jd_count):
    with st.expander(f"📄 JD #{i+1}", expanded=i < 2):
        col_name, col_jd = st.columns([1, 3])
        with col_name:
            rn = st.text_input("Role Title", key=f"rn_{i}", placeholder="e.g. ML Engineer")
        with col_jd:
            jt = st.text_area("Job Description", height=130, key=f"jt_{i}", placeholder="Paste full JD...")
        if jt and rn:
            jds_data.append({"role_name": rn, "jd_text": jt})

col_add, col_go = st.columns([1, 3])
with col_add:
    if st.session_state.jd_count < 5:
        if st.button("➕ Add JD", use_container_width=True):
            st.session_state.jd_count = min(5, st.session_state.jd_count + 1)
            st.rerun()
with col_go:
    go_btn = st.button("⚖️  Compare All JDs", type="primary", use_container_width=True, key="cmp_btn")

if go_btn:
    if len(jds_data) < 2:
        st.warning("Fill in at least 2 JDs with role names.")
        st.stop()
    with st.spinner("Comparing..."):
        ext = SkillExtractor()
        ana = GapAnalyzer()
        processed = [{"role_name": j["role_name"], "jd_data": ext.extract_from_jd(j["jd_text"])} for j in jds_data]
        results = ana.compare_multiple_jds(resume_skills, processed)
        st.session_state["cmp_results"] = results

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.get("cmp_results"):
    results = st.session_state["cmp_results"]
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Rank cards
    st.markdown("<h3 style='color:#f0f0f8;margin-bottom:16px;'>🏆 Ranked Results</h3>", unsafe_allow_html=True)
    rank_colors = ["#fbbf24", "#94a3b8", "#f97316"]
    rank_labels = ["Apply Now", "Short-Term Prep", "Medium-Term Target"]
    for i, r in enumerate(results[:5]):
        score = r.get("match_score", 0)
        s_color = "#4ade80" if score >= 70 else "#fbbf24" if score >= 45 else "#f87171"
        rc = rank_colors[min(i, 2)]
        gaps_str = ", ".join(r.get("critical_gaps", [])[:3]) or "None"
        st.markdown(f"""
        <div style='background:#0e0e16;border:1px solid #1e1e2e;border-left:3px solid {rc};
             border-radius:12px;padding:16px 20px;margin-bottom:10px;
             display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;'>
          <div style='display:flex;align-items:center;gap:16px;'>
            <div style='font-size:1.4rem;font-weight:900;color:{rc};min-width:28px;'>#{i+1}</div>
            <div>
              <div style='font-size:0.95rem;font-weight:700;color:#e2e8f0;'>{r.get('role_name','')}</div>
              <div style='font-size:0.75rem;color:#4a4a6a;margin-top:2px;'>Gaps: {gaps_str[:50]}</div>
            </div>
          </div>
          <div style='display:flex;align-items:center;gap:16px;'>
            <div style='text-align:right;'>
              <div style='font-size:1.6rem;font-weight:900;color:{s_color};'>{int(score)}%</div>
              <div style='font-size:0.68rem;color:#4a4a6a;'>match</div>
            </div>
            <div style='background:{rc}20;border:1px solid {rc}60;color:{rc};padding:4px 12px;
                 border-radius:99px;font-size:0.72rem;font-weight:700;white-space:nowrap;'>
              {rank_labels[min(i,2)]}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chart
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    roles = [r.get("role_name", f"Role {i+1}") for i, r in enumerate(results)]
    scores = [r.get("match_score", 0) for r in results]
    bar_colors = ["#4ade80" if s >= 70 else "#fbbf24" if s >= 45 else "#f87171" for s in scores]

    fig = go.Figure(go.Bar(x=roles, y=scores, marker_color=bar_colors,
                           text=[f"{int(s)}%" for s in scores], textposition="outside",
                           textfont=dict(color="#94a3b8", size=12)))
    fig.update_layout(plot_bgcolor="#08080c", paper_bgcolor="#08080c", height=280,
                      margin=dict(t=20, b=20, l=0, r=0),
                      xaxis=dict(tickfont=dict(color="#6b6b8a"), gridcolor="#1e1e2e"),
                      yaxis=dict(tickfont=dict(color="#6b6b8a"), gridcolor="#1e1e2e", range=[0,105]))
    st.plotly_chart(fig, use_container_width=True)

    # Overlap analysis
    all_gap_sets = [set(r.get("critical_gaps", [])) for r in results]
    if len(all_gap_sets) >= 2:
        common = set.intersection(*all_gap_sets)
        if common:
            tags = "".join(f"<span style='background:#0e0e16;border:1px solid #252538;color:#fbbf24;padding:3px 10px;border-radius:99px;font-size:0.75rem;margin:2px;display:inline-block;'>{g.title()}</span>" for g in common)
            st.markdown(f"""
            <div style='background:#150a01;border:1px solid #78350f;border-radius:12px;padding:16px 20px;margin-top:8px;'>
              <div style='font-size:0.78rem;font-weight:700;color:#fbbf24;margin-bottom:8px;'>
                📌 Universal Gaps — learn these to boost ALL your applications
              </div>
              <div>{tags}</div>
            </div>
            """, unsafe_allow_html=True)
        all_matched = [set(r.get("matched_skills", [])) for r in results]
        common_m = set.intersection(*all_matched) if all_matched else set()
        if common_m:
            tags_m = "".join(f"<span style='background:#052e16;border:1px solid #166534;color:#4ade80;padding:3px 10px;border-radius:99px;font-size:0.75rem;margin:2px;display:inline-block;'>{g.title()}</span>" for g in common_m)
            st.markdown(f"""
            <div style='background:#052e16;border:1px solid #166534;border-radius:12px;padding:16px 20px;margin-top:8px;'>
              <div style='font-size:0.78rem;font-weight:700;color:#4ade80;margin-bottom:8px;'>
                ✅ Strengths across all roles — these are your core selling points
              </div>
              <div>{tags_m}</div>
            </div>
            """, unsafe_allow_html=True)
