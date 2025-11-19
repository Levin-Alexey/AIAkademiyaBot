# Миграции базы данных

## Описание

Эти SQL скрипты создают таблицы для системы платных курсов и платежей.

## Порядок выполнения

### 1. Создание таблиц

Выполните скрипт `create_course_tables.sql`:

```bash
# Через psql
psql -U your_username -d your_database -f create_course_tables.sql

# Или через pgAdmin / другой SQL клиент
# Просто скопируйте и выполните содержимое файла
```

### 2. Добавление тестового курса (опционально)

Если хотите сразу протестировать систему, выполните:

```bash
psql -U your_username -d your_database -f insert_test_course.sql
```

Или измените дату и цену в файле перед выполнением.

## Что создается

### Таблицы:

1. **courses** - Платные курсы
   - `id` - ID курса
   - `course_name` - Название курса
   - `start_date` - Дата и время старта
   - `price` - Цена в рублях
   - `description` - Описание курса
   - `course_link` - Ссылка на курс (опционально)
   - `is_active` - Активен ли курс
   - `created_at` - Дата создания

2. **course_registrations** - Регистрации на курсы (many-to-many)
   - `user_id` - ID пользователя
   - `course_id` - ID курса
   - `registration_date` - Дата регистрации

3. **payments** - Платежи через ЮКассу
   - `id` - ID платежа
   - `user_id` - ID пользователя
   - `course_id` - ID курса
   - `payment_id` - Уникальный ID от ЮКассы
   - `amount` - Сумма в рублях
   - `currency` - Валюта (по умолчанию RUB)
   - `status` - Статус платежа (pending/succeeded/canceled/failed)
   - `created_at` - Дата создания платежа
   - `paid_at` - Дата оплаты (если оплачен)
   - `metadata` - Дополнительные данные в JSON

### Типы:

- **payment_status** - ENUM для статусов платежа

### Индексы:

Создаются индексы для оптимизации запросов по:
- `courses.is_active` и `start_date`
- `course_registrations.user_id` и `course_id`
- `payments.user_id`, `course_id`, `payment_id`, `status`

## Проверка

После выполнения миграций проверьте, что таблицы созданы:

```sql
-- Проверка таблиц
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('courses', 'course_registrations', 'payments');

-- Проверка типа
SELECT typname 
FROM pg_type 
WHERE typname = 'payment_status';

-- Проверка курсов
SELECT * FROM courses;
```

## Откат (если нужно удалить таблицы)

```sql
-- ВНИМАНИЕ: Это удалит все данные!
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS course_registrations CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
```

