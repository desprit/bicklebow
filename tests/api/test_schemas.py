from api.src import schemas


def test_trigger_should_trigger_by_candle_price():
    """
    When price dropped below desired one.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.CandleRange.CANDLE_1D.value,
        threshold=5,
        direction=schemas.Direction.DECREASE.value,
    )
    candle_prices = {"CANDLE_1D": 1000, "CANDLE_1W": 980, "CANDLE_1M": 900}
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "TSLA",
            "current_price": 900,
            "candle_prices": candle_prices,
            "portfolio_price": None,
        }
    )
    assert trigger.is_triggered(position)


def test_trigger_should_trigger_by_portfolio_price():
    """
    When price spiked above desired one.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.TriggerReference.PORTFOLIO.value,
        threshold=5,
        direction=schemas.Direction.INCREASE.value,
    )
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "TSLA",
            "current_price": 1000,
            "candle_prices": None,
            "portfolio_price": 900,
        }
    )
    assert trigger.is_triggered(position)


def test_trigger_should_not_trigger_by_candle_price():
    """
    When price spiked but not high enough.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.CandleRange.CANDLE_1M.value,
        threshold=15,
        direction=schemas.Direction.INCREASE.value,
    )
    candle_prices = {"CANDLE_1D": 1000, "CANDLE_1W": 980, "CANDLE_1M": 900}
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "TSLA",
            "current_price": 1000,
            "candle_prices": candle_prices,
            "portfolio_price": None,
        }
    )
    assert trigger.is_triggered(position) is False


def test_trigger_should_not_trigger_by_portfolio_price():
    """
    When price dropped but not low enough.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.TriggerReference.PORTFOLIO.value,
        threshold=15,
        direction=schemas.Direction.DECREASE.value,
    )
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "TSLA",
            "current_price": 900,
            "candle_prices": None,
            "portfolio_price": 1000,
        }
    )
    assert trigger.is_triggered(position) is False


def test_trigger_should_not_trigger_if_tickers_are_different():
    """
    When trigger is not for the same ticker as position, return False.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.TriggerReference.PORTFOLIO.value,
        threshold=0.05,
        direction=schemas.Direction.INCREASE.value,
    )
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "BABA",
            "current_price": 1000,
            "candle_prices": None,
            "portfolio_price": 900,
        }
    )
    assert trigger.is_triggered(position) is False


def test_trigger_should_trigger_for_general_ticker():
    """
    When ticker value is not set, trigger should proceed normally.
    """
    trigger = schemas.Trigger(
        0,
        0,
        ticker=None,
        reference=schemas.TriggerReference.PORTFOLIO.value,
        threshold=0.05,
        direction=schemas.Direction.INCREASE.value,
    )
    position = schemas.PortfolioPosition(
        **{
            "name": "Tesla",
            "ticker": "BABA",
            "current_price": 1000,
            "candle_prices": None,
            "portfolio_price": 900,
        }
    )
    assert trigger.is_triggered(position)


def test_trigger_return_message():
    trigger = schemas.Trigger(
        0,
        0,
        ticker="TSLA",
        reference=schemas.TriggerReference.PORTFOLIO.value,
        threshold=0.15,
        direction=schemas.Direction.INCREASE.value,
    )
    assert str(trigger) == f"Increased by more than {trigger.threshold}% from portfolio"
