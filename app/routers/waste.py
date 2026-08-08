"""
Müllkalender-Router für den Tagesbegleiter.

Endpunkte:
  POST /waste/upload   — ICS-Datei hochladen (multipart/form-data), parst und speichert alle Termine
  GET  /waste/next     — Nächste n Abfuhrtermine ab heute (default: 7 Tage Vorschau)
  GET  /waste/today    — Termine für heute und morgen (für Briefing + Abend-Reminder)
"""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from app.db import get_session
from app.models import WastePickup

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_ics(content: bytes) -> List[dict]:
    """
    Minimaler ICS-Parser — kein icalendar-Dependency nötig.
    Liest VEVENT-Blöcke und extrahiert DTSTART + SUMMARY.
    Unterstützt DTSTART;VALUE=DATE (nur Datum) und DTSTART mit Uhrzeit.
    """
    text = content.decode("utf-8", errors="replace")
    events = []
    in_event = False
    current: dict = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # RFC 5545: Zeilenfortsetzung mit führendem Leerzeichen/Tab
        if raw_line.startswith((" ", "\t")) and current:
            # Anhängen an letzten Wert — für uns irrelevant, ignorieren
            continue

        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
        elif line == "END:VEVENT" and in_event:
            in_event = False
            if "date" in current and "summary" in current:
                events.append(current)
            current = {}
        elif in_event:
            if line.startswith("DTSTART"):
                # DTSTART;VALUE=DATE:20260715  oder  DTSTART:20260715T060000Z
                value = line.split(":", 1)[-1].strip()
                try:
                    if "T" in value:
                        # Datetime — nur Datumsteil nehmen
                        current["date"] = datetime.strptime(value[:8], "%Y%m%d").date()
                    else:
                        current["date"] = datetime.strptime(value[:8], "%Y%m%d").date()
                except ValueError:
                    pass
            elif line.startswith("SUMMARY"):
                value = line.split(":", 1)[-1].strip()
                current["summary"] = value

    return events


def _category_from_summary(summary: str) -> str:
    """Leitet Kategorie aus dem ICS-Summary ab (KWU-Entsorgung Notation)."""
    s = summary.lower()
    if "rest" in s:
        return "Restmüll"
    if "bio" in s:
        return "Biomüll"
    if "papier" in s or "pappe" in s:
        return "Papier"
    if "gelb" in s or "sack" in s or "leichtverpackung" in s or "lv" in s:
        return "Gelber Sack"
    if "sperr" in s:
        return "Sperrmüll"
    if "elektro" in s or "elektrogroß" in s:
        return "Elektroschrott"
    return summary  # Originaltext als Fallback


# ── Endpunkte ──────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_ics(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """
    ICS-Datei vom KWU-Entsorgungskalender hochladen.
    Parst alle VEVENT-Einträge und speichert sie in der Datenbank.
    Bereits vorhandene Termine (gleiche Kombination date+category) werden übersprungen.

    Aufruf:
      curl -X POST https://tagesbegleiter.app/waste/upload \\
        -H "X-API-Key: <key>" \\
        -F "file=@entsorgungskalender2026.ics"
    """
    if not file.filename or not file.filename.lower().endswith(".ics"):
        raise HTTPException(status_code=400, detail="Nur .ics-Dateien werden akzeptiert")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:  # 2 MB Limit
        raise HTTPException(status_code=400, detail="Datei zu groß (max 2 MB)")

    events = _parse_ics(content)
    if not events:
        raise HTTPException(status_code=422, detail="Keine VEVENT-Einträge in der ICS-Datei gefunden")

    inserted = 0
    skipped = 0

    for ev in events:
        category = _category_from_summary(ev["summary"])
        # Duplikat-Check
        existing = session.exec(
            select(WastePickup).where(
                WastePickup.pickup_date == ev["date"],
                WastePickup.category == category,
            )
        ).first()
        if existing:
            skipped += 1
            continue

        pickup = WastePickup(
            pickup_date=ev["date"],
            category=category,
            raw_summary=ev["summary"],
        )
        session.add(pickup)
        inserted += 1

    session.commit()

    return {
        "status": "ok",
        "inserted": inserted,
        "skipped": skipped,
        "total_in_file": len(events),
    }


@router.get("/next", response_model=List[WastePickup])
def get_next_pickups(
    days: int = 7,
    session: Session = Depends(get_session),
):
    """
    Nächste Abfuhrtermine für die nächsten `days` Tage (default 7).
    Gibt alle Termine ab heute zurück, aufsteigend sortiert.

    Aufruf:
      curl -H "X-API-Key: <key>" "https://tagesbegleiter.app/waste/next?days=14"
    """
    today = date.today()
    until = today + timedelta(days=days)

    results = session.exec(
        select(WastePickup)
        .where(WastePickup.pickup_date >= today)
        .where(WastePickup.pickup_date <= until)
        .order_by(WastePickup.pickup_date)
    ).all()

    return results


@router.get("/today")
def get_today_and_tomorrow(session: Session = Depends(get_session)):
    """
    Termine für heute und morgen — optimiert für Briefing und Abend-Reminder.

    Gibt zurück:
      {
        "today": [...],
        "tomorrow": [...],
        "reminder_needed": true/false  (true wenn morgen Abholung)
      }

    Aufruf:
      curl -H "X-API-Key: <key>" https://tagesbegleiter.app/waste/today
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_pickups = session.exec(
        select(WastePickup).where(WastePickup.pickup_date == today)
    ).all()

    tomorrow_pickups = session.exec(
        select(WastePickup).where(WastePickup.pickup_date == tomorrow)
    ).all()

    return {
        "today": [{"date": str(p.pickup_date), "category": p.category} for p in today_pickups],
        "tomorrow": [{"date": str(p.pickup_date), "category": p.category} for p in tomorrow_pickups],
        "reminder_needed": len(tomorrow_pickups) > 0,
    }
