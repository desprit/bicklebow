use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct SqliteSettings {
    pub path: &'static str,
    pub name: &'static str,
    pub tables: HashMap<String, String>,
}

#[derive(Debug, Clone)]
pub struct Settings {
    pub sqlite: SqliteSettings,
    pub project_name: &'static str,
}

impl Settings {
    fn new() -> Self {
        Settings {
            project_name: "bicklebow",
            sqlite: SqliteSettings {
                name: "bicklebow",
                path: "./src/database/bicklebow.db",
                tables: {
                    let mut tables = HashMap::new();
                    let table_names = ["markets", "metrics", "news"];
                    for table_name in table_names {
                        tables.insert(
                            table_name.to_string(),
                            format!("./src/database/sql/{}.sql", table_name),
                        );
                    }
                    tables
                },
            },
        }
    }
}

lazy_static! {
    pub static ref SETTINGS: Settings = Settings::new();
}
