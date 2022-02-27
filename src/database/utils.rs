#![allow(dead_code)]
use crate::config::SETTINGS;
use rusqlite::{Connection, Result};

use std::fmt;

#[derive(Debug)]
pub enum CustomError {
    UnexpectedTableError,
}

impl std::error::Error for CustomError {}

impl fmt::Display for CustomError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            CustomError::UnexpectedTableError => write!(f, "Table is not defined in Settings"),
        }
    }
}

pub fn get_conn() -> Result<rusqlite::Connection, rusqlite::Error> {
    let conn = Connection::open(SETTINGS.sqlite.path);
    conn
}

pub fn delete_database() -> std::io::Result<()> {
    if std::path::Path::new(SETTINGS.sqlite.path).exists() {
        return std::fs::remove_file(SETTINGS.sqlite.path);
    }
    Ok(())
}

pub fn create_tables() -> Result<(), Box<dyn std::error::Error>> {
    let conn = get_conn()?;
    for (_, table_path) in &SETTINGS.sqlite.tables {
        let sql = std::fs::read_to_string(table_path)?;
        conn.execute(sql.as_str(), [])?;
    }
    Ok(())
}

pub fn create_table(table_name: &str) -> Result<usize, Box<dyn std::error::Error>> {
    let conn = get_conn()?;
    match SETTINGS.sqlite.tables.contains_key(table_name) {
        true => {
            let sql_path = &SETTINGS.sqlite.tables[table_name];
            let sql = std::fs::read_to_string(sql_path)?;
            return conn.execute(&sql, []).map_err(|e| e.into());
        }
        false => return Err(CustomError::UnexpectedTableError.into()),
    };
}

pub fn delete_tables() -> Result<(), Box<dyn std::error::Error>> {
    delete_database()?;
    get_conn()?;
    Ok(())
}

pub fn delete_table(table_name: &str) -> Result<usize, rusqlite::Error> {
    let conn = get_conn()?;
    let sql = format!("DROP TABLE IF EXISTS {};", table_name);
    conn.execute(sql.as_str(), [])
}

pub fn truncate_table(table_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    delete_table(table_name)?;
    create_table(table_name)?;
    Ok(())
}

pub fn setup_db() -> Result<(), Box<dyn std::error::Error>> {
    delete_tables()?;
    create_tables()?;
    Ok(())
}

pub fn teardown_db() -> Result<(), Box<dyn std::error::Error>> {
    delete_database()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{setup_db, teardown_db};
    use serial_test::serial;

    fn get_table_names() -> Vec<String> {
        let conn = super::get_conn().unwrap();
        let mut stmt = conn
            .prepare(
                "SELECT name
                FROM sqlite_schema
                WHERE type ='table' AND name NOT LIKE 'sqlite_%';",
            )
            .unwrap();
        let rows = stmt.query_map([], |row| row.get::<_, String>(0)).unwrap();
        let mut table_names = Vec::new();
        for row in rows {
            table_names.push(row.unwrap());
        }
        table_names
    }

    #[test]
    #[serial]
    fn test_get_conn_creates_db_file() {
        std::fs::remove_file(super::SETTINGS.sqlite.path).ok();
        super::get_conn().ok();
        assert!(std::path::Path::new(super::SETTINGS.sqlite.path).exists());
    }

    #[test]
    #[serial]
    fn test_get_conn_returns_connection() {
        let conn = super::get_conn();
        assert!(conn.is_ok());
    }

    #[test]
    #[serial]
    fn test_delete_database_should_delete_file_when_exists() {
        super::get_conn().unwrap();
        assert!(std::path::Path::new(super::SETTINGS.sqlite.path).exists());
        super::delete_database().unwrap();
        assert!(!std::path::Path::new(super::SETTINGS.sqlite.path).exists());
    }

    #[test]
    #[serial]
    fn test_create_tables_should_create_all_tables_from_models() {
        super::delete_database().unwrap();
        super::create_tables().unwrap();
        let table_names = get_table_names();
        assert!(super::SETTINGS
            .sqlite
            .tables
            .keys()
            .all(|table_name| table_names.contains(table_name)));
    }

    #[test]
    #[serial]
    fn test_delete_tables_should_remove_all_tables() {
        setup_db().unwrap();
        super::delete_tables().unwrap();
        let table_names = get_table_names();
        assert!(table_names.is_empty());
        teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_delete_table_should_remove_table_by_name() {
        setup_db().unwrap();
        let table_name = super::SETTINGS.sqlite.tables.keys().next().unwrap();
        let mut table_names = get_table_names();
        assert!(table_names.contains(table_name));
        super::delete_table(table_name.as_str()).unwrap();
        table_names = get_table_names();
        assert!(!table_names.contains(table_name));
        teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_create_table_should_throw_error_if_table_not_exists_in_settings() {
        setup_db().unwrap();
        let table_name = "incorrect-name";
        let error_kind = super::create_table(table_name).unwrap_err();
        assert_eq!(error_kind.to_string(), "Table is not defined in Settings");
        teardown_db().unwrap();
    }

    #[test]
    #[serial]
    fn test_create_table_should_create_table_by_name() {
        super::delete_database().unwrap();
        let table_name = super::SETTINGS.sqlite.tables.keys().next().unwrap();
        let mut table_names = get_table_names();
        assert!(!table_names.contains(table_name));
        super::create_table(table_name).unwrap();
        table_names = get_table_names();
        assert!(table_names.contains(table_name));
    }

    #[test]
    #[serial]
    fn test_truncate_table_shoudnt_throw_error() {
        setup_db().unwrap();
        let table_name = super::SETTINGS.sqlite.tables.keys().next().unwrap();
        super::truncate_table(table_name).unwrap();
        teardown_db().unwrap();
    }
}
