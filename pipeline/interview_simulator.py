"""
Interview Simulator — Adaptive AI-powered mock interview engine.
"""
from __future__ import annotations
import os
import json
import re
import time
import warnings
warnings.filterwarnings("ignore")

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


class InterviewSimulator:
    """Adaptive mock interview simulator powered by Gemini."""

    QUESTION_TEMPLATES = {
        "python": [
            "Explain the difference between a list and a tuple in Python. When would you use each?",
            "What are Python decorators? Write a simple example.",
            "How does Python's GIL (Global Interpreter Lock) affect multithreading?",
        ],
        "machine learning": [
            "Explain the bias-variance tradeoff with an example.",
            "What is the difference between bagging and boosting?",
            "How would you handle imbalanced datasets in a classification problem?",
        ],
        "system design": [
            "Design a URL shortening service like bit.ly. Walk me through your approach.",
            "How would you design a notification system that can handle 1 million users?",
            "Design the backend for a ride-sharing app like Ola.",
        ],
        "data structures": [
            "Explain the time complexity of common HashMap operations and when they degrade.",
            "When would you use a heap over a sorted array?",
            "Explain how quicksort works and its average vs worst-case complexity.",
        ],
        "sql": [
            "What is the difference between INNER JOIN and LEFT JOIN? Give an example.",
            "Explain window functions in SQL. Write a query using ROW_NUMBER().",
            "How would you optimise a slow SQL query?",
        ],
        "docker": [
            "What is the difference between a Docker image and a Docker container?",
            "Explain the purpose of a Dockerfile. Write one for a Python Flask app.",
            "What is Docker Compose used for?",
        ],
    }

    DEFAULT_QUESTIONS = [
        "Tell me about yourself and your technical background.",
        "What is your most complex project? Walk me through the architecture.",
        "How do you approach learning a new technology quickly?",
    ]

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model = None
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)

    def start_session(self, gap_data: dict, role_title: str) -> dict:
        """
        Initialise an interview session focused on top 3 gaps.

        Returns session_state dict with questions queue.
        """
        top_gaps = gap_data.get("critical_gaps", [])[:3]
        if not top_gaps:
            top_gaps = ["python", "data structures", "system design"]

        questions = []
        for gap in top_gaps:
            gap_lower = gap.lower()
            # Pick 3 questions per gap
            gap_questions = self.QUESTION_TEMPLATES.get(gap_lower, self.DEFAULT_QUESTIONS)
            for q in gap_questions[:3]:
                questions.append({"question": q, "skill": gap, "difficulty": "medium"})

        return {
            "role_title": role_title,
            "gaps_covered": top_gaps,
            "questions": questions,
            "current_index": 0,
            "performance": [],
            "session_active": True,
        }

    def evaluate_answer(self, question: str, user_answer: str, skill: str) -> dict:
        """
        Evaluate user answer with Gemini. Returns score, feedback, model answer.
        """
        if not user_answer or len(user_answer.strip()) < 20:
            return {
                "score": 1,
                "feedback": "Answer is too brief. Please provide a complete, detailed response.",
                "model_answer": self._get_template_answer(skill, question),
                "follow_up_question": f"Can you elaborate more on {skill}?",
                "tip": f"Always explain your reasoning, not just the answer.",
            }

        prompt = f"""
You are a strict but fair technical interviewer evaluating a candidate for a software engineering role.

QUESTION: {question}
SKILL BEING TESTED: {skill}
CANDIDATE'S ANSWER: {user_answer}

Evaluate the answer and return ONLY valid JSON (no markdown, no explanation):
{{
  "score": <integer 1-10>,
  "feedback": "<2-3 sentences: what was good, what was missing, be specific>",
  "model_answer": "<Ideal 4-6 sentence answer that would score 10/10>",
  "follow_up_question": "<A natural follow-up question based on their answer>",
  "tip": "<One specific actionable tip to improve their answer>"
}}

Scoring guide:
1-3: Major misconceptions or very incomplete
4-5: Basic understanding but missing key points
6-7: Good understanding, minor gaps
8-9: Strong answer, nearly complete
10: Perfect — clear, accurate, with example
"""
        raw = self._call_gemini(prompt)
        if raw:
            try:
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    # Ensure all keys are present
                    result.setdefault("score", 5)
                    result.setdefault("feedback", "Good attempt. Review the model answer for improvements.")
                    result.setdefault("model_answer", self._get_template_answer(skill, question))
                    result.setdefault("follow_up_question", f"Can you give a real-world example of {skill}?")
                    result.setdefault("tip", f"Practice explaining {skill} concepts in simple terms.")
                    return result
            except Exception:
                pass

        # Fallback evaluation
        word_count = len(user_answer.split())
        score = min(7, max(3, word_count // 20))
        return {
            "score": score,
            "feedback": (
                f"You provided a {word_count}-word response. "
                "Ensure you cover the core concept, a concrete example, and edge cases."
            ),
            "model_answer": self._get_template_answer(skill, question),
            "follow_up_question": f"How would you apply {skill} in a production system?",
            "tip": f"Structure your answer: define the concept → give an example → mention trade-offs.",
        }

    def generate_next_question(self, session_state: dict, performance: list[dict]) -> str:
        """
        Adaptive question selection based on previous performance.

        If score < 5: easier follow-up on same skill
        If score > 7: harder follow-up
        """
        questions = session_state.get("questions", [])
        current_idx = session_state.get("current_index", 0)

        if not performance:
            return questions[0]["question"] if questions else "Tell me about yourself."

        last_score = performance[-1].get("score", 5) if performance else 5
        last_skill = performance[-1].get("skill", "") if performance else ""

        # Move to next question in queue
        next_idx = current_idx + 1
        if next_idx < len(questions):
            next_q = questions[next_idx]

            # Adapt difficulty
            if last_score < 5 and last_skill == next_q.get("skill"):
                # Easier rephrasing
                return f"Let me rephrase — explain {last_skill} in the simplest possible terms with an example."
            elif last_score > 7:
                # Harder follow-up
                harder_prompts = {
                    "python": "Now explain Python's memory management and garbage collection.",
                    "machine learning": "How would you deploy this model to production with monitoring?",
                    "system design": "How would you scale this to 100M users? What breaks first?",
                    "data structures": "Can you write the implementation from scratch? What's the space complexity?",
                }
                if last_skill.lower() in harder_prompts:
                    return harder_prompts[last_skill.lower()]

            return next_q["question"]

        return "That concludes our session! Let me summarise your performance."

    def _call_gemini(self, prompt: str) -> str:
        if not self.model:
            return ""
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.5, "max_output_tokens": 800},
                )
                return resp.text
            except Exception:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        return ""

    @staticmethod
    def _get_template_answer(skill: str, question: str) -> str:
        templates = {
            "python": "Python is a high-level, interpreted language known for its readability. Key concepts include dynamic typing, first-class functions, and the extensive standard library. For example, decorators use the @syntax to wrap functions, allowing cross-cutting concerns like logging without modifying core logic.",
            "machine learning": "Machine learning involves training statistical models on data to make predictions. The key trade-off is bias vs variance: high bias models underfit (too simple), high variance models overfit (too complex). Regularisation, cross-validation, and ensemble methods help manage this.",
            "system design": "System design requires understanding requirements (scale, latency, consistency), then choosing appropriate components: load balancers for traffic distribution, caching layers (Redis) for speed, databases chosen for access patterns (SQL for ACID, NoSQL for scale/flexibility), and message queues for async processing.",
            "data structures": "The right data structure depends on the operations needed: arrays for O(1) index access, hash maps for O(1) key lookup, trees for sorted data with O(log n) operations, and graphs for relationship modelling. Always analyse time and space complexity before choosing.",
            "sql": "SQL is the standard query language for relational databases. JOINs combine tables on matching keys — INNER returns only matched rows, LEFT returns all left rows with nulls for unmatched right rows. Window functions like ROW_NUMBER(), RANK(), and SUM() OVER() enable powerful analytical queries without collapsing rows.",
            "docker": "Docker containers package code and dependencies into isolated, portable units. A Dockerfile defines the image build steps (FROM → RUN → COPY → CMD). Containers are instances of images. Docker Compose orchestrates multi-container apps with a YAML config defining services, networks, and volumes.",
        }
        skill_lower = skill.lower()
        for key, answer in templates.items():
            if key in skill_lower:
                return answer
        return f"A strong answer to '{question}' would cover: the core concept definition, a concrete example, trade-offs or edge cases, and a real-world application. Practice explaining it in under 2 minutes."
