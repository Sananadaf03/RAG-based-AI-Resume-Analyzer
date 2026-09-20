import streamlit as st
from utils.theme import load_theme
from services.auth_service import login, is_logged_in

st.set_page_config(page_title="Login · Resume Analyzer Pro", page_icon="🔑", layout="centered")
load_theme()

if is_logged_in():
    st.success(f"Already logged in as **{st.session_state['username']}**.")
    st.page_link("pages/3_Dashboard.py", label="→ Go to Dashboard")
    st.stop()

st.markdown("""
<div class="glass-card glass-card-accent fade-in" style="max-width:420px;margin:3rem auto;">
  <h2 style="margin-top:0;">🔑 Log in</h2>
  <p style="color:#94a3b8;font-size:.9rem;">Welcome back. Pick up where you left off.</p>
</div>
""", unsafe_allow_html=True)

with st.form("login_form", clear_on_submit=False):
    user = st.text_input("Username or email")
    pw = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log in", width="stretch")

if submit:
    ok, msg = login(user, pw)
    if ok:
        st.success(msg); st.rerun()
    else:
        st.error(msg)

st.markdown("---")
st.page_link("pages/2_Signup.py", label="No account? Sign up →")
