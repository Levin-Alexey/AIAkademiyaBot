-- SQL скрипт для проверки и исправления статусов платежей
-- Выполните этот скрипт, чтобы проверить и исправить данные

-- 1. Проверка текущих статусов в таблице payments
SELECT 
    id,
    payment_id,
    status,
    CASE 
        WHEN status::text = 'pending' THEN '✅ OK'
        WHEN status::text = 'succeeded' THEN '✅ OK'
        WHEN status::text = 'canceled' THEN '✅ OK'
        WHEN status::text = 'failed' THEN '✅ OK'
        ELSE '❌ НЕПРАВИЛЬНО'
    END as "Status Check"
FROM payments
ORDER BY id;

-- 2. Проверка enum типа (должен быть в нижнем регистре)
SELECT 
    enumlabel as "Enum Value",
    enumsortorder as "Order"
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'payment_status')
ORDER BY enumsortorder;

-- 3. Если нужно обновить статусы (если они были в неправильном регистре)
-- ВНИМАНИЕ: Выполняйте только если есть проблемы!
-- Обычно это не нужно, т.к. enum автоматически конвертирует значения

-- Пример обновления (если статусы были сохранены неправильно):
-- UPDATE payments 
-- SET status = 'succeeded'::payment_status 
-- WHERE status::text = 'SUCCEEDED' OR status::text = 'Succeeded';

-- 4. Проверка, что все статусы корректны
SELECT 
    status::text as "Current Status",
    COUNT(*) as "Count"
FROM payments
GROUP BY status::text
ORDER BY status::text;

-- 5. Если нужно удалить все тестовые платежи (опционально)
-- DELETE FROM payments WHERE status = 'pending'::payment_status;

