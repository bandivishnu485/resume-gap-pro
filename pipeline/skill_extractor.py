"""
Skill Extractor — NLP-based skill identification from resume and JD text.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

try:
    import spacy
    _nlp = None
    def _get_nlp():
        global _nlp
        if _nlp is None:
            try:
                _nlp = spacy.load("en_core_web_lg")
            except OSError:
                try:
                    _nlp = spacy.load("en_core_web_sm")
                except OSError:
                    _nlp = None
        return _nlp
except ImportError:
    def _get_nlp():
        return None


TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "skill_taxonomy.json"

ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "created", "led", "managed",
    "architected", "deployed", "optimised", "improved", "reduced", "increased",
    "automated", "integrated", "collaborated", "mentored", "trained", "researched",
    "analysed", "delivered", "launched", "scaled", "maintained", "migrated",
    "refactored", "tested", "documented", "coordinated", "spearheaded", "directed",
    "drove", "facilitated", "established", "streamlined", "engineered", "solved"
]

JD_SOFT_SIGNALS = {
    "communication": ["communicate", "communication", "verbal", "written", "presentation"],
    "leadership": ["lead", "leadership", "manage", "mentor", "guide", "oversee"],
    "teamwork": ["team", "collaborate", "cross-functional", "cooperative", "together"],
    "problem solving": ["solve", "problem-solving", "analytical", "troubleshoot", "debug"],
    "ownership": ["ownership", "initiative", "proactive", "accountability", "responsible"],
    "adaptability": ["adapt", "flexible", "fast learner", "quick learner", "dynamic"],
}


class SkillExtractor:
    """Extracts technical and soft skills from resume sections and job descriptions."""

    def __init__(self):
        self.nlp = _get_nlp()
        with open(TAXONOMY_PATH, encoding="utf-8") as f:
            self.taxonomy: dict = json.load(f)

        # Build reverse alias map: alias_lower -> canonical_skill
        self.alias_map: dict[str, str] = {}
        for skill, meta in self.taxonomy.items():
            self.alias_map[skill.lower()] = skill
            for alias in meta.get("aliases", []):
                self.alias_map[alias.lower()] = skill

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def extract_from_resume(self, sections: dict) -> dict:
        """
        Extract skills from parsed resume sections.

        Returns:
            {
                "technical": [...],
                "soft": [...],
                "tools": [...],
                "action_verbs": [...],
                "has_metrics": bool,
                "all": [...]
            }
        """
        full_text = " ".join(sections.values()).lower()

        technical, soft, tools = [], [], []

        for alias, canonical in self.alias_map.items():
            if self._phrase_in_text(alias, full_text):
                meta = self.taxonomy.get(canonical, {})
                if meta.get("soft"):
                    if canonical not in soft:
                        soft.append(canonical)
                elif meta.get("category") == "tools":
                    if canonical not in tools:
                        tools.append(canonical)
                else:
                    if canonical not in technical:
                        technical.append(canonical)

        # Action verbs from experience/projects
        exp_text = (sections.get("experience", "") + " " + sections.get("projects", "")).lower()
        found_verbs = [v for v in ACTION_VERBS if v in exp_text]

        # Metric presence
        has_metrics = bool(re.search(r'\d+\s*(%|percent|x|times|lpa|lakhs?|k\b|million)', full_text))

        all_skills = list({*technical, *soft, *tools})

        return {
            "technical": technical,
            "soft": soft,
            "tools": tools,
            "action_verbs": found_verbs,
            "has_metrics": has_metrics,
            "all": all_skills,
        }

    def extract_from_jd(self, jd_text: str) -> dict:
        """
        Extract requirements from a job description.

        Returns:
            {
                "required_skills": [...],
                "preferred_skills": [...],
                "soft_skills": [...],
                "experience_years": int,
                "seniority": str,
                "role_title": str,
                "action_verbs_expected": [...]
            }
        """
        lower_jd = jd_text.lower()

        required_skills, preferred_skills, soft_skills = [], [], []

        # Split into required vs preferred blocks
        required_block, preferred_block = self._split_required_preferred(jd_text)

        for alias, canonical in self.alias_map.items():
            meta = self.taxonomy.get(canonical, {})
            if meta.get("soft"):
                if self._phrase_in_text(alias, lower_jd):
                    if canonical not in soft_skills:
                        soft_skills.append(canonical)
            else:
                if self._phrase_in_text(alias, required_block.lower()):
                    if canonical not in required_skills:
                        required_skills.append(canonical)
                elif self._phrase_in_text(alias, preferred_block.lower()):
                    if canonical not in preferred_skills:
                        preferred_skills.append(canonical)
                elif self._phrase_in_text(alias, lower_jd):
                    if canonical not in required_skills and canonical not in preferred_skills:
                        required_skills.append(canonical)

        # Experience years
        exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)', lower_jd)
        experience_years = int(exp_match.group(1)) if exp_match else 0

        # Seniority
        seniority = "fresher"
        if re.search(r'\b(senior|sr\.?|lead|principal|architect|staff)\b', lower_jd):
            seniority = "senior"
        elif re.search(r'\b(mid|middle|associate|ii)\b', lower_jd):
            seniority = "mid"
        elif experience_years >= 3:
            seniority = "mid"

        # Role title (first line heuristic)
        role_title = self._extract_role_title(jd_text)

        # Expected action verbs from JD
        expected_verbs = [v for v in ACTION_VERBS if v in lower_jd]

        return {
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "soft_skills": soft_skills,
            "experience_years": experience_years,
            "seniority": seniority,
            "role_title": role_title,
            "action_verbs_expected": expected_verbs,
        }

    def extract_soft_gaps(self, resume_data: dict, jd_data: dict) -> list[str]:
        """
        Compare expected soft signals vs what's in the resume.

        Returns list of missing soft skill signals.
        """
        resume_soft = set(s.lower() for s in resume_data.get("soft", []))
        resume_verbs = set(resume_data.get("action_verbs", []))
        jd_soft = set(s.lower() for s in jd_data.get("soft_skills", []))
        jd_verbs = set(jd_data.get("action_verbs_expected", []))

        missing = []
        for skill in jd_soft:
            if skill not in resume_soft:
                missing.append(skill)

        # Check for verb presence signals
        leadership_verbs = {"led", "managed", "coordinated", "spearheaded", "directed", "mentored"}
        if "leadership" in jd_soft and not (resume_verbs & leadership_verbs):
            if "leadership" not in missing:
                missing.append("leadership (no leadership verbs found in resume)")

        return missing

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _phrase_in_text(phrase: str, text: str) -> bool:
        """Check if phrase occurs as a word-bounded match in text."""
        pattern = r'\b' + re.escape(phrase) + r'\b'
        return bool(re.search(pattern, text))

    @staticmethod
    def _split_required_preferred(jd_text: str) -> tuple[str, str]:
        """Split JD into required and preferred sections."""
        lower = jd_text.lower()
        preferred_keywords = ["preferred", "nice to have", "good to have", "bonus", "plus"]
        required_keywords = ["required", "must have", "must-have", "essential", "mandatory"]

        split_idx = len(jd_text)
        for kw in preferred_keywords:
            idx = lower.find(kw)
            if idx != -1 and idx < split_idx:
                split_idx = idx

        required_block = jd_text[:split_idx]
        preferred_block = jd_text[split_idx:]
        return required_block, preferred_block

    @staticmethod
    def _extract_role_title(jd_text: str) -> str:
        """Extract role title from first meaningful line of JD."""
        common_roles = [
            "Machine Learning Engineer", "Software Engineer", "Data Scientist",
            "Data Analyst", "Backend Engineer", "Full Stack Developer",
            "DevOps Engineer", "Frontend Developer", "Data Engineer",
            "Product Manager", "ML Engineer", "AI Engineer",
            "Software Developer", "SDE", "SDE-1", "SDE-2",
        ]
        for role in common_roles:
            if role.lower() in jd_text.lower():
                return role

        # Fallback: first non-empty line ≤ 50 chars
        for line in jd_text.split("\n")[:5]:
            stripped = line.strip()
            if 3 < len(stripped) <= 60:
                return stripped

        return "Software Engineer"
