"""
Mentor Matcher — Curated mentor suggestions based on skill gaps.
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

MENTOR_DATABASE = [
    {"name": "Krish Naik", "role": "Head of AI at iNeuron.ai", "expertise": ["machine learning", "deep learning", "mlops", "python", "data science"], "linkedin": "https://www.linkedin.com/in/naikkrish/", "why": "One of India's most popular ML educators. His YouTube channel has helped thousands of freshers crack ML interviews."},
    {"name": "Abhishek Thakur", "role": "Chief Data Scientist & Kaggle Grandmaster", "expertise": ["machine learning", "nlp", "deep learning", "pytorch", "kaggle"], "linkedin": "https://www.linkedin.com/in/abhishek-thakur/", "why": "World's first Kaggle 4x Grandmaster. Exceptional at explaining practical ML workflows and competition strategies."},
    {"name": "Kunal Kushwaha", "role": "DevRel Engineer & Open Source Lead", "expertise": ["java", "dsa", "devops", "kubernetes", "open source", "community"], "linkedin": "https://www.linkedin.com/in/kunal-kushwaha/", "why": "Known for his free DSA bootcamp and DevOps courses. Strong advocate for fresher developers entering the industry."},
    {"name": "Striver (Raj Vikramaditya)", "role": "SDE at Google India", "expertise": ["data structures", "algorithms", "system design", "competitive programming", "dsa"], "linkedin": "https://www.linkedin.com/in/rajvikramaditya/", "why": "Creator of Striver's SDE Sheet, the most popular DSA prep resource for Indian placements. Ex-TCS, now at Google."},
    {"name": "Sandeep Jain", "role": "Founder of GeeksforGeeks", "expertise": ["data structures", "algorithms", "system design", "competitive programming"], "linkedin": "https://www.linkedin.com/in/sandeepjain1509/", "why": "Founded India's largest CS learning platform. Deep expertise in interview preparation and computer science fundamentals."},
    {"name": "Apna College (Shradha & Aman)", "role": "Educators & Full Stack Developers", "expertise": ["python", "java", "data structures", "sql", "web development"], "linkedin": "https://www.linkedin.com/school/apna-college/", "why": "Created one of the most popular free programming curricula for Indian engineering students. Clear Hindi explanations."},
    {"name": "Prashant Narang", "role": "Engineering Manager at Microsoft", "expertise": ["system design", "software engineering", "career growth", "leadership"], "linkedin": "https://www.linkedin.com/in/prashant-narang-20/", "why": "Shares actionable system design content and career advice specifically for Indian tech professionals targeting product companies."},
    {"name": "Gaurav Sen", "role": "Engineering Lead at Google", "expertise": ["system design", "distributed systems", "algorithms", "backend"], "linkedin": "https://www.linkedin.com/in/gauravsen1994/", "why": "His system design YouTube series is considered one of the best free resources for FAANG prep globally."},
    {"name": "Harshit Juneja", "role": "Data Scientist at Amazon", "expertise": ["data science", "machine learning", "statistics", "python", "sql"], "linkedin": "https://www.linkedin.com/in/harshit-juneja/", "why": "Creates concise, interview-focused data science content. Covers the full pipeline from EDA to model deployment."},
    {"name": "Code With Harry", "role": "Full Stack Educator", "expertise": ["python", "web development", "flask", "react", "javascript", "node.js"], "linkedin": "https://www.linkedin.com/in/harryprogrammer/", "why": "One of India's most watched programming educators. Covers full-stack development in clear Hindi with project-based learning."},
    {"name": "Aditya Kumar", "role": "SWE at Google", "expertise": ["competitive programming", "data structures", "algorithms", "c++"], "linkedin": "https://www.linkedin.com/in/adityakumar-/", "why": "ICPC Asia champion who shares competitive programming strategies and DSA tips targeted at Indian college students."},
    {"name": "Piyush Garg", "role": "Senior SDE & Educator", "expertise": ["node.js", "react", "backend", "devops", "docker", "system design"], "linkedin": "https://www.linkedin.com/in/piyushgarg-dev/", "why": "Highly rated educator for backend and DevOps topics. Known for practical, project-based teaching style on YouTube."},
    {"name": "Hitesh Choudhary", "role": "CTO & Educator at LearnCodeOnline", "expertise": ["javascript", "react", "node.js", "python", "devops", "web development"], "linkedin": "https://www.linkedin.com/in/hiteshchoudhary/", "why": "Veteran educator with 20+ years of industry experience. Creates thorough, production-quality learning content."},
    {"name": "Nishant Chahar", "role": "SDE at LinkedIn", "expertise": ["data structures", "system design", "java", "competitive programming"], "linkedin": "https://www.linkedin.com/in/nishantchahar11/", "why": "Shares placement-focused content specifically targeting product company interviews at LinkedIn, Google, and Amazon."},
    {"name": "Rachit Jain", "role": "Ex-Google SWE & Educator", "expertise": ["competitive programming", "data structures", "algorithms", "problem solving"], "linkedin": "https://www.linkedin.com/in/rachit-jain/", "why": "Former Google engineer who now shares competitive programming techniques and placement prep strategies for freshers."},
    {"name": "Tanishq Rawat", "role": "ML Engineer at Cohere", "expertise": ["nlp", "llm", "hugging face", "transformers", "machine learning"], "linkedin": "https://www.linkedin.com/in/tanishq-rawat/", "why": "Specialises in modern NLP and LLM engineering. Great mentor for anyone targeting AI/ML roles at top tech companies."},
    {"name": "Rohan Paul", "role": "Senior SWE & Educator", "expertise": ["javascript", "react", "node.js", "mongodb", "full stack", "web development"], "linkedin": "https://www.linkedin.com/in/rohan-paul-b8054440/", "why": "Creates comprehensive MERN stack learning content with a focus on building real-world production applications."},
    {"name": "Vivek Singh", "role": "Data Science Lead at Flipkart", "expertise": ["data science", "machine learning", "statistics", "sql", "product analytics"], "linkedin": "https://www.linkedin.com/in/vivek-singh-ds/", "why": "Shares practical data science interview tips with a focus on product company interviews at Flipkart and similar firms."},
    {"name": "Aryan Mittal", "role": "Ex-Amazon SDE", "expertise": ["aws", "cloud", "backend", "system design", "devops"], "linkedin": "https://www.linkedin.com/in/aryan-mittal/", "why": "Specialises in AWS cloud architecture and backend system design. Shares Amazon interview prep content consistently."},
    {"name": "Deepak Kumar", "role": "DevOps Engineer at ThoughtWorks", "expertise": ["docker", "kubernetes", "devops", "ci/cd", "terraform", "linux"], "linkedin": "https://www.linkedin.com/in/deepak-kumar-devops/", "why": "One of the best free DevOps educators covering Docker, Kubernetes, CI/CD, and cloud infrastructure from scratch."},
]


class MentorMatcher:
    """Matches skill gaps to relevant mentors from a curated list."""

    def suggest_mentors(self, gap_data: dict) -> list[dict]:
        """
        Return top 3 mentor matches for the user's gap profile.

        Scoring: count of expertise overlap with critical + optional gaps.
        """
        all_gaps = (
            gap_data.get("critical_gaps", []) +
            gap_data.get("optional_gaps", []) +
            gap_data.get("soft_gaps", [])
        )
        gap_lower = [g.lower() for g in all_gaps]

        scored = []
        for mentor in MENTOR_DATABASE:
            expertise_lower = [e.lower() for e in mentor.get("expertise", [])]
            overlap = sum(
                1 for gap in gap_lower
                if any(gap in exp or exp in gap for exp in expertise_lower)
            )
            scored.append((overlap, mentor))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:3]]

    def generate_outreach_message(
        self,
        mentor: dict,
        user_background: str,
        gap: str,
    ) -> str:
        """
        Generate a personalised cold outreach message (≤150 words).
        """
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if HAS_GEMINI and api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
Write a professional LinkedIn connection request message (max 150 words).

FROM: A student/fresher with background: {user_background[:200]}
TO: {mentor['name']} — {mentor['role']}
CONTEXT: I need help with {gap}. I admire their work: {mentor['why']}

Rules:
- Be specific about WHY this mentor and WHY this gap
- Mention one concrete thing you've already tried
- Ask ONE specific question or request (not "please mentor me")
- Professional but warm — not sycophantic
- No "I hope this message finds you well"
- End with appreciation, not begging

Write only the message, no subject line.
"""
            for attempt in range(3):
                try:
                    resp = model.generate_content(prompt)
                    return resp.text.strip()
                except Exception:
                    if attempt < 2:
                        time.sleep(2 ** attempt)

        # Fallback template
        expertise_str = ", ".join(mentor.get("expertise", [gap])[:3])
        return (
            f"Hi {mentor['name'].split()[0]},\n\n"
            f"I'm a CS fresher targeting {gap} roles and have been following your work on {expertise_str}. "
            f"Your content on {gap} has been particularly helpful as I prepare for placements.\n\n"
            f"I'm currently struggling with {gap} — specifically applying it in projects. "
            f"Would you be open to a quick 15-minute call to share your perspective? "
            f"I understand you're busy and would truly value even a brief exchange.\n\n"
            f"Thank you for all the content you share — it makes a real difference.\n\n"
            f"Best,\n[Your Name]"
        )
