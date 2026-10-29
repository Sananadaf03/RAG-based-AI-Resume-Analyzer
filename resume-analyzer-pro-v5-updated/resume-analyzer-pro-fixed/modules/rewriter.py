# ============================================================
# modules/rewriter.py
# AI Resume Section Rewriter — NLP-based enhancement engine
# Uses local NLP only: spaCy, sklearn, rule-based templates
# ============================================================

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Action verb banks by category ─────────────────────────
ACTION_VERBS = {
    "leadership": ["Led", "Directed", "Managed", "Oversaw", "Guided", "Mentored",
                   "Spearheaded", "Championed", "Orchestrated", "Supervised"],
    "development": ["Developed", "Built", "Engineered", "Architected", "Designed",
                    "Implemented", "Created", "Constructed", "Deployed", "Shipped"],
    "optimization": ["Optimized", "Reduced", "Accelerated", "Streamlined", "Enhanced",
                     "Improved", "Boosted", "Transformed", "Automated", "Refactored"],
    "collaboration": ["Collaborated", "Partnered", "Coordinated", "Aligned", "Facilitated",
                      "Drove", "Enabled", "Supported", "Integrated", "Liaised"],
    "analysis": ["Analyzed", "Evaluated", "Assessed", "Researched", "Identified",
                 "Investigated", "Diagnosed", "Benchmarked", "Validated", "Audited"],
    "achievement": ["Achieved", "Delivered", "Exceeded", "Generated", "Secured",
                    "Established", "Launched", "Pioneered", "Scaled", "Grew"],
}

WEAK_OPENERS = [
    "responsible for", "worked on", "helped with", "assisted with",
    "was involved in", "participated in", "took part in", "contributed to",
    "handled", "dealt with", "was in charge of", "duties included",
    "tasks included", "used", "utilized",
]

METRIC_TEMPLATES = [
    "reducing X by {n}%",
    "improving performance by {n}%",
    "serving {n}+ users",
    "processing {n}+ requests/second",
    "cutting costs by {n}%",
    "increasing efficiency by {n}%",
    "delivering {n} features on schedule",
]


def _capitalize_first(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _strip_leading_weak(text: str) -> str:
    lower = text.lower().strip()
    for weak in WEAK_OPENERS:
        if lower.startswith(weak):
            text = text[len(weak):].strip().lstrip(",").strip()
            break
    return _capitalize_first(text)


def _inject_action_verb(text: str, category: str = "development") -> str:
    verbs = ACTION_VERBS.get(category, ACTION_VERBS["development"])
    cleaned = _strip_leading_weak(text)
    for verb_list in ACTION_VERBS.values():
        for v in verb_list:
            if cleaned.lower().startswith(v.lower()):
                return cleaned
    import random
    verb = random.choice(verbs[:5])
    first_word = cleaned.split()[0] if cleaned.split() else ""
    if first_word and not any(cleaned.lower().startswith(v.lower()) for vl in ACTION_VERBS.values() for v in vl):
        return f"{verb} {cleaned[0].lower()}{cleaned[1:]}"
    return cleaned


def _has_metric(text: str) -> bool:
    return bool(re.search(r'\d+\s*(%|percent|x|times|\+|k\b|m\b|ms\b|s\b)', text, re.I))


def _suggest_metric(text: str) -> str:
    lower = text.lower()
    if "performance" in lower or "speed" in lower or "latency" in lower:
        return ", reducing latency by ~40%"
    if "cost" in lower or "budget" in lower or "expense" in lower:
        return ", cutting costs by ~25%"
    if "user" in lower or "customer" in lower or "client" in lower:
        return ", serving 10K+ users"
    if "team" in lower or "engineer" in lower or "developer" in lower:
        return " across a team of 5+ engineers"
    if "process" in lower or "workflow" in lower or "pipeline" in lower:
        return ", reducing manual effort by ~50%"
    return ", improving overall efficiency by ~30%"


def rewrite_bullet(bullet: str, missing_skills: list[str] = None,
                   category: str = "development") -> dict:
    """
    Rewrite a single resume bullet point to be more impactful.

    Returns:
        dict with keys: original, rewritten, tip, improvements
    """
    original = bullet.strip()
    if not original:
        return {"original": original, "rewritten": original, "tip": "", "improvements": []}

    improvements = []
    rewritten = original

    # 1. Strip weak openers
    cleaned = _strip_leading_weak(rewritten)
    if cleaned != rewritten:
        improvements.append("Removed weak opener")
        rewritten = cleaned

    # 2. Inject strong action verb
    enhanced = _inject_action_verb(rewritten, category)
    if enhanced != rewritten:
        improvements.append("Added strong action verb")
        rewritten = enhanced

    # 3. Add metric if missing
    if not _has_metric(rewritten) and len(rewritten) > 30:
        metric = _suggest_metric(rewritten)
        if rewritten.endswith("."):
            rewritten = rewritten[:-1] + metric + "."
        else:
            rewritten = rewritten + metric + "."
        improvements.append("Added quantified impact metric")

    # 4. Inject missing skill naturally (if fits)
    if missing_skills:
        skill = missing_skills[0]
        lower = rewritten.lower()
        if skill.lower() not in lower and len(rewritten) < 200:
            if "using" in lower or "with" in lower:
                rewritten = re.sub(
                    r'\b(using|with)\b',
                    f"using {skill} and",
                    rewritten, count=1, flags=re.I
                )
            improvements.append(f"Integrated missing skill: {skill}")

    # 5. Ensure ends with period
    if rewritten and not rewritten[-1] in ".!":
        rewritten += "."

    tip = _generate_tip(improvements, original)

    return {
        "original": original,
        "rewritten": rewritten,
        "tip": tip,
        "improvements": improvements,
    }


def _generate_tip(improvements: list[str], original: str) -> str:
    if "Removed weak opener" in improvements:
        return "Replace passive phrases like 'responsible for' with direct action verbs."
    if "Added strong action verb" in improvements:
        return "Starting with a power verb makes recruiters read faster and notice impact."
    if "Added quantified impact metric" in improvements:
        return "Numbers make bullets 3× more credible — replace placeholders with real data."
    if not improvements:
        return "This bullet already follows ATS best practices."
    return "Combine strong verbs + specific technologies + measurable outcomes."


def rewrite_summary(summary: str, job_title: str = "", missing_skills: list[str] = None,
                    years_exp: float = 0) -> dict:
    """
    Rewrite a professional summary to be ATS-optimized.

    Returns dict with original, rewritten, tip
    """
    original = summary.strip()
    if not original:
        return _generate_default_summary(job_title, missing_skills or [], years_exp)

    lines = original.split(". ")
    top_skills = (missing_skills or [])[:3]
    skill_phrase = ", ".join(top_skills) if top_skills else "modern technologies"
    exp_phrase = f"{int(years_exp)}+" if years_exp >= 1 else ""

    rewritten = (
        f"{exp_phrase + '-year ' if exp_phrase else ''}results-driven professional"
        f"{' with expertise in ' + skill_phrase if top_skills else ''}. "
        f"{lines[0].strip()}. "
        f"Passionate about delivering measurable outcomes and driving continuous improvement."
    )
    rewritten = _capitalize_first(rewritten.strip())

    return {
        "original": original,
        "rewritten": rewritten,
        "tip": "Open with years of experience + top skills + value proposition for maximum ATS impact.",
    }


def _generate_default_summary(job_title: str, skills: list[str], years: float) -> dict:
    top = skills[:3] if skills else ["software engineering", "problem solving"]
    skill_str = ", ".join(top)
    yr = f"{int(years)}+-year " if years >= 1 else ""
    rewritten = (
        f"Motivated {yr}professional with hands-on expertise in {skill_str}. "
        f"Track record of delivering high-quality solutions on time while collaborating "
        f"effectively across cross-functional teams. Seeking to leverage technical skills "
        f"and drive meaningful impact."
    )
    return {
        "original": "",
        "rewritten": rewritten,
        "tip": "Add a summary section — it's the first thing ATS and recruiters read.",
    }


def rewrite_experience_section(experience_text: str, missing_skills: list[str] = None,
                                job_category: str = "development") -> list[dict]:
    """
    Rewrite each bullet in an experience section.
    Returns list of rewrite dicts.
    """
    if not experience_text:
        return []

    bullets = [
        line.strip().lstrip("•-*▸►→✓").strip()
        for line in experience_text.split("\n")
        if line.strip() and len(line.strip()) > 20
    ]

    rewrites = []
    skills_queue = list(missing_skills or [])

    for i, bullet in enumerate(bullets[:8]):
        use_skills = skills_queue[i:i+1] if skills_queue else []
        rewrites.append(rewrite_bullet(bullet, use_skills, job_category))

    return rewrites


def calculate_improvement_score(original: str, rewritten: str) -> float:
    """
    Calculate an improvement percentage between original and rewritten text.
    Based on: action verb presence, metric presence, length optimization, weak opener removal.
    """
    original_score = _text_quality_score(original)
    rewritten_score = _text_quality_score(rewritten)

    if original_score == 0:
        return 0.0

    improvement = ((rewritten_score - original_score) / original_score) * 100
    return round(min(improvement, 95.0), 1)


def _text_quality_score(text: str) -> float:
    score = 0
    lower = text.lower()

    # Has action verb
    for vl in ACTION_VERBS.values():
        for v in vl:
            if lower.startswith(v.lower()):
                score += 25
                break

    # Has metric
    if _has_metric(text):
        score += 30

    # No weak opener
    if not any(lower.startswith(w) for w in WEAK_OPENERS):
        score += 20

    # Length optimization (40-200 chars is ideal for a bullet)
    length = len(text)
    if 40 <= length <= 200:
        score += 15
    elif length > 20:
        score += 8

    # Ends with punctuation
    if text.strip()[-1:] in ".!":
        score += 10

    return max(score, 1)


def generate_optimized_summary(
    resume_data: dict,
    jd_data: dict,
    missing_skills: list[str],
    years_exp: float,
) -> str:
    """
    Generate a fully optimized professional summary using resume + JD context.
    """
    jd_text = jd_data.get("full_text", "")
    job_title = _extract_job_title(jd_text)
    top_skills = (resume_data.get("matched_skills") or missing_skills or [])[:4]
    skill_str = ", ".join(top_skills) if top_skills else "technology"

    exp_phrase = f"{int(years_exp)}+-year" if years_exp >= 1 else "results-driven"

    summary = (
        f"{_capitalize_first(exp_phrase)} {job_title or 'professional'} with proven expertise in "
        f"{skill_str}. Adept at designing, building, and optimizing solutions that deliver "
        f"measurable business impact. Collaborative team player with a track record of "
        f"shipping high-quality work on time and thriving in fast-paced environments."
    )
    return summary


def _extract_job_title(jd_text: str) -> str:
    patterns = [
        r"(?:position|role|title)[:\s]+([A-Z][a-z\s]+Engineer|[A-Z][a-z\s]+Developer|[A-Z][a-z\s]+Analyst|[A-Z][a-z\s]+Manager)",
        r"^([A-Z][a-z\s]+(Engineer|Developer|Analyst|Manager|Designer|Architect))",
    ]
    for pat in patterns:
        m = re.search(pat, jd_text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    return ""
