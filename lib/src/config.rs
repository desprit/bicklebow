use std::collections::HashMap;
use std::env;

#[derive(Debug, Clone)]
pub struct SqliteSettings {
    pub path: String,
    pub name: &'static str,
    pub tables: HashMap<String, String>,
}

#[derive(Debug, Clone)]
pub struct Settings {
    pub sqlite: SqliteSettings,
    pub project_name: &'static str,
    pub project_root: String,
}

impl Settings {
    fn new() -> Self {
        let path = env::var("CARGO_MANIFEST_DIR").unwrap();
        let env = env::var("BICKLEBOW_ENV").unwrap_or("testing".to_string());
        let root_path = std::path::Path::new(path.as_str())
            .parent()
            .unwrap()
            .to_str()
            .unwrap();
        Settings {
            project_name: "bicklebow",
            project_root: root_path.to_string(),
            sqlite: SqliteSettings {
                name: "bicklebow",
                path: {
                    match env.as_str() {
                        "testing" => String::from("/tmp/bicklebow.db"),
                        _ => format!("{}/bicklebow.db", root_path.clone()),
                    }
                },
                tables: {
                    let mut tables = HashMap::new();
                    let table_names = ["markets", "metrics"];
                    for table_name in table_names {
                        tables.insert(
                            table_name.to_string(),
                            format!(
                                "{}/lib/src/database/sql/{}.sql",
                                root_path.clone(),
                                table_name
                            ),
                        );
                    }
                    tables
                },
            },
        }
    }
}

lazy_static! {
    #[derive(Debug)]
    pub static ref SETTINGS: Settings = Settings::new();
}
