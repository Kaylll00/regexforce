"""Database engine and FastAPI session dependency."""

from __future__ import annotations

import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./regexforge.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield one database session for a request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
