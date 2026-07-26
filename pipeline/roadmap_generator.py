"""
Roadmap Generator — Ultra-detailed, highly accurate LLM & Template powered study roadmap generation.
"""
from __future__ import annotations
import os
import time
import json
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_MODEL = "gemini-1.5-flash"
MAX_RETRIES = 3


# ----------------------------------------------------------------------
# Curriculum Database for Precision Fallbacks & Structure
# ----------------------------------------------------------------------
CURRICULUM_DB = {
    "python": {
        "title": "Python Software Engineering & Best Practices",
        "days": [
            ("Day 1", "Advanced Data Structures & Collections", "Master Lists, Dicts, Sets, `collections` (Counter, defaultdict, deque), and Memory Complexity."),
            ("Day 2", "Object-Oriented Programming (OOP)", "Implement Classes, Inheritance, Polymorphism, Dunder Methods (`__init__`, `__repr__`, `__eq__`), and `@classmethod`."),
            ("Day 3", "Functional Python, Decorators & Generators", "Master First-class Functions, Closures, Custom `@decorators`, Iterators, and Memory-Efficient `yield` Generators."),
            ("Day 4", "Concurrency, AsyncIO & Threading", "Understand GIL (Global Interpreter Lock), `threading` vs `multiprocessing`, and `async`/`await` event loop programming."),
            ("Day 5", "REST API Development with FastAPI / Flask", "Build robust HTTP endpoints, request/response models with Pydantic, and status code handling."),
            ("Day 6", "Unit Testing, Debugging & Code Quality", "Write comprehensive unit tests with `pytest`, mock external calls, and run linter/formatters (`flake8`, `black`)."),
            ("Day 7", "Production Microservice Build", "Build & package a modular REST API or CLI application with structured docstrings and a clean GitHub README."),
        ],
        "practice": "LeetCode Python 3 Track: 2Sum, Group Anagrams, LRU Cache implementation.",
    },
    "sql": {
        "title": "Database Architecture & Advanced SQL Analytics",
        "days": [
            ("Day 1", "Complex Relational JOINs & Subqueries", "Master INNER, LEFT, RIGHT, FULL OUTER JOINs, Self-JOINs, Correlated Subqueries, and `WITH` CTE expressions."),
            ("Day 2", "Window Functions & Analytical Queries", "Master `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LEAD()`, `LAG()`, and `SUM() OVER(PARTITION BY...)`."),
            ("Day 3", "Aggregations & Conditional Logic", "Master `GROUP BY`, `HAVING`, `CASE WHEN` pivoting, handling `NULL` values (`COALESCE`, `NULLIF`)."),
            ("Day 4", "Database Schema Design & Normalization", "Design Entity-Relationship diagrams, 1NF to 3NF normalization, Primary/Foreign keys, Constraints."),
            ("Day 5", "Indexing & Query Optimization", "Understand B-Tree vs Hash Indexes, Composite Indexes, `EXPLAIN ANALYZE` execution plans, and avoiding full table scans."),
            ("Day 6", "Transactions & Database Concurrency", "ACID properties, Isolation Levels (Read Committed, Repeatable Read, Serializable), Row Locking, Deadlocks."),
            ("Day 7", "E-Commerce SQL Analytics Case Study", "Write 10 production-grade SQL analytical queries on a multi-table database schema."),
        ],
        "practice": "LeetCode / HackerRank SQL 50: Department Top Three Salaries, Consecutive Numbers, Tree Node.",
    },
    "data structures": {
        "title": "Data Structures & Algorithms (DSA Mastery)",
        "days": [
            ("Day 1", "Arrays, Strings & Sliding Window", "Two-pointer technique, Sliding Window algorithm, In-place array mutations, Prefix Sums."),
            ("Day 2", "Linked Lists & Fast/Slow Pointers", "Singly & Doubly Linked Lists, Reversing a Linked List, Cycle Detection (Floyd's Algorithm)."),
            ("Day 3", "Stacks, Queues & Hash Tables", "Monotonic Stack, Circular Queue, Custom Hash Table implementation, Collision resolution."),
            ("Day 4", "Trees, BST & Traversals", "Binary Tree BFS & DFS (In-order, Pre-order, Post-order), BST operations, Lowest Common Ancestor."),
            ("Day 5", "Heaps, Priority Queues & Graphs", "Max/Min Heap operations, Graph Adjacency List, BFS, DFS, Topological Sort (Kahn's Algorithm)."),
            ("Day 6", "Dynamic Programming Fundamentals", "1D DP (Memoization vs Tabulation), Fibonacci, Climbing Stairs, Coin Change, 0/1 Knapsack."),
            ("Day 7", "Timed Mock Interview Drill", "Solve 3 LeetCode Medium problems under 45 minutes with optimal time & space complexity explanations."),
        ],
        "practice": "Neetcode 150 / Blind 75 curated problem set.",
    },
    "system design": {
        "title": "Scalable System Architecture & Distributed Systems",
        "days": [
            ("Day 1", "Scalability Foundations & CAP Theorem", "Vertical vs Horizontal Scaling, Stateless vs Stateful servers, CAP & PACELC Theorem trade-offs."),
            ("Day 2", "Load Balancers & API Gateways", "Layer 4 vs Layer 7 Load Balancing, Round-Robin, Least Connections, Consistent Hashing."),
            ("Day 3", "Caching Architecture & Redis", "Cache-Aside, Write-Through, Write-Back patterns, Cache Eviction (LRU, LFU), Cache Stampede."),
            ("Day 4", "Database Sharding & Replication", "Primary-Replica replication, Horizontal Sharding, Sharding Keys, Consistent Hashing."),
            ("Day 5", "Message Queues & Event-Driven Systems", "Asynchronous processing with Apache Kafka / RabbitMQ, Publisher-Subscriber models, Idempotency."),
            ("Day 6", "Resiliency & Rate Limiting", "Token Bucket / Leaky Bucket Rate Limiters, Circuit Breakers, Graceful Degradation."),
            ("Day 7", "End-to-End System Design Blueprint", "Draft full architecture for a URL Shortener (TinyURL) or Real-Time Notification Service with data flow diagrams."),
        ],
        "practice": "System Design Primer: High-Level Architecture Diagrams + Data Flow Specs.",
    },
    "docker": {
        "title": "Containerization & DevOps Workflows",
        "days": [
            ("Day 1", "Container Fundamentals & Docker Engine", "Understand Containers vs VMs, Docker Architecture, Images, Registries, CLI commands (`run`, `ps`, `exec`)."),
            ("Day 2", "Production Dockerfile Authoring", "Write clean Dockerfiles, Base Image selection, Layer Caching, `.dockerignore`, Multi-Stage Builds for small image sizes."),
            ("Day 3", "Docker Networking & Storage", "Bridge, Host & Overlay networks, Named Volumes vs Bind Mounts, Data Persistence."),
            ("Day 4", "Multi-Container Orchestration with Docker Compose", "Define multi-service environments (`docker-compose.yml`), Service Dependencies, Environment Files."),
            ("Day 5", "CI/CD Pipeline Integration", "Build automated GitHub Actions workflow to build, test, and push Docker images to Docker Hub."),
            ("Day 6", "Container Security & Best Practices", "Non-root container user, Scanning vulnerabilities (`trivy`), Environment secret handling."),
            ("Day 7", "Deployment Showcase", "Containerize a Full-Stack application (Frontend + Backend + DB) and deploy to a cloud host."),
        ],
        "practice": "Dockerize a Python REST API + PostgreSQL database setup.",
    },
    "react": {
        "title": "Modern Frontend Development with React & TypeScript",
        "days": [
            ("Day 1", "Modern JavaScript & React Core", "ES6+ Destructuring, Spread, Promises, Async/Await, JSX, Component Lifecycle."),
            ("Day 2", "Hooks Deep Dive", "Master `useState`, `useEffect` cleanup, `useRef`, `useMemo`, `useCallback` for performance."),
            ("Day 3", "State Management & Context API", "Global state management using React Context API or Zustand / Redux Toolkit."),
            ("Day 4", "API Integration & Async State", "Axios/Fetch integration, Loading states, Error handling, Custom Hooks for data fetching."),
            ("Day 5", "Routing & Component Architecture", "React Router v6, Nested Routes, Protected Routes, Dynamic Code-Splitting (`React.lazy`)."),
            ("Day 6", "Form Handling & Validation", "Controlled vs Uncontrolled components, Form validation using React Hook Form + Zod."),
            ("Day 7", "Production Build & Deployment", "Optimize assets, lighthouse performance score check, deploy live on Vercel / Netlify."),
        ],
        "practice": "Build a responsive Analytics Dashboard with live API data.",
    },
    "machine learning": {
        "title": "Applied Machine Learning & Model Engineering",
        "days": [
            ("Day 1", "Data Preprocessing & Exploratory Data Analysis", "Pandas, NumPy, Feature Scaling (StandardScaler, MinMaxScaler), Encoding Categorical Variables."),
            ("Day 2", "Supervised Learning Algorithms", "Linear/Logistic Regression, Decision Trees, Random Forests, Gradient Boosting (XGBoost)."),
            ("Day 3", "Model Evaluation & Metrics", "Confusion Matrix, Precision, Recall, F1-Score, ROC-AUC, Bias-Variance Trade-off."),
            ("Day 4", "Unsupervised Learning & Clustering", "K-Means Clustering, Hierarchical Clustering, PCA Dimensionality Reduction."),
            ("Day 5", "Hyperparameter Optimization & Validation", "Cross-Validation (K-Fold), GridSearchCV, RandomizedSearchCV, Avoiding Data Leakage."),
            ("Day 6", "ML Pipelines & Feature Engineering", "Scikit-Learn Pipelines, ColumnTransformer, Custom Transformers, Feature Selection."),
            ("Day 7", "Model API Deployment", "Export model (`joblib`), build REST API inference endpoint with FastAPI / Streamlit."),
        ],
        "practice": "Kaggle End-to-End Classification Benchmark Project.",
    },
}


class RoadmapGenerator:
    """Generates personalised, highly detailed study roadmaps using Gemini LLM with RAG context."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        else:
            self.model = None

    # ------------------------------------------------------------------
    # Core roadmap generation
    # ------------------------------------------------------------------

    def generate_roadmap(
        self,
        resume_skills: dict,
        gap_data: dict,
        retrieved_courses: dict,
        role_title: str,
        deadline_days: int = 30,
    ) -> str:
        """
        Generate an accurate, day-by-day personalised study roadmap.
        """
        critical_gaps = gap_data.get("critical_gaps", [])
        optional_gaps = gap_data.get("optional_gaps", [])
        matched = gap_data.get("matched_skills", [])

        # Format RAG context
        rag_context = self._format_rag_context(retrieved_courses)

        if deadline_days < 30:
            return self.generate_urgent_roadmap(gap_data, retrieved_courses, deadline_days)

        weeks = max(4, min(8, len(critical_gaps) + 2))
        hours_per_day = max(2, min(5, 90 // max(deadline_days, 1))) if deadline_days > 0 else 3

        system_prompt = (
            "You are a Senior Principal Engineering Coach and Placement Strategist for top Indian product companies (FAANG/Tier-1 Startups). "
            "Generate an ultra-detailed, highly accurate, day-by-day and week-by-week technical study roadmap. "
            "Every single week MUST include explicit Day 1 through Day 7 sub-schedules with exact topic titles, "
            "hands-on coding tasks, specific practice problem names, and quantitative deliverables. "
            "Do NOT give vague summaries like 'study concepts'. Provide specific, actionable technical instructions."
        )

        user_prompt = f"""
CANDIDATE TARGET ROLE: {role_title}
PREPARATION DEADLINE: {deadline_days} Days ({weeks} Weeks)
DAILY TIME COMMITMENT: {hours_per_day} Hours/Day

SKILL PROFILE:
- Matched Skills (Strengths): {', '.join(matched[:8]) or 'Basics'}
- CRITICAL SKILL GAPS TO CLOSE: {', '.join(critical_gaps) or 'Core Computer Science'}
- OPTIONAL/SECONDARY GAPS: {', '.join(optional_gaps[:5]) or 'Secondary tools'}

RECOMMENDED COURSE CONTEXT (USE EXACT TITLES & URLS IN THE PLAN):
{rag_context}

FORMAT REQUIREMENTS:
1. Start with a 4-line Executive Master Strategy Summary.
2. Provide a week-by-week breakdown for {weeks} weeks.
3. FOR EVERY WEEK:
   - State the Primary Focus Skill & Milestone Goal.
   - List EXACT Day 1 through Day 7 schedules with:
     * 📖 Theory & Core Concepts (1.5 hrs)
     * 💻 Hands-on Implementation & Practice (1.5 hrs)
     * 🧪 Recommended Practice Problems / LeetCode / SQL / System Design questions (1 hr)
   - State the Sunday Deliverable & GitHub Project Commit.
4. Include 3 High-Impact Real-World Project Ideas mapped specifically to the critical gaps.
5. Provide a revised 3-line ATS-Optimized Resume Summary statement.
6. Provide Top 5 Technical Interview Screening Questions & Model Answers for the candidate's top gap.

Be thorough, precise, accurate, and realistic!
"""

        fallback_md = self._template_roadmap(
            role_title, critical_gaps, retrieved_courses, deadline_days, hours_per_day
        )

        return self._call_gemini(system_prompt, user_prompt, fallback=fallback_md)

    def generate_urgent_roadmap(
        self,
        gap_data: dict,
        retrieved_courses: dict,
        days_available: int,
    ) -> str:
        """Generate a compressed, high-intensity roadmap for interview < 30 days away."""
        critical_gaps = gap_data.get("critical_gaps", [])[:3]
        if not critical_gaps:
            critical_gaps = ["Data Structures & Algorithms", "System Design"]

        rag_context = self._format_rag_context(
            {k: v for k, v in retrieved_courses.items() if k in critical_gaps}
        )
        role_title = gap_data.get("role_title", "Software Engineer")
        hours_per_day = min(6, max(3, 90 // max(days_available, 1)))

        system_prompt = (
            "You are a High-Intensity Technical Interview Coach specializing in urgent candidate preparation. "
            "Generate a razor-sharp, zero-fluff, day-by-day emergency study roadmap."
        )

        user_prompt = f"""
EMERGENCY INTERVIEW PREPARATION: {days_available} Days Left
TARGET ROLE: {role_title}
TOP 3 CRITICAL GAPS: {', '.join(critical_gaps)}
DAILY COMMITMENT: {hours_per_day} Hours/Day

COURSE CONTEXT:
{rag_context}

Create a day-by-day plan covering all {days_available} days:
- Split each day into Morning Session (Concepts + Course), Afternoon Session (Coding Drills), and Evening Session (Revision & Mock Questions).
- Focus strictly on high-frequency interview topics.
- Include 2 High-Speed Mini-Projects.
- Final 3-Day Sprint Strategy & Mock Interview Checkpoint.
"""

        fallback_md = self._urgent_template_roadmap(role_title, critical_gaps, retrieved_courses, days_available, hours_per_day)
        return self._call_gemini(system_prompt, user_prompt, fallback=fallback_md)

    def generate_interview_questions(self, skill: str, level: str = "fresher") -> dict:
        """Generate interview Q&A for a specific skill."""
        system_prompt = (
            "You are a technical interview coach. Generate realistic interview questions "
            "with model answers. Be specific, not generic."
        )
        user_prompt = f"""
Generate interview questions for: {skill}
Candidate level: {level}

Return JSON (and ONLY JSON, no markdown):
{{
  "conceptual": ["Q1", "Q2", "Q3"],
  "coding": ["Q1", "Q2"],
  "system_design": ["Q1"],
  "model_answers": {{"Q1": "answer", "Q2": "answer"}}
}}
"""
        raw = self._call_gemini(system_prompt, user_prompt, fallback=None)
        if raw:
            try:
                import re
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception:
                pass

        return {
            "conceptual": [
                f"What is {skill} and why is it important?",
                f"Explain the core concepts of {skill}.",
                f"How have you used {skill} in a project?",
            ],
            "coding": [
                f"Write a simple implementation demonstrating {skill}.",
                f"Debug this {skill}-related code snippet.",
            ],
            "system_design": [f"Design a scalable system that uses {skill}."],
            "model_answers": {},
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _call_gemini(self, system_prompt: str, user_prompt: str, fallback: str = "") -> str:
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if HAS_GEMINI and api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content(
                    f"{system_prompt}\n\n{user_prompt}",
                    generation_config={"temperature": 0.7, "max_output_tokens": 3500},
                )
                if response and response.text and len(response.text.strip()) > 100:
                    return response.text
            except Exception:
                pass
        return fallback or "⚠️ Add a valid GOOGLE_API_KEY to enable AI roadmap generation."

    @staticmethod
    def _format_rag_context(retrieved_courses: dict) -> str:
        lines = []
        for skill, courses in retrieved_courses.items():
            lines.append(f"\n**{skill.title()} Courses:**")
            for c in courses:
                lines.append(
                    f"  - {c.get('course_name', 'Unknown')} "
                    f"({c.get('platform', '')}, {c.get('duration', '')}, "
                    f"{'Free' if c.get('free') else 'Paid'}) — {c.get('url', '')}"
                )
        return "\n".join(lines) if lines else "No specific courses retrieved."

    # ------------------------------------------------------------------
    # Domain-Aware Comprehensive Template Generators (Fallbacks)
    # ------------------------------------------------------------------

    @staticmethod
    def _template_roadmap(
        role_title: str,
        critical_gaps: list,
        retrieved_courses: dict,
        deadline_days: int,
        hours_per_day: int,
    ) -> str:
        """Detailed, domain-aware fallback roadmap template."""
        if not critical_gaps:
            critical_gaps = ["data structures", "system design", "sql"]

        weeks = max(4, min(8, len(critical_gaps) + 1))
        per_gap_weeks = max(1, weeks // max(len(critical_gaps), 1))

        md = f"""# 🗺️ Master Technical Study Roadmap: {role_title}

> **Target Goal:** Close **{len(critical_gaps)} Critical Skill Gap(s)** in **{deadline_days} Days** ({weeks} Weeks) at **{hours_per_day} Hours/Day**.
> **Strategy:** Structured 7-day technical sprints with daily concepts, hands-on coding drills, course modules, and GitHub deliverables.

---

## 📌 Executive Strategy Summary
1. **Focus:** Eliminate critical gaps (**{', '.join(g.title() for g in critical_gaps[:4])}**) with structured daily practice.
2. **Pacing:** {hours_per_day} hours daily split into: 1.5h Theory & Video, 1.5h Hands-on Implementation, 1h Problem Solving.
3. **Outcome:** Ship 3 production-ready GitHub repository projects and pass placement technical screenings.

---
"""

        current_week = 1
        for gap_idx, gap in enumerate(critical_gaps[:weeks]):
            gap_key = gap.lower()
            matching_key = next((k for k in CURRICULUM_DB if k in gap_key), None)
            curr = CURRICULUM_DB.get(matching_key) if matching_key else None

            courses = retrieved_courses.get(gap, [])
            course_info = ""
            if courses:
                c = courses[0]
                course_info = f"📖 **Primary Course:** [{c.get('course_name')}]({c.get('url')}) ({c.get('platform')}, {c.get('duration')})"
            else:
                course_info = f"📖 **Recommended Track:** Search top Coursera/YouTube tracks for *{gap.title()}*"

            for w in range(per_gap_weeks):
                if current_week > weeks:
                    break

                week_title = curr['title'] if (curr and w == 0) else f"{gap.title()} Core Mastery & Integration"

                md += f"""
## 📅 Week {current_week}: {week_title}
{course_info}

**Weekly Goal:** Build deep proficiency in {gap.title()} and complete daily hands-on implementation drills.

"""
                if curr and w == 0:
                    for day_name, topic, desc in curr["days"]:
                        md += f"""### 🔹 {day_name}: {topic}
- 📚 **Theory & Video (1.5h):** {desc}
- 💻 **Hands-On Coding (1.5h):** Build a small script or demo implementing {topic}.
- 🧪 **Drills & Practice (1h):** {curr.get('practice', 'Solve 3 targeted exercises on this concept.')}

"""
                else:
                    days_default = [
                        ("Day 1", f"{gap.title()} Architecture & Core Principles", "Study core definitions, architectural patterns, and foundational mechanics."),
                        ("Day 2", f"{gap.title()} Deep Dive & Advanced Mechanics", "Explore internal workings, optimization techniques, and performance considerations."),
                        ("Day 3", f"{gap.title()} Framework & Library Integration", "Integrate with standard industry frameworks, APIs, and tooling."),
                        ("Day 4", f"{gap.title()} Testing, Debugging & Edge Cases", "Write unit tests, handle exception boundaries, and profile performance."),
                        ("Day 5", f"{gap.title()} Production Best Practices", "Implement security, logging, metrics, and standard coding guidelines."),
                        ("Day 6", f"{gap.title()} Mini-Project Implementation", "Combine learnings into a multi-file modular repository component."),
                        ("Day 7", f"{gap.title()} Code Review & Documentation", "Refactor code, write comprehensive Markdown README, push to GitHub."),
                    ]
                    for day_name, topic, desc in days_default:
                        md += f"""### 🔹 {day_name}: {topic}
- 📚 **Theory & Video (1.5h):** {desc}
- 💻 **Hands-On Coding (1.5h):** Write clean, modular code demonstrating {topic}.
- 🧪 **Drills & Practice (1h):** Solve 2 interview-level questions on this concept.

"""

                md += f"""**🏆 Sunday Milestone:** Push tested code for {gap.title()} to GitHub + document learnings in your study log.

---
"""
                current_week += 1

        md += f"""
## 🛠️ High-Impact Portfolio Project Blueprint

### Project 1: {critical_gaps[0].title() if critical_gaps else 'Core'} Enterprise Microservice
- **Goal:** Showcase enterprise-grade application design using {critical_gaps[0].title() if critical_gaps else 'Python/Java'}.
- **Key Features:** REST API endpoints, input validation, robust error handling, unit test suite.
- **Deliverable:** GitHub repo with architectural diagram, setup instructions, and demo GIF.

### Project 2: Multi-Skill Integration Application
- **Goal:** Combine {', '.join(g.title() for g in critical_gaps[:2])} into a unified end-to-end system.
- **Key Features:** Database persistence, caching layer, modular service layer.
- **Deliverable:** Containerized application with Docker Compose configuration.

---

## 📝 ATS-Optimized Resume Summary Statement
*Results-driven {role_title} candidate with hands-on proficiency in {', '.join(g.title() for g in critical_gaps[:3])}. Demonstrated experience in building scalable microservices, optimizing database performance, and writing clean, tested code. Passionate about solving complex software engineering challenges.*

---
*💪 Tip: Consistency beats intensity! Complete your daily 3-hour blocks without distraction.*
"""
        return md

    @staticmethod
    def _urgent_template_roadmap(
        role_title: str,
        critical_gaps: list,
        retrieved_courses: dict,
        days_available: int,
        hours_per_day: int,
    ) -> str:
        """Detailed emergency roadmap fallback for urgent deadlines."""
        md = f"""# ⚡ Emergency {days_available}-Day Interview Preparation Plan: {role_title}

> 🚨 **High Intensity Warning:** You have **{days_available} days** left until your interview.
> **Daily Target:** {hours_per_day} hours/day strictly focused on high-yield placement topics.

---

## 🎯 Top Priority Focus Areas
{chr(10).join(f"{i+1}. **{gap.title()}** — High-frequency interview topic" for i, gap in enumerate(critical_gaps[:3]))}

---
"""
        for day in range(1, days_available + 1):
            gap_focus = critical_gaps[(day - 1) % max(len(critical_gaps), 1)]
            md += f"""
### ⚡ Day {day}: High-Yield Focus on {gap_focus.title()}
- 🌅 **Morning Session ({hours_per_day // 2}h):** Intensive review of core definitions, syntax, and top 5 interview questions for {gap_focus.title()}.
- 🌆 **Afternoon/Evening Session ({hours_per_day - (hours_per_day // 2)}h):** Hands-on problem solving — complete 3 top LeetCode / Interview questions.
- 📝 **Daily Checkpoint:** Write down 3 key concepts in flashcard format for fast pre-interview review.
"""

        md += """
---
## 🏁 Final 24-Hour Checklist
1. Review your past project READMEs and prepare 2-minute elevator pitches for each.
2. Re-read core CS fundamentals (OS, DBMS, Networks, OOP).
3. Ensure your resume formatting is clean and ready.
"""
        return md
