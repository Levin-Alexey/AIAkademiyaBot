from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "private_channel")
async def private_channel_handler(callback: CallbackQuery):
    # Эта кнопка должна быть с url, поэтому этот обработчик может не вызываться,
    # но оставлен на случай, если url не указан или для отладки.
    await callback.answer("Вы выбрали 'Наш закрытый канал'.", show_alert=True)