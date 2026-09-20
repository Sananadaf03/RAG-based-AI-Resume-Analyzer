# ============================================================
# services/rewrite_service.py
# Resume Rewrite & Optimization Service
# ============================================================
import streamlit as st
from db.database import get_session
from db.models import Analysis
from modules.rewriter import rewrite_bullet, rewrite_summary, calculate_improvement_score
from modules.optimizer import optimize_resume, generate_diff_report


def get_or_run_optimization(analysis: dict, resume_data: dict, jd_data: dict) -> dict:
    """
    Run resume optimization if not already cached in session.
    Returns optimization result dict.
    """
    cache_key = f"optimization_{hash(str(analysis.get('ats_score', 0)))}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    result = optimize_resume(resume_data, jd_data, analysis)
    st.session_state[cache_key] = result
    return result


def rewrite_single_bullet(bullet: str, missing_skills: list[str] = None,
                           category: str = "development") -> dict:
    """Rewrite a single bullet point interactively."""
    return rewrite_bullet(bullet, missing_skills or [], category)


def get_diff_report(optimization_result: dict) -> list[dict]:
    """Generate section-by-section comparison report."""
    return generate_diff_report(
        optimization_result["original_sections"],
        optimization_result["optimized_sections"],
    )


def compute_improvement_pct(original: str, rewritten: str) -> float:
    return calculate_improvement_score(original, rewritten)
