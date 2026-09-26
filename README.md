# SkillSetu — AI-Powered Longitudinal Skilling Outcomes Tracker

**Smart India Hackathon 2026 · Problem Statement SIH26135 · Government of Maharashtra · Theme: Miscellaneous**
**Team:** The Gradient Crew — Axis Institute of Technology & Management, Kanpur

**Live demo:** https://skillsetu-sih26135.vercel.app
**API:** https://skillsetu-sih26135.onrender.com (interactive docs at `/docs`)

---

## The problem

Skilling programmes record enrolment, attendance and certification, but lose track of trainees once training ends. Nobody reliably knows who got a job, who became self-employed, how wages progressed, or *why* a trainee is still unemployed. Without these longitudinal outcomes, the state cannot compare providers, fix courses or target investment.

## Our solution

SkillSetu follows each trainee from enrolment to real employment outcomes with consent-based, low-burden follow-ups, and uses AI to explain the gaps.

| Module | What it does |
|---|---|
| **Consent-based registration** | Trainee opts in explicitly; a 30 / 90 / 180-day follow-up schedule is generated from the consent timestamp. |
| **Follow-up + AI reasoning** | When a trainee reports "still searching", Groq AI classifies the non-placement reason from their free-text reply and recommends a policy action. |
| **Skill Gap Self-Assessment** | A 10-question, programme-specific test scored per skill area. Groq AI writes a personal skill-gap analysis and upskilling plan. Falls back to an offline analysis if the AI service is unavailable. |
| **Analytics command center** | District, programme and provider views: employment conversion, outcome breakdown, attrition reasons and an AI policy insight. |

Programmes covered in the demo: CNC Machine Operator, Full Stack Web Developer, Healthcare General Duty Assistant, Automotive Service Technician.

## Architecture

```
Browser (Vercel: HTML + Tailwind + Chart.js)
        │  fetch (JSON)
        ▼
FastAPI backend (Render) ──► Groq API (openai/gpt-oss-120b)
        │
        ▼
SQLAlchemy (SQLite for the demo, PostgreSQL via DATABASE_URL)
```

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/trainees` | Validate consent and return the 30/90/180-day follow-up schedule |
| `POST` | `/api/v1/ai/analyze` | Classify a non-placement reason from trainee feedback |
| `POST` | `/api/v1/assessment/analyze` | Skill-gap analysis for a scored self-assessment (returns `503` if the AI is unavailable) |

The readiness level (Job-Ready ≥ 75%, Nearly Job-Ready ≥ 50%, Needs Upskilling below that) is calculated in code, never by the LLM. The AI only writes the explanation.

## Run locally

```bash
cd backend
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn app.main:app --reload
```

Then open `frontend/index.html` in a browser (it calls the API URL set in `API_BASE_URL` inside the page script).

With Docker:

```bash
GROQ_API_KEY=your_key_here docker compose up --build
```

## Privacy by design

- No tracking without explicit opt-in consent.
- Self-assessment results are private to the trainee; only anonymised, aggregated skill gaps are used for course improvement, never as a hiring filter.
- Input sizes are validated and capped on the backend.

## Roadmap

1. **Gateway scale:** SMS / IVR follow-ups through a bulk messaging gateway (e.g. MSG91) for 100k+ trainees.
2. **Verified outcomes:** EPFO employer matching and DigiLocker-style persistent IDs to handle changed phone numbers and locations.
3. **Persistent storage:** PostgreSQL records for trainees, follow-ups and assessments feeding the live dashboard.
4. **Multi-state rollout:** open API standards for MSDE integration.
