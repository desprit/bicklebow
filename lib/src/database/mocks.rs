use crate::database::models::markets;
use crate::database::models::metrics;
use chrono::prelude::Utc;
use rand;
use rand::prelude::IteratorRandom;

pub fn get_metric_mocks() -> Vec<metrics::Metric> {
    let metric = metrics::Metric {
        id: Some(1),
        source: String::from("tinkoff"),
        is_signal: false,
        price: 1000.00,
        volume: 100,
        market_id: Some(1),
        datetime: String::from("2022-02-01T04:00:00Z"),
        created_at: Some(Utc::now().to_string()),
    };
    vec![metric]
}

pub fn get_metric_mock() -> Option<metrics::Metric> {
    get_metric_mocks()
        .into_iter()
        .choose(&mut rand::thread_rng())
}

pub fn get_source_metrics() -> Vec<metrics::SourceMetric> {
    let metric = metrics::SourceMetric {
        source: String::from("tinkoff"),
        market: String::from("GAZP"),
        period: metrics::Period::Current,
        price: 130000.00,
        volume: 1000,
        datetime: String::from("2022-02-01T04:00:00Z"),
    };
    vec![metric]
}

pub fn get_source_metric() -> Option<metrics::SourceMetric> {
    get_source_metrics()
        .into_iter()
        .choose(&mut rand::thread_rng())
}

pub fn get_market_mocks() -> Vec<markets::Market> {
    let market = markets::Market {
        id: Some(1),
        ticker: String::from("GAZP"),
        label: String::from("Gazprom"),
        figi: Some(String::from("BBG004730RP0")),
        risk: 0,
        priority: 0,
        category: Some(markets::MarketCategory::Financial),
        created_at: Some(Utc::now().to_string()),
    };
    vec![market]
}

pub fn get_market_mock() -> Option<markets::Market> {
    get_market_mocks()
        .into_iter()
        .choose(&mut rand::thread_rng())
}

pub fn get_source_markets() -> Vec<markets::SourceMarket> {
    let source_market = markets::SourceMarket {
        figi: Some(String::from("BBG004730RP0")),
        ticker: String::from("GAZP"),
    };
    vec![source_market]
}

pub fn get_source_market() -> Option<markets::SourceMarket> {
    get_source_markets()
        .into_iter()
        .choose(&mut rand::thread_rng())
}
