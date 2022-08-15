CREATE TABLE IF NOT EXISTS markets (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `ticker` VARCHAR(96) NOT NULL UNIQUE,
    `label` VARCHAR(96) NOT NULL,
    `figi` VARCHAR(96) UNIQUE,
    `risk` INT NOT NULL,
    `priority` INT NOT NULL,
    `labels` TEXT DEFAULT NULL,
    `category` VARCHAR(96),
    `created_at` TIMESTAMP NOT NULL
);