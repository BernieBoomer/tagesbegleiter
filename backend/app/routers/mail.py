from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import MailSummary, MailSummaryBase

router = APIRouter()


@router.get("/summary", response_model=Optional[MailSummary])
def get_mail_summary(
    date_filter: Optional[str] = None,  # "today" (default) | "latest"
    session: Session = Depends(get_session),
):
    """
    Aktuelle Mail-Zusammenfassung abrufen.
    Wird vom Bodo-Cron täglich gespeichert, die App liest sie hier aus.
      ?date_filter=today   → Zusammenfassung von heute
      ?date_filter=latest  → Neueste verfügbare (auch wenn nicht heute)

    # Testaufruf:
    # curl "http://localhost:8000/mail/summary?date_filter=today"
    """
    query = select(MailSummary).order_by(MailSummary.created_at.desc())  # type: ignore

    if date_filter == "today" or date_filter is None:
        today = date.today()
        query = query.where(
            MailSummary.summary_date >= datetime(today.year, today.month, today.day, 0, 0, 0),
        )

    result = session.exec(query).first()
    return result


@router.get("/summary/history", response_model=List[MailSummary])
def get_mail_summary_history(
    limit: int = 7,
    session: Session = Depends(get_session),
):
    """
    Letzte N Mail-Zusammenfassungen (Standard: 7 Tage).

    # Testaufruf:
    # curl "http://localhost:8000/mail/summary/history?limit=5"
    """
    query = select(MailSummary).order_by(MailSummary.created_at.desc()).limit(limit)  # type: ignore
    return session.exec(query).all()


@router.post("/summary", response_model=MailSummary, status_code=201)
def create_mail_summary(summary: MailSummaryBase, session: Session = Depends(get_session)):
    """
    Mail-Zusammenfassung speichern — wird vom Bodo-Cron-Job aufgerufen.

    # Testaufruf:
    # curl -s -X POST http://localhost:8000/mail/summary \
    #   -H "Content-Type: application/json" \
    #   -d '{"total_count": 25, "important_count": 3, "summary_text": "3 wichtige Mails: ..."}'
    """
    db_summary = MailSummary.model_validate(summary)
    session.add(db_summary)
    session.commit()
    session.refresh(db_summary)
    return db_summary


@router.delete("/summary/{summary_id}", status_code=204)
def delete_mail_summary(summary_id: int, session: Session = Depends(get_session)):
    """Alte Mail-Zusammenfassung löschen."""
    summary = session.get(MailSummary, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Zusammenfassung nicht gefunden")
    session.delete(summary)
    session.commit()
