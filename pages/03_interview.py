"""Page 3 — Mock Interview Simulator (Fixed with two-phase state machine)."""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.interview_simulator import InterviewSimulator

st.set_page_config(page_title="Mock Interview — Resume Gap Pro", page_icon="🎤", layout="wide")

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
.stButton>button{font-weight:600!important;border-radius:10px!important;transition:all .2s ease!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#7c6af7,#a78bfa)!important;border:none!important;color:white!important;box-shadow:0 4px 20px rgba(124,106,247,.4)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;}
.stButton>button[kind="secondary"]{background:#12121c!important;border:1px solid #252538!important;color:#94a3b8!important;}
.stTextArea textarea{background:#12121c!important;border:1px solid #252538!important;border-radius:10px!important;color:#f0f0f8!important;}
.stTextArea textarea:focus{border-color:#7c6af7!important;box-shadow:0 0 0 3px rgba(124,106,247,.15)!important;}
.stTextArea label{color:#6b6b8a!important;}
.stProgress > div > div{border-radius:99px!important;background:#1e1e2e!important;}
.stProgress > div > div > div{background:linear-gradient(90deg,#7c6af7,#22d3ee)!important;border-radius:99px!important;}
.streamlit-expanderHeader{background:#12121c!important;border:1px solid #252538!important;border-radius:10px!important;color:#94a3b8!important;font-weight:600!important;}
.stAlert{border-radius:10px!important;}
hr{border-color:#1e1e2e!important;}
h1,h2,h3{color:#f0f0f8!important;}
</style>
""", unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("analysis"):
    st.markdown("""
    <div style='background:#12121c;border:1px solid #252538;border-left:3px solid #fbbf24;
         border-radius:12px;padding:20px 24px;margin:40px 0;'>
      <div style='font-size:1rem;font-weight:700;color:#fbbf24;'>Analysis Required</div>
      <div style='font-size:0.85rem;color:#6b6b8a;margin-top:4px;'>Run Gap Analysis (Page 1) first to unlock the mock interview.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

an = st.session_state.get("analysis")
role_title = st.session_state.get("role_title", "Software Engineer")

# ── State initialisation ───────────────────────────────────────────────────────
for key, val in [("interview_session", None), ("interview_performance", []),
                 ("interview_phase", "asking"), ("last_result", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

sim = InterviewSimulator()
top_gaps = an.get("critical_gaps", [])[:3]

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(135deg,#08080c,#0e0814);border-bottom:1px solid #1e1e2e;
     padding:40px 0 32px;margin:0 -4rem 32px;'>
  <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;
       color:#f472b6;margin-bottom:8px;'>Practice Mode</div>
  <h1 style='font-size:2.4rem;font-weight:800;color:#f0f0f8;letter-spacing:-1px;margin:0 0 8px;'>
    AI Mock Interview
  </h1>
  <p style='font-size:0.9rem;color:#6b6b8a;margin:0;'>
    Adaptive questions on your exact skill gaps. Get scored, see model answers, and advance only when you're ready.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Start / Reset ──────────────────────────────────────────────────────────────
if not st.session_state.interview_session:
    # Show gap focus cards
    if top_gaps:
        st.markdown(f"<p style='font-size:0.82rem;color:#6b6b8a;margin-bottom:12px;'>This session will focus on your top gaps:</p>", unsafe_allow_html=True)
        gap_cols = st.columns(len(top_gaps))
        gap_colors = ["#7c6af7", "#22d3ee", "#f472b6"]
        for col, gap, color in zip(gap_cols, top_gaps, gap_colors):
            with col:
                st.markdown(f"""
                <div style='background:#0e0e16;border:1px solid {color}40;border-top:3px solid {color};
                     border-radius:12px;padding:16px;text-align:center;'>
                  <div style='font-size:0.85rem;font-weight:700;color:{color};'>{gap.title()}</div>
                  <div style='font-size:0.72rem;color:#4a4a6a;margin-top:4px;'>3 questions</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if st.button("🚀  Start Interview Session", type="primary", use_container_width=True):
        session = sim.start_session(an, role_title)
        st.session_state.interview_session = session
        st.session_state.interview_performance = []
        st.session_state.interview_phase = "asking"
        st.session_state.last_result = None
        st.rerun()
    st.stop()

# Reset button (top right)
col_info, col_reset = st.columns([4, 1])
with col_reset:
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.interview_session = None
        st.session_state.interview_performance = []
        st.session_state.interview_phase = "asking"
        st.session_state.last_result = None
        st.rerun()

session     = st.session_state.interview_session
performance = st.session_state.interview_performance
questions   = session.get("questions", [])
total_q     = len(questions)
current_idx = session.get("current_index", 0)
phase       = st.session_state.interview_phase

# ── Complete screen ────────────────────────────────────────────────────────────
if current_idx >= total_q:
    st.balloons()
    avg = sum(p.get("score", 5) for p in performance) / max(len(performance), 1)
    score_color = "#4ade80" if avg >= 7 else "#fbbf24" if avg >= 5 else "#f87171"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0e0e16,#12121c);border:1px solid #252538;
         border-radius:16px;padding:32px;text-align:center;margin-bottom:24px;'>
      <div style='font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4a4a6a;margin-bottom:8px;'>Session Complete</div>
      <div style='font-size:4rem;font-weight:900;color:{score_color};line-height:1;'>{avg:.1f}</div>
      <div style='font-size:1rem;color:#6b6b8a;margin-top:4px;'>out of 10</div>
    </div>
    """, unsafe_allow_html=True)

    if performance:
        by_skill = {}
        for p in performance:
            by_skill.setdefault(p["skill"], []).append(p["score"])
        weakest = min(by_skill, key=lambda s: sum(by_skill[s]) / len(by_skill[s]))
        st.markdown(f"""
        <div style='background:#150505;border:1px solid #7f1d1d;border-radius:10px;padding:14px 18px;margin-bottom:16px;'>
          <span style='color:#f87171;font-weight:700;'>📉 Weakest area: {weakest}</span>
          <span style='color:#7f1d1d;font-size:0.83rem;'> — Prioritise this in your roadmap and re-practice here.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 Performance Log")
        for p in performance:
            sc = p.get("score", 5)
            pc = "#4ade80" if sc >= 7 else "#fbbf24" if sc >= 5 else "#f87171"
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #1e1e2e;'>
              <div style='font-size:1.1rem;font-weight:900;color:{pc};min-width:32px;'>{sc}</div>
              <div>
                <div style='font-size:0.82rem;font-weight:600;color:#94a3b8;'>{p['skill'].title()}</div>
                <div style='font-size:0.77rem;color:#4a4a6a;'>{p.get('feedback','')[:80]}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("🔄  New Session", type="primary"):
        st.session_state.interview_session = None
        st.session_state.interview_performance = []
        st.session_state.interview_phase = "asking"
        st.session_state.last_result = None
        st.rerun()
    st.stop()

# ── Progress ───────────────────────────────────────────────────────────────────
st.progress(current_idx / max(total_q, 1), text=f"Question {current_idx+1} of {total_q}")
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

current_q     = questions[current_idx]
question_text = current_q["question"]
skill         = current_q["skill"]

# ── Question card ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#0e0e16,#0c0514);
     border:1px solid #252538;border-left:4px solid #7c6af7;
     border-radius:14px;padding:24px;margin-bottom:20px;'>
  <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;
       color:#7c6af7;margin-bottom:10px;'>
    Q{current_idx+1} · {skill.upper()}
  </div>
  <div style='font-size:1.1rem;font-weight:500;color:#f0f0f8;line-height:1.7;'>
    {question_text}
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# PHASE: ASKING
# ════════════════════════════════════════════════════════════════════════════════
if phase == "asking":
    user_answer = st.text_area(
        "Your Answer",
        height=180,
        placeholder="Structure your answer: define the concept → give a real example → mention trade-offs or edge cases.",
        key=f"answer_{current_idx}",
    )
    sub_col, skip_col = st.columns([4, 1])
    with sub_col:
        submit = st.button("✅  Submit Answer", type="primary", use_container_width=True, key=f"submit_{current_idx}")
    with skip_col:
        skip = st.button("⏭ Skip", use_container_width=True, key=f"skip_{current_idx}")

    if skip:
        session["current_index"] = current_idx + 1
        st.session_state.interview_session = session
        st.session_state.interview_phase = "asking"
        st.rerun()

    if submit and user_answer.strip():
        with st.spinner("🤔 Evaluating..."):
            result = sim.evaluate_answer(question_text, user_answer, skill)
        performance.append({"question": question_text, "answer": user_answer,
                            "score": result.get("score", 5), "feedback": result.get("feedback", ""), "skill": skill})
        st.session_state.interview_performance = performance
        st.session_state.last_result = result
        st.session_state.interview_phase = "feedback"
        st.rerun()
    elif submit:
        st.warning("Please type your answer before submitting.")

# ════════════════════════════════════════════════════════════════════════════════
# PHASE: FEEDBACK — holds screen until user clicks Next
# ════════════════════════════════════════════════════════════════════════════════
elif phase == "feedback":
    result = st.session_state.last_result or {}
    score  = result.get("score", 5)
    color  = "#4ade80" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"
    bg     = "#052e16" if score >= 7 else "#451a03" if score >= 5 else "#450a0a"
    border = "#166534" if score >= 7 else "#78350f" if score >= 5 else "#7f1d1d"
    label  = "Excellent! 🌟" if score >= 8 else "Good 👍" if score >= 6 else "Needs Work 📚"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{bg},{bg}80);border:1px solid {border};
         border-radius:14px;padding:24px;margin-bottom:16px;'>
      <div style='display:flex;align-items:center;gap:20px;margin-bottom:12px;'>
        <div style='font-size:3rem;font-weight:900;color:{color};line-height:1;'>{score}<span style='font-size:1.2rem;'>/10</span></div>
        <div style='font-size:1.1rem;font-weight:700;color:{color};'>{label}</div>
      </div>
      <div style='font-size:0.9rem;color:#94a3b8;line-height:1.65;'>{result.get('feedback','')}</div>
    </div>
    """, unsafe_allow_html=True)

    if result.get("tip"):
        st.markdown(f"""
        <div style='background:#0f0525;border:1px solid #4c1d95;border-radius:10px;padding:12px 16px;margin-bottom:14px;'>
          <span style='color:#c4b5fd;font-size:0.83rem;'>💡 <strong>Tip:</strong> {result['tip']}</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📖 See Model Answer"):
        st.markdown(f"<div style='color:#94a3b8;font-size:0.88rem;line-height:1.7;'>{result.get('model_answer','')}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    next_label = "▶️  Next Question" if current_idx + 1 < total_q else "🏁  View Results"
    if st.button(next_label, type="primary", key=f"next_{current_idx}"):
        session["current_index"] = current_idx + 1
        st.session_state.interview_session = session
        st.session_state.interview_phase = "asking"
        st.session_state.last_result = None
        st.rerun()
