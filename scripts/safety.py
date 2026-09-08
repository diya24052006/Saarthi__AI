import re


# ============================================================
# SAFETY KEYWORDS
# ============================================================

CRISIS_PATTERNS = [

    # Suicide / death
    r"\bkill myself\b",
    r"\bkilling myself\b",
    r"\bend my life\b",
    r"\bend it all\b",
    r"\btake my own life\b",
    r"\bwant to die\b",
    r"\bwish i was dead\b",
    r"\bwish i were dead\b",
    r"\bdon't want to live\b",
    r"\bdo not want to live\b",
    r"\bno reason to live\b",
    r"\blife is not worth living\b",

    # Self-harm
    r"\bhurt myself\b",
    r"\bharm myself\b",
    r"\bcut myself\b",
    r"\bself harm\b",
    r"\bself-harm\b",

    # Immediate danger
    r"\bgoing to kill myself\b",
    r"\babout to kill myself\b",
    r"\bgoing to hurt myself\b",
]


HARM_TO_OTHERS_PATTERNS = [

    r"\bkill him\b",
    r"\bkill her\b",
    r"\bkill them\b",
    r"\bkill someone\b",
    r"\bhurt him\b",
    r"\bhurt her\b",
    r"\bhurt them\b",
    r"\bhurt someone\b",
]


ELEVATED_PATTERNS = [

    r"\bhopeless\b",
    r"\bcan't go on\b",
    r"\bcannot go on\b",
    r"\bno hope\b",
    r"\bcompletely alone\b",
    r"\bextremely lonely\b",
    r"\bwant to disappear\b",
    r"\bnothing matters\b",
    r"\beverything is pointless\b",
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:

    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# PATTERN MATCHING
# ============================================================

def contains_pattern(text: str, patterns: list[str]) -> bool:

    for pattern in patterns:

        if re.search(pattern, text):
            return True

    return False


# ============================================================
# SAFETY ANALYSIS
# ============================================================

def analyze_safety(user_message: str) -> dict:

    text = normalize_text(user_message)

    # --------------------------------------------------------
    # CRISIS
    # --------------------------------------------------------

    if contains_pattern(text, CRISIS_PATTERNS):

        return {
            "safety_level": "crisis",
            "reason": "possible self-harm or suicide risk",
            "allow_gita_rag": False
        }

    # --------------------------------------------------------
    # HARM TO OTHERS
    # --------------------------------------------------------

    if contains_pattern(text, HARM_TO_OTHERS_PATTERNS):

        return {
            "safety_level": "crisis",
            "reason": "possible risk of harm to another person",
            "allow_gita_rag": False
        }

    # --------------------------------------------------------
    # ELEVATED DISTRESS
    # --------------------------------------------------------

    if contains_pattern(text, ELEVATED_PATTERNS):

        return {
            "safety_level": "elevated",
            "reason": "significant emotional distress",
            "allow_gita_rag": True
        }

    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    return {
        "safety_level": "normal",
        "reason": "no immediate safety signal detected",
        "allow_gita_rag": True
    }


# ============================================================
# SAFETY RESPONSE
# ============================================================

def get_safety_response(safety_level: str) -> str:

    if safety_level == "crisis":

        return """
I'm really sorry you're going through something this painful.

Your immediate safety matters more than anything else right now.
Please move away from anything you could use to hurt yourself or
someone else, and stay with a trusted person if possible.

If you may act on these thoughts or someone is in immediate danger,
please contact your local emergency service or go to the nearest
emergency department now.

You can also contact a qualified mental-health professional or a
trusted person who can stay with you.

AI Saarthi can listen and support you, but it is not a replacement
for immediate professional or emergency help.
""".strip()

    return ""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AI SAARTHI - SAFETY LAYER")
    print("=" * 70)

    while True:

        user_message = input("\nEnter a message (or type 'exit'):\n> ")

        if user_message.lower() == "exit":
            break

        result = analyze_safety(user_message)

        print("\nSAFETY RESULT")
        print("-" * 70)

        print(f"Level: {result['safety_level']}")
        print(f"Reason: {result['reason']}")
        print(f"Allow Gita RAG: {result['allow_gita_rag']}")

        if result["safety_level"] == "crisis":

            print("\nSAFETY RESPONSE")
            print("-" * 70)
            print(get_safety_response("crisis"))