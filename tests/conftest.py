import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine

import app.database as database

# Point the app at a throwaway DB before app.main creates tables and seeds data.
_db_path = Path(tempfile.mkdtemp()) / "test.db"
database.engine = create_engine(f"sqlite:///{_db_path}", connect_args={"check_same_thread": False})
database.SessionLocal.configure(bind=database.engine)

from fastapi.testclient import TestClient  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Item  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
    db = SessionLocal()
    db.query(Item).delete()
    db.commit()
    db.close()


@pytest.fixture
def item_names():
    def _names():
        db = SessionLocal()
        try:
            return sorted(name for (name,) in db.query(Item.name).all())
        finally:
            db.close()
    return _names
