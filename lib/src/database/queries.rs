use crate::database::models::markets;
use crate::database::models::metrics;
use crate::database::utils;
use chrono::prelude::Utc;
use rusqlite::params;
use rusqlite::types::{FromSql, FromSqlError, FromSqlResult, ToSql, ToSqlOutput, Value, ValueRef};
use std::str::FromStr;

impl ToSql for markets::MarketCategory {
    fn to_sql(&self) -> Result<ToSqlOutput, rusqlite::Error> {
        match self {
            _ => Ok(ToSqlOutput::Owned(Value::Text(self.to_string()))),
        }
    }
}

impl FromSql for markets::MarketCategory {
    fn column_result(value: ValueRef<'_>) -> FromSqlResult<Self> {
        markets::MarketCategory::from_str(value.as_str()?)
            .map_err(|x| FromSqlError::Other(x.into()))
    }
}

pub fn create_metric(metric: &metrics::Metric) -> Result<usize, rusqlite::Error> {
    let conn = utils::get_conn()?;
    conn.execute(
        "
            INSERT INTO metrics 
                (source, is_signal, price, volume, market_id, datetime, created_at)
            VALUES 
                (?1, ?2, ?3, ?4, ?5, ?6, ?7)
        ",
        params![
            metric.source,
            metric.is_signal,
            metric.price,
            metric.volume,
            metric.market_id,
            metric.datetime,
            Utc::now().to_string()
        ],
    )
}

pub fn create_market(market: &markets::Market) -> Result<usize, rusqlite::Error> {
    let conn = utils::get_conn()?;
    conn.execute(
        "
            INSERT OR IGNORE INTO markets 
                (ticker, label, figi, risk, priority, category, created_at)
            VALUES 
                (?1, ?2, ?3, ?4, ?5, ?6, ?7)
        ",
        params![
            market.ticker,
            market.label,
            market.figi,
            market.risk,
            market.priority,
            market.category,
            Utc::now().to_string()
        ],
    )
}

pub fn get_markets() -> Result<Vec<markets::Market>, rusqlite::Error> {
    let conn = utils::get_conn()?;
    let mut stmt = conn.prepare(
        "
        SELECT id, ticker, label, figi, risk, priority, category, created_at
        FROM markets;
    ",
    )?;
    let rows = stmt.query_map([], |row| {
        Ok(markets::Market {
            id: Some(row.get(0)?),
            ticker: row.get(1)?,
            label: row.get(2)?,
            figi: row.get(3)?,
            risk: row.get(4)?,
            priority: row.get(5)?,
            category: row.get(6)?,
            created_at: row.get(7)?,
        })
    })?;
    let mut markets: Vec<markets::Market> = Vec::new();
    for row in rows {
        markets.push(row?);
    }
    Ok(markets)
}

pub fn get_market_by_ticker(ticker: &str) -> Result<markets::Market, rusqlite::Error> {
    let conn = utils::get_conn()?;
    let mut stmt = conn.prepare(
        "
        SELECT id, ticker, label, figi, risk, priority, category, created_at
        FROM markets 
        WHERE ticker=?1;
    ",
    )?;
    stmt.query_row([ticker], |row| {
        Ok(markets::Market {
            id: Some(row.get(0)?),
            ticker: row.get(1)?,
            label: row.get(2)?,
            figi: row.get(3)?,
            risk: row.get(4)?,
            priority: row.get(5)?,
            category: row.get(6)?,
            created_at: row.get(7)?,
        })
    })
}

#[cfg(test)]
mod tests {
    use crate::database::mocks;
    use serial_test::serial;

    #[test]
    #[serial]
    fn test_can_insert_metric() {
        super::utils::setup_db().unwrap();
        let metric = mocks::get_metric_mock().unwrap();
        super::create_metric(&metric).unwrap();
        let conn = super::utils::get_conn().unwrap();
        let mut stmt = conn.prepare("SELECT COUNT(*) FROM metrics").unwrap();
        let count = stmt.query_row([], |row| row.get::<_, i32>(0)).unwrap();
        assert_eq!(count, 1);
        super::utils::teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_can_insert_market() {
        super::utils::setup_db().unwrap();
        let market = mocks::get_market_mock().unwrap();
        super::create_market(&market).unwrap();
        let conn = super::utils::get_conn().unwrap();
        let mut stmt = conn.prepare("SELECT COUNT(*) FROM markets").unwrap();
        let count = stmt.query_row([], |row| row.get::<_, i32>(0)).unwrap();
        assert_eq!(count, 1);
        super::utils::teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_can_get_market() {
        super::utils::setup_db().unwrap();
        let market = mocks::get_market_mock().unwrap();
        super::create_market(&market).unwrap();
        let market_db = super::get_market_by_ticker(market.ticker.as_str()).unwrap();
        assert_eq!(market_db.figi, market.figi);
        assert_eq!(market_db.category, market.category);
        super::utils::teardown_db().unwrap();
    }
}
