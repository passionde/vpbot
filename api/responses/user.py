from api.responses.base import BASE_MODEL_RESPONSE
import api.schemas.user as user

GetUserInfoSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": user.GetUserInfoResponse,
        "description": "Успешное выполнение"
    }
}