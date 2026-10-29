# ============================================================
# services/analysis_service.py
# Wraps the existing RAG + ATS pipeline and persists results.
# Performance: singleton analyzer + cached JD parsing.
# ============================================================
import hashlib
import streamlit as st
from db.database import get_session
from db.models import Analysis
from modules.parser import parse_resume, parse_job_description
from modules.retriever import build_retriever_from_resume
from modules.analyzer import ATSAnalyzer


# ── Singleton analyzer (model loaded once, reused) ──────────
@st.cache_resource(show_spinner=False)
def _get_analyzer() -> ATSAnalyzer:
    return ATSAnalyzer()


# ── Cache JD parsing (same JD text → same result) ──────────
@st.cache_data(show_spinner=False, ttl=3600)
def _parse_jd_cached(jd_text: str) -> dict:
    return parse_job_description(jd_text)


def run_analysis(resume_bytes: bytes, file_ext: str, jd_text: str) -> dict:
    """Pure pipeline — stateless, optimized with caching."""
    resume_data = parse_resume(resume_bytes, file_ext)
    jd_data = _parse_jd_cached(jd_text)
    retriever = build_retriever_from_resume(resume_data, alpha=0.6)
    chunks = retriever.retrieve_for_jd_sections(jd_data["chunks"], top_k_per_chunk=4)
    return _get_analyzer().analyze(
        resume_data=resume_data, jd_data=jd_data,
        retriever=retriever, retrieved_chunks=chunks,
    )


def save_analysis(user_id: int, resume_id: int, jd_id: int | None, result: dict) -> int:
    with get_session() as s:
        a = Analysis(
            user_id=user_id, resume_id=resume_id, jd_id=jd_id,
            ats_score=float(result.get("ats_score", 0)), result=result,
        )
        s.add(a); s.commit(); s.refresh(a)
        return a.id


def list_analyses(user_id: int, limit: int = 200) -> list[dict]:
    with get_session() as s:
        rows = (s.query(Analysis).filter_by(user_id=user_id)
                .order_by(Analysis.created_at.desc()).limit(limit).all())
        return [{"id": a.id, "ats_score": a.ats_score,
                 "created_at": a.created_at, "resume_id": a.resume_id} for a in rows]


@st.cache_data(show_spinner=False, ttl=300)
def load_analysis(analysis_id: int, user_id: int) -> dict | None:
    with get_session() as s:
        a = s.query(Analysis).filter_by(id=analysis_id, user_id=user_id).first()
        return a.result if a else None


def load_latest_analysis(user_id: int) -> dict | None:
    with get_session() as s:
        a = (s.query(Analysis)
               .filter_by(user_id=user_id)
               .order_by(Analysis.created_at.desc())
               .first())
        return a.result if a else None
