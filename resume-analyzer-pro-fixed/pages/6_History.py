# ============================================================
# pages/6_History.py  – Full Analysis History System
# ============================================================
import streamlit as st
import pandas as pd
from utils.theme import load_theme, render_3d_mini_banner
from services.auth_service import require_login, current_user_id, logout
from services.analysis_service import list_analyses, load_analysis
from utils.charts import score_gauge, score_breakdown_radar, keyword_gap_hbar

st.set_page_config(page_title="History · Resume Analyzer Pro", page_icon="📂", layout="wide")
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
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.page_link("pages/3_Dashboard.py",          label="📊 Dashboard",   width="stretch")
    st.page_link("pages/4_Analyze.py",            label="🔬 Analyze",     width="stretch")
    st.page_link("pages/7_ATS_Deep_Dive.py",      label="🎯 ATS Dive",    width="stretch")
    st.page_link("pages/8_Rewrite_Assistant.py",  label="✍️ Rewrite AI",  width="stretch")
    st.page_link("pages/9_Job_Resume.py",         label="🚀 Job Resume",  width="stretch")
    st.page_link("pages/10_Compare.py",           label="🔀 Compare",     width="stretch")
    st.markdown("---")
    if st.button("🚪 Log out", use_container_width=True):
        logout(); st.rerun()

render_3d_mini_banner()

st.markdown("""
<div style="text-align:center;padding:1rem 0 1.5rem;">
  <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:800;
              background:linear-gradient(135deg,#fff 0%,#c4b5fd 35%,#67e8f9 70%);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    ANALYSIS HISTORY
  </div>
  <p style="color:#5c5880;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;margin-top:.3rem;">
    Every analysis you've run · Sorted newest first
  </p>
</div>
""", unsafe_allow_html=True)

rows = list_analyses(uid, limit=200)

if not rows:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem;">
      <div class="float-anim" style="font-size:3rem;">📂</div>
      <h3>No analyses yet</h3>
      <p style="color:#94a3b8;">Run your first analysis on the Analyze page.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Analyze.py", label="→ Run your first analysis")
    st.stop()

df = pd.DataFrame(rows)
df["created_at"] = pd.to_datetime(df["created_at"])
df["date_display"] = df["created_at"].dt.strftime("%b %d, %Y · %H:%M")

# ── Search + Filter ─────────────────────────────────────────
col_s, col_f, col_sort = st.columns([2, 1.5, 1.5], gap="medium")
with col_s:
    search_q = st.text_input("search", placeholder="🔍 Search by Analysis ID…", label_visibility="collapsed")
with col_f:
    score_filter = st.selectbox("filter", ["All Scores", "Excellent (≥75)", "Good (55–74)", "Needs Work (<55)"], label_visibility="collapsed")
with col_sort:
    sort_order = st.selectbox("sort", ["Newest First", "Oldest First", "Score ↑", "Score ↓"], label_visibility="collapsed")

filtered = df.copy()
if search_q.strip():
    try:
        sid = int(search_q.strip())
        filtered = filtered[filtered["id"] == sid]
    except ValueError:
        pass

if score_filter == "Excellent (≥75)":
    filtered = filtered[filtered["ats_score"] >= 75]
elif score_filter == "Good (55–74)":
    filtered = filtered[(filtered["ats_score"] >= 55) & (filtered["ats_score"] < 75)]
elif score_filter == "Needs Work (<55)":
    filtered = filtered[filtered["ats_score"] < 55]

if sort_order == "Oldest First":
    filtered = filtered.sort_values("created_at", ascending=True)
elif sort_order == "Score ↑":
    filtered = filtered.sort_values("ats_score", ascending=True)
elif sort_order == "Score ↓":
    filtered = filtered.sort_values("ats_score", ascending=False)
else:
    filtered = filtered.sort_values("created_at", ascending=False)

st.markdown("<br>", unsafe_allow_html=True)

if filtered.empty:
    st.info("No analyses match your filters.")
    st.stop()

# Track which analysis is open inline
if "history_open_id" not in st.session_state:
    st.session_state["history_open_id"] = None

def _tags(items, cls):
    if not items:
        return '<p style="color:#475569;font-size:.85rem;">None.</p>'
    inner = "".join(f'<span class="tag {cls}">{x}</span>' for x in items)
    return f'<div class="tag-container">{inner}</div>'

for _, row in filtered.iterrows():
    aid = int(row["id"])
    score = row["ats_score"] or 0
    score_color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 55 else "#ef4444"
    score_label = "EXCELLENT" if score >= 75 else "GOOD" if score >= 55 else "NEEDS WORK"
    is_open = st.session_state["history_open_id"] == aid

    border_extra = f"box-shadow:0 0 18px rgba(139,92,246,.25);" if is_open else ""

    st.markdown(f"""
    <div class="glass-card fade-in" style="padding:1rem 1.5rem;margin-bottom:.4rem;
         border-left:3px solid {score_color};{border_extra}">
      <div style="display:flex;align-items:center;gap:1.2rem;">
        <div style="min-width:64px;text-align:center;">
          <div style="font-size:1.4rem;font-weight:800;color:{score_color};">{score:.0f}%</div>
          <div style="font-size:.58rem;color:{score_color};letter-spacing:.04em;">{score_label}</div>
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;color:#e2e8f0;font-size:.92rem;">Analysis #{aid}</div>
          <div style="font-size:.76rem;color:#5c5880;margin-top:.15rem;">📅 {row['date_display']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    btn_label = "🔼 Close" if is_open else "📂 Open Analysis"
    if st.button(btn_label, key=f"open_{aid}"):
        st.session_state["history_open_id"] = None if is_open else aid
        st.rerun()

    if is_open:
        a = load_analysis(aid, uid)
        if not a:
            st.warning("Could not load this analysis.")
        else:
            score_val = a.get("ats_score", 0)

            st.markdown("""
            <div style="background:rgba(124,58,237,.04);border:1px solid rgba(139,92,246,.2);
                        border-radius:16px;padding:1.5rem 1.5rem 1rem;margin-bottom:1rem;">
            """, unsafe_allow_html=True)

            # Score + Radar
            cg, cr = st.columns([1, 1.4], gap="large")
            with cg:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(score_gauge(score_val), use_container_width=True,
                                config={"displayModeBar": False})
                dims = [
                    ("Semantic",    a.get("semantic_similarity", 0)),
                    ("Skills",      a.get("skill_match_pct", 0)),
                    ("Keywords",    a.get("keyword_match_pct", 0)),
                    ("Experience",  a.get("experience_score", 0)),
                    ("Education",   a.get("education_score", 0)),
                    ("Format",      a.get("format_score", 0)),
                ]
                for lbl, val in dims:
                    col = "#22c55e" if val >= 70 else "#f59e0b" if val >= 45 else "#ef4444"
                    st.markdown(f"""
                    <div style="margin:.22rem 0;">
                      <div style="display:flex;justify-content:space-between;font-size:.74rem;color:#94a3b8;">
                        <span>{lbl}</span><span style="color:{col};">{val:.1f}%</span>
                      </div>
                      <div style="height:5px;background:rgba(255,255,255,.07);border-radius:99px;margin-top:2px;">
                        <div style="width:{val}%;height:100%;background:{col};border-radius:99px;"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with cr:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.plotly_chart(score_breakdown_radar(a), use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            htab1, htab2, htab3, htab4 = st.tabs(["🎯 Skills", "🔑 Keywords", "💡 Suggestions", "✍️ Rewrites"])

            with htab1:
                sc1, sc2, sc3 = st.columns(3)
                sc1.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">✅</span><span class="section-title">Matched</span></div>{_tags(a.get("matched_skills",[]),"tag-matched")}</div>', unsafe_allow_html=True)
                sc2.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">❌</span><span class="section-title">Missing</span></div>{_tags(a.get("missing_skills",[]),"tag-missing")}</div>', unsafe_allow_html=True)
                sc3.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">⭐</span><span class="section-title">Bonus</span></div>{_tags(a.get("extra_skills",[])[:20],"tag-extra")}</div>', unsafe_allow_html=True)

            with htab2:
                kc1, kc2 = st.columns([1.3, 1], gap="large")
                with kc1:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.plotly_chart(keyword_gap_hbar(a.get("matched_keywords", []), a.get("missing_keywords", [])),
                                    use_container_width=True, config={"displayModeBar": False})
                    st.markdown("</div>", unsafe_allow_html=True)
                with kc2:
                    st.markdown(f'<div class="glass-card"><div class="section-header"><span class="section-icon">🔑</span><span class="section-title">Missing Keywords</span></div>{_tags(sorted(a.get("missing_keywords",[]))[:20],"tag-missing")}</div>', unsafe_allow_html=True)

            with htab3:
                for sug in a.get("improvement_suggestions", []):
                    cls = {"HIGH": "priority-high", "MEDIUM": "priority-medium", "LOW": "priority-low"}.get(sug.get("priority"), "")
                    st.markdown(f"""
                    <div class="suggestion-card {cls}">
                      <div class="suggestion-category">{sug.get('category','')}</div>
                      <div class="suggestion-text">→ {sug.get('suggestion','')}</div>
                      <div class="suggestion-impact">💡 {sug.get('impact','')}</div>
                    </div>""", unsafe_allow_html=True)

            with htab4:
                for i, rw in enumerate(a.get("rewrite_bullets", []), 1):
                    st.markdown(f"""
                    <div class="rewrite-card fade-in stagger-{min(i,5)}">
                      <div class="rewrite-before"><div class="rewrite-label before">❌ Before</div><div class="rewrite-text">{rw.get('before','')}</div></div>
                      <div class="rewrite-after"><div class="rewrite-label after">✅ After</div><div class="rewrite-text">{rw.get('after','')}</div></div>
                      <div class="rewrite-tip">💡 {rw.get('tip','')}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Use this analysis → Job Resume", key=f"use_{aid}"):
                st.session_state["analysis"] = a
                st.session_state["analysis_id"] = aid
                st.switch_page("pages/9_Job_Resume.py")

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:.15rem;'></div>", unsafe_allow_html=True)

# ── Summary row ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📊 Summary")
sc1, sc2, sc3, sc4 = st.columns(4)
sc1.metric("Total Analyses", len(filtered))
sc2.metric("Best Score",  f"{filtered['ats_score'].max():.1f}%")
sc3.metric("Avg Score",   f"{filtered['ats_score'].mean():.1f}%")
sc4.metric("Latest Score", f"{filtered.iloc[0]['ats_score']:.1f}%")
