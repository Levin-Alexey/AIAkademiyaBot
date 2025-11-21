
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


@router.callback_query(F.data == "direction_business")
async def direction_business_handler(callback: CallbackQuery):
    await callback.answer()

    async with async_session() as session:
        stmt = update(User).where(
            User.telegram_id == callback.from_user.id
        ).values(direction='business')
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
                    text="💰 ХОЧУ МАСШТАБИРОВАТЬ БИЗНЕС!",
                    callback_data="register",
                )
            ]
        ]
    )

    text = """🚀 <b>Это будущее твоего бизнеса!</b>

Ты только что увидел, как ИИ работает. А теперь представь, что так же работает ТВОЙ бизнес.

💰 <b>Реальные цифры моих клиентов:</b>
→ <b>Кофейня:</b> Чат-бот принимает заказы → <b>+30% к выручке</b>
→ <b>Салон:</b> Автозапись клиентов → <b>-2 часа работы админа</b>
→ <b>Магазин:</b> ИИ генерит контент → <b>×3 охваты в соцсетях</b>

И это БЕЗ программистов. БЕЗ больших вложений.

🔥 <b>На вебинаре ты получишь:</b>
✅ Чат-боты для клиентов (запуск за 1 день, бесплатно)
✅ ИИ-контент для соцсетей (10 постов за 15 минут)
✅ Автоматизация процессов без кода

💡 Покажу схемы, которые работают в реальном бизнесе

🔐 <b>После регистрации:</b> доступ в закрытую группу с 70+ ИИ для бизнеса и готовыми кейсами

⚡ <b>Результат:</b> Больше клиентов. Меньше рутины. Рост без найма.

🔒 Данные в безопасности | ✅ Вебинар бесплатный | ⏰ Напомним за час
"""
    if callback.message:
        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
