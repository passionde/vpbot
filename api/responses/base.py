from api.schemas import base

BASE_MODEL_RESPONSE = {
    401: {
        "model": base.ErrorResponse,
        "description": "Неверная <a href='https://dev.vk.com/mini-apps/development/launch-params'>"
                       "строка</a> загрузки приложения"
    }
}