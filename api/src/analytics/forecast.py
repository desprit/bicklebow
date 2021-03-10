"""
This module contains very primitive attempts to calculate expected
profit of different investing strategies.
E.g. every time the market goes up/down by X% we open/close position.
This strategy is then applied to a historical data to get the profit.
"""
import glob
import datetime

import typer

from api.src import schemas
from api.src import config
from api.src.analytics.portfolio import Portfolio


app = typer.Typer()

datetime.tzinfo = None


@app.command()
def calculate_profit():
    rules = [
        # Open new position when market is up by X% from the highest position in portfolio
        schemas.Rule(open_threshold=0.15),
        # Close all positions that are in profit by Y%
        schemas.Rule(close_threshold=0.2),
        # Open new position if market is down by X% from the lowest position in portfolio
        schemas.Rule(open_threshold=-0.1),
    ]
    candles = {}
    for path in glob.glob(f"{config.DATA_PATH}/candles/*.txt"):
        with open(path) as f:
            figi = path.split("/")[-1].split("-")[0]
            for line in f.readlines():
                candle = schemas.Candle.from_json(line.strip())
                candles.setdefault(figi, {}).setdefault(candle.time.isoformat(), candle)
        # break
    portfolio = Portfolio(
        rules,
        initial_value=1000.00,
        deposit_value=1000.00,
        debug=True,
        open_immediate=True,
    )
    s_date = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    e_date = datetime.datetime(2020, 12, 31, tzinfo=datetime.timezone.utc)
    c_date = s_date
    while c_date < e_date:
        portfolio.deposit_if_should(c_date)
        for figi, figi_candles in candles.items():
            if figi_candles.get(c_date.isoformat()):
                portfolio.check_candle(figi_candles[c_date.isoformat()])
        c_date += datetime.timedelta(hours=1)
    print(portfolio)


if __name__ == "__main__":
    app()
