from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.schemas import (
    TraineeRegistrationSchema,
    AIAnalysisRequestSchema,
    SelfAssessmentRequestSchema,
    SelfAssessmentResponseSchema,
)
from app.groq_service import (
    GROQ_MODEL,
    AIServiceError,
    analyze_trainee_feedback_with_groq,
    analyze_self_assessment_with_groq,
)

FOLLOW_UP_DAYS = (30, 90, 180)

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillSetu API",
    description="Backend API for longitudinal skilling outcomes and Groq AI reasoning (SIH26135)",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "SkillSetu",
        "hackathon": "Smart India Hackathon 2026",
        "problem_statement": "SIH26135",
        "agency": "Govt. of Maharashtra"
    }

@app.post("/api/v1/trainees")
def register_trainee(data: TraineeRegistrationSchema, db: Session = Depends(get_db)):
    """
    Registers a trainee with explicit consent and queues them for longitudinal tracking.
    """
    if not data.consent_given:
        raise HTTPException(
            status_code=400, 
            detail="Explicit consent is legally mandatory for longitudinal outcome tracking under state guidelines."
        )
    
    # Roadmap: persist the record in PostgreSQL and hand the schedule to the SMS/IVR worker.
    consent_at = datetime.now(timezone.utc)
    return {
        "success": True,
        "message": "Consent validated. Follow-up schedule generated for day 30, 90 and 180.",
        "registered_data": {
            "full_name": data.full_name,
            "programme": data.programme,
            "district": data.district,
            "gender": data.gender,
            "age_group": data.age_group,
            "consent_status": "Opted-In",
            "consent_timestamp": consent_at.isoformat(),
        },
        "follow_up_schedule": [
            {"day": d, "due_date": (consent_at + timedelta(days=d)).date().isoformat()} for d in FOLLOW_UP_DAYS
        ],
    }

@app.post("/api/v1/ai/analyze")
def analyze_employment_bottleneck(data: AIAnalysisRequestSchema):
    """
    Analyzes unstructured trainee feedback using the Groq API (openai/gpt-oss-120b)
    to categorize non-placement reasons for policymakers.
    """
    if data.employment_status != "searching":
        return {
            "primary_bottleneck": "None (Employed / Self-Employed)",
            "confidence_score": "100%",
            "recommended_action": "No intervention required. Record marked as successfully converted."
        }

    # Call Groq AI service layer
    analysis_result = analyze_trainee_feedback_with_groq(data.trainee_feedback)
    return analysis_result


def readiness_level(score_percent: int) -> str:
    """Deterministic readiness band (never decided by the LLM)."""
    if score_percent >= 75:
        return "Job-Ready"
    if score_percent >= 50:
        return "Nearly Job-Ready"
    return "Needs Upskilling"


@app.post("/api/v1/assessment/analyze", response_model=SelfAssessmentResponseSchema)
def analyze_self_assessment(data: SelfAssessmentRequestSchema):
    """
    Skill Gap Self-Assessment: takes the scored test (per-skill correct/total)
    and returns a personalised skill-gap analysis written by Groq AI.
    Returns HTTP 503 if the AI service is unavailable so the frontend can
    fall back to its offline analysis.
    """
    if data.correct_answers > data.total_questions:
        raise HTTPException(status_code=422, detail="correct_answers cannot exceed total_questions.")
    if any(s.correct > s.total for s in data.skill_scores):
        raise HTTPException(status_code=422, detail="A skill score has more correct answers than questions.")

    score_percent = round(100 * data.correct_answers / data.total_questions)
    level = readiness_level(score_percent)

    payload = {
        "programme": data.programme,
        "district": data.district,
        "candidate_name": data.candidate_name or "the trainee",
        "overall_score": f"{data.correct_answers}/{data.total_questions} ({score_percent}%)",
        "readiness_level": level,
        "skill_scores": [
            {"skill": s.skill, "score": f"{s.correct}/{s.total}", "percent": round(100 * s.correct / s.total)}
            for s in data.skill_scores
        ],
        "missed_topics": data.missed_topics,
    }

    try:
        analysis = analyze_self_assessment_with_groq(payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {
        "readiness_level": level,
        "score_percent": score_percent,
        "model": GROQ_MODEL,
        **analysis,
    }
