"""Page 6 — Placement Cell Dashboard (Batch Analysis)."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from pipeline.resume_parser import ResumeParser
from pipeline.skill_extractor import SkillExtractor
from pipeline.gap_analyzer import GapAnalyzer

st.set_page_config(page_title="Dashboard — Resume Gap Pro", page_icon="📊", layout="wide")

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
div[data-testid="metric-container"]{background:#12121c!important;border:1px solid #252538!important;border-radius:14px!important;padding:18px!important;transition:all .2s;}
div[data-testid="metric-container"]:hover{border-color:#7c6af7!important;transform:translateY(-2px);}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#f0f0f8!important;font-size:1.9rem!important;font-weight:800!important;}
div[data-testid="metric-container"] [data-testid="stMetricLabel"]{color:#6b6b8a!important;font-size:0.75rem!important;}
.stTextArea textarea,.stTextInput input{background:#12121c!important;border:1px solid #252538!important;border-radius:9px!important;color:#f0f0f8!important;}
.stTextArea label,.stTextInput label,.stSelectbox label{color:#6b6b8a!important;}
.stSelectbox>div>div{background:#12121c!important;border-color:#252538!important;color:#94a3b8!important;}
[data-testid="stFileUploader"] section{border:2px dashed #252538!important;border-radius:14px!important;background:#12121c!important;}
[data-testid="stFileUploader"] section:hover{border-color:#7c6af7!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden;}
.stAlert{border-radius:10px!important;}
hr{border-color:#1e1e2e!important;}
h1,h2,h3{color:#f0f0f8!important;}
.stProgress>div>div{border-radius:99px!important;background:#1e1e2e!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,#7c6af7,#22d3ee)!important;border-radius:99px!important;}
</style>
""", unsafe_allow_html=True)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ── Auth gate ──────────────────────────────────────────────────────────────────
if "dash_auth" not in st.session_state:
    st.session_state.dash_auth = False

if not st.session_state.dash_auth:
    st.markdown("""
    <div style='max-width:400px;margin:80px auto;'>
      <div style='text-align:center;margin-bottom:32px;'>
        <div style='font-size:2rem;margin-bottom:8px;'>📊</div>
        <h2 style='color:#f0f0f8;margin:0 0 6px;'>Placement Cell Dashboard</h2>
        <p style='color:#6b6b8a;font-size:0.85rem;'>For placement coordinators and faculty only</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    col_c = st.columns([1,2,1])[1]
    with col_c:
        pwd = st.text_input("Password", type="password", placeholder="Enter admin password")
        if st.button("🔓  Login", type="primary", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.dash_auth = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.caption("Default: `admin123` — change via ADMIN_PASSWORD in .env")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
col_hdr, col_logout = st.columns([4, 1])
with col_hdr:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#08080c,#0e0814);border-bottom:1px solid #1e1e2e;
         padding:40px 0 32px;margin:0 -4rem 32px;'>
      <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#a78bfa;margin-bottom:8px;'>Admin</div>
      <h1 style='font-size:2.4rem;font-weight:800;color:#f0f0f8;letter-spacing:-1px;margin:0 0 8px;'>Placement Cell Dashboard</h1>
      <p style='font-size:0.9rem;color:#6b6b8a;margin:0;'>Bulk-analyse your entire batch and identify cohort-wide skill gaps before placement season.</p>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    if st.button("🔓 Logout"):
        st.session_state.dash_auth = False
        st.session_state.batch_results = None
        st.rerun()

# ── Inputs ─────────────────────────────────────────────────────────────────────
col_i1, col_i2 = st.columns(2)
with col_i1:
    uploaded_resumes = st.file_uploader("📁 Upload Student Resumes (up to 50 PDFs)",
                                         type=["pdf"], accept_multiple_files=True, key="batch_res")
with col_i2:
    target_company = st.selectbox("🏢 Target Company", ["None","Google","Amazon","Microsoft","TCS","Infosys","Flipkart","Wipro","Swiggy","Razorpay"])
    target_role = st.selectbox("🎯 Target Role", ["Software Engineer","Machine Learning Engineer","Data Analyst","Data Scientist","Backend Engineer","Full Stack Developer","DevOps Engineer"])

jd_text = st.text_area("📋 Target JD (optional — auto-generated if blank)", height=100,
                        placeholder="Paste the target company's JD for accurate analysis...", key="batch_jd")
analyse_btn = st.button(f"🚀  Analyse Batch ({len(uploaded_resumes) if uploaded_resumes else 0} resumes)",
                        type="primary", use_container_width=True)

if analyse_btn:
    if not uploaded_resumes:
        st.error("Upload at least one resume.")
        st.stop()
    if len(uploaded_resumes) > 50:
        uploaded_resumes = uploaded_resumes[:50]
    if not jd_text or len(jd_text.split()) < 20:
        jd_text = f"We are hiring for {target_role}. Required: Python, SQL, Data Structures, Algorithms, System Design, Git, Problem Solving. Fresher to 2 years."

    parser = ResumeParser(); ext = SkillExtractor(); ana = GapAnalyzer()
    jd_data = ext.extract_from_jd(jd_text)
    batch_results = []
    prog = st.progress(0, text="Starting batch analysis...")

    for i, f in enumerate(uploaded_resumes):
        prog.progress((i+1)/len(uploaded_resumes), text=f"Processing {f.name} ({i+1}/{len(uploaded_resumes)})")
        try:
            raw = parser.extract_text(f.read())
            clean = parser.clean_text(raw)
            if len(clean.strip()) < 100:
                continue
            secs = parser.extract_sections(clean)
            skills = ext.extract_from_resume(secs)
            gap = ana.compute_gaps(skills, jd_data, company=None if target_company=="None" else target_company)
            batch_results.append({"name": f.name.replace(".pdf",""), "match_score": gap["match_score"],
                                  "critical_gaps": gap.get("critical_gaps",[]),
                                  "matched_skills": gap.get("matched_skills",[]),
                                  "status": "Ready" if gap["match_score"] >= 70 else "Needs Prep"})
        except Exception:
            pass

    prog.empty()
    st.session_state["batch_results"] = batch_results

if st.session_state.get("batch_results"):
    results = st.session_state["batch_results"]
    if not results:
        st.error("No results.")
        st.stop()

    scores = [r["match_score"] for r in results]
    avg = sum(scores) / len(scores)
    ready = sum(1 for s in scores if s >= 70)

    # Metrics
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total Students", len(results))
    m2.metric("📊 Avg Match Score", f"{avg:.1f}%")
    m3.metric("✅ Ready (>70%)", ready)
    m4.metric("⚡ Needs Prep", len(results)-ready)

    # Gap heatmap
    st.markdown("<h3 style='margin:24px 0 12px;'>🔥 Cohort-Wide Skill Gaps</h3>", unsafe_allow_html=True)
    all_gaps: dict = {}
    for r in results:
        for g in r["critical_gaps"]:
            all_gaps[g.title()] = all_gaps.get(g.title(), 0) + 1
    top_gaps = sorted(all_gaps.items(), key=lambda x: x[1], reverse=True)[:10]

    if top_gaps:
        gnames, gcounts = zip(*top_gaps)
        gpcts = [round(c/len(results)*100) for c in gcounts]
        bar_cols = ["#f87171" if p >= 60 else "#fbbf24" if p >= 35 else "#94a3b8" for p in gpcts]
        fig_g = go.Figure(go.Bar(x=list(gpcts), y=list(gnames), orientation="h",
                                 marker_color=bar_cols, text=[f"{p}%" for p in gpcts], textposition="outside",
                                 textfont=dict(color="#6b6b8a", size=11)))
        fig_g.update_layout(plot_bgcolor="#08080c", paper_bgcolor="#08080c", height=340,
                            margin=dict(l=160,r=40,t=20,b=20),
                            xaxis=dict(tickfont=dict(color="#6b6b8a"), gridcolor="#1e1e2e",
                                      title=dict(text="% of students missing", font=dict(color="#4a4a6a"))),
                            yaxis=dict(tickfont=dict(color="#94a3b8")))
        st.plotly_chart(fig_g, use_container_width=True)

        # Workshop recommendations
        st.markdown("""
        <div style='background:#0e0e16;border:1px solid #1e1e2e;border-radius:14px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#7c6af7;margin-bottom:12px;'>
            🏫 Recommended Pre-Placement Workshops
          </div>
        """, unsafe_allow_html=True)
        for i, (skill, count) in enumerate(top_gaps[:3], 1):
            pct = round(count/len(results)*100)
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #1e1e2e;'>
              <div style='font-size:0.9rem;font-weight:900;color:#7c6af7;min-width:24px;'>{i}</div>
              <div>
                <div style='font-size:0.85rem;font-weight:700;color:#e2e8f0;'>{skill}</div>
                <div style='font-size:0.75rem;color:#4a4a6a;'>{pct}% of batch missing this — schedule 2-day intensive workshop</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Score distribution
    st.markdown("<h3 style='margin:20px 0 12px;'>📊 Score Distribution</h3>", unsafe_allow_html=True)
    fig_d = px.histogram(x=scores, nbins=10, labels={"x":"Match Score (%)"},
                         title="Batch Score Distribution", color_discrete_sequence=["#7c6af7"])
    fig_d.add_vline(x=70, line_dash="dash", line_color="#4ade80",
                   annotation_text="Ready threshold", annotation_font_color="#4ade80")
    fig_d.update_layout(plot_bgcolor="#08080c", paper_bgcolor="#08080c", height=260,
                        title_font_color="#94a3b8", margin=dict(t=30,b=20,l=0,r=0),
                        xaxis=dict(tickfont=dict(color="#6b6b8a"), gridcolor="#1e1e2e"),
                        yaxis=dict(tickfont=dict(color="#6b6b8a"), gridcolor="#1e1e2e"))
    st.plotly_chart(fig_d, use_container_width=True)

    # Individual table
    st.markdown("<h3 style='margin:20px 0 12px;'>👤 Individual Results</h3>", unsafe_allow_html=True)
    df_tbl = pd.DataFrame([{"Name": r["name"], "Match %": int(r["match_score"]),
                             "Critical Gaps": ", ".join(r["critical_gaps"][:4]) or "None",
                             "Status": r["status"]}
                           for r in results]).sort_values("Match %", ascending=False)
    st.dataframe(df_tbl, use_container_width=True, hide_index=True)

    # Exports
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.download_button("⬇️ Download Batch Report (CSV)",
                          data=df_tbl.to_csv(index=False),
                          file_name="batch_placement_report.csv", mime="text/csv", use_container_width=True)
    with col_e2:
        summary = f"""PLACEMENT READINESS REPORT
Target Role: {target_role} | Company: {target_company}
Students Analysed: {len(results)} | Avg Score: {avg:.1f}%
Ready (>70%): {ready} ({round(ready/len(results)*100)}%) | Needs Prep: {len(results)-ready}

TOP GAPS:
""" + "\n".join(f"{i+1}. {s} — {round(c/len(results)*100)}% of batch" for i,(s,c) in enumerate(top_gaps[:5]))
        st.download_button("📄 Download Summary (.txt)",
                          data=summary, file_name="placement_summary.txt",
                          mime="text/plain", use_container_width=True)
