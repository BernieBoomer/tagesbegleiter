"""
REKONSTRUIERT am 08.08.2026 nach Regression — UNSICHERER als transcribe.py.

Einziger konkreter Hinweis aus dem Chat-Verlauf (Übergabe vom 01.08., Endpoint-Liste):
  POST /waste/upload   ← ICS-Upload
  GET  /waste/today

Das deutet auf: Nutzer/Bernd lädt eine ICS-Kalenderdatei (z.B. Export aus dem
Abfallkalender-Portal der Gemeinde) hoch, das Backend parst die Termine und legt
sie in der `wastepickup`-Tabelle ab. `/waste/today` liefert dann heutige +
morgige Termine für die "Diese Woche"-Karte im Dashboard.

WICHTIG: Diese Annahme ist nicht durch curl-Tests oder Originalcode belegt,
nur durch eine Erwähnung in einer Zusammenfassung. Bitte mit Bernd verifizieren,
ob ICS-Upload tatsächlich der richtige Mechanismus war, bevor das als "wiederhergestellt"
gilt — ansonsten bewusst als Neubau behandeln, nicht als Recovery.
"""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session, select
from icalendar import Calendar

from app.db import get_session
from app.models import WastePickup
from app.auth import verify_api_key

router = APIRouter()


@router.post("/waste/upload", dependencies=[Depends(verify_api_key)])
async def upload_ics(file: UploadFile = File(...), session: Session = Depends(get_session)):
    content = await file.read()
    try:
        cal = Calendar.from_ical(content)
    except ValueError:
        raise HTTPException(status_code=422, detail="Ungültige ICS-Datei")

    created = 0
    for component in cal.walk("VEVENT"):
        summary = str(component.get("summary", ""))
        dtstart = component.get("dtstart")
        if dtstart is None:
            continue
        pickup_date = dtstart.dt if hasattr(dtstart.dt, "year") else None
        if pickup_date is None:
            continue

        entry = WastePickup(
            pickup_date=pickup_date,
            category=summary,
            raw_summary=summary,
        )
        session.add(entry)
        created += 1

    session.commit()
    return {"imported": created}


@router.get("/waste/today", dependencies=[Depends(verify_api_key)])
def waste_today(session: Session = Depends(get_session)):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_entries = session.exec(
        select(WastePickup).where(WastePickup.pickup_date == today)
    ).all()
    tomorrow_entries = session.exec(
        select(WastePickup).where(WastePickup.pickup_date == tomorrow)
    ).all()

    return {
        "today": [e.category for e in today_entries],
        "tomorrow": [e.category for e in tomorrow_entries],
        "reminder_needed": len(tomorrow_entries) > 0,
    }
