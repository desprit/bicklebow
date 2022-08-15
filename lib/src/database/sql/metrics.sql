CREATE TABLE IF NOT EXISTS metrics (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `source` VARCHAR(96) NOT NULL,
    `is_signal` BOOLEAN NOT NULL,
    `price` REAL NOT NULL,
    `volume` REAL NOT NULL,
    `market_id` INT NOT NULL,
    `datetime` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP NOT NULL
);