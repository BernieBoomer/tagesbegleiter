import os
import asyncio
import tempfile
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlmodel import Session
from app.db import get_session, engine
from app.models import Todo, VisitNote

router = APIRouter()

# --- faster-whisper Model (einmalig beim Start geladen) ---
_whisper_model = None
_model_lock = asyncio.Lock()
_executor = ThreadPoolExecutor(max_workers=2)

WHISPER_MODEL_SIZE = "small"
WHISPER_COMPUTE_TYPE = "int8"


def get_whisper_model():
    """Lädt das Modell lazy beim ersten Aufruf, dann gecacht."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device="cpu",
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _whisper_model


def _transcribe_sync(audio_path: str) -> str:
    """Synchrone Transkription — läuft im ThreadPoolExecutor."""
    model = get_whisper_model()
    segments, info = model.transcribe(audio_path, language="de")
    text = " ".join(s.text.strip() for s in segments).strip()
    return text


def kategorisiere(text: str) -> str:
    """
    Regelbasierte Kategorisierung.
    Gibt zurück: 'todo' | 'einkauf' | 'besuchsnotiz' | 'notiz'
    """
    text_lower = text.lower()

    besuch_keywords = [
        "besuch", "klinik", "arzt", "ärztin", "dr.", "doktor",
        "gespräch bei", "meeting", "termin bei", "professor", "chefarzt",
        "onkologie", "station", "krankenhaus", "praxis", "uni-klinik",
        "uniklinik", "follow-up", "visite"
    ]
    if any(k in text_lower for k in besuch_keywords):
        return "besuchsnotiz"

    einkauf_keywords = [
        "kauf", "kaufe", "kaufen", "einkauf", "einkaufen",
        "rewe", "edeka", "aldi", "lidl", "obi", "baumarkt",
        "milch", "brot", "brauche", "brauchen", "besorge", "besorgen"
    ]
    if any(k in text_lower for k in einkauf_keywords):
        return "einkauf"

    todo_keywords = [
        "erinnere", "erinnern", "nicht vergessen", "muss ich", "müssen",
        "soll ich", "aufgabe", "todo", "anrufen", "antworten",
        "schicken", "schreiben", "melden", "wiedervorlage"
    ]
    if any(k in text_lower for k in todo_keywords):
        return "todo"

    return "todo"  # Fallback


def _save_to_db(text: str, kategorie: str) -> dict:
    """Speichert den transkribierten Text in die DB."""
    from sqlmodel import Session
    with Session(engine) as session:
        if kategorie == "besuchsnotiz":
            note = VisitNote(
                contact_name="Unbekannt",
                topic=text,
                followup_open=True,
            )
            session.add(note)
            session.commit()
            session.refresh(note)
            return {"saved_as": "visit_note", "id": note.id}
        else:
            todo = Todo(text=text, category=kategorie)
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return {"saved_as": "todo", "id": todo.id}


def _notify_telegram(message: str):
    """Sendet eine Telegram-Nachricht an Bernd über den Hermes-Gateway."""
    import urllib.request
    import json
    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_HOME_CHANNEL", "")
        if not bot_token or not chat_id:
            print(f"[transcribe] Telegram-Config fehlt — Nachricht nur geloggt: {message}")
            return
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": message}).encode()
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[transcribe] Telegram-Benachrichtigung fehlgeschlagen: {e}")


def _process_audio_background(tmp_path: str, job_id: str):
    """
    Hintergrund-Job: Transkribiert Audio und speichert Ergebnis.
    Räumt temp-Datei am Ende auf.
    Bei Fehler: Telegram-Benachrichtigung statt stillem Fehlschlag.
    """
    try:
        text = _transcribe_sync(tmp_path)
        if not text:
            print(f"[transcribe] job={job_id} leere Transkription — Datei evtl. kein Sprach-Audio")
            _notify_telegram(f"⚠️ Sprachnotiz (Job {job_id}) konnte nicht transkribiert werden — kein Sprach-Audio erkannt.")
            return
        kategorie = kategorisiere(text)
        result = _save_to_db(text, kategorie)
        print(f"[transcribe] job={job_id} text='{text[:60]}' category={kategorie} saved={result}")
        # Erfolgsmeldung — kurze Bestätigung
        emoji = {"besuchsnotiz": "🏥", "einkauf": "🛒", "todo": "✅", "notiz": "📝"}.get(kategorie, "📝")
        _notify_telegram(f"{emoji} Notiz gespeichert ({kategorie}):\n\"{text[:120]}\"")
    except Exception as e:
        # Voller Fehlertext ins Server-Log (journald), nicht an Telegram
        import traceback
        print(f"[transcribe] job={job_id} ERROR: {traceback.format_exc()}")
        # Nutzer bekommt generische Meldung
        _notify_telegram("⚠️ Verarbeitung fehlgeschlagen — bitte nochmal versuchen.")
    finally:
        for path in [tmp_path, tmp_path + ".txt"]:
            if os.path.exists(path):
                os.unlink(path)


@router.post("/transcribe")
async def transcribe_and_save(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Nimmt eine Audiodatei entgegen (ogg, mp3, wav, m4a),
    bestätigt den Empfang sofort und transkribiert im Hintergrund.

    Sofortige Antwort:
    {"status": "received", "job_id": "<uuid>", "message": "Notiz erhalten — wird verarbeitet"}

    Testaufruf:
    curl -X POST https://tagesbegleiter.app/voice/transcribe \
      -H "X-API-Key: <key>" \
      -F "file=@notiz.ogg"
    """
    import uuid
    job_id = str(uuid.uuid4())[:8]

    # Audiodatei temporär speichern
    suffix = os.path.splitext(file.filename or "audio.ogg")[1] or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Sofort bestätigen, Transkription läuft im Hintergrund
    background_tasks.add_task(_process_audio_background, tmp_path, job_id)

    return {
        "status": "received",
        "job_id": job_id,
        "message": "Notiz erhalten — wird verarbeitet",
    }


@router.post("/transcribe/sync")
async def transcribe_sync(
    file: UploadFile = File(...),
):
    """
    Synchrone Variante — wartet auf Ergebnis (für Tests).

    Testaufruf:
    curl -X POST https://tagesbegleiter.app/voice/transcribe/sync \
      -H "X-API-Key: <key>" \
      -F "file=@notiz.ogg"
    """
    suffix = os.path.splitext(file.filename or "audio.ogg")[1] or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(_executor, _transcribe_sync, tmp_path)
        if not text:
            raise HTTPException(status_code=422, detail="Transkription leer")
        kategorie = kategorisiere(text)
        result = _save_to_db(text, kategorie)
        return {
            "text": text,
            "category": kategorie,
            **result,
        }
    finally:
        for path in [tmp_path, tmp_path + ".txt"]:
            if os.path.exists(path):
                os.unlink(path)
