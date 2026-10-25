"""Markdown report for download."""
from datetime import date

from job_matcher import label


def build_report(filename, skills_by_cat, matches, target, roadmap, tips) -> str:
    L = [f"# Resume Analysis Report", f"File: {filename}  |  Date: {date.today().isoformat()}", ""]
    L += [f"## Target role: {target['role']}",
          f"Match score: **{target['score']}%** ({label(target['score'])})",
          f"(skill coverage {target['skill_coverage']}%, text similarity {target['text_similarity']}%)", ""]
    L += ["## Skills found"] + [f"- **{c}**: {', '.join(s)}" for c, s in skills_by_cat.items()] + [""]
    L += ["## Top recommended roles"] + [f"{i}. {m['role']} - {m['score']}%" for i, m in enumerate(matches[:3], 1)] + [""]
    L += ["## Missing skills for target role",
          "Required: " + (", ".join(target["missing_required"]) or "none"),
          "Nice to have: " + (", ".join(target["missing_nice"]) or "none"), ""]
    L += ["## Learning roadmap"] + [f"- {r['period']}: {r['skill']} - {r['topic']}" for r in roadmap] + [""]
    L += ["## Resume tips"] + [f"- {t}" for t in tips] + [""]
    L += ["---", "Scores are automated estimates for guidance only. They are not recruiter decisions, "
          "and a missing keyword does not mean missing ability. Gender, age, religion, nationality, "
          "photo, marital status and disability are never used in scoring."]
    return "\n".join(L)
