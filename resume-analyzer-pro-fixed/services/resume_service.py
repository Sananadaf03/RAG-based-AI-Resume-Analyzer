# ============================================================
# services/resume_service.py
# Persistence wrapper around modules/parser.py
# ============================================================
from db.database import get_session
from db.models import Resume, JobDescription
from modules.parser import parse_resume, parse_job_description


def save_resume(user_id: int, filename: str, file_bytes: bytes, file_ext: str) -> tuple[int, dict]:
    parsed = parse_resume(file_bytes, file_ext)
    with get_session() as s:
        r = Resume(
            user_id=user_id,
            filename=filename,
            file_ext=file_ext,
            file_bytes=file_bytes,
            full_text=parsed["full_text"],
            parsed_data={
                "sections": parsed["sections"],
                "chunks": parsed["chunks"],
                "word_count": parsed["word_count"],
                "char_count": parsed["char_count"],
                "section_names": parsed["section_names"],
            },
        )
        s.add(r); s.commit(); s.refresh(r)
        return r.id, parsed


def list_resumes(user_id: int) -> list[dict]:
    with get_session() as s:
        rs = s.query(Resume).filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
        return [{"id": r.id, "filename": r.filename, "created_at": r.created_at} for r in rs]


def load_resume(resume_id: int, user_id: int) -> dict | None:
    with get_session() as s:
        r = s.query(Resume).filter_by(id=resume_id, user_id=user_id).first()
        if not r:
            return None
        d = dict(r.parsed_data or {})
        d["full_text"] = r.full_text
        d["filename"] = r.filename
        return d


def save_jd(user_id: int, text: str, title: str = "") -> int:
    parsed = parse_job_description(text)
    with get_session() as s:
        jd = JobDescription(user_id=user_id, title=title or "Untitled JD", text=parsed["full_text"])
        s.add(jd); s.commit(); s.refresh(jd)
        return jd.id
