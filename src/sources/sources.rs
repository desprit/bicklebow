use crate::database::{models, queries};

pub trait Source {
    fn read(&self) -> Vec<models::SourceData>;
}

pub struct TinkoffMarketValuesSource {}
pub struct TinkoffMarketNewsSource {}

impl Into<models::SourceData> for models::MarketValue {
    fn into(self) -> models::SourceData {
        models::SourceData::Metric {
            source: String::from("test source"),
            created_at: String::from("test created_at"),
            is_signal: false,
            value: 1000,
            market_id: 1,
        }
    }
}

impl Into<models::SourceData> for models::MarketNews {
    fn into(self) -> models::SourceData {
        models::SourceData::News {
            source: String::from("test source"),
            created_at: String::from("test created_at"),
            is_signal: false,
            value: String::from("test_value"),
            market_id: 1,
        }
    }
}

impl Source for TinkoffMarketValuesSource {
    fn read(&self) -> Vec<models::SourceData> {
        // Logic to send Tinkoff API request and receive data
        let market_values: Vec<models::MarketValue> = vec![];
        market_values.into_iter().map(|m| m.into()).collect()
    }
}

impl Source for TinkoffMarketNewsSource {
    fn read(&self) -> Vec<models::SourceData> {
        // Logic to parse Tinkoff news feed
        let market_news: Vec<models::MarketNews> = vec![];
        market_news.into_iter().map(|m| m.into()).collect()
    }
}

impl models::SourceData {
    pub fn save(&self) -> Result<usize, rusqlite::Error> {
        queries::create_source_data(self)
    }
}

#[cfg(test)]
mod tests {
    use super::Source;
    use crate::database::mocks;

    #[test]
    fn test_can_read_tinkoff_market_values() {
        let t = super::TinkoffMarketValuesSource {};
        t.read();
    }

    #[test]
    fn test_can_read_tinkoff_market_news() {
        let t = super::TinkoffMarketNewsSource {};
        t.read();
    }

    #[test]
    fn test_market_values_into_source_data() {
        let market_value = mocks::get_market_value().unwrap();
        let source_data: super::models::SourceData = market_value.into();
        match &source_data {
            super::models::SourceData::Metric { .. } => assert!(true),
            super::models::SourceData::News { .. } => assert!(false),
        }
    }

    #[test]
    fn test_market_news_into_source_data() {
        let market_news = mocks::get_market_news().unwrap();
        let source_data: super::models::SourceData = market_news.into();
        match &source_data {
            super::models::SourceData::Metric { .. } => assert!(false),
            super::models::SourceData::News { .. } => assert!(true),
        }
    }
}
