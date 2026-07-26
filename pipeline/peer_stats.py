"""
Peer Stats — Compares user score against anonymised aggregate data.
"""
from __future__ import annotations
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

ROLE_MAP = {
    "machine learning engineer": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "data scientist": "Data Scientist",
    "data analyst": "Data Analyst",
    "data engineer": "Data Engineer",
    "devops engineer": "DevOps Engineer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "backend engineer": "Backend Engineer",
    "software engineer": "Software Engineer",
    "software developer": "Software Engineer",
}


class PeerStats:
    """Provides percentile and peer comparison for a given role + match score."""

    def __init__(self):
        with open(DATA_DIR / "peer_stats.json", encoding="utf-8") as f:
            self.data: dict = json.load(f)

    def get_comparison(self, role_title: str, match_score: float) -> dict:
        """
        Return percentile, distribution, and peer messages.

        Returns:
            {
                "percentile": int,
                "avg_score": float,
                "common_gaps": [...],
                "score_distribution": [...],
                "score_buckets": [...],
                "message": str,
                "total_peers": int
            }
        """
        role_key = self._match_role(role_title)
        by_role = self.data.get("by_role", {})

        if role_key not in by_role:
            # Default fallback
            return self._default_comparison(match_score)

        role_data = by_role[role_key]
        avg_score = role_data.get("avg_match_score", 55)
        distribution = role_data.get("score_distribution", [5, 12, 28, 35, 14, 6])
        buckets = role_data.get("score_buckets", ["0-20", "20-40", "40-60", "60-80", "80-90", "90-100"])
        total_peers = role_data.get("total_users", 100)

        percentile = self._compute_percentile(match_score, distribution, buckets, total_peers)

        if percentile >= 90:
            message = f"🏆 Exceptional! You are in the top {100 - percentile}% of {total_peers} students targeting this role."
        elif percentile >= 70:
            message = f"✅ Strong profile! You outperform {percentile}% of peers targeting {role_key}."
        elif percentile >= 50:
            message = f"📈 Above average! You're ahead of {percentile}% of {total_peers} peers. Close 2-3 more gaps to reach top quartile."
        elif percentile >= 25:
            message = f"⚡ You're at the {percentile}th percentile. Focus on critical gaps to move into the top half."
        else:
            message = f"💪 You're at the {percentile}th percentile — plenty of room to grow! The roadmap will help you catch up fast."

        return {
            "percentile": percentile,
            "avg_score": avg_score,
            "common_gaps": role_data.get("common_gaps", []),
            "score_distribution": distribution,
            "score_buckets": buckets,
            "message": message,
            "total_peers": total_peers,
            "role_matched": role_key,
        }

    def _compute_percentile(
        self,
        score: float,
        distribution: list,
        buckets: list,
        total: int,
    ) -> int:
        """Estimate percentile from score distribution."""
        bucket_ranges = []
        for b in buckets:
            parts = b.split("-")
            try:
                lo, hi = int(parts[0]), int(parts[1])
            except Exception:
                lo, hi = 0, 100
            bucket_ranges.append((lo, hi))

        below_count = 0
        for i, (lo, hi) in enumerate(bucket_ranges):
            if score > hi:
                below_count += distribution[i] if i < len(distribution) else 0
            elif lo <= score <= hi and i < len(distribution):
                # Partial credit within this bucket
                bucket_fraction = (score - lo) / max(hi - lo, 1)
                below_count += distribution[i] * bucket_fraction

        total_dist = sum(distribution)
        percentile = int(below_count / max(total_dist, 1) * 100)
        return max(1, min(99, percentile))

    def _match_role(self, role_title: str) -> str:
        lower = role_title.lower()
        for key, canonical in ROLE_MAP.items():
            if key in lower:
                return canonical
        return "Software Engineer"

    @staticmethod
    def _default_comparison(score: float) -> dict:
        distribution = [5, 12, 28, 35, 14, 6]
        buckets = ["0-20", "20-40", "40-60", "60-80", "80-90", "90-100"]
        return {
            "percentile": 50,
            "avg_score": 55,
            "common_gaps": ["System Design", "DSA", "Docker", "SQL"],
            "score_distribution": distribution,
            "score_buckets": buckets,
            "message": f"Your score of {int(score)}% puts you in a competitive position. Keep closing gaps!",
            "total_peers": 200,
            "role_matched": "Software Engineer",
        }
