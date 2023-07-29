import datetime

from sqlalchemy import Column, Integer, DateTime

from setting import START_VP_COINS
from db.models.database import Base


# Модель пользователя
class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True)
    vp_coins = Column(Integer, default=START_VP_COINS)
    rating = Column(Integer, default=0)

    date_added = Column(DateTime(timezone=True), default=datetime.datetime.now)
