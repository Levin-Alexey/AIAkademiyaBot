
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database import async_session
from models import User, Webinar
from keyboards import _get_additional_buttons
from coin_service import add_coins, get_balance

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
                        text="✨ ПОДТВЕРДИТЬ УЧАСТИЕ ✨",
                        callback_data=f"confirm_registration_{next_webinar.id}",
                    )
                ]
            ]
        )
        await callback.message.answer(
            f"""🏁 Финишная прямая!

🗓 Дата: {next_webinar.webinar_date.strftime('%d.%m.%Y')}
⏰ Время: {next_webinar.webinar_date.strftime('%H:%M')} МСК
📍 Место: Онлайн

⚠️ Важно: Чтобы забрать Базу нейросетей и активировать доступ к закрытой группе, нажми финальную кнопку регистрации.

За это действие я начислю еще +100 монет! 🪙
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

        # Начисляем +100 монет при подтверждении регистрации
        await add_coins(
            telegram_id=callback.from_user.id,
            amount=100,
            reason="подтверждение регистрации",
            description="Бонус за подтверждение регистрации на вебинар"
        )

        inline_keyboard = []
        # if webinar.webinar_link: # Используем webinar.webinar_link, а не upcoming_registration.webinar_link
        #     inline_keyboard.append([
        #         InlineKeyboardButton(
        #             text="🎥 Ссылка на вебинар",
        #             url=webinar.webinar_link,
        #         )
        #     ])
        inline_keyboard.append([
            InlineKeyboardButton(
                text="🔐 Закрытая группа по ИИ",
                url="https://t.me/+VxGcD_UbVJE5NTNi"
            )
        ])
        
        # Добавляем дополнительные кнопки
        inline_keyboard.extend(_get_additional_buttons())

        inline_keyboard.append([
            InlineKeyboardButton(
                text="ℹ️ Информация о спикере",
                callback_data="speaker_info"
            )
        ])
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        # Отправляем изображение
        image_url = (
            "https://image2url.com/images/1763061053554-10bed84f-dbf9-44ba-"
            "b230-8fc9a1549a99.jpeg"
        )
        await callback.message.answer_photo(image_url)

        # Отправляем текст сообщения
        balance = await get_balance(callback.from_user.id)
        text = f"""🎉 УРА! ТЫ В СПИСКЕ УЧАСТНИКОВ!

✅ Регистрация пройдена.
💰 Твой баланс: {balance} AI-Coins (Ты сможешь обменять их на скидку или бонусы в конце вебинара).

📲 Что дальше:
Ссылку на вход я пришлю в этот бот:
- в день эфира утром
- за 1 час до старта.

🔥 А ТЕПЕРЬ - ГЛАВНЫЙ БОНУС!
Я открыл тебе доступ в Закрытый канал, где уже лежит та самая полезная информация.

👇 Вступай прямо сейчас, пока ссылка активна"""

        await callback.message.answer(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
    
    await callback.answer()
