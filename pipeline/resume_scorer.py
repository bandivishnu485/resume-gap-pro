"""
Resume Scorer — Section-by-section resume quality scoring.
"""
from __future__ import annotations
import re


class ResumeScorer:
    """Scores each resume section on quality rubrics."""

    TECH_KEYWORDS = [
        "python", "java", "c++", "javascript", "sql", "react", "node", "django",
        "flask", "fastapi", "docker", "kubernetes", "aws", "tensorflow", "pytorch",
        "machine learning", "deep learning", "api", "git", "linux", "mongodb",
        "postgresql", "redis", "kafka", "spark", "hadoop", "tableau", "excel",
    ]
    ACTION_VERBS = [
        "built", "developed", "designed", "implemented", "created", "led",
        "managed", "deployed", "optimised", "improved", "delivered", "launched",
        "scaled", "engineered", "automated", "integrated", "collaborated",
        "researched", "analysed", "maintained", "refactored", "coordinated",
    ]
    GRADE_MAP = {(90, 101): "A+", (80, 90): "A", (70, 80): "B+",
                 (60, 70): "B", (50, 60): "C+", (40, 50): "C", (0, 40): "D"}

    def score(self, sections: dict, resume_data: dict) -> dict:
        """
        Score each resume section and return rubric-based scores.

        Returns:
            {
                "summary": {"score": int, "feedback": str},
                "experience": {"score": int, "feedback": str},
                "skills": {"score": int, "feedback": str},
                "projects": {"score": int, "feedback": str},
                "overall": int,
                "grade": str
            }
        """
        result = {}

        result["summary"] = self._score_summary(sections.get("summary", ""))
        result["experience"] = self._score_experience(
            sections.get("experience", ""), resume_data
        )
        result["skills"] = self._score_skills(
            sections.get("skills", ""), resume_data
        )
        result["projects"] = self._score_projects(sections.get("projects", ""))

        # Weighted overall
        weights = {"summary": 0.15, "experience": 0.40, "skills": 0.25, "projects": 0.20}
        overall = round(sum(result[k]["score"] * w for k, w in weights.items()))
        result["overall"] = overall
        result["grade"] = self._get_grade(overall)
        return result

    # ------------------------------------------------------------------

    def _score_summary(self, text: str) -> dict:
        score = 0
        feedback = []
        words = len(text.split())

        # Length rubric (ideal: 50-100 words)
        if 50 <= words <= 100:
            score += 35
        elif 30 <= words < 50:
            score += 20
            feedback.append("Expand your summary to 50–100 words for optimal ATS performance.")
        elif words > 100:
            score += 20
            feedback.append("Summary is too long — trim to under 100 words.")
        elif words > 0:
            score += 10
            feedback.append("Summary is too brief. Write 2–3 sentences about your background, skills, and goal.")
        else:
            feedback.append("No summary section found. Add a 2–3 sentence professional summary.")

        # Role clarity
        role_words = ["engineer", "developer", "analyst", "scientist", "manager", "designer", "architect"]
        if any(r in text.lower() for r in role_words):
            score += 30
        else:
            feedback.append("Mention your target role explicitly in the summary.")

        # Skill mentions
        skill_hits = sum(1 for kw in self.TECH_KEYWORDS if kw in text.lower())
        if skill_hits >= 3:
            score += 25
        elif skill_hits >= 1:
            score += 15
            feedback.append("Name 2–3 key technical skills in your summary.")
        else:
            feedback.append("Include your core technical skills in the summary.")

        # No generic filler phrases
        fillers = ["hardworking", "passionate", "team player", "go-getter", "dynamic"]
        if any(f in text.lower() for f in fillers):
            score = max(0, score - 10)
            feedback.append("Avoid generic filler phrases like 'passionate' or 'hardworking'. Be specific.")
        else:
            score += 10

        return {"score": min(100, score), "feedback": " ".join(feedback) or "Excellent summary!"}

    def _score_experience(self, text: str, resume_data: dict) -> dict:
        score = 0
        feedback = []

        # Action verbs
        verbs = resume_data.get("action_verbs", [])
        if len(verbs) >= 8:
            score += 35
        elif len(verbs) >= 4:
            score += 20
            feedback.append("Add more action verbs to each bullet point.")
        elif len(verbs) >= 1:
            score += 10
            feedback.append("Use strong action verbs to start every bullet: built, deployed, optimised.")
        else:
            feedback.append("No action verbs detected. Rewrite bullets to start with action verbs.")

        # Quantification
        if resume_data.get("has_metrics"):
            score += 35
        else:
            feedback.append(
                "No metrics found. Add percentages, user counts, or performance numbers to every achievement."
            )

        # Content length (detail indicator)
        word_count = len(text.split())
        if word_count >= 200:
            score += 20
        elif word_count >= 100:
            score += 12
            feedback.append("Add more detail to your experience bullets.")
        else:
            feedback.append("Experience section is sparse — expand with responsibilities and outcomes.")

        # Date/timeline presence
        if re.search(r'(20\d{2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', text.lower()):
            score += 10
        else:
            feedback.append("Include dates for each position (e.g., June 2022 – May 2023).")

        return {"score": min(100, score), "feedback": " ".join(feedback) or "Strong experience section!"}

    def _score_skills(self, text: str, resume_data: dict) -> dict:
        score = 0
        feedback = []

        tech_count = len(resume_data.get("technical", []))
        if tech_count >= 12:
            score += 45
        elif tech_count >= 7:
            score += 30
            feedback.append("Expand your technical skills list for better keyword coverage.")
        elif tech_count >= 3:
            score += 15
            feedback.append("Your skills section is thin — list all relevant tools and technologies.")
        else:
            feedback.append("Very few skills listed. This is critical for ATS — list all your technologies.")

        # Category organisation
        categories = ["language", "framework", "tool", "database", "cloud", "library"]
        organised = any(c in text.lower() for c in categories)
        if organised:
            score += 25
        else:
            feedback.append("Organise skills into categories: Languages, Frameworks, Tools, Databases.")

        # Soft skills presence
        soft_count = len(resume_data.get("soft", []))
        if soft_count >= 2:
            score += 15
        else:
            feedback.append("Include 2–3 soft skills relevant to your target role.")

        # Length adequacy
        if len(text) > 150:
            score += 15

        return {"score": min(100, score), "feedback": " ".join(feedback) or "Excellent skills section!"}

    def _score_projects(self, text: str) -> dict:
        score = 0
        feedback = []

        if not text.strip():
            return {
                "score": 15,
                "feedback": "No projects section found. Add 2–3 projects with tech stack, outcomes, and links."
            }

        # Tech stack mention
        tech_hits = sum(1 for kw in self.TECH_KEYWORDS if kw in text.lower())
        if tech_hits >= 4:
            score += 35
        elif tech_hits >= 2:
            score += 20
            feedback.append("Mention the specific tech stack for each project.")
        else:
            feedback.append("List the technologies used in each project explicitly.")

        # Outcome indicators
        outcomes = ["deployed", "github", "live", "users", "api", "performance", "accuracy", "f1", "precision"]
        outcome_hits = sum(1 for o in outcomes if o in text.lower())
        if outcome_hits >= 3:
            score += 35
        elif outcome_hits >= 1:
            score += 20
            feedback.append("Add project outcomes: deployment status, user count, or performance metrics.")
        else:
            feedback.append("Describe the impact of each project. Who used it? What was the result?")

        # Complexity indicators
        complexity = ["restful", "api", "database", "model", "neural", "cloud", "microservice", "containeris"]
        complexity_hits = sum(1 for c in complexity if c in text.lower())
        if complexity_hits >= 2:
            score += 20
        else:
            score += 10
            feedback.append("Include technically complex projects to stand out.")

        # GitHub/link presence
        if re.search(r'(github\.com|deployed|live at|hosted|demo)', text.lower()):
            score += 10
        else:
            feedback.append("Add GitHub links or deployment URLs to your projects.")

        return {"score": min(100, score), "feedback": " ".join(feedback) or "Great projects section!"}

    @staticmethod
    def _get_grade(score: int) -> str:
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        return "D"
