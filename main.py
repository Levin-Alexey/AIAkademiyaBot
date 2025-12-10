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
from datetime import datetime

from database import async_session
from models import User, Webinar
from handlers import personal_direction, business_direction, registration, admin, additional_actions, enroll_course, speaker_info
from keyboards import _get_additional_buttons
from coin_service import add_coins, get_balance

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
dp.include_router(speaker_info.router)

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
                    text="🔐 Закрытая группа по ИИ",
                    url="https://t.me/+VxGcD_UbVJE5NTNi"
                )
            ])
            
            # Добавляем дополнительные кнопки
            inline_keyboard.extend(_get_additional_buttons())

            inline_keyboard.append([
                InlineKeyboardButton(
                    text="ℹ️ Информация о спикере",
                    callback_data="speaker_info"
                )
            ])
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

🔐 Нажми на кнопку "Закрытая группа по ИИ" - там тебя ждут эксклюзивные знания!

💡 Будь с нами - всё самое важное будет приходить сюда!

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

    # Начисляем +100 монет при первом входе (вход считается новым, если баланс == 0)
    current_balance = await get_balance(message.from_user.id)
    if current_balance == 0:
        await add_coins(
            telegram_id=message.from_user.id,
            amount=100,
            reason="регистрация",
            description="Бонус за регистрацию при первом входе /start"
        )

    # Показываем стандартное приветствие
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧑‍💻 Для личной эффективности (+50 🪙)",
                    callback_data="direction_personal",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💼 Для бизнеса и масштабирования (+50 🪙)",
                    callback_data="direction_business",
                )
            ],
        ]
    )

    caption = (
        "👋 Привет!\n"
        "Ты в игре. Твой бонусный счет открыт: +100 AI-Coins 🪙 начислены!\n\n"
        "Чтобы вебинар прошел для тебя максимально полезно, я хочу адаптировать примеры эфира под твои задачи. За выбор направления я начислю еще 50 монет.\n\n"
        "👇 Посмотри, что нас ждет на эфире (1 час):\n"
        "🔹 Блок 1: ИИ как привычка (делегируем рутину).\n"
        "🔹 Блок 2: Бесплатный арсенал (инструменты мощнее ChatGPT).\n"
        "🔹 Блок 3: Тотальная автоматизация (схемы экономии времени).\n\n"
        "🎁 <b>Твой подарок (База нейросетей) придет сразу после регистрации</b>\n\n"
        "Для каких целей ты хочешь освоить ИИ?"
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
