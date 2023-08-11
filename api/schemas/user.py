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
    photo_url_160: str = Field(
        ...,
        description="URL на первую фотографию пользователя 160x160",
        example="https://vpchallenge.tw1.su/img/1069351042.jpg"
    )
    username_or_first_name: str = Field(
        ...,
        description="Username пользователя или его имя",
        example="passionde"
    )
    url: str = Field(
        ...,
        description="Ссылка на аккаунт пользователя",
        example="tg://user?id=1069351042"
    )
