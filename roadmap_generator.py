"""Rule-based learning roadmap built from the skill gap."""
import pandas as pd

from skill_extractor import load_dictionary


def build_roadmap(missing_required: list[str], missing_nice: list[str], max_skills: int = 6) -> list[dict]:
    info = load_dictionary().set_index("skill")
    ordered = (missing_required + missing_nice)[:max_skills]
    plan, week = [], 1
    for skill in ordered:
        weeks = int(info.loc[skill, "weeks"])
        period = f"Week {week}" if weeks == 1 else f"Weeks {week}-{week + weeks - 1}"
        plan.append({
            "period": period,
            "skill": skill,
            "priority": "Required" if skill in missing_required else "Nice to have",
            "topic": info.loc[skill, "learn"],
        })
        week += weeks
    if plan:
        plan.append({
            "period": f"Week {week}",
            "skill": "Portfolio project",
            "priority": "Required",
            "topic": "Build and deploy one project that uses the new skills, push it to GitHub and add it to the resume",
        })
    return plan


def roadmap_dataframe(plan: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(plan, columns=["period", "skill", "priority", "topic"])
