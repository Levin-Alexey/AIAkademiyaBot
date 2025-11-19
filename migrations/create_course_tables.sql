-- SQL скрипт для создания таблиц платных курсов и платежей
-- Выполните этот скрипт в вашей PostgreSQL базе данных

-- 1. Создание ENUM типа для статусов платежа
-- Используем DO блок для безопасного создания (если уже существует - не ошибется)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payment_status AS ENUM ('pending', 'succeeded', 'canceled', 'failed');
    END IF;
END $$;

-- 2. Создание таблицы courses (платные курсы)
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR NOT NULL,
    start_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    description TEXT,
    course_link VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Создание таблицы course_registrations (связь пользователей и курсов)
CREATE TABLE IF NOT EXISTS course_registrations (
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    registration_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, course_id),
    CONSTRAINT fk_course_registrations_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_course_registrations_course 
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 4. Создание таблицы payments (платежи)
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    payment_id VARCHAR NOT NULL UNIQUE,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR NOT NULL DEFAULT 'RUB',
    status payment_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP WITHOUT TIME ZONE,
    payment_metadata TEXT,
    CONSTRAINT fk_payments_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_course 
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 5. Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_courses_is_active_start_date 
    ON courses(is_active, start_date) 
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_course_registrations_user_id 
    ON course_registrations(user_id);

CREATE INDEX IF NOT EXISTS idx_course_registrations_course_id 
    ON course_registrations(course_id);

CREATE INDEX IF NOT EXISTS idx_payments_user_id 
    ON payments(user_id);

CREATE INDEX IF NOT EXISTS idx_payments_course_id 
    ON payments(course_id);

CREATE INDEX IF NOT EXISTS idx_payments_payment_id 
    ON payments(payment_id);

CREATE INDEX IF NOT EXISTS idx_payments_status 
    ON payments(status);

-- 6. Комментарии к таблицам (опционально, для документации)
COMMENT ON TABLE courses IS 'Таблица платных курсов';
COMMENT ON TABLE course_registrations IS 'Связь пользователей и курсов (many-to-many)';
COMMENT ON TABLE payments IS 'Таблица платежей через ЮКассу';
COMMENT ON COLUMN courses.price IS 'Цена курса в рублях';
COMMENT ON COLUMN payments.payment_id IS 'Уникальный ID платежа от ЮКассы';
COMMENT ON COLUMN payments.payment_metadata IS 'Дополнительные данные платежа в формате JSON';
COMMENT ON COLUMN payments.status IS 'Статус платежа: pending, succeeded, canceled, failed';

