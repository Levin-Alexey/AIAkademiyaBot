-- Создание таблицы для отслеживания операций с AI монетами
CREATE TABLE IF NOT EXISTS ai_coin_operations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    reason VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_operation_type (operation_type)
);

-- Добавляем колонку ai_coins_balance в таблицу users, если её еще нет
ALTER TABLE users ADD COLUMN IF NOT EXISTS ai_coins_balance INTEGER DEFAULT 0 NOT NULL;

-- Создаем индекс для быстрого получения баланса
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

