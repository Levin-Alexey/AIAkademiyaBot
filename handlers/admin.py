from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta
import logging

from database import async_session
from models import Webinar, User, AICoinOperation
from coin_service import get_balance
from sqlalchemy import select

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


@router.message(Command("balance"))
async def check_balance_handler(message: Message):
    """
    Проверяет баланс AI монет пользователя.
    Пример использования: /balance или /balance 123456789
    """
    try:
        args = message.text.split()

        # Если указан ID пользователя, проверяем его, иначе проверяем текущего пользователя
        if len(args) > 1:
            telegram_id = int(args[1])
        else:
            telegram_id = message.from_user.id

        balance = await get_balance(telegram_id)

        async with async_session() as session:
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()

        if not user:
            await message.answer(f"❌ Пользователь с ID {telegram_id} не найден в базе.")
            return

        direction = user.direction if user.direction else "не выбрано"
        text = f"""💰 Баланс AI Coins 🪙

👤 Пользователь: {user.user_name or 'Анонимно'}
🆔 Telegram ID: {telegram_id}
💵 Баланс: {balance} монет
📍 Направление: {direction}
📅 Дата регистрации: {user.start_time.strftime('%d.%m.%Y %H:%M') if user.start_time else 'неизвестна'}
"""
        await message.answer(text)

    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: /balance или /balance <telegram_id>")
    except Exception as e:
        logger.error(f"Ошибка при проверке баланса: {e}")
        await message.answer("❌ Произошла ошибка при проверке баланса.")


@router.message(Command("user_stats"))
async def user_stats_handler(message: Message):
    """
    Показывает статистику операций с монетами пользователя.
    Пример использования: /user_stats или /user_stats 123456789
    """
    try:
        args = message.text.split()

        # Если указан ID пользователя, проверяем его, иначе проверяем текущего пользователя
        if len(args) > 1:
            telegram_id = int(args[1])
        else:
            telegram_id = message.from_user.id

        async with async_session() as session:
            # Находим пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                await message.answer(f"❌ Пользователь с ID {telegram_id} не найден.")
                return

            # Получаем все операции пользователя
            operations_result = await session.execute(
                select(AICoinOperation)
                .where(AICoinOperation.user_id == user.id)
                .order_by(AICoinOperation.created_at.desc())
            )
            operations = operations_result.scalars().all()

        # Подсчитываем статистику
        total_earned = sum(op.amount for op in operations if op.operation_type.value == 'earned')
        total_spent = sum(abs(op.amount) for op in operations if op.operation_type.value == 'spent')

        # Формируем текст сообщения
        text = f"""📊 Статистика операций с монетами 🪙

👤 Пользователь: {user.user_name or 'Анонимно'}
🆔 Telegram ID: {telegram_id}
💵 Текущий баланс: {user.ai_coins_balance} монет

📈 Статистика:
✅ Всего заработано: {total_earned} монет
❌ Всего потрачено: {total_spent} монет
📝 Всего операций: {len(operations)}

📜 Последние операции:
"""

        if operations:
            for op in operations[:10]:  # Показываем последние 10 операций
                op_type = "➕" if op.operation_type.value == 'earned' else "➖"
                text += f"\n{op_type} {op.amount:+d} монет - {op.reason}"
                if op.created_at:
                    text += f" ({op.created_at.strftime('%d.%m.%Y %H:%M')})"
        else:
            text += "\nНет операций"

        await message.answer(text)

    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: /user_stats или /user_stats <telegram_id>")
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer("❌ Произошла ошибка при получении статистики.")
