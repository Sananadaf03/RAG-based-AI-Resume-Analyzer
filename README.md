# 🚀 AI Resume Analyzer Pro

An AI-powered **ATS Resume Analyzer and Optimization Platform** built with **Python and Streamlit**. The application analyzes resumes against job descriptions, identifies skill and keyword gaps, provides ATS-focused insights, rewrites resume content, and generates optimized resumes in **PDF and DOCX** formats.

The project is designed as a complete career intelligence platform with authentication, analysis history, ATS deep-dive analytics, resume optimization, and career assistance.

---

## ✨ Key Features

### 🎯 ATS Resume Analysis

* Upload PDF/DOCX resumes
* Compare resumes with job descriptions
* Six-dimensional ATS scoring
* Semantic similarity analysis
* Keyword matching
* Skill matching
* Experience analysis
* Education matching
* Resume format analysis

### 📊 ATS Deep Dive

* Detailed ATS score breakdown
* Skill-gap identification
* Keyword coverage analysis
* Resume-job matching insights
* Visual score dashboards and charts

### ✍️ AI Resume Rewriter

* Rewrite resume bullet points
* Improve action verbs
* Add relevant job keywords
* Improve clarity and impact
* Optimize content for ATS systems

### 🚀 Job-Specific Resume Generator

* Tailor resumes according to job descriptions
* Generate optimized resume content
* Export optimized resumes
* Supports PDF and DOCX formats

### 🔀 Resume Comparison

* Compare original and optimized content
* Identify improvements
* Review changes made during optimization

### 💬 Career & Company Assistant

* Career-related Q&A
* Interview preparation
* Company-related information
* Resume and job-search assistance
* Retrieval-based knowledge system

### 🔐 User Authentication

* User signup and login
* Password hashing with bcrypt
* JWT-based authentication
* User-specific analysis history

### 📂 Analysis History

* Store previous resume analyses
* Track ATS scores
* Review previous results
* Monitor resume optimization progress

### 💾 Database Support

* SQLite by default
* PostgreSQL support through `DATABASE_URL`
* SQLAlchemy-based database architecture

### 🎨 Modern 3D UI

* Interactive Streamlit interface
* Three.js-based visual effects
* Responsive dashboard
* Dark futuristic UI
* Animated cards and visual components

---

## 🛠️ Tech Stack

| Category               | Technologies              |
| ---------------------- | ------------------------- |
| Programming Language   | Python                    |
| Frontend/UI            | Streamlit, HTML, CSS      |
| Machine Learning       | Scikit-learn              |
| NLP                    | spaCy, NLTK               |
| Embeddings             | Sentence Transformers     |
| Vector Search          | FAISS                     |
| Data Processing        | Pandas, NumPy             |
| Visualization          | Plotly, Matplotlib        |
| PDF Processing         | PyMuPDF, ReportLab, FPDF2 |
| DOCX Processing        | python-docx               |
| Authentication         | JWT, bcrypt               |
| Database               | SQLite, PostgreSQL        |
| ORM                    | SQLAlchemy                |
| Environment Management | python-dotenv             |
| 3D UI                  | Three.js                  |
| Version Control        | Git & GitHub              |

---

## 🧠 ATS Scoring System

The analyzer evaluates a resume across multiple dimensions:

1. **Semantic Similarity**
2. **Skill Match**
3. **Keyword Coverage**
4. **Experience Match**
5. **Education Match**
6. **Resume Format**

The system also includes skill synonym handling to recognize variations such as:

```text
k8s → Kubernetes
sklearn → scikit-learn
nodejs → Node.js
```

It uses calibrated scoring, partial skill matching, keyword analysis, and semantic similarity to provide more useful resume-job matching results.

---

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

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ai-resume-analyzer-pro.git
cd ai-resume-analyzer-pro
```

### 2. Create a virtual environment

#### Windows

```powershell
py -3.11 -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Some machine-learning packages such as `sentence-transformers`, `faiss-cpu`, and `spacy` may take additional time to install.

### 4. Configure environment variables

Create a `.env` file based on:

```text
.env.example
```

SQLite is used by default, so no database configuration is required for basic local usage.

### 5. Run the application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## 🖥️ Windows Quick Start

The project includes:

```text
run.bat
```

You can also start the application from PowerShell:

```powershell
streamlit run app.py
```

---

## 🔄 Application Workflow

```text
User Signup/Login
        ↓
Upload Resume
        ↓
Enter Job Description
        ↓
Resume Parsing
        ↓
ATS Analysis
        ↓
┌─────────────────────────────┐
│ Semantic Similarity         │
│ Skill Matching              │
│ Keyword Analysis            │
│ Experience Analysis         │
│ Education Analysis          │
│ Format Analysis             │
└─────────────────────────────┘
        ↓
ATS Score & Skill Gaps
        ↓
Resume Optimization
        ↓
AI Resume Rewriting
        ↓
Job-Specific Resume
        ↓
PDF / DOCX Export
```

---

## 📊 Main Application Pages

| Page              | Purpose                                  |
| ----------------- | ---------------------------------------- |
| Login             | Secure user authentication               |
| Signup            | Create a user account                    |
| Dashboard         | Resume analysis overview                 |
| Analyze           | Analyze resume against a job description |
| History           | View previous analyses                   |
| ATS Deep Dive     | Detailed ATS and skill analysis          |
| Rewrite Assistant | Improve resume bullet points             |
| Job Resume        | Generate job-specific resumes            |
| Compare           | Compare original and optimized resumes   |

---

## 🔒 Privacy

The project is designed with a **local-first approach**.

Core resume analysis can be performed locally without requiring paid external AI APIs.

User authentication and analysis data can be stored using the configured local database.

> Do not commit real credentials, API keys, passwords, database credentials, uploaded resumes, or private user data to GitHub.

---

## 📌 Future Improvements

* [ ] Cloud deployment
* [ ] Additional resume templates
* [ ] More job-category intelligence
* [ ] Advanced semantic search
* [ ] LinkedIn profile analysis
* [ ] Automated job-description extraction
* [ ] Resume version management
* [ ] More company knowledge bases
* [ ] Improved mobile responsiveness

---

## 🎓 Project Highlights

This project demonstrates practical experience with:

* Python application development
* Machine Learning
* Natural Language Processing
* Semantic similarity
* Vector search
* Retrieval-Augmented Generation concepts
* Resume parsing
* ATS optimization
* Data visualization
* Streamlit application development
* Authentication and authorization
* Database management
* PDF/DOCX generation
* Modular software architecture
* Git/GitHub project management

---

## 👩‍💻 Author

**Sana Nadaf**

B.E. Computer Science & Engineering

GitHub: `github.com/Sananadaf03`

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub.
