"""
Salary Estimator — Estimates current and post-upskilling salary range.
"""
from __future__ import annotations
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


class SalaryEstimator:
    """Estimates salary ranges based on role and match score."""

    ROLE_MAP = {
        "machine learning": "Machine Learning Engineer",
        "ml engineer": "Machine Learning Engineer",
        "ml": "Machine Learning Engineer",
        "data scientist": "Data Scientist",
        "data analyst": "Data Analyst",
        "data engineer": "Data Engineer",
        "devops": "DevOps Engineer",
        "sre": "DevOps Engineer",
        "full stack": "Full Stack Developer",
        "fullstack": "Full Stack Developer",
        "mern": "Full Stack Developer",
        "frontend": "Frontend Developer",
        "front-end": "Frontend Developer",
        "backend": "Backend Engineer",
        "back-end": "Backend Engineer",
        "software engineer": "Software Engineer",
        "software developer": "Software Engineer",
        "sde": "Software Engineer",
        "product manager": "Product Manager",
        "pm": "Product Manager",
    }

    BRACKET_ORDER = ["0-40", "40-60", "60-80", "80-100"]

    def __init__(self):
        with open(DATA_DIR / "salary_data.json", encoding="utf-8") as f:
            self.salary_data: dict = json.load(f)

    def estimate(self, role_title: str, match_score: float, gap_data: dict = None) -> dict:
        """
        Estimate current and post-gap-closure salary range.

        Returns:
            {
                "current": {"min": int, "max": int, "label": "₹X–Y LPA"},
                "after_upskilling": {"min": int, "max": int, "label": "₹X–Y LPA"},
                "increase": str,
                "note": str
            }
        """
        role_key = self._match_role(role_title)
        role_data = self.salary_data.get(role_key, self.salary_data["Software Engineer"])

        current_bracket = self._bracket(match_score)
        after_bracket = self._next_bracket(current_bracket)

        current = role_data.get(current_bracket, role_data["40-60"])
        after = role_data.get(after_bracket, role_data["80-100"])

        increase_min = after["min"] - current["min"]
        increase_max = after["max"] - current["max"]

        return {
            "current": {**current, "label": f"₹{current['min']}–{current['max']} LPA"},
            "after_upskilling": {**after, "label": f"₹{after['min']}–{after['max']} LPA"},
            "increase": f"₹{increase_min}–{increase_max} LPA potential increase",
            "note": (
                "Estimates based on 2024 Indian market data. Actual offers vary by company size, "
                "city, and negotiation. IITs/NITs may command 30-50% premium."
            ),
            "role_matched": role_key,
            "current_bracket": current_bracket,
            "after_bracket": after_bracket,
        }

    def _match_role(self, role_title: str) -> str:
        lower = role_title.lower()
        for keyword, canonical in self.ROLE_MAP.items():
            if keyword in lower:
                return canonical
        return "Software Engineer"

    def _bracket(self, score: float) -> str:
        if score < 40:
            return "0-40"
        if score < 60:
            return "40-60"
        if score < 80:
            return "60-80"
        return "80-100"

    def _next_bracket(self, bracket: str) -> str:
        idx = self.BRACKET_ORDER.index(bracket) if bracket in self.BRACKET_ORDER else 0
        return self.BRACKET_ORDER[min(idx + 1, len(self.BRACKET_ORDER) - 1)]
