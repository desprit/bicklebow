use crate::database::models::markets;
use crate::database::models::metrics;
use crate::database::queries;
use async_trait::async_trait;

#[async_trait]
pub trait MarketsSource {
    async fn read(&self) -> Result<Vec<markets::Market>, Box<dyn std::error::Error + Send + Sync>>;
}

#[async_trait]
pub trait MetricsSource {
    async fn read(
        &self,
        markets: Vec<markets::Market>,
    ) -> Result<Vec<metrics::Metric>, Box<dyn std::error::Error + Send + Sync>>;
}

impl TryFrom<metrics::SourceMetric> for metrics::Metric {
    type Error = String;

    fn try_from(source_metric: metrics::SourceMetric) -> Result<Self, Self::Error> {
        match queries::get_market_by_ticker(source_metric.market.as_str()) {
            Ok(market) => Ok(metrics::Metric {
                id: None,
                source: source_metric.source,
                is_signal: false,
                price: source_metric.price,
                volume: source_metric.volume,
                market_id: market.id,
                datetime: source_metric.datetime,
                created_at: None,
            }),
            // TODO: add to global logger
            Err(_) => {
                dbg!("Couldn't find market {}", &source_metric.market);
                return Err(String::from(format!(
                    "Couldn't find market {}",
                    source_metric.market
                )));
            }
        }
    }
}

impl TryFrom<markets::SourceMarket> for markets::Market {
    type Error = String;

    fn try_from(source_market: markets::SourceMarket) -> Result<Self, Self::Error> {
        match queries::get_market_by_ticker(source_market.ticker.as_str()) {
            Ok(market) => Ok(market),
            Err(_) => {
                dbg!("Couldn't find market {}", &source_market.ticker);
                return Err(String::from(format!(
                    "Couldn't find market {}",
                    source_market.ticker
                )));
            }
        }
    }
}

impl metrics::Metric {
    pub fn save(&self) -> Result<usize, rusqlite::Error> {
        queries::create_metric(self)
    }
}

#[cfg(test)]
mod tests {
    use crate::database::{mocks, utils};
    use serial_test::serial;

    #[test]
    #[serial]
    fn test_source_metric_into_metric() {
        utils::setup_db().unwrap();
        let market = mocks::get_market_mock().unwrap();
        super::queries::create_market(&market).unwrap();
        let source_metric = mocks::get_source_metric().unwrap();
        let _ = super::metrics::Metric::try_from(source_metric).unwrap();
        utils::teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_source_market_into_market() {
        utils::setup_db().unwrap();
        let market = mocks::get_market_mock().unwrap();
        super::queries::create_market(&market).unwrap();
        let source_market = mocks::get_source_market().unwrap();
        let _ = super::markets::Market::try_from(source_market).unwrap();
        utils::teardown_db().unwrap();
    }
}
