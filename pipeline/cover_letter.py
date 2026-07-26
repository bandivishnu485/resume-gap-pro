"""
Cover Letter Generator & LinkedIn Optimiser.
"""
from __future__ import annotations
import os
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


def _get_model():
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not HAS_GEMINI or not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)


def _call_gemini(model, prompt: str, fallback: str = "") -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if HAS_GEMINI and api_key:
        try:
            genai.configure(api_key=api_key)
            g_model = genai.GenerativeModel(GEMINI_MODEL)
            resp = g_model.generate_content(
                prompt,
                generation_config={"temperature": 0.75, "max_output_tokens": 1500},
            )
            if resp and resp.text:
                return resp.text
        except Exception:
            pass
    return fallback


class CoverLetterGenerator:
    """Generates personalised cover letters and LinkedIn profiles."""

    def __init__(self):
        self.model = _get_model()

    def generate(
        self,
        resume_sections: dict,
        jd_data: dict,
        gap_data: dict,
        company: str = None,
    ) -> str:
        """Generate a 250–350 word personalised cover letter."""
        matched = gap_data.get("matched_skills", [])
        top_gap = (gap_data.get("critical_gaps", []) + ["problem solving"])[0]
        role_title = gap_data.get("role_title", jd_data.get("role_title", "Software Engineer"))
        summary = resume_sections.get("summary", "")
        experience = resume_sections.get("experience", "")[:500]
        projects = resume_sections.get("projects", "")[:400]
        company_str = f"at {company}" if company else ""

        prompt = f"""
Write a professional cover letter for a {role_title} position {company_str}.

CANDIDATE BACKGROUND:
- Summary: {summary[:300]}
- Key matched skills: {', '.join(matched[:6])}
- Top gap being addressed: {top_gap}
- Recent experience: {experience[:400]}
- Projects: {projects[:300]}

STRUCTURE (4 paragraphs, 250–350 words total):
1. Opening: Hook + role name + top 2 matching skills
2. Body 1: Relevant experience and project highlights (specific, not generic)
3. Body 2: Proactively address top gap — frame as active learning (e.g., "Currently completing...")
4. Closing: Enthusiasm + specific value proposition + call to action

Tone: Professional but warm. Not overly formal. Avoid clichés like "I am writing to express my interest".
Do NOT include [Name] or [Date] placeholders — write the letter body only.
"""
        fallback = f"""Dear Hiring Manager,

I am excited to apply for the {role_title} position {company_str}. With strong proficiency in {', '.join(matched[:3])}, I am confident I can make an immediate contribution to your team.

In my academic and project work, I have built end-to-end solutions that demonstrate my technical depth and ability to deliver results. My projects in {(resume_sections.get('projects', 'software development'))[:80]} have honed my skills in translating requirements into working software.

I recognise that {top_gap} is a key requirement, and I am currently actively upskilling through online coursework to close this gap before joining.

I would welcome the opportunity to discuss how my background aligns with your needs. Thank you for considering my application.

Sincerely,
[Your Name]
"""
        return _call_gemini(self.model, prompt, fallback=fallback)

    def generate_linkedin_optimisation(
        self,
        resume_sections: dict,
        gap_data: dict,
        role_title: str,
    ) -> dict:
        """Generate an optimised LinkedIn headline, About section, and skills."""
        matched = gap_data.get("matched_skills", [])[:8]
        gaps = gap_data.get("critical_gaps", [])[:5]
        summary = resume_sections.get("summary", "")[:400]
        experience = resume_sections.get("experience", "")[:400]

        prompt = f"""
Generate LinkedIn profile optimisation for a {role_title} candidate.

PROFILE DATA:
- Matched skills: {', '.join(matched)}
- Learning: {', '.join(gaps[:3])}
- Current summary: {summary}
- Experience excerpt: {experience}

Return ONLY a JSON object (no markdown, no explanation):
{{
  "headline": "One line, max 220 chars, includes role + top 2-3 skills + differentiator",
  "about": "Full About section, 1800-2200 chars. 5 paragraphs: hook, background, skills+projects, what youre learning, CTA. Use line breaks between paragraphs. No hashtags until the last line. End with: Open to {role_title} opportunities.",
  "skills_to_add": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "featured_section_idea": "One specific idea for the Featured section (e.g., GitHub project or blog post)"
}}
"""
        raw = _call_gemini(self.model, prompt, fallback=None)
        if raw:
            try:
                import json, re
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception:
                pass

        return {
            "headline": f"{role_title} | {' · '.join(matched[:3])} | Open to Opportunities",
            "about": (
                f"🚀 Aspiring {role_title} with a passion for building scalable, impactful software.\n\n"
                f"I have strong hands-on experience in {', '.join(matched[:4])}, built through academic projects "
                "and self-driven learning. I believe in learning by doing — every project I take on has a real-world use case.\n\n"
                f"Currently levelling up in {', '.join(gaps[:2])} to be interview-ready for product companies.\n\n"
                f"Open to {role_title} opportunities. Let's connect!"
            ),
            "skills_to_add": matched[:5] + gaps[:2],
            "featured_section_idea": "Pin your best GitHub project with a demo GIF or screenshots.",
        }


class LinkedInOptimiser:
    """Wrapper class for LinkedIn optimisation (delegates to CoverLetterGenerator)."""

    def __init__(self):
        self._gen = CoverLetterGenerator()

    def optimise(self, resume_sections: dict, gap_data: dict, role_title: str) -> dict:
        return self._gen.generate_linkedin_optimisation(resume_sections, gap_data, role_title)
