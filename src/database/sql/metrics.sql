CREATE TABLE IF NOT EXISTS metrics (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `source` VARCHAR(96) NOT NULL,
    `is_signal` BOOLEAN NOT NULL,
    `value` INT NOT NULL,
    `market_id` INT NOT NULL,
    `created_at` TIMESTAMP NULL DEFAULT NULL
);