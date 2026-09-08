import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from scripts.search import search_gita
from scripts.analyzer import analyze_situation
from scripts.safety import analyze_safety, get_safety_response
# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found.\n"
        "Please add it to your .env file."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# AI SAARTHI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are AI Saarthi, a compassionate guidance assistant
inspired by the Bhagavad Gita.

Your purpose is to help people reflect on difficult life
situations using relevant teachings from the Bhagavad Gita
and practical everyday guidance.

You are NOT a licensed therapist, psychologist, psychiatrist,
doctor, or emergency service.

IMPORTANT RULES:

1. Do not diagnose mental-health conditions.

2. Do not claim that a specific Gita verse says something
   unless that idea is supported by the retrieved context.

3. Never invent, fabricate, or hallucinate Bhagavad Gita verses.

4. Use the retrieved Gita passages as your primary source
   for spiritual guidance.

5. Explain the teaching in simple modern language.

6. Connect the teaching to the user's situation.

7. Give practical and realistic suggestions where appropriate.

8. Do not preach or force religious beliefs on the user.

9. Be compassionate, respectful, and non-judgmental.

10. If the user is experiencing significant emotional distress,
    respond gently and encourage appropriate human support.

11. If the safety system identifies a crisis, do not provide
    ordinary Gita-based guidance. The safety response should
    take priority.

A useful response structure is:

- Acknowledge what the person is experiencing.
- Explain the relevant Gita teaching from the retrieved context.
- Connect it to their situation.
- Give practical next steps.
- End with a gentle reflection or question when appropriate.

Keep the response conversational rather than sounding like
a textbook.
"""


# ============================================================
# BUILD GITA CONTEXT
# ============================================================

def build_context(results):

    context_parts = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
PASSAGE {i}

Chapter: {result.get("chapter")}
Chapter Title: {result.get("chapter_title")}
Verse: {result.get("verse")}
Speaker: {result.get("speaker")}

Text:
{result.get("text")}

Source:
{result.get("source")}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(
    user_message,
    analysis,
    results
):

    context = build_context(results)

    user_prompt = f"""
The user has shared the following situation:

USER MESSAGE:
{user_message}


SITUATION ANALYSIS:

Emotion:
{analysis.get("emotion")}

Situation:
{analysis.get("situation")}

Need:
{analysis.get("need")}

Intent:
{analysis.get("intent")}

Safety Level:
{analysis.get("safety_level")}


RETRIEVED BHAGAVAD GITA CONTEXT:

{context}


Now provide a compassionate and practical response.

Use the retrieved Gita context carefully.

Do not invent verses or teachings that are not supported
by the retrieved passages.
"""

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.4,

        max_tokens=800
    )

    return response.choices[0].message.content.strip()


# ============================================================
# MAIN AI SAARTHI PIPELINE
# ============================================================

def run_saarthi(user_message):

    print("\n" + "=" * 70)
    print("🚨 SAFETY CHECK")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1: SAFETY
    # --------------------------------------------------------

    safety = analyze_safety(user_message)

    print(f"Safety Level: {safety['safety_level']}")
    print(f"Reason: {safety['reason']}")

    # --------------------------------------------------------
    # CRISIS → STOP NORMAL PIPELINE
    # --------------------------------------------------------

    if not safety["allow_gita_rag"]:

        print("\n🚨 Crisis detected.")
        print("Normal Gita retrieval has been stopped.")

        return get_safety_response(
            safety["safety_level"]
        )


    # --------------------------------------------------------
    # STEP 2: SITUATION ANALYSIS
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("🧠 UNDERSTANDING USER")
    print("=" * 70)

    analysis = analyze_situation(user_message)

    print(f"Emotion: {analysis.get('emotion')}")
    print(f"Situation: {analysis.get('situation')}")
    print(f"Need: {analysis.get('need')}")
    print(f"Intent: {analysis.get('intent')}")
    print(f"Safety: {analysis.get('safety_level')}")

    semantic_query = analysis.get(
        "semantic_query",
        user_message
    )

    print(f"\nSemantic Query:\n{semantic_query}")


    # --------------------------------------------------------
    # STEP 3: FAISS RETRIEVAL
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("🔎 SEARCHING BHAGAVAD GITA")
    print("=" * 70)

    results = search_gita(
        semantic_query,
        top_k=5
    )

    print(f"Retrieved {len(results)} passages.")


    # --------------------------------------------------------
    # STEP 4: GROQ RESPONSE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("🤖 GENERATING AI SAARTHI RESPONSE")
    print("=" * 70)

    response = generate_response(
        user_message,
        analysis,
        results
    )

    return response, analysis, results


# ============================================================
# CHAT LOOP
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("🌱 AI SAARTHI")
    print("Bhagavad Gita Inspired Guidance Assistant")
    print("=" * 70)

    print("\nType 'exit' to stop.")

    while True:

        user_message = input(
            "\nYou:\n> "
        ).strip()

        if user_message.lower() == "exit":

            print("\nSaarthi: Take care. 🌱")

            break

        if not user_message:

            print("Please enter a message.")

            continue


        try:

            result = run_saarthi(
                user_message
            )


            # ------------------------------------------------
            # CRISIS RESPONSE
            # ------------------------------------------------

            if isinstance(result, str):

                print("\n" + "=" * 70)
                print("🌱 AI SAARTHI")
                print("=" * 70)

                print(result)

                continue


            # ------------------------------------------------
            # NORMAL RESPONSE
            # ------------------------------------------------

            response, analysis, results = result

            print("\n" + "=" * 70)
            print("🌱 AI SAARTHI")
            print("=" * 70)

            print(response)


            # ------------------------------------------------
            # SHOW SOURCES
            # ------------------------------------------------

            print("\n" + "=" * 70)
            print("📖 RETRIEVED GITA PASSAGES")
            print("=" * 70)

            for i, result in enumerate(
                results,
                start=1
            ):

                print(
                    f"\n{i}. "
                    f"Chapter {result.get('chapter')} "
                    f"| Verse {result.get('verse')} "
                    f"| Score: {result.get('score', 0):.4f}"
                )


        except Exception as e:

            print("\n❌ ERROR")
            print("-" * 70)
            print(str(e))   