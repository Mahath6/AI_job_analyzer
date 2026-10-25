"""Text cleaning. Keeps technical symbols such as C++, C#, .NET, Node.js."""
import re

_EMAIL = re.compile(r"\S+@\S+\.\S+")
_URL = re.compile(r"https?://\S+|www\.\S+")
_PHONE = re.compile(r"\+?\d[\d\s\-()]{8,}\d")
_ALLOWED = re.compile(r"[^a-z0-9+#./\-\s]")


def clean_text(text: str) -> str:
    """Lowercase, drop contact details (not job-related), strip noisy symbols."""
    text = text.replace("\u2022", " ").replace("\u00a0", " ")
    text = _EMAIL.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _PHONE.sub(" ", text)
    text = text.lower()
    text = _ALLOWED.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
