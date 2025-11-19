-- SQL скрипт для проверки и исправления данных
-- Выполните этот скрипт для проверки текущего состояния

-- 1. Проверка enum типа (должен существовать)
SELECT 
    typname as "Enum Type",
    CASE 
        WHEN typname = 'payment_status' THEN '✅ Создан'
        ELSE '❌ Не найден'
    END as "Status"
FROM pg_type 
WHERE typname = 'payment_status';

-- 2. Проверка значений enum (должны быть в нижнем регистре)
SELECT 
    enumlabel as "Enum Value",
    enumsortorder as "Order"
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'payment_status')
ORDER BY enumsortorder;

-- 3. Проверка таблицы payments
SELECT 
    id,
    payment_id,
    status::text as "Status",
    amount,
    created_at
FROM payments
ORDER BY id;

-- 4. Проверка корректности статусов
SELECT 
    status::text as "Status",
    COUNT(*) as "Count"
FROM payments
GROUP BY status::text
ORDER BY status::text;

-- 5. Если нужно исправить статусы (выполняйте только если есть проблемы!)
-- Раскомментируйте нужные строки:

-- UPDATE payments 
-- SET status = 'succeeded'::payment_status 
-- WHERE status::text NOT IN ('pending', 'succeeded', 'canceled', 'failed')
--   AND payment_id IN (SELECT payment_id FROM payments WHERE ...);

-- 6. Проверка таблицы courses
SELECT 
    id,
    course_name,
    start_date,
    price,
    is_active
FROM courses
ORDER BY id;

-- 7. Проверка регистраций на курсы
SELECT 
    cr.user_id,
    cr.course_id,
    cr.registration_date,
    u.telegram_id,
    c.course_name
FROM course_registrations cr
JOIN users u ON cr.user_id = u.id
JOIN courses c ON cr.course_id = c.id
ORDER BY cr.registration_date DESC;

