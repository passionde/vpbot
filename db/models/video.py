import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

from db.models.database import Base


# Модель тэга
class Tag(Base):
    __tablename__ = "Tag"

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String)


class Video(Base):
    __tablename__ = "Video"

    video_id = Column(String, primary_key=True)
    date_added = Column(DateTime(timezone=True), default=datetime.datetime.now)
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("User.user_id"))
    tag_id = Column(Integer, ForeignKey("Tag.tag_id"))
