"""Page 2 — AI & Rule-Based Resume Rewriter, Cover Letter, LinkedIn Optimiser, Mentor Match."""
import streamlit as st
import sys, os
import re
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from pipeline.cover_letter import CoverLetterGenerator
from pipeline.mentor_matcher import MentorMatcher

try:
    import google.generativeai as genai
    _key = os.getenv("GOOGLE_API_KEY", "").strip()
    if _key:
        genai.configure(api_key=_key)
    HAS_GEMINI = bool(_key)
except Exception:
    HAS_GEMINI = False

st.set_page_config(page_title="Rewriter — Resume Gap Pro", page_icon="✍️", layout="wide")

# Shared state defaults
from app import _defaults
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ----------------------------------------------------------------------
# Advanced Rule-Based Enhancer (Template Engine with X-Y-Z Formula)
# ----------------------------------------------------------------------
VERB_REPLACEMENTS = [
    (r"\bworked on\b", "Spearheaded development of"),
    (r"\bwas responsible for\b", "Engineered and delivered"),
    (r"\bresponsible for\b", "Engineered and delivered"),
    (r"\bbuilt\b", "Architected and deployed"),
    (r"\bmade\b", "Designed and implemented"),
    (r"\bhelped with\b", "Collaborated to optimize"),
    (r"\bhandled\b", "Orchestrated and managed"),
    (r"\bused\b", "Leveraged"),
    (r"\bcreated\b", "Pioneered and created"),
    (r"\badded\b", "Integrated"),
    (r"\bfixed\b", "Resolved and optimized"),
]

QUANTIFIED_SUFFIXES = [
    "reducing response latency by 35%.",
    "serving over 5,000+ active user requests.",
    "improving overall execution speed by 40%.",
    "increasing test coverage to 90%+ across modules.",
    "reducing database query overhead by 25%.",
    "streamlining deployment time by 50%.",
]

def _enhance_text_with_xyz(text: str, mode: str = "ats", missing_keywords: list = None) -> str:
    """Enhance text using power action verbs, missing keywords, and X-Y-Z metric formulas."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return text

    kw_list = [k.title() for k in (missing_keywords or [])]
    enhanced_lines = []

    for idx, line in enumerate(lines):
        enhanced_line = line
        # Replace weak verbs
        for pattern, replacement in VERB_REPLACEMENTS:
            enhanced_line = re.sub(pattern, replacement, enhanced_line, flags=re.IGNORECASE)

        # Inject missing keyword if applicable
        if kw_list and idx < len(kw_list) and not any(kw.lower() in line.lower() for kw in kw_list[:3]):
            kw_to_add = kw_list[idx % len(kw_list)]
            if not enhanced_line.endswith("."):
                enhanced_line += "."
            enhanced_line += f" (Utilized **{kw_to_add}** for system optimization)."

        # Ensure bullet point styling
        if not enhanced_line.startswith("•") and not enhanced_line.startswith("-"):
            enhanced_line = "• " + enhanced_line

        # Add Google X-Y-Z metric formula if mode is xyz and no numbers present
        if mode == "xyz" and not re.search(r"\d+%", enhanced_line) and not re.search(r"\d+", enhanced_line):
            suffix = QUANTIFIED_SUFFIXES[idx % len(QUANTIFIED_SUFFIXES)]
            if enhanced_line.endswith("."):
                enhanced_line = enhanced_line[:-1]
            enhanced_line += f", {suffix}"

        enhanced_lines.append(enhanced_line)

    return "\n".join(enhanced_lines)


def _template_rewrite(sec_name: str, sec_text: str, role_title: str, required_skills: list, missing_keywords: list, mode: str = "ats") -> str:
    """Advanced fallback template engine."""
    skills_str = ", ".join(s.title() for s in required_skills[:6]) if required_skills else "Software Engineering, System Design & Clean Code"
    kw_str = ", ".join(k.title() for k in (missing_keywords or [])[:4])

    if sec_name == "summary":
        if mode == "xyz":
            return (
                f"High-impact {role_title} with strong technical foundation in {skills_str}. "
                f"Engineered and deployed scalable applications delivering 35%+ performance optimizations across project implementations. "
                f"Currently mastering {kw_str or 'modern software engineering standards'} to drive production-ready software solutions."
            )
        elif mode == "senior":
            return (
                f"Results-driven {role_title} candidate with proven expertise in architecting end-to-end software solutions in {skills_str}. "
                f"Demonstrated track record of clean code architecture, cross-functional engineering collaboration, and performance tuning. "
                f"Passionate about applying rigorous engineering practices to solve complex product challenges."
            )
        else:
            return (
                f"Results-driven {role_title} with a strong technical foundation in {skills_str}. "
                f"Experienced in building, testing, and deploying robust software applications with emphasis on reliability and clean code. "
                f"Actively expanding expertise in {kw_str or 'scalable system architecture'} to deliver immediate engineering value."
            )

    elif sec_name == "skills":
        req_formatted = "\n• ".join(s.title() for s in required_skills[:8]) if required_skills else "Software Engineering"
        missing_formatted = "\n• ".join(k.title() for k in (missing_keywords or [])[:5])
        return (
            f"**Core Technical Skills:**\n• {req_formatted}\n\n"
            f"**Tools, Frameworks & Libraries:**\n• Git, Docker, REST APIs, Linux CLI, Postman, PyTest\n\n"
            f"**Target Role Competencies (In Progress / Proficient):**\n• {missing_formatted or 'System Design, CI/CD, Agile'}"
        )

    elif sec_name == "experience":
        return _enhance_text_with_xyz(sec_text, mode=mode, missing_keywords=missing_keywords)

    elif sec_name == "projects":
        return _enhance_text_with_xyz(sec_text, mode=mode, missing_keywords=missing_keywords)

    return sec_text


def _css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
    body,.stApp{background:#08080c!important;}
    .main .block-container{padding-top:0!important;max-width:1280px!important;}
    section[data-testid="stSidebar"]{background:#0e0e16!important;border-right:1px solid #1e1e2e!important;}
    section[data-testid="stSidebar"] .stMarkdown *{color:#4a4a6a!important;}
    .stButton>button{font-weight:600!important;border-radius:10px!important;transition:all .2s ease!important;}
    .stButton>button[kind="primary"]{background:linear-gradient(135deg,#7c6af7,#a78bfa)!important;border:none!important;color:white!important;box-shadow:0 4px 20px rgba(124,106,247,.4)!important;}
    .stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;box-shadow:0 10px 28px rgba(124,106,247,.5)!important;}
    .stButton>button[kind="secondary"]{background:#12121c!important;border:1px solid #252538!important;color:#94a3b8!important;}
    div[data-testid="metric-container"]{background:#12121c!important;border:1px solid #252538!important;border-radius:14px!important;padding:16px!important;}
    .stTextArea textarea{background:#12121c!important;border:1px solid #252538!important;border-radius:10px!important;color:#f0f0f8!important;}
    .stTextArea textarea:focus{border-color:#7c6af7!important;box-shadow:0 0 0 3px rgba(124,106,247,.15)!important;}
    .stTextArea label,.stTextInput label,.stSelectbox label{color:#6b6b8a!important;}
    .stTextInput input{background:#12121c!important;border:1px solid #252538!important;border-radius:9px!important;color:#f0f0f8!important;}
    .streamlit-expanderHeader{background:#12121c!important;border:1px solid #252538!important;border-radius:10px!important;color:#94a3b8!important;font-weight:600!important;}
    .stAlert{border-radius:10px!important;}
    hr{border-color:#1e1e2e!important;}
    h1,h2,h3{color:#f0f0f8!important;}
    </style>""", unsafe_allow_html=True)
_css()

if not st.session_state.get("analysis"):
    st.markdown("""
    <div style='background:#12121c;border:1px solid #252538;border-left:3px solid #fbbf24;
         border-radius:12px;padding:20px 24px;margin:40px 0;'>
      <div style='font-size:1rem;font-weight:700;color:#fbbf24;margin-bottom:4px;'>Analysis Required</div>
      <div style='font-size:0.85rem;color:#6b6b8a;'>Run the Gap Analysis on Page 1 first to unlock all rewriter features.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

an = st.session_state.analysis
sections = st.session_state.sections
jd_data = st.session_state.jd_data
role_title = st.session_state.role_title
ats_info = an.get("ats", {})
missing_kw = ats_info.get("missing_keywords", [])
gen = CoverLetterGenerator()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#08080c,#0e0814);border-bottom:1px solid #1e1e2e;
     padding:40px 0 32px;margin:0 -4rem 32px;'>
  <div style='max-width:800px;'>
    <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;
         color:#7c6af7;margin-bottom:8px;'>Tools</div>
    <h1 style='font-size:2.4rem;font-weight:800;color:#f0f0f8;letter-spacing:-1px;margin:0 0 8px;'>
      Resume Rewriter & Career Suite
    </h1>
    <p style='font-size:0.9rem;color:#6b6b8a;margin:0;'>
      AI & Rule-Based Section Rewriter (Google X-Y-Z Formula), Cover Letter Generator, LinkedIn Profiler & Mentors.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Step tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Resume Rewriter", "📩 Cover Letter", "💼 LinkedIn", "🧑‍💼 Mentors"])

# ─── Tab 1: Resume Rewriter ───────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div style='background:#12121c;border:1px solid #1e1e2e;border-radius:12px;padding:18px 20px;margin-bottom:20px;'>
      <div style='font-size:0.82rem;color:#94a3b8;'>
        Transform your resume sections using <strong>Google's X-Y-Z Impact Formula</strong> (<em>"Accomplished X, measured by Y, by doing Z"</em>) and natural ATS keyword injection.
      </div>
    </div>
    """, unsafe_allow_html=True)

    has_key = bool(os.getenv("GOOGLE_API_KEY", "").strip())

    # Strategy controls
    col_strat, col_kw_info = st.columns([2, 1])
    with col_strat:
        rewrite_mode = st.radio(
            "Select Rewriting Strategy:",
            options=["ats", "xyz", "senior"],
            format_func=lambda x: {
                "ats": "🎯 ATS Keyword Densification (Inject missing JD keywords + Strong Action Verbs)",
                "xyz": "📊 Quantified Google X-Y-Z Formula (Add metrics, impact percentages & numbers)",
                "senior": "💼 Seniority & Executive Architecture Polish (Leadership & system scale tone)"
            }[x],
            horizontal=False,
            key="rw_mode_select"
        )
    with col_kw_info:
        st.markdown("**🔑 Top Missing Keywords:**")
        if missing_kw:
            for kw in missing_kw[:5]:
                st.markdown(f"<span style='background:#2e1065;color:#c4b5fd;padding:2px 8px;border-radius:99px;font-size:0.7rem;margin:2px;display:inline-block;'>+ {kw}</span>", unsafe_allow_html=True)
        else:
            st.caption("No missing keywords detected! Great job.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("✨  Rewrite with Gemini AI" if has_key else "✨  Rewrite with Gemini AI (Key Required)", type="primary" if has_key else "secondary", key="rewrite_btn", use_container_width=True):
            if not has_key:
                st.warning("⚠️ Please enter your GOOGLE_API_KEY below to use Gemini AI.")
            else:
                with st.spinner("🔄 Rewriting sections with Gemini AI..."):
                    try:
                        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        rewritten = {}
                        for sec_name in ["summary", "skills", "experience", "projects"]:
                            sec_text = sections.get(sec_name, "")
                            if not sec_text.strip():
                                continue
                            prompt = f"""You are an elite Silicon Valley resume writer. Rewrite this {sec_name} section for the target role.
Rules:
- Keep all facts accurate — do NOT invent work experience.
- Apply Google's X-Y-Z formula ("Accomplished X, measured by Y, by doing Z") for bullet points.
- Inject missing ATS keywords naturally: {', '.join(missing_kw[:6])}
- Target Role: {role_title}
- Mode: {rewrite_mode}

ORIGINAL SECTION ({sec_name.upper()}):
{sec_text[:900]}

Return only the rewritten section with strong action verbs and clean markdown bullets."""
                            try:
                                rewritten[sec_name] = model.generate_content(prompt).text
                            except Exception:
                                rewritten[sec_name] = _template_rewrite(sec_name, sec_text, role_title, jd_data.get('required_skills', []), missing_kw, mode=rewrite_mode)
                        st.session_state.rewritten_resume = rewritten
                        st.success("Resume sections rewritten with Gemini AI!")
                    except Exception as e:
                        st.error(f"Rewrite failed: {e}")

    with col_btn2:
        if st.button("⚡  Generate Enhanced Rewrite (Rule & Metric Engine)", type="secondary" if has_key else "primary", key="template_rewrite_btn", use_container_width=True):
            req_skills = jd_data.get("required_skills", [])
            rewritten = {}
            for sec_name in ["summary", "skills", "experience", "projects"]:
                sec_text = sections.get(sec_name, "")
                if sec_text.strip():
                    rewritten[sec_name] = _template_rewrite(sec_name, sec_text, role_title, req_skills, missing_kw, mode=rewrite_mode)
            st.session_state.rewritten_resume = rewritten
            st.success("Generated rule-enhanced, metric-packed resume sections!")

    if not has_key:
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        with st.expander("🔑 Add / Update Free Gemini API Key", expanded=True):
            st.caption("Get a free key in 10 seconds at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
            user_key = st.text_input("Google Gemini API Key", type="password", key="inline_gemini_key", placeholder="AIzaSy...")
            if st.button("Save & Apply Key", key="save_inline_key"):
                if user_key.strip():
                    os.environ["GOOGLE_API_KEY"] = user_key.strip()
                    try:
                        genai.configure(api_key=user_key.strip())
                    except Exception:
                        pass
                    st.success("API Key saved for current session!")
                    st.rerun()

    if st.session_state.get("rewritten_resume"):
        rewritten = st.session_state.rewritten_resume
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Side-by-Side Comparison")

        for sec_name in ["summary", "skills", "experience", "projects"]:
            if sec_name not in rewritten:
                continue
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;margin:24px 0 10px;'>
              <div style='height:1px;flex:1;background:#1e1e2e;'></div>
              <span style='font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                   color:#7c6af7;padding:0 12px;'>{sec_name.title()} Section</span>
              <div style='height:1px;flex:1;background:#1e1e2e;'></div>
            </div>
            """, unsafe_allow_html=True)
            col_orig, col_new = st.columns(2)
            with col_orig:
                st.markdown("<p style='font-size:0.75rem;font-weight:600;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;'>Original Text</p>", unsafe_allow_html=True)
                st.text_area(f"orig_{sec_name}", value=sections.get(sec_name, "")[:800], height=160, disabled=True, label_visibility="collapsed")
            with col_new:
                st.markdown("<p style='font-size:0.75rem;font-weight:600;color:#7c6af7;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;'>✨ Enhanced & Rewritten (X-Y-Z Formatted)</p>", unsafe_allow_html=True)
                st.text_area(f"new_{sec_name}", value=rewritten[sec_name][:1000], height=160, label_visibility="collapsed", key=f"rw_{sec_name}")

        full_rewritten = "\n\n".join(f"# {k.upper()}\n{v}" for k, v in rewritten.items())
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.download_button("⬇️ Download Complete Rewritten Resume (.txt)", data=full_rewritten,
                          file_name=f"rewritten_{role_title.replace(' ','_')}.txt",
                          mime="text/plain", use_container_width=True)

# ─── Tab 2: Cover Letter ──────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div style='background:#12121c;border:1px solid #1e1e2e;border-radius:12px;padding:18px 20px;margin-bottom:20px;'>
      <div style='font-size:0.82rem;color:#6b6b8a;'>
        Generates a 4-paragraph cover letter: opening with your strongest matches, experience highlights,
        proactive gap framing, and a strong closing. Target: 250–350 words.
      </div>
    </div>
    """, unsafe_allow_html=True)

    company_name = st.text_input("🏢 Company Name (optional)", placeholder="e.g. Flipkart, Google, Razorpay")

    if st.button("📝  Generate Cover Letter", type="primary", key="cl_btn", use_container_width=True):
        with st.spinner("✍️ Crafting your cover letter..."):
            try:
                letter = gen.generate(resume_sections=sections, jd_data=jd_data,
                                      gap_data=an, company=company_name or None)
                st.session_state.cover_letter_text = letter
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if st.session_state.get("cover_letter_text"):
        letter = st.session_state.cover_letter_text
        word_count = len(letter.split())
        wc_color = "#4ade80" if 250 <= word_count <= 350 else "#fbbf24"
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
          <span style='font-size:0.8rem;color:#6b6b8a;'>Edit your cover letter below</span>
          <span style='font-size:0.75rem;font-weight:700;color:{wc_color};'>{word_count} words (target 250–350)</span>
        </div>
        """, unsafe_allow_html=True)
        edited = st.text_area("Cover Letter", value=letter, height=380, key="cl_edit", label_visibility="collapsed")
        st.download_button("⬇️ Download Cover Letter (.txt)", data=edited,
                          file_name="cover_letter.txt", mime="text/plain", use_container_width=True)

# ─── Tab 3: LinkedIn ──────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style='background:#12121c;border:1px solid #1e1e2e;border-radius:12px;padding:18px 20px;margin-bottom:20px;'>
      <div style='font-size:0.82rem;color:#6b6b8a;'>
        Generates a keyword-rich LinkedIn headline, a full 2200-character About section,
        and a targeted skills list — all tailored to your gap profile and target role.
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀  Generate LinkedIn Profile", type="primary", key="li_btn", use_container_width=True):
        with st.spinner("Generating LinkedIn optimisation..."):
            try:
                li_data = gen.generate_linkedin_optimisation(resume_sections=sections, gap_data=an, role_title=role_title)
                st.session_state.linkedin_data = li_data
            except Exception as e:
                st.error(f"Failed: {e}")

    if st.session_state.get("linkedin_data"):
        li = st.session_state.linkedin_data
        col_h, col_s = st.columns([3, 1])
        with col_h:
            st.markdown("<p style='font-size:0.75rem;font-weight:700;color:#7c6af7;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;'>📌 Headline</p>", unsafe_allow_html=True)
            headline_val = st.text_area("Headline", value=li.get("headline", ""), height=72, key="li_hl", label_visibility="collapsed")
            st.caption(f"{len(headline_val)}/220 characters")
        with col_s:
            st.markdown("<p style='font-size:0.75rem;font-weight:700;color:#7c6af7;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;'>🛠 Skills to Add</p>", unsafe_allow_html=True)
            for s in li.get("skills_to_add", [])[:6]:
                st.markdown(f"<div style='font-size:0.8rem;color:#94a3b8;padding:3px 0;border-bottom:1px solid #1e1e2e;'>+ {s}</div>", unsafe_allow_html=True)

        st.markdown("<p style='font-size:0.75rem;font-weight:700;color:#7c6af7;text-transform:uppercase;letter-spacing:0.5px;margin:16px 0 6px;'>📝 About Section</p>", unsafe_allow_html=True)
        about_val = st.text_area("About", value=li.get("about", ""), height=280, key="li_about", label_visibility="collapsed")
        ac = len(about_val)
        ac_color = "#4ade80" if ac <= 2200 else "#f87171"
        st.markdown(f"<div style='font-size:0.72rem;color:{ac_color};text-align:right;'>{ac}/2200 characters</div>", unsafe_allow_html=True)

        if li.get("featured_section_idea"):
            st.markdown(f"""
            <div style='background:#0f0525;border:1px solid #4c1d95;border-radius:10px;padding:12px 16px;margin-top:12px;'>
              <span style='font-size:0.72rem;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:0.5px;'>⭐ Featured Section Idea</span>
              <div style='font-size:0.83rem;color:#a78bfa;margin-top:4px;'>{li['featured_section_idea']}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── Tab 4: Mentors ───────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style='background:#12121c;border:1px solid #1e1e2e;border-radius:12px;padding:18px 20px;margin-bottom:20px;'>
      <div style='font-size:0.82rem;color:#6b6b8a;'>
        Curated Indian tech mentors matched to your skill gaps. Includes a ready-to-send
        personalised cold outreach message for each (≤150 words).
      </div>
    </div>
    """, unsafe_allow_html=True)

    matcher = MentorMatcher()
    mentors = matcher.suggest_mentors(an)
    user_bg = sections.get("summary", "")[:200] or sections.get("experience", "")[:200]

    if not mentors:
        st.info("Run gap analysis first to get mentor suggestions.")
    else:
        for i, mentor in enumerate(mentors):
            name = mentor['name']
            role_m = mentor['role']
            expertise = mentor.get('expertise', [])
            why = mentor['why']
            linkedin = mentor['linkedin']
            main_gap = an.get("critical_gaps", ["your target role"])[0]

            exp_tags = "".join(f"<span style='background:#0e0e16;border:1px solid #252538;color:#94a3b8;padding:2px 9px;border-radius:99px;font-size:0.68rem;margin:2px;display:inline-block;'>{e}</span>" for e in expertise[:4])

            st.markdown(f"""
            <div style='background:#0e0e16;border:1px solid #1e1e2e;border-radius:14px;padding:20px;margin-bottom:14px;'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;flex-wrap:wrap;gap:8px;'>
                <div>
                  <div style='font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:2px;'>{name}</div>
                  <div style='font-size:0.8rem;color:#6b6b8a;'>{role_m}</div>
                </div>
                <a href='{linkedin}' target='_blank' style='background:#0a66c2;color:white;padding:6px 14px;
                   border-radius:8px;font-size:0.75rem;font-weight:600;text-decoration:none;'>🔗 LinkedIn</a>
              </div>
              <div style='font-size:0.8rem;color:#94a3b8;margin-bottom:10px;line-height:1.5;'>{why}</div>
              <div>{exp_tags}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"📨 Generate outreach message for {name.split()[0]}"):
                outreach = matcher.generate_outreach_message(mentor, user_bg, main_gap)
                edited_msg = st.text_area("Outreach Message (editable)", value=outreach,
                                          height=180, key=f"msg_{i}_{name.replace(' ','_')}", label_visibility="collapsed")
                wc = len(edited_msg.split())
                wc_col = "#4ade80" if wc <= 150 else "#fbbf24"
                st.markdown(f"<div style='font-size:0.72rem;color:{wc_col};'>{wc} words (target ≤150)</div>", unsafe_allow_html=True)
