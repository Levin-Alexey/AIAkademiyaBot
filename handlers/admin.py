from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta
import logging

from database import async_session
from models import Webinar

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("create_webinar"))
async def create_webinar_handler(message: Message):
    """
    Создает новый вебинар.
    Пример использования: /create_webinar 2025-12-31 19:00
    Если дата не указана, вебинар создается через 24 часа.
    """
    try:
        args = message.text.split()
        if len(args) > 1:
            # Пользователь указал дату и время
            date_str = " ".join(args[1:])
            webinar_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        else:
            # Дата и время не указаны, создаем через 24 часа
            webinar_date = datetime.now() + timedelta(days=1)

        async with async_session() as session:
            new_webinar = Webinar(webinar_date=webinar_date)
            session.add(new_webinar)
            await session.commit()
        
        await message.answer(f"✅ Вебинар успешно создан на {webinar_date.strftime('%d.%m.%Y в %H:%M')}.")
        logger.info(f"Создан новый вебинар на {webinar_date}")

    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте: YYYY-MM-DD HH:MM\nНапример: /create_webinar 2025-12-31 19:00")
    except Exception as e:
        logger.error(f"Ошибка при создании вебинара: {e}")
        await message.answer("❌ Произошла ошибка при создании вебинара.")
