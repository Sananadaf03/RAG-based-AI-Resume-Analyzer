# ============================================================
# modules/analyzer.py  (v2 — improved ATS accuracy)
# Core Analysis Engine: ATS Scoring, Skill Extraction, Gap Detection
# ============================================================

import re
import logging
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Comprehensive Skills Knowledge Base
# ─────────────────────────────────────────────
TECH_SKILLS = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "swift", "kotlin", "scala", "r", "matlab", "julia", "dart", "php",
        "ruby", "perl", "bash", "shell", "powershell", "sql", "html", "css",
    ],
    "ml_ai": [
        "machine learning", "deep learning", "neural network", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost",
        "lightgbm", "catboost", "hugging face", "transformers", "bert", "gpt",
        "llm", "large language model", "rag", "retrieval augmented generation",
        "langchain", "llamaindex", "stable diffusion", "diffusion model",
        "opencv", "yolo", "object detection", "image segmentation",
        "recommendation system", "time series", "forecasting", "regression",
        "classification", "clustering", "pca", "dimensionality reduction",
        "feature engineering", "hyperparameter tuning", "mlflow", "wandb",
        "model deployment", "model serving", "onnx",
    ],
    "data_engineering": [
        "spark", "apache spark", "hadoop", "hive", "kafka", "airflow", "dbt",
        "etl", "elt", "data pipeline", "data warehouse", "data lake", "lakehouse",
        "snowflake", "databricks", "bigquery", "redshift", "clickhouse",
        "pandas", "numpy", "dask", "polars", "arrow",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
        "dynamodb", "sqlite", "oracle", "sql server", "neo4j", "vector database",
        "pinecone", "weaviate", "chroma", "faiss", "milvus",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "github actions", "ci/cd", "devops",
        "mlops", "helm", "istio", "prometheus", "grafana", "nginx", "linux",
        "serverless", "lambda", "cloud functions", "ecs", "eks", "aks",
    ],
    "web_api": [
        "rest", "restful", "api", "graphql", "grpc", "fastapi", "flask", "django",
        "node.js", "express", "react", "vue", "angular", "next.js", "streamlit",
        "websocket", "microservices", "swagger", "openapi",
    ],
    "tools_practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "agile", "scrum",
        "unit testing", "integration testing", "tdd", "bdd", "code review",
        "system design", "design patterns", "solid", "object oriented",
        "functional programming", "data structures", "algorithms", "leetcode",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "collaboration", "problem solving",
        "critical thinking", "analytical", "presentation", "mentoring", "stakeholder",
        "project management", "cross-functional", "strategic thinking",
    ],
}

# Synonym / alias map: when we see the key we treat it as equivalent to the value
SKILL_SYNONYMS: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8": "kubernetes",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "gcp": "google cloud",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "elastic": "elasticsearch",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "vuejs": "vue",
    "nextjs": "next.js",
    "golang": "go",
    "ml": "machine learning",
    "dl": "deep learning",
    "cv": "computer vision",
    "llms": "llm",
    "nlp": "natural language processing",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "rest api": "rest",
    "restful api": "restful",
    "object-oriented": "object oriented",
    "oop": "object oriented",
    "data science": "machine learning",
    "data engineering": "data pipeline",
    "deep-learning": "deep learning",
    "machinelearning": "machine learning",
}

# Flatten + canonical lookup
ALL_SKILLS: list[str] = []
SKILL_CATEGORIES: dict[str, str] = {}
for _cat, _skills in TECH_SKILLS.items():
    for _sk in _skills:
        ALL_SKILLS.append(_sk)
        SKILL_CATEGORIES[_sk] = _cat

# Sort longest-first so multi-word phrases match before sub-words
ALL_SKILLS.sort(key=len, reverse=True)


# ─────────────────────────────────────────────
# ATS Scoring Weights  (tuned for fairness)
# ─────────────────────────────────────────────
SCORING_WEIGHTS = {
    "semantic_similarity": 0.28,
    "keyword_match":       0.22,
    "skill_match":         0.28,
    "experience_match":    0.10,
    "education_match":     0.07,
    "format_quality":      0.05,
}

# Calibration: raw component scores tend to be lower than intuition
# These per-component floors prevent any single weak signal from
# collapsing the whole score.
COMPONENT_FLOORS = {
    "semantic_similarity": 0.20,
    "keyword_match":       0.15,
    "skill_match":         0.10,
    "experience_match":    0.70,  # default OK when JD doesn't state years
    "education_match":     0.60,
    "format_quality":      0.60,
}

# Sigmoid-like booster: maps raw [0,1] → rescaled [floor, 1]
def _scale_component(raw: float, floor: float) -> float:
    """Linearly rescale raw score from [0,1] to [floor,1]."""
    raw = float(np.clip(raw, 0.0, 1.0))
    return floor + raw * (1.0 - floor)


# ─────────────────────────────────────────────
# Skill Extractor (improved)
# ─────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """Lowercase, collapse whitespace, normalise hyphens/slashes."""
    t = text.lower()
    t = re.sub(r"[-/]", " ", t)          # c++ stays; c/c++ → c  c++
    t = re.sub(r"\s+", " ", t)
    return t


def _resolve_synonyms(text: str) -> str:
    """Replace known aliases with canonical skill names."""
    for alias, canonical in SKILL_SYNONYMS.items():
        # word-boundary safe replacement
        text = re.sub(r'\b' + re.escape(alias) + r'\b', canonical, text)
    return text


def extract_skills(text: str) -> dict:
    """
    Extract skills from text using keyword matching with synonym expansion.
    Returns skills grouped by category.
    """
    norm = _normalize_text(text)
    norm = _resolve_synonyms(norm)

    found: dict[str, list[str]] = {}
    consumed = set()  # track character spans to avoid double-counting

    for skill in ALL_SKILLS:  # longest-first order
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        for m in re.finditer(pattern, norm):
            span = (m.start(), m.end())
            # Skip if already covered by a longer match
            if any(s <= span[0] and span[1] <= e for s, e in consumed):
                continue
            consumed.add(span)
            cat = SKILL_CATEGORIES.get(skill, "general")
            found.setdefault(cat, [])
            if skill not in found[cat]:
                found[cat].append(skill)

    return found


def extract_years_experience(text: str) -> float:
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*(?:relevant\s*|total\s*)?experience',
        r'(\d+)\+?\s*years?\s*experience',
        r'over\s*(\d+)\s*years?',
        r'(\d+)\+?\s*yrs',
        r'(\d{4})\s*[-–]\s*(?:present|current|now)',   # date ranges
    ]
    years_found = []
    for pat in patterns:
        matches = re.findall(pat, text.lower())
        if pat.endswith(r'(?:present|current|now)'):
            # date range: approximate tenure
            import datetime
            current_year = datetime.datetime.now().year
            for m in matches:
                try:
                    diff = current_year - int(m)
                    if 0 < diff < 50:
                        years_found.append(diff)
                except ValueError:
                    pass
        else:
            years_found.extend([int(m) for m in matches if m.isdigit()])

    return max(years_found) if years_found else 0.0


def extract_required_experience(jd_text: str) -> float:
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*(?:relevant\s*)?experience',
        r'minimum\s*(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
        r'(\d+)\+?\s*yrs',
    ]
    years_found = []
    for pat in patterns:
        matches = re.findall(pat, jd_text.lower())
        years_found.extend([int(m) for m in matches if m.isdigit()])
    return min(years_found) if years_found else 0.0


def extract_keywords_tfidf(jd_text: str, resume_text: str, top_n: int = 30) -> tuple[set, set]:
    """
    Improved keyword extraction: fit TF-IDF on *both* texts so the vocabulary
    is shared. JD keywords are top-weighted terms in the JD; resume keywords are
    the subset of JD keywords found in the resume.

    Returns (jd_keywords, resume_matched_keywords)
    """
    try:
        tfidf = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=500,
            sublinear_tf=True,
            min_df=1,
        )
        matrix = tfidf.fit_transform([jd_text, resume_text])
        feature_names = tfidf.get_feature_names_out()

        jd_scores = matrix[0].toarray()[0]
        resume_scores = matrix[1].toarray()[0]

        # Top JD keywords
        top_idx = jd_scores.argsort()[::-1][:top_n]
        jd_kws = {feature_names[i] for i in top_idx if jd_scores[i] > 0}

        # Which of those appear in the resume (any non-zero score)
        matched_kws = {kw for kw in jd_kws if resume_scores[list(feature_names).index(kw)] > 0}

        return jd_kws, matched_kws
    except Exception:
        return set(), set()


def detect_degree(text: str) -> list[str]:
    degrees = []
    patterns = {
        "PhD / Doctorate":   r'\b(ph\.?d|doctorate|doctoral)\b',
        "Master's Degree":   r'\b(m\.?s\.?|m\.?tech|mba|master)\b',
        "Bachelor's Degree": r'\b(b\.?s\.?|b\.?tech|b\.?e\.?|bachelor)\b',
        "Associate Degree":  r'\b(associate)\b',
        "Certification":     r'\b(certified|certification|certificate)\b',
        "Bootcamp":          r'\b(bootcamp|boot camp)\b',
    }
    text_lower = text.lower()
    for degree, pat in patterns.items():
        if re.search(pat, text_lower):
            degrees.append(degree)
    return degrees


# ─────────────────────────────────────────────
# Core ATS Analyzer
# ─────────────────────────────────────────────

class ATSAnalyzer:
    """
    Main analysis engine combining RAG retrieval results with
    rule-based NLP analysis for comprehensive ATS scoring.
    """

    def analyze(
        self,
        resume_data: dict,
        jd_data: dict,
        retriever,
        retrieved_chunks: list[dict],
    ) -> dict:
        resume_text = resume_data["full_text"]
        jd_text = jd_data["full_text"]

        # ── Step 1: Skill Analysis (improved extractor)
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        resume_skills_flat = set(s for skills in resume_skills.values() for s in skills)
        jd_skills_flat = set(s for skills in jd_skills.values() for s in skills)

        matched_skills = resume_skills_flat & jd_skills_flat
        missing_skills = jd_skills_flat - resume_skills_flat
        extra_skills = resume_skills_flat - jd_skills_flat

        # Partial credit: also count near-matches via synonyms
        if jd_skills_flat:
            # Count any JD skill whose synonym/alias appears in resume text
            norm_resume = _resolve_synonyms(_normalize_text(resume_text))
            partial_matches = set()
            for sk in missing_skills:
                if re.search(r'\b' + re.escape(sk) + r'\b', norm_resume):
                    partial_matches.add(sk)
            effective_matched = matched_skills | partial_matches
            skill_match_pct = min(
                len(effective_matched) / len(jd_skills_flat) +
                0.05 * (len(extra_skills) / max(len(jd_skills_flat), 1)),  # bonus for extra
                1.0
            )
        else:
            effective_matched = matched_skills
            skill_match_pct = 0.85  # No skills in JD → assume OK

        # ── Step 2: Keyword Analysis (improved — shared vocabulary)
        jd_keywords, matched_keywords = extract_keywords_tfidf(jd_text, resume_text, top_n=35)
        missing_keywords = jd_keywords - matched_keywords
        keyword_match_pct = (
            len(matched_keywords) / len(jd_keywords) if jd_keywords else 0.85
        )

        # ── Step 3: Semantic Similarity (from retriever)
        raw_sem_sim = retriever.get_overall_similarity(resume_text, jd_text)
        raw_sem_sim = float(np.clip(raw_sem_sim, 0.0, 1.0))

        # ── Step 4: Experience Match
        resume_years = extract_years_experience(resume_text)
        required_years = extract_required_experience(jd_text)
        if required_years > 0 and resume_years > 0:
            exp_score = min(resume_years / required_years, 1.0)
        elif resume_years > 0:
            exp_score = min(0.70 + 0.06 * resume_years, 1.0)  # more years → higher default
        else:
            exp_score = 0.75  # unknown → neutral-positive

        # ── Step 5: Education Match
        resume_degrees = detect_degree(resume_text)
        jd_degrees = detect_degree(jd_text)
        if not jd_degrees:
            education_score = 0.85  # No requirement → generous default
        elif any(d in jd_degrees for d in resume_degrees):
            education_score = 1.0
        elif resume_degrees:
            education_score = 0.65  # Has a degree, just different level
        else:
            education_score = 0.35

        # ── Step 6: Format Quality
        word_count = resume_data.get("word_count", 0)
        section_count = len(resume_data.get("sections", {}))
        format_score = self._score_format(word_count, section_count)

        # ── Step 7: Apply per-component floors then compute weighted score
        scaled = {
            "semantic_similarity": _scale_component(raw_sem_sim,    COMPONENT_FLOORS["semantic_similarity"]),
            "keyword_match":       _scale_component(keyword_match_pct, COMPONENT_FLOORS["keyword_match"]),
            "skill_match":         _scale_component(skill_match_pct,   COMPONENT_FLOORS["skill_match"]),
            "experience_match":    _scale_component(exp_score,        COMPONENT_FLOORS["experience_match"]),
            "education_match":     _scale_component(education_score,  COMPONENT_FLOORS["education_match"]),
            "format_quality":      _scale_component(format_score,     COMPONENT_FLOORS["format_quality"]),
        }

        weighted_score = sum(
            SCORING_WEIGHTS[k] * scaled[k] for k in SCORING_WEIGHTS
        )
        ats_score = round(weighted_score * 100, 1)

        # ── Step 8: Suggestions
        suggestions = self._generate_suggestions(
            ats_score=ats_score,
            missing_skills=missing_skills,
            missing_keywords=missing_keywords,
            word_count=word_count,
            section_names=resume_data.get("section_names", []),
            resume_years=resume_years,
            required_years=required_years,
            skill_match_pct=skill_match_pct * 100,
        )

        # ── Step 9: Rewriting Suggestions
        rewrite_bullets = self._generate_rewrite_bullets(
            resume_data=resume_data,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )

        # ── Step 10: Confidence Score
        confidence = self._compute_confidence(
            resume_data=resume_data,
            retrieved_chunks=retrieved_chunks,
        )

        return {
            # Scores
            "ats_score":            ats_score,
            "confidence_score":     confidence,
            "semantic_similarity":  round(scaled["semantic_similarity"] * 100, 1),
            "skill_match_pct":      round(scaled["skill_match"] * 100, 1),
            "keyword_match_pct":    round(scaled["keyword_match"] * 100, 1),
            "experience_score":     round(scaled["experience_match"] * 100, 1),
            "education_score":      round(scaled["education_match"] * 100, 1),
            "format_score":         round(scaled["format_quality"] * 100, 1),

            # Skills
            "matched_skills":            sorted(matched_skills),
            "missing_skills":            sorted(missing_skills),
            "extra_skills":              sorted(extra_skills),
            "resume_skills_by_category": resume_skills,
            "jd_skills_by_category":     jd_skills,

            # Keywords
            "matched_keywords": sorted(matched_keywords),
            "missing_keywords": sorted(missing_keywords),

            # Experience & Education
            "resume_years_experience":  resume_years,
            "required_years_experience": required_years,
            "resume_degrees":           resume_degrees,
            "jd_degrees":               jd_degrees,

            # Suggestions
            "improvement_suggestions": suggestions,
            "rewrite_bullets":         rewrite_bullets,

            # Retrieved context
            "top_retrieved_chunks": retrieved_chunks[:5],

            # Metadata
            "word_count":    word_count,
            "section_count": section_count,
            "section_names": resume_data.get("section_names", []),
        }

    # ── helpers ──────────────────────────────────────────────

    def _score_format(self, word_count: int, section_count: int) -> float:
        """Score resume formatting quality."""
        if word_count < 100:
            wc_score = 0.30
        elif word_count < 250:
            wc_score = 0.60
        elif word_count <= 900:
            wc_score = 1.0
        elif word_count <= 1400:
            wc_score = 0.88
        else:
            wc_score = 0.70

        sec_score = min(section_count / 5, 1.0)
        return 0.6 * wc_score + 0.4 * sec_score

    def _generate_suggestions(
        self,
        ats_score: float,
        missing_skills: set,
        missing_keywords: set,
        word_count: int,
        section_names: list,
        resume_years: float,
        required_years: float,
        skill_match_pct: float,
    ) -> list[dict]:
        suggestions = []

        if missing_skills:
            top_missing = sorted(missing_skills)[:8]
            suggestions.append({
                "category": "🎯 Skill Gaps",
                "priority": "HIGH",
                "suggestion": f"Add these missing skills to your resume: {', '.join(top_missing)}",
                "impact": "Can increase ATS score by 10–20 points",
            })

        if missing_keywords:
            top_kw = sorted(missing_keywords)[:6]
            suggestions.append({
                "category": "🔑 Keywords",
                "priority": "HIGH",
                "suggestion": f"Incorporate these JD keywords naturally: {', '.join(top_kw)}",
                "impact": "Helps pass automated keyword filters",
            })

        if required_years > 0 and resume_years < required_years:
            suggestions.append({
                "category": "⏳ Experience",
                "priority": "MEDIUM",
                "suggestion": (
                    f"The JD requires {required_years:.0f}+ years but your resume "
                    f"shows ~{resume_years:.0f} years. Highlight consulting, freelance, "
                    f"or side projects to bridge the gap."
                ),
                "impact": "Can improve experience score significantly",
            })

        if word_count < 350:
            suggestions.append({
                "category": "📝 Content Length",
                "priority": "MEDIUM",
                "suggestion": "Your resume is too short. Expand bullet points with quantified achievements.",
                "impact": "Longer, richer resumes rank better with ATS",
            })
        elif word_count > 1100:
            suggestions.append({
                "category": "📝 Content Length",
                "priority": "LOW",
                "suggestion": "Your resume may be too long. Trim to 1–2 pages; remove outdated experience.",
                "impact": "Concise resumes are preferred by recruiters",
            })

        essential_sections = {"experience", "skills", "education"}
        present = set(section_names)
        for sec in essential_sections - present:
            suggestions.append({
                "category": "🗂️ Structure",
                "priority": "HIGH",
                "suggestion": f"Add a dedicated '{sec.title()}' section to your resume.",
                "impact": "ATS systems look for labeled sections",
            })

        if "summary" not in present and "objective" not in present:
            suggestions.append({
                "category": "🗂️ Structure",
                "priority": "MEDIUM",
                "suggestion": "Add a professional Summary/Profile section tailored to this role.",
                "impact": "First thing recruiters and ATS read — set the tone",
            })

        suggestions.append({
            "category": "📊 Impact Metrics",
            "priority": "MEDIUM",
            "suggestion": "Quantify achievements: use numbers, %, $, and time (e.g., 'Reduced latency by 40%').",
            "impact": "Metrics make bullets 3× more impactful to recruiters",
        })

        if ats_score < 50:
            suggestions.append({
                "category": "⚠️ Overall Strategy",
                "priority": "HIGH",
                "suggestion": "Major overhaul needed. Tailor your resume specifically for this job description.",
                "impact": "Customized resumes score 30–50% higher",
            })
        elif ats_score < 70:
            suggestions.append({
                "category": "✅ Overall Strategy",
                "priority": "MEDIUM",
                "suggestion": "Good foundation. Focus on keyword integration and quantified bullets.",
                "impact": "Could push score above 75%",
            })

        return suggestions

    def _generate_rewrite_bullets(
        self,
        resume_data: dict,
        matched_skills: set,
        missing_skills: set,
    ) -> list[dict]:
        weak_patterns = [
            {
                "before": "Responsible for maintaining the codebase.",
                "after": "Owned and maintained a 50K-line Python codebase, reducing bug rate by 35% through automated testing.",
                "tip": "Replace 'responsible for' with an action verb + metric.",
            },
            {
                "before": "Worked on machine learning models.",
                "after": "Developed and deployed 3 production ML models (XGBoost, BERT) achieving 94% accuracy on classification tasks.",
                "tip": "Specify technology stack + quantify performance.",
            },
            {
                "before": "Helped improve system performance.",
                "after": "Optimized database queries and caching strategy, reducing API response time by 60% (400ms → 160ms).",
                "tip": "Show before/after metrics and the method used.",
            },
            {
                "before": "Led a team of engineers.",
                "after": "Led a cross-functional team of 5 engineers, delivering 3 product features on schedule with 0 P1 incidents.",
                "tip": "State team size, deliverables, and outcome.",
            },
            {
                "before": "Collaborated with data scientists on projects.",
                "after": "Partnered with data science team to productionize 2 recommender models, driving 18% increase in user engagement.",
                "tip": "Name collaborators, the output, and business impact.",
            },
        ]

        if missing_skills:
            top_3_missing = sorted(missing_skills)[:3]
            for skill in top_3_missing:
                weak_patterns.append({
                    "before": "Used various tools and technologies.",
                    "after": f"Integrated {skill} into the data pipeline, reducing manual processing time by 45%.",
                    "tip": f"Mention '{skill}' explicitly — it's in the JD but missing from your resume.",
                })

        return weak_patterns[:8]

    def _compute_confidence(self, resume_data: dict, retrieved_chunks: list[dict]) -> float:
        word_count = resume_data.get("word_count", 0)
        n_chunks = len(retrieved_chunks)

        wc_conf = min(word_count / 400, 1.0)
        chunk_conf = min(n_chunks / 5, 1.0)

        avg_retrieval_score = (
            np.mean([c.get("hybrid_score", 0) for c in retrieved_chunks])
            if retrieved_chunks else 0.0
        )

        confidence = 0.4 * wc_conf + 0.3 * chunk_conf + 0.3 * float(avg_retrieval_score)
        # Floor the confidence so it doesn't show 0% for reasonable inputs
        confidence = max(confidence, 0.35)
        return round(float(np.clip(confidence, 0, 1)) * 100, 1)
