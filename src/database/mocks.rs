use crate::database::models;
use rand;
use rand::prelude::IteratorRandom;

pub fn get_metric_mocks() -> Vec<models::SourceData> {
    let metric = models::SourceData::Metric {
        source: String::from("test source"),
        market_id: 1,
        is_signal: false,
        created_at: String::from("test created_at"),
        value: 1000,
    };
    vec![metric]
}

pub fn get_metric_mock() -> Option<models::SourceData> {
    get_metric_mocks()
        .into_iter()
        .choose(&mut rand::thread_rng())
}

pub fn get_news_mocks() -> Vec<models::SourceData> {
    let metric = models::SourceData::News {
        source: String::from("test source"),
        market_id: 1,
        is_signal: false,
        created_at: String::from("test created_at"),
        value: String::from("test value"),
    };
    vec![metric]
}

pub fn get_news_mock() -> Option<models::SourceData> {
    get_news_mocks().into_iter().choose(&mut rand::thread_rng())
}

pub fn get_market_values() -> Vec<models::MarketValue> {
    let market_value = models::MarketValue {
        market: String::from("APPL"),
        period: models::Period::Current,
        price: 130000,
        qty: 1000,
    };
    vec![market_value]
}

pub fn get_market_value() -> Option<models::MarketValue> {
    get_market_values()
        .into_iter()
        .choose(&mut rand::thread_rng())
}

pub fn get_market_news_multiple() -> Vec<models::MarketNews> {
    let market_news = models::MarketNews {
        market: String::from("APPL"),
        text: String::from("test text"),
    };
    vec![market_news]
}

pub fn get_market_news() -> Option<models::MarketNews> {
    get_market_news_multiple()
        .into_iter()
        .choose(&mut rand::thread_rng())
}
