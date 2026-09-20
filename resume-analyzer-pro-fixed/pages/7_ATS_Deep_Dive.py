# ============================================================
# pages/7_ATS_Deep_Dive.py
# Advanced ATS Dashboard — animated metrics, deep skill analysis
# ============================================================
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import load_latest_analysis, list_analyses

st.set_page_config(page_title="ATS Deep Dive · Resume Analyzer Pro", page_icon="🎯", layout="wide")
load_theme()
require_login()
uid = current_user_id()

with st.sidebar:
    uname = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:.75rem 0 1rem;">
      <div style="width:40px;height:40px;border-radius:50%;
                  background:linear-gradient(135deg,#6d28d9,#e879f9);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem;margin:0 auto .5rem;
                  box-shadow:0 0 16px rgba(232,121,249,.4);">🎯</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:.72rem;font-weight:700;color:#c4b5fd;">{uname.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/3_Dashboard.py",        label="📊 Dashboard",     width="stretch")
    st.page_link("pages/4_Analyze.py",          label="🔬 Analyze",       width="stretch")
    st.page_link("pages/8_Rewrite_Assistant.py",label="✍️ Rewrite",       width="stretch")
    st.page_link("pages/9_Job_Resume.py",       label="🚀 Job Resume",    width="stretch")
    st.page_link("pages/10_Compare.py",         label="🔀 Compare",       width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()
st.markdown("""
<div style="text-align:center;padding:.75rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:800;
              background:linear-gradient(135deg,#fff,#e879f9 50%,#67e8f9);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    ATS DEEP DIVE
  </div>
  <p style="color:#5c5880;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    Granular breakdown of every scoring dimension
  </p>
</div>
""", unsafe_allow_html=True)

analysis = st.session_state.get("analysis") or load_latest_analysis(uid)

if not analysis:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem;">
      <div class="float-anim" style="font-size:3rem;">🎯</div>
      <h3>No analysis loaded</h3>
      <p style="color:#94a3b8;">Run an analysis first to see your deep ATS breakdown.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Analyze.py", label="→ Run Analysis")
    st.stop()

score = analysis.get("ats_score", 0)

# ── Top KPI row ────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpi_style = "glass-card glass-card-accent"

def kpi_card(col, icon, label, value, color, glow):
    col.markdown(f"""
    <div class="{kpi_style} fade-in" style="text-align:center;padding:1.4rem .5rem;
         border-color:rgba(139,92,246,.25);">
      <div style="font-size:1.8rem;margin-bottom:.3rem;">{icon}</div>
      <div style="font-size:1.75rem;font-weight:900;font-family:'Orbitron',sans-serif;
                  color:{color};text-shadow:0 0 20px {glow};">{value}</div>
      <div style="font-size:.65rem;color:#5c5880;text-transform:uppercase;
                  letter-spacing:.08em;margin-top:.3rem;">{label}</div>
    </div>""", unsafe_allow_html=True)

score_color = "#34d399" if score >= 75 else "#fbbf24" if score >= 55 else "#f43f5e"
score_glow  = "rgba(52,211,153,.5)" if score >= 75 else "rgba(251,191,36,.5)" if score >= 55 else "rgba(244,63,94,.5)"
kpi_card(k1, "🏆", "ATS Score",    f"{score:.1f}%",                              score_color, score_glow)
kpi_card(k2, "🎯", "Skill Match",  f"{analysis.get('skill_match_pct',0):.1f}%",  "#a78bfa", "rgba(167,139,250,.5)")
kpi_card(k3, "🔑", "Keyword Match",f"{analysis.get('keyword_match_pct',0):.1f}%","#67e8f9", "rgba(103,232,249,.5)")
kpi_card(k4, "🧠", "Semantic Sim.",f"{analysis.get('semantic_similarity',0):.1f}%","#e879f9","rgba(232,121,249,.5)")
kpi_card(k5, "📊", "Format Score", f"{analysis.get('format_score',0):.1f}%",     "#34d399", "rgba(52,211,153,.5)")

st.markdown("<br>", unsafe_allow_html=True)

# ── Animated progress bars ─────────────────────────────────
dims = [
    ("🧠 Semantic Similarity",   analysis.get("semantic_similarity", 0),    "accent"),
    ("🎯 Skill Match",            analysis.get("skill_match_pct", 0),        "accent"),
    ("🔑 Keyword Match",          analysis.get("keyword_match_pct", 0),      "accent"),
    ("⏳ Experience Alignment",   analysis.get("experience_score", 0),       "warning"),
    ("🎓 Education Match",        analysis.get("education_score", 0),        "warning"),
    ("📝 Format Quality",         analysis.get("format_score", 0),           "success"),
]

GRAD = {
    "accent":  "linear-gradient(90deg,#8b5cf6,#22d3ee)",
    "success": "linear-gradient(90deg,#059669,#34d399)",
    "warning": "linear-gradient(90deg,#d97706,#fbbf24)",
    "danger":  "linear-gradient(90deg,#dc2626,#f43f5e)",
}

def gradient_for(val, name):
    if val >= 75: return GRAD["success"]
    if val >= 55: return GRAD["warning"]
    return GRAD["danger"]

bars_html = '<div class="glass-card fade-in" style="padding:1.5rem 2rem;">'
bars_html += '<div class="section-header"><span class="section-icon">📊</span><span class="section-title" style="font-size:1rem;font-weight:700;">Scoring Dimensions</span></div><br>'
for label, val, _ in dims:
    g = gradient_for(val, label)
    status = "✅ Strong" if val >= 75 else "⚠️ Average" if val >= 55 else "❌ Weak"
    bars_html += f"""
    <div class="progress-container">
      <div class="progress-label">
        <span>{label}</span>
        <span style="display:flex;gap:8px;align-items:center;">
          <span style="font-size:.72rem;color:#94a3b8;">{status}</span>
          <span style="font-weight:600;">{val:.1f}%</span>
        </span>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" style="width:{val}%;background:{g};"></div>
      </div>
    </div>"""
bars_html += "</div>"
st.markdown(bars_html, unsafe_allow_html=True)

# ── Skill Analysis ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
sa, sb = st.columns(2, gap="large")

with sa:
    matched = analysis.get("matched_skills", [])
    missing = analysis.get("missing_skills", [])
    extra   = analysis.get("extra_skills", [])[:20]

    # Donut chart
    fig_d = go.Figure(go.Pie(
        labels=["Matched", "Missing"],
        values=[len(matched), len(missing)],
        hole=0.65,
        marker=dict(colors=["#22c55e", "#ef4444"],
                    line=dict(color="rgba(0,0,0,0.2)", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="white"),
    ))
    fig_d.add_annotation(
        text=f"<b>{len(matched)}<br><span style='font-size:10px'>matched</span></b>",
        x=0.5, y=0.5, font=dict(size=18, color="white"), showarrow=False,
    )
    fig_d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"), height=280,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        title=dict(text="Skill Coverage", font=dict(color="white", size=14), x=0.5),
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with sb:
    # Skills by category
    resume_cat = analysis.get("resume_skills_by_category", {})
    jd_cat = analysis.get("jd_skills_by_category", {})
    all_cats = sorted(set(list(resume_cat.keys()) + list(jd_cat.keys())))
    if all_cats:
        df_cat = pd.DataFrame({
            "Category": [c.replace("_", " ").title() for c in all_cats],
            "Your Resume": [len(resume_cat.get(c, [])) for c in all_cats],
            "Job Description": [len(jd_cat.get(c, [])) for c in all_cats],
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Your Resume", x=df_cat["Category"],
                                  y=df_cat["Your Resume"],
                                  marker=dict(color="#8b5cf6", opacity=0.85)))
        fig_bar.add_trace(go.Bar(name="Job Description", x=df_cat["Category"],
                                  y=df_cat["Job Description"],
                                  marker=dict(color="#22d3ee", opacity=0.75)))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a8a4c8", family="Orbitron", size=9), height=280,
            barmode="group",
            margin=dict(l=0, r=0, t=30, b=40),
            xaxis=dict(tickfont=dict(size=8), gridcolor="rgba(139,92,246,0.08)"),
            yaxis=dict(gridcolor="rgba(139,92,246,0.08)"),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(size=9)),
            title=dict(text="Skills by Category", font=dict(color="#c4b5fd", size=13, family="Orbitron"), x=0.5),
        )
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ── Skill tag tables ───────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
tc1, tc2, tc3 = st.columns(3, gap="medium")

def render_skill_tags(skills, css_class):
    if not skills:
        return '<p style="color:#475569;font-size:.85rem;">None detected.</p>'
    return '<div class="tag-container">' + \
           "".join(f'<span class="tag {css_class}">{s}</span>' for s in skills) + \
           "</div>"

tc1.markdown(f"""
<div class="glass-card fade-in">
  <div class="section-header">
    <span class="section-icon">✅</span>
    <span class="section-title">Matched Skills ({len(matched)})</span>
  </div>
  {render_skill_tags(matched, "tag-matched")}
</div>""", unsafe_allow_html=True)

tc2.markdown(f"""
<div class="glass-card fade-in stagger-1">
  <div class="section-header">
    <span class="section-icon">❌</span>
    <span class="section-title">Missing Skills ({len(missing)})</span>
  </div>
  {render_skill_tags(missing, "tag-missing")}
  {'<p style="margin-top:.75rem;font-size:.8rem;color:#94a3b8;">💡 Add these to your skills section & work experience.</p>' if missing else ''}
</div>""", unsafe_allow_html=True)

tc3.markdown(f"""
<div class="glass-card fade-in stagger-2">
  <div class="section-header">
    <span class="section-icon">⭐</span>
    <span class="section-title">Bonus Skills ({len(extra)})</span>
  </div>
  {render_skill_tags(extra, "tag-extra")}
  {'<p style="margin-top:.75rem;font-size:.8rem;color:#94a3b8;">✨ These differentiate you — highlight them!</p>' if extra else ''}
</div>""", unsafe_allow_html=True)

# ── Keyword Gap Analysis ───────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><span class="section-icon">🔑</span><span class="section-title" style="font-size:1.1rem;font-weight:700;">Keyword Gap Analysis</span></div>', unsafe_allow_html=True)

matched_kw = sorted(analysis.get("matched_keywords", []))[:15]
missing_kw = sorted(analysis.get("missing_keywords", []))[:15]

kwa, kwb = st.columns(2, gap="large")
with kwa:
    st.markdown(f"""
    <div class="glass-card fade-in">
      <div class="section-header"><span class="section-icon">✅</span><span class="section-title">Present Keywords ({len(matched_kw)})</span></div>
      <div class="tag-container">
        {"".join(f'<span class="tag tag-matched">{k}</span>' for k in matched_kw)}
      </div>
    </div>""", unsafe_allow_html=True)

with kwb:
    st.markdown(f"""
    <div class="glass-card fade-in stagger-1">
      <div class="section-header"><span class="section-icon">❌</span><span class="section-title">Missing Keywords ({len(missing_kw)})</span></div>
      <div class="tag-container">
        {"".join(f'<span class="tag tag-missing">{k}</span>' for k in missing_kw)}
      </div>
      <p style="margin-top:.75rem;font-size:.8rem;color:#94a3b8;">
        💡 Weave these naturally into your bullet points and summary.
      </p>
    </div>""", unsafe_allow_html=True)

# ── Score History ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
analyses_hist = list_analyses(uid)
if len(analyses_hist) > 1:
    st.markdown('<div class="section-header"><span class="section-icon">📈</span><span class="section-title" style="font-size:1.1rem;font-weight:700;">ATS Score Journey</span></div>', unsafe_allow_html=True)
    df_h = pd.DataFrame(analyses_hist).sort_values("created_at")
    fig_h = px.area(df_h, x="created_at", y="ats_score",
                    labels={"created_at": "Date", "ats_score": "ATS Score"})
    fig_h.update_traces(
        line=dict(color="#7c3aed", width=3),
        fillcolor="rgba(124,58,237,0.15)",
    )
    fig_h.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"), height=260,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 100]),
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Improvement Suggestions ────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><span class="section-icon">💡</span><span class="section-title" style="font-size:1.1rem;font-weight:700;">Prioritized Action Plan</span></div>', unsafe_allow_html=True)
for sug in analysis.get("improvement_suggestions", []):
    cls = {"HIGH": "priority-high", "MEDIUM": "priority-medium", "LOW": "priority-low"}.get(
        sug.get("priority", ""), "")
    badge_color = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#22c55e"}.get(
        sug.get("priority", ""), "#6b7280")
    st.markdown(f"""
    <div class="suggestion-card {cls} fade-in">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
        <span style="background:{badge_color};color:white;border-radius:6px;padding:2px 8px;font-size:.7rem;font-weight:700;">{sug.get('priority','')}</span>
        <span class="suggestion-category">{sug.get('category','')}</span>
      </div>
      <div class="suggestion-text">→ {sug.get('suggestion','')}</div>
      <div class="suggestion-impact">💡 {sug.get('impact','')}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/8_Rewrite_Assistant.py", label="✍️ Rewrite my resume with AI →")
with c2:
    st.page_link("pages/9_Job_Resume.py", label="🚀 Generate optimized resume →")
