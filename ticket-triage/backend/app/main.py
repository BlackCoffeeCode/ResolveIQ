from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers.ai_analysis_controller import router as ai_analysis_router
from app.controllers.ticket_controller import router as ticket_router
from app.config.settings import get_settings
from app.database import create_all_tables
from app.models.ai_analysis import TicketAIAnalysis  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401

app = FastAPI(
    title="ResolveIQ API",
    description="Support ticket triage API with explainable keyword rules",
    version="1.0.0",
)

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_all_tables()


app.include_router(ticket_router)
app.include_router(ai_analysis_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
