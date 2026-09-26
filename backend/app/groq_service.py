import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

GROQ_MODEL = "openai/gpt-oss-120b"


class AIServiceError(Exception):
    """Raised when the Groq service is unavailable or returns an unusable response."""


def get_groq_client():
    key = os.getenv("GROQ_API_KEY")

    if not key or key == "dummy_key_for_demo":
        logger.error("GROQ_API_KEY is missing or still set to the demo placeholder.")
        return None

    return Groq(api_key=key)


def analyze_trainee_feedback_with_groq(feedback_text: str):
    client = get_groq_client()

    if not client:
        return {
            "primary_bottleneck": "Groq API Configuration Error",
            "confidence_score": "0%",
            "recommended_action": "Groq API key is not configured correctly on the server."
        }

    system_prompt = """You are an AI policy advisor for the Government of Maharashtra skilling department (SIH26135).

Analyze the trainee's feedback regarding why they haven't secured employment.

You MUST respond ONLY with a valid JSON object matching this exact schema:

{
    "primary_bottleneck": "A short 3-5 word label of the root issue",
    "confidence_score": "e.g. 94.5%",
    "recommended_action": "A specific, high-impact policy/curriculum recommendation for state officials"
}

Do not include markdown codeblocks, explanation, or extra text."""

    try:
        logger.info("Sending trainee feedback to Groq AI for analysis.")

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Trainee Feedback: {feedback_text}"
                }
            ],
            temperature=0.2,
            max_tokens=600,
            reasoning_effort="low",
            response_format={"type": "json_object"}
        )

        raw_content = completion.choices[0].message.content

        logger.info("Groq AI response received successfully.")

        return json.loads(raw_content)

    except Exception as e:
        logger.exception("GROQ AI REQUEST FAILED")

        return {
            "primary_bottleneck": "AI Service Error",
            "confidence_score": "0%",
            "recommended_action": "The Groq AI service request failed. Check the Render logs for the exact error."
        }

def _clean_list(value, limit=5):
    """Keep only non-empty strings from an LLM-provided list."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, (str, int, float)) and str(item).strip()][:limit]


def analyze_self_assessment_with_groq(payload: dict) -> dict:
    """Turn a scored self-assessment into a personalised skill-gap analysis.

    Scoring is deterministic and done before this call; the LLM only writes the
    narrative (summary, strengths, gaps, modules, next step).
    Raises AIServiceError if Groq is not configured or returns an unusable answer.
    """
    client = get_groq_client()
    if not client:
        raise AIServiceError("Groq API key is not configured.")

    system_prompt = """You are a skills-assessment counsellor for the Government of Maharashtra's skilling programmes (SIH26135 - SkillSetu).

You receive a trainee's self-assessment result: programme, district, overall score, per-skill scores and the topics they got wrong.
Write a short, encouraging, practical skill-gap analysis in simple English that a trainee can understand.

Rules:
- Base every statement ONLY on the scores and missed topics provided. Do not invent scores.
- A skill with 75% or more is a strength; below 75% is a gap.
- Recommended modules must be concrete short courses (name + approximate hours) that fix the listed gaps.
- Keep each list item under 20 words. Maximum 4 items per list.

Respond ONLY with a valid JSON object using exactly this schema:
{
    "summary": "2 sentences on overall readiness and the biggest gap",
    "strengths": ["..."],
    "skill_gaps": ["..."],
    "recommended_modules": ["..."],
    "next_step": "One specific action for the next 30 days"
}"""

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.3,
            max_tokens=900,
            reasoning_effort="low",
            response_format={"type": "json_object"},
        )
        data = json.loads(completion.choices[0].message.content)
    except Exception as exc:
        logger.exception("GROQ SELF-ASSESSMENT REQUEST FAILED")
        raise AIServiceError("Groq request failed.") from exc

    summary = str(data.get("summary", "")).strip() if isinstance(data, dict) else ""
    next_step = str(data.get("next_step", "")).strip() if isinstance(data, dict) else ""
    if not summary or not next_step:
        raise AIServiceError("Groq returned an incomplete analysis.")

    return {
        "summary": summary,
        "strengths": _clean_list(data.get("strengths")),
        "skill_gaps": _clean_list(data.get("skill_gaps")),
        "recommended_modules": _clean_list(data.get("recommended_modules")),
        "next_step": next_step,
    }
