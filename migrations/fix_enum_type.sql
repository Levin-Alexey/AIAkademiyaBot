-- SQL скрипт для создания enum типа payment_status
-- Выполните этот скрипт, если получили ошибку "type paymentstatus does not exist"

-- Создание enum типа (если еще не создан)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payment_status AS ENUM ('pending', 'succeeded', 'canceled', 'failed');
    END IF;
END $$;

-- Проверка, что тип создан
SELECT typname, typtype 
FROM pg_type 
WHERE typname = 'payment_status';

