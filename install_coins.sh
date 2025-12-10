#!/bin/bash
# Скрипт для установки и запуска системы AI Coins

echo "🪙 Установка системы AI Coins..."
echo ""

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    exit 1
fi
echo "✅ Python3 найден"

# Проверяем зависимости
echo ""
echo "📦 Проверка зависимостей..."
python3 -m pip install -q sqlalchemy asyncpg psycopg2-binary aiogram python-dotenv 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены"
else
    echo "⚠️ Некоторые зависимости не удалось установить. Установите вручную:"
    echo "   pip install -r requirements.txt"
fi

# Проверяем .env файл
echo ""
echo "⚙️ Проверка конфигурации..."
if [ ! -f .env ]; then
    echo "⚠️ Файл .env не найден. Создайте его на основе env_example.txt"
    exit 1
fi
echo "✅ .env файл найден"

# Проверяем подключение к БД
echo ""
echo "🗄️ Проверка подключения к БД..."
python3 << EOF
import asyncio
from database import async_session
from models import create_tables

async def test_db():
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        print("✅ Подключение к БД успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

asyncio.run(test_db())
EOF

# Применяем миграции
echo ""
echo "📊 Применение миграций..."
python3 << EOF
import asyncio
from models import create_tables

async def migrate():
    try:
        await create_tables()
        print("✅ Миграции применены успешно")
    except Exception as e:
        print(f"⚠️ Ошибка при миграции: {e}")
        print("   Попробуйте вручную:")
        print("   psql -U user -d database -f migrations/create_ai_coins_table.sql")

asyncio.run(migrate())
EOF

echo ""
echo "🚀 Установка завершена!"
echo ""
echo "Теперь запустите бота командой:"
echo "   python main.py"
echo ""
echo "После запуска проверьте:"
echo "   1. Отправьте /start"
echo "   2. Выберите направление"
echo "   3. Подтвердите регистрацию"
echo "   4. Команда /balance должна показать 250 монет"

