"""
REKONSTRUIERT am 08.08.2026 nach Regression (Original ging beim Deployment verloren,
kein Git-Backup vorhanden). Basiert auf der im Chat-Verlauf dokumentierten
Spezifikation vom 30.07.-01.08.2026, NICHT auf dem tatsächlichen Original-Code.

WICHTIG: Vor Produktivbetrieb erneut vollständig testen (Smoke-Tests wie am 01.08.:
korrupte Audiodatei, echte Sprachnotiz, Telegram-Rückmeldung prüfen). Diese Version
ist ein bestmöglicher Nachbau, keine Wiederherstellung des Originals.

Bekannte Eckpunkte aus der Spezifikation:
- faster-whisper, Modell "small", compute_type "int8", CPU, Sprache "de"
- Modell wird einmalig beim Server-Start geladen (nicht pro Request)
- Async: sofortige Bestätigung (~134ms), Transkription läuft im Hintergrund
- Regelbasierte Kategorisierung: todo / einkauf / besuchsnotiz / notiz
- Ergebnis geht an den passenden Endpoint (todos, visit-notes), kein Universal-Endpoint
- Telegram-Rückmeldung bei Erfolg (Emoji + Text-Preview), leerer Transkription
  und Exception (generische Nutzermeldung, voller Stack-Trace nur ins Log)
- Audiodatei wird nach Transkription gelöscht (os.unlink) — kein BLOB in der DB
"""

import os
import traceback
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File
from faster_whisper import WhisperModel

from app.db import get_session
from app.models import Todo, VisitNote
from app.auth import verify_api_key

router = APIRouter()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_HOME_CHANNEL = os.environ.get("TELEGRAM_HOME_CHANNEL", "")

_model: WhisperModel | None = None


def load_model() -> None:
    """Beim Server-Start aufrufen (main.py on_startup), nicht pro Request."""
    global _model
    _model = WhisperModel("small", device="cpu", compute_type="int8")


def _notify_telegram(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_HOME_CHANNEL:
        print(f"[transcribe] Telegram nicht konfiguriert, Nachricht verworfen: {text}")
        return
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_HOME_CHANNEL, "text": text},
            timeout=10,
        )
    except Exception:
        print(f"[transcribe] Telegram-Benachrichtigung fehlgeschlagen: {traceback.format_exc()}")


def _categorize(text: str) -> str:
    """Regelbasierte Kategorisierung. Einfache Keyword-Heuristik als Platzhalter —
    bei Bedarf durch echte Klassifikation ersetzen."""
    lower = text.lower()
    einkauf_keywords = ["kauf", "einkauf", "besorg", "milch", "rewe", "supermarkt"]
    besuch_keywords = ["dr.", "doktor", "klinik", "arzt", "besuch", "termin bei"]
    if any(k in lower for k in einkauf_keywords):
        return "einkauf"
    if any(k in lower for k in besuch_keywords):
        return "besuchsnotiz"
    return "todo"


def _process_audio_background(tmp_path: str, job_id: str) -> None:
    session = next(get_session())
    try:
        if _model is None:
            raise RuntimeError("Whisper-Modell nicht geladen")

        segments, _info = _model.transcribe(tmp_path, language="de")
        text = " ".join(seg.text.strip() for seg in segments).strip()

        if not text:
            _notify_telegram("⚠️ Sprachnotiz konnte nicht transkribiert werden.")
            return

        category = _categorize(text)

        if category == "besuchsnotiz":
            entry = VisitNote(contact_name="unbekannt", topic=text, followup_open=True)
            session.add(entry)
            session.commit()
            session.refresh(entry)
            saved_as = "visit_note"
            entry_id = entry.id
        else:
            entry = Todo(text=text, category=category, source="sprache")
            session.add(entry)
            session.commit()
            session.refresh(entry)
            saved_as = "todo"
            entry_id = entry.id

        preview = text[:120]
        _notify_telegram(f"✅ Notiz gespeichert ({category}): '{preview}'")
        print(f"[transcribe] job={job_id} OK saved_as={saved_as} id={entry_id}")

    except Exception:
        print(f"[transcribe] job={job_id} ERROR: {traceback.format_exc()}")
        _notify_telegram("⚠️ Verarbeitung fehlgeschlagen — bitte nochmal versuchen.")
    finally:
        session.close()
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@router.post("/voice/transcribe", dependencies=[Depends(verify_api_key)])
async def transcribe_async(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    tmp_path = f"/tmp/tmp{uuid.uuid4().hex}.ogg"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    background_tasks.add_task(_process_audio_background, tmp_path, job_id)
    return {"status": "received", "job_id": job_id}


@router.post("/voice/transcribe/sync", dependencies=[Depends(verify_api_key)])
async def transcribe_sync(file: UploadFile = File(...)):
    """Wartet auf das Ergebnis — nur für Tests, nicht für den Telegram-Flow."""
    tmp_path = f"/tmp/tmp{uuid.uuid4().hex}.ogg"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    try:
        if _model is None:
            raise RuntimeError("Whisper-Modell nicht geladen")
        segments, _info = _model.transcribe(tmp_path, language="de")
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return {"text": text, "category": _categorize(text) if text else None}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
