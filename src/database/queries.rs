use crate::database::{models, utils};
use rusqlite::params;

pub fn create_source_data(data: &models::SourceData) -> Result<usize, rusqlite::Error> {
    let conn = utils::get_conn()?;
    match data {
        models::SourceData::Metric {
            source,
            is_signal,
            created_at,
            value,
            market_id,
        } => conn.execute(
            "
                    INSERT OR IGNORE INTO metrics (source, is_signal, value, market_id, created_at)
                    VALUES (?1, ?2, ?3, ?4, ?5)
                ",
            params![source, is_signal, value, market_id, created_at],
        ),
        models::SourceData::News {
            source,
            is_signal,
            created_at,
            value,
            market_id,
        } => conn.execute(
            "
                    INSERT OR IGNORE INTO news (source, is_signal, value, market_id, created_at)
                    VALUES (?1, ?2, ?3, ?4, ?5)
                ",
            params![source, is_signal, value, market_id, created_at],
        ),
    }
}

pub fn update_item() {}

pub fn delete_item() {}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::database::mocks;
    use serial_test::serial;

    #[test]
    #[serial]
    fn test_can_insert_metrics() {
        utils::setup_db().unwrap();
        let metrics = mocks::get_metric_mock().unwrap();
        create_source_data(&metrics).unwrap();
        let conn = utils::get_conn().unwrap();
        let mut stmt = conn.prepare("SELECT COUNT(*) FROM metrics").unwrap();
        let count = stmt.query_row([], |row| row.get::<_, i32>(0)).unwrap();
        assert_eq!(count, 1);
        utils::teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_can_insert_news() {
        utils::setup_db().unwrap();
        let news = mocks::get_news_mock().unwrap();
        create_source_data(&news).unwrap();
        let conn = utils::get_conn().unwrap();
        let mut stmt = conn.prepare("SELECT COUNT(*) FROM news").unwrap();
        let count = stmt.query_row([], |row| row.get::<_, i32>(0)).unwrap();
        assert_eq!(count, 1);
        utils::teardown_db().unwrap();
    }
}
