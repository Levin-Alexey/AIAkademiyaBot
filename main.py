"""
AI Bot Education - Telegram бот на aiogram
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from datetime import datetime

from database import async_session
from models import User, Webinar
from handlers import personal_direction, business_direction, registration, admin, additional_actions, enroll_course
from keyboards import _get_additional_buttons

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

# Подключение роутеров
dp.include_router(admin.router)
dp.include_router(personal_direction.router)
dp.include_router(business_direction.router)
dp.include_router(registration.router)
dp.include_router(additional_actions.router)
dp.include_router(enroll_course.router)

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """
    Приветственное сообщение при старте бота.
    Проверяет, записан ли пользователь на вебинар.
    """
    async with async_session() as session:
        # 1. Проверяем, есть ли у пользователя регистрация на будущий вебинар
        stmt = select(Webinar).join(User.webinars).where(
            User.telegram_id == message.from_user.id,
            Webinar.webinar_date > datetime.now()
        ).order_by(Webinar.webinar_date.asc()).limit(1)
        
        result = await session.execute(stmt)
        upcoming_registration = result.scalar_one_or_none()

        # 2. Если регистрация найдена, показываем специальное сообщение
        if upcoming_registration:
            inline_keyboard = []
            if upcoming_registration.webinar_link:
                inline_keyboard.append([
                    InlineKeyboardButton(
                        text="🎥 Ссылка на вебинар",
                        url=upcoming_registration.webinar_link,
                    )
                ])
            inline_keyboard.append([
                InlineKeyboardButton(
                    text="🎁 Бонусные материалы",
                    callback_data="bonus_materials"
                )
            ])
            
            # Добавляем дополнительные кнопки
            inline_keyboard.extend(_get_additional_buttons())

            keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
            
            # Отправляем изображение
            image_url = (
                "https://image2url.com/images/1763063078779-"
                "f4fbaecb-7fe2-4524-99d5-e65417d77473.jpeg"
            )
            await message.answer_photo(image_url)

            # Форматируем дату и время из базы данных
            webinar_date = upcoming_registration.webinar_date.strftime(
                '%d.%m.%Y'
            )
            webinar_time = upcoming_registration.webinar_date.strftime('%H:%M')
            
            text = f"""🎉 <b>Приветсвую тебя, {message.from_user.first_name}!</b>
Отлично, что вернулся, скоро мы начинаем большое путешествие в мир ИИ! 

<b>Ты зарегистрирован на вебинар: 📅 {webinar_date} в {webinar_time} МСК</b>

✅ <b>Всё готово к старту:</b>

🎥 Ссылка на вебинар, <b>под этим собщением</b>

📲 Напоминание придёт сюда, в чат, за 1 час до начала

🎁 Нажми на кнопку "Бонусные материалы" и получи подарок!

💡 Будь с нами - все полезные материалы будут приходить сюда!

⚡ До встречи! Готовься к мощным знаниям! 🚀"""

            await message.answer(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return

    # 3. Если регистрация не найдена, запускаем стандартный флоу
    # Сначала убедимся, что пользователь существует в базе
    async with async_session() as session:
        insert_stmt = insert(User).values(
            telegram_id=message.from_user.id,
            user_name=message.from_user.username
        ).on_conflict_do_nothing(index_elements=['telegram_id'])
        await session.execute(insert_stmt)
        await session.commit()

    # Показываем стандартное приветствие
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💼 Для работы и личной эффективности",
                    callback_data="direction_personal",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚀 Для бизнеса и масштабирования",
                    callback_data="direction_business",
                )
            ],
        ]
    )

    caption = (
        "🎉 Отлично! Ты почти на вебинаре!\n"
        "Через пару минут ты зарегистрируешься и получишь доступ к знаниям, "
        "которые изменят твой подход к работе.\n\n"
        "🔥 <b>Программа вебинара (60 минут):</b>\n\n"
        "<b>Блок 1: ИИ каждый день (20 мин)</b>\n"
        "✅ Как использовать ИИ для писем, планов, идей, отчетов\n"
        "✅ Превращаем ИИ из эксперимента в привычку\n"
        "✅ Конкретные сценарии применения\n\n"
        "<b>Блок 2: Бесплатные инструменты (20 мин)</b>\n"
        "✅ ТОП нейросетей мощнее ChatGPT Plus и Midjourney\n"
        "✅ Где найти и как применять\n"
        "✅ Сравнение с платными аналогами\n\n"
        "<b>Блок 3: Автоматизация (20 мин)</b>\n"
        "✅ Как 3 часа рутины превращаются в 15 минут\n"
        "✅ Готовые схемы автоматизации\n"
        "✅ Промпты для копирования\n\n"
        "💡 <b>Бонус:</b> Секреты, которыми пользуются профи\n"
        "🎁 <b>Подарок всем:</b> база из ТОП бесплатных ИИ + промпты + сценарии\n\n"
        "⚡ <b>ИИ умножает твои возможности!</b>\n\n"
        "<b>Выбери своё направление:</b>"
    )

    await message.answer_photo(
        photo=(
            "https://image2url.com/images/"
            "1762884119936-b5ace70c-3771-4df5-8930-b265953e1e77.jpeg"
        ),
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
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
