# ============================================================
# modules/job_categories.py
# Comprehensive job category catalog for ATS scoring & rewriting.
# Each category contains:
#   - required_skills:     core technical/role skills
#   - ats_keywords:        common ATS-tracked keywords for the role
#   - tools:               recommended tools/frameworks
#   - resume_tips:         section-level resume suggestions
#   - scoring_weights:     industry-specific weighting (sums ~1.0)
# ============================================================

JOB_CATEGORIES: dict[str, dict] = {
    "Software Engineer": {
        "required_skills": ["python", "java", "c++", "data structures", "algorithms",
                            "system design", "git", "sql", "rest api", "unit testing"],
        "ats_keywords": ["software development", "oop", "agile", "scrum", "ci/cd",
                         "code review", "debugging", "microservices"],
        "tools": ["Git", "Docker", "Jenkins", "Jira", "VS Code", "IntelliJ"],
        "resume_tips": [
            "Quantify performance gains (latency, throughput, cost).",
            "Mention scale: requests/sec, users, data volume.",
            "List languages and paradigms in a Skills block.",
        ],
        "scoring_weights": {"skills": 0.35, "keywords": 0.25, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "Full Stack Developer": {
        "required_skills": ["javascript", "typescript", "react", "node.js", "express",
                            "html", "css", "rest api", "sql", "mongodb", "git"],
        "ats_keywords": ["full stack", "frontend", "backend", "responsive design",
                         "spa", "rest", "graphql", "authentication"],
        "tools": ["React", "Next.js", "Node.js", "PostgreSQL", "MongoDB", "Vercel"],
        "resume_tips": [
            "Show end-to-end ownership: schema → API → UI.",
            "Highlight deployments and CI/CD pipelines.",
        ],
        "scoring_weights": {"skills": 0.32, "keywords": 0.28, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "Frontend Developer": {
        "required_skills": ["html", "css", "javascript", "typescript", "react",
                            "vue", "responsive design", "accessibility", "tailwind"],
        "ats_keywords": ["ui", "ux", "spa", "component library", "wcag", "seo",
                         "performance optimization", "web vitals"],
        "tools": ["React", "Vite", "Tailwind", "Figma", "Storybook", "Chrome DevTools"],
        "resume_tips": [
            "Mention Lighthouse / Web Vitals improvements.",
            "Highlight design-system contributions and a11y work.",
        ],
        "scoring_weights": {"skills": 0.32, "keywords": 0.28, "experience": 0.18,
                            "semantic": 0.17, "format": 0.05},
    },
    "Backend Developer": {
        "required_skills": ["python", "java", "node.js", "go", "sql", "rest api",
                            "microservices", "redis", "postgresql", "system design"],
        "ats_keywords": ["api design", "scalability", "throughput", "queue",
                         "caching", "authentication", "authorization"],
        "tools": ["Postgres", "Redis", "Kafka", "Docker", "Kubernetes", "Postman"],
        "resume_tips": [
            "Quantify p95 latency, RPS, cost per request.",
            "Show schema design and migration ownership.",
        ],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Java Developer": {
        "required_skills": ["java", "spring boot", "hibernate", "jpa", "maven",
                            "rest api", "microservices", "junit", "sql"],
        "ats_keywords": ["spring", "j2ee", "multithreading", "design patterns",
                         "kafka", "mockito"],
        "tools": ["IntelliJ", "Maven", "Gradle", "Spring Boot", "Docker", "Jenkins"],
        "resume_tips": ["Specify Spring Boot version and JVM tuning wins."],
        "scoring_weights": {"skills": 0.36, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Python Developer": {
        "required_skills": ["python", "django", "flask", "fastapi", "rest api",
                            "sql", "pandas", "numpy", "pytest"],
        "ats_keywords": ["asyncio", "celery", "etl", "scripting", "automation",
                         "pep8", "type hints"],
        "tools": ["FastAPI", "Django", "Celery", "Pytest", "Poetry", "Docker"],
        "resume_tips": ["Show PyPI packages, async work, or perf wins."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "Data Analyst": {
        "required_skills": ["sql", "excel", "python", "tableau", "power bi",
                            "statistics", "data visualization", "etl"],
        "ats_keywords": ["dashboard", "reporting", "kpi", "a/b testing",
                         "stakeholder", "insight"],
        "tools": ["SQL", "Tableau", "Power BI", "Excel", "Looker", "dbt"],
        "resume_tips": ["Show $ or % business impact from each insight."],
        "scoring_weights": {"skills": 0.30, "keywords": 0.30, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "Data Scientist": {
        "required_skills": ["python", "sql", "machine learning", "statistics",
                            "pandas", "scikit-learn", "tensorflow", "pytorch",
                            "data visualization"],
        "ats_keywords": ["modeling", "feature engineering", "experimentation",
                         "a/b testing", "regression", "classification"],
        "tools": ["Jupyter", "scikit-learn", "MLflow", "Airflow", "Spark"],
        "resume_tips": ["Lead with model lift and downstream business KPI."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.15, "format": 0.05},
    },
    "Machine Learning Engineer": {
        "required_skills": ["python", "tensorflow", "pytorch", "mlops", "docker",
                            "kubernetes", "spark", "feature store", "model deployment"],
        "ats_keywords": ["training pipeline", "inference", "model serving",
                         "monitoring", "drift", "gpu"],
        "tools": ["MLflow", "Kubeflow", "SageMaker", "Vertex AI", "Triton"],
        "resume_tips": ["Show training cost reductions and serving latency."],
        "scoring_weights": {"skills": 0.36, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "AI Engineer": {
        "required_skills": ["python", "llm", "rag", "transformers", "langchain",
                            "vector database", "prompt engineering", "fine-tuning"],
        "ats_keywords": ["generative ai", "openai", "embedding", "evaluation",
                         "guardrails", "agents"],
        "tools": ["LangChain", "LlamaIndex", "Pinecone", "FAISS", "Hugging Face"],
        "resume_tips": ["Cite eval metrics (faithfulness, latency, cost/req)."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "DevOps Engineer": {
        "required_skills": ["linux", "docker", "kubernetes", "terraform", "aws",
                            "ci/cd", "jenkins", "bash", "monitoring"],
        "ats_keywords": ["iac", "observability", "sre", "incident response",
                         "ansible", "helm"],
        "tools": ["Terraform", "Helm", "ArgoCD", "Prometheus", "Grafana"],
        "resume_tips": ["Show MTTR, deploy frequency, infra cost savings."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Cloud Engineer": {
        "required_skills": ["aws", "azure", "gcp", "terraform", "kubernetes",
                            "networking", "iam", "linux"],
        "ats_keywords": ["multi-region", "high availability", "vpc", "well-architected"],
        "tools": ["Terraform", "CloudFormation", "EKS", "GKE", "AKS"],
        "resume_tips": ["List certifications (AWS SA, GCP PCA, AZ-104)."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Cybersecurity Analyst": {
        "required_skills": ["siem", "incident response", "vulnerability assessment",
                            "network security", "python", "linux", "owasp"],
        "ats_keywords": ["soc", "edr", "threat intelligence", "compliance",
                         "iso 27001", "nist"],
        "tools": ["Splunk", "Wireshark", "Nessus", "Burp Suite", "CrowdStrike"],
        "resume_tips": ["Quote MTTD/MTTR and incidents handled."],
        "scoring_weights": {"skills": 0.32, "keywords": 0.30, "experience": 0.20,
                            "semantic": 0.13, "format": 0.05},
    },
    "UI/UX Designer": {
        "required_skills": ["figma", "user research", "wireframing", "prototyping",
                            "design system", "usability testing", "accessibility"],
        "ats_keywords": ["user-centered", "personas", "journey map", "ia",
                         "interaction design", "wcag"],
        "tools": ["Figma", "Sketch", "Adobe XD", "Maze", "Notion"],
        "resume_tips": ["Link a portfolio; quote conversion or task-success lift."],
        "scoring_weights": {"skills": 0.30, "keywords": 0.25, "experience": 0.20,
                            "semantic": 0.20, "format": 0.05},
    },
    "Product Manager": {
        "required_skills": ["roadmap", "user research", "data analysis", "agile",
                            "stakeholder management", "sql", "a/b testing"],
        "ats_keywords": ["okrs", "kpi", "discovery", "go-to-market", "prioritization",
                         "user stories"],
        "tools": ["Jira", "Notion", "Amplitude", "Mixpanel", "Figma"],
        "resume_tips": ["Lead bullets with the metric you moved."],
        "scoring_weights": {"skills": 0.25, "keywords": 0.30, "experience": 0.25,
                            "semantic": 0.15, "format": 0.05},
    },
    "Business Analyst": {
        "required_skills": ["sql", "excel", "requirements gathering", "process mapping",
                            "data analysis", "tableau", "stakeholder management"],
        "ats_keywords": ["brd", "frd", "uat", "gap analysis", "kpi", "agile"],
        "tools": ["Excel", "SQL", "Tableau", "Power BI", "Visio", "Jira"],
        "resume_tips": ["Quantify hours saved or revenue uplift."],
        "scoring_weights": {"skills": 0.28, "keywords": 0.30, "experience": 0.22,
                            "semantic": 0.15, "format": 0.05},
    },
    "Mobile App Developer": {
        "required_skills": ["react native", "flutter", "ios", "android", "kotlin",
                            "swift", "rest api", "git"],
        "ats_keywords": ["app store", "play store", "push notifications",
                         "offline-first", "performance"],
        "tools": ["Xcode", "Android Studio", "Firebase", "Fastlane"],
        "resume_tips": ["List app store ratings and downloads."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.15, "format": 0.05},
    },
    "Android Developer": {
        "required_skills": ["kotlin", "java", "android sdk", "jetpack compose",
                            "mvvm", "rest api", "rxjava", "coroutines"],
        "ats_keywords": ["material design", "play store", "ci/cd", "espresso"],
        "tools": ["Android Studio", "Firebase", "Gradle", "Detekt"],
        "resume_tips": ["Mention min SDK, ANR/crash-free rates."],
        "scoring_weights": {"skills": 0.36, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "iOS Developer": {
        "required_skills": ["swift", "swiftui", "uikit", "core data", "combine",
                            "rest api", "xcode"],
        "ats_keywords": ["app store", "tdd", "mvvm", "asynchronous", "testflight"],
        "tools": ["Xcode", "SwiftLint", "Fastlane", "Firebase"],
        "resume_tips": ["Mention crash-free sessions and store ratings."],
        "scoring_weights": {"skills": 0.36, "keywords": 0.24, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "QA Engineer": {
        "required_skills": ["selenium", "cypress", "playwright", "test automation",
                            "api testing", "sql", "ci/cd", "jira"],
        "ats_keywords": ["regression", "smoke test", "test plan", "bug triage",
                         "performance testing", "load testing"],
        "tools": ["Selenium", "Cypress", "Postman", "JMeter", "TestRail"],
        "resume_tips": ["Cite defect-escape rate and automation coverage %."],
        "scoring_weights": {"skills": 0.32, "keywords": 0.28, "experience": 0.20,
                            "semantic": 0.15, "format": 0.05},
    },
    "System Administrator": {
        "required_skills": ["linux", "windows server", "bash", "powershell",
                            "active directory", "networking", "backup", "monitoring"],
        "ats_keywords": ["uptime", "patching", "incident", "ticketing", "automation"],
        "tools": ["Ansible", "Nagios", "Zabbix", "VMware"],
        "resume_tips": ["Mention SLA uptime % and tickets resolved/wk."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Network Engineer": {
        "required_skills": ["cisco", "tcp/ip", "bgp", "ospf", "vpn", "firewall",
                            "sdn", "wireless"],
        "ats_keywords": ["lan", "wan", "ccna", "ccnp", "qos", "load balancer"],
        "tools": ["Wireshark", "Cisco IOS", "Juniper", "Palo Alto"],
        "resume_tips": ["List certs (CCNA/CCNP) prominently."],
        "scoring_weights": {"skills": 0.34, "keywords": 0.26, "experience": 0.22,
                            "semantic": 0.13, "format": 0.05},
    },
    "Digital Marketing": {
        "required_skills": ["seo", "sem", "google ads", "facebook ads",
                            "google analytics", "content marketing", "email marketing"],
        "ats_keywords": ["roas", "ctr", "cpa", "funnel", "conversion", "campaign"],
        "tools": ["Google Ads", "GA4", "HubSpot", "SEMrush", "Mailchimp"],
        "resume_tips": ["Show ROAS, CAC, and conversion lifts."],
        "scoring_weights": {"skills": 0.26, "keywords": 0.32, "experience": 0.22,
                            "semantic": 0.15, "format": 0.05},
    },
    "HR": {
        "required_skills": ["recruitment", "onboarding", "employee relations",
                            "hris", "payroll", "compliance", "performance management"],
        "ats_keywords": ["talent acquisition", "ats", "engagement", "retention",
                         "diversity", "policy"],
        "tools": ["Workday", "BambooHR", "Greenhouse", "LinkedIn Recruiter"],
        "resume_tips": ["Quote time-to-hire and retention improvements."],
        "scoring_weights": {"skills": 0.26, "keywords": 0.30, "experience": 0.24,
                            "semantic": 0.15, "format": 0.05},
    },
    "Finance": {
        "required_skills": ["financial modeling", "excel", "accounting", "forecasting",
                            "budgeting", "valuation", "sql", "powerbi"],
        "ats_keywords": ["p&l", "cash flow", "variance analysis", "ifrs", "gaap",
                         "fp&a"],
        "tools": ["Excel", "SAP", "Oracle", "Tableau", "Power BI"],
        "resume_tips": ["Cite $ amounts managed and accuracy %."],
        "scoring_weights": {"skills": 0.28, "keywords": 0.30, "experience": 0.24,
                            "semantic": 0.13, "format": 0.05},
    },
    "Sales": {
        "required_skills": ["b2b sales", "crm", "lead generation", "negotiation",
                            "account management", "forecasting", "salesforce"],
        "ats_keywords": ["quota", "pipeline", "closed won", "arr", "mrr",
                         "cold outreach"],
        "tools": ["Salesforce", "HubSpot", "Outreach", "LinkedIn Sales Nav"],
        "resume_tips": ["Lead bullets with quota attainment %."],
        "scoring_weights": {"skills": 0.24, "keywords": 0.32, "experience": 0.26,
                            "semantic": 0.13, "format": 0.05},
    },
    "Content Writer": {
        "required_skills": ["copywriting", "seo", "editing", "research",
                            "content strategy", "wordpress", "cms"],
        "ats_keywords": ["blog", "long-form", "tone of voice", "keyword research",
                         "engagement"],
        "tools": ["WordPress", "Grammarly", "SurferSEO", "Notion"],
        "resume_tips": ["Cite organic traffic growth or rankings won."],
        "scoring_weights": {"skills": 0.24, "keywords": 0.32, "experience": 0.24,
                            "semantic": 0.15, "format": 0.05},
    },
    "Graphic Designer": {
        "required_skills": ["adobe photoshop", "illustrator", "indesign", "figma",
                            "branding", "typography", "layout"],
        "ats_keywords": ["visual identity", "print", "digital", "campaign",
                         "marketing collateral"],
        "tools": ["Photoshop", "Illustrator", "InDesign", "Figma", "After Effects"],
        "resume_tips": ["Link a portfolio; quote engagement or brand lift."],
        "scoring_weights": {"skills": 0.30, "keywords": 0.25, "experience": 0.20,
                            "semantic": 0.20, "format": 0.05},
    },
}


def list_categories() -> list[str]:
    return list(JOB_CATEGORIES.keys())


def get_category(name: str) -> dict | None:
    return JOB_CATEGORIES.get(name)


def detect_category(jd_text: str) -> str:
    """Best-effort heuristic: pick the category whose keywords appear most in the JD."""
    if not jd_text:
        return "Software Engineer"
    jd_lower = jd_text.lower()
    best, best_score = "Software Engineer", 0
    for name, cat in JOB_CATEGORIES.items():
        score = 0
        for kw in cat["required_skills"] + cat["ats_keywords"]:
            if kw.lower() in jd_lower:
                score += 1
        if score > best_score:
            best, best_score = name, score
    return best
