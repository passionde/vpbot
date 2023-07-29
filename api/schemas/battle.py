import datetime

from pydantic import BaseModel, Field
from api.schemas import fields


class BattleMethodRequest(BaseModel):
    """Модель запроса для метода POST appoint-battle"""
    user_video_id: str = Field(
        ...,
        title="ID видео",
        example="EdOJ8QoU_Uk",
        description="ID видео, которым нападает пользователь, который сгенерировал запрос"
    )
    opponent_video_id: str = Field(
        ...,
        title="ID видео",
        example="EdOJ8QoU_Uk",
        description="ID видео, которому бросают вызов"
    )


class InvitationOptionsRequest(BaseModel):
    """Модель запроса для методов обработки приглашения на батл"""
    invitation_id: int = Field(
        ...,
        title="ID приглашения",
        example="3",
        description="ID приглашения, которое передается в оповещениях"
    )


class GetAllCurrentBattlesRequest(BaseModel):
    """Модель запроса для метода get-current-battles-by-tag"""
    page: int = fields.page
    tag: str = fields.tag


class Participant(BaseModel):
    video_id: str = fields.video_id
    likes_start: int = Field(
        ...,
        description="Количество лайков у видео на момент старта",
        example=300
    )
    user_id: int = fields.user_id


class ItemResponseGetAllCurrentBattles(BaseModel):
    """Модель элемента ответа роутера get-all-current-battles"""
    battle_id: int = Field(
        ...,
        description="Порядковый номер батла",
        example=2
    )
    date_start: datetime.datetime = Field(
        ...,
        description="Дата начала батла"
    )
    date_end: datetime.datetime = Field(
        ...,
        description="Дата окончания батла"
    )
    participant_1: Participant
    participant_2: Participant


class GetAllCurrentBattlesResponse(BaseModel):
    """Модель ответа роутера get-all-current-battles"""
    items: list[ItemResponseGetAllCurrentBattles]