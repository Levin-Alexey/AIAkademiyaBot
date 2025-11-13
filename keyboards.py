
from aiogram.types import InlineKeyboardButton

def _get_additional_buttons():
    """Возвращает список дополнительных кнопок."""
    return [
        [InlineKeyboardButton(text="Написать в поддержку", callback_data="support_contact")],
        [InlineKeyboardButton(text="Записаться на полный курс по ИИ", callback_data="enroll_course")],
        [InlineKeyboardButton(text="Наш закрытый канал", url="https://t.me/your_private_channel_link")] # Замените на реальную ссылку
    ]
