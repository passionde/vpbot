from api.schemas.tags import TagInfo
from api.responses.base import BASE_MODEL_RESPONSE

GetTagsSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": TagInfo,
        "description": "Успешное выполнение"
    },
}