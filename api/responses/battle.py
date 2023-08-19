from api.responses.base import BASE_MODEL_RESPONSE
from api.schemas import base
from api.schemas.battle import GetAllCurrentBattlesResponse, AssignRandomOpponentResponse

AppointBattleSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": base.SuccessResponse,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>1 - видео пользователя не найдено. Возможно при удалении видео на YouTube</li>"
                       "<li>2 - видео противника не найдено. Возможно при удалении видео на YouTube</li>"
                       "<li>3 - отказано в доступе. Видео принадлежит другому пользователю</li>"
                       "<li>4 - данному видео уже был брошен вызов. Возникает при повторном назначении вызова. "
                       "При этом завершенным и отказанным вызовам, повторная отправка разрешена</li>"
                       "<li>5 - у видео отличаются категории</li>"
                       "</ul>"
    }
}


AgreeBattleSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": base.SuccessResponse,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>1 - видео пользователя не найдено. Возможно при удалении его в приложении</li>"
                       "<li>2 - видео противника не найдено. Возможно при удалении его в приложении</li>"
                       "<li>3 - отказано в доступе. Видео принадлежит другому пользователю</li>"
                       "<li>4 - не найдено приглашение на батл</li>"
                       "<li>5 - на данное приглашение уже было принято решение</li>"
                       "<li>6 - видео пользователя не найдено. Возможно при удалении видео на YouTube</li>"
                       "<li>7 - видео противника не найдено. Возможно при удалении видео на YouTube</li>"
                       "<li>8 - системная ошибка при сохранение в БД</li>"
                       "</ul>"
    }
}

GiveUpBattleSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": base.SuccessResponse,
        "description": "Успешное выполнение"
    },
    400: {
        "model": base.ErrorResponse,
        "description": "Ошибка при обработке запроса. В ответе содержится код ошибки error_code:\n"
                       "<ul>"
                       "<li>1 - видео пользователя не найдено. Возможно при удалении его в приложении</li>"
                       "<li>2 - видео противника не найдено. Возможно при удалении его в приложении</li>"
                       "<li>3 - отказано в доступе. Видео принадлежит другому пользователю</li>"
                       "<li>4 - не найдено приглашение на батл</li>"
                       "<li>5 - на данное приглашение уже было принято решение</li>"
                       "<li>8 - системная ошибка при сохранение в БД</li>"
                       "</ul>"
    }
}

GetAllCurrentBattlesSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": GetAllCurrentBattlesResponse,
        "description": "Успешное выполнение"
    }
}

AssignRandomOpponentSchema = {
    **BASE_MODEL_RESPONSE,
    200: {
        "model": AssignRandomOpponentResponse,
        "description": "Успешное выполнение. Если видео не найдено, вернется пустая строка"
    },
}
