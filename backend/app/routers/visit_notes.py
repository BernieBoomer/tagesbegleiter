from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import VisitNote, VisitNoteBase, VisitNoteUpdate

router = APIRouter()

# WICHTIG: Diese Daten NIE an ein externes CRM oder einen Drittanbieter senden.
# Nur lokale Speicherung in SQLite. Siehe Pflichtenheft Punkt 6.


@router.get("", response_model=List[VisitNote])
def list_visit_notes(
    followup: Optional[str] = None,  # "open" → nur offene Follow-ups
    session: Session = Depends(get_session),
):
    """
    Besuchsnotizen abfragen.
      ?followup=open → nur offene Follow-ups (für Dashboard-Karte)

    # Testaufruf:
    # curl "http://localhost:8000/visit-notes?followup=open"
    """
    query = select(VisitNote)
    if followup == "open":
        query = query.where(VisitNote.followup_open == True)  # noqa: E712
    return session.exec(query).all()


@router.post("", response_model=VisitNote, status_code=201)
def create_visit_note(note: VisitNoteBase, session: Session = Depends(get_session)):
    """
    Neue Besuchsnotiz anlegen. NIEMALS an CRM senden.

    # Testaufruf:
    # curl -s -X POST http://localhost:8000/visit-notes \
    #   -H "Content-Type: application/json" \
    #   -d '{"contact_name": "Dr. Müller", "clinic": "Uniklinik HH", "topic": "Produkt X", "result": "Interesse", "followup_open": true}'
    """
    db_note = VisitNote.model_validate(note)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.patch("/{note_id}", response_model=VisitNote)
def update_visit_note(note_id: int, updates: VisitNoteUpdate, session: Session = Depends(get_session)):
    """
    Besuchsnotiz aktualisieren (z.B. followup_open=false nach Nachfassen).

    # Testaufruf:
    # curl -s -X PATCH http://localhost:8000/visit-notes/1 \
    #   -H "Content-Type: application/json" \
    #   -d '{"followup_open": false}'
    """
    note = session.get(VisitNote, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Besuchsnotiz nicht gefunden")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)

    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_visit_note(note_id: int, session: Session = Depends(get_session)):
    """
    Besuchsnotiz löschen.

    # Testaufruf:
    # curl -s -X DELETE http://localhost:8000/visit-notes/1
    """
    note = session.get(VisitNote, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Besuchsnotiz nicht gefunden")
    session.delete(note)
    session.commit()
