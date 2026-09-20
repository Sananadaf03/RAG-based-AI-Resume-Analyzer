# AI Resume Analyzer Pro — 3D UI Edition

An AI-powered ATS Resume Optimization platform with Three.js 3D animations, deep skill analysis, AI rewriting, PDF/DOCX export, and a full career chatbot — **100% offline, no paid APIs**.

---

## Quick Start (VS Code / Local)

### 1. Requirements
- Python 3.10 or 3.11
- pip

### 2. Install dependencies
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

> Some heavy packages (`sentence-transformers`, `faiss-cpu`, `spacy`) may take a few minutes. The app gracefully degrades if they fail — core features still work.

### 3. Run the app
```bash
streamlit run app.py
```

The app will open at:
- **Local URL:**   http://localhost:8501
- **Network URL:** http://YOUR_IP:8501

### 4. (Optional) Set up PostgreSQL
By default the app uses **SQLite** (no setup needed).
To use PostgreSQL, set this environment variable before running:

```bash
# Windows (PowerShell)
$env:DATABASE_URL = "postgresql://user:password@localhost:5432/resume_analyzer"

# macOS / Linux
export DATABASE_URL="postgresql://user:password@localhost:5432/resume_analyzer"
```

---

## One-Click Run Scripts

**Windows** — double-click `run.bat`  
**macOS / Linux** — run `bash run.sh`

---

## Features (10 Pages)

| Page | Feature |
|------|---------|
| 🔑 Login / ✨ Signup | JWT auth, bcrypt passwords |
| 📊 Dashboard | Score history, KPI cards, trend charts |
| 🔬 Analyze | Upload resume + paste JD → 6-dimension ATS score |
| 🎯 ATS Deep Dive | Animated gauges, skill gap map, keyword analysis |
| ✍️ Rewrite Assistant | AI bullet rewriter — action verbs + metric injection |
| 🚀 Job Resume | ATS-optimized resume generator — PDF & DOCX download |
| 🔀 Compare | Before/after section diff of all improvements |
| 💬 AI Chat | Company KB (10+ companies), interview prep, career Q&A |
| 📂 History | All past analyses with score trends |

---

## Project Structure

```
resume-analyzer-pro/
├── app.py                        ← Main entry + 3D landing page
├── requirements.txt              ← Python dependencies
├── run.bat                       ← Windows one-click launcher
├── run.sh                        ← macOS/Linux launcher
├── .streamlit/
│   └── config.toml               ← Port 8501, dark theme
├── pages/
│   ├── 1_Login.py
│   ├── 2_Signup.py
│   ├── 3_Dashboard.py
│   ├── 4_Analyze.py
│   ├── 5_Chat.py
│   ├── 6_History.py
│   ├── 7_ATS_Deep_Dive.py
│   ├── 8_Rewrite_Assistant.py
│   ├── 9_Job_Resume.py
│   └── 10_Compare.py
├── modules/
│   ├── analyzer.py               ← ATS scoring engine
│   ├── parser.py                 ← PDF/DOCX parser
│   ├── rewriter.py               ← NLP bullet rewriter
│   ├── optimizer.py              ← Resume optimization
│   └── company_kb.py             ← Company knowledge base
├── services/
│   ├── analysis_service.py
│   ├── auth_service.py
│   ├── chat_service.py
│   ├── export_service.py         ← PDF + DOCX export
│   └── rewrite_service.py
├── utils/
│   ├── theme.py                  ← CSS + Three.js 3D scene injector
│   └── charts.py
├── assets/
│   └── styles.css                ← Deep Space Neon theme (3D CSS)
└── db/
    └── database.py               ← SQLAlchemy dual-backend (PG / SQLite)
```

---

## 3D UI Stack

- **Three.js r128** (via CDN) — particle sphere, wireframe shapes, orbital rings
- **CSS 3D transforms** — `perspective`, `rotateX/Y`, `translateZ` on all cards and buttons
- **Font: Orbitron** — futuristic headings; **Inter** — body; **JetBrains Mono** — code
- **Color palette:** Deep Space `#02010a` · Violet `#8b5cf6` · Cyan `#22d3ee` · Magenta `#e879f9` · Emerald `#34d399`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port already in use | Change port in `.streamlit/config.toml` |
| `psycopg2` error | Run `pip install psycopg2-binary` or remove `DATABASE_URL` to use SQLite |
| `spacy` model missing | Run `python -m spacy download en_core_web_sm` |
| Blank page / white flash | Hard-refresh browser (Ctrl+Shift+R) |
| `sentence-transformers` fails | Safe to ignore — app works without it |
