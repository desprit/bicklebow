import time
import json
import datetime
from typing import List, Dict, Optional, Tuple

import typer
import tinvest
import requests
from tinvest.schemas import CandleResolution

from api.src import schemas, database, utils


app = typer.Typer()


def create_market_values_from_response(
    response: requests.Response, symbol_prices: Dict[str, Dict[CandleResolution, float]]
) -> List[schemas.MarketValue]:
    content = json.loads(response.text)
    market_values = []
    for value in content["payload"]["values"]:
        candle_prices = symbol_prices[value["symbol"]["ticker"]]
        market_values.append(
            schemas.MarketValue(
                ticker=value["symbol"]["ticker"],
                current_price=value["price"]["value"],
                candle_1d_price=candle_prices[CandleResolution.day],
                candle_1w_price=candle_prices[CandleResolution.week],
                candle_1m_price=candle_prices[CandleResolution.month],
            )
        )
    return market_values


def get_portfolio_markets_from_response(
    response: tinvest.schemas.PortfolioResponse,
) -> Dict[tinvest.schemas.InstrumentType, Tuple[str, str]]:
    """
    Example:
    >>> get_portfolio_markets_from_response(response)
    {<InstrumentType.stock: 'Stock'>: [('GAZP', 'BBG004730RP0'), ('BABA', 'BBG006G2JVL2'), ...], ...}
    """
    portfolio_markets = {}
    for position in response.payload.positions:
        # This probably corresponds to remaining USD balance on account
        if position.ticker == "USD000UTSTOM":
            continue
        portfolio_markets.setdefault(position.instrument_type, []).append(
            (position.ticker, position.figi)
        )
    return portfolio_markets


def get_portfolio_positions_from_response(
    response: tinvest.schemas.PortfolioResponse,
    market_values: List[schemas.MarketValue],
) -> List[schemas.PortfolioPosition]:
    portfolio_positions = []
    for position in response.payload.positions:
        # This probably corresponds to remaining USD balance on account
        if position.ticker == "USD000UTSTOM":
            continue
        market_value = next(m for m in market_values if m.ticker == position.ticker)
        portfolio_positions.append(
            schemas.PortfolioPosition(
                name=position.name,
                ticker=position.ticker,
                candle_prices={
                    "CANDLE_1D": market_value.candle_1d_price,
                    "CANDLE_1W": market_value.candle_1w_price,
                    "CANDLE_1M": market_value.candle_1m_price,
                },
                portfolio_price=float(position.average_position_price.value),
                current_price=market_value.current_price,
            )
        )
    return portfolio_positions


def get_avg_prices_from_candles(
    client: tinvest.SyncClient, figi: str
) -> Dict[CandleResolution, float]:

    prices = {}
    now = datetime.datetime.now()
    periods = [
        [now - datetime.timedelta(days=1), now, CandleResolution.day],
        [now - datetime.timedelta(days=7), now, CandleResolution.week],
        [now - datetime.timedelta(days=30), now, CandleResolution.month],
    ]
    for period in periods:
        response = client.get_market_candles(
            figi, period[0], period[1], CandleResolution.day
        )
        h = float(response.payload.candles[0].h)
        l = float(response.payload.candles[0].l)
        avg = round((h + l) / 2, 2)
        prices[period[2]] = avg
    return prices


def get_market_values(
    client: tinvest.SyncClient,
    markets: Dict[tinvest.schemas.InstrumentType, Tuple[str, str]],
) -> List[schemas.MarketValue]:
    market_values = []
    for instrument_type, symbols in markets.items():
        symbol_prices = {}
        for symbol in symbols:
            prices = get_avg_prices_from_candles(client, symbol[1])
            symbol_prices[symbol[0]] = prices
        url = "https://www.tinkoff.ru/api/trading/stocks/list"
        if instrument_type == tinvest.schemas.InstrumentType.etf:
            url = "https://www.tinkoff.ru/api/trading/etfs/list"
        if instrument_type == tinvest.schemas.InstrumentType.currency:
            url = "https://www.tinkoff.ru/api/trading/currency/list"
        headers = {"content-type": "application/json"}
        tickers = [s[0] for s in symbols]
        payload = {
            "tickers": tickers,
            "start": 0,
            "end": 100,
            "sortType": "ByName",
            "orderType": "Asc",
            "country": "All",
        }
        r = requests.post(url, headers=headers, json=payload)
        market_values.extend(create_market_values_from_response(r, symbol_prices))
    return market_values


def get_user(user_id: int) -> Optional[schemas.User]:
    with database.get_db_session() as session:
        user = session.query(database.User).filter(database.User.id == user_id).first()
        if not user:
            print(f"User with ID {user_id} not found")
            return
        return schemas.User.from_model(user)


def get_candles(figi: str) -> List[schemas.Candle]:
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 12, 31)
    with database.get_db_session() as session:
        user = session.query(database.User).first()
        client = tinvest.SyncClient(user.token)
    candles = set()
    f = datetime.datetime.now() - datetime.timedelta(days=65)
    t = datetime.datetime.now() - datetime.timedelta(days=60)
    current_date = start_date
    while current_date < end_date:
        f = current_date
        t = f + datetime.timedelta(days=5)
        print(f"Extracting candles between {f.date()} and {t.date()}...")
        response = client.get_market_candles(figi, f, t, CandleResolution.hour)
        for i in response.payload.candles:
            candles.add(
                schemas.Candle(
                    time=i.time,
                    figi=i.figi,
                    o=float(i.o),
                    c=float(i.c),
                    h=float(i.h),
                    l=float(i.l),
                )
            )
        current_date += datetime.timedelta(days=4)
        time.sleep(1)
    return candles


def save_candles(figi: str, candles: List[schemas.Candle]):
    candles_sorted = list(candles)
    candles_sorted.sort(key=lambda x: x.time)
    with open(f"./data/candles/{figi}-1h.txt", "w") as w:
        for candle in candles_sorted:
            w.write(candle.to_json())
            w.write("\n")


@app.command()
def get_user_positions(user_id: int) -> List[schemas.PortfolioPosition]:
    """
    Return positions for a given user together with current market price
    and candle prices for the past day, week and month.
    """
    user = get_user(user_id)
    if not user:
        return []
    client = tinvest.SyncClient(user.token)
    response = client.get_portfolio()
    portfolio_markets = get_portfolio_markets_from_response(response)
    market_values = get_market_values(client, portfolio_markets)
    portfolio_positions = get_portfolio_positions_from_response(response, market_values)
    print(portfolio_positions)
    return portfolio_positions


@app.command()
def download_candles(figi: str) -> None:
    candles = get_candles(figi)
    save_candles(figi, candles)


@app.command()
def get_markets(user_id: int) -> None:
    with database.get_db_session() as session:
        user = utils.get_user_by_id(user_id, session)
        if not user:
            return
    client = tinvest.SyncClient(user.token)
    response = client.get_market_stocks()
    for instrument in response.payload.instruments:
        print(
            instrument.figi,
            instrument.name,
            instrument.ticker,
            instrument.lot,
            instrument.min_quantity,
        )


@app.command()
def get_positions(user_id: int) -> None:
    with database.get_db_session() as session:
        user = utils.get_user_by_id(user_id, session)
        if not user:
            return
    client = tinvest.SyncClient(user.token)
    response = client.get_portfolio()
    for position in response.payload.positions:
        print(position.__dict__)


if __name__ == "__main__":
    app()
