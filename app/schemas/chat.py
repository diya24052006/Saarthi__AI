from pydantic import BaseModel, Field


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message to AI Saarthi"
    )


# ============================================================
# GITA SOURCE
# ============================================================

class Source(BaseModel):

    chapter: int | None = None

    chapter_title: str | None = None

    verse: str | None = None

    speaker: str | None = None

    score: float | None = None


# ============================================================
# CHAT RESPONSE
# ============================================================

class ChatResponse(BaseModel):

    response: str

    emotion: str | None = None

    situation: str | None = None

    need: str | None = None

    intent: str | None = None

    safety_level: str

    sources: list[Source] = Field(
        default_factory=list
    )