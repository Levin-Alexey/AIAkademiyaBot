"""
AI Bot Education - Telegram бот на aiogram
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден! Создайте файл .env с токеном бота.")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение при старте бота"""
    await message.answer(
        "🤖 Привет! Я бот и помогу тебе!\n\n"
        "Добро пожаловать в образовательный AI-бот!\n"
        "Этот проект создан для изучения разработки ботов.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/info - Информация о боте"
    )


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь по использованию бота"""
    await message.answer(
        "📚 Помощь:\n\n"
        "Этот бот находится в разработке.\n"
        "Скоро здесь появятся новые функции!\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/help - Эта справка\n"
        "/info - Информация о боте"
    )


# Обработчик команды /info
@dp.message(Command("info"))
async def cmd_info(message: Message):
    """Информация о боте"""
    await message.answer(
        "ℹ️ Информация о боте:\n\n"
        "🔹 Название: AI Bot Education\n"
        "🔹 Версия: 0.1.0\n"
        "🔹 Фреймворк: aiogram 3.x\n"
        "🔹 Язык: Python\n\n"
        "Создан для образовательных целей 📖"
    )


# Обработчик всех текстовых сообщений
@dp.message()
async def echo_message(message: Message):
    """Эхо-обработчик для всех остальных сообщений"""
    await message.answer(
        f"Ты написал: {message.text}\n\n"
        "Используй /help чтобы узнать доступные команды."
    )


async def main():
    """Главная функция запуска бота"""
    logger.info("🤖 Бот запускается...")
    logger.info("Я бот и помогу тебе!")
    
    try:
        # Удаление вебхуков (на случай если были установлены)
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запуск бота
        logger.info("✅ Бот успешно запущен и готов к работе!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
