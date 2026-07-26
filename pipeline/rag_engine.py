"""
RAG Engine — Hybrid dense + sparse retrieval for course recommendations.
"""
from __future__ import annotations
import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
import json
import pickle
from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

DATA_DIR = Path(__file__).parent.parent / "data"
VECTOR_STORE_DIR = Path(__file__).parent.parent / "vector_store"

PROJECT_SUGGESTIONS = [
    {"skill": "python", "title": "CLI Task Manager", "desc": "Build a command-line task manager with file persistence.", "type": "project"},
    {"skill": "docker", "title": "Containerised Flask API", "desc": "Wrap a Flask REST API in Docker with docker-compose.", "type": "project"},
    {"skill": "machine learning", "title": "House Price Predictor", "desc": "Train a regression model on Indian housing data and deploy as a FastAPI endpoint.", "type": "project"},
    {"skill": "nlp", "title": "Sentiment Analyser API", "desc": "Build a Twitter sentiment analyser using BERT fine-tuning, served via FastAPI.", "type": "project"},
    {"skill": "system design", "title": "URL Shortener Design", "desc": "Design and implement a URL shortener with Redis caching and PostgreSQL persistence.", "type": "project"},
    {"skill": "react", "title": "Job Board App", "desc": "Build a full-stack job board with React frontend and Node.js backend.", "type": "project"},
    {"skill": "sql", "title": "E-Commerce Analytics Dashboard", "desc": "Write complex SQL queries to analyse sales data and build a Streamlit dashboard.", "type": "project"},
    {"skill": "aws", "title": "Serverless Image Processor", "desc": "Build an AWS Lambda function that processes images uploaded to S3.", "type": "project"},
    {"skill": "data structures", "title": "LeetCode Blind 75 Tracker", "desc": "Solve and document all 75 must-know DSA problems with time/space analysis.", "type": "project"},
    {"skill": "mlops", "title": "MLflow Model Registry", "desc": "Track model experiments with MLflow and deploy the best model via a REST API.", "type": "project"},
]


class RAGEngine:
    """Hybrid BM25 + FAISS retrieval engine for course and project recommendations."""

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.courses: list[dict] = []
        self.all_docs: list[dict] = []  # courses + project suggestions
        self.index: Optional[object] = None  # faiss index
        self.bm25: Optional[object] = None
        self.doc_texts: list[str] = []
        self._load()

    def _load(self) -> None:
        """Load courses, build or restore the index."""
        with open(DATA_DIR / "courses.json", encoding="utf-8") as f:
            self.courses = json.load(f)

        self.all_docs = self.courses + [
            {**p, "course_name": p["title"], "description": p["desc"],
             "platform": "Project", "url": "", "duration": "2-5 days",
             "level": "Intermediate", "free": True, "certificate": False}
            for p in PROJECT_SUGGESTIONS
        ]

        self.doc_texts = [
            f"{d.get('skill', '')} {d.get('course_name', '')} {d.get('description', '')}"
            for d in self.all_docs
        ]

        if HAS_BM25:
            tokenized = [t.lower().split() for t in self.doc_texts]
            self.bm25 = BM25Okapi(tokenized)

        if HAS_FAISS:
            index_path = VECTOR_STORE_DIR / "courses.faiss"
            embed_path = VECTOR_STORE_DIR / "courses_embeddings.pkl"
            VECTOR_STORE_DIR.mkdir(exist_ok=True)

            if index_path.exists() and embed_path.exists():
                self.index = faiss.read_index(str(index_path))
                with open(embed_path, "rb") as f:
                    self._embeddings = pickle.load(f)
            else:
                self._build_faiss_index(index_path, embed_path)

            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self.model = None

    def _build_faiss_index(self, index_path: Path, embed_path: Path) -> None:
        """Build FAISS index from course documents."""
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(self.doc_texts, show_progress_bar=False)
            embeddings = embeddings.astype("float32")
            import numpy as np
            faiss.normalize_L2(embeddings)
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(embeddings)
            faiss.write_index(self.index, str(index_path))
            self._embeddings = embeddings
            with open(embed_path, "wb") as f:
                pickle.dump(embeddings, f)
        except Exception as e:
            self.index = None

    def build_index(self, courses: list) -> None:
        """Rebuild index from provided courses list."""
        self.courses = courses
        self._build_faiss_index(
            VECTOR_STORE_DIR / "courses.faiss",
            VECTOR_STORE_DIR / "courses_embeddings.pkl"
        )

    def hybrid_retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Hybrid retrieval: FAISS dense + BM25 sparse, fused with RRF.
        """
        faiss_results = self._faiss_retrieve(query, top_k=20)
        bm25_results = self._bm25_retrieve(query, top_k=20)

        fused = self._rrf_fusion(faiss_results, bm25_results)
        return [self.all_docs[i] for i in fused[:top_k] if i < len(self.all_docs)]

    def _faiss_retrieve(self, query: str, top_k: int = 20) -> list[int]:
        if not self.index or not HAS_FAISS:
            return list(range(min(top_k, len(self.all_docs))))
        try:
            if not self.model:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            import numpy as np
            q_emb = self.model.encode([query], show_progress_bar=False).astype("float32")
            faiss.normalize_L2(q_emb)
            _, ids = self.index.search(q_emb, min(top_k, len(self.all_docs)))
            return [int(i) for i in ids[0] if i >= 0]
        except Exception:
            return list(range(min(top_k, len(self.all_docs))))

    def _bm25_retrieve(self, query: str, top_k: int = 20) -> list[int]:
        if not self.bm25 or not HAS_BM25:
            return list(range(min(top_k, len(self.all_docs))))
        try:
            tokens = query.lower().split()
            scores = self.bm25.get_scores(tokens)
            ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            return ranked[:top_k]
        except Exception:
            return list(range(min(top_k, len(self.all_docs))))

    @staticmethod
    def _rrf_fusion(list_a: list[int], list_b: list[int], k: int = 60) -> list[int]:
        """Reciprocal Rank Fusion of two ranked lists."""
        scores: dict[int, float] = {}
        for rank, doc_id in enumerate(list_a):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        for rank, doc_id in enumerate(list_b):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        return sorted(scores, key=lambda d: scores[d], reverse=True)

    def retrieve_for_all_gaps(self, gaps: list[str]) -> dict[str, list[dict]]:
        """Retrieve top courses for each gap skill."""
        result = {}
        for gap in gaps:
            docs = self.hybrid_retrieve(gap, top_k=3)
            # Filter out project suggestions
            courses_only = [d for d in docs if d.get("type") != "project"][:3]
            result[gap] = courses_only
        return result

    def retrieve_projects(self, gap: str) -> list[dict]:
        """Retrieve project suggestions for a gap skill."""
        docs = self.hybrid_retrieve(gap, top_k=8)
        projects = [d for d in docs if d.get("type") == "project"]
        if not projects:
            # Return from static PROJECT_SUGGESTIONS as fallback
            lower_gap = gap.lower()
            projects = [
                p for p in PROJECT_SUGGESTIONS
                if lower_gap in p.get("skill", "").lower() or p.get("skill", "").lower() in lower_gap
            ][:2]
        return projects[:2]
