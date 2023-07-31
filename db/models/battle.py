import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

from db.models.database import Base
from setting import DEFAULT_TAG


# Модель батла
class Battle(Base):
    __tablename__ = "Battle"

    battle_id = Column(Integer, primary_key=True, autoincrement=True)

    date_start = Column(DateTime(timezone=True), default=datetime.datetime.now)
    date_end = Column(DateTime(timezone=True))
    is_finish = Column(Boolean, default=False)

    video_id_1 = Column(String, ForeignKey("Video.video_id"))
    video_id_2 = Column(String, ForeignKey("Video.video_id"))

    likes_start_1 = Column(Integer, default=0)
    likes_start_2 = Column(Integer, default=0)

    likes_finish_1 = Column(Integer, default=0)
    likes_finish_2 = Column(Integer, default=0)

    winner_id = Column(String, ForeignKey("Video.video_id"))
    loser_id = Column(String, ForeignKey("Video.video_id"))

    invitation_id = Column(Integer, ForeignKey("InvitationBattle.invitation_id"))
    tag_name = Column(String, ForeignKey("Tag.tag"))


class StatusInvitation(Base):
    __tablename__ = "StatusInvitation"
    status = Column(String, primary_key=True)


class InvitationBattle(Base):
    __tablename__ = "InvitationBattle"

    invitation_id = Column(Integer, primary_key=True, autoincrement=True)
    date_added = Column(DateTime(timezone=True), default=datetime.datetime.now)

    status = Column(Integer, ForeignKey("StatusInvitation.status"), default="waiting")  # todo сделать ENUM
    video_id_appointing = Column(String, ForeignKey("Video.video_id"))
    video_id_accepting: Column = Column(String, ForeignKey("Video.video_id"))
