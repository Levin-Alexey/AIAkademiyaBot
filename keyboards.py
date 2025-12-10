
from aiogram.types import InlineKeyboardButton


def _get_additional_buttons():
    """Возвращает список дополнительных кнопок."""
    return [
        [InlineKeyboardButton(
            text="💬 Написать в поддержку",
            url="https://t.me/LevinMSK"
        )],
        # [InlineKeyboardButton(
        #     text="🚀 Записаться на полный курс по ИИ",
        #     callback_data="enroll_course"
        # )],

    ]
