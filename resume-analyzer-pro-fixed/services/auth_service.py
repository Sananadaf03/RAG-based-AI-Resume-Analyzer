# ============================================================
# services/auth_service.py
# Signup / login / session — bcrypt password hashing
# ============================================================
import re
import bcrypt
import streamlit as st
from db.database import get_session
from db.models import User


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def signup(username: str, email: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    with get_session() as s:
        if s.query(User).filter((User.username == username) | (User.email == email)).first():
            return False, "Username or email already exists."
        user = User(username=username, email=email, password_hash=_hash(password))
        s.add(user)
        s.commit()
        s.refresh(user)
        return True, f"Account created. Welcome, {user.username}!"


def login(username_or_email: str, password: str) -> tuple[bool, str]:
    key = username_or_email.strip()
    with get_session() as s:
        user = s.query(User).filter(
            (User.username == key) | (User.email == key.lower())
        ).first()
        if not user or not _verify(password, user.password_hash):
            return False, "Invalid credentials."
        st.session_state["user_id"] = user.id
        st.session_state["username"] = user.username
        st.session_state["email"] = user.email
        return True, f"Welcome back, {user.username}!"


def logout():
    for k in ("user_id", "username", "email", "analysis", "resume_filename",
              "current_chat_id", "current_resume_id"):
        st.session_state.pop(k, None)


def is_logged_in() -> bool:
    return bool(st.session_state.get("user_id"))


def current_user_id() -> int | None:
    return st.session_state.get("user_id")


def require_login():
    """Call at top of every protected page."""
    if not is_logged_in():
        st.warning("🔒 Please log in to continue.")
        st.page_link("pages/1_Login.py", label="Go to Login", icon="🔑")
        st.stop()
