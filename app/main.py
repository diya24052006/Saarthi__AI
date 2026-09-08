from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title="AI Saarthi API",

    description=(
        "Bhagavad Gita inspired emotional "
        "guidance assistant using RAG and AI."
    ),

    version="1.0.0"
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(router)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# ============================================================
# FRONTEND
# ============================================================

@app.get("/")
def root():

    from fastapi.responses import FileResponse

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )