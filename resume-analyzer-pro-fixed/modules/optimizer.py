# ============================================================
# modules/optimizer.py
# Resume Optimizer — generates a fully optimized resume that
# PRESERVES every section of the user's original resume while
# improving wording, keywords, action verbs, and ATS coverage.
# ============================================================

import re
import logging
from datetime import datetime
from modules.rewriter import (
    rewrite_bullet, rewrite_summary,
    ACTION_VERBS,
)

logger = logging.getLogger(__name__)


# Canonical order we render in the optimized resume.
SECTION_ORDER = [
    "header",          # name + contact lines (always first)
    "summary",
    "skills",
    "experience",
    "projects",
    "internships",
    "education",
    "certifications",
    "achievements",
    "publications",
    "languages",
    "interests",
    "volunteer",
    "extras",
]

SECTION_LABELS = {
    "header":          "Contact",
    "summary":         "Professional Summary",
    "skills":          "Technical Skills",
    "experience":      "Work Experience",
    "projects":        "Projects",
    "internships":     "Internships",
    "education":       "Education",
    "certifications":  "Certifications",
    "achievements":    "Achievements",
    "publications":    "Publications",
    "languages":       "Languages",
    "interests":       "Interests",
    "volunteer":       "Volunteer Experience",
    "extras":          "Additional",
}

# Map raw parser keys -> canonical keys above.
SECTION_ALIASES = {
    "summary":               "summary",
    "objective":             "summary",
    "profile":               "summary",
    "about":                 "summary",
    "experience":            "experience",
    "work experience":       "experience",
    "employment":            "experience",
    "professional experience": "experience",
    "education":             "education",
    "academic":              "education",
    "qualification":         "education",
    "skills":                "skills",
    "technical skills":      "skills",
    "core competencies":     "skills",
    "expertise":             "skills",
    "projects":              "projects",
    "personal projects":     "projects",
    "key projects":          "projects",
    "internships":           "internships",
    "internship":            "internships",
    "certifications":        "certifications",
    "certificates":          "certifications",
    "licenses":              "certifications",
    "achievements":          "achievements",
    "awards":                "achievements",
    "honors":                "achievements",
    "publications":          "publications",
    "research":              "publications",
    "languages":             "languages",
    "interests":             "interests",
    "hobbies":               "interests",
    "volunteer":             "volunteer",
    "references":            "extras",
    "contact":               "header",
    "links":                 "header",
}


# ─────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────
def optimize_resume(resume_data: dict, jd_data: dict, analysis: dict,
                    job_category: dict | None = None) -> dict:
    """
    Build an optimized resume preserving ALL original content.

    job_category: optional dict from modules.job_categories.get_category(name)
                  used to enrich keyword injection and tips.
    """
    missing_skills   = list(analysis.get("missing_skills", []))
    matched_skills   = list(analysis.get("matched_skills", []))
    missing_keywords = list(analysis.get("missing_keywords", []))
    years_exp        = analysis.get("resume_years_experience", 0)

    raw_sections = resume_data.get("sections", {}) or {}
    full_text    = resume_data.get("full_text", "") or ""

    # 1) Canonicalize sections from the parser output.
    canon = _canonicalize_sections(raw_sections, full_text)

    # Header lives at the top of the resume — try to extract from raw text if missing.
    if not canon.get("header"):
        canon["header"] = _extract_header_block(full_text)

    # Determine a smart section order that mirrors the user's original resume order
    orig_order = _detect_original_section_order(raw_sections, SECTION_ORDER)

    optimized: dict[str, str] = {}
    improvements: dict[str, dict] = {}

    # Keep header verbatim (don't AI-mangle phone/email/links).
    optimized["header"] = canon.get("header", "")

    # 2) Summary — rewrite using JD context.
    summary_orig = canon.get("summary", "")
    job_title = _extract_job_title_from_jd(jd_data.get("full_text", ""))
    summary_res = rewrite_summary(
        summary_orig, job_title=job_title,
        missing_skills=missing_skills, years_exp=years_exp,
    )
    optimized["summary"] = summary_res["rewritten"]
    improvements["summary"] = {
        "original": summary_res["original"],
        "optimized": summary_res["rewritten"],
        "tip": summary_res["tip"],
    }

    # 3) Skills — inject missing skills + category-required skills.
    extra_skills = []
    if job_category:
        extra_skills = [s for s in job_category.get("required_skills", [])
                        if s.lower() not in (canon.get("skills", "") or "").lower()]
    optimized["skills"], skills_added = _optimize_skills_section(
        canon.get("skills", ""), missing_skills + extra_skills, matched_skills,
    )
    improvements["skills"] = {
        "original": canon.get("skills", ""),
        "optimized": optimized["skills"],
        "skills_added": skills_added,
        "tip": (f"Added {len(skills_added)} skill(s): "
                f"{', '.join(skills_added[:6])}") if skills_added else "Already comprehensive.",
    }

    # 4) Experience — bullet-by-bullet rewrite (action verbs + keyword sprinkle).
    exp_text = canon.get("experience", "")
    if exp_text.strip():
        exp_res = _rewrite_bullets_block(exp_text, missing_skills)
        optimized["experience"] = exp_res["optimized_text"]
        improvements["experience"] = exp_res
    else:
        optimized["experience"] = exp_text

    # 5) Projects — same treatment as experience.
    proj_text = canon.get("projects", "")
    if proj_text.strip():
        proj_res = _rewrite_bullets_block(proj_text, missing_skills[:5])
        optimized["projects"] = proj_res["optimized_text"]
        improvements["projects"] = proj_res
    else:
        optimized["projects"] = proj_text

    # 6) Internships — light bullet polish, preserve content.
    intern_text = canon.get("internships", "")
    if intern_text.strip():
        res = _rewrite_bullets_block(intern_text, missing_skills[:3])
        optimized["internships"] = res["optimized_text"]
        improvements["internships"] = res
    else:
        optimized["internships"] = intern_text

    # 7) Achievements — strengthen action verbs but keep facts.
    ach = canon.get("achievements", "")
    optimized["achievements"] = _polish_lines(ach) if ach.strip() else ach

    # Sections we preserve verbatim (factual content; never invent).
    for k in ("education", "certifications", "publications",
              "languages", "interests", "volunteer", "extras"):
        optimized[k] = canon.get(k, "")

    # 8) Build the full reading-order text (used by export & preview).
    full_optimized_text = _join_sections(optimized)

    # 9) Score / improvement metrics.
    full_original_text = _join_sections(canon)
    improvement_pct = _calculate_overall_improvement(
        full_original_text, full_optimized_text, missing_skills, analysis,
    )
    orig_ats = float(analysis.get("ats_score", 0) or 0)

    return {
        "original_sections":        canon,
        "optimized_sections":       optimized,
        "section_order":            orig_order,
        "section_labels":           SECTION_LABELS,
        "section_improvements":     improvements,
        "missing_skills_added":     skills_added,
        "missing_keywords_woven_in": missing_keywords[:8],
        "improvement_percentage":   improvement_pct,
        "original_ats_score":       orig_ats,
        "estimated_new_ats_score":  min(orig_ats + improvement_pct * 0.75, 96),
        "full_optimized_text":      full_optimized_text,
        "generated_at":             datetime.now().isoformat(),
        "resume_name":              resume_data.get("filename", "resume"),
        "job_category":             (job_category or {}).get("name") if job_category else None,
    }


# ─────────────────────────────────────────────────────────────
# Section helpers
# ─────────────────────────────────────────────────────────────
def _canonicalize_sections(raw: dict, full_text: str) -> dict:
    out: dict[str, str] = {}
    for raw_key, content in raw.items():
        if not isinstance(content, str):
            continue
        key = SECTION_ALIASES.get(raw_key.lower().strip(), raw_key.lower().strip())
        if key not in SECTION_ORDER:
            # unknown bucket → extras (but keep original label in content)
            out["extras"] = (out.get("extras", "") + "\n" + content).strip()
        else:
            out[key] = (out.get(key, "") + ("\n" if out.get(key) else "") + content).strip()

    # Fallback: pull obviously-named sections from the raw text if the parser missed.
    for k in ("certifications", "achievements", "publications", "languages",
              "internships", "interests", "volunteer"):
        if not out.get(k):
            extracted = _extract_section_from_text(full_text, k)
            if extracted:
                out[k] = extracted

    # Also try common aliases not in the fallback list
    alias_fallbacks = {
        "awards": "achievements",
        "certificates": "certifications",
        "training": "certifications",
        "portfolio": "extras",
        "links": "header",
        "hobbies": "interests",
        "activities": "interests",
        "references": "extras",
    }
    for alias, canon_key in alias_fallbacks.items():
        if not out.get(canon_key):
            extracted = _extract_section_from_text(full_text, alias)
            if extracted:
                out[canon_key] = extracted

    return out


def _extract_header_block(full_text: str) -> str:
    """Take the first 8 non-empty lines as the contact header (name, email, phone, links, location)."""
    lines = [l.strip() for l in full_text.splitlines() if l.strip()]
    if not lines:
        return ""
    # Grab up to 8 lines or until we hit what looks like a section heading
    header_lines = []
    section_markers = re.compile(
        r"^\s*(summary|objective|profile|experience|education|skills|projects|"
        r"certifications|achievements|internship|publications|languages|interests)\s*[:\s]*$",
        re.IGNORECASE
    )
    for line in lines[:10]:
        if section_markers.match(line):
            break
        header_lines.append(line)
        if len(header_lines) >= 8:
            break
    return "\n".join(header_lines)


def _detect_original_section_order(raw_sections: dict, default_order: list) -> list:
    """Return a section order that mirrors the user's original resume where possible."""
    seen = []
    for raw_key in raw_sections.keys():
        canon = SECTION_ALIASES.get(raw_key.lower().strip(), raw_key.lower().strip())
        if canon in default_order and canon not in seen:
            seen.append(canon)
    # Append any canonical sections not found in raw (extras, etc.) in default order
    for k in default_order:
        if k not in seen:
            seen.append(k)
    return seen


def _rewrite_bullets_block(block: str, skills_queue: list[str]) -> dict:
    """Rewrite bullet-like lines while preserving non-bullet headers (job titles,
    company names, dates) verbatim."""
    out_lines: list[str] = []
    bullets_improved: list[dict] = []
    si = 0
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            out_lines.append("")
            continue
        is_bullet = bool(re.match(r"^[\-\*\u2022\u25CF\u25E6\u25B8\u25BA\u2192\u2713]", stripped)) \
                    or (len(stripped) > 25 and stripped[0].isalpha() and stripped.endswith("."))
        if is_bullet and len(stripped) > 20:
            text = re.sub(r"^[\-\*\u2022\u25CF\u25E6\u25B8\u25BA\u2192\u2713]\s*", "", stripped)
            inject = [skills_queue[si]] if si < len(skills_queue) else []
            si += 1
            res = rewrite_bullet(text, inject)
            new_line = "• " + res["rewritten"]
            out_lines.append(new_line)
            if res["improvements"]:
                bullets_improved.append({
                    "original": stripped, "rewritten": new_line,
                    "improvements": res["improvements"],
                })
        else:
            out_lines.append(stripped)
    return {
        "original_text":  block,
        "optimized_text": "\n".join(out_lines).strip(),
        "bullets_improved": bullets_improved,
        "improved_count": len(bullets_improved),
    }


def _polish_lines(text: str) -> str:
    """Light cleanup: ensure lines start with action/strong verbs, trim filler."""
    fillers = ("responsible for ", "tasked with ", "duties included ",
               "worked on ", "helped to ")
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            out.append(""); continue
        low = s.lower()
        for f in fillers:
            if low.startswith(f):
                s = s[len(f):]
                s = s[:1].upper() + s[1:]
                break
        out.append(s)
    return "\n".join(out).strip()


def _optimize_skills_section(skills_text: str, missing_skills: list[str],
                              matched_skills: list[str]) -> tuple[str, list[str]]:
    if not skills_text.strip():
        all_skills = matched_skills + missing_skills[:12]
        return ", ".join(dict.fromkeys(all_skills)), missing_skills[:12]
    existing_lower = skills_text.lower()
    to_add = []
    for s in missing_skills:
        if s.lower() not in existing_lower and s not in to_add:
            to_add.append(s)
        if len(to_add) >= 12:
            break
    if not to_add:
        return skills_text, []
    sep = ", " if not skills_text.rstrip().endswith(",") else " "
    return skills_text.rstrip(" ,") + sep + ", ".join(to_add), to_add


def _join_sections(sections: dict) -> str:
    parts = []
    for key in SECTION_ORDER:
        text = (sections.get(key) or "").strip()
        if not text:
            continue
        if key == "header":
            parts.append(text)
            continue
        parts.append(SECTION_LABELS[key].upper())
        parts.append(text)
        parts.append("")
    return "\n".join(parts).strip()


def _extract_section_from_text(full_text: str, section_name: str) -> str:
    pat = rf"(?im)^\s*{re.escape(section_name)}\s*[:\n]+(.+?)(?=\n\s*[A-Z][A-Z &/]{{2,}}\s*\n|\Z)"
    m = re.search(pat, full_text, re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_job_title_from_jd(jd_text: str) -> str:
    patterns = [
        r"(?:position|role|title)[:\s]+([A-Z][a-zA-Z\s/\-]+(?:Engineer|Developer|Analyst|Manager|Designer|Architect|Lead|Director|Scientist))",
        r"^([A-Z][a-zA-Z\s/\-]+(?:Engineer|Developer|Analyst|Manager|Designer|Scientist))",
    ]
    for p in patterns:
        m = re.search(p, jd_text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    return "Professional"


def _calculate_overall_improvement(original: str, optimized: str,
                                    missing_skills: list[str], analysis: dict) -> float:
    base = 0.0
    skill_match   = analysis.get("skill_match_pct", 0)
    keyword_match = analysis.get("keyword_match_pct", 0)
    ats           = analysis.get("ats_score", 0)
    n_missing = len(missing_skills)
    if skill_match < 50:    base += 18
    elif skill_match < 65:  base += 12
    elif skill_match < 80:  base += 7
    if n_missing > 10:      base += 8
    elif n_missing > 5:     base += 5
    elif n_missing > 2:     base += 3
    if keyword_match < 50:  base += 12
    elif keyword_match < 65: base += 8
    elif keyword_match < 80: base += 4
    orig_words = len(original.split())
    opt_words  = len(optimized.split())
    word_growth = (opt_words - orig_words) / max(orig_words, 1)
    if word_growth > 0.05:
        base += min(word_growth * 20, 6.0)
    if ats < 45:   base += 10
    elif ats < 60: base += 6
    elif ats < 75: base += 3
    return round(min(base, 55.0), 1)


def generate_diff_report(original_sections: dict, optimized_sections: dict) -> list[dict]:
    diffs = []
    keys = set(original_sections) | set(optimized_sections)
    for k in SECTION_ORDER:
        if k not in keys: continue
        orig = (original_sections.get(k) or "").strip()
        opti = (optimized_sections.get(k) or "").strip()
        if not orig and not opti: continue
        ow, nw = set(orig.lower().split()), set(opti.lower().split())
        diffs.append({
            "section": SECTION_LABELS.get(k, k.title()),
            "original": orig, "optimized": opti,
            "words_added":   len(nw - ow),
            "words_removed": len(ow - nw),
            "changed":       orig != opti,
        })
    return diffs
