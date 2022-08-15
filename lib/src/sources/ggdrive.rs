use crate::database::models::markets;
use crate::sources::sources;
use async_trait::async_trait;

pub struct GoogleDriveMarketsSource {}

#[async_trait]
impl sources::MarketsSource for GoogleDriveMarketsSource {
    async fn read(&self) -> Result<Vec<markets::Market>, Box<dyn std::error::Error + Send + Sync>> {
        // Logic to send Tinkoff API request and receive data
        let values: Vec<markets::SourceMarket> = vec![];
        Ok(values
            .into_iter()
            .filter_map(|m| markets::Market::try_from(m).ok())
            .collect())
    }
}

#[cfg(test)]
mod tests {}
