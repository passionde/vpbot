import api.schemas.video as video
import api.schemas.base as base
from api.responses.base import BASE_MODEL_RESPONSE

AddNewVideoSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": video.VideoInfo,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>1 - неверный формат ссылки на клип</li>"
                       "<li>2 - клип не найден</li>"
                       "<li>3 - у клипа отсутствует обязательный тег приложения</li>"
                       "<li>4 - данный клип уже добавлен</li>"
                       "<li>5 - клип принадлежит другому пользователю</li>"
                       "<li>6 - Видео восстановлено. Добавлено видео, которое ранее было удалено</li>"
                       "</ul>"
    }
}

ListVideoInfoSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": video.ListVideoInfo,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>2 - тэг не найден</li>"
                       "</ul>"
    }
}

DelVideoSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": base.SuccessResponse,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>2 - клип не найден</li>"
                       "<li>5 - клип принадлежит другому пользователю</li>"
                       "</ul>"
    }
}

