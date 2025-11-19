
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from database import async_session
from models import User, Webinar
from keyboards import _get_additional_buttons # Импортируем функцию из keyboards

router = Router()

@router.callback_query((F.data == "register") | (F.data == "scale_business"))
async def show_next_webinar_handler(callback: CallbackQuery):
    """
    Показывает следующий вебинар и кнопку для подтверждения регистрации.
    """
    async with async_session() as session:
        # Находим следующий предстоящий вебинар
        webinar_result = await session.execute(
            select(Webinar).where(Webinar.webinar_date > func.now()).order_by(Webinar.webinar_date.asc()).limit(1)
        )
        next_webinar = webinar_result.scalar_one_or_none()

        if not next_webinar:
            await callback.message.answer("К сожалению, сейчас нет запланированных вебинаров.")
            await callback.answer()
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔥Зарегистрироваться🔥",
                        callback_data=f"confirm_registration_{next_webinar.id}",
                    )
                ]
            ]
        )
        await callback.message.answer(
            f"""🎉 Почти готово!

Ты в одном клике от доступа к знаниям, которые изменят твой подход к работе.

🔥 <b>Ближайший вебинар:</b>
📅 {next_webinar.webinar_date.strftime('%d.%m.%Y')}
⏰ {next_webinar.webinar_date.strftime('%H:%M')} по МСК

💡 Что получишь:

→ Инструменты, которые работают
→ Промпты, которые экономят часы
→ Схемы, которые можно применить завтра

⚡ Мест ограничено. Не упусти!

<b>ЖМИ КНОПКУ НИЖЕ - ✨ЗАРЕГИСТРИРОВАТЬСЯ✨</b>

После регистрации придёт:
✅ Ссылка на вебинар
✅ Напоминание за 1 час
✅ Бонусные материалы
""",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_registration_"))
async def confirm_registration_handler(callback: CallbackQuery):
    """
    Подтверждает регистрацию пользователя на вебинар.
    """
    webinar_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).options(selectinload(User.webinars)).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()

        # Находим вебинар
        webinar = await session.get(Webinar, webinar_id)

        if not user or not webinar:
            await callback.message.answer("Произошла ошибка. Попробуйте снова.")
            await callback.answer()
            return

        # Проверяем, не зарегистрирован ли пользователь уже
        if webinar in user.webinars:
            await callback.message.answer("Вы уже зарегистрированы на этот вебинар.")
            await callback.answer()
            return
        
        # Регистрируем пользователя
        user.webinars.append(webinar)
        await session.commit()

        # Формируем клавиатуру с дополнительными кнопками
        additional_buttons = _get_additional_buttons()
        keyboard = InlineKeyboardMarkup(inline_keyboard=additional_buttons)

        # Отправляем изображение
        image_url = (
            "https://image2url.com/images/1763061053554-10bed84f-dbf9-44ba-"
            "b230-8fc9a1549a99.jpeg"
        )
        await callback.message.answer_photo(image_url)

        # Отправляем текст сообщения
        text = """🎉 <b>УРА! ТЫ НА ВЕБИНАРЕ!</b>

Поздравляю! Ты только что сделал шаг, который изменит твой подход к работе навсегда.

✅ <b>Ты зарегистрирован!</b>

📲 <b>Что дальше:</b>

→ За 1 час до вебинара - напомню здесь, в боте 

→ Бонусные материалы, ниже под этим сообщением

🔥 <b>А пока можешь:</b>

👇 Выбери что интересно:

⚡ До встречи на вебинаре! Будет <b>ОГОНЬ!</b> 🔥"""

        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
    
    await callback.answer()
