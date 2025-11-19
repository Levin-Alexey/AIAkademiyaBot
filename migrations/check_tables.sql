-- SQL скрипт для проверки созданных таблиц и типов
-- Выполните этот скрипт, чтобы убедиться, что все создано правильно

-- 1. Проверка enum типа
SELECT 
    typname as "Enum Type",
    typtype as "Type Code",
    CASE typtype 
        WHEN 'e' THEN 'ENUM'
        ELSE 'OTHER'
    END as "Type"
FROM pg_type 
WHERE typname = 'payment_status';

-- 2. Проверка таблиц
SELECT 
    table_name as "Table Name",
    CASE 
        WHEN table_name = 'courses' THEN 'Платные курсы'
        WHEN table_name = 'course_registrations' THEN 'Регистрации на курсы'
        WHEN table_name = 'payments' THEN 'Платежи'
        ELSE 'Другая таблица'
    END as "Description"
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('courses', 'course_registrations', 'payments')
ORDER BY table_name;

-- 3. Проверка структуры таблицы payments
SELECT 
    column_name as "Column",
    data_type as "Type",
    is_nullable as "Nullable",
    column_default as "Default"
FROM information_schema.columns
WHERE table_name = 'payments'
ORDER BY ordinal_position;

-- 4. Проверка индексов
SELECT 
    indexname as "Index Name",
    tablename as "Table",
    indexdef as "Definition"
FROM pg_indexes
WHERE tablename IN ('courses', 'course_registrations', 'payments')
ORDER BY tablename, indexname;

