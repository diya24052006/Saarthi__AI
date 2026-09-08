import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# --------------------------------------------------
# LOAD ENVIRONMENT
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY was not found in .env")


# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

client = Groq(api_key=GROQ_API_KEY)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

ANALYZER_PROMPT = """
You are the situation understanding component of AI Saarthi.

AI Saarthi is a Bhagavad Gita inspired emotional guidance system.

Your job is NOT to diagnose mental illnesses.

Analyze the user's message and identify:

1. emotion
2. situation
3. need
4. intent
5. safety_level
6. semantic_query

Important:

- Do not diagnose the user.
- Do not assume a medical condition.
- Use simple emotional descriptions such as:
  sadness, loneliness, fear, anger, confusion,
  guilt, grief, disappointment, stress,
  insecurity, frustration, hope, etc.
- If multiple emotions are present, select the dominant one.
- Situation should describe what is happening in the user's life.
- Need should describe what kind of support or guidance the person appears to be seeking.
- Intent describes what the user wants from AI Saarthi.
- semantic_query should transform the situation into a concise
  conceptual search query useful for retrieving relevant
  Bhagavad Gita passages.

Safety levels:

normal:
ordinary emotional/life difficulty.

elevated:
strong emotional distress, hopelessness, severe isolation,
or language suggesting the person may be struggling significantly.

crisis:
explicit suicidal thoughts, self-harm intentions,
desire to die, immediate danger, or inability to stay safe.

Return ONLY valid JSON.

Use exactly this structure:

{
    "emotion": "...",
    "situation": "...",
    "need": "...",
    "intent": "...",
    "safety_level": "...",
    "semantic_query": "..."
}
"""


# --------------------------------------------------
# ANALYZE USER MESSAGE
# --------------------------------------------------

def analyze_situation(user_message: str):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": ANALYZER_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.1,
        max_tokens=400
    )

    result = response.choices[0].message.content.strip()

    # ----------------------------------------------
    # Remove accidental markdown code fences
    # ----------------------------------------------

    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    # ----------------------------------------------
    # Convert JSON string → Python dictionary
    # ----------------------------------------------

    try:
        analysis = json.loads(result)

    except json.JSONDecodeError:
        print("\nCould not parse analyzer response:")
        print(result)

        return {
            "emotion": "unknown",
            "situation": user_message,
            "need": "guidance",
            "intent": "seeking guidance",
            "safety_level": "normal",
            "semantic_query": user_message
        }

    return analysis


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("AI SAARTHI - SITUATION ANALYZER")
    print("=" * 70)

    user_message = input("\nTell Saarthi what you're going through:\n> ")

    analysis = analyze_situation(user_message)

    print("\nUNDERSTANDING")
    print("-" * 70)

    print(json.dumps(
        analysis,
        indent=4,
        ensure_ascii=False
    ))