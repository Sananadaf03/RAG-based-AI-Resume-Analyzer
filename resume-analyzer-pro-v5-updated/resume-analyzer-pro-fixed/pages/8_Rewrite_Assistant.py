# ============================================================
# pages/8_Rewrite_Assistant.py
# AI Resume Rewrite Panel — Summary + Bulk Rewriter only
# ============================================================
import streamlit as st

from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import load_latest_analysis
from services.rewrite_service import rewrite_single_bullet, compute_improvement_pct
from modules.rewriter import (
    rewrite_experience_section, rewrite_summary,
    calculate_improvement_score, ACTION_VERBS,
)

st.set_page_config(page_title="AI Rewrite · Resume Analyzer Pro", page_icon="✍️", layout="wide")
load_theme()
require_login()
uid = current_user_id()

with st.sidebar:
    uname = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:.75rem 0 1rem;">
      <div style="width:40px;height:40px;border-radius:50%;
                  background:linear-gradient(135deg,#d97706,#fbbf24);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem;margin:0 auto .5rem;
                  box-shadow:0 0 16px rgba(251,191,36,.4);">✍️</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:.72rem;font-weight:700;color:#fbbf24;">{uname.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/3_Dashboard.py",         label="📊 Dashboard",   width="stretch")
    st.page_link("pages/4_Analyze.py",           label="🔬 Analyze",     width="stretch")
    st.page_link("pages/7_ATS_Deep_Dive.py",     label="🎯 ATS Dive",    width="stretch")
    st.page_link("pages/9_Job_Resume.py",        label="🚀 Job Resume",  width="stretch")
    st.page_link("pages/10_Compare.py",          label="🔀 Compare",     width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()
st.markdown("""
<div style="text-align:center;padding:.75rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:800;
              background:linear-gradient(135deg,#fbbf24,#f43f5e 50%,#a78bfa);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    AI REWRITE ASSISTANT
  </div>
  <p style="color:#5c5880;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    Transform weak bullets into ATS-optimized impact statements
  </p>
</div>
""", unsafe_allow_html=True)

analysis = st.session_state.get("analysis") or load_latest_analysis(uid)
missing_skills    = analysis.get("missing_skills", []) if analysis else []
matched_skills    = analysis.get("matched_skills", []) if analysis else []
missing_keywords  = list(analysis.get("missing_keywords", [])) if analysis else []
ats_score         = analysis.get("ats_score", 0) if analysis else 0

tabs = st.tabs([
    "📝 Summary Rewriter",
    "📋 Bulk Rewriter",
])

# ─────────────────────────────────────────────────────────────
# Tab 0: Summary Rewriter
# ─────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
    st.markdown("### 📝 Professional Summary Rewriter")
    st.markdown('<p style="color:#94a3b8;font-size:.9rem;">Craft an ATS-optimized professional summary tailored to your target role.</p>', unsafe_allow_html=True)

    sum_col1, sum_col2 = st.columns(2, gap="large")
    with sum_col1:
        orig_summary = st.text_area(
            "Your current summary (leave blank to generate from scratch):",
            height=150,
            placeholder="Results-driven developer with 3 years of experience...",
            key="summary_input",
        )
        job_title_input = st.text_input("Target job title:", placeholder="e.g. Senior Software Engineer")
        years_input = st.number_input("Years of experience:", min_value=0, max_value=50, value=3, step=1)
        top_skills_input = st.text_input(
            "Top 3 skills to highlight:",
            value=", ".join(missing_skills[:3]) if missing_skills else "",
            placeholder="Python, Machine Learning, AWS",
        )
        gen_summary_btn = st.button("✨ Generate Optimized Summary", type="primary")

    with sum_col2:
        if gen_summary_btn:
            skills_list = [s.strip() for s in top_skills_input.split(",") if s.strip()]
            with st.spinner("Crafting your summary..."):
                result = rewrite_summary(
                    orig_summary, job_title_input, skills_list, float(years_input)
                )
            st.markdown(f"""
            <div>
              {'<div class="rewrite-before"><div class="rewrite-label before">❌ Original</div><div class="rewrite-text">' + result["original"] + "</div></div><br>" if result["original"] else ""}
              <div class="rewrite-after">
                <div class="rewrite-label after">✅ Optimized Summary</div>
                <div class="rewrite-text" style="font-size:.95rem;line-height:1.65;">{result["rewritten"]}</div>
              </div>
              <div class="rewrite-tip" style="margin-top:.75rem;">💡 {result["tip"]}</div>
            </div>""", unsafe_allow_html=True)

            st.download_button(
                "📥 Copy as text",
                data=result["rewritten"],
                file_name="optimized_summary.txt",
                mime="text/plain",
            )
        else:
            st.markdown("""
            <div style="padding:3rem 1rem;text-align:center;color:#475569;">
              <div style="font-size:2.5rem;" class="float-anim">✍️</div>
              <p>Your optimized summary will appear here.</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Tab 1: Bulk Rewriter
# ─────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
    st.markdown("### 📋 Bulk Experience Rewriter")
    st.markdown('<p style="color:#94a3b8;font-size:.9rem;">Paste your entire experience section — every bullet gets rewritten.</p>', unsafe_allow_html=True)

    bulk_text = st.text_area(
        "Paste your experience section (one bullet per line):",
        height=200,
        placeholder="• Responsible for maintaining the codebase\n• Worked on machine learning models\n• Helped improve system performance\n• Led a team of engineers",
        key="bulk_exp_input",
    )
    bulk_cat = st.selectbox("Role category:", list(ACTION_VERBS.keys()), index=1, key="bulk_cat")
    bulk_btn = st.button("🔄 Rewrite All Bullets", type="primary")

    if bulk_btn and bulk_text.strip():
        with st.spinner("Rewriting experience section..."):
            rewrites = rewrite_experience_section(bulk_text, missing_skills, bulk_cat)

        total = len(rewrites)
        improved = sum(1 for r in rewrites if r.get("improvements"))
        st.success(f"✅ Rewrote {total} bullets — {improved} improved ({improved/max(total,1)*100:.0f}% improvement rate)")

        for i, rw in enumerate(rewrites, 1):
            with st.expander(f"Bullet {i} — {('Improved ✅' if rw.get('improvements') else 'Already good 👍')}"):
                st.markdown(f"""
                <div class="rewrite-before">
                  <div class="rewrite-label before">❌ Original</div>
                  <div class="rewrite-text">{rw['original']}</div>
                </div>
                <br>
                <div class="rewrite-after">
                  <div class="rewrite-label after">✅ Rewritten</div>
                  <div class="rewrite-text">{rw['rewritten']}</div>
                </div>""", unsafe_allow_html=True)
                if rw.get("improvements"):
                    st.caption("Changes: " + " · ".join(rw["improvements"]))
                if rw.get("tip"):
                    st.markdown(f'<div class="rewrite-tip">💡 {rw["tip"]}</div>', unsafe_allow_html=True)

        all_rewritten = "\n".join(f"• {r['rewritten']}" for r in rewrites)
        st.download_button(
            "📥 Download All Rewritten Bullets",
            data=all_rewritten,
            file_name="rewritten_experience.txt",
            mime="text/plain",
        )
    elif bulk_btn:
        st.warning("Please paste your experience section.")

    st.markdown("</div>", unsafe_allow_html=True)
