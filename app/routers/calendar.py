from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import CalendarEvent, CalendarEventBase

router = APIRouter()


@router.get("", response_model=List[CalendarEvent])
def list_events(
    date_filter: Optional[str] = None,  # "today" | "tomorrow" | "week"
    session: Session = Depends(get_session),
):
    """
    Kalendereinträge abfragen.
      ?date_filter=today    → Termine heute
      ?date_filter=tomorrow → Termine morgen
      ?date_filter=week     → Termine diese Woche

    # Testaufruf:
    # curl "http://localhost:8000/calendar?date_filter=tomorrow"
    """
    query = select(CalendarEvent)

    if date_filter == "today":
        today = date.today()
        query = query.where(
            CalendarEvent.start_time >= datetime(today.year, today.month, today.day, 0, 0, 0),
            CalendarEvent.start_time <= datetime(today.year, today.month, today.day, 23, 59, 59),
        )
    elif date_filter == "tomorrow":
        tomorrow = date.today() + timedelta(days=1)
        query = query.where(
            CalendarEvent.start_time >= datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0),
            CalendarEvent.start_time <= datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59),
        )
    elif date_filter == "week":
        today = date.today()
        week_end = today + timedelta(days=7)
        query = query.where(
            CalendarEvent.start_time >= datetime(today.year, today.month, today.day, 0, 0, 0),
            CalendarEvent.start_time <= datetime(week_end.year, week_end.month, week_end.day, 23, 59, 59),
        )

    return session.exec(query.order_by(CalendarEvent.start_time)).all()


@router.post("", response_model=CalendarEvent, status_code=201)
def create_event(event: CalendarEventBase, session: Session = Depends(get_session)):
    """
    Neuen Kalendertermin anlegen.

    # Testaufruf:
    # curl -s -X POST http://localhost:8000/calendar \
    #   -H "Content-Type: application/json" \
    #   -d '{"title": "Arzttermin Dr. Weber", "start_time": "2026-08-06T14:30:00", "location": "Praxis Musterstr. 1"}'
    """
    db_event = CalendarEvent.model_validate(event)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """
    Kalendertermin löschen.

    # Testaufruf:
    # curl -s -X DELETE http://localhost:8000/calendar/1
    """
    event = session.get(CalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Termin nicht gefunden")
    session.delete(event)
    session.commit()
