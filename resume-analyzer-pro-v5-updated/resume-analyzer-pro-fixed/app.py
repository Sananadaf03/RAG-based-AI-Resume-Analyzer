# ============================================================
# app.py — Landing / Auth gateway (3D UI Edition)
# ============================================================
import streamlit as st

st.set_page_config(
    page_title="🚀 AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

from db.database import init_db
init_db()

from utils.theme import load_theme, render_3d_hero, render_3d_mini_banner
from services.auth_service import is_logged_in, logout

load_theme()


def render_landing():
    render_3d_hero()

    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;">
      <div class="hero-badge neon-flicker">⚡ Fully Offline · RAG-Powered · 100% Private</div>
    </div>
    """, unsafe_allow_html=True)

    # 4 feature cards with 3D hover effect
    c1, c2, c3, c4 = st.columns(4, gap="large")
    cards = [
        ("🎯", "ATS Score Engine",
         "Six-dimension scoring: semantic similarity, skill match, keyword coverage, experience, education, format.",
         "rgba(139,92,246,0.12)", "rgba(139,92,246,0.4)"),
        ("🧠", "RAG-Powered Chat",
         "Ask about your resume, any FAANG company, career roadmaps, or interview prep — fully offline.",
         "rgba(34,211,238,0.1)", "rgba(34,211,238,0.35)"),
        ("✍️", "AI Rewrite Coach",
         "Bullet-by-bullet rewriting: strong action verbs, quantified metrics, ATS keyword injection.",
         "rgba(232,121,249,0.1)", "rgba(232,121,249,0.35)"),
        ("🚀", "Resume Generator",
         "Generate a fully optimized resume tailored to the JD and download it as PDF or DOCX instantly.",
         "rgba(251,191,36,0.1)", "rgba(251,191,36,0.35)"),
    ]
    for col, (icon, title, body, bg, bdr) in zip((c1, c2, c3, c4), cards):
        col.markdown(f"""
        <div class="glass-card fade-in" style="
          text-align:center; padding:2rem 1.25rem; cursor:default;
          background:{bg}; border-color:{bdr};
          min-height:200px;
        ">
          <div style="font-size:2.6rem;margin-bottom:.75rem;" class="float-anim">{icon}</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:.82rem;font-weight:700;
                      letter-spacing:.05em;text-transform:uppercase;color:#e2e0f0;
                      margin-bottom:.6rem;">{title}</div>
          <p style="color:#7b7fa0;font-size:.82rem;line-height:1.65;">{body}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div class="gradient-divider"></div>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:2.5rem;
                padding:1.5rem 2rem;
                background:rgba(10,8,30,0.5);
                border:1px solid rgba(139,92,246,0.12);
                border-radius:18px; margin-bottom:2rem;">
      <div style="text-align:center;">
        <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;
                    background:linear-gradient(135deg,#a78bfa,#67e8f9);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">10+</div>
        <div style="font-size:.65rem;color:#5c5880;text-transform:uppercase;letter-spacing:.1em;">Pages</div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;
                    background:linear-gradient(135deg,#67e8f9,#e879f9);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">6D</div>
        <div style="font-size:.65rem;color:#5c5880;text-transform:uppercase;letter-spacing:.1em;">ATS Scoring</div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;
                    background:linear-gradient(135deg,#e879f9,#fbbf24);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">100%</div>
        <div style="font-size:.65rem;color:#5c5880;text-transform:uppercase;letter-spacing:.1em;">Offline</div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;
                    background:linear-gradient(135deg,#fbbf24,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">0</div>
        <div style="font-size:.65rem;color:#5c5880;text-transform:uppercase;letter-spacing:.1em;">API Fees</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature badges grid
    features = [
        ("📊", "ATS Deep Dive", "#c4b5fd"),
        ("✍️", "Rewrite AI", "#67e8f9"),
        ("🔀", "Before/After", "#86efac"),
        ("📥", "PDF/DOCX Export", "#fbbf24"),
        ("📈", "Score History", "#67e8f9"),
    ]
    grid_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:2rem;max-width:700px;margin-left:auto;margin-right:auto;">'
    for icon, label, color in features:
        grid_html += f"""
        <div style="padding:.85rem;
                    background:rgba(10,8,30,0.55);
                    border:1px solid rgba(139,92,246,0.12);
                    border-radius:12px;text-align:center;
                    transition:all .2s ease;cursor:default;"
             onmouseover="this.style.borderColor='rgba(139,92,246,.4)';this.style.transform='translateY(-2px)'"
             onmouseout="this.style.borderColor='rgba(139,92,246,.12)';this.style.transform='none'">
          <div style="font-size:1.3rem;margin-bottom:.3rem;">{icon}</div>
          <div style="font-size:.72rem;font-weight:700;font-family:'Orbitron',sans-serif;
                      color:{color};letter-spacing:.04em;">{label}</div>
        </div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    a, b = st.columns(2, gap="large")
    with a:
        st.page_link("pages/1_Login.py", label="🔑  Log in to your account")
    with b:
        st.page_link("pages/2_Signup.py", label="✨  Create free account")


def render_dashboard_redirect():
    render_3d_mini_banner()

    username = st.session_state.get('username', '')
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:800;
                  background:linear-gradient(135deg,#fff 0%,#c4b5fd 35%,#67e8f9 70%,#e879f9 100%);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        WELCOME BACK, {username.upper()}
      </div>
      <p style="color:#5c5880;font-size:.85rem;margin-top:.3rem;letter-spacing:.06em;text-transform:uppercase;">
        Your career intelligence platform is ready
      </p>
    </div>
    """, unsafe_allow_html=True)

    row1 = st.columns(4, gap="medium")
    row2 = st.columns(4, gap="medium")

    nav = [
        ("📊", "Dashboard",      "pages/3_Dashboard.py",         "#8b5cf6"),
        ("🔬", "Analyze",        "pages/4_Analyze.py",           "#22d3ee"),
        ("🎯", "ATS Deep Dive",  "pages/7_ATS_Deep_Dive.py",     "#e879f9"),
        ("✍️", "Rewrite AI",     "pages/8_Rewrite_Assistant.py", "#fbbf24"),
        ("🚀", "Job Resume",     "pages/9_Job_Resume.py",        "#10b981"),
        ("🔀", "Compare",        "pages/10_Compare.py",          "#f43f5e"),
        ("📂", "History",        "pages/6_History.py",           "#67e8f9"),
    ]
    for col, (icon, label, page, color) in zip(list(row1) + list(row2), nav):
        col.markdown(f"""
        <div class="glass-card fade-in" style="text-align:center;padding:1.25rem .75rem;cursor:pointer;
             border-color:rgba(139,92,246,0.15);">
          <div style="font-size:1.8rem;margin-bottom:.5rem;" class="float-anim">{icon}</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:.68rem;font-weight:700;
                      letter-spacing:.06em;text-transform:uppercase;color:{color};">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        col.page_link(page, label=f"→ {label}")

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:1rem .5rem 1.5rem;">
          <div style="width:48px;height:48px;border-radius:50%;
                      background:linear-gradient(135deg,#6d28d9,#4f46e5);
                      display:flex;align-items:center;justify-content:center;
                      font-size:1.2rem;margin:0 auto .75rem;
                      box-shadow:0 0 20px rgba(139,92,246,.5);">👤</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:.8rem;font-weight:700;color:#c4b5fd;">
            {username.upper()}
          </div>
          <div style="font-size:.72rem;color:#5c5880;">{st.session_state.get('email','')}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        for icon, label, page, _ in nav:
            st.page_link(page, label=f"{icon} {label}", width="stretch")
        st.markdown("---")
        if st.button("🚪 Log out", use_container_width=True):
            logout(); st.rerun()


if is_logged_in():
    render_dashboard_redirect()
else:
    render_landing()
