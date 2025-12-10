# Инструкция по запуску системы AI Coins

## Шаг 1: Обновить базу данных

Выполнить SQL миграцию для создания таблицы `ai_coin_operations`:

```bash
# В терминале PostgreSQL
psql -U your_user -d your_database -f migrations/create_ai_coins_table.sql
```

Или через Python:

```python
import asyncio
from models import create_tables

asyncio.run(create_tables())
```

## Шаг 2: Убедиться что обновлены все файлы

Проверьте что все файлы обновлены:
- ✅ `coin_service.py` - создан новый файл с функциями для работы с монетами
- ✅ `models.py` - добавлена модель `AICoinOperation` и поле `ai_coins_balance` в User
- ✅ `main.py` - добавлено начисление +100 при /start
- ✅ `handlers/personal_direction.py` - добавлено начисление +50 при выборе personal
- ✅ `handlers/business_direction.py` - добавлено начисление +50 при выборе business
- ✅ `handlers/registration.py` - добавлено начисление +100 при регистрации на вебинар

## Шаг 3: Перезапустить бот

```bash
python main.py
```

## Проверка работы

### Тестирование потока:

1. Отправьте `/start` - должно начислиться +100 монет
2. Выберите направление (Personal или Business) - должно начислиться +50 монет
3. Подтвердите регистрацию на вебинар - должно начислиться +100 монет
4. Проверьте баланс в сообщении - должно быть 250 монет

### SQL запрос для проверки операций:

```sql
-- Все операции пользователя (по telegram_id)
SELECT 
    u.telegram_id,
    u.user_name,
    u.ai_coins_balance,
    o.amount,
    o.operation_type,
    o.reason,
    o.created_at
FROM users u
LEFT JOIN ai_coin_operations o ON u.id = o.user_id
WHERE u.telegram_id = YOUR_TELEGRAM_ID
ORDER BY o.created_at DESC;

-- Баланс всех пользователей
SELECT 
    telegram_id,
    user_name,
    ai_coins_balance,
    COUNT(CASE WHEN direction IS NOT NULL THEN 1 END) as has_direction
FROM users
ORDER BY ai_coins_balance DESC;
```

## Важные замечания

⚠️ **Убедитесь что:**
- PostgreSQL база данных запущена
- Переменные окружения в `.env` правильно установлены
- Все импорты в файлах на месте
- Таблица `users` существует в базе

## Отладка проблем

Если возникают проблемы с начислением монет:

1. Проверьте логи бота
2. Убедитесь что пользователь существует в таблице `users`
3. Проверьте что таблица `ai_coin_operations` создана
4. Убедитесь что `coin_service.py` импортируется правильно


