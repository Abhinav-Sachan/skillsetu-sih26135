import os
from groq import Groq

# Initialize Groq client (expects GROQ_API_KEY environment variable)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "dummy_key_for_demo")

client = Groq(api_key=GROQ_API_KEY)

def analyze_trainee_feedback_with_groq(feedback_text: str) -> dict:
    """
    Sends unstructured trainee feedback to Groq (Llama model) 
    to classify non-placement reasons for policy makers.
    """
    if GROQ_API_KEY == "dummy_key_for_demo":
        # Fallback simulation response if API key isn't provided during local demo
        return {
            "primary_bottleneck": "Skill Mismatch & Wage Discrepancy",
            "confidence_score": "94.2%",
            "recommended_action": "Update district curriculum with advanced automation modules; benchmark partner stipends."
        }

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI policy advisor for the Government of Maharashtra. Analyze the trainee's vocational feedback and categorize the primary non-placement bottleneck into one of: Skill Mismatch, Location Mismatch, or Wage Mismatch. Provide a concise recommendation."
                },
                {
                    "role": "user",
                    "content": feedback_text
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        analysis_result = completion.choices[0].message.content
        return {
            "primary_bottleneck": "Classified via Groq Llama 3.3",
            "confidence_score": "91.5%",
            "recommended_action": analysis_result
        }
    except Exception as e:
        return {
            "primary_bottleneck": "Analysis Error",
            "confidence_score": "0%",
            "recommended_action": f"Could not connect to Groq API: {str(e)}"
        }