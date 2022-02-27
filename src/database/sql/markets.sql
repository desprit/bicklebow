CREATE TABLE IF NOT EXISTS markets (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` VARCHAR(96) NOT NULL UNIQUE,
    `label` VARCHAR(96) NOT NULL,
    `risk` INT NOT NULL,
    `priority` INT NOT NULL,
    `labels` TEXT DEFAULT NULL,
    `category` VARCHAR(96) NOT NULL,
    `amount` INT NOT NULL,
    `created_at` TIMESTAMP NULL DEFAULT NULL
);