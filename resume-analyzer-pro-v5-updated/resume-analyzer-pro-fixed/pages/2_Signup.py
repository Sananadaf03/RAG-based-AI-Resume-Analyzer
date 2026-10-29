import streamlit as st
from utils.theme import load_theme
from services.auth_service import signup, is_logged_in

st.set_page_config(page_title="Sign up · Resume Analyzer Pro", page_icon="✨", layout="centered")
load_theme()

if is_logged_in():
    st.info("You're already logged in.")
    st.page_link("pages/3_Dashboard.py", label="→ Dashboard")
    st.stop()

st.markdown("""
<div class="glass-card glass-card-accent fade-in" style="max-width:420px;margin:3rem auto;">
  <h2 style="margin-top:0;">✨ Create your account</h2>
  <p style="color:#94a3b8;font-size:.9rem;">Free, local, private. Your data stays on your machine.</p>
</div>
""", unsafe_allow_html=True)

with st.form("signup_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    pw2 = st.text_input("Confirm password", type="password")
    submit = st.form_submit_button("Create account", width="stretch")

if submit:
    if pw != pw2:
        st.error("Passwords don't match.")
    else:
        ok, msg = signup(username, email, pw)
        (st.success if ok else st.error)(msg)
        if ok:
            st.page_link("pages/1_Login.py", label="→ Go log in")

st.markdown("---")
st.page_link("pages/1_Login.py", label="Already have an account? Log in →")
