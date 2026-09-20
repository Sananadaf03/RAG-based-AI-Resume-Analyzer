import time
from pathlib import Path
import streamlit as st

from utils.theme import load_theme
from services.auth_service import require_login, current_user_id, logout
from services.resume_service import save_resume, save_jd
from services.analysis_service import run_analysis, save_analysis

# Existing UI helpers from your codebase — reused
from utils.charts import (
    score_gauge, skill_donut, score_breakdown_radar,
    skills_by_category_bar, keyword_gap_hbar,
)
from utils.report_generator import generate_text_report, generate_pdf_report

st.set_page_config(page_title="Analyze · Resume Analyzer Pro", page_icon="🔬", layout="wide")
load_theme()
require_login()
uid = current_user_id()


# ─── helpers (copied from original app.py, trimmed) ─────────
def render_progress_bar(label, value, color="accent"):
    grad = {
        "accent":  "linear-gradient(90deg,#7c3aed,#06b6d4)",
        "success": "linear-gradient(90deg,#16a34a,#22c55e)",
        "warning": "linear-gradient(90deg,#d97706,#f59e0b)",
        "danger":  "linear-gradient(90deg,#dc2626,#ef4444)",
    }[color]
    return f"""
    <div class="progress-container">
      <div class="progress-label"><span>{label}</span><span>{value:.1f}%</span></div>
      <div class="progress-bar-track"><div class="progress-bar-fill" style="width:{value}%;background:{grad};"></div></div>
    </div>"""


def render_tags(items, cls):
    if not items:
        return '<p style="color:#475569;font-size:.85rem;">None.</p>'
    inner = "".join(f'<span class="tag {cls}">{x}</span>' for x in items)
    return f'<div class="tag-container">{inner}</div>'


def score_class(s):
    return ("score-excellent" if s >= 75 else
            "score-good" if s >= 55 else "score-poor")


# ─── sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    st.page_link("pages/3_Dashboard.py", label="📊 Dashboard", width="stretch")
    st.page_link("pages/6_History.py", label="📂 History", width="stretch")
    if st.button("🚪 Log out", width="stretch"):
        logout(); st.rerun()


# ─── header ────────────────────────────────────────────────
st.markdown("""
<div class="hero-container fade-in" style="padding:2rem 1rem 1rem;">
  <h1 class="hero-title" style="font-size:2.2rem !important;">🔬 Analyze Resume</h1>
  <p class="hero-subtitle">Upload a resume + paste a job description. Get a deep ATS analysis.</p>
  <p style="font-size:.78rem;color:#7c6fa0;margin-top:.4rem;">
    Scoring model v2 — calibrated across semantic similarity, skill match, keyword density,
    experience alignment, education, and format quality.
  </p>
</div>
""", unsafe_allow_html=True)


# ─── inputs ────────────────────────────────────────────────
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("**📄 Resume** *(PDF / DOCX)*")
    f = st.file_uploader("resume", type=["pdf", "docx", "doc"], label_visibility="collapsed")
with c2:
    st.markdown("**💼 Job Description**")
    jd = st.text_area("jd", height=220, label_visibility="collapsed",
                      placeholder="Paste the full job description here…")

if st.button("🚀 Analyze Resume"):
    if not f:
        st.error("Upload a resume first."); st.stop()
    if not jd or len(jd.strip()) < 50:
        st.error("Paste a job description (min 50 chars)."); st.stop()

    prog = st.progress(0, text="🔍 Saving resume…")
    file_bytes = f.read()
    file_ext = Path(f.name).suffix.lstrip(".")
    resume_id, _ = save_resume(uid, f.name, file_bytes, file_ext)
    prog.progress(15, text="📝 Saving job description…")
    jd_id = save_jd(uid, jd)
    prog.progress(30, text="🧠 Building embedding index (first run downloads ~22MB)…")

    try:
        result = run_analysis(file_bytes, file_ext, jd)
    except Exception as e:
        prog.empty(); st.error(f"❌ {e}"); st.stop()

    prog.progress(85, text="💾 Saving analysis…")
    aid = save_analysis(uid, resume_id, jd_id, result)
    prog.progress(100, text="✅ Done!"); time.sleep(0.3); prog.empty()

    st.session_state["analysis"] = result
    st.session_state["analysis_id"] = aid
    st.session_state["resume_filename"] = f.name


# ─── results ───────────────────────────────────────────────
analysis = st.session_state.get("analysis")
if analysis:
    fname = st.session_state.get("resume_filename", "resume")
    score = analysis["ats_score"]

    # download buttons
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📥 Export")
        st.download_button("📄 Text Report",
                           data=generate_text_report(analysis, fname),
                           file_name="resume_analysis.txt",
                           mime="text/plain", width="stretch")
        try:
            pdf = generate_pdf_report(analysis, fname)
            st.download_button("📑 PDF Report", data=pdf,
                               file_name="resume_analysis.pdf",
                               mime="application/pdf", width="stretch")
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")

    tabs = st.tabs(["🏠 Overview", "🎯 Skills", "🔑 Keywords", "💡 Suggestions", "✍️ Rewrites"])

    # Overview
    with tabs[0]:
        cg, cb = st.columns([1, 1.4], gap="large")
        with cg:
            st.markdown(f"""
            <div class="glass-card glass-card-accent" style="text-align:center;padding:2rem 1rem;">
              <div class="score-number {score_class(score)}">{score:.1f}%</div>
              <div class="score-label">Confidence: {analysis['confidence_score']:.1f}%</div>
            </div>""", unsafe_allow_html=True)
            dims = [
                ("Semantic", analysis["semantic_similarity"]),
                ("Skills",   analysis["skill_match_pct"]),
                ("Keywords", analysis["keyword_match_pct"]),
                ("Experience", analysis["experience_score"]),
                ("Education",  analysis["education_score"]),
                ("Format",     analysis["format_score"]),
            ]
            bars = "".join(render_progress_bar(l, v,
                            "success" if v >= 70 else "warning" if v >= 45 else "danger")
                           for l, v in dims)
            st.markdown(f'<div class="glass-card">{bars}</div>', unsafe_allow_html=True)
        with cb:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.plotly_chart(score_breakdown_radar(analysis), width="stretch",
                            config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    # Skills
    with tabs[1]:
        a, b = st.columns([1, 1.2], gap="large")
        with a:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.plotly_chart(skill_donut(analysis.get("matched_skills", []),
                                        analysis.get("missing_skills", [])),
                            width="stretch", config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with b:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.plotly_chart(skills_by_category_bar(
                analysis.get("resume_skills_by_category", {}),
                analysis.get("jd_skills_by_category", {})),
                width="stretch", config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        m, mi, ex = st.columns(3)
        m.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">✅</span><span class="section-title">Matched</span></div>{render_tags(analysis.get("matched_skills",[]),"tag-matched")}</div>', unsafe_allow_html=True)
        mi.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">❌</span><span class="section-title">Missing</span></div>{render_tags(analysis.get("missing_skills",[]),"tag-missing")}</div>', unsafe_allow_html=True)
        ex.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">⭐</span><span class="section-title">Bonus</span></div>{render_tags(analysis.get("extra_skills",[])[:20],"tag-extra")}</div>', unsafe_allow_html=True)

    # Keywords
    with tabs[2]:
        a, b = st.columns([1.3, 1], gap="large")
        with a:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.plotly_chart(keyword_gap_hbar(analysis.get("matched_keywords", []),
                                             analysis.get("missing_keywords", [])),
                            width="stretch", config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">🔑</span><span class="section-title">Missing Keywords</span></div>{render_tags(sorted(analysis.get("missing_keywords",[]))[:20],"tag-missing")}</div>', unsafe_allow_html=True)

    # Suggestions
    with tabs[3]:
        for sug in analysis.get("improvement_suggestions", []):
            cls = {"HIGH": "priority-high", "MEDIUM": "priority-medium", "LOW": "priority-low"}.get(sug.get("priority"), "")
            st.markdown(f"""
            <div class="suggestion-card {cls}">
              <div class="suggestion-category">{sug.get('category','')}</div>
              <div class="suggestion-text">→ {sug.get('suggestion','')}</div>
              <div class="suggestion-impact">💡 {sug.get('impact','')}</div>
            </div>""", unsafe_allow_html=True)

    # Rewrites
    with tabs[4]:
        for i, rw in enumerate(analysis.get("rewrite_bullets", []), 1):
            st.markdown(f"""
            <div class="rewrite-card fade-in stagger-{min(i,5)}">
              <div class="rewrite-before"><div class="rewrite-label before">❌ Before</div><div class="rewrite-text">{rw.get('before','')}</div></div>
              <div class="rewrite-after"><div class="rewrite-label after">✅ After</div><div class="rewrite-text">{rw.get('after','')}</div></div>
              <div class="rewrite-tip">💡 {rw.get('tip','')}</div>
            </div>""", unsafe_allow_html=True)




