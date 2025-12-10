"""
Сервис для управления AI монетами пользователей
"""

from sqlalchemy.orm import selectinload
from sqlalchemy import select
from database import async_session
from models import User, AICoinOperation, CoinOperationType


async def add_coins(telegram_id: int, amount: int, reason: str, description: str = None) -> int:
    """
    Начисляет монеты пользователю и создает запись об операции.

    Args:
        telegram_id: ID пользователя в Telegram
        amount: Количество монет для начисления (должно быть положительным)
        reason: Причина начисления (например: "регистрация", "выбор направления" и т.д.)
        description: Полное описание операции (опционально)

    Returns:
        Новый баланс пользователя
    """
    amount = abs(amount)  # Убеждаемся, что это положительное число

    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return 0

        # Обновляем баланс
        user.ai_coins_balance += amount

        # Создаем запись об операции
        coin_operation = AICoinOperation(
            user_id=user.id,
            amount=amount,
            operation_type=CoinOperationType.EARNED,
            reason=reason,
            description=description
        )
        session.add(coin_operation)

        # Сохраняем изменения
        await session.commit()
        await session.refresh(user)

        return user.ai_coins_balance


async def subtract_coins(telegram_id: int, amount: int, reason: str, description: str = None) -> int:
    """
    Списывает монеты у пользователя и создает запись об операции.

    Args:
        telegram_id: ID пользователя в Telegram
        amount: Количество монет для списания (должно быть положительным)
        reason: Причина списания
        description: Полное описание операции (опционально)

    Returns:
        Новый баланс пользователя (или -1 если недостаточно монет)
    """
    amount = abs(amount)  # Убеждаемся, что это положительное число

    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return -1

        # Проверяем достаточность монет
        if user.ai_coins_balance < amount:
            return -1

        # Обновляем баланс
        user.ai_coins_balance -= amount

        # Создаем запись об операции
        coin_operation = AICoinOperation(
            user_id=user.id,
            amount=-amount,
            operation_type=CoinOperationType.SPENT,
            reason=reason,
            description=description
        )
        session.add(coin_operation)

        # Сохраняем изменения
        await session.commit()
        await session.refresh(user)

        return user.ai_coins_balance


async def get_balance(telegram_id: int) -> int:
    """
    Получает текущий баланс монет пользователя.

    Args:
        telegram_id: ID пользователя в Telegram

    Returns:
        Количество монет на счете
    """
    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return 0

        return user.ai_coins_balance


async def get_user_with_coins(telegram_id: int):
    """
    Получает пользователя со всеми его данными.

    Args:
        telegram_id: ID пользователя в Telegram

    Returns:
        Объект User или None
    """
    async with async_session() as session:
        user_result = await session.execute(
            select(User)
            .options(selectinload(User.coin_operations))
            .where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if user:
            await session.refresh(user)

        return user

