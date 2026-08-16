from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.auth import verify_api_key
from app.models import ShoppingItem, ShoppingItemCreate, ShoppingItemUpdate

router = APIRouter(prefix="/v1/shopping", tags=["shopping"])


@router.get("", response_model=List[ShoppingItem])
def list_items(
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Alle Einkaufsartikel — offen zuerst, dann erledigte."""
    items = session.exec(select(ShoppingItem).order_by(ShoppingItem.done, ShoppingItem.created_at)).all()
    return items


@router.post("", response_model=ShoppingItem, status_code=201)
def add_item(
    payload: ShoppingItemCreate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Artikel zur Einkaufsliste hinzufügen."""
    item = ShoppingItem.from_orm(payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.patch("/{item_id}/done", response_model=ShoppingItem)
def check_item(
    item_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Artikel abhaken (done=True)."""
    item = session.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    item.done = True
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ShoppingItem)
def update_item(
    item_id: int,
    payload: ShoppingItemUpdate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Artikel aktualisieren (Name, Menge, done)."""
    item = session.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(verify_api_key),
):
    """Artikel aus der Liste entfernen."""
    item = session.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    session.delete(item)
    session.commit()
