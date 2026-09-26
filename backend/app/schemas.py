from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class TraineeRegistrationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(..., min_length=1, max_length=80, examples=["Rahul Patil"])
    phone_number: str = Field(..., pattern=r"^[6-9]\d{9}$", examples=["9876543210"])
    programme: str = Field(..., min_length=1, max_length=120, examples=["CNC Machine Operator (PMKVY)"])
    district: str = Field(..., min_length=1, max_length=60, examples=["Pune"])
    gender: Optional[str] = Field(None, max_length=30, examples=["Female"])
    age_group: Optional[str] = Field(None, max_length=10, examples=["18-24"])
    consent_given: bool = Field(..., examples=[True])


class AIAnalysisRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trainee_feedback: str = Field(..., max_length=2000, examples=["Companies in Pune want advanced automation experience."])
    employment_status: str = Field(..., max_length=30, examples=["searching"])


class SkillScore(BaseModel):
    skill: str = Field(..., min_length=1, max_length=60)
    correct: int = Field(..., ge=0, le=50)
    total: int = Field(..., ge=1, le=50)


class SelfAssessmentRequestSchema(BaseModel):
    candidate_name: Optional[str] = Field(None, max_length=60, examples=["Sneha Jadhav"])
    programme: str = Field(..., min_length=1, max_length=120, examples=["CNC Machine Operator"])
    district: str = Field(..., min_length=1, max_length=60, examples=["Pune"])
    correct_answers: int = Field(..., ge=0, le=100)
    total_questions: int = Field(..., ge=1, le=100)
    skill_scores: List[SkillScore] = Field(..., min_length=1, max_length=10)
    missed_topics: List[ShortText] = Field(default_factory=list, max_length=20)


class SelfAssessmentResponseSchema(BaseModel):
    readiness_level: str
    score_percent: int
    summary: str
    strengths: List[str]
    skill_gaps: List[str]
    recommended_modules: List[str]
    next_step: str
    model: str
