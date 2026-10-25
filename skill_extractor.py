"""Dictionary based skill extraction with alias support and categories."""
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"

# Python-only tools: if a resume mentions them, the candidate uses Python even
# if the word "Python" is never written (e.g. "Built an API with Flask").
IMPLIES_PYTHON = {
    "Flask", "Django", "FastAPI", "Pandas", "NumPy", "Scikit-learn",
    "Matplotlib", "PyTorch", "Hugging Face", "spaCy", "NLTK", "Jupyter",
}


@lru_cache(maxsize=1)
def load_dictionary() -> pd.DataFrame:
    return pd.read_csv(DATA / "skill_dictionary.csv").fillna("")


@lru_cache(maxsize=1)
def _patterns():
    """One compiled regex per skill. Boundaries avoid matching 'sql' inside
    'postgresql' or 'r' inside words, while still allowing 'c++' and '.net'."""
    pats = {}
    for _, row in load_dictionary().iterrows():
        names = {row["skill"].lower()} | {a.strip().lower() for a in row["aliases"].split("|") if a.strip()}
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        pats[row["skill"]] = re.compile(rf"(?<![a-z0-9+#])(?:{alt})(?![a-z0-9+#])")
    return pats


def extract_skills(cleaned_text: str) -> list[str]:
    found = [skill for skill, pat in _patterns().items() if pat.search(cleaned_text)]
    if "Python" not in found and IMPLIES_PYTHON & set(found):
        found.insert(0, "Python")
    return found


def group_by_category(skills: list[str]) -> dict[str, list[str]]:
    df = load_dictionary().set_index("skill")
    groups: dict[str, list[str]] = {}
    for s in skills:
        groups.setdefault(df.loc[s, "category"], []).append(s)
    return groups
