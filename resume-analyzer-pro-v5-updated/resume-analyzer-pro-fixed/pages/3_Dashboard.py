import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import list_analyses, load_analysis
from services.resume_service import list_resumes
from utils.charts import score_gauge, score_breakdown_radar

st.set_page_config(page_title="Dashboard · Resume Analyzer Pro", page_icon="📊", layout="wide")
load_theme()
require_login()

uid = current_user_id()

with st.sidebar:
    uname = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:.75rem 0 1rem;">
      <div style="width:44px;height:44px;border-radius:50%;
                  background:linear-gradient(135deg,#6d28d9,#4f46e5);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1.1rem;margin:0 auto .6rem;
                  box-shadow:0 0 18px rgba(139,92,246,.5);">👤</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:.78rem;font-weight:700;color:#c4b5fd;">{uname.upper()}</div>
      <div style="font-size:.7rem;color:#5c5880;">{st.session_state.get('email','')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/4_Analyze.py",           label="🔬 New Analysis",    width="stretch")
    st.page_link("pages/7_ATS_Deep_Dive.py",     label="🎯 ATS Deep Dive",   width="stretch")
    st.page_link("pages/8_Rewrite_Assistant.py", label="✍️ Rewrite AI",      width="stretch")
    st.page_link("pages/9_Job_Resume.py",        label="🚀 Job Resume",      width="stretch")
    st.page_link("pages/6_History.py",           label="📂 History",         width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()

st.markdown(f"""
<div style="text-align:center;padding:1rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:800;
              background:linear-gradient(135deg,#fff 0%,#c4b5fd 35%,#67e8f9 70%);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    MISSION CONTROL
  </div>
  <p style="color:#5c5880;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    {st.session_state.get('username','')} · Career Intelligence Dashboard
  </p>
</div>
""", unsafe_allow_html=True)

analyses = list_analyses(uid)
resumes  = list_resumes(uid)

# ── KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Resumes Uploaded", len(resumes))
c2.metric("Analyses Run", len(analyses))
c3.metric("Best ATS Score", f"{max((a['ats_score'] or 0) for a in analyses):.1f}%" if analyses else "—")
c4.metric("Avg ATS Score",
          f"{(sum((a['ats_score'] or 0) for a in analyses)/len(analyses)):.1f}%" if analyses else "—")

if not analyses:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem;">
      <div class="float-anim" style="font-size:3rem;">🚀</div>
      <h3>No analyses yet</h3>
      <p style="color:#94a3b8;">Upload a resume + JD on the Analyze page to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Analyze.py", label="→ Run your first analysis")
    st.stop()

# ── Latest analysis snapshot
latest = load_analysis(analyses[0]["id"], uid)
if latest:
    col_g, col_r = st.columns([1, 1.4], gap="large")
    with col_g:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(score_gauge(latest["ats_score"]), width="stretch",
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(score_breakdown_radar(latest), width="stretch",
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ── Score over time
st.markdown("### 📈 Score Trend")
df = pd.DataFrame(analyses).sort_values("created_at")
fig = px.line(df, x="created_at", y="ats_score", markers=True,
              labels={"created_at": "Date", "ats_score": "ATS Score"})
fig.update_traces(
    line=dict(color="#8b5cf6", width=3),
    marker=dict(color="#22d3ee", size=8, line=dict(color="#8b5cf6", width=2)),
    mode="lines+markers",          # NO text mode — removes numeric labels
    text=None,
    textposition=None,
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a8a4c8", family="'Orbitron', sans-serif", size=11),
    height=320, margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(gridcolor="rgba(139,92,246,0.1)", zeroline=False,
               showline=False, tickfont=dict(size=10, color="#6b7280")),
    yaxis=dict(gridcolor="rgba(139,92,246,0.1)", zeroline=False,
               showline=False, tickfont=dict(size=10, color="#6b7280"),
               range=[0, 105]),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1e1e2e", bordercolor="#8b5cf6",
                    font=dict(color="white", size=12)),
)
# Gradient fill under the line
fig.add_traces(go.Scatter(
    x=df["created_at"], y=df["ats_score"],
    fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
    line=dict(width=0), showlegend=False, hoverinfo="skip",
))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
