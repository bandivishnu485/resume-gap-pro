"""
Project Suggester — Maps skill gaps to hands-on mini-projects.
"""
from __future__ import annotations

PROJECTS: dict[str, list[dict]] = {
    "python": [
        {"title": "CLI Expense Tracker", "desc": "Build a command-line expense tracker with CSV persistence, categories, and monthly summaries using Python standard library.", "days": 2, "github_ready": True, "skills_demonstrated": ["Python", "File I/O", "argparse", "CSV"]},
        {"title": "Web Scraper + Dashboard", "desc": "Scrape job listings from a public site using requests+BeautifulSoup, store in SQLite, and visualise trends with a Streamlit dashboard.", "days": 3, "github_ready": True, "skills_demonstrated": ["Python", "BeautifulSoup", "SQLite", "Streamlit"]},
    ],
    "sql": [
        {"title": "E-Commerce Analytics", "desc": "Write 20 progressively complex SQL queries (window functions, CTEs, subqueries) against a sample e-commerce dataset and document insights.", "days": 2, "github_ready": True, "skills_demonstrated": ["SQL", "Window Functions", "CTEs", "Analytics"]},
        {"title": "Sales KPI Dashboard", "desc": "Build a PostgreSQL database from a CSV dataset and create a Python + Plotly dashboard showing sales KPIs with SQL as the data layer.", "days": 3, "github_ready": True, "skills_demonstrated": ["PostgreSQL", "SQL", "Plotly", "Python"]},
    ],
    "data structures": [
        {"title": "LeetCode Pattern Tracker", "desc": "Solve 30 LeetCode problems (10 each of Easy/Medium/Hard) and document the pattern, time/space complexity, and optimal approach for each.", "days": 14, "github_ready": True, "skills_demonstrated": ["DSA", "Problem Solving", "Algorithms", "Python"]},
        {"title": "Custom Data Structure Library", "desc": "Implement LinkedList, Stack, Queue, Binary Search Tree, and Graph from scratch with unit tests and Big-O documentation.", "days": 4, "github_ready": True, "skills_demonstrated": ["Data Structures", "Python", "Unit Testing", "OOP"]},
    ],
    "machine learning": [
        {"title": "House Price Predictor", "desc": "Train regression models on Bangalore/Mumbai housing data, compare algorithms, tune hyperparameters, and deploy predictions via a Streamlit app.", "days": 4, "github_ready": True, "skills_demonstrated": ["ML", "scikit-learn", "Regression", "Streamlit", "EDA"]},
        {"title": "Churn Prediction System", "desc": "Build an end-to-end classification pipeline: EDA → feature engineering → model training → threshold tuning → FastAPI deployment.", "days": 5, "github_ready": True, "skills_demonstrated": ["ML", "Classification", "FastAPI", "scikit-learn", "Pandas"]},
    ],
    "deep learning": [
        {"title": "Handwritten Digit Classifier", "desc": "Train a CNN on MNIST/EMNIST, achieve >99% accuracy, add Grad-CAM explainability, and build a Streamlit draw-and-predict UI.", "days": 3, "github_ready": True, "skills_demonstrated": ["CNN", "PyTorch/TF", "Deep Learning", "Streamlit"]},
        {"title": "Transfer Learning Image Classifier", "desc": "Fine-tune ResNet50 or EfficientNet on a custom dataset (e.g., Indian food categories) and deploy via FastAPI with a web UI.", "days": 4, "github_ready": True, "skills_demonstrated": ["Transfer Learning", "CNN", "PyTorch", "FastAPI"]},
    ],
    "nlp": [
        {"title": "Resume Keyword Extractor", "desc": "Build a spaCy-based NLP pipeline that extracts skills, experience, and education from any resume PDF, returning structured JSON.", "days": 3, "github_ready": True, "skills_demonstrated": ["NLP", "spaCy", "PDF Parsing", "Python", "FastAPI"]},
        {"title": "News Sentiment Analyser", "desc": "Scrape 500 news articles, classify sentiment with BERT fine-tuning, and build a topic-wise sentiment trend dashboard.", "days": 4, "github_ready": True, "skills_demonstrated": ["NLP", "BERT", "Hugging Face", "Sentiment Analysis", "Plotly"]},
    ],
    "docker": [
        {"title": "Containerised Flask API", "desc": "Build a REST API with Flask, containerise it with a multi-stage Dockerfile, add docker-compose with PostgreSQL, and document the setup.", "days": 2, "github_ready": True, "skills_demonstrated": ["Docker", "Flask", "PostgreSQL", "REST API", "DevOps"]},
        {"title": "Microservices TODO App", "desc": "Build 3 microservices (auth, tasks, notifications) in Python/Node, each containerised separately and orchestrated with docker-compose.", "days": 4, "github_ready": True, "skills_demonstrated": ["Docker", "Microservices", "API Design", "docker-compose"]},
    ],
    "system design": [
        {"title": "URL Shortener with Redis", "desc": "Design and implement bit.ly — FastAPI backend, Redis for fast lookups, PostgreSQL for persistence, with rate limiting and analytics.", "days": 3, "github_ready": True, "skills_demonstrated": ["System Design", "FastAPI", "Redis", "PostgreSQL", "Caching"]},
        {"title": "Distributed Rate Limiter", "desc": "Implement a token bucket + sliding window rate limiter as a standalone FastAPI middleware with Redis, and document the design decisions.", "days": 3, "github_ready": True, "skills_demonstrated": ["System Design", "Redis", "Distributed Systems", "FastAPI"]},
    ],
    "react": [
        {"title": "Job Tracker SPA", "desc": "Build a React SPA to track job applications with Kanban board view, status filters, notes, and local storage persistence.", "days": 4, "github_ready": True, "skills_demonstrated": ["React", "Hooks", "State Management", "CSS", "localStorage"]},
        {"title": "GitHub Profile Viewer", "desc": "Build a React app using GitHub public API to display any user's repos, stars, language stats, and contribution graph.", "days": 3, "github_ready": True, "skills_demonstrated": ["React", "REST API", "Axios", "Recharts", "Responsive Design"]},
    ],
    "node.js": [
        {"title": "REST API with Auth", "desc": "Build a full Node.js + Express REST API with JWT authentication, bcrypt password hashing, PostgreSQL via Sequelize, and Swagger docs.", "days": 4, "github_ready": True, "skills_demonstrated": ["Node.js", "Express", "JWT", "PostgreSQL", "API Design"]},
        {"title": "Real-Time Chat App", "desc": "Build a WebSocket chat application using Socket.io + Node.js with rooms, typing indicators, and message history stored in MongoDB.", "days": 3, "github_ready": True, "skills_demonstrated": ["Node.js", "Socket.io", "MongoDB", "Real-time", "WebSockets"]},
    ],
    "aws": [
        {"title": "Serverless Image Processor", "desc": "Build an AWS Lambda that resizes images uploaded to S3, stores metadata in DynamoDB, and returns a CDN URL — all with Terraform IaC.", "days": 4, "github_ready": True, "skills_demonstrated": ["AWS Lambda", "S3", "DynamoDB", "Terraform", "Serverless"]},
        {"title": "3-Tier Web App on AWS", "desc": "Deploy a Flask app on EC2 with RDS PostgreSQL, S3 static assets, and an Application Load Balancer, all provisioned via CloudFormation.", "days": 5, "github_ready": True, "skills_demonstrated": ["AWS EC2", "RDS", "S3", "ALB", "CloudFormation"]},
    ],
    "kubernetes": [
        {"title": "K8s Microservices Deployment", "desc": "Containerise a 3-service app and write full Kubernetes manifests: Deployments, Services, Ingress, ConfigMaps, and Secrets.", "days": 4, "github_ready": True, "skills_demonstrated": ["Kubernetes", "Docker", "Helm", "DevOps", "YAML"]},
        {"title": "Auto-Scaling Demo", "desc": "Deploy a CPU-intensive Flask app to Kubernetes, configure HorizontalPodAutoscaler, and load test it with Locust to demonstrate auto-scaling.", "days": 3, "github_ready": True, "skills_demonstrated": ["Kubernetes", "HPA", "Load Testing", "Locust", "Monitoring"]},
    ],
    "mlops": [
        {"title": "MLflow Experiment Tracker", "desc": "Train 3 ML models with different hyperparameters, track all with MLflow, compare runs, register the best model, and serve it via MLflow's built-in server.", "days": 3, "github_ready": True, "skills_demonstrated": ["MLOps", "MLflow", "Model Registry", "scikit-learn", "Python"]},
        {"title": "CI/CD ML Pipeline", "desc": "Build a GitHub Actions pipeline that trains a model on PR, runs evaluation tests, and auto-deploys the model to a staging FastAPI server.", "days": 4, "github_ready": True, "skills_demonstrated": ["MLOps", "GitHub Actions", "CI/CD", "FastAPI", "Docker"]},
    ],
    "fastapi": [
        {"title": "URL Shortener API", "desc": "Build a FastAPI URL shortener and containerise it with Docker. Includes PostgreSQL, Redis caching, authentication, and OpenAPI docs.", "days": 2, "github_ready": True, "skills_demonstrated": ["FastAPI", "Docker", "Redis", "PostgreSQL", "REST API"]},
        {"title": "ML Model Serving API", "desc": "Wrap a trained scikit-learn model in a FastAPI endpoint with input validation via Pydantic, background tasks, and async database logging.", "days": 2, "github_ready": True, "skills_demonstrated": ["FastAPI", "Pydantic", "ML Deployment", "Async", "Python"]},
    ],
    "statistics": [
        {"title": "A/B Test Simulator", "desc": "Build a Python simulation of A/B tests for an e-commerce site, covering t-tests, chi-square tests, p-values, and power analysis.", "days": 3, "github_ready": True, "skills_demonstrated": ["Statistics", "A/B Testing", "scipy", "Python", "Data Science"]},
        {"title": "Statistical EDA Notebook", "desc": "Perform a comprehensive statistical analysis of a real dataset (e.g., Indian census data) covering distributions, correlations, and hypothesis tests.", "days": 2, "github_ready": True, "skills_demonstrated": ["Statistics", "Pandas", "Seaborn", "Hypothesis Testing", "EDA"]},
    ],
    "git": [
        {"title": "Open Source Contribution", "desc": "Find a beginner-friendly GitHub issue in a popular Python/JS project, fix it, and submit a Pull Request following open source contribution guidelines.", "days": 3, "github_ready": True, "skills_demonstrated": ["Git", "GitHub", "Open Source", "Code Review", "Collaboration"]},
        {"title": "Git Workflow Cheatsheet Project", "desc": "Create a well-documented GitHub repo demonstrating branching strategies, merge vs rebase, conflict resolution, and GitHub Actions CI.", "days": 1, "github_ready": True, "skills_demonstrated": ["Git", "GitHub Actions", "Version Control", "Documentation"]},
    ],
    "communication": [
        {"title": "Technical Blog Series", "desc": "Write 3 technical blog posts on Medium or Dev.to about projects you've built — each 800+ words with code examples and clear explanations.", "days": 6, "github_ready": False, "skills_demonstrated": ["Communication", "Technical Writing", "Documentation", "Knowledge Sharing"]},
        {"title": "YouTube Tech Explainer", "desc": "Record and publish 2 YouTube videos explaining a technical concept (e.g., 'How does Docker work?') in under 5 minutes each.", "days": 4, "github_ready": False, "skills_demonstrated": ["Communication", "Teaching", "Presentation", "Technical Depth"]},
    ],
    "leadership": [
        {"title": "Hackathon Team Lead", "desc": "Lead a 3-4 person team in a weekend hackathon, manage task division, handle conflicts, and present the final project to judges.", "days": 2, "github_ready": False, "skills_demonstrated": ["Leadership", "Teamwork", "Project Management", "Communication"]},
        {"title": "Study Group Organiser", "desc": "Organise and run 5 weekly study sessions for peers on DSA or ML — create study materials, track progress, and document learnings.", "days": 35, "github_ready": True, "skills_demonstrated": ["Leadership", "Teaching", "Mentoring", "Documentation"]},
    ],
}


class ProjectSuggester:
    """Maps skill gaps to hands-on mini-projects."""

    def suggest(self, gaps: list[str]) -> dict[str, list[dict]]:
        """
        Return up to 2 project suggestions per gap.

        Args:
            gaps: List of skill gap names.

        Returns:
            { gap: [project1, project2] }
        """
        result = {}
        for gap in gaps:
            gap_lower = gap.lower().strip()
            projects = self._find_projects(gap_lower)
            result[gap] = projects[:2]
        return result

    def _find_projects(self, gap_lower: str) -> list[dict]:
        """Find projects by exact or fuzzy skill match."""
        # Exact match
        if gap_lower in PROJECTS:
            return PROJECTS[gap_lower]

        # Fuzzy match
        for key, projs in PROJECTS.items():
            if key in gap_lower or gap_lower in key:
                return projs

        # Keyword match
        keywords = {
            "deep learning": "deep learning", "neural": "deep learning",
            "ml": "machine learning", "model": "machine learning",
            "node": "node.js", "express": "node.js",
            "k8s": "kubernetes", "container orchestration": "kubernetes",
            "flask": "fastapi", "web framework": "fastapi",
            "nosql": "sql", "database": "sql",
            "algorithm": "data structures", "leetcode": "data structures",
            "stat": "statistics", "probability": "statistics",
            "github": "git", "version control": "git",
            "cloud": "aws", "serverless": "aws",
            "soft": "communication", "verbal": "communication",
            "lead": "leadership", "manage": "leadership",
        }
        for kw, mapped in keywords.items():
            if kw in gap_lower:
                return PROJECTS.get(mapped, [])

        # Generic fallback
        return [
            {
                "title": f"{gap_lower.title()} Practice Project",
                "desc": f"Build a small end-to-end project that demonstrates your understanding of {gap_lower}. Push to GitHub with a thorough README.",
                "days": 3,
                "github_ready": True,
                "skills_demonstrated": [gap_lower.title(), "Python", "Documentation"],
            }
        ]
