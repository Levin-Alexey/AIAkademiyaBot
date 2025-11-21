
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
                    text="🚀 ЗАРЕГИСТРИРОВАТЬСЯ",
                    callback_data="register",
                )
            ]
        ]
    )

    text = """🎯 <b>Вот так выглядит будущее работы!</b>

Ты только что увидел, как ИИ может изменить твою продуктивность.
А теперь представь:

✨ <b>Твой обычный день с ИИ:</b>
→ <b>Утро:</b> ИИ составил план дня за 30 секунд
→ <b>День:</b> Письма клиентам написаны за 5 минут вместо часа
→ <b>Вечер:</b> Отчёт готов за 10 минут, ты идёшь домой вовремя

🔥 <b>На вебинаре ты получишь:</b>
✅ Готовые промпты для писем, планов, отчётов
✅ ТОП-10 ИИ для работы (все бесплатные)
✅ Схемы автоматизации твоих задач

💡 Покажу то, как профессионалы экономят 15+ часов в неделю

🔐 <b>После регистрации:</b> доступ в закрытую группу с ТОП нейросетями и промптами

⚡ <b>Результат:</b> Работаешь меньше. Успеваешь больше. Живёшь лучше.

<b>Нажимай кнопку ЗАРЕГИСТРИРОВАТЬСЯ, выбери дату и прокачивайся в ИИ</b>
"""
    if callback.message:
        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
