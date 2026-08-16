from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


# ---------------------------------------------------------------------------
# Todo
# ---------------------------------------------------------------------------

class TodoBase(SQLModel):
    text: str
    category: str = "manuell"       # manuell | mail | sprache | einkauf | arbeit | privat
    source: str = "manuell"         # manuell | mail | sprache  — UI-Herkunfts-Tag
    done: bool = False
    due_date: Optional[datetime] = None
    is_wiedervorlage: bool = False


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    """Payload für POST /todos — id und created_at werden serverseitig gesetzt."""
    pass


class TodoUpdate(SQLModel):
    """Payload für PATCH /todos/{id} — alle Felder optional."""
    text: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    done: Optional[bool] = None
    due_date: Optional[datetime] = None
    is_wiedervorlage: Optional[bool] = None


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

class ContactBase(SQLModel):
    name: str
    channel: str = "telegram"       # telegram | whatsapp
    channel_id: Optional[str] = None
    notes: Optional[str] = None


class Contact(ContactBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ContactUpdate(SQLModel):
    name: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# VisitNote  (NIEMALS an CRM synchronisieren — nur lokal!)
# ---------------------------------------------------------------------------

class VisitNoteBase(SQLModel):
    contact_name: str
    clinic: Optional[str] = None
    topic: Optional[str] = None
    result: Optional[str] = None
    followup_open: bool = False


class VisitNote(VisitNoteBase, table=True):
    """Besuchsprotokolle. NIEMALS an ein CRM synchronisieren — nur lokal."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VisitNoteUpdate(SQLModel):
    contact_name: Optional[str] = None
    clinic: Optional[str] = None
    topic: Optional[str] = None
    result: Optional[str] = None
    followup_open: Optional[bool] = None


# ---------------------------------------------------------------------------
# CalendarEvent
# ---------------------------------------------------------------------------

class CalendarEventBase(SQLModel):
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class CalendarEvent(CalendarEventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# ---------------------------------------------------------------------------
# MailSummary  — gespeicherte Mail-Zusammenfassungen (von Bodo-Cron)
# Spaltenname summary_date (bestehende DB), total_count=mail_count (Alias)
# ---------------------------------------------------------------------------

class MailSummaryBase(SQLModel):
    summary_date: datetime = Field(default_factory=datetime.utcnow)
    mail_count: int = 0
    important_count: int = 0
    summary_text: str


class MailSummary(MailSummaryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# WastePickup  — Müllkalender (aus ICS-Upload)
# ---------------------------------------------------------------------------

class WastePickup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pickup_date: datetime
    category: str           # z.B. "Restmüll", "Biomüll", "Gelbe Tonne"
    raw_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# ShoppingItem  — Einkaufsliste
# ---------------------------------------------------------------------------

class ShoppingItemBase(SQLModel):
    name: str
    quantity: Optional[str] = None   # z.B. "2", "1 kg", "eine Packung"
    done: bool = False


class ShoppingItem(ShoppingItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ShoppingItemCreate(ShoppingItemBase):
    pass


class ShoppingItemUpdate(SQLModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    done: Optional[bool] = None

