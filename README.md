# 🚀 AI Resume Analyzer Pro

An AI-powered ATS Resume Analyzer and Optimization Platform built with **Python and Streamlit**. The application analyzes resumes against job descriptions, identifies skill and keyword gaps, provides ATS-focused insights, rewrites resume content, and generates optimized resumes in PDF and DOCX formats.

Designed as a career intelligence platform, it combines resume analysis, semantic similarity, skill matching, resume optimization, authentication, analysis history, and career assistance in one application.

## ✨ Key Features

### 🎯 ATS Resume Analysis

* Upload resumes in PDF and DOCX formats.
* Compare resumes against job descriptions.
* Evaluate resumes across six scoring dimensions.
* Analyze semantic similarity and keyword coverage.
* Identify matching and missing skills.
* Evaluate experience, education, and resume formatting.

### 📊 ATS Deep Dive

* Detailed ATS score breakdown.
* Skill-gap identification and analysis.
* Keyword coverage insights.
* Resume-to-job matching results.
* Visual dashboards and charts.

### ✍️ AI Resume Rewriter

* Rewrite resume bullet points.
* Improve action verbs and sentence clarity.
* Incorporate relevant job-description keywords.
* Improve the presentation of achievements and responsibilities.
* Optimize resume content for ATS compatibility.

### 🚀 Job-Specific Resume Generator

* Tailor resume content to specific job descriptions.
* Generate job-focused resume content.
* Export optimized resumes in PDF and DOCX formats.

### 🔀 Resume Comparison

* Compare original and optimized resume content.
* Review changes introduced during optimization.
* Identify improvements in wording and keyword alignment.

### 💬 Career & Company Assistant

* Career-related question answering.
* Interview preparation assistance.
* Company-related information.
* Resume and job-search guidance.
* Retrieval-based knowledge support.

### 🔐 User Authentication

* User registration and login.
* Password hashing using bcrypt.
* JWT-based authentication.
* User-specific analysis history.

### 📂 Analysis History

* Store previous resume analyses.
* Track ATS scores and analysis results.
* Review previous assessments.
* Monitor resume optimization progress.

### 💾 Database Support

* SQLite database support by default.
* PostgreSQL support through `DATABASE_URL`.
* SQLAlchemy-based database architecture.

### 🎨 Modern 3D User Interface

* Interactive Streamlit interface.
* Custom HTML and CSS styling.
* Three.js-based visual effects.
* Dark futuristic dashboard.
* Animated cards and visual components.

## 🛠️ Tech Stack

| Category                    | Technologies              |
| --------------------------- | ------------------------- |
| Programming Language        | Python                    |
| Frontend / UI               | Streamlit, HTML, CSS      |
| Machine Learning            | Scikit-learn              |
| Natural Language Processing | spaCy, NLTK               |
| Text Embeddings             | Sentence Transformers     |
| Vector Search               | FAISS                     |
| Data Processing             | Pandas, NumPy             |
| Visualization               | Plotly, Matplotlib        |
| PDF Processing              | PyMuPDF, ReportLab, FPDF2 |
| DOCX Processing             | python-docx               |
| Authentication              | JWT, bcrypt               |
| Database                    | SQLite, PostgreSQL        |
| ORM                         | SQLAlchemy                |
| Environment Configuration   | python-dotenv             |
| 3D UI Effects               | Three.js                  |
| Version Control             | Git, GitHub               |

## 🧠 ATS Scoring System

The application evaluates resumes across six dimensions:

1. **Semantic Similarity** — measures the contextual similarity between resume content and the job description.
2. **Skill Match** — identifies relevant skills present in both the resume and job requirements.
3. **Keyword Coverage** — evaluates the presence of important job-related keywords.
4. **Experience Match** — assesses the relevance of the candidate's experience.
5. **Education Match** — evaluates alignment with educational requirements.
6. **Resume Format** — examines resume structure and formatting.

### Skill Synonym Handling

The analyzer can recognize variations of common technical terms, such as:

* `k8s` → Kubernetes
* `sklearn` → scikit-learn
* `nodejs` → Node.js

Additional analysis techniques include partial skill matching, keyword analysis, semantic similarity, and calibrated scoring.

*ATS scores are application-generated estimates and should not be interpreted as scores from an actual employer's ATS.*

## 📁 Project Structure

```text
ai-resume-analyzer-pro/
│
├── app.py
├── requirements.txt
├── README.md
├── UPGRADE_NOTES.md
├── run.bat
├── run.sh
├── .env.example
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   └── styles.css
│
├── db/
│   ├── database.py
│   ├── models.py
│   └── __init__.py
│
├── modules/
│   ├── analyzer.py
│   ├── company_kb.py
│   ├── embeddings.py
│   ├── job_categories.py
│   ├── optimizer.py
│   ├── parser.py
│   ├── retriever.py
│   ├── rewriter.py
│   └── __init__.py
│
├── services/
│   ├── analysis_service.py
│   ├── auth_service.py
│   ├── export_service.py
│   ├── resume_service.py
│   ├── rewrite_service.py
│   └── __init__.py
│
├── utils/
│   ├── charts.py
│   ├── report_generator.py
│   ├── theme.py
│   └── __init__.py
│
└── pages/
    ├── 1_Login.py
    ├── 2_Signup.py
    ├── 3_Dashboard.py
    ├── 4_Analyze.py
    ├── 6_History.py
    ├── 7_ATS_Deep_Dive.py
    ├── 8_Rewrite_Assistant.py
    ├── 9_Job_Resume.py
    └── 10_Compare.py
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sananadaf03/RAG-based-AI-Resume-Analyzer.git
cd RAG-based-AI-Resume-Analyzer
```

> Ensure that the repository folder and commands match your actual GitHub project structure.

### 2. Create a Virtual Environment

**Windows — PowerShell**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Some machine-learning dependencies, including Sentence Transformers, FAISS, and spaCy, may require additional installation time.

### 4. Configure Environment Variables

Create a `.env` file using `.env.example` as a reference.

Add only the configuration values required by your application. Do not commit real API keys, passwords, or database credentials to GitHub.

SQLite is configured as the default database according to the project setup. PostgreSQL can be configured using `DATABASE_URL` if supported by your environment.

### 5. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## 🔄 Application Workflow

```text
User Signup / Login
        ↓
Upload Resume
        ↓
Enter Job Description
        ↓
Resume Parsing
        ↓
ATS Analysis
        ↓
┌───────────────────────────┐
│ Semantic Similarity       │
│ Skill Matching            │
│ Keyword Analysis          │
│ Experience Analysis       │
│ Education Analysis        │
│ Format Analysis           │
└───────────────────────────┘
        ↓
ATS Score and Skill Gaps
        ↓
Resume Optimization
        ↓
Resume Rewriting
        ↓
Job-Specific Resume
        ↓
PDF / DOCX Export
```

## 📊 Main Application Pages

| Page              | Purpose                                 |
| ----------------- | --------------------------------------- |
| Login             | Secure user authentication              |
| Signup            | Create a user account                   |
| Dashboard         | View resume analysis overview           |
| Analyze           | Compare a resume with a job description |
| History           | Review previous analyses                |
| ATS Deep Dive     | Explore detailed ATS and skill insights |
| Rewrite Assistant | Improve resume bullet points            |
| Job Resume        | Generate job-specific resume content    |
| Compare           | Compare original and optimized content  |

## 🔒 Privacy and Security

* Core resume analysis is designed to run locally without requiring paid external AI APIs.
* User authentication and analysis data can be stored using the configured database.
* Passwords should be stored using secure hashing rather than plain text.
* Never commit private resumes, personal user data, credentials, or secret keys to a public repository.
* Review any external AI integrations before sending resume content to third-party services.

## 🚀 Future Improvements

* Cloud deployment.
* Additional resume templates.
* Expanded job-category intelligence.
* Advanced semantic search.
* LinkedIn profile analysis.
* Automated job-description extraction.
* Resume version management.
* Expanded company knowledge bases.
* Improved mobile responsiveness.

## 🎓 Project Highlights

This project demonstrates practical implementation of:

* Python application development.
* Machine learning and natural language processing.
* Semantic similarity and text embeddings.
* Vector search using FAISS.
* Retrieval-based question answering concepts.
* Resume parsing and ATS optimization.
* Data visualization.
* Streamlit application development.
* Authentication and authorization.
* Database management.
* PDF and DOCX generation.
* Modular software architecture.
* Git and GitHub workflows.

## 👩‍💻 Author

**Sana Nadaf**

B.E. Computer Science & Engineering

GitHub: [Sananadaf03](https://github.com/Sananadaf03)

## ⭐ Support

If you find this project useful, consider giving the repository a star on GitHub.

---

*Built to help job seekers understand resume-job alignment and improve their resumes through structured analysis and optimization.*
