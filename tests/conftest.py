"""
This module contains general-scope fixtures.
"""
from typing import List
from datetime import datetime
from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api.src import schemas, database


@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    database.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def users() -> List[schemas.User]:
    tinkoff_users = [
        {
            "id": 0,
            "username": "gunnar",
            "token": "test-token",
            "chat_id": "test-chat_id",
        },
        {
            "id": 1,
            "username": "alamar",
            "token": "test-token",
            "chat_id": "test-chat_id",
        },
    ]
    return [schemas.User(**user) for user in tinkoff_users]


@pytest.fixture
def triggers(users) -> List[schemas.Trigger]:
    triggers = [
        [0, users[0].id, "TSLA", "CANDLE_1D", 20, "INCREASE"],
        [1, users[0].id, "BABA", "CANDLE_1M", 10, "DECREASE"],
        [2, users[0].id, "GOOG", "PORTFOLIO", 15, "DECREASE"],
        [3, users[0].id, "NTLA", "PORTFOLIO", 25, "INCREASE"],
    ]
    return [schemas.Trigger(*values) for values in triggers]


@pytest.fixture
def alerts(users, triggers) -> List[schemas.Alert]:
    alerts = [
        {
            "id": 0,
            "user_id": users[0].id,
            "trigger_id": triggers[0].id,
            "created_at": datetime.now(),
        },
        {
            "id": 1,
            "user_id": users[0].id,
            "trigger_id": triggers[1].id,
            "created_at": datetime.now(),
        },
    ]
    return [schemas.Alert(**alert) for alert in alerts]


@pytest.fixture
def session(
    in_memory_sqlite_db,
    triggers: List[schemas.Trigger],
    users: List[schemas.User],
    alerts: List[schemas.Alert],
) -> Session:
    session: Session = sessionmaker(bind=in_memory_sqlite_db)()
    user_models = [database.User(**user.to_dict()) for user in users]
    trigger_models = [database.Trigger(**trigger.to_dict()) for trigger in triggers]
    alert_models = [database.Alert(**alert.to_dict()) for alert in alerts]
    session.add_all([*user_models, *trigger_models, *alert_models])
    yield session
    session.commit()
    session.close()


@pytest.fixture
def get_db_session(session):
    @contextmanager
    def fn():
        yield session

    return fn()
