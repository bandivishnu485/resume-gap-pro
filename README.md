# 🎯 Resume Gap Pro

An AI-powered career coaching web application for Indian engineering placement preparation. Upload your resume, paste a job description, and get an instant gap analysis with a personalised week-by-week roadmap, ATS score, salary estimate, mock interview, and 16 more features — all powered by RAG + Gemini LLM, running entirely locally.

---

## ✨ Features (20 Total)

- 🔍 **Gap Analysis** — Identifies critical, optional, and semantic skill gaps
- 🤖 **ATS Compatibility Scorer** — Keyword density, formatting, and section checks
- 📝 **Resume Section Scorer** — Summary, Experience, Skills, Projects — rubric-based grades
- 💰 **Salary Estimator** — Current vs after-upskilling range (2024 Indian market, LPA)
- 👥 **Peer Comparison** — Percentile rank among 800+ peer profiles by role
- 🗺️ **RAG-Grounded Roadmap** — Week-by-week plan using only real, free courses
- 📅 **Calendar Export** — Download study roadmap as RFC-5545 .ics for Google/Outlook Calendar
- 🎤 **Mock Interview Simulator** — Adaptive AI questions on your exact gaps, with scoring
- ✍️ **Resume Rewriter** — Section-by-section AI rewrite targeting the JD
- 📩 **Cover Letter Generator** — 4-paragraph personalised cover letter
- 💼 **LinkedIn Optimiser** — Headline, About section, and skills tailored to the role
- 🧑‍💼 **Mentor Matcher** — Curated Indian tech mentors matched to your gaps + outreach messages
- ⚖️ **Multi-JD Comparator** — Compare up to 5 JDs to find your best match
- 👥 **Team Gap Analyser** — Upload 2–6 resumes, get team skill heatmap + role assignments
- 📊 **Placement Cell Dashboard** — Bulk-analyse 50+ resumes with cohort gap heatmap
- 🛠️ **Project Suggester** — 2 hands-on mini-projects per skill gap
- 📤 **Share Card** — 1200×628px LinkedIn-ready PNG with your score
- 📄 **PDF Report** — Full 13-page professional analysis report
- 🌐 **Vernacular Translation** — Hindi, Telugu, Tamil, Kannada, Bengali output
- ⚡ **Urgency Mode** — Compressed roadmap when interview is < 30 days away

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Streamlit UI                   │
│  app.py │ 01_analysis │ 02_rewriter │ 03_interview│
│          04_compare │ 05_team │ 06_dashboard      │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │      Pipeline Layer    │
         │                       │
         │  resume_parser        │
         │  skill_extractor      │◄── spaCy + skill_taxonomy.json
         │  gap_analyzer         │
         │  ats_checker          │
         │  resume_scorer        │
         │  rag_engine           │◄── FAISS + BM25 + sentence-transformers
         │  roadmap_generator    │◄── Gemini 1.5 Flash (RAG-grounded)
         │  salary_estimator     │◄── salary_data.json
         │  cover_letter         │◄── Gemini
         │  calendar_exporter    │◄── icalendar
         │  interview_simulator  │◄── Gemini (adaptive)
         │  share_card           │◄── Pillow
         │  mentor_matcher       │◄── Static curated list + Gemini
         │  pdf_report           │◄── fpdf2
         │  vernacular           │◄── deep-translator
         │  peer_stats           │◄── peer_stats.json
         │  project_suggester    │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │      Data Layer       │
         │  courses.json (60+)   │
         │  skill_taxonomy.json  │
         │  salary_data.json     │
         │  company_profiles.json│
         │  peer_stats.json      │
         └───────────────────────┘
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- A free [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone & Install

```bash
git clone https://github.com/your-username/resume-gap-pro.git
cd resume-gap-pro

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GOOGLE_API_KEY=your_key_here
```

### 3. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📸 Screenshots

| Gap Analysis | Roadmap | Mock Interview |
|---|---|---|
| *(Add screenshot)* | *(Add screenshot)* | *(Add screenshot)* |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Google Gemini 1.5 Flash (free tier) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS (local, CPU) |
| BM25 | rank-bm25 |
| NLP | spaCy (en_core_web_lg) |
| PDF Parsing | PyMuPDF (fitz) |
| PDF Export | fpdf2 |
| Calendar | icalendar (RFC 5545) |
| Translation | deep-translator (Google) |
| Visualisation | Plotly + Matplotlib |
| Image Gen | Pillow |
| Data | Pandas, NumPy |

---

## 🗺️ Feature Roadmap

- [ ] Resume version history & progress tracking
- [ ] GitHub Actions CI for automated test suite
- [ ] Integration with NPTEL course completion API
- [ ] Personalised peer-to-peer study group matching
- [ ] WhatsApp/Telegram bot interface for mobile users
- [ ] Voice-based mock interview mode
- [ ] Resume template generator (ATS-optimised)
- [ ] Placement season calendar integration (company visit dates)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Submit a Pull Request with a clear description

Please follow PEP 8 and add docstrings to all new classes and functions.

---

## 📄 License

MIT License — free for personal and educational use.

---

*Built with ❤️ for Indian engineering students by the Resume Gap Pro team.*
