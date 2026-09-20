# ============================================================
# pages/9_Job_Resume.py
# Job-Ready Resume Generator — Full Resume Generation
# ============================================================
import time
import io
from pathlib import Path
import streamlit as st

from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import (
    run_analysis, save_analysis, load_latest_analysis,
)
from services.resume_service import save_resume, save_jd
from services.export_service import generate_optimized_pdf, generate_optimized_docx
from modules.optimizer import optimize_resume
from modules.job_categories import list_categories, get_category, detect_category

st.set_page_config(page_title="Job Resume · Resume Analyzer Pro", page_icon="🚀", layout="wide")
load_theme()
require_login()
uid = current_user_id()

with st.sidebar:
    uname = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:.75rem 0 1rem;">
      <div style="width:40px;height:40px;border-radius:50%;
                  background:linear-gradient(135deg,#059669,#34d399);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem;margin:0 auto .5rem;
                  box-shadow:0 0 16px rgba(52,211,153,.4);">🚀</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:.72rem;font-weight:700;color:#34d399;">{uname.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/3_Dashboard.py",         label="📊 Dashboard",   width="stretch")
    st.page_link("pages/4_Analyze.py",           label="🔬 Analyze",     width="stretch")
    st.page_link("pages/7_ATS_Deep_Dive.py",     label="🎯 ATS Dive",    width="stretch")
    st.page_link("pages/8_Rewrite_Assistant.py", label="✍️ Rewrite",     width="stretch")
    st.page_link("pages/6_History.py",           label="📂 History",     width="stretch")
    st.page_link("pages/10_Compare.py",          label="🔀 Compare",     width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()
st.markdown("""
<div style="text-align:center;padding:.75rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:800;
              background:linear-gradient(135deg,#34d399,#67e8f9 50%,#a78bfa);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    JOB-READY RESUME GENERATOR
  </div>
  <p style="color:#5c5880;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    Upload resume + job description · Get a fully optimized, downloadable resume
  </p>
</div>
""", unsafe_allow_html=True)

# ── How it works ────────────────────────────────────────────
st.markdown("""
<div class="glass-card fade-in" style="padding:1.25rem 2rem;margin-bottom:1rem;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">
    <div style="text-align:center;padding:.75rem;background:rgba(124,58,237,.08);border-radius:10px;">
      <div style="font-size:1.4rem;">📄</div>
      <div style="font-size:.8rem;color:#c4b5fd;font-weight:600;margin:.3rem 0;">1. Upload</div>
      <div style="font-size:.72rem;color:#94a3b8;">Your resume + job description</div>
    </div>
    <div style="text-align:center;padding:.75rem;background:rgba(6,182,212,.08);border-radius:10px;">
      <div style="font-size:1.4rem;">🧠</div>
      <div style="font-size:.8rem;color:#67e8f9;font-weight:600;margin:.3rem 0;">2. Analyze</div>
      <div style="font-size:.72rem;color:#94a3b8;">Deep ATS + gap analysis</div>
    </div>
    <div style="text-align:center;padding:.75rem;background:rgba(167,139,250,.08);border-radius:10px;">
      <div style="font-size:1.4rem;">✍️</div>
      <div style="font-size:.8rem;color:#a78bfa;font-weight:600;margin:.3rem 0;">3. Rewrite</div>
      <div style="font-size:.72rem;color:#94a3b8;">Full resume, every section</div>
    </div>
    <div style="text-align:center;padding:.75rem;background:rgba(34,197,94,.08);border-radius:10px;">
      <div style="font-size:1.4rem;">📥</div>
      <div style="font-size:.8rem;color:#86efac;font-weight:600;margin:.3rem 0;">4. Download</div>
      <div style="font-size:.72rem;color:#94a3b8;">PDF + DOCX, ATS-ready</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ────────────────────────────────────────────
CACHE_KEY = "job_resume_optimization"
ANALYSIS_KEY = "job_resume_analysis"

# Allow re-upload even if session analysis exists
with st.expander("📤 Upload Resume & Job Description", expanded=(CACHE_KEY not in st.session_state)):
    ui_c1, ui_c2 = st.columns(2, gap="large")
    with ui_c1:
        st.markdown("**📄 Resume** *(PDF / DOCX)*")
        jf = st.file_uploader("job_resume_file", type=["pdf", "docx", "doc"], label_visibility="collapsed",
                              key="job_resume_uploader")
    with ui_c2:
        st.markdown("**💼 Job Description**")
        jd_text = st.text_area("job_jd", height=200, label_visibility="collapsed",
                               placeholder="Paste the full job description here…",
                               key="job_resume_jd")

    cats = list_categories()
    detected_cat = detect_category(jd_text or "")
    default_idx = cats.index(detected_cat) if detected_cat in cats else 0
    selected_cat = st.selectbox("🎯 Job category", cats, index=default_idx, key="job_resume_category")

    gen_c1, gen_c2, gen_c3 = st.columns([1, 2, 1])
    with gen_c2:
        run_btn = st.button("⚡ Analyze & Generate Full Resume", type="primary", use_container_width=True)

if run_btn:
    if not jf:
        st.error("Please upload your resume (PDF or DOCX)."); st.stop()
    if not jd_text or len(jd_text.strip()) < 50:
        st.error("Please paste a job description (at least 50 characters)."); st.stop()

    # Clear previous result
    for k in [CACHE_KEY, ANALYSIS_KEY]:
        st.session_state.pop(k, None)

    prog = st.progress(0, text="🔍 Parsing resume…")
    file_bytes = jf.read()
    file_ext = Path(jf.name).suffix.lstrip(".")
    resume_id, _ = save_resume(uid, jf.name, file_bytes, file_ext)
    prog.progress(15, text="📝 Saving job description…")
    jd_id = save_jd(uid, jd_text)
    prog.progress(30, text="🧠 Running ATS analysis…")

    try:
        analysis = run_analysis(file_bytes, file_ext, jd_text)
    except Exception as e:
        prog.empty(); st.error(f"❌ Analysis error: {e}"); st.stop()

    aid = save_analysis(uid, resume_id, jd_id, analysis)
    st.session_state["analysis"] = analysis
    st.session_state["analysis_id"] = aid
    st.session_state["resume_filename"] = jf.name
    st.session_state[ANALYSIS_KEY] = analysis
    prog.progress(65, text="✍️ Generating full optimized resume…")

    from modules.parser import parse_resume, parse_job_description
    resume_data = parse_resume(file_bytes, file_ext)
    jd_data = parse_job_description(jd_text)
    cat = get_category(selected_cat) or {}
    cat = {**cat, "name": selected_cat}

    try:
        result = optimize_resume(resume_data, jd_data, analysis, job_category=cat)
    except Exception as e:
        prog.empty(); st.error(f"❌ Optimization error: {e}"); st.stop()

    prog.progress(95, text="💾 Saving…")
    st.session_state[CACHE_KEY] = result
    prog.progress(100, text="✅ Done!")
    time.sleep(0.3)
    prog.empty()
    st.rerun()

# ── Use session analysis as fallback (from History/Analyze pages) ────
if CACHE_KEY not in st.session_state:
    # Try loading from existing session analysis without re-uploading
    existing = st.session_state.get("analysis") or load_latest_analysis(uid)
    if existing and st.session_state.get("_jd_data_cache"):
        # Silently pre-load existing — user can still click generate above
        pass

# ── Results ──────────────────────────────────────────────────
if CACHE_KEY in st.session_state:
    result = st.session_state[CACHE_KEY]
    analysis = st.session_state.get(ANALYSIS_KEY) or st.session_state.get("analysis") or {}
    orig_score  = result.get("original_ats_score", analysis.get("ats_score", 0))
    est_score   = result.get("estimated_new_ats_score", 0)
    improvement = result.get("improvement_percentage", 0)
    skills_added = result.get("missing_skills_added", [])

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    def _stat(col, icon, label, val, color):
        col.markdown(f"""
        <div class="glass-card glass-card-accent fade-in" style="text-align:center;padding:1rem .5rem;">
          <div style="font-size:1.4rem;">{icon}</div>
          <div style="font-size:1.6rem;font-weight:700;color:{color};">{val}</div>
          <div style="font-size:.72rem;color:#94a3b8;">{label}</div>
        </div>""", unsafe_allow_html=True)

    _stat(s1, "📊", "Original ATS",     f"{orig_score:.1f}%",  "#f59e0b")
    _stat(s2, "🎯", "Estimated Score",  f"~{est_score:.0f}%",  "#22c55e")
    _stat(s3, "📈", "Improvement",      f"+{improvement:.0f}%", "#7c3aed")
    _stat(s4, "💡", "Skills Injected",  str(len(skills_added)), "#06b6d4")

    st.markdown("<br>", unsafe_allow_html=True)

    if skills_added:
        inner = "".join(f'<span class="tag tag-matched">{s}</span>' for s in skills_added)
        st.markdown(f"""
        <div class="glass-card fade-in" style="border-left:3px solid #22c55e;padding:1rem 1.5rem;">
          <div style="font-weight:600;color:#86efac;margin-bottom:.5rem;">✅ Missing skills injected into your resume</div>
          <div class="tag-container">{inner}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Preview + Download tabs
    tab_preview, tab_download = st.tabs(["📋 Full Resume Preview", "📥 Download"])

    with tab_preview:
        sections    = result.get("optimized_sections", {})
        sec_labels  = result.get("section_labels", {})
        sec_order   = result.get("section_order", list(sections.keys()))

        if not sections:
            st.info("No sections found in result. Try regenerating.")
        else:
            # Render a nicely formatted resume preview
            st.markdown("""
            <div style="max-width:860px;margin:0 auto;background:rgba(255,255,255,.03);
                        border:1px solid rgba(139,92,246,.2);border-radius:16px;
                        padding:2.5rem 3rem;font-family:'Inter',sans-serif;">
            """, unsafe_allow_html=True)

            for sec_key in sec_order:
                text = sections.get(sec_key, "")
                if not text or not text.strip():
                    continue
                label = sec_labels.get(sec_key, sec_key.replace("_", " ").title())

                # Header section — render as large name block
                if sec_key == "header":
                    st.markdown(f"""
                    <div style="border-bottom:2px solid rgba(139,92,246,.4);
                                padding-bottom:1rem;margin-bottom:1.2rem;">
                      <div style="white-space:pre-wrap;color:#e2e8f0;font-size:.92rem;
                                  line-height:1.7;">{text.strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Section header
                    st.markdown(f"""
                    <div style="margin-top:1.5rem;margin-bottom:.6rem;">
                      <div style="font-family:'Orbitron',sans-serif;font-size:.82rem;
                                  font-weight:700;color:#8b5cf6;letter-spacing:.1em;
                                  text-transform:uppercase;border-bottom:1px solid rgba(139,92,246,.25);
                                  padding-bottom:.4rem;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Content
                    formatted = text.strip()
                    # Convert bullet lines to styled HTML
                    lines = formatted.split("\n")
                    html_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith(("•", "-", "*", "–")):
                            content = stripped.lstrip("•-*–").strip()
                            html_lines.append(f'<div style="display:flex;gap:.5rem;margin:.25rem 0;color:#cbd5e1;font-size:.88rem;line-height:1.65;"><span style="color:#8b5cf6;margin-top:.1rem;">▸</span><span>{content}</span></div>')
                        elif stripped:
                            html_lines.append(f'<div style="color:#cbd5e1;font-size:.88rem;line-height:1.65;margin:.2rem 0;">{stripped}</div>')
                        else:
                            html_lines.append("<div style='height:.4rem;'></div>")

                    st.markdown("".join(html_lines), unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ATS badge
            st.markdown(f"""
            <div style="text-align:center;margin-top:1rem;">
              <span style="background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.3);
                           color:#86efac;padding:.35rem 1rem;border-radius:99px;font-size:.78rem;
                           font-weight:600;">✅ ATS-Optimized Resume · Estimated Score ~{est_score:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_download:
        resume_name = st.session_state.get("resume_filename", "optimized_resume")

        st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
        st.markdown("### 📥 Download Your Fully Optimized Resume")
        st.markdown('<p style="color:#94a3b8;">Your complete resume has been rewritten — every section optimized, keywords injected, bullets strengthened.</p>', unsafe_allow_html=True)

        dl1, dl2 = st.columns(2, gap="large")
        with dl1:
            st.markdown("""
            <div style="padding:1.5rem;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.2);border-radius:12px;text-align:center;">
              <div style="font-size:2rem;">📑</div>
              <div style="font-weight:600;margin:.5rem 0;">PDF Format</div>
              <div style="color:#94a3b8;font-size:.8rem;">Professionally formatted, print-ready, ATS-friendly</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            try:
                pdf_bytes = generate_optimized_pdf(result, resume_name)
                st.download_button("📑 Download PDF",
                    data=pdf_bytes,
                    file_name=f"optimized_{Path(resume_name).stem}.pdf",
                    mime="application/pdf",
                    use_container_width=True)
            except Exception as e:
                st.error(f"PDF error: {e}")

        with dl2:
            st.markdown("""
            <div style="padding:1.5rem;background:rgba(6,182,212,.06);border:1px solid rgba(6,182,212,.2);border-radius:12px;text-align:center;">
              <div style="font-size:2rem;">📄</div>
              <div style="font-weight:600;margin:.5rem 0;">DOCX Format</div>
              <div style="color:#94a3b8;font-size:.8rem;">Editable Word document — customize before submitting</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            try:
                docx_bytes = generate_optimized_docx(result, resume_name)
                st.download_button("📄 Download DOCX",
                    data=docx_bytes,
                    file_name=f"optimized_{Path(resume_name).stem}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            except Exception as e:
                st.error(f"DOCX error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset & Generate New"):
        for k in [CACHE_KEY, ANALYSIS_KEY]:
            st.session_state.pop(k, None)
        st.rerun()

elif not run_btn:
    # Show prompt to upload if nothing in session
    existing = st.session_state.get("analysis") or load_latest_analysis(uid)
    if not existing:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem;">
          <div class="float-anim" style="font-size:3rem;">🚀</div>
          <h3>Ready to generate your job-ready resume?</h3>
          <p style="color:#94a3b8;">Upload your resume and job description above, then click Generate.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("💡 You have a previous analysis in session. Upload a resume + job description above and click Generate to create a full optimized resume.")
