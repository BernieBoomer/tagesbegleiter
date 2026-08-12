import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tagesbegleiter:***@localhost:5432/tagesbegleiter"
)

# pool_pre_ping=True: prüft Verbindung vor jedem Query automatisch —
# verhindert "SSL connection has been closed unexpectedly" nach Inaktivität.
# pool_recycle=1800: Verbindungen nach 30min erneuern (PostgreSQL-Timeout liegt bei ~1h).
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine, checkfirst=True)


def get_session():
    with Session(engine) as session:
        yield session
