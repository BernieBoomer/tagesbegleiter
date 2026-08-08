import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tagesbegleiter:tb_secure_2026@localhost:5432/tagesbegleiter"
)
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine, checkfirst=True)


def get_session():
    with Session(engine) as session:
        yield session
