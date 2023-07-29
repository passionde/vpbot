import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

from db.models.database import Base


# Модель участника батла
class Participant(Base):
    __tablename__ = "Participant"

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    number_likes_start = Column(Integer, default=0)
    number_likes_finish = Column(Integer, default=0)

    video_id = Column(String, ForeignKey("Video.video_id"))


# Модель батла
class Battle(Base):
    __tablename__ = "Battle"

    battle_id = Column(Integer, primary_key=True, autoincrement=True)

    date_start = Column(DateTime(timezone=True), default=datetime.datetime.now)
    date_end = Column(DateTime(timezone=True))
    is_finish = Column(Boolean, default=False)

    participant_1 = Column(Integer, ForeignKey("Participant.participant_id"))
    participant_2 = Column(Integer, ForeignKey("Participant.participant_id"))
    winner = Column(Integer, ForeignKey("Participant.participant_id"))


class InvitationBattle(Base):
    __tablename__ = "InvitationBattle"

    invitation_id = Column(Integer, primary_key=True, autoincrement=True)
    date_added = Column(DateTime(timezone=True), default=datetime.datetime.now)
    status = Column(Integer, default=1)  # todo сделать привязку к таблице 1 - ожидание, 2 - отмена, 3 - согласие
    video_id_appointing = Column(String, ForeignKey("Video.video_id"))
    video_id_accepting = Column(String, ForeignKey("Video.video_id"))
