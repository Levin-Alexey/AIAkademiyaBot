
import os
import uuid
import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from dotenv import load_dotenv
from sqlalchemy import select, text
from yookassa import Configuration
from yookassa import Payment as YooKassaPayment  # noqa: F401

from database import async_session
from models import User, Course, Payment, PaymentStatus, course_registrations

load_dotenv()

router = Router()

# Настройка ЮКассы
Configuration.account_id = os.getenv('PAYMENT_SHOP_ID')
Configuration.secret_key = os.getenv('PAYMENT_SECRET_KEY')


@router.callback_query(F.data == "enroll_course")
async def enroll_course_handler(callback: CallbackQuery):
    """Обработчик кнопки записи на полный курс"""
    photo_url = (
        "https://image2url.com/images/"
        "1763093675664-50aea332-8b0b-4d62-89ac-d06086940beb.jpeg"
    )

    await callback.answer()

    if not callback.message:
        return

    async with async_session() as session:
        try:
            # Ищем активный курс
            stmt = select(Course).where(
                Course.is_active.is_(True),
                Course.start_date > datetime.now()
            ).order_by(Course.start_date.asc()).limit(1)
            result = await session.execute(stmt)
            course = result.scalar_one_or_none()

            if course:
                course_date = course.start_date.strftime('%d.%m.%Y')
                course_time = course.start_date.strftime('%H:%M')
                caption = (
                    f"<b>{course.course_name}</b>\n\n"
                    f"📅 Дата старта: {course_date} в {course_time} МСК\n"
                    f"💰 Цена: {float(course.price):.2f} ₽\n\n"
                )
                if course.description:
                    caption += f"{course.description}\n\n"
                caption += "Подробности об обучении позже..."
            else:
                caption = "Подробности об обучении позже..."

            # Создаем клавиатуру с кнопками
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Узнать подробнее",
                            callback_data="course_details"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Приобрести курс",
                            callback_data="purchase_course"
                        )
                    ]
                ]
            )

            try:
                await callback.message.answer_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception:
                # Если фото не отправилось, отправляем текст с кнопками
                await callback.message.answer(
                    caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

        except Exception:
            # Если ошибка, отправляем базовое сообщение
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Узнать подробнее",
                            callback_data="course_details"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Приобрести курс",
                            callback_data="purchase_course"
                        )
                    ]
                ]
            )
            try:
                await callback.message.answer_photo(
                    photo=photo_url,
                    caption="Подробности об обучении позже...",
                    reply_markup=keyboard
                )
            except Exception:
                await callback.message.answer(
                    "Подробности об обучении позже...",
                    reply_markup=keyboard
                )


@router.callback_query(F.data == "purchase_course")
async def purchase_course_handler(callback: CallbackQuery):
    """Обработчик кнопки покупки курса"""
    await callback.answer()

    if not callback.message:
        return

    telegram_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Пользователь"
    default_webhook = "https://lexi.neuronaikids.ru/webhook"
    webhook_url = os.getenv('WEBHOOK_URL', default_webhook)

    async with async_session() as session:
        try:
            # 1. Получаем или создаем пользователя
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    user_name=callback.from_user.username
                )
                session.add(user)
                await session.flush()  # Получаем ID пользователя

            # 2. Ищем активный курс
            stmt = select(Course).where(
                Course.is_active.is_(True),
                Course.start_date > datetime.now()
            ).order_by(Course.start_date.asc()).limit(1)
            result = await session.execute(stmt)
            course = result.scalar_one_or_none()

            if not course:
                await callback.message.answer(
                    "❌ В данный момент нет доступных курсов для покупки."
                )
                return

            # 3. Проверяем, не купил ли уже пользователь этот курс
            # Проверяем через course_registrations
            stmt = select(course_registrations).where(
                course_registrations.c.user_id == user.id,
                course_registrations.c.course_id == course.id
            )
            result = await session.execute(stmt)
            existing_registration = result.first()

            if existing_registration:
                await callback.message.answer(
                    f"✅ Вы уже зарегистрированы на курс "
                    f"<b>{course.course_name}</b>!\n\n"
                    f"📅 Дата старта: "
                    f"{course.start_date.strftime('%d.%m.%Y в %H:%M')} МСК",
                    parse_mode="HTML"
                )
                return

            # 4. Проверяем, нет ли уже успешного платежа
            # Используем SQL cast для правильного сравнения enum
            status_value = PaymentStatus.SUCCEEDED.value
            stmt = select(Payment).where(
                Payment.user_id == user.id,
                Payment.course_id == course.id,
                text(f"payments.status = '{status_value}'::payment_status")
            )
            result = await session.execute(stmt)
            existing_payment = result.scalar_one_or_none()

            if existing_payment:
                await callback.message.answer(
                    f"✅ У вас уже есть оплаченный доступ к курсу "
                    f"<b>{course.course_name}</b>!\n\n"
                    f"📅 Дата старта: "
                    f"{course.start_date.strftime('%d.%m.%Y в %H:%M')} МСК",
                    parse_mode="HTML"
                )
                return

            # 5. Создаем уникальный ID платежа для ЮКассы
            yookassa_payment_id = str(uuid.uuid4())

            # 6. Создаем платеж через API ЮКассы
            # Для receipt ОБЯЗАТЕЛЬНО нужен email или телефон покупателя
            customer_data = {}
            # Пробуем получить email или телефон (если доступны)
            user_email = getattr(callback.from_user, 'email', None)
            user_phone = getattr(callback.from_user, 'phone', None)
            
            # ВСЕГДА заполняем customer_data
            if user_email:
                customer_data["email"] = user_email
            elif user_phone:
                customer_data["phone"] = user_phone
            else:
                # Если нет email и телефона, используем дефолтный email или создаем временный
                default_email = os.getenv('DEFAULT_CUSTOMER_EMAIL', '')
                if default_email:
                    customer_data["email"] = default_email
                else:
                    # Создаем временный email на основе telegram_id
                    customer_data["email"] = f"user_{telegram_id}@telegram.local"
            
            payment_data = {
                "amount": {
                    "value": f"{float(course.price):.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": webhook_url
                },
                "capture": True,
                "description": f"Оплата курса: {course.course_name}",
                "receipt": {
                    "customer": customer_data,
                    "items": [
                        {
                            "description": course.course_name,
                            "quantity": "1.00",
                            "amount": {
                                "value": f"{float(course.price):.2f}",
                                "currency": "RUB"
                            },
                            "vat_code": 1,  # НДС не облагается (для образовательных услуг)
                            "payment_subject": "service",  # Обязательное поле: услуга
                            "payment_mode": "full_prepayment"  # Обязательное поле: способ расчета
                        }
                    ]
                },
                "metadata": {
                    "user_id": str(user.id),
                    "telegram_id": str(telegram_id),
                    "user_name": user_name,
                    "course_id": str(course.id),
                    "course_name": course.course_name
                }
            }
            
            yookassa_payment = YooKassaPayment.create(payment_data, yookassa_payment_id)

            # 7. Сохраняем платеж в БД
            # Используем прямое SQL для правильного сохранения enum
            from sqlalchemy import insert
            result = await session.execute(
                insert(Payment).values(
                    user_id=user.id,
                    course_id=course.id,
                    payment_id=yookassa_payment_id,
                    amount=course.price,
                    currency="RUB",
                    status=text(f"'{PaymentStatus.PENDING.value}'::payment_status"),
                    payment_metadata=json.dumps(yookassa_payment.metadata or {})
                ).returning(Payment.id)
            )
            payment_db_id = result.scalar_one()
            await session.commit()
            
            # Платеж успешно сохранен в БД, объект не нужен для дальнейшей работы

            # 8. Получаем ссылку на оплату
            payment_url = yookassa_payment.confirmation.confirmation_url

            # 9. Отправляем пользователю ссылку на оплату
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 Оплатить курс",
                            url=payment_url
                        )
                    ]
                ]
            )

            course_date = course.start_date.strftime('%d.%m.%Y')
            course_time = course.start_date.strftime('%H:%M')

            await callback.message.answer(
                f"💳 <b>Оплата курса: {course.course_name}</b>\n\n"
                f"📅 Дата старта: {course_date} в {course_time} МСК\n"
                f"💰 Сумма: {float(course.price):.2f} ₽\n\n"
                f"Нажмите на кнопку ниже, чтобы перейти к оплате:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        except Exception as e:
            await session.rollback()
            await callback.message.answer(
                f"❌ Произошла ошибка при создании платежа. "
                f"Попробуйте позже.\n\nОшибка: {str(e)}"
            )
