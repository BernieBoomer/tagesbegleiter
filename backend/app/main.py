import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.db import init_db
from app.routers import todos, calendar, contacts, visit_notes, mail, transcribe, waste

app = FastAPI(
    title="Tagesbegleiter API",
    version="0.2.0",
    description="Persönlicher KI-Gedächtnisassistent — API-Backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tagesbegleiter.app",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("TAGESBEGLEITER_API_KEY", "")
EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)
    if API_KEY:
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Ungültiger oder fehlender API-Key"})
    return await call_next(request)

@app.on_event("startup")
def on_startup() -> None:
    init_db()
    transcribe.load_model()  # Preload Whisper-Modell

@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "version": "0.2.0"}

app.include_router(todos.router,       prefix="/v1/todos",       tags=["todos"])
app.include_router(calendar.router,    prefix="/v1/calendar",    tags=["calendar"])
app.include_router(contacts.router,    prefix="/v1/contacts",    tags=["contacts"])
app.include_router(visit_notes.router, prefix="/v1/visit-notes", tags=["visit-notes"])
app.include_router(mail.router,        prefix="/v1/mail",        tags=["mail"])
app.include_router(transcribe.router,  tags=["voice"])  # /voice/transcribe, /voice/transcribe/sync
app.include_router(waste.router,       prefix="/v1",             tags=["waste"])  # /v1/waste/upload, /v1/waste/today
