
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
import os
from dotenv import load_dotenv
from sqlalchemy import update
from database import async_session
from models import User
from coin_service import add_coins

router = Router()

# Загрузка переменных окружения
load_dotenv()


@router.callback_query(F.data == "direction_business")
async def direction_business_handler(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        stmt = update(User).where(
            User.telegram_id == callback.from_user.id
        ).values(direction='business')
        await session.execute(stmt)
        await session.commit()

    # Начисляем +50 монет при выборе направления
    await add_coins(
        telegram_id=callback.from_user.id,
        amount=50,
        reason="выбор направления",
        description="Бонус за выбор бизнес направления (business)"
    )

    video_file_id = os.getenv('VIDEO_FILE_ID')
    video_width = os.getenv('VIDEO_WIDTH')
    video_height = os.getenv('VIDEO_HEIGHT')
    video_duration = os.getenv('VIDEO_DURATION')

    if not video_file_id:
        msg = (
            "Ошибка: ID видео не найден. Пожалуйста, убедитесь, "
            "что VIDEO_FILE_ID установлен в файле .env"
        )
        if callback.message:
            await callback.message.answer(msg)
        return

    # Отправка видео с максимальными параметрами для сохранения качества
    if callback.message:
        if video_width and video_height:
            if video_duration:
                await callback.message.answer_video(
                    video=video_file_id,
                    width=int(video_width),
                    height=int(video_height),
                    duration=int(video_duration),
                    supports_streaming=True
                )
            else:
                await callback.message.answer_video(
                    video=video_file_id,
                    width=int(video_width),
                    height=int(video_height),
                    supports_streaming=True
                )
        else:
            await callback.message.answer_video(
                video=video_file_id,
                supports_streaming=True
            )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ ЗАБРАТЬ ПОДАРОК И ЗАПИСАТЬСЯ",
                    callback_data="register",
                )
            ]
        ]
    )

    text = """🤯 Впечатляет, правда?
Только что с тобой говорил не я, а мой цифровой двойник. Поздравляю! Твой баланс: 150 AI-Coins 🪙

<b>Представь, что так же автономно работает ТВОЙ бизнес</b>

💰 Реальные цифры моих клиентов:
Кофейня: Чат-бот принимает заказы ➡️ +30% к выручке
Салон красоты: Автозапись клиентов ➡️ минус 2 часа рутины
Ритейл: ИИ генерит контент ➡️ охваты ×3.

🎁 <b>Твой подарок (База нейросетей) уже ждет. Но сначала - давай закрепим твое место, чтобы система не аннулировала монет</b>

👇 Жми кнопку ниже.
"""
    if callback.message:
        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
