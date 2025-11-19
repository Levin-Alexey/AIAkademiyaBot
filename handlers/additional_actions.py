from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "private_channel")
async def private_channel_handler(callback: CallbackQuery):
    # Эта кнопка должна быть с url, поэтому этот обработчик может не вызываться,
    # но оставлен на случай, если url не указан или для отладки.
    await callback.answer("Вы выбрали 'Наш закрытый канал'.", show_alert=True)

@router.callback_query(F.data == "bonus_materials")
async def bonus_materials_handler(callback: CallbackQuery):
    await callback.answer("Вы выбрали 'Бонусные материалы'. Этот раздел в разработке.", show_alert=True)