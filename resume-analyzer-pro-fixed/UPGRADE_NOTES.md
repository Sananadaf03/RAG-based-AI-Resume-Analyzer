# Resume Analyzer Pro — Upgrade Notes

## v5 — ATS Scoring Accuracy Fix (2026-05-18)

### Problem fixed
The ATS score was consistently too low, including when re-analyzing an already-optimized resume.
Root causes:

1. **Raw scores were never calibrated.**  
   Sentence-transformer cosine similarities typically land in the 0.25–0.65 range for
   professional text, not 0.8–1.0. The old code used raw values directly, making every
   resume look like a poor match.

2. **Keyword matching was unreliable.**  
   TF-IDF was fitted on only the resume (single document), so the vocabulary was biased
   and JD keywords that existed in the resume were still scored as 0.

3. **Skill extraction missed synonyms.**  
   "k8s" wasn't recognized as Kubernetes; "sklearn" wasn't recognized as scikit-learn;
   "Node.js" wasn't matched when written as "nodejs". Resume skills were systematically
   under-counted.

4. **No partial credit or bonus for extra skills.**  
   A candidate with 20 bonus skills received the same score as one with 0.

5. **Improvement estimation was too conservative.**  
   The estimated new ATS score after optimization was capped too aggressively.

### Changes in v5

#### `modules/analyzer.py`
- Added **per-component score floors** (calibration): each component is rescaled from
  its raw `[0, 1]` range to a calibrated `[floor, 1]` range that reflects real-world
  baseline competence.
- **Rewritten keyword extraction** (`extract_keywords_tfidf`): now fits TF-IDF on **both**
  the resume and JD so the vocabulary is shared — resume terms correctly match against JD terms.
- **Synonym expansion** (`SKILL_SYNONYMS` dict + `_resolve_synonyms`): 30+ aliases resolve
  before skill matching (e.g., k8s→kubernetes, sklearn→scikit-learn, nodejs→node.js).
- **Longest-match-first** skill scanning prevents sub-string collisions.
- **Partial credit + extra-skill bonus** in `skill_match_pct`.
- Improved experience heuristic: date ranges (2019–present) now contribute to years count.
- Higher education and experience defaults when JD doesn't state requirements.
- Confidence score floored at 35% so it never shows 0% for a real resume.

#### `modules/retriever.py`
- `get_overall_similarity`: now averages over **multiple chunks** from each document
  (rather than truncating both to 2000 chars) for a more stable semantic score. Uses
  top-half percentile average — more generous than mean, more stable than max.

#### `modules/optimizer.py`
- `_calculate_overall_improvement`: expanded logic accounts for word-count growth
  (longer optimized text → more semantic coverage), separate skill-gap and keyword-gap
  bonuses, and ATS-score-band bonuses.
- `estimated_new_ats_score` multiplier raised from 0.60 → 0.75 to better reflect
  the actual gains from skill injection and bullet rewriting.

### Score interpretation guide
| Score   | Meaning                                            |
|---------|----------------------------------------------------|
| < 50%   | Needs significant tailoring for this role          |
| 50–64%  | Moderate match — target missing skills & keywords  |
| 65–74%  | Good match — refine bullets and add metrics        |
| 75–84%  | Strong match — polish summary and format           |
| 85%+    | Excellent match — submit with confidence           |
