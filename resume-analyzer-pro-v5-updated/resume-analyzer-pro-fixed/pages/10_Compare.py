# ============================================================
# pages/10_Compare.py
# Resume Comparison — before vs after with diff highlighting
# ============================================================
import streamlit as st
import plotly.graph_objects as go

from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import load_latest_analysis
from modules.optimizer import optimize_resume, generate_diff_report
from modules.rewriter import calculate_improvement_score

st.set_page_config(page_title="Compare · Resume Analyzer Pro", page_icon="🔀", layout="wide")
load_theme()
require_login()
uid = current_user_id()

with st.sidebar:
    uname = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:.75rem 0 1rem;">
      <div style="width:40px;height:40px;border-radius:50%;
                  background:linear-gradient(135deg,#f43f5e,#fbbf24);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem;margin:0 auto .5rem;
                  box-shadow:0 0 16px rgba(244,63,94,.4);">🔀</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:.72rem;font-weight:700;color:#fda4af;">{uname.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/3_Dashboard.py",         label="📊 Dashboard",   width="stretch")
    st.page_link("pages/4_Analyze.py",           label="🔬 Analyze",     width="stretch")
    st.page_link("pages/7_ATS_Deep_Dive.py",     label="🎯 ATS Dive",    width="stretch")
    st.page_link("pages/8_Rewrite_Assistant.py", label="✍️ Rewrite",     width="stretch")
    st.page_link("pages/9_Job_Resume.py",        label="🚀 Job Resume",  width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()
st.markdown("""
<div style="text-align:center;padding:.75rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:800;
              background:linear-gradient(135deg,#f43f5e,#fbbf24 50%,#67e8f9);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    BEFORE / AFTER COMPARE
  </div>
  <p style="color:#5c5880;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    Section-by-section diff of every improvement
  </p>
</div>
""", unsafe_allow_html=True)

analysis = st.session_state.get("analysis") or load_latest_analysis(uid)

if not analysis:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem;">
      <div class="float-anim" style="font-size:3rem;">🔀</div>
      <h3>No analysis loaded</h3>
      <p style="color:#94a3b8;">Run an analysis and generate a resume first.</p>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/4_Analyze.py", label="→ Run Analysis")
    st.stop()

# ── Get or generate optimization ──────────────────────────
cache_key = "job_resume_optimization"
if cache_key not in st.session_state:
    st.info("💡 Generate an optimized resume first to see the comparison.")
    st.page_link("pages/9_Job_Resume.py", label="→ Generate Optimized Resume")

    # Offer to generate inline
    if st.button("⚡ Generate Optimization Now"):
        resume_data = st.session_state.get("_resume_data_cache", {
            "full_text": "", "sections": {}, "word_count": 0,
            "filename": st.session_state.get("resume_filename", "resume"),
        })
        jd_data = st.session_state.get("_jd_data_cache", {"full_text": ""})
        with st.spinner("Optimizing..."):
            result = optimize_resume(resume_data, jd_data, analysis)
        st.session_state[cache_key] = result
        st.rerun()
    st.stop()

result = st.session_state[cache_key]
orig_sections  = result.get("original_sections", {})
opti_sections  = result.get("optimized_sections", {})
orig_score     = result.get("original_ats_score", 0)
est_score      = result.get("estimated_new_ats_score", 0)
improvement    = result.get("improvement_percentage", 0)
skills_added   = result.get("missing_skills_added", [])

# ── Score comparison gauge ─────────────────────────────────
st.markdown("### 📊 Score Improvement")
ga, gb, gc = st.columns([1, 2, 1])

def mini_gauge(val, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={"text": title, "font": {"size": 13, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "white", "size": 9}},
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "rgba(255,255,255,0.04)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "rgba(239,68,68,0.1)"},
                {"range": [35, 65], "color": "rgba(245,158,11,0.1)"},
                {"range": [65, 100], "color": "rgba(34,197,94,0.1)"},
            ],
        },
        number={"suffix": "%", "font": {"size": 28, "color": color}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=220, margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig

with ga:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(mini_gauge(orig_score, "Original Score", "#f59e0b"),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with gb:
    st.markdown(f"""
    <div class="glass-card glass-card-accent fade-in" style="text-align:center;padding:2rem 1rem;">
      <div style="font-size:3rem;font-weight:800;color:#22c55e;">+{improvement:.0f}%</div>
      <div style="color:#86efac;font-size:1rem;font-weight:600;">Estimated Improvement</div>
      <br>
      <div class="tag-container" style="justify-content:center;">
        <span class="tag tag-matched">+{len(skills_added)} skills added</span>
        <span class="tag tag-matched">Stronger bullets</span>
        <span class="tag tag-matched">Keywords injected</span>
      </div>
      <br>
      <p style="color:#94a3b8;font-size:.8rem;">Based on local NLP analysis · No AI APIs used</p>
    </div>""", unsafe_allow_html=True)

with gc:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(mini_gauge(min(est_score, 98), "Estimated New Score", "#22c55e"),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Section-by-section diff ────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🔍 Section-by-Section Comparison")

diffs = generate_diff_report(orig_sections, opti_sections)
changed_sections = [d for d in diffs if d["changed"]]
unchanged_sections = [d for d in diffs if not d["changed"]]

st.markdown(f"""
<div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
  <div style="padding:.5rem 1rem;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.3);border-radius:8px;font-size:.85rem;color:#86efac;">
    ✅ {len(changed_sections)} sections improved
  </div>
  <div style="padding:.5rem 1rem;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:8px;font-size:.85rem;color:#94a3b8;">
    ≡ {len(unchanged_sections)} sections unchanged
  </div>
</div>""", unsafe_allow_html=True)

# Show changed sections
for diff in diffs:
    section_name = diff["section"]
    is_changed = diff["changed"]
    is_new = diff.get("is_new", False)

    badge = ("🆕 NEW" if is_new else "✅ IMPROVED" if is_changed else "≡ UNCHANGED")
    badge_color = "#22c55e" if is_changed or is_new else "#6b7280"

    with st.expander(f"{section_name}  —  {badge}", expanded=is_changed):
        if is_changed:
            col_orig, col_opti = st.columns(2, gap="large")

            with col_orig:
                st.markdown("""
                <div style="margin-bottom:.5rem;">
                  <span style="background:rgba(239,68,68,.2);color:#fca5a5;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700;">❌ ORIGINAL</span>
                </div>""", unsafe_allow_html=True)
                orig_text = diff.get("original", "")
                if orig_text:
                    st.code(orig_text, language=None)
                else:
                    st.markdown('<p style="color:#6b7280;font-style:italic;">No original content</p>',
                                unsafe_allow_html=True)

            with col_opti:
                st.markdown("""
                <div style="margin-bottom:.5rem;">
                  <span style="background:rgba(34,197,94,.2);color:#86efac;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700;">✅ OPTIMIZED</span>
                </div>""", unsafe_allow_html=True)
                opti_text = diff.get("optimized", "")
                if opti_text:
                    st.code(opti_text, language=None)
                else:
                    st.markdown('<p style="color:#6b7280;font-style:italic;">No content generated</p>',
                                unsafe_allow_html=True)

            # Change stats
            words_added = diff.get("words_added", 0)
            words_removed = diff.get("words_removed", 0)
            if words_added > 0 or words_removed > 0:
                st.caption(f"Changes: +{words_added} words added · -{words_removed} words removed")
        else:
            st.markdown(f"""
            <div style="padding:.75rem;background:rgba(255,255,255,.02);border-radius:8px;color:#6b7280;font-size:.85rem;">
              This section was not modified — it already met quality standards.
            </div>""", unsafe_allow_html=True)
            if diff.get("original"):
                with st.container():
                    st.code(diff["original"][:500], language=None)

# ── Improvement summary ────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if skills_added:
    st.markdown(f"""
    <div class="glass-card fade-in" style="border-left:4px solid #22c55e;">
      <div class="section-header">
        <span class="section-icon">💡</span>
        <span class="section-title">Key Improvements Summary</span>
      </div>
      <ul style="color:#cbd5e1;font-size:.9rem;line-height:2;margin:.5rem 0;">
        <li>Added <strong>{len(skills_added)} missing skills</strong> to your skills section: {', '.join(skills_added[:5])}</li>
        <li>Replaced weak openers ("responsible for", "helped with") with strong action verbs</li>
        <li>Added quantified impact metrics to experience bullets</li>
        <li>Rewrote professional summary to match job description</li>
        <li>Estimated ATS score increase: <strong>+{improvement:.0f}%</strong></li>
      </ul>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/9_Job_Resume.py", label="📥 Download Optimized Resume →")
with c2:
    st.page_link("pages/8_Rewrite_Assistant.py", label="✍️ Manual Rewrite Assistant →")
