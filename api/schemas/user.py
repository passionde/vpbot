import datetime

from pydantic import BaseModel, Field

from api.schemas import fields


class GetUserVideosByTagRequest(BaseModel):
    """Модель запроса для метода POST get-user-videos-by-tag"""
    tag: str = fields.tag


class GetUserInfoResponse(BaseModel):
    """Модель ответа для метода POST get-user-info"""
    user_id: int = fields.user_id
    vp_coins: int = Field(
        ...,
        title="VPCoins",
        example=10,
        description="Количество VPCoin на балансе пользователя"
    )
    rating: int = Field(
        ...,
        title="Рейтинг",
        example=120,
        description="Рейтинг пользователя"
    )
    date_added: datetime.datetime = Field(
        ...,
        description="Дата регистрации пользователя"
    )
