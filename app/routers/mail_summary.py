from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import MailSummary

router = APIRouter()


@router.get("", response_model=Optional[MailSummary])
def get_mail_summary(
    date: Optional[str] = None,  # ISO date string, default: today
    session: Session = Depends(get_session),
):
    """
    Gibt die Mail-Zusammenfassung für ein Datum zurück.
    Default: heute.

    Testaufruf:
    curl -H "X-API-Key: <key>" https://tagesbegleiter.app/mail/summary
    curl -H "X-API-Key: <key>" https://tagesbegleiter.app/mail/summary?date=2026-07-30
    """
    if date:
        try:
            target = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=422, detail="Ungültiges Datumsformat — erwartet YYYY-MM-DD")
    else:
        target = datetime.utcnow().date()

    stmt = (
        select(MailSummary)
        .where(MailSummary.summary_date == target)
        .order_by(MailSummary.created_at.desc())
    )
    result = session.exec(stmt).first()
    return result  # None wenn kein Eintrag für dieses Datum


@router.post("", response_model=MailSummary)
def create_mail_summary(summary: MailSummary, session: Session = Depends(get_session)):
    """
    Speichert eine neue Mail-Zusammenfassung.
    Wird von Hermes (Bodo) täglich aufgerufen.

    Testaufruf:
    curl -X POST https://tagesbegleiter.app/mail/summary \\
      -H "X-API-Key: <key>" \\
      -H "Content-Type: application/json" \\
      -d '{"summary_text": "3 wichtige Mails heute: ...", "mail_count": 12, "important_count": 3}'
    """
    session.add(summary)
    session.commit()
    session.refresh(summary)
    return summary
