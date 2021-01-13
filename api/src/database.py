"""
SQLAlchemy table models.
"""
from typing import Iterator
from datetime import datetime as dt
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Float, ForeignKey

from api.src.config import settings


Base = declarative_base()
USERS_TABLE = "users"
ALERTS_TABLE = "alerts"
TRIGGERS_TABLE = "triggers"


class Trigger(Base):
    __tablename__ = TRIGGERS_TABLE

    id = Column(Integer, primary_key=True)

    ticker = Column(String(16))
    reference = Column(String(16), nullable=False)
    direction = Column(String(16), nullable=False)
    threshold = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)
    updated_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Alert(Base):
    __tablename__ = ALERTS_TABLE

    id = Column(Integer, primary_key=True)

    ticker = Column(String(16))
    created_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)
    updated_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)

    trigger_id = Column(
        Integer, ForeignKey("triggers.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class User(Base):
    __tablename__ = USERS_TABLE

    id = Column(Integer, primary_key=True)

    token = Column(String(96), nullable=False)
    chat_id = Column(String(96), nullable=False)
    username = Column(String(48), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)
    updated_at = Column(TIMESTAMP, default=dt.utcnow(), nullable=False)


def get_db_engine():
    engine = create_engine(settings.SQLITE_URI)
    return engine


@contextmanager
def get_db_session(engine=None) -> Iterator[Session]:
    engine = get_db_engine() if not engine else engine
    session = sessionmaker(bind=engine)()
    try:
        yield session
        session.commit()
    finally:
        session.close()


def init_db() -> None:
    engine = get_db_engine()
    Base.metadata.create_all(engine)


def drop_db() -> None:
    engine = get_db_engine()
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    # drop_db()
    init_db()
