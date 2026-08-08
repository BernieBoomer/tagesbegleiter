from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Contact, ContactBase, ContactUpdate

router = APIRouter()


@router.get("", response_model=List[Contact])
def list_contacts(
    recent: Optional[bool] = None,  # True → nur letzte 10 Kontakte
    session: Session = Depends(get_session),
):
    """
    Kontakte abfragen.
      ?recent=true → letzte 10 (für Seitenleiste Dashboard)

    # Testaufruf:
    # curl "http://localhost:8000/contacts?recent=true"
    """
    query = select(Contact)
    results = session.exec(query).all()

    if recent:
        results = results[-10:]

    return results


@router.post("", response_model=Contact, status_code=201)
def create_contact(contact: ContactBase, session: Session = Depends(get_session)):
    """
    Neuen Kontakt anlegen.

    # Testaufruf:
    # curl -s -X POST http://localhost:8000/contacts \
    #   -H "Content-Type: application/json" \
    #   -d '{"name": "Dr. Weber", "channel": "telegram", "notes": "Onkologie, Uniklinik"}'
    """
    db_contact = Contact.model_validate(contact)
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact


@router.patch("/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, updates: ContactUpdate, session: Session = Depends(get_session)):
    """
    Kontakt aktualisieren.

    # Testaufruf:
    # curl -s -X PATCH http://localhost:8000/contacts/1 \
    #   -H "Content-Type: application/json" \
    #   -d '{"notes": "Neue Notiz"}'
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)

    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    """
    Kontakt löschen.

    # Testaufruf:
    # curl -s -X DELETE http://localhost:8000/contacts/1
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Kontakt nicht gefunden")
    session.delete(contact)
    session.commit()

# TODO: Nachrichten-Entwurf Endpoint (WhatsApp/Telegram) — Vorschlag generieren,
# NICHT automatisch senden. Siehe Pflichtenheft "Entwurf statt Autopilot".
