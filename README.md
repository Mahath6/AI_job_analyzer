# AI Resume Analyzer & Job Recommendation System

Upload a PDF, DOCX or TXT resume, choose a target role (or paste a job description) and get:
a match score, detected skills by category, top-3 recommended roles, missing skills,
a week-by-week learning roadmap, resume tips and a downloadable report.

## How it works
Upload -> extract text (pypdf / python-docx) -> clean -> skill extraction (dictionary + aliases)
-> role matching -> skill gap -> roadmap -> Streamlit dashboard

**Score (0-100)** = 75% skill coverage + 25% TF-IDF cosine similarity.
Required skills weigh 1.0 and nice-to-have skills weigh 0.5 in coverage.

## Architecture
![Architecture](docs/architecture.png)

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests
```bash
python tests/run_tests.py
```
Runs 9 sample resumes (PDF, DOCX, TXT) and writes `tests/evaluation_sheet.csv`.
Current result: strict top-1 8/9, lenient top-1 9/9, top-3 9/9. It also checks symbol
handling (C++, C#), word boundaries (no "sql" inside "postgresql"), dictionary consistency
and score consistency (adding relevant skills raises the score).

## Customise
- `data/job_roles.csv`: add roles (skill names must exist in the dictionary; the test checks this).
- `data/skill_dictionary.csv`: add skills, aliases (`|` separated), weeks and learning hint.
- Weights and the TF-IDF scale are constants at the top of `job_matcher.py`.

## Responsible AI
- Guidance tool only, not for hiring or rejecting people.
- Email, phone and URLs are stripped before analysis. Gender, age, religion, nationality,
  photo, marital status and disability are never scored.
- Files are processed in memory and never stored.
- A missing keyword does not mean missing ability. Scores are estimates.

## Known limitations
- Keyword matching misses skills written in unusual wording (add aliases to fix).
- Scanned/image PDFs are not supported (no OCR).
- `resume_d_fresher_web.txt` expects Backend Developer, but Python Developer ranks first
  (Flask implies Python and the resume meets every required Python Developer skill; it
  lacks Docker for Backend Developer). Both are reasonable, so the test sheet lists
  Python Developer as "also acceptable".
- The 9 sample resumes are small and were written for this project, so accuracy is
  optimistic. A real evaluation needs 15+ anonymised resumes from different templates.

## Project documents
- `docs/PROJECT_REPORT.md` - short project report
- `docs/architecture.png` - workflow / architecture diagram (`python docs/make_diagram.py` regenerates it)
- `docs/DEMO_VIDEO_SCRIPT.md` - script for the demonstration video
- `docs/GITHUB_AND_DEPLOY_STEPS.md` - GitHub upload and Streamlit Cloud deployment

## Deploy (Streamlit Community Cloud)
Push to GitHub, then at share.streamlit.io choose the repo and `app.py`.
