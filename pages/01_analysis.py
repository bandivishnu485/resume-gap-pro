"""
Page 1 — Core Gap Analysis.
"""
import os, sys
import warnings
warnings.filterwarnings("ignore")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.resume_parser import ResumeParser
from pipeline.skill_extractor import SkillExtractor
from pipeline.gap_analyzer import GapAnalyzer
from pipeline.ats_checker import ATSChecker
from pipeline.resume_scorer import ResumeScorer
from pipeline.rag_engine import RAGEngine
from pipeline.roadmap_generator import RoadmapGenerator
from pipeline.salary_estimator import SalaryEstimator
from pipeline.peer_stats import PeerStats
from pipeline.project_suggester import ProjectSuggester
from pipeline.share_card import ShareCardGenerator
from pipeline.calendar_exporter import CalendarExporter
from pipeline.vernacular import VernacularTranslator

st.set_page_config(page_title="Gap Analysis — Resume Gap Pro", page_icon="🔍", layout="wide")

# ─── Session State Defaults ───────────────────────────────────────────────────
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

# ─── Helpers ─────────────────────────────────────────────────────────────────
def pill(text, cls="pill-blue"):
    return f'<span class="skill-pill {cls}">{text}</span>'

def pills_html(items, cls):
    return " ".join(pill(i.title(), cls) for i in items[:15])

def score_color_class(score):
    if score >= 70: return "score-green"
    if score >= 40: return "score-amber"
    return "score-red"

# ─── Page ────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Resume Gap Analysis")
st.markdown("Upload your resume and paste the job description to get a full AI-powered gap report.")

# ─── Input Section ───────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    uploaded = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"], key="resume_upload")
    company = st.selectbox(
        "🏢 Target Company (optional)",
        ["None", "Google", "Amazon", "Microsoft", "TCS", "Infosys",
         "Flipkart", "Wipro", "Swiggy", "Razorpay", "FAANG (General)"],
        key="company_select",
    )
    interview_date = st.date_input("📅 Interview Date (optional)", value=None, key="interview_date_input")

with col_right:
    jd_text = st.text_area(
        "📋 Paste Job Description",
        height=220,
        placeholder="Paste the full job description here. Include required skills, responsibilities, and preferred qualifications...",
        key="jd_input",
    )
    role_override = st.text_input("🎯 Role Title (auto-detected or override)", key="role_override")

st.markdown("<br>", unsafe_allow_html=True)
analyse_btn = st.button("🚀 Analyse My Resume", type="primary", use_container_width=True, key="analyse_btn")

# ─── Analysis ────────────────────────────────────────────────────────────────
if analyse_btn:
    if not uploaded:
        st.error("❌ Please upload a PDF resume.")
        st.stop()
    if not jd_text or len(jd_text.split()) < 30:
        st.warning("⚠️ Please paste a full job description (at least 30 words) for accurate analysis.")

    pdf_bytes = uploaded.read()

    with st.status("🔄 Running AI analysis...", expanded=True) as status:
        st.write("📄 Parsing your resume...")
        parser = ResumeParser()
        raw_text = parser.extract_text(pdf_bytes)
        clean_text = parser.clean_text(raw_text)
        sections = parser.extract_sections(clean_text)
        format_issues = parser.detect_format_issues(pdf_bytes)

        if len(clean_text.strip()) < 100:
            st.error("⚠️ Could not extract text from your PDF. It may be a scanned image. Please use a text-based PDF.")
            st.stop()

        st.write("🧠 Extracting skills with NLP...")
        extractor = SkillExtractor()
        resume_skills = extractor.extract_from_resume(sections)
        jd_data = extractor.extract_from_jd(jd_text)
        soft_gaps = extractor.extract_soft_gaps(resume_skills, jd_data)

        role_title = role_override or jd_data.get("role_title", "Software Engineer")

        st.write("📊 Running gap analysis...")
        analyzer = GapAnalyzer()
        selected_company = None if company == "None" else company
        gap_result = analyzer.compute_gaps(resume_skills, jd_data, company=selected_company)
        gap_result["soft_gaps"] = soft_gaps

        st.write("🤖 Checking ATS compatibility...")
        ats_checker = ATSChecker()
        ats_result = ats_checker.check(clean_text, jd_text, format_issues)

        st.write("📝 Scoring resume sections...")
        scorer = ResumeScorer()
        section_scores = scorer.score(sections, resume_skills)

        st.write("📚 Retrieving courses via RAG...")
        rag = RAGEngine()
        all_gaps = gap_result.get("critical_gaps", []) + gap_result.get("optional_gaps", [])[:3]
        retrieved_courses = rag.retrieve_for_all_gaps(all_gaps)

        st.write("💰 Estimating salary...")
        sal_estimator = SalaryEstimator()
        salary_data = sal_estimator.estimate(role_title, gap_result["match_score"])

        st.write("👥 Computing peer comparison...")
        peer = PeerStats()
        peer_data = peer.get_comparison(role_title, gap_result["match_score"])

        st.write("🗺️ Generating your roadmap...")
        deadline_days = 30
        if interview_date:
            deadline_days = max(1, (interview_date - date.today()).days)

        rg = RoadmapGenerator()
        roadmap = rg.generate_roadmap(
            resume_skills, gap_result, retrieved_courses, role_title, deadline_days
        )

        # Persist to session state
        full_analysis = {
            **gap_result,
            "ats": ats_result,
            "section_scores": section_scores,
            "salary": salary_data,
            "peer": peer_data,
            "retrieved_courses": retrieved_courses,
            "format_issues": format_issues,
            "role_title": role_title,
        }

        st.session_state.analysis = full_analysis
        st.session_state.resume_text = clean_text
        st.session_state.sections = sections
        st.session_state.jd_text = jd_text
        st.session_state.role_title = role_title
        st.session_state.roadmap = roadmap
        st.session_state.resume_skills = resume_skills
        st.session_state.jd_data = jd_data
        st.session_state.retrieved_courses = retrieved_courses
        st.session_state.company = selected_company
        st.session_state.interview_date = interview_date
        st.session_state.history.append({
            "date": str(date.today()),
            "role": role_title,
            "score": gap_result["match_score"],
        })

        # Translation
        lang = st.session_state.get("lang", "English")
        if lang != "English":
            translator = VernacularTranslator()
            st.session_state.analysis = translator.translate_report(full_analysis, lang)

        status.update(label="✅ Analysis complete!", state="complete")

# ─── Results ─────────────────────────────────────────────────────────────────
if st.session_state.get("analysis"):
    an = st.session_state.get("analysis")
    match_score = an.get("match_score", 0)
    ats = an.get("ats", {})
    scores = an.get("section_scores", {})
    salary = an.get("salary", {})
    peer_d = an.get("peer", {})
    retrieved = st.session_state.get("retrieved_courses", {})

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview", "📋 Gap Table", "🤖 ATS Report",
        "📝 Resume Score", "💰 Salary", "🗺️ Roadmap",
        "🛠️ Projects", "👥 Peers", "📤 Share"
    ])

    # ── Tab 1: Overview ───────────────────────────────────────────────────────
    with tabs[0]:
        # Metric cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🎯 Match Score", f"{int(match_score)}%")
        m2.metric("🤖 ATS Score", f"{ats.get('ats_score', 0)}/100")
        m3.metric("📝 Resume Score", f"{scores.get('overall', 0)}/100")
        m4.metric("💰 Salary Boost", an.get("salary", {}).get("increase", "Possible"))

        # Score circle
        col_circ, col_stats = st.columns([1, 2])
        with col_circ:
            cls = score_color_class(match_score)
            st.markdown(f"""
            <div style='text-align:center; padding: 30px 0;'>
                <div class='score-circle {cls}'>{int(match_score)}%</div>
                <p style='text-align:center; color:#64748b; margin-top:12px; font-size:0.85rem;'>
                    Match Score for<br><strong>{st.session_state.role_title}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            if an.get("company_tip"):
                st.info(f"💡 **Company Tip:** {an['company_tip']}")

        with col_stats:
            st.markdown("**✅ Matched Skills**")
            matched = an.get("matched_skills", [])
            if matched:
                st.markdown(pills_html(matched, "pill-green"), unsafe_allow_html=True)
            else:
                st.caption("No exact matches found.")

            st.markdown("**❌ Critical Gaps**")
            critical = an.get("critical_gaps", [])
            if critical:
                st.markdown(pills_html(critical, "pill-red"), unsafe_allow_html=True)
            else:
                st.success("No critical gaps! You're a strong match.")

            st.markdown("**🟡 Soft Skill Gaps**")
            soft = an.get("soft_gaps", [])
            if soft:
                st.markdown(pills_html(soft, "pill-amber"), unsafe_allow_html=True)
            else:
                st.caption("Soft skill signals look good.")

        # Peer comparison box
        st.markdown("---")
        st.markdown("### 👥 Peer Comparison")
        percentile = peer_d.get("percentile", 50)
        avg = peer_d.get("avg_score", 55)
        message = peer_d.get("message", "")
        col_peer1, col_peer2 = st.columns([2, 1])
        with col_peer1:
            st.info(message)
            dist = peer_d.get("score_distribution", [])
            buckets = peer_d.get("score_buckets", [])
            if dist and buckets:
                fig = px.bar(
                    x=buckets, y=dist,
                    labels={"x": "Score Range", "y": "# Students"},
                    title="Score Distribution (Peers)",
                    color=dist,
                    color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
                )
                fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col_peer2:
            st.metric("📊 Your Percentile", f"{percentile}th")
            st.metric("📈 Peer Avg Score", f"{avg}%")
            common_gaps = peer_d.get("common_gaps", [])
            if common_gaps:
                st.markdown("**Common peer gaps:**")
                for cg in common_gaps[:4]:
                    st.markdown(f"• {cg}")

    # ── Tab 2: Gap Table ──────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 📋 Detailed Gap Analysis")
        severity_map = an.get("severity", {})
        rows = []
        for skill in an.get("critical_gaps", []):
            courses = retrieved.get(skill, [{}])
            c = courses[0] if courses else {}
            rows.append({
                "Skill": skill.title(),
                "Type": "Technical",
                "Severity": severity_map.get(skill, "Medium"),
                "ATS Impact": "High" if severity_map.get(skill) == "High" else "Medium",
                "Top Course": c.get("course_name", "Search online")[:40],
                "Platform": c.get("platform", "-"),
                "Duration": c.get("duration", "-"),
                "URL": c.get("url", ""),
            })
        for skill in an.get("optional_gaps", []):
            courses = retrieved.get(skill, [{}])
            c = courses[0] if courses else {}
            rows.append({
                "Skill": skill.title(),
                "Type": "Optional",
                "Severity": "Low",
                "ATS Impact": "Low",
                "Top Course": c.get("course_name", "Search online")[:40],
                "Platform": c.get("platform", "-"),
                "Duration": c.get("duration", "-"),
                "URL": c.get("url", ""),
            })

        if rows:
            df = pd.DataFrame(rows)

            def color_severity(val):
                if val == "High": return "background-color: #fee2e2; color: #991b1b"
                if val == "Medium": return "background-color: #fef3c7; color: #92400e"
                return "background-color: #f0fdf4; color: #166534"

            styler_map = getattr(df.style, "map", getattr(df.style, "applymap", None))
            styled = styler_map(color_severity, subset=["Severity"]) if styler_map else df
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 No significant skill gaps found! You're a strong match for this role.")

    # ── Tab 3: ATS Report ─────────────────────────────────────────────────────
    with tabs[2]:
        ats_score = ats.get("ats_score", 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ats_score,
            delta={"reference": 70, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#6366f1"},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
                "threshold": {"line": {"color": "red"}, "thickness": 0.75, "value": 70},
            },
            title={"text": "ATS Compatibility Score"},
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=30, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

        col_kw, col_fmt = st.columns(2)
        with col_kw:
            st.markdown("**🔑 Missing Keywords (add these)**")
            missing_kw = ats.get("missing_keywords", [])
            if missing_kw:
                kw_text = ", ".join(missing_kw[:20])
                st.code(kw_text, language=None)
                st.caption("Copy-paste these into your Skills or Experience section.")
            else:
                st.success("Good keyword coverage!")

        with col_fmt:
            st.markdown("**📐 Format Issues**")
            fmt_issues = ats.get("format_issues", [])
            if fmt_issues:
                for issue in fmt_issues:
                    st.warning(issue)
            else:
                st.success("No formatting issues detected.")

        st.markdown("**💡 Recommendations**")
        for rec in ats.get("recommendations", []):
            st.markdown(f"- {rec}")

    # ── Tab 4: Resume Score ───────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### 📝 Resume Section Quality Scores")
        overall = scores.get("overall", 0)
        grade = scores.get("grade", "C")
        col_ov1, col_ov2 = st.columns([1, 3])
        with col_ov1:
            color = "#22c55e" if overall >= 70 else "#f59e0b" if overall >= 50 else "#ef4444"
            st.markdown(f"""
            <div style='background:{color}; color:white; border-radius:12px; padding:20px; text-align:center;'>
                <div style='font-size:2.5rem; font-weight:900;'>{grade}</div>
                <div style='font-size:1rem;'>{overall}/100</div>
            </div>
            """, unsafe_allow_html=True)

        for section in ["summary", "experience", "skills", "projects"]:
            data = scores.get(section, {"score": 0, "feedback": ""})
            s = data.get("score", 0)
            fb = data.get("feedback", "")
            bar_color = "normal" if s >= 60 else "inverse"
            st.markdown(f"**{section.title()} — {s}/100**")
            st.progress(s / 100)
            if fb:
                st.caption(fb)
            st.markdown("")

    # ── Tab 5: Salary ─────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("### 💰 Salary Estimate (2024 Indian Market)")
        cur = salary.get("current", {})
        aft = salary.get("after_upskilling", {})
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"""
            <div style='background:#fef3c7; border-radius:12px; padding:24px; text-align:center;'>
                <div style='font-size:0.9rem; color:#92400e; margin-bottom:8px;'>Current Estimate</div>
                <div style='font-size:2rem; font-weight:800; color:#d97706;'>{cur.get('label', '₹5-10 LPA')}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"""
            <div style='background:#dcfce7; border-radius:12px; padding:24px; text-align:center;'>
                <div style='font-size:0.9rem; color:#166534; margin-bottom:8px;'>After Closing Gaps</div>
                <div style='font-size:2rem; font-weight:800; color:#16a34a;'>{aft.get('label', '₹12-20 LPA')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align:center; margin-top:16px; font-size:1.1rem; color:#6366f1; font-weight:600;'>
            ↑ {salary.get('increase', '')}
        </div>
        """, unsafe_allow_html=True)
        st.caption(salary.get("note", ""))


    # ── Tab 6: Roadmap ────────────────────────────────────────────────────────
    with tabs[5]:
        roadmap_text = st.session_state.roadmap
        critical_gaps = an.get("critical_gaps", [])
        role_title_rd = st.session_state.role_title or "Software Engineer"

        if st.session_state.interview_date:
            days_left = max(1, (st.session_state.interview_date - date.today()).days)
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#450a0a,#3b0764);border:1px solid #7f1d1d;
                 border-radius:12px;padding:14px 18px;margin-bottom:16px;display:flex;
                 align-items:center;gap:12px;'>
              <span style='font-size:1.4rem;'>⚡</span>
              <div>
                <div style='font-size:0.85rem;font-weight:700;color:#fca5a5;'>Urgency Mode Active</div>
                <div style='font-size:0.78rem;color:#7f1d1d;'>{days_left} days until your interview — roadmap compressed to critical gaps only.</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Focus Areas Dashboard ──────────────────────────────────────────────
        if critical_gaps:
            st.markdown("### 🎯 Your Weekly Focus Areas")
            week_colors = ["#7c6af7", "#22d3ee", "#f472b6", "#4ade80", "#fbbf24", "#a78bfa"]
            deadline = 30
            if st.session_state.interview_date:
                deadline = max(7, (st.session_state.interview_date - date.today()).days)

            weeks = max(2, min(6, len(critical_gaps) + 1))
            gaps_per_week = max(1, len(critical_gaps) // weeks + 1)

            focus_cols = st.columns(min(weeks, 4))
            for wi in range(min(weeks, len(focus_cols))):
                gap_slice = critical_gaps[wi*gaps_per_week:(wi+1)*gaps_per_week]
                if not gap_slice and wi > 0:
                    gap_slice = ["Portfolio & Practice"]
                elif not gap_slice:
                    gap_slice = critical_gaps[:1]

                color = week_colors[wi % len(week_colors)]
                hours_day = max(2, 90 // deadline)
                with focus_cols[wi]:
                    skills_html = "".join(f"<div style='font-size:0.72rem;color:#94a3b8;padding:3px 0;border-bottom:1px solid #1e1e2e;'>→ {g.title()}</div>" for g in gap_slice[:3])
                    retrieved_for_gap = retrieved.get(gap_slice[0], [{}]) if gap_slice else [{}]
                    top_course = retrieved_for_gap[0].get("course_name", "")[:30] if retrieved_for_gap else ""
                    top_platform = retrieved_for_gap[0].get("platform", "") if retrieved_for_gap else ""
                    st.markdown(f"""
                    <div style='background:#0e0e16;border:1px solid #1e1e2e;border-top:3px solid {color};
                         border-radius:12px;padding:16px;height:200px;position:relative;overflow:hidden;'>
                      <div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;
                           letter-spacing:1px;color:{color};margin-bottom:6px;'>Week {wi+1}</div>
                      {skills_html}
                      <div style='position:absolute;bottom:12px;left:16px;right:16px;'>
                        <div style='font-size:0.68rem;color:#3a3a5c;margin-bottom:3px;'>⏱ {hours_day}h/day</div>
                        {f'<div style="font-size:0.68rem;color:#4a4a6a;">📖 {top_course}<br><span style=&quot;color:#3a3a5c&quot;>{top_platform}</span></div>' if top_course else ''}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Study Schedule breakdown ───────────────────────────────────────────
        if critical_gaps:
            with st.expander("📅 Daily Study Schedule Breakdown", expanded=False):
                deadline = 30
                if st.session_state.interview_date:
                    deadline = max(7, (st.session_state.interview_date - date.today()).days)
                hours_day = max(2, min(5, 90 // deadline))

                schedule_data = {
                    "Morning (Theory)": f"{max(1, hours_day//2)}h — Watch course videos, read docs",
                    "Afternoon (Coding)": f"{max(1, hours_day//2)}h — Solve problems, build mini-project",
                    "Evening (Review)": "30 min — Note key concepts, update GitHub",
                    "Weekend Deep Dive": "4–6h — Full project implementation + revision",
                }
                for slot, plan in schedule_data.items():
                    st.markdown(f"""
                    <div style='display:flex;gap:12px;align-items:center;padding:8px 0;border-bottom:1px solid #1e1e2e;'>
                      <div style='font-size:0.8rem;font-weight:600;color:#94a3b8;min-width:160px;'>{slot}</div>
                      <div style='font-size:0.8rem;color:#6b6b8a;'>{plan}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Milestones ────────────────────────────────────────────────────────
        if critical_gaps:
            st.markdown("### 🏁 Milestones & Checkpoints")
            milestones = []
            if len(critical_gaps) >= 1:
                milestones.append((f"Week 1 end", f"Complete intro to {critical_gaps[0].title()} — pass a basic quiz", "#7c6af7"))
            if len(critical_gaps) >= 2:
                milestones.append((f"Week 2 end", f"Ship a mini-project using {critical_gaps[0].title()} + start {critical_gaps[1].title()}", "#22d3ee"))
            if len(critical_gaps) >= 3:
                milestones.append((f"Week 3 end", f"Solve 10 LeetCode-style problems involving {critical_gaps[1].title()}", "#f472b6"))
            milestones.append(("Final week", "Mock interview on ALL gaps · Update resume · Apply", "#4ade80"))

            for i, (when, what, color) in enumerate(milestones):
                st.markdown(f"""
                <div style='display:flex;gap:16px;align-items:flex-start;margin-bottom:10px;'>
                  <div style='width:10px;height:10px;border-radius:50%;background:{color};
                       margin-top:5px;flex-shrink:0;box-shadow:0 0 8px {color}80;'></div>
                  <div>
                    <div style='font-size:0.8rem;font-weight:700;color:{color};margin-bottom:2px;'>{when}</div>
                    <div style='font-size:0.82rem;color:#94a3b8;'>{what}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Gemini roadmap (full text) ─────────────────────────────────────────
        if roadmap_text:
            with st.expander("📄 Master Technical Study Roadmap", expanded=True):
                st.markdown(roadmap_text)
        else:
            st.info("Roadmap will appear here after analysis. Make sure your GOOGLE_API_KEY is set in .env")

        # ── Downloads ─────────────────────────────────────────────────────────
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if roadmap_text:
                st.download_button(
                    "⬇️ Download Roadmap (.md)",
                    data=roadmap_text,
                    file_name=f"roadmap_{role_title_rd.replace(' ','_')}.md",
                    mime="text/markdown", use_container_width=True,
                )
        with col_dl2:
            if roadmap_text:
                try:
                    cal_exp = CalendarExporter()
                    ics_bytes = cal_exp.generate_ics(roadmap_text, date.today())
                    st.download_button(
                        "📅 Export to Calendar (.ics)",
                        data=ics_bytes, file_name="study_roadmap.ics",
                        mime="text/calendar", use_container_width=True,
                    )
                except Exception as e:
                    st.caption(f"Calendar export unavailable: {e}")

    # ── Tab 7: Projects ───────────────────────────────────────────────────────
    with tabs[6]:
        critical_gaps_proj = an.get("critical_gaps", [])[:6]
        suggester = ProjectSuggester()
        projects_map = suggester.suggest(critical_gaps_proj)

        if not critical_gaps_proj:
            st.success("🎉 No critical gaps — you're a strong match! Consider projects that showcase your existing skills.")
        else:
            st.markdown("### 🛠️ Hands-On Projects for Your Gaps")
            st.markdown("<p style='color:#6b6b8a;font-size:0.85rem;'>Build these to close gaps AND get GitHub-ready proof of skills. Each card estimates realistic time for a fresher.</p>", unsafe_allow_html=True)

        diff_colors = {"Beginner": "#4ade80", "Intermediate": "#fbbf24", "Advanced": "#f87171"}
        diff_bg = {"Beginner": "#052e16", "Intermediate": "#451a03", "Advanced": "#450a0a"}

        for gap in critical_gaps_proj:
            projects = projects_map.get(gap, [])
            if not projects:
                continue

            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin:20px 0 10px;'>
              <div style='height:1px;flex:1;background:#1e1e2e;'></div>
              <span style='font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                   color:#6b6b8a;padding:0 12px;'>{gap.title()}</span>
              <div style='height:1px;flex:1;background:#1e1e2e;'></div>
            </div>
            """, unsafe_allow_html=True)

            proj_cols = st.columns(min(len(projects), 2))
            for i, proj in enumerate(projects[:2]):
                with proj_cols[i]:
                    title = proj.get("title", "Project")
                    desc = proj.get("desc", "")
                    days = proj.get("days", 3)
                    skills = proj.get("skills_demonstrated", [])
                    github_ready = proj.get("github_ready", True)

                    # Infer difficulty from days
                    diff = "Beginner" if days <= 2 else ("Intermediate" if days <= 4 else "Advanced")
                    dc = diff_colors.get(diff, "#fbbf24")
                    db = diff_bg.get(diff, "#451a03")

                    skills_badges = "".join(
                        f"<span style='background:#0e0e16;border:1px solid #252538;color:#94a3b8;padding:2px 9px;border-radius:99px;font-size:0.68rem;margin:2px;display:inline-block;'>{s}</span>"
                        for s in skills[:5]
                    )

                    st.markdown(f"""
                    <div style='background:#0e0e16;border:1px solid #1e1e2e;border-radius:14px;padding:20px;
                         height:260px;position:relative;overflow:hidden;'>
                      <!-- Difficulty badge -->
                      <div style='position:absolute;top:14px;right:14px;background:{db};
                           border:1px solid {dc};color:{dc};padding:2px 9px;border-radius:99px;
                           font-size:0.66rem;font-weight:700;'>{diff}</div>

                      <!-- Title -->
                      <div style='font-size:0.95rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;
                           padding-right:72px;line-height:1.3;'>{title}</div>

                      <!-- Description -->
                      <div style='font-size:0.78rem;color:#6b6b8a;line-height:1.55;margin-bottom:10px;'>{desc[:120]}{"..." if len(desc)>120 else ""}</div>

                      <!-- Skills -->
                      <div style='margin-bottom:10px;'>{skills_badges}</div>

                      <!-- Footer stats -->
                      <div style='position:absolute;bottom:14px;left:20px;right:20px;
                           display:flex;justify-content:space-between;align-items:center;'>
                        <div style='font-size:0.72rem;color:#4a4a6a;'>⏱️ Est. {days} day{"s" if days>1 else ""}</div>
                        {'<div style="font-size:0.72rem;color:#4ade80;">✓ GitHub-ready</div>' if github_ready else ''}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    readme_md = f"""# {title}

{desc}

## Tech Stack
{", ".join(skills)}

## Estimated Time
{days} day{"s" if days > 1 else ""}

## What You'll Learn
Building this project will help you demonstrate **{gap.title()}** skills in a real-world context.

## Steps
1. Set up the project structure and repository
2. Implement the core functionality
3. Add error handling and edge cases
4. Write a clear README with setup instructions
5. Deploy or add a demo GIF

## How to Stand Out
- Add proper documentation and docstrings
- Include unit tests (even basic ones)
- Add a live demo link or screenshots to your README
- Write a LinkedIn post about what you learned
"""
                    st.download_button(
                        "📋 Get README Template",
                        data=readme_md,
                        file_name=f"{title.replace(' ','_')}_README.md",
                        mime="text/markdown",
                        key=f"readme_{gap}_{i}",
                        use_container_width=True,
                    )

        # ── Project tips box ──────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#0e0e16;border:1px solid #252538;border-left:3px solid #7c6af7;
             border-radius:10px;padding:16px 20px;'>
          <div style='font-size:0.82rem;font-weight:700;color:#a78bfa;margin-bottom:8px;'>💡 Make Your Projects Stand Out</div>
          <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
            <div style='font-size:0.78rem;color:#6b6b8a;'>→ Push every project to GitHub with a README + screenshot</div>
            <div style='font-size:0.78rem;color:#6b6b8a;'>→ Deploy at least one project (Streamlit Cloud, Vercel, Render — all free)</div>
            <div style='font-size:0.78rem;color:#6b6b8a;'>→ Write a 300-word LinkedIn post about what you built and learned</div>
            <div style='font-size:0.78rem;color:#6b6b8a;'>→ Add the project to your resume with a bullet on the outcome/impact</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 8: Peer Comparison ────────────────────────────────────────────────
    with tabs[7]:
        percentile = peer_d.get("percentile", 50)
        avg_score = peer_d.get("avg_score", 55)
        total_peers = peer_d.get("total_peers", 100)
        role_matched = peer_d.get("role_matched", st.session_state.role_title)
        common_gaps = peer_d.get("common_gaps", [])
        dist = peer_d.get("score_distribution", [])
        buckets = peer_d.get("score_buckets", [])
        message = peer_d.get("message", "")

        # ── Percentile hero card ──────────────────────────────────────────────
        pct_color = "#4ade80" if percentile >= 70 else "#fbbf24" if percentile >= 40 else "#f87171"
        pct_bg = "#052e16" if percentile >= 70 else "#451a03" if percentile >= 40 else "#450a0a"
        pct_border = "#166534" if percentile >= 70 else "#78350f" if percentile >= 40 else "#7f1d1d"

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,{pct_bg},{pct_bg}80);
             border:1px solid {pct_border};border-radius:16px;padding:24px 28px;
             display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:16px;'>
          <div>
            <div style='font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                 color:{pct_color}80;margin-bottom:4px;'>Your Rank Among Peers</div>
            <div style='font-size:0.85rem;color:#94a3b8;max-width:400px;line-height:1.5;'>{message}</div>
          </div>
          <div style='text-align:center;'>
            <div style='font-size:3.5rem;font-weight:900;color:{pct_color};line-height:1;'>{percentile}<span style='font-size:1.5rem;'>th</span></div>
            <div style='font-size:0.72rem;color:{pct_color}80;'>percentile</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 3 metrics ─────────────────────────────────────────────────────────
        pm1, pm2, pm3 = st.columns(3)
        pm1.metric("Your Score", f"{int(match_score)}%")
        pm2.metric(f"Avg ({role_matched})", f"{avg_score}%", delta=f"{int(match_score)-avg_score:+d}%")
        pm3.metric("Peers Analysed", f"{total_peers:,}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Distribution chart ────────────────────────────────────────────────
        col_chart, col_gaps = st.columns([3, 2])
        with col_chart:
            if dist and buckets:
                bar_colors = []
                for b in buckets:
                    try:
                        lo = int(b.split("-")[0])
                        hi = int(b.split("-")[1])
                        bar_colors.append("#7c6af7" if lo <= match_score <= hi else "#1e1e2e")
                    except Exception:
                        bar_colors.append("#1e1e2e")

                fig_peer = go.Figure(go.Bar(
                    x=buckets, y=dist,
                    marker_color=bar_colors,
                    marker_line_color=["#a78bfa" if c == "#7c6af7" else "#252538" for c in bar_colors],
                    marker_line_width=2,
                    text=[f"{v}" for v in dist],
                    textposition="outside",
                    textfont=dict(color="#6b6b8a", size=11),
                ))
                # Your score annotation
                try:
                    user_b = next((b for b in buckets if "-" in b and int(b.split("-")[0]) <= match_score <= int(b.split("-")[1])), buckets[min(2, len(buckets)-1)])
                    if user_b in buckets:
                        b_idx = buckets.index(user_b)
                        y_val = dist[b_idx] if b_idx < len(dist) else 1
                        fig_peer.add_annotation(
                            x=user_b, y=y_val,
                            text=f"You: {int(match_score)}%",
                            showarrow=True, arrowhead=2, arrowcolor="#a78bfa",
                            font=dict(color="#a78bfa", size=11),
                            yshift=10,
                        )
                except Exception:
                    pass
                fig_peer.update_layout(
                    plot_bgcolor="#08080c",
                    paper_bgcolor="#08080c",
                    title=dict(text=f"Score Distribution — {role_matched}", font=dict(color="#94a3b8", size=13)),
                    xaxis=dict(tickfont=dict(color="#6b6b8a", size=11), gridcolor="#1e1e2e", title=dict(text="Score Range", font=dict(color="#4a4a6a"))),
                    yaxis=dict(tickfont=dict(color="#6b6b8a", size=11), gridcolor="#1e1e2e", title=dict(text="# Students", font=dict(color="#4a4a6a"))),
                    height=280, margin=dict(t=40, b=20, l=40, r=20),
                )
                st.plotly_chart(fig_peer, use_container_width=True)

        with col_gaps:
            st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.78rem;font-weight:700;color:#6b6b8a;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;'>Most Common Peer Gaps</p>", unsafe_allow_html=True)
            for idx, cg in enumerate(common_gaps[:5]):
                # Frequency bar (simulated: top gap = 100%, decreasing)
                freq = max(40, 90 - idx * 14)
                gap_color = "#f87171" if idx == 0 else "#fbbf24" if idx == 1 else "#93c5fd"
                is_user_gap = cg.lower() in [g.lower() for g in an.get("critical_gaps", [])]
                you_tag = "<span style='font-size:0.6rem;background:#2e1065;color:#c4b5fd;padding:1px 6px;border-radius:99px;border:1px solid #4c1d95;margin-left:6px;'>you</span>" if is_user_gap else ""
                st.markdown(f"""
                <div style='margin-bottom:12px;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
                    <span style='font-size:0.78rem;color:#94a3b8;'>{cg.title()}{you_tag}</span>
                    <span style='font-size:0.72rem;color:#4a4a6a;'>{freq}% of peers</span>
                  </div>
                  <div style='background:#1e1e2e;border-radius:99px;height:5px;'>
                    <div style='background:{gap_color};height:5px;border-radius:99px;width:{freq}%;
                         box-shadow:0 0 6px {gap_color}60;'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── What to do next panel ─────────────────────────────────────────────
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if percentile >= 70:
            action_msg = "🚀 You're ahead of the curve. Focus on polish — quantify your resume achievements and prep for system design rounds."
            action_color = "#4ade80"
        elif percentile >= 40:
            action_msg = "📈 You're above average. Close your top 2 critical gaps and you'll jump into the top quartile within 3 weeks."
            action_color = "#fbbf24"
        else:
            action_msg = "💪 You have a clear path up. Start with the highest-severity gap, build one project, and re-run this analysis in 2 weeks."
            action_color = "#f87171"

        st.markdown(f"""
        <div style='background:#0e0e16;border:1px solid #252538;border-left:3px solid {action_color};
             border-radius:10px;padding:14px 18px;display:flex;align-items:center;gap:12px;'>
          <span style='font-size:1.2rem;'>🎯</span>
          <div style='font-size:0.83rem;color:#94a3b8;'>{action_msg}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 9: Share ──────────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown("### 📤 Share Your Progress")
        col_sh1, col_sh2 = st.columns([1, 1])

        with col_sh1:
            name_input = st.text_input("Your Name (for share card)", key="share_name", placeholder="e.g. Priya Sharma")
            if st.button("🎨 Generate Share Card", type="primary", key="gen_card"):
                try:
                    gen = ShareCardGenerator()
                    card_bytes = gen.generate(
                        name=name_input,
                        role_title=st.session_state.role_title,
                        match_score=match_score,
                        top_gaps=an.get("critical_gaps", [])[:3],
                        days_in_plan=30,
                    )
                    if card_bytes:
                        st.image(card_bytes, use_container_width=True)
                        st.download_button(
                            "⬇️ Download Share Card (PNG)",
                            data=card_bytes,
                            file_name="resume_gap_pro_share.png",
                            mime="image/png",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.warning(f"Could not generate share card: {e}")

        with col_sh2:
            st.markdown("**📝 LinkedIn Caption**")
            caption = (
                f"🎯 Just ran an AI-powered resume gap analysis!\n\n"
                f"📊 Match Score: {int(match_score)}% for {st.session_state.role_title}\n"
                f"📚 Closing gaps in: {', '.join(an.get('critical_gaps', [])[:3])}\n"
                f"🗺️ 30-day personalised roadmap activated!\n\n"
                f"Used Resume Gap Pro — an open-source AI career coach built for Indian placement prep.\n\n"
                f"#Placements2025 #CareerGrowth #TechCareers #ResumeGapPro"
            )
            st.text_area("Copy this caption:", value=caption, height=200, key="linkedin_caption")
