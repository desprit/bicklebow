use crate::database::queries;
use crate::sources::tinkoff;

pub async fn init_markets() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let markets = tinkoff::get_markets().await?;
    for market in &markets {
        queries::create_market(&market)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::database::utils;
    use serial_test::serial;

    #[tokio::test]
    #[serial]
    async fn get_init_markets_should_work() {
        utils::setup_db().unwrap();
        assert_eq!(super::queries::get_markets().unwrap().len(), 0);
        super::init_markets().await.unwrap();
        assert_ne!(super::queries::get_markets().unwrap().len(), 0);
        utils::teardown_db().unwrap();
    }
}
