import datetime
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

from tinvest import schemas

from api.src import database


class CandleRange(Enum):
    CANDLE_1D = "CANDLE_1D"  # Candle for the past day
    CANDLE_1W = "CANDLE_1W"  # Candle for the past week
    CANDLE_1M = "CANDLE_1M"  # Candle for the last month


class TriggerReference(Enum):
    CANDLE = CandleRange  # Candle for the past period
    PORTFOLIO = "PORTFOLIO"  # Average portfolio price


class Direction(Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"


@dataclass
class MarketValue:
    ticker: str
    current_price: float
    candle_1d_price: float
    candle_1w_price: float
    candle_1m_price: float


@dataclass
class PortfolioPosition:
    name: str
    ticker: str
    current_price: float
    candle_prices: Dict[str, float]
    portfolio_price: float


@dataclass
class User:
    id: int
    token: str
    username: str
    chat_id: str

    @classmethod
    def from_model(cls, model: database.User):
        return cls(
            **{
                "id": model.id,
                "token": model.token,
                "chat_id": model.chat_id,
                "username": model.username,
            }
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "token": self.token,
            "chat_id": self.chat_id,
            "username": self.username,
        }


@dataclass
class Alert:
    id: int
    user_id: int
    trigger_id: int
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: database.Alert):
        return cls(
            **{
                "id": model.id,
                "user_id": model.user_id,
                "trigger_id": model.trigger_id,
                "created_at": model.created_at,
            }
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "trigger_id": self.trigger_id,
            "created_at": self.created_at,
        }


@dataclass
class Trigger:
    id: int
    user_id: int
    ticker: Optional[str]  # Market name, e.g. TSLA
    reference: TriggerReference
    threshold: float
    direction: Optional[Direction]

    def __init__(
        self,
        id: int,
        user_id: int,
        ticker: str,
        reference: str,
        threshold: str,
        direction: str,
    ):
        self.id = id
        self.user_id = user_id
        self.ticker = ticker
        self.threshold = threshold
        self.direction = Direction[direction]
        if "CANDLE" in reference:
            self.reference = CandleRange[reference]
        else:
            self.reference = TriggerReference[reference]

    @classmethod
    def from_model(cls, model: database.Trigger):
        return cls(
            model.id,
            model.user_id,
            model.ticker,
            model.reference,
            model.threshold,
            model.direction,
        )

    def __str__(self) -> str:
        action = "dropped" if self.direction == Direction.DECREASE else "increased"
        reference = "from portfolio"
        if self.reference == CandleRange.CANDLE_1D:
            reference = "in a day"
        if self.reference == CandleRange.CANDLE_1W:
            reference = "in a week"
        if self.reference == CandleRange.CANDLE_1M:
            reference = "in a month"
        return f"{action.title()} by more than {self.threshold}% {reference}"

    def is_triggered(self, position: schemas.PortfolioPosition) -> bool:
        if self.ticker and position.ticker != self.ticker:
            return False
        if self.reference == TriggerReference.PORTFOLIO:
            return self._is_triggered_by_reference(
                position.portfolio_price, position.current_price
            )
        if self.reference in TriggerReference.CANDLE.value:
            candle_price = position.candle_prices[self.reference.value]
            return self._is_triggered_by_reference(candle_price, position.current_price)
        raise TypeError(f"Reference {self.reference} unknown")

    def _is_triggered_by_reference(
        self, reference_price: float, current_price: float
    ) -> bool:
        if self.direction == Direction.INCREASE:
            if current_price < reference_price:
                return False
        if self.direction == Direction.DECREASE:
            if current_price > reference_price:
                return False
        if abs(1 - current_price / reference_price) * 100 > self.threshold:
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ticker": self.ticker,
            "reference": self.reference.value,
            "threshold": self.threshold,
            "direction": self.direction.value,
        }


class ServerStartMode(Enum):
    POLLING = "POLLING"
    WEBHOOK = "WEBHOOK"
