from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Схема ошибки"""
    error_code: int = Field(
        ...,
        title="Код ошибки",
        example=3,
        description="Содержит код ошибки"
    )
    msg: str = Field(
        ...,
        title="Сообщение ошибки",
        example="the clip is missing a required application tag",
        description="Содержит сообщение ошибки"
    )


class ErrorResponse(BaseModel):
    detail: ErrorDetail


class SuccessResponse(BaseModel):
    """Модель ответа для методов без тела ответа"""
    success: bool = Field(..., title="Статус запроса", description="true - выполнен, false - нет", example=True)
