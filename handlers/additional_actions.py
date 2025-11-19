from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "support_contact")
async def support_contact_handler(callback: CallbackQuery):
    await callback.answer("Вы выбрали 'Написать в поддержку'. Скоро здесь будет форма или контакт.", show_alert=True)
    # Здесь можно добавить логику для связи с поддержкой, например, ссылку на Telegram-аккаунт или форму.

@router.callback_query(F.data == "private_channel")
async def private_channel_handler(callback: CallbackQuery):
    # Эта кнопка должна быть с url, поэтому этот обработчик может не вызываться,
    # но оставлен на случай, если url не указан или для отладки.
    await callback.answer("Вы выбрали 'Наш закрытый канал'.", show_alert=True)

@router.callback_query(F.data == "bonus_materials")
async def bonus_materials_handler(callback: CallbackQuery):
    await callback.answer("Вы выбрали 'Бонусные материалы'. Этот раздел в разработке.", show_alert=True)