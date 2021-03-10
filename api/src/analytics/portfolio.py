import datetime
from typing import List, Dict, Tuple, Optional

from api.src import schemas


class Portfolio:

    rules: List[schemas.Rule]
    open_immediate: bool
    initial_value: float
    deposit_value: float
    debug: bool
    positions: Dict[str, List[schemas.Position]] = {}
    deposits: List[schemas.Deposit] = []
    history: List[schemas.ClosedPosition] = []
    balance = 0

    def __init__(
        self,
        rules: List[schemas.Rule],
        open_immediate=False,
        initial_value=0,
        deposit_value=0,
        debug=False,
    ):
        """
        Param `open_immediate` - open new position right after closing
        Param `initial_value` - initial amount of money in portfolio
        """
        self.rules = rules
        self.open_immediate = open_immediate
        self.initial_value = initial_value
        self.deposit_value = deposit_value
        self.debug = debug
        for rule in self.rules:
            if rule.close_threshold and rule.close_threshold < 0:
                raise NotImplementedError("Don't close with loss!")

    def __repr__(self) -> str:
        response = ""
        positions = "\n".join(
            [f"Number of opened for {k}: {len(v)}" for k, v in self.positions.items()]
        )
        response += "==========\n"
        response += f"{positions}\n"
        response += f"Deposited: {round(self.deposited)}$\n"
        response += f"Currently invested: {round(self.invested)}$\n"
        response += f"Balance: {round(self.balance)}$\n"
        response += f"Profit: {round(self.profit)}$ ({round(self.profit / self.deposited * 100)}%)\n"
        response += "=========="
        return response

    @property
    def deposited(self) -> float:
        return sum([d.amount for d in self.deposits])

    @property
    def invested(self) -> float:
        return sum([_p.value for p in self.positions.values() for _p in p])

    @property
    def profit(self) -> float:
        return sum([self.calculate_profit(p) for p in self.history])

    def deposit_if_should(self, d: datetime.datetime) -> None:
        deposits = None
        if self.deposits:
            deposits = sorted(self.deposits, key=lambda d: d.time, reverse=True)
        if not self.deposits or (deposits[0].time + datetime.timedelta(days=30)) < d:
            self.deposits.append(schemas.Deposit(time=d, amount=self.deposit_value))
            self.balance += self.deposit_value

    def min_position_for_market(self, figi: str) -> float:
        return 50

    def check_candle(self, candle: schemas.Candle) -> None:
        result, reason = self.apply_rules(candle)
        if result == 1:
            return self.open_position_for_candle(candle, reason)
        if result == -1:
            return self.close_position_for_candle(candle, reason)

    def apply_rules(self, candle: schemas.Candle) -> Tuple[int, Optional[str]]:
        if candle.figi not in self.positions or not self.positions[candle.figi]:
            return 1, "first position"
        max_position = max(self.positions[candle.figi], key=lambda p: p.price)
        min_position = min(self.positions[candle.figi], key=lambda p: p.price)
        for rule in self.rules:
            if rule.open_threshold:
                # When candle price is above the highest in portfolio by x%
                if rule.open_threshold > 0:
                    price = max_position.price
                    threshold = price + (rule.open_threshold * price)
                    if candle.o > threshold:
                        if self.debug:
                            print(
                                f"Rule {rule.open_threshold*100}%, portfolio: {price}, candle: {candle.o}"
                            )
                        return 1, "above portfolio"
                # When candle price is below the lowest in portfolio by x%
                if rule.open_threshold < 0:
                    price = min_position.price
                    threshold = price + (rule.open_threshold * price)
                    if candle.o < threshold:
                        if self.debug:
                            print(
                                f"Rule {rule.open_threshold*100}%, portfolio: {price}, candle: {candle.o}"
                            )
                        return 1, "below portfolio"
            if rule.close_threshold:
                price = min_position.price
                threshold = price + (rule.close_threshold * price)
                if rule.close_threshold > 0 and candle.o > threshold:
                    if self.debug:
                        print(
                            f"Rule {rule.close_threshold*100}%, portfolio: {price}, candle: {candle.o}"
                        )
                    return -1, "above portfolio"
        return 0, None

    def open_position_for_candle(self, candle: schemas.Candle, reason: str) -> None:
        invested_for_figi = 0
        if candle.figi in self.positions:
            invested_for_figi = sum([p.value for p in self.positions[candle.figi]])
        allowed_amount = (self.invested + self.balance) / (
            len(self.positions.keys()) or 1
        )
        min_amount = self.min_position_for_market(candle.figi)
        open_amount = allowed_amount - invested_for_figi
        if allowed_amount < invested_for_figi or open_amount < min_amount:
            if self.debug:
                print(f"Already overinvested in {candle.figi}, skipping\n")
            return
        if reason == "above portfolio":
            open_amount = (
                open_amount / 5 if open_amount / 5 > min_amount else open_amount
            )
        else:
            open_amount = (
                open_amount / 2 if open_amount / 2 > min_amount else open_amount
            )
        if self.debug:
            print(f"Opening new position for {candle.figi} because {reason}")
        position = schemas.Position(candle.figi, candle.o, open_amount, candle.time)
        self.positions.setdefault(candle.figi, []).append(position)
        self.balance -= position.value
        if self.debug:
            print(f"Opened position for {candle.figi}\n")

    def close_position_for_candle(self, candle: schemas.Candle, reason: str) -> None:
        if self.debug:
            print(f"Closing position for {candle.figi} because {reason}")
        min_position = min(self.positions[candle.figi], key=lambda p: p.price)
        self.positions[candle.figi] = [
            p for p in self.positions[candle.figi] if p != min_position
        ]
        closed_position = schemas.ClosedPosition(min_position, candle.time, candle.o)
        self.history.append(closed_position)
        self.balance += closed_position.position.value
        self.balance += self.calculate_profit(closed_position)
        if self.debug:
            print(f"Closed position for {candle.figi}\n")
        if self.open_immediate:
            self.open_position_for_candle(candle, "open_immediate is True")

    def calculate_profit(self, position: schemas.ClosedPosition) -> float:
        return (
            position.close_price / position.position.price * position.position.value
            - position.position.value
        )
