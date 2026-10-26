from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from .config import get_settings

# Tabel dibuat dan diubah oleh Alembic: jalankan `alembic upgrade head` sebelum memulai server.
engine = create_engine(get_settings().database_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
