extern crate tinkoff_invest;

use crate::database::models::markets;
use crate::database::models::metrics;
use crate::sources::sources;
use async_trait::async_trait;
use chrono::{Duration, Utc};
use tinkoff_invest::{CandlestickResolution, TinkoffInvest};

const TOKEN: &str =
    "t.YedLHH1iR2tn6T3GzlhlNMvtHqcNJxZAsH3LX7S83NXzZ62fdQKGW5b6nkfcfXCQ-y3pFpGQhf-aN90cHiRfPQ";
const SOURCE_NAME: &str = "tinkoff";

pub struct TinkoffMetricsSource {}
pub struct TinkoffMarketsSource {}

impl From<metrics::Period> for CandlestickResolution {
    fn from(period: metrics::Period) -> Self {
        match period {
            metrics::Period::Hour => CandlestickResolution::HOUR,
            metrics::Period::Day => CandlestickResolution::DAY,
            metrics::Period::Week => CandlestickResolution::WEEK,
            metrics::Period::Month => CandlestickResolution::MONTH,
            metrics::Period::Current => CandlestickResolution::MIN1,
        }
    }
}

pub async fn get_markets() -> Result<Vec<markets::Market>, Box<dyn std::error::Error + Send + Sync>>
{
    let tinkoff = TinkoffInvest::new(TOKEN);
    let bonds = tinkoff.stock_market_instruments().await?;
    Ok(bonds
        .iter()
        .map(|x| markets::Market {
            id: None,
            ticker: x.ticker.clone(),
            label: x.name.clone(),
            figi: Some(x.figi.clone()),
            risk: 0,
            priority: 0,
            category: None, // TODO
            created_at: None,
        })
        .collect())
}

pub async fn get_portfolio_markets(
) -> Result<Vec<markets::SourceMarket>, Box<dyn std::error::Error + Send + Sync>> {
    let tinkoff = TinkoffInvest::new(TOKEN);
    let portfolio = tinkoff.portfolio(None).await?;
    Ok(portfolio
        .into_iter()
        .filter(|x| x.ticker.is_some())
        .map(|x| markets::SourceMarket {
            figi: Some(x.figi),
            ticker: x.ticker.unwrap(), // TODO: unwrap?
        })
        .collect())
}

pub async fn get_metrics(
    markets: Vec<markets::Market>,
) -> Result<Vec<metrics::SourceMetric>, Box<dyn std::error::Error + Send + Sync>> {
    let now = Utc::now();
    let tinkoff = TinkoffInvest::new(TOKEN);
    let intervals = vec![
        (now - Duration::minutes(2), now, metrics::Period::Current),
        (now - Duration::hours(2), now, metrics::Period::Hour),
        (now - Duration::days(2), now, metrics::Period::Day),
        (now - Duration::days(14), now, metrics::Period::Week),
        (now - Duration::days(60), now, metrics::Period::Month),
    ];
    let mut source_metrics: Vec<metrics::SourceMetric> = vec![];
    for market in markets {
        dbg!("Requesting metrics for {}", &market.ticker);
        for (from, to, interval) in &intervals {
            if let Some(figi) = &market.figi {
                let candles = tinkoff
                    .candlesticks(
                        *from,
                        *to,
                        figi.as_str(),
                        CandlestickResolution::from(*interval),
                    )
                    .await?;
                if let Some(candle) = candles.last() {
                    source_metrics.push(metrics::SourceMetric {
                        source: String::from(SOURCE_NAME),
                        market: market.ticker.clone(),
                        period: *interval,
                        price: (candle.open + candle.close) / 2.,
                        volume: candle.volume,
                        datetime: candle.datetime.clone(),
                    });
                }
            }
        }
    }
    Ok(source_metrics)
}

#[async_trait]
impl sources::MetricsSource for TinkoffMetricsSource {
    async fn read(
        &self,
        markets: Vec<markets::Market>,
    ) -> Result<Vec<metrics::Metric>, Box<dyn std::error::Error + Send + Sync>> {
        Ok(get_metrics(markets)
            .await?
            .into_iter()
            .filter_map(|m| metrics::Metric::try_from(m).ok())
            .collect())
    }
}

#[async_trait]
impl sources::MarketsSource for TinkoffMarketsSource {
    async fn read(&self) -> Result<Vec<markets::Market>, Box<dyn std::error::Error + Send + Sync>> {
        Ok(get_portfolio_markets()
            .await?
            .into_iter()
            .filter_map(|m| markets::Market::try_from(m).ok())
            .collect())
    }
}

#[cfg(test)]
mod tests {
    use crate::database::mocks;

    #[tokio::test]
    async fn test_can_get_portfolio_markets() {
        let markets = super::get_portfolio_markets().await.unwrap();
        dbg!(markets);
    }

    #[tokio::test]
    async fn test_can_get_metrics() {
        let markets = mocks::get_market_mocks();
        let metrics = super::get_metrics(markets).await.unwrap();
        dbg!(metrics);
    }

    #[tokio::test]
    async fn test_can_get_markets() {
        let markets = super::get_markets().await.unwrap();
        dbg!(markets);
    }
}
