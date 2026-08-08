from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Todo, TodoCreate, TodoUpdate

router = APIRouter()


@router.get("", response_model=List[Todo])
def list_todos(
    status: Optional[str] = None,   # "open" | "done"
    category: Optional[str] = None, # manuell | mail | sprache | einkauf | arbeit | privat
    date_filter: Optional[str] = None,  # "today" | "tomorrow" (filtert due_date)
    session: Session = Depends(get_session),
):
    """
    Todos abfragen. Kombinierbare Filter:
      ?status=open
      ?category=einkauf
      ?date_filter=today   → due_date liegt heute
    """
    query = select(Todo)

    if status == "open":
        query = query.where(Todo.done == False)  # noqa: E712
    elif status == "done":
        query = query.where(Todo.done == True)   # noqa: E712

    if category:
        query = query.where(Todo.category == category)

    if date_filter == "today":
        today = date.today()
        query = query.where(
            Todo.due_date >= datetime(today.year, today.month, today.day, 0, 0, 0),
            Todo.due_date <= datetime(today.year, today.month, today.day, 23, 59, 59),
        )
    elif date_filter == "tomorrow":
        from datetime import timedelta
        tomorrow = date.today() + timedelta(days=1)
        query = query.where(
            Todo.due_date >= datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0),
            Todo.due_date <= datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59),
        )

    return session.exec(query).all()


@router.post("", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate, session: Session = Depends(get_session)):
    """
    Neues Todo anlegen.

    # Testaufruf:
    # curl -s -X POST http://localhost:8000/todos \
    #   -H "Content-Type: application/json" \
    #   -d '{"text": "Mail an Dr. Weber beantworten", "category": "mail", "source": "mail"}'
    """
    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.patch("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updates: TodoUpdate, session: Session = Depends(get_session)):
    """
    Beliebige Felder eines Todos aktualisieren (z.B. nur done=true setzen).

    # Testaufruf:
    # curl -s -X PATCH http://localhost:8000/todos/1 \
    #   -H "Content-Type: application/json" \
    #   -d '{"done": true}'
    """
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    """
    Todo löschen.

    # Testaufruf:
    # curl -s -X DELETE http://localhost:8000/todos/1
    """
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")
    session.delete(todo)
    session.commit()
