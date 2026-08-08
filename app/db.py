from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tagesbegleiter:Tages2026!pgSecure@localhost:5432/tagesbegleiter"
)

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
