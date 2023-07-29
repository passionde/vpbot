from pydantic import BaseModel, Field


class TagInfo(BaseModel):
    """Модель данных тэгов"""
    tags_names: list[str] = Field(
        ...,
        title="Обложки видео",
        description="Массив ссылок на обложки видео разного разрешения",
        example=["random", "vocal", "sport", "dance", "beatbox", "talent"]
    )
