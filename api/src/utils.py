"""
Database queries and utility functions.
"""
from typing import List, Optional
from datetime import datetime, timedelta

import telegram
from sqlalchemy import desc
from sqlalchemy.orm.session import Session

from api.src import database, schemas
from api.src.config import settings


def clean_unused_triggers(
    user: schemas.User,
    triggers: List[schemas.Trigger],
    positions: List[schemas.PortfolioPosition],
    session: Session,
) -> None:
    """
    Remove triggers from the database for symbols that user no longer have.
    """
    tickers = [p.ticker for p in positions]
    unused_triggers = [t for t in triggers if (t.ticker and t.ticker not in tickers)]
    for trigger in unused_triggers:
        query = session.query(database.Trigger)
        query = query.filter(database.Trigger.user_id == user.id)
        query = query.filter(database.Trigger.ticker == trigger.ticker)
        query.delete()
        session.commit()


def get_user_triggers(user_id: int, session: Session) -> List[schemas.Trigger]:
    """
    Return triggers for a given user.
    """
    triggers = (
        session.query(database.Trigger)
        .filter(database.Trigger.user_id == user_id)
        .all()
    )
    return [schemas.Trigger.from_model(trigger) for trigger in triggers]


def get_user_alerts(user_id: int, session: Session) -> List[schemas.Alert]:
    """
    Return alerts for a given user.
    """
    alerts = (
        session.query(database.Alert)
        .order_by(desc(database.Alert.created_at))
        .filter(database.Alert.user_id == user_id)
        .limit(10)
    )
    return [schemas.Alert.from_model(alert) for alert in alerts]


def get_users(session: Session) -> List[schemas.User]:
    """
    Return a list of registered users.
    """
    users = session.query(database.User).all()
    return [schemas.User.from_model(user) for user in users]


def get_user_trigger_alerts(
    user_id: int, trigger_id: int, session: Session
) -> List[schemas.Alert]:
    """
    Return a list of alerts for a given user and trigger.
    """
    alerts = (
        session.query(database.Alert)
        .order_by(desc(database.Alert.created_at))
        .filter(database.Alert.user_id == user_id)
        .filter(database.Alert.trigger_id == trigger_id)
        .limit(10)
    )
    return [schemas.Alert.from_model(alert) for alert in alerts]


def get_user_by_username(username: str, session: Session) -> Optional[schemas.User]:
    query = session.query(database.User)
    user = query.filter(database.User.username == username).first()
    if user:
        return schemas.User.from_model(user)
    return None


def send_alert(
    user: schemas.User, trigger: schemas.Trigger, position: schemas.PortfolioPosition
) -> None:
    client = telegram.Bot(token=settings.BOT_TOKEN)
    text = f"{position.name}\n{str(trigger)}"
    client.sendMessage(chat_id=user.chat_id, text=text)


def save_alert(user: schemas.User, trigger: schemas.Trigger, session: Session) -> None:
    alert = {"trigger_id": trigger.id, "user_id": user.id}
    session.add(database.Alert(**alert))
    session.commit()


def should_ignore(trigger: schemas.Trigger) -> bool:
    """
    Ignore trigger if alert already present in the database.
    """
    alert_threshold = datetime.now() - timedelta(days=7)
    if trigger.reference == schemas.CandleRange.CANDLE_1D:
        alert_threshold = datetime.now() - timedelta(days=1)
    if trigger.reference == schemas.CandleRange.CANDLE_1M:
        alert_threshold = datetime.now() - timedelta(days=30)
    with database.get_db_session() as session:
        query = session.query(database.Alert)
        query = query.order_by(desc(database.Alert.created_at))
        query = query.filter(database.Alert.trigger_id == trigger.id)
        trigger_alerts: List[database.Alert] = query.all()
        for alert in trigger_alerts:
            if alert.created_at > alert_threshold:
                return True
        return False
