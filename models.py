
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from database import engine

Base = declarative_base()

# Association Table for User and Webinar (many-to-many)
webinar_registrations = Table('webinar_registrations', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('webinar_id', Integer, ForeignKey('webinars.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    user_name = Column(String)
    start_time = Column(DateTime, default=func.now())
    direction = Column(String, nullable=True)

    # Relationship to the Webinar model
    webinars = relationship('Webinar', secondary=webinar_registrations, back_populates='attendees')

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, user_name='{self.user_name}')>"

class Webinar(Base):
    __tablename__ = 'webinars'

    id = Column(Integer, primary_key=True)
    webinar_date = Column(DateTime, nullable=False)
    topic = Column(String, default="Общий вебинар")
    webinar_link = Column(String, nullable=True)

    # Relationship to the User model
    attendees = relationship('User', secondary=webinar_registrations, back_populates='webinars')

    def __repr__(self):
        return f"<Webinar(id={self.id}, date='{self.webinar_date.strftime('%Y-%m-%d %H:%M')}')>"


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

