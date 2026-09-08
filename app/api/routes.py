from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Source
)

from scripts.chat import run_saarthi


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Saarthi"
    }


# ============================================================
# CHAT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    try:

        result = run_saarthi(
            request.message
        )


        # ----------------------------------------------------
        # CRISIS RESPONSE
        # ----------------------------------------------------

        if isinstance(result, str):

            return ChatResponse(
                response=result,
                safety_level="crisis",
                sources=[]
            )


        # ----------------------------------------------------
        # NORMAL RESPONSE
        # ----------------------------------------------------

        response, analysis, results = result


        sources = []


        for item in results:

            sources.append(
                Source(
                    chapter=item.get("chapter"),
                    chapter_title=item.get(
                        "chapter_title"
                    ),
                    verse=item.get("verse"),
                    speaker=item.get("speaker"),
                    score=item.get("score")
                )
            )


        return ChatResponse(

            response=response,

            emotion=analysis.get(
                "emotion"
            ),

            situation=analysis.get(
                "situation"
            ),

            need=analysis.get(
                "need"
            ),

            intent=analysis.get(
                "intent"
            ),

            safety_level=analysis.get(
                "safety_level",
                "normal"
            ),

            sources=sources
        )


    except Exception as e:

        print("\nAI Saarthi Error:")
        print(e)

        raise HTTPException(
            status_code=500,
            detail="AI Saarthi encountered an internal error."
        )