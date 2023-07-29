import datetime

from pydantic import BaseModel, Field

import api.schemas.fields as fields


class VideoInfo(BaseModel):
    """Модель данных видео"""
    video_id: str = fields.video_id
    tag: str = fields.tag
    date_added: datetime.datetime = Field(
        ...,
        description="Дата добавления видео"
    )
    thumbnails: list[str] = Field(
        ...,
        title="Обложки видео",
        description="Массив ссылок на обложки видео разного разрешения",
        example=[
            "https://i.ytimg.com/vi/VIDEOID/default.jpg",
            "https://i.ytimg.com/vi/VIDEOID/hqdefault.jpg",
            "https://i.ytimg.com/vi/VIDEOID/maxresdefault.jpg",
            "https://i.ytimg.com/vi/VIDEOID/mqdefault.jpg",
            "https://i.ytimg.com/vi/VIDEOID/sddefault.jpg",
        ]
    )
    owner_id: int = Field(
        ...,
        description="user_id владельца видео"
    )


class ListVideoInfo(BaseModel):
    """Массив клипов"""
    items: list[VideoInfo]


class AddNewVideoRequest(BaseModel):
    """Модель запроса для метода POST add-new-video"""
    video_url: str = Field(
        ...,
        title="Ссылка на видео в YouTube",
        examples=["https://www.youtube.com/shorts/VIDEOID", "https://youtube.com/shorts/VIDEOID"],
        description="Обязательная ссылка на клип. Должна вести на /shorts/ и относится к YouTube"
    )


class GetAllVideosByTagRequest(BaseModel):
    """Модель запроса для метода POST get_all_videos_by_tag"""
    tag: str = fields.tag
    page: int = fields.page


class DelVideoVideoRequest(BaseModel):
    """Модель запроса для метода POST del-video"""
    video_id: str = fields.video_id
