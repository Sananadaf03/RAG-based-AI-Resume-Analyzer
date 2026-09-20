# ============================================================
# modules/company_kb.py
# Company Knowledge Base — local dataset for common companies,
# interview questions, required skills, and career guidance.
# ============================================================

import re
import logging

logger = logging.getLogger(__name__)

COMPANY_DATABASE = {
    "google": {
        "name": "Google (Alphabet Inc.)",
        "overview": "One of the world's most valuable technology companies, known for Search, Cloud, Android, YouTube, and AI. Headquartered in Mountain View, CA.",
        "culture": "Data-driven, innovative culture with emphasis on 20% projects, psychological safety, and OKR goal-setting.",
        "technologies": ["Python", "Go", "C++", "Java", "JavaScript", "TensorFlow", "Kubernetes", "BigQuery", "Spanner", "Borg/Kubernetes"],
        "required_skills": ["Algorithms & Data Structures", "System Design", "Distributed Systems", "Machine Learning", "Cloud Computing"],
        "interview_process": [
            "Online Application / Referral",
            "Recruiter Screen (30 min)",
            "Technical Phone Interview (45-60 min) — 1-2 rounds",
            "On-site / Virtual Loop (4-5 rounds): Coding + System Design + Behavioral",
            "Team Matching & Offer",
        ],
        "interview_questions": [
            "Design a URL shortener like bit.ly",
            "Find the LCA of two nodes in a binary tree",
            "Design Google Search autocomplete",
            "How would you scale a distributed key-value store?",
            "Tell me about a time you handled a conflict with a coworker",
        ],
        "certifications": ["Google Cloud Professional", "TensorFlow Developer Certificate", "Google Analytics"],
        "avg_salary": "$180,000 - $350,000 (SWE L4-L7)",
    },
    "amazon": {
        "name": "Amazon (Amazon.com, Inc.)",
        "overview": "Global leader in e-commerce and cloud computing (AWS). Also operates Alexa, Prime Video, Whole Foods. HQ: Seattle, WA.",
        "culture": "Leadership Principles-driven culture: Customer Obsession, Ownership, Invent & Simplify, Bias for Action, Deliver Results.",
        "technologies": ["Java", "Python", "C++", "AWS", "DynamoDB", "S3", "Lambda", "Kinesis", "Kafka", "React"],
        "required_skills": ["AWS Services", "System Design", "Leadership Principles", "Algorithms", "Microservices", "DevOps"],
        "interview_process": [
            "Online Application",
            "Online Assessment: Coding + Work Simulation",
            "Phone Screen (45 min): Coding + LP questions",
            "Virtual On-site Loop (4-6 rounds): Coding + System Design + Bar Raiser + Behavioral",
        ],
        "interview_questions": [
            "Design Amazon's recommendation system",
            "Tell me about a time you had to make a decision with incomplete data",
            "LRU Cache implementation",
            "Design a distributed logging system",
            "Tell me about a time you failed and what you learned",
        ],
        "certifications": ["AWS Certified Solutions Architect", "AWS Developer Associate", "AWS DevOps Engineer"],
        "avg_salary": "$160,000 - $320,000 (SDE I - Principal)",
    },
    "microsoft": {
        "name": "Microsoft Corporation",
        "overview": "Global technology company known for Windows, Azure, Office 365, Xbox, LinkedIn, and GitHub. HQ: Redmond, WA.",
        "culture": "Growth mindset culture under Satya Nadella. Collaborative, inclusive, and focused on empowerment.",
        "technologies": ["C#", ".NET", "Python", "TypeScript", "Azure", "SQL Server", "PowerShell", "Kubernetes", "React", "Go"],
        "required_skills": ["Cloud Architecture (Azure)", "System Design", "Object-Oriented Design", "Algorithms", "DevOps", "Security"],
        "interview_process": [
            "Online Application / LinkedIn",
            "Recruiter Screen",
            "Technical Phone Interview",
            "On-site / Virtual Loop: 4-5 rounds of Coding + Design + Behavioral",
        ],
        "interview_questions": [
            "Design a scalable notification system",
            "Implement a thread-safe singleton",
            "How would you design OneDrive?",
            "Tell me about a time you influenced without authority",
            "Serialize and deserialize a binary tree",
        ],
        "certifications": ["Azure Solutions Architect Expert", "Azure Developer Associate", "Azure AI Engineer"],
        "avg_salary": "$155,000 - $310,000 (SDE I - Principal)",
    },
    "meta": {
        "name": "Meta Platforms (formerly Facebook)",
        "overview": "Social media and technology giant operating Facebook, Instagram, WhatsApp, and Oculus VR. HQ: Menlo Park, CA.",
        "culture": "Move fast, be bold, focus on impact. Flat hierarchy with a focus on shipping features rapidly.",
        "technologies": ["Python", "PHP/Hack", "JavaScript/React", "C++", "PyTorch", "GraphQL", "Presto", "Cassandra", "TAO"],
        "required_skills": ["Algorithms", "System Design at Scale", "Distributed Systems", "Machine Learning", "React", "Data Modeling"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview (coding)",
            "On-site: 2 Coding + 1 System Design + 1 Behavioral",
        ],
        "interview_questions": [
            "Design Facebook's News Feed",
            "Clone a graph",
            "Design Instagram's photo storage system",
            "Find all connected components in a social graph",
            "Tell me about the most impactful project you've shipped",
        ],
        "certifications": ["Meta Certified Developer", "PyTorch Certified"],
        "avg_salary": "$170,000 - $360,000 (E3-E6)",
    },
    "apple": {
        "name": "Apple Inc.",
        "overview": "Global consumer electronics and software company. Known for iPhone, Mac, iPad, Apple Watch, App Store, and Apple Silicon. HQ: Cupertino, CA.",
        "culture": "Secretive, design-obsessed culture with extremely high quality bar. Small teams with big impact.",
        "technologies": ["Swift", "Objective-C", "Python", "C++", "Metal", "CoreML", "Xcode", "macOS/iOS frameworks"],
        "required_skills": ["iOS/macOS Development", "Swift", "System Programming", "Performance Optimization", "Security", "HCI"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview",
            "On-site: Multiple technical rounds + Design + Behavioral",
        ],
        "interview_questions": [
            "Design a contacts app",
            "Implement a concurrent download manager in Swift",
            "How does ARC work in Swift?",
            "Design Core Data's persistence layer",
            "Tell me about a time you improved app performance significantly",
        ],
        "certifications": ["Apple Certified Support Professional", "Apple Developer Program"],
        "avg_salary": "$165,000 - $330,000 (ICT2-ICT5)",
    },
    "netflix": {
        "name": "Netflix, Inc.",
        "overview": "Global streaming entertainment service with 260M+ subscribers. Known for its freedom & responsibility culture. HQ: Los Gatos, CA.",
        "culture": "Freedom & Responsibility: top talent, no process overhead, context not control, radical transparency.",
        "technologies": ["Java", "Python", "Node.js", "AWS", "Cassandra", "Kafka", "Hystrix", "Zuul", "Spinnaker", "React"],
        "required_skills": ["Distributed Systems", "Microservices", "Java/JVM", "Cloud (AWS)", "Data Engineering", "System Reliability"],
        "interview_process": [
            "Recruiter Screen",
            "Hiring Manager Screen",
            "Technical / Domain Expert Interviews (2-4 rounds)",
            "Reference Checks",
        ],
        "interview_questions": [
            "Design Netflix's recommendation engine",
            "How would you handle a global CDN failure?",
            "Design a real-time video transcoding pipeline",
            "How would you handle 100M concurrent streams?",
            "Tell me about a time you made a controversial technical decision",
        ],
        "certifications": ["AWS Certified", "Certified Kubernetes Administrator"],
        "avg_salary": "$185,000 - $400,000+ (E4-E6, high equity)",
    },
    "uber": {
        "name": "Uber Technologies, Inc.",
        "overview": "Global ride-hailing, food delivery (Uber Eats), and freight company. Operates in 70+ countries. HQ: San Francisco, CA.",
        "culture": "Challenger mindset, move fast, data-driven decision making. Post-Kalanick era: more collaborative and values-driven.",
        "technologies": ["Go", "Python", "Java", "Node.js", "MySQL", "Cassandra", "Kafka", "Kubernetes", "Presto", "M3"],
        "required_skills": ["Distributed Systems", "Real-time Systems", "Microservices", "Go or Java", "Database Design", "Maps/Geospatial"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview",
            "On-site: Coding + System Design + Behavioral",
        ],
        "interview_questions": [
            "Design Uber's surge pricing system",
            "How would you match drivers to riders at scale?",
            "Implement a rate limiter",
            "Design a real-time GPS tracking system",
            "Tell me about a system you built from scratch",
        ],
        "certifications": ["AWS Certified", "Certified Kubernetes Administrator"],
        "avg_salary": "$155,000 - $290,000 (L4-L6)",
    },
    "airbnb": {
        "name": "Airbnb, Inc.",
        "overview": "Global online marketplace for lodging and travel experiences. Operates in 220+ countries. HQ: San Francisco, CA.",
        "culture": "Belong Anywhere — mission-driven, diverse and inclusive, focused on creating belonging.",
        "technologies": ["Python", "Java", "JavaScript/React", "Ruby on Rails", "MySQL", "Druid", "Airflow", "Kubernetes", "Spark"],
        "required_skills": ["Full Stack Development", "Data Engineering", "System Design", "Machine Learning", "Search Systems"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview (coding)",
            "On-site: 2 Coding + 1 System Design + 2 Cross-functional",
        ],
        "interview_questions": [
            "Design Airbnb's search and filtering system",
            "Design a pricing algorithm for hosts",
            "Implement a calendar booking system",
            "How would you detect fraudulent bookings?",
            "Tell me about a product decision you influenced with data",
        ],
        "certifications": ["AWS Certified", "GCP Professional"],
        "avg_salary": "$160,000 - $300,000",
    },
    "linkedin": {
        "name": "LinkedIn (Microsoft subsidiary)",
        "overview": "World's largest professional network with 950M+ members. Offers job search, networking, and learning. HQ: Sunnyvale, CA.",
        "culture": "Transformation culture: members first, relationships matter, be open, honest and constructive.",
        "technologies": ["Java", "Scala", "Python", "Kafka", "Samza", "Espresso", "Voldemort", "Hadoop", "React", "Rest.li"],
        "required_skills": ["Distributed Systems", "Search & Relevance", "Java/Scala", "Big Data", "ML for Recommendations"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Screen",
            "On-site: Coding + System Design + Behavioral",
        ],
        "interview_questions": [
            "Design LinkedIn's People You May Know feature",
            "How would you build a job recommendation system?",
            "Design LinkedIn's newsfeed",
            "How do you rank search results for jobs?",
            "Tell me about a complex data pipeline you built",
        ],
        "certifications": ["Azure Certified", "Hadoop/Spark Certifications"],
        "avg_salary": "$155,000 - $290,000",
    },
    "spotify": {
        "name": "Spotify Technology S.A.",
        "overview": "World's largest audio streaming platform with 600M+ users, 230M+ subscribers. HQ: Stockholm, Sweden.",
        "culture": "Autonomous squads (teams), tribes, chapters, guilds. High psychological safety and experimentation culture.",
        "technologies": ["Python", "Java", "Scala", "Google Cloud", "BigQuery", "Dataflow", "Kafka", "Cassandra", "React"],
        "required_skills": ["Backend Development", "Data Engineering", "Machine Learning", "Recommendation Systems", "A/B Testing"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview",
            "Home assignment (some roles)",
            "On-site: Technical + Cultural interviews",
        ],
        "interview_questions": [
            "Design Spotify's Discover Weekly playlist generation",
            "How would you build a real-time music charts system?",
            "Design Spotify's radio feature",
            "How do you handle audio streaming at 100M concurrent listeners?",
            "Tell me about an A/B test you ran and what you learned",
        ],
        "certifications": ["GCP Professional", "Spark Certifications"],
        "avg_salary": "$140,000 - $260,000",
    },
    "tesla": {
        "name": "Tesla, Inc.",
        "overview": "Electric vehicle and clean energy company. Makes Model S/3/X/Y, Semi, Cybertruck, Powerwall, and Solar Roof. HQ: Austin, TX.",
        "culture": "Mission-driven (sustainable energy), fast-paced, high-ownership, minimal bureaucracy. Elon Musk's 'move fast' ethos.",
        "technologies": ["C++", "Python", "CUDA", "PyTorch", "Autopilot", "CAN bus", "ROS", "Rust", "Embedded Linux"],
        "required_skills": ["Embedded Systems", "C++", "Computer Vision", "Deep Learning", "Real-time Systems", "CUDA/GPU Programming"],
        "interview_process": [
            "Recruiter Screen",
            "Technical Phone Interview",
            "On-site: Technical + Hands-on coding + Behavioral",
        ],
        "interview_questions": [
            "How would you design an obstacle detection algorithm?",
            "Design a fail-safe system for autonomous driving",
            "How would you optimize inference speed for a CNN on edge hardware?",
            "Explain how you'd handle sensor fusion (camera + radar + lidar)",
            "Tell me about a time you delivered under extreme time pressure",
        ],
        "certifications": ["NVIDIA Deep Learning Institute", "Embedded Systems Certifications"],
        "avg_salary": "$140,000 - $280,000",
    },
}

CAREER_GUIDANCE = {
    "software_engineer": {
        "roadmap": [
            "Master CS fundamentals: algorithms, data structures, OS, networking",
            "Pick a primary language deeply (Python, Java, or JavaScript)",
            "Learn a web framework (FastAPI, Spring Boot, Express, etc.)",
            "Study databases: SQL (PostgreSQL) + NoSQL (MongoDB/Redis)",
            "Learn Git, Docker, CI/CD pipelines",
            "Practice LeetCode: 100+ problems (easy+medium) for FAANG",
            "Build 2-3 strong portfolio projects with GitHub READMEs",
            "Contribute to open source or build a SaaS project",
            "Learn system design for senior roles",
            "Network: LinkedIn, meetups, GitHub contributions",
        ],
        "certifications": ["AWS Developer Associate", "Google Cloud Associate", "Kubernetes CKA"],
        "salary_range": "$85,000 - $350,000 depending on level/company",
    },
    "data_scientist": {
        "roadmap": [
            "Master statistics: probability, hypothesis testing, regression",
            "Python data stack: NumPy, Pandas, Matplotlib, Seaborn",
            "Machine learning: scikit-learn, supervised/unsupervised learning",
            "Deep learning: TensorFlow or PyTorch",
            "SQL: complex queries, window functions, CTEs",
            "Data visualization: Tableau, Power BI, or Plotly",
            "MLOps: model deployment, monitoring, MLflow",
            "Big Data: Spark, Hadoop fundamentals",
            "NLP, Computer Vision, or Recommender Systems for specialization",
            "Kaggle competitions + portfolio projects",
        ],
        "certifications": ["TensorFlow Developer Certificate", "AWS ML Specialty", "Google ML Engineer"],
        "salary_range": "$95,000 - $290,000",
    },
    "product_manager": {
        "roadmap": [
            "Understand product thinking: user research, personas, journey maps",
            "Learn agile/scrum methodologies",
            "Master data analysis: SQL, A/B testing, metrics",
            "Study product strategy: frameworks like RICE, OKRs, MoSCoW",
            "Build communication skills: PRDs, roadmaps, stakeholder management",
            "Learn basic UX/UI design principles (Figma)",
            "Understand business metrics: ARR, MRR, LTV, CAC, NPS",
            "Get industry domain knowledge (fintech, healthtech, SaaS, etc.)",
            "Build case studies from existing PM interview prep resources",
            "Network with PMs on LinkedIn",
        ],
        "certifications": ["AIPMM CPM", "Pragmatic Marketing Certified", "CSPO"],
        "salary_range": "$110,000 - $280,000",
    },
    "devops": {
        "roadmap": [
            "Linux fundamentals and shell scripting",
            "Networking: TCP/IP, DNS, HTTP, Load Balancing",
            "Infrastructure as Code: Terraform, Ansible",
            "Containers: Docker, Kubernetes (CKA certification)",
            "CI/CD: Jenkins, GitHub Actions, GitLab CI",
            "Cloud platforms: AWS, GCP, or Azure (get certified!)",
            "Monitoring: Prometheus, Grafana, ELK Stack",
            "Security: IAM, secrets management, vulnerability scanning",
            "Site Reliability Engineering (SRE) principles",
            "Learn GitOps: ArgoCD, Flux",
        ],
        "certifications": ["CKA", "AWS DevOps Professional", "HashiCorp Terraform Associate"],
        "salary_range": "$110,000 - $270,000",
    },
}

INTERVIEW_PREP = {
    "behavioral": [
        "Tell me about yourself.",
        "Describe a challenging project and how you overcame obstacles.",
        "Tell me about a time you disagreed with your manager.",
        "How do you prioritize tasks when everything feels urgent?",
        "Describe a time you failed and what you learned.",
        "Tell me about a time you showed leadership without authority.",
        "Give an example of when you had to learn something quickly.",
        "Describe a time you improved a process significantly.",
        "How do you handle ambiguous requirements?",
        "Tell me about a time you received critical feedback.",
    ],
    "technical_coding": [
        "Reverse a linked list (iterative + recursive).",
        "Find all permutations of a string.",
        "Implement BFS and DFS on a graph.",
        "Two Sum / Three Sum variations.",
        "Merge intervals.",
        "Detect cycle in a linked list.",
        "Implement LRU Cache.",
        "Word break problem (DP).",
        "Number of islands.",
        "Serialize and deserialize a binary tree.",
    ],
    "system_design": [
        "Design a URL shortener (TinyURL).",
        "Design a scalable notification system.",
        "Design Twitter's trending topics.",
        "Design a distributed key-value store.",
        "Design a ride-sharing backend (Uber).",
        "Design a video streaming platform (YouTube).",
        "Design a web crawler.",
        "Design a rate limiter.",
        "Design a real-time collaborative editor (Google Docs).",
        "Design a search autocomplete system.",
    ],
}


def search_company(query: str) -> dict | None:
    query_lower = query.lower().strip()
    for key, data in COMPANY_DATABASE.items():
        if key in query_lower or key.replace("_", " ") in query_lower:
            return data
    # partial match
    for key, data in COMPANY_DATABASE.items():
        if any(word in query_lower for word in key.split("_")):
            return data
    return None


def get_career_guidance(role_query: str) -> dict | None:
    role_lower = role_query.lower()
    for key, data in CAREER_GUIDANCE.items():
        if key.replace("_", " ") in role_lower or any(w in role_lower for w in key.split("_")):
            return {"role": key.replace("_", " ").title(), **data}
    return None


def get_interview_questions(category: str = "behavioral") -> list[str]:
    return INTERVIEW_PREP.get(category, INTERVIEW_PREP["behavioral"])


def answer_company_question(question: str) -> str | None:
    company_data = search_company(question)
    if not company_data:
        return None

    q = question.lower()
    name = company_data["name"]

    if any(w in q for w in ["interview", "hiring", "process", "round"]):
        steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(company_data["interview_process"]))
        return f"**{name} Interview Process:**\n{steps}"

    if any(w in q for w in ["skill", "require", "need", "tech", "stack", "technology"]):
        tech = ", ".join(company_data["technologies"][:8])
        skills = ", ".join(company_data["required_skills"][:5])
        return (f"**{name} Tech Stack:** {tech}\n\n"
                f"**Required Skills:** {skills}")

    if any(w in q for w in ["question", "ask", "prepare", "common"]):
        qs = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(company_data["interview_questions"][:5]))
        return f"**{name} Common Interview Questions:**\n{qs}"

    if any(w in q for w in ["salary", "pay", "compensation", "ctc"]):
        return f"**{name} Salary Range:** {company_data['avg_salary']}"

    if any(w in q for w in ["cert", "certif"]):
        certs = ", ".join(company_data["certifications"])
        return f"**{name} Valued Certifications:** {certs}"

    # Default: full overview
    return (
        f"**{name}**\n\n"
        f"📋 **Overview:** {company_data['overview']}\n\n"
        f"🌐 **Culture:** {company_data['culture']}\n\n"
        f"💻 **Key Technologies:** {', '.join(company_data['technologies'][:6])}\n\n"
        f"🎯 **Required Skills:** {', '.join(company_data['required_skills'][:5])}\n\n"
        f"💰 **Salary Range:** {company_data['avg_salary']}"
    )
