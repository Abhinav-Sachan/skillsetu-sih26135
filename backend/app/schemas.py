from pydantic import BaseModel, Field

class TraineeRegistrationSchema(BaseModel):
    full_name: str = Field(..., example="Rahul Patil")
    phone_number: str = Field(..., example="9876543210")
    programme: str = Field(..., example="CNC Machine Operator (PMKVY)")
    district: str = Field(..., example="Pune")
    consent_given: bool = Field(..., example=True)

    class Config:
        from_attributes = True

class AIAnalysisRequestSchema(BaseModel):
    trainee_feedback: str = Field(..., example="Companies in Pune want advanced automation experience.")
    employment_status: str = Field(..., example="searching")

    class Config:
        from_attributes = True