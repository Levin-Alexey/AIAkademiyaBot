# 💡 Примеры использования системы AI Coins

## 📚 Пример 1: Начисление монет при событии

### Базовый пример
```python
from coin_service import add_coins

# Когда пользователь что-то делает
async def some_user_action(telegram_id: int):
    # Начисляем монеты
    new_balance = await add_coins(
        telegram_id=telegram_id,
        amount=50,
        reason="завершение задачи",
        description="Пользователь завершил квиз"
    )
    
    # Используем новый баланс
    print(f"Новый баланс: {new_balance} монет")
```

### В контексте обработчика Telegram бота
```python
from aiogram import Router, F
from aiogram.types import CallbackQuery
from coin_service import add_coins, get_balance

router = Router()

@router.callback_query(F.data == "complete_quiz")
async def complete_quiz_handler(callback: CallbackQuery):
    # Начисляем монеты
    await add_coins(
        telegram_id=callback.from_user.id,
        amount=50,
        reason="завершение квиза",
        description="Пользователь прошел обучающий квиз"
    )
    
    # Получаем новый баланс
    balance = await get_balance(callback.from_user.id)
    
    # Отправляем ответ
    await callback.message.answer(
        f"🎉 Поздравляем!\n"
        f"Вы получили +50 монет\n"
        f"Ваш баланс: {balance} 🪙"
    )
```

---

## 💸 Пример 2: Списание монет (покупка)

```python
from coin_service import subtract_coins, get_balance

async def buy_item(telegram_id: int, item_name: str, price: int):
    # Проверяем баланс и списываем
    new_balance = await subtract_coins(
        telegram_id=telegram_id,
        amount=price,
        reason="покупка",
        description=f"Покупка: {item_name}"
    )
    
    # Проверяем результат
    if new_balance == -1:
        return {"error": "Недостаточно монет"}
    
    return {
        "success": True,
        "new_balance": new_balance,
        "spent": price
    }

# Использование в обработчике
@router.callback_query(F.data.startswith("buy_"))
async def buy_handler(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = get_item_by_id(item_id)  # ваша функция
    
    result = await buy_item(
        telegram_id=callback.from_user.id,
        item_name=item.name,
        price=item.price
    )
    
    if "error" in result:
        await callback.message.answer(f"❌ {result['error']}")
    else:
        await callback.message.answer(
            f"✅ Вы купили: {item.name}\n"
            f"Потрачено: {result['spent']} 🪙\n"
            f"Новый баланс: {result['new_balance']} 🪙"
        )
```

---

## 👤 Пример 3: Получение информации о пользователе

```python
from coin_service import get_user_with_coins
from sqlalchemy.orm import selectinload

async def show_user_profile(telegram_id: int):
    user = await get_user_with_coins(telegram_id)
    
    if not user:
        print("Пользователь не найден")
        return
    
    print(f"👤 Профиль пользователя")
    print(f"Имя: {user.user_name}")
    print(f"ID: {user.telegram_id}")
    print(f"Баланс: {user.ai_coins_balance} монет")
    print(f"Направление: {user.direction}")
    print(f"Дата регистрации: {user.start_time}")
    
    # Показываем операции
    print(f"\n📜 История операций:")
    for op in user.coin_operations:
        op_type = "➕" if op.operation_type.value == 'earned' else "➖"
        print(f"{op_type} {op.amount} - {op.reason} ({op.created_at})")
```

---

## 📊 Пример 4: Проверка баланса и условное действие

```python
from coin_service import get_balance, subtract_coins

async def try_action_if_enough_coins(telegram_id: int, required_coins: int):
    balance = await get_balance(telegram_id)
    
    if balance >= required_coins:
        # Достаточно монет
        new_balance = await subtract_coins(
            telegram_id=telegram_id,
            amount=required_coins,
            reason="использование функции",
            description="Использование премиум функции"
        )
        
        return {
            "success": True,
            "message": "Функция активирована",
            "new_balance": new_balance
        }
    else:
        # Недостаточно монет
        need_more = required_coins - balance
        return {
            "success": False,
            "message": f"Недостаточно монет. Нужно еще {need_more}",
            "current_balance": balance,
            "required": required_coins
        }
```

---

## 🎯 Пример 5: Ежедневный бонус

```python
from datetime import datetime, timedelta
from coin_service import add_coins, get_balance
from database import async_session
from models import User
from sqlalchemy import select, and_

async def give_daily_bonus(telegram_id: int):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Проверяем дату последнего бонуса
        today = datetime.now().date()
        last_bonus_date = user.last_bonus_date.date() if user.last_bonus_date else None
        
        if last_bonus_date != today:
            # Начисляем бонус
            await add_coins(
                telegram_id=telegram_id,
                amount=10,
                reason="ежедневный бонус",
                description=f"Ежедневный бонус за {today}"
            )
            
            # Обновляем дату
            user.last_bonus_date = datetime.now()
            await session.commit()
            
            return True
        
        return False
```

---

## 🏆 Пример 6: Лидерборд

```python
from database import async_session
from models import User
from sqlalchemy import select, desc

async def get_leaderboard(limit: int = 10):
    async with async_session() as session:
        # Получаем топ пользователей
        result = await session.execute(
            select(User)
            .order_by(desc(User.ai_coins_balance))
            .limit(limit)
        )
        users = result.scalars().all()
        
        # Формируем текст
        text = "🏆 ТОП ПОЛЬЗОВАТЕЛЕЙ ПО МОНЕТАМ\n\n"
        for i, user in enumerate(users, 1):
            text += f"{i}. {user.user_name or 'Анонимно'} - {user.ai_coins_balance} 🪙\n"
        
        return text
```

---

## 📱 Пример 7: Полная интеграция в Telegram обработчик

```python
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from coin_service import add_coins, subtract_coins, get_balance

router = Router()

@router.callback_query(F.data == "daily_check_in")
async def daily_checkin_handler(callback: CallbackQuery):
    """
    Ежедневная явка со случайным бонусом
    """
    import random
    
    telegram_id = callback.from_user.id
    
    # Генерируем случайный бонус от 10 до 50 монет
    bonus = random.choice([10, 20, 30, 40, 50])
    
    # Начисляем бонус
    new_balance = await add_coins(
        telegram_id=telegram_id,
        amount=bonus,
        reason="ежедневная явка",
        description=f"Бонус за посещение в {datetime.now().strftime('%d.%m.%Y')}"
    )
    
    # Формируем сообщение
    text = f"""
✨ ЕЖЕДНЕВНАЯ ЯВКА ✨

Вы получили: +{bonus} 🪙
Ваш баланс: {new_balance} 🪙

Приходите завтра за новым бонусом! 🚀
    """
    
    # Кнопки для дальнейших действий
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Купить премиум",
                    callback_data="buy_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Лидерборд",
                    callback_data="show_leaderboard"
                )
            ]
        ]
    )
    
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()
```

---

## 🔄 Пример 8: Возврат монет (refund)

```python
from models import AICoinOperation, CoinOperationType
from database import async_session
from sqlalchemy import select, update

async def refund_coins(telegram_id: int, amount: int, reason: str):
    """
    Возвращает монеты пользователю и создает запись операции
    """
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Добавляем монеты
        user.ai_coins_balance += amount
        
        # Создаем запись операции
        operation = AICoinOperation(
            user_id=user.id,
            amount=amount,
            operation_type=CoinOperationType.REFUND,
            reason=reason,
            description=f"Возврат: {reason}"
        )
        session.add(operation)
        
        await session.commit()
        return user.ai_coins_balance

# Использование
@router.callback_query(F.data == "return_item")
async def return_item_handler(callback: CallbackQuery):
    result = await refund_coins(
        telegram_id=callback.from_user.id,
        amount=50,
        reason="возврат товара"
    )
    
    if result:
        await callback.message.answer(
            f"✅ Возврат принят\n"
            f"Возвращено: +50 🪙\n"
            f"Новый баланс: {result} 🪙"
        )
```

---

## 🎮 Пример 9: Мини-игра с наградой

```python
import random

async def play_mini_game(telegram_id: int):
    """
    Простая мини-игра: угадайте число
    """
    secret_number = random.randint(1, 10)
    
    # Пользователь должен угадать (упрощенная логика)
    # В реальном приложении здесь будет взаимодействие с пользователем
    
    user_guess = random.randint(1, 10)  # для примера
    
    if user_guess == secret_number:
        # Победа! Начисляем крупный приз
        reward = 100
        message = f"🎉 Вы выиграли! +{reward} 🪙"
    else:
        # Проигрыш, но даем утешительный приз
        reward = 5
        message = f"😢 Не угадали, но вот утешительный приз: +{reward} 🪙"
    
    # Начисляем награду
    new_balance = await add_coins(
        telegram_id=telegram_id,
        amount=reward,
        reason="мини-игра",
        description=f"Награда за мини-игру. Ответ: {secret_number}"
    )
    
    return {
        "message": message,
        "new_balance": new_balance,
        "reward": reward
    }
```

---

## 🔐 Пример 10: Безопасная транзакция

```python
from database import async_session
from sqlalchemy import update

async def safe_coin_transaction(telegram_id: int, amount: int):
    """
    Безопасная транзакция с откатом при ошибке
    """
    async with async_session() as session:
        try:
            # Находим пользователя с блокировкой для избежания race condition
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise ValueError("Пользователь не найден")
            
            if user.ai_coins_balance < amount:
                raise ValueError("Недостаточно монет")
            
            # Выполняем операцию
            user.ai_coins_balance -= amount
            
            # Создаем запись
            operation = AICoinOperation(
                user_id=user.id,
                amount=-amount,
                operation_type=CoinOperationType.SPENT,
                reason="безопасная транзакция",
                description="Транзакция выполнена успешно"
            )
            session.add(operation)
            
            # Сохраняем все
            await session.commit()
            
            return {
                "success": True,
                "new_balance": user.ai_coins_balance
            }
            
        except Exception as e:
            # Откат при ошибке (автоматический rollback)
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
```

---

## 📋 Заметки к примерам

- Все примеры используют `async/await`
- Используется `async_session()` для работы с БД
- Все операции записываются в историю
- Баланс всегда проверяется перед списанием
- Используются типы enum для безопасности


