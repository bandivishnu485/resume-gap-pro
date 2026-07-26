"""Page 5 — Team Gap Analyser."""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.resume_parser import ResumeParser
from pipeline.skill_extractor import SkillExtractor
from pipeline.gap_analyzer import GapAnalyzer

st.set_page_config(page_title="Team Analyser — Resume Gap Pro", page_icon="👥", layout="wide")

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
div[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#f0f0f8!important;font-size:1.7rem!important;font-weight:800!important;}
div[data-testid="metric-container"] [data-testid="stMetricLabel"]{color:#6b6b8a!important;}
.stTextArea textarea,.stTextInput input{background:#12121c!important;border:1px solid #252538!important;border-radius:9px!important;color:#f0f0f8!important;}
.stTextArea label,.stTextInput label{color:#6b6b8a!important;}
[data-testid="stFileUploader"] section{border:2px dashed #252538!important;border-radius:14px!important;background:#12121c!important;}
[data-testid="stFileUploader"] section:hover{border-color:#7c6af7!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden;}
.stAlert{border-radius:10px!important;}
hr{border-color:#1e1e2e!important;}
h1,h2,h3{color:#f0f0f8!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background:linear-gradient(135deg,#08080c,#0e0814);border-bottom:1px solid #1e1e2e;
     padding:40px 0 32px;margin:0 -4rem 32px;'>
  <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4ade80;margin-bottom:8px;'>Collaboration</div>
  <h1 style='font-size:2.4rem;font-weight:800;color:#f0f0f8;letter-spacing:-1px;margin:0 0 8px;'>Team Gap Analyser</h1>
  <p style='font-size:0.9rem;color:#6b6b8a;margin:0;'>Upload 2–6 resumes to visualise team skill coverage, identify gaps nobody covers, and suggest role assignments.</p>
</div>
""", unsafe_allow_html=True)

# ── Inputs ─────────────────────────────────────────────────────────────────────
uploaded_files = st.file_uploader("📁 Upload Team Resumes (2–6 PDFs)", type=["pdf"],
                                   accept_multiple_files=True, key="team_resumes")
names_inputs = []
if uploaded_files:
    name_cols = st.columns(min(len(uploaded_files), 3))
    for i, f in enumerate(uploaded_files):
        with name_cols[i % 3]:
            n = st.text_input(f"Name for file {i+1}", value=f.name.replace(".pdf",""), key=f"tn_{i}")
            names_inputs.append(n)

jd_text = st.text_area("📋 Target Project / Role Description", height=150,
                        placeholder="Paste the project requirements and tech stack...", key="team_jd")
analyse_btn = st.button("🔍  Analyse Team", type="primary", use_container_width=True, key="team_btn")

if analyse_btn:
    if not uploaded_files or len(uploaded_files) < 2:
        st.error("Upload at least 2 resumes.")
        st.stop()
    if not jd_text or len(jd_text.split()) < 20:
        st.warning("Paste a more detailed project description for accurate results.")

    parser = ResumeParser(); ext = SkillExtractor(); ana = GapAnalyzer()
    jd_data = ext.extract_from_jd(jd_text)
    required_skills = jd_data.get("required_skills", [])
    team_data = []

    with st.spinner(f"Analysing {len(uploaded_files)} team members..."):
        for i, f in enumerate(uploaded_files):
            try:
                raw = parser.extract_text(f.read())
                clean = parser.clean_text(raw)
                secs = parser.extract_sections(clean)
                skills = ext.extract_from_resume(secs)
                gap = ana.compute_gaps(skills, jd_data)
                team_data.append({"name": names_inputs[i] if i < len(names_inputs) else f"Member {i+1}",
                                  "skills": skills, "gap_result": gap})
            except Exception as e:
                st.warning(f"Could not process {f.name}: {e}")

    st.session_state["team_data"] = team_data
    st.session_state["team_req_skills"] = required_skills

if st.session_state.get("team_data"):
    team_data = st.session_state["team_data"]
    required_skills = st.session_state.get("team_req_skills", [])
    scores = [t["gap_result"]["match_score"] for t in team_data]
    avg_score = sum(scores) / len(scores)

    # Metrics
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Team Size", len(team_data))
    m2.metric("📊 Avg Match", f"{avg_score:.1f}%")
    m3.metric("✅ Ready (>70%)", sum(1 for s in scores if s >= 70))
    m4.metric("⚡ Needs Prep", sum(1 for s in scores if s < 70))

    # Heatmap
    if required_skills:
        st.markdown("<h3 style='margin:24px 0 12px;'>🗺️ Skill Coverage Heatmap</h3>", unsafe_allow_html=True)
        hm = []
        for m in team_data:
            ms = set(s.lower() for s in m["skills"].get("all", []))
            row = {"Member": m["name"]}
            for sk in required_skills[:14]:
                row[sk.title()] = 1 if sk.lower() in ms else 0
            hm.append(row)
        df_hm = pd.DataFrame(hm).set_index("Member")
        fig_hm = px.imshow(df_hm, color_continuous_scale=[[0,"#1e1e2e"],[1,"#4ade80"]],
                          labels={"color":"Has Skill"}, aspect="auto",
                          title="Green = Has skill · Dark = Missing")
        fig_hm.update_layout(plot_bgcolor="#08080c", paper_bgcolor="#08080c",
                             height=max(200, len(team_data)*55+80),
                             title_font_color="#94a3b8",
                             xaxis=dict(tickfont=dict(color="#6b6b8a")),
                             yaxis=dict(tickfont=dict(color="#94a3b8")))
        st.plotly_chart(fig_hm, use_container_width=True)

    # Role suggestions
    st.markdown("<h3 style='margin:24px 0 12px;'>🎯 Role Assignment Suggestions</h3>", unsafe_allow_html=True)
    for m in team_data:
        s_list = m["skills"].get("technical", [])
        score = m["gap_result"]["match_score"]
        matched = m["gap_result"].get("matched_skills", [])
        if any(x in " ".join(s_list) for x in ["ml","machine","deep","nlp"]):
            role_s = "ML / AI Lead"
        elif any(x in " ".join(s_list) for x in ["docker","kubernetes","devops","ci"]):
            role_s = "DevOps Lead"
        elif any(x in " ".join(s_list) for x in ["react","frontend","css","vue"]):
            role_s = "Frontend Lead"
        elif any(x in " ".join(s_list) for x in ["sql","data","analytics","pandas"]):
            role_s = "Data Lead"
        else:
            role_s = "Backend Lead"

        sc_col = "#4ade80" if score >= 70 else "#fbbf24" if score >= 40 else "#f87171"
        top_skills = ", ".join((matched or s_list)[:5])
        st.markdown(f"""
        <div style='background:#0e0e16;border:1px solid #1e1e2e;border-left:3px solid {sc_col};
             border-radius:12px;padding:14px 18px;margin-bottom:8px;
             display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;'>
          <div>
            <span style='font-size:0.9rem;font-weight:700;color:#e2e8f0;'>{m['name']}</span>
            <span style='color:#4a4a6a;margin:0 8px;'>→</span>
            <span style='font-size:0.88rem;font-weight:700;color:{sc_col};'>{role_s}</span>
            <div style='font-size:0.75rem;color:#4a4a6a;margin-top:3px;'>Skills: {top_skills}</div>
          </div>
          <div style='font-size:1.4rem;font-weight:900;color:{sc_col};'>{int(score)}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Team gaps
    all_skills = set()
    for m in team_data:
        all_skills.update(s.lower() for s in m["skills"].get("all", []))
    team_gaps = [s for s in required_skills if s.lower() not in all_skills]

    if team_gaps:
        tags = "".join(f"<span style='background:#450a0a;border:1px solid #7f1d1d;color:#f87171;padding:4px 12px;border-radius:99px;font-size:0.78rem;margin:3px;display:inline-block;'>{g.title()}</span>" for g in team_gaps)
        st.markdown(f"""
        <div style='background:#150505;border:1px solid #7f1d1d;border-radius:12px;padding:18px 20px;margin:16px 0;'>
          <div style='font-size:0.82rem;font-weight:700;color:#f87171;margin-bottom:10px;'>
            🚨 Team Gaps — skills nobody on the team has
          </div>
          <div>{tags}</div>
          <div style='font-size:0.78rem;color:#7f1d1d;margin-top:10px;'>
            Assign at least one team member to upskill in each before the project starts.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#052e16;border:1px solid #166534;border-radius:12px;padding:14px 18px;margin-top:12px;'>
          <span style='color:#4ade80;font-weight:700;'>✅ All required skills are covered by at least one team member!</span>
        </div>
        """, unsafe_allow_html=True)

    # CSV export
    csv_rows = [{"Name": m["name"], "Match %": int(m["gap_result"]["match_score"]),
                 "Matched Skills": ", ".join(m["gap_result"].get("matched_skills",[])[:5]),
                 "Critical Gaps": ", ".join(m["gap_result"].get("critical_gaps",[])[:4]),
                 "Status": "Ready" if m["gap_result"]["match_score"] >= 70 else "Needs Prep"}
                for m in team_data]
    st.download_button("⬇️ Download Team Report (CSV)", data=pd.DataFrame(csv_rows).to_csv(index=False),
                       file_name="team_gap_report.csv", mime="text/csv", use_container_width=True)
