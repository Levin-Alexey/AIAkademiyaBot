
from sqlalchemy import (
    Column, Integer, String, BigInteger, DateTime, func, Table,
    ForeignKey, Numeric, Boolean, Text, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from database import engine
import enum

Base = declarative_base()


# Enum для статусов платежа
class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"


# Association Table for User and Webinar (many-to-many)
webinar_registrations = Table('webinar_registrations', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('webinar_id', Integer, ForeignKey('webinars.id'), primary_key=True)
)

# Association Table for User and Course (many-to-many)
course_registrations = Table('course_registrations', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('registration_date', DateTime, default=func.now())
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    user_name = Column(String)
    start_time = Column(DateTime, default=func.now())
    direction = Column(String, nullable=True)

    # Relationship to the Webinar model (бесплатные вебинары)
    webinars = relationship(
        'Webinar',
        secondary=webinar_registrations,
        back_populates='attendees'
    )

    # Relationship to the Course model (платные курсы)
    courses = relationship(
        'Course',
        secondary=course_registrations,
        back_populates='students'
    )

    # Relationship to payments
    payments = relationship('Payment', back_populates='user')

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, user_name='{self.user_name}')>"

class Webinar(Base):
    __tablename__ = 'webinars'

    id = Column(Integer, primary_key=True)
    webinar_date = Column(DateTime, nullable=False)
    topic = Column(String, default="Общий вебинар")
    webinar_link = Column(String, nullable=True)

    # Relationship to the User model
    attendees = relationship(
        'User',
        secondary=webinar_registrations,
        back_populates='webinars'
    )

    def __repr__(self):
        return f"<Webinar(id={self.id}, date='{self.webinar_date.strftime('%Y-%m-%d %H:%M')}')>"


class Course(Base):
    """Модель платного курса"""
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    course_name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Цена в рублях
    description = Column(Text, nullable=True)
    course_link = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship to the User model
    students = relationship(
        'User',
        secondary=course_registrations,
        back_populates='courses'
    )

    # Relationship to payments
    payments = relationship('Payment', back_populates='course')

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.course_name}', price={self.price})>"


class Payment(Base):
    """Модель платежа через ЮКассу"""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    payment_id = Column(String, unique=True, nullable=False, index=True)  # ID от ЮКассы
    amount = Column(Numeric(10, 2), nullable=False)  # Сумма в рублях
    currency = Column(String, default='RUB', nullable=False)
    status = Column(
        Enum(PaymentStatus, name='payment_status', create_type=False, native_enum=True),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=func.now(), nullable=False)
    paid_at = Column(DateTime, nullable=True)
    payment_metadata = Column(Text, nullable=True)  # JSON с дополнительными данными

    # Relationships
    user = relationship('User', back_populates='payments')
    course = relationship('Course', back_populates='payments')

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, payment_id='{self.payment_id}', "
            f"status={self.status.value}, amount={self.amount})>"
        )


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

