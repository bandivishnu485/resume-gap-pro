"""
ATS Checker — Standalone ATS compatibility analysis.
"""
from __future__ import annotations
import re


class ATSChecker:
    """Analyses resume ATS compatibility against a job description."""

    SECTION_KEYWORDS = [
        "experience", "education", "skills", "projects",
        "certifications", "summary", "objective",
    ]
    ACTION_VERBS = [
        "built", "developed", "designed", "implemented", "created",
        "led", "managed", "deployed", "optimised", "improved",
        "delivered", "launched", "scaled", "engineered", "automated",
    ]
    STOPWORDS = {
        "the", "and", "for", "are", "with", "this", "that", "have",
        "from", "will", "your", "our", "their", "about", "able", "also",
        "been", "has", "was", "not", "but", "can", "they", "which",
    }

    def check(
        self,
        resume_text: str,
        jd_text: str,
        format_issues: list[str],
    ) -> dict:
        """
        Full ATS compatibility check.

        Returns dict with ats_score, keyword_score, format_score,
        missing_keywords, format_issues, and recommendations.
        """
        lower_resume = resume_text.lower()
        lower_jd = jd_text.lower()

        # --- Keyword density (40 pts) ---
        jd_tokens = set(re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', lower_jd)) - self.STOPWORDS
        resume_tokens = set(re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', lower_resume)) - self.STOPWORDS
        matched_kw = jd_tokens & resume_tokens
        missing_kw = sorted(
            [k for k in (jd_tokens - resume_tokens) if len(k) > 4],
            key=len, reverse=True
        )[:25]
        kw_ratio = len(matched_kw) / max(len(jd_tokens), 1)
        keyword_score = min(40, round(kw_ratio * 55))

        # --- Format score (30 pts) ---
        format_score = max(0, 30 - len(format_issues) * 7)

        # --- Section header presence (20 pts) ---
        found_sections = [s for s in self.SECTION_KEYWORDS if s in lower_resume]
        section_score = min(20, round(len(found_sections) / len(self.SECTION_KEYWORDS) * 28))
        missing_sections = [s.capitalize() for s in self.SECTION_KEYWORDS[:4] if s not in lower_resume]

        # --- Action verbs & quantification (10 pts) ---
        verb_count = sum(1 for v in self.ACTION_VERBS if v in lower_resume)
        has_metrics = bool(re.search(r'\d+\s*(%|percent|\bx\b|times|lpa|cr|lakhs?)', lower_resume))
        verb_score = min(6, verb_count)
        metric_score = 4 if has_metrics else 0

        total_score = min(100, keyword_score + format_score + section_score + verb_score + metric_score)

        # --- Recommendations ---
        recs = []
        if keyword_score < 25:
            recs.append(
                "🔑 Keyword gap: Mirror JD language in your skills and experience sections. "
                "Copy exact terms — 'Python' not 'py'."
            )
        if format_issues:
            recs.append(
                f"📐 Format: Fix {len(format_issues)} formatting issue(s). "
                "Use single-column layout, standard fonts, and no tables."
            )
        if missing_sections:
            recs.append(
                f"📋 Missing sections: Add clearly labelled {', '.join(missing_sections)} sections."
            )
        if verb_count < 5:
            recs.append(
                "⚡ Action verbs: Replace passive language with active verbs — "
                "built, deployed, optimised, delivered, scaled."
            )
        if not has_metrics:
            recs.append(
                "📊 Quantify: Add metrics to every achievement. Example: "
                "'Reduced API latency by 40%', 'Served 10k daily active users'."
            )
        if not recs:
            recs.append("✅ Great ATS compatibility! Keep your keywords updated with each application.")

        return {
            "ats_score": total_score,
            "keyword_score": keyword_score,
            "format_score": format_score,
            "section_score": section_score,
            "action_verb_score": verb_score + metric_score,
            "missing_keywords": missing_kw,
            "format_issues": format_issues,
            "missing_sections": missing_sections,
            "recommendations": recs,
            "has_metrics": has_metrics,
            "verb_count": verb_count,
        }
