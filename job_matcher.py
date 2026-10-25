"""Role matching.

Final score (0-100) = 75% skill coverage + 25% TF-IDF text similarity.
  * skill coverage : required skills weigh 1.0, nice-to-have skills weigh 0.5
  * text similarity: cosine similarity between resume text and role text,
                     scaled by TEXT_SCALE and clipped to 1
Scores are estimates for guidance, not recruiter decisions.
"""
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills
from text_cleaner import clean_text

DATA = Path(__file__).parent / "data"
SKILL_WEIGHT, TEXT_WEIGHT = 0.75, 0.25
NICE_WEIGHT = 0.5
TEXT_SCALE = 3.0
TOKEN_PATTERN = r"[a-z0-9][a-z0-9+#\-]*(?:\.[a-z0-9]+)*"


@dataclass
class Role:
    name: str
    required: list[str]
    nice: list[str] = field(default_factory=list)
    description: str = ""

    @property
    def text(self) -> str:
        return clean_text(f"{self.name} {self.description} " + " ".join(self.required + self.nice))


@lru_cache(maxsize=1)
def load_roles() -> tuple[Role, ...]:
    df = pd.read_csv(DATA / "job_roles.csv").fillna("")
    split = lambda s: [x.strip() for x in s.split("|") if x.strip()]
    return tuple(
        Role(r.role, split(r.required_skills), split(r.nice_to_have), r.description)
        for r in df.itertuples()
    )


def role_from_job_description(jd_text: str, name: str = "Custom job description") -> Role:
    """Build a Role from a pasted job description (required = skills found in it)."""
    found = extract_skills(clean_text(jd_text))
    return Role(name, found, [], jd_text)


def skill_coverage(found: set[str], role: Role) -> float:
    total = len(role.required) + NICE_WEIGHT * len(role.nice)
    if total == 0:
        return 0.0
    got = sum(1 for s in role.required if s in found) + NICE_WEIGHT * sum(1 for s in role.nice if s in found)
    return got / total


def score_roles(cleaned_resume: str, skills: list[str], roles=None) -> list[dict]:
    roles = list(roles or load_roles())
    found = set(skills)
    docs = [cleaned_resume] + [r.text for r in roles]
    tfidf = TfidfVectorizer(token_pattern=TOKEN_PATTERN, ngram_range=(1, 2), sublinear_tf=True).fit_transform(docs)
    sims = cosine_similarity(tfidf[0], tfidf[1:]).ravel()

    results = []
    for role, sim in zip(roles, sims):
        cov = skill_coverage(found, role)
        text = min(1.0, float(sim) * TEXT_SCALE)
        results.append({
            "role": role.name,
            "score": round(100 * (SKILL_WEIGHT * cov + TEXT_WEIGHT * text), 1),
            "skill_coverage": round(100 * cov, 1),
            "text_similarity": round(100 * text, 1),
            "matched_required": [s for s in role.required if s in found],
            "missing_required": [s for s in role.required if s not in found],
            "matched_nice": [s for s in role.nice if s in found],
            "missing_nice": [s for s in role.nice if s not in found],
        })
    return sorted(results, key=lambda d: d["score"], reverse=True)


def label(score: float) -> str:
    if score >= 70:
        return "Strong match"
    if score >= 40:
        return "Partial match"
    return "Early stage"
