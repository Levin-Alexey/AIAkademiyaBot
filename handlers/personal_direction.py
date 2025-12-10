
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


@router.callback_query(F.data == "direction_personal")
async def direction_personal_handler(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        stmt = update(User).where(
            User.telegram_id == callback.from_user.id
        ).values(direction='personal')
        await session.execute(stmt)
        await session.commit()

    # Начисляем +50 монет при выборе направления
    await add_coins(
        telegram_id=callback.from_user.id,
        amount=50,
        reason="выбор направления",
        description="Бонус за выбор личного направления (personal)"
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

    text = """🤯 Круто, да?
Пока мой цифровой аватар общался с тобой, я пил кофе или занимался стратегией.

<b>Именно так выглядит личная эффективность с ИИ.</b> Ты перестаешь быть «белкой в колесе» и становишься архитектором своей жизни.

🔥 <b>На вебинаре за 1 час ты научишься:</b>
✅ Писать письма и отчеты за секунды (вместо часов мучений).
✅ Делать презентации и картинки, не будучи дизайнером.
✅ Учиться новому в 10 раз быстрее с персональным ИИ-ментором.

🎁 <b>Твой подарок уже ждет!</b> Я открываю тебе доступ в закрытый канал, где уже лежит база лучших нейросетей и инструкции.

👇 <b>Жми кнопку, чтобы забрать доступ и закрепить за собой место на эфире!</b>
"""
    if callback.message:
        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
