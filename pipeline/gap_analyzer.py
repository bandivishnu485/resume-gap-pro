"""
Gap Analyzer — Core gap computation, ATS scoring, and resume section scoring.
"""
from __future__ import annotations
import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
import json
import re
from pathlib import Path
from typing import Optional

try:
    from sentence_transformers import SentenceTransformer, util
    _sbert_model = None
    def _get_sbert():
        global _sbert_model
        if _sbert_model is None:
            _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
        return _sbert_model
except ImportError:
    def _get_sbert():
        return None

DATA_DIR = Path(__file__).parent.parent / "data"


class GapAnalyzer:
    """Computes skill gaps between resume and job description."""

    SEVERITY_THRESHOLDS = {
        "High": 0.85,    # weight >= 0.85 → High
        "Medium": 0.70,  # weight >= 0.70 → Medium
        "Low": 0.0,      # else Low
    }

    def __init__(self):
        self.model = _get_sbert()
        with open(DATA_DIR / "company_profiles.json", encoding="utf-8") as f:
            self.company_profiles: dict = json.load(f)
        with open(DATA_DIR / "salary_data.json", encoding="utf-8") as f:
            self.salary_data: dict = json.load(f)
        with open(DATA_DIR / "skill_taxonomy.json", encoding="utf-8") as f:
            self.taxonomy: dict = json.load(f)

    # ------------------------------------------------------------------
    # Core gap computation
    # ------------------------------------------------------------------

    def compute_gaps(
        self,
        resume_skills: dict,
        jd_data: dict,
        company: Optional[str] = None,
    ) -> dict:
        """
        Compute skill gaps between resume and JD, with optional company weighting.

        Returns dict with match_score, gaps, severities, etc.
        """
        resume_all = set(s.lower() for s in resume_skills.get("all", []))
        required = [s.lower() for s in jd_data.get("required_skills", [])]
        preferred = [s.lower() for s in jd_data.get("preferred_skills", [])]
        jd_soft = [s.lower() for s in jd_data.get("soft_skills", [])]

        # Exact matched skills
        matched = [s for s in required if s in resume_all]
        critical_gaps = [s for s in required if s not in resume_all]
        optional_gaps = [s for s in preferred if s not in resume_all]
        soft_gaps = [s for s in jd_soft if s not in set(rs.lower() for rs in resume_skills.get("soft", []))]
        bonus_skills = [s for s in resume_all if s not in required and s not in preferred]

        # Semantic gap detection (for gaps not exact-matched)
        semantic_gaps = self._semantic_gap_check(critical_gaps, resume_all)

        # Compute match score
        total_required = max(len(required), 1)
        raw_score = len(matched) / total_required * 100

        # Severity mapping
        severity = {}
        for gap in critical_gaps:
            meta = self.taxonomy.get(gap, {})
            weight = meta.get("weight", 0.5)
            if weight >= 0.85:
                severity[gap] = "High"
            elif weight >= 0.70:
                severity[gap] = "Medium"
            else:
                severity[gap] = "Low"

        for gap in optional_gaps:
            severity[gap] = "Low"

        # Company-specific weighting
        weighted_score = raw_score
        company_tip = ""
        if company and company in self.company_profiles:
            profile = self.company_profiles[company]
            weights = profile.get("weights", {})
            company_tip = profile.get("tip", "")
            focus_areas = [f.lower() for f in profile.get("focus", [])]

            # Boost score if resume has focus-area skills; penalise if missing
            focus_matched = sum(1 for f in focus_areas if any(f in s for s in resume_all))
            focus_ratio = focus_matched / max(len(focus_areas), 1)
            weighted_score = raw_score * 0.7 + focus_ratio * 100 * 0.3
            weighted_score = min(100, weighted_score)

        return {
            "match_score": round(raw_score, 1),
            "weighted_score": round(weighted_score, 1),
            "matched_skills": matched,
            "critical_gaps": critical_gaps,
            "optional_gaps": optional_gaps,
            "soft_gaps": soft_gaps,
            "bonus_skills": list(bonus_skills)[:10],
            "semantic_gaps": semantic_gaps,
            "severity": severity,
            "company_tip": company_tip,
            "role_title": jd_data.get("role_title", "Software Engineer"),
        }

    def _semantic_gap_check(self, critical_gaps: list, resume_skills: set) -> list:
        """Use sentence-transformers to find semantically close matches."""
        if not self.model or not critical_gaps or not resume_skills:
            return []

        semantic_gaps = []
        try:
            gap_embeddings = self.model.encode(critical_gaps, convert_to_tensor=True)
            resume_list = list(resume_skills)
            resume_embeddings = self.model.encode(resume_list, convert_to_tensor=True)

            for i, gap in enumerate(critical_gaps):
                scores = util.cos_sim(gap_embeddings[i], resume_embeddings)[0]
                max_score = float(scores.max())
                if max_score < 0.5:  # No close semantic match found
                    semantic_gaps.append(gap)
        except Exception:
            pass

        return semantic_gaps

    # ------------------------------------------------------------------
    # ATS score
    # ------------------------------------------------------------------

    def compute_ats_score(
        self,
        resume_text: str,
        jd_text: str,
        format_issues: list,
    ) -> dict:
        """
        Compute ATS compatibility score.

        Returns dict with ats_score, breakdown, and recommendations.
        """
        lower_resume = resume_text.lower()
        lower_jd = jd_text.lower()

        # Keyword score (40 points)
        jd_words = set(re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', lower_jd))
        resume_words = set(re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', lower_resume))
        stopwords = {"the", "and", "for", "are", "with", "this", "that", "have", "from",
                     "will", "you", "your", "our", "their", "about", "able", "also", "been"}
        jd_keywords = jd_words - stopwords
        matched_kw = jd_keywords & resume_words
        missing_kw = jd_keywords - resume_words
        kw_ratio = len(matched_kw) / max(len(jd_keywords), 1)
        keyword_score = min(40, round(kw_ratio * 50))

        # Format score (30 points)
        format_score = max(0, 30 - len(format_issues) * 6)

        # Section presence score (20 points)
        required_sections = ["experience", "education", "skills"]
        section_hits = sum(1 for s in required_sections if s in lower_resume)
        section_score = round(section_hits / len(required_sections) * 20)

        # Action verb & metric score (10 points)
        action_verbs = ["built", "developed", "led", "managed", "designed", "implemented",
                        "delivered", "improved", "optimised", "deployed"]
        verb_hits = sum(1 for v in action_verbs if v in lower_resume)
        has_metrics = bool(re.search(r'\d+\s*(%|percent|x|times)', lower_resume))
        av_score = min(6, verb_hits) + (4 if has_metrics else 0)

        ats_score = keyword_score + format_score + section_score + av_score

        # Top missing keywords (meaningful ones)
        important_missing = sorted(
            [kw for kw in missing_kw if len(kw) > 4],
            key=len, reverse=True
        )[:20]

        recommendations = []
        if keyword_score < 25:
            recommendations.append("Add more keywords from the JD directly into your skills section.")
        if format_issues:
            recommendations.append("Fix formatting issues: avoid tables, columns, and images.")
        if section_hits < 3:
            recommendations.append("Ensure your resume has clearly labelled Experience, Education, and Skills sections.")
        if verb_hits < 4:
            recommendations.append("Use stronger action verbs: built, delivered, optimised, deployed.")
        if not has_metrics:
            recommendations.append("Add quantified achievements: '40% faster', '10k users', '₹2L cost saved'.")

        return {
            "ats_score": min(100, ats_score),
            "keyword_score": keyword_score,
            "format_score": format_score,
            "section_score": section_score,
            "action_verb_score": av_score,
            "missing_keywords": important_missing,
            "format_issues": format_issues,
            "recommendations": recommendations,
        }

    # ------------------------------------------------------------------
    # Resume section scorer
    # ------------------------------------------------------------------

    def score_resume_sections(self, sections: dict, resume_data: dict) -> dict:
        """Score each resume section on rubric criteria."""

        scores = {}

        # Summary
        summary_text = sections.get("summary", "")
        summary_words = len(summary_text.split())
        s_score = 0
        s_feedback = []
        if summary_words >= 30:
            s_score += 40
        elif summary_words > 0:
            s_score += 20
            s_feedback.append("Summary is too short — aim for 50–100 words.")
        if any(kw in summary_text.lower() for kw in ["engineer", "developer", "analyst", "scientist", "manager"]):
            s_score += 30
        else:
            s_feedback.append("Summary should mention your target role explicitly.")
        if summary_words <= 100:
            s_score += 30
        else:
            s_feedback.append("Summary is too long — keep it under 100 words.")
        scores["summary"] = {"score": min(100, s_score), "feedback": " ".join(s_feedback) or "Well-structured summary!"}

        # Experience
        exp_text = sections.get("experience", "")
        action_verbs_count = len(resume_data.get("action_verbs", []))
        has_metrics = resume_data.get("has_metrics", False)
        e_score = 0
        e_feedback = []
        if action_verbs_count >= 6:
            e_score += 40
        elif action_verbs_count >= 3:
            e_score += 25
            e_feedback.append("Use more action verbs: built, delivered, optimised, led.")
        else:
            e_feedback.append("Experience section lacks strong action verbs.")
        if has_metrics:
            e_score += 40
        else:
            e_feedback.append("Add numbers and metrics to quantify your achievements.")
        if len(exp_text) > 200:
            e_score += 20
        else:
            e_feedback.append("Experience section seems sparse — add more detail.")
        scores["experience"] = {"score": min(100, e_score), "feedback": " ".join(e_feedback) or "Strong experience section!"}

        # Skills
        skills_text = sections.get("skills", "")
        tech_count = len(resume_data.get("technical", []))
        sk_score = 0
        sk_feedback = []
        if tech_count >= 10:
            sk_score += 50
        elif tech_count >= 5:
            sk_score += 30
            sk_feedback.append("List more relevant technical skills for better ATS matching.")
        else:
            sk_score += 10
            sk_feedback.append("Skills section has very few skills — expand it significantly.")
        if len(skills_text) > 100:
            sk_score += 30
        if any(cat in skills_text.lower() for cat in ["languages", "frameworks", "tools", "databases"]):
            sk_score += 20
        else:
            sk_feedback.append("Organise skills into categories: Languages, Frameworks, Tools, Databases.")
        scores["skills"] = {"score": min(100, sk_score), "feedback": " ".join(sk_feedback) or "Good skills section!"}

        # Projects
        projects_text = sections.get("projects", "")
        pr_score = 0
        pr_feedback = []
        tech_mentioned = sum(1 for tech in ["python", "react", "node", "sql", "docker", "api", "ml", "flask", "django"]
                             if tech in projects_text.lower())
        if tech_mentioned >= 3:
            pr_score += 40
        elif tech_mentioned >= 1:
            pr_score += 20
            pr_feedback.append("Mention specific technologies used in each project.")
        if len(projects_text) > 300:
            pr_score += 30
        elif len(projects_text) > 100:
            pr_score += 15
            pr_feedback.append("Expand project descriptions to show scope and impact.")
        if re.search(r'(github|deployed|live|hosted|users|downloads)', projects_text.lower()):
            pr_score += 30
        else:
            pr_feedback.append("Add GitHub links or deployment outcomes to your projects.")
        scores["projects"] = {"score": min(100, pr_score), "feedback": " ".join(pr_feedback) or "Projects section looks good!"}

        # Overall
        section_weights = {"summary": 0.15, "experience": 0.40, "skills": 0.25, "projects": 0.20}
        overall = sum(scores[k]["score"] * w for k, w in section_weights.items() if k in scores)
        scores["overall"] = round(overall)

        return scores

    # ------------------------------------------------------------------
    # Salary estimation
    # ------------------------------------------------------------------

    def estimate_salary(self, role_title: str, match_score: float) -> dict:
        """Estimate salary range from salary_data.json."""
        # Fuzzy match role title
        role_key = self._fuzzy_role_match(role_title)
        if role_key not in self.salary_data:
            role_key = "Software Engineer"

        bracket = self._get_salary_bracket(match_score)
        role_data = self.salary_data[role_key]
        current = role_data.get(bracket, role_data.get("40-60", {}))

        # After-upskilling: assume one bracket higher
        next_bracket = self._next_bracket(bracket)
        after = role_data.get(next_bracket, role_data.get("80-100", {}))

        return {
            "current_range": current,
            "after_gap_closure": after,
            "currency": "LPA",
        }

    def _fuzzy_role_match(self, role_title: str) -> str:
        role_lower = role_title.lower()
        if "machine learning" in role_lower or "ml engineer" in role_lower:
            return "Machine Learning Engineer"
        if "data scientist" in role_lower:
            return "Data Scientist"
        if "data analyst" in role_lower:
            return "Data Analyst"
        if "data engineer" in role_lower:
            return "Data Engineer"
        if "devops" in role_lower or "sre" in role_lower:
            return "DevOps Engineer"
        if "full stack" in role_lower or "fullstack" in role_lower:
            return "Full Stack Developer"
        if "frontend" in role_lower or "front-end" in role_lower:
            return "Frontend Developer"
        if "backend" in role_lower or "back-end" in role_lower:
            return "Backend Engineer"
        if "product manager" in role_lower:
            return "Product Manager"
        return "Software Engineer"

    @staticmethod
    def _get_salary_bracket(score: float) -> str:
        if score < 40:
            return "0-40"
        if score < 60:
            return "40-60"
        if score < 80:
            return "60-80"
        return "80-100"

    @staticmethod
    def _next_bracket(bracket: str) -> str:
        order = ["0-40", "40-60", "60-80", "80-100"]
        idx = order.index(bracket) if bracket in order else 0
        return order[min(idx + 1, len(order) - 1)]

    # ------------------------------------------------------------------
    # Multi-JD comparison
    # ------------------------------------------------------------------

    def compare_multiple_jds(self, resume_skills: dict, jds: list[dict]) -> list[dict]:
        """Run gap analysis for each JD and return sorted results."""
        results = []
        for jd in jds:
            jd_data = jd.get("jd_data", {})
            role_name = jd.get("role_name", jd_data.get("role_title", "Unknown Role"))
            gap_result = self.compute_gaps(resume_skills, jd_data)
            gap_result["role_name"] = role_name
            results.append(gap_result)

        results.sort(key=lambda r: r["match_score"], reverse=True)

        for i, r in enumerate(results):
            score = r["match_score"]
            gap_count = len(r["critical_gaps"])
            if score >= 70:
                r["recommendation"] = "Apply now — you meet the core requirements."
            elif score >= 50:
                r["recommendation"] = f"Apply with {max(1, gap_count // 2)} week(s) of prep."
            else:
                r["recommendation"] = f"Target after closing {gap_count} critical gap(s)."

        return results
