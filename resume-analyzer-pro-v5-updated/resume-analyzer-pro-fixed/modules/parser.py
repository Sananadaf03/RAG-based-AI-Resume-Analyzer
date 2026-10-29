# ============================================================
# modules/parser.py
# Document Parser: PDF & DOCX Resume Extraction
# ============================================================

import re
import fitz  # PyMuPDF
from docx import Document
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Section Headers commonly found in resumes
# ─────────────────────────────────────────────
SECTION_HEADERS = [
    "summary", "objective", "profile", "about",
    "experience", "work experience", "employment", "professional experience",
    "education", "academic", "qualification",
    "skills", "technical skills", "core competencies", "expertise",
    "projects", "personal projects", "key projects",
    "certifications", "certificates", "licenses",
    "achievements", "awards", "honors",
    "publications", "research",
    "languages", "interests", "hobbies", "volunteer",
    "references", "contact", "links",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract clean text from PDF bytes using PyMuPDF.
    Handles multi-column layouts and preserves reading order.
    """
    text_blocks = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num, page in enumerate(doc):
            # Extract with reading order preserved
            blocks = page.get_text("blocks", sort=True)
            for block in blocks:
                if block[6] == 0:  # Text block (not image)
                    text_blocks.append(block[4].strip())
        doc.close()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise ValueError(f"Could not parse PDF: {e}")

    raw_text = "\n".join(text_blocks)
    return clean_text(raw_text)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX bytes using python-docx.
    Preserves paragraph structure and table content.
    """
    import io
    text_parts = []
    try:
        doc = Document(io.BytesIO(file_bytes))

        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                )
                if row_text:
                    text_parts.append(row_text)

    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise ValueError(f"Could not parse DOCX: {e}")

    raw_text = "\n".join(text_parts)
    return clean_text(raw_text)


def clean_text(text: str) -> str:
    """
    Normalize and clean extracted resume text.
    - Remove excessive whitespace
    - Normalize unicode characters
    - Remove non-printable characters
    """
    # Normalize unicode
    text = text.encode("ascii", "ignore").decode("ascii")

    # Remove non-printable chars (keep newlines, tabs)
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse more than 2 consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing spaces per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


def segment_resume_sections(text: str) -> dict:
    """
    Segment resume text into logical sections (Experience, Skills, Education, etc.)
    Returns a dict of {section_name: section_text}.
    """
    sections = {}
    current_section = "header"
    current_content = []

    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content.append("")
            continue

        # Detect if this line is a section header
        lower = stripped.lower().rstrip(":").strip()
        is_header = (
            lower in SECTION_HEADERS
            and len(stripped) < 60  # Headers are short
            and not stripped.endswith(".")  # Not a sentence
        )

        if is_header:
            # Save previous section
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = lower
            current_content = []
        else:
            current_content.append(stripped)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for embedding.
    Uses word-boundary splitting to avoid cutting mid-word.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap  # Overlap for context continuity

    return [c for c in chunks if c.strip()]


def parse_resume(file_bytes: bytes, file_extension: str) -> dict:
    """
    Main entry point: parse resume file and return structured data.

    Returns:
        {
            "full_text": str,
            "sections": dict,
            "chunks": list[str],
            "word_count": int,
            "char_count": int,
        }
    """
    ext = file_extension.lower().lstrip(".")

    if ext == "pdf":
        full_text = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        full_text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF or DOCX.")

    if len(full_text.strip()) < 50:
        raise ValueError("Extracted text is too short. The file may be empty or image-only.")

    sections = segment_resume_sections(full_text)
    chunks = chunk_text(full_text, chunk_size=250, overlap=40)

    return {
        "full_text": full_text,
        "sections": sections,
        "chunks": chunks,
        "word_count": len(full_text.split()),
        "char_count": len(full_text),
        "section_names": list(sections.keys()),
    }


def parse_job_description(jd_text: str) -> dict:
    """
    Parse and clean a raw job description string.
    Chunks it for retrieval comparison.
    """
    cleaned = clean_text(jd_text)
    chunks = chunk_text(cleaned, chunk_size=200, overlap=30)

    return {
        "full_text": cleaned,
        "chunks": chunks,
        "word_count": len(cleaned.split()),
    }
