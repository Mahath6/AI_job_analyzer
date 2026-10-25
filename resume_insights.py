"""Simple resume structure checks (section detection and quality tips)."""
import re

SECTION_PATTERNS = {
    "Education": r"\b(education|academic|qualification)",
    "Skills": r"\b(skills|technical skills|technologies|tech stack)\b",
    "Projects": r"\b(projects?|personal projects?|academic projects?)\b",
    "Experience": r"\b(experience|internships?|work history|employment)\b",
}


def detect_sections(raw_text: str) -> dict[str, bool]:
    """A section counts as present if a short line (a heading) matches its pattern."""
    lines = [l.strip().lower() for l in raw_text.splitlines() if 0 < len(l.strip()) <= 40]
    return {name: any(re.search(p, l) for l in lines) for name, p in SECTION_PATTERNS.items()}


def resume_tips(raw_text: str, skills: list[str]) -> list[str]:
    tips = []
    sections = detect_sections(raw_text)
    for name, present in sections.items():
        if not present:
            tips.append(f"Add a clear '{name}' heading so both people and parsers can find it.")
    words = len(raw_text.split())
    if words < 150:
        tips.append("The resume is very short. Add project descriptions and what you built.")
    if words > 900:
        tips.append("The resume is long. For internships and junior roles, aim for one page.")
    if not re.search(r"\d+\s?%|\b\d{2,}\b", raw_text):
        tips.append("Add numbers to your projects (accuracy, users, dataset size, time saved).")
    if not re.search(r"github\.com|gitlab\.com", raw_text.lower()):
        tips.append("Add a GitHub link so projects can be checked.")
    if len(skills) < 10:
        tips.append("Few skills were detected. List tools used inside project descriptions as well.")
    return tips or ["The structure looks solid. Focus on closing the skill gaps below."]
