import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


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
            model="llama-3.1-8b-instant",
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
            max_tokens=250,
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