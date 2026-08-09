import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.auth import verify_api_key
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

# Keine eigene Middleware mehr — Auth läuft ausschliesslich über verify_api_key (app/auth.py).
# auth.py ist fail-closed: 500 wenn API_KEY nicht gesetzt, 401 bei falschem Key.
# EXEMPT: /health, /docs, /openapi.json, /redoc (kein Depends nötig, kein Key in Signatur)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    transcribe.load_model()  # Preload Whisper-Modell


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "version": "0.2.0"}


_auth = [Depends(verify_api_key)]

app.include_router(todos.router,       prefix="/v1/todos",       tags=["todos"],       dependencies=_auth)
app.include_router(calendar.router,    prefix="/v1/calendar",    tags=["calendar"],    dependencies=_auth)
app.include_router(contacts.router,    prefix="/v1/contacts",    tags=["contacts"],    dependencies=_auth)
app.include_router(visit_notes.router, prefix="/v1/visit-notes", tags=["visit-notes"], dependencies=_auth)
app.include_router(mail.router,        prefix="/v1/mail",        tags=["mail"],        dependencies=_auth)
app.include_router(transcribe.router,  tags=["voice"],           dependencies=_auth)
app.include_router(waste.router,       prefix="/v1",             tags=["waste"],       dependencies=_auth)
