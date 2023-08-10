
from api.responses.base import BASE_MODEL_RESPONSE
import api.schemas.user as user
from api.schemas import base

GetUserInfoSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": user.GetUserInfoResponse,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>1 - не получилось отправить запрос на получение информации об аккаунте пользователя</li>"
                       "</ul>"
    }
}