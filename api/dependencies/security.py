import hmac
import json
from hashlib import sha256
from typing import Annotated
from urllib.parse import unquote, parse_qs, urlencode

from fastapi import Header, Depends

import config
from api.dependencies.exception import APIException


secret_key = hmac.new(b'WebAppData', bytes(config.BOT_TOKEN, encoding='utf-8'), sha256).digest()


class InitData:
    def __init__(self, qp: dict):
        self.query_id: str = qp.get("query_id", "")
        self.auth_date: int = int(qp.get("auth_date", 0))

        user = dict(json.loads(qp.get("user")))
        self.user_id: int = int(user.get("id", -1))
        self.first_name: str = user.get("first_name", "")
        self.last_name: str = user.get("last_name", "")
        self.username: str = user.get("username", "")
        self.language_code: str = user.get("language_code", "")


async def parse_launch_params(init_data: str = Header(
    ..., title="Telegram.WevApp.initData",
    description="Данные загрузки приложения для авторизации пользователя",
    example="query_id=AAGCAL0_AAAAAIIAvT9m-88z&user=%7B%22id%22%3A1069351042%2C%22first_name%22%3A%22Yaroslav%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22passionfde%22%2C%22language_code%22%3A%22ru%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1690396687&hash=b44292a9c1e418084508345ac62d3bd5588c5a181212c75930932fe0f2ddd1bf"
)) -> InitData:
    if not init_data:
        raise APIException(401, "Invalid initData")

    init_data_dict = {key: value[0] for key, value in parse_qs(init_data).items()}
    hash_value = init_data_dict.pop("hash", "")

    sorted_init_data = dict(sorted(init_data_dict.items()))
    check_data_string = urlencode(sorted_init_data, doseq=True, safe='=')
    check_data_string = unquote(check_data_string.replace('&', '\n'))

    init_data_hash = hmac.new(secret_key, bytes(check_data_string, encoding='utf-8'), sha256).hexdigest()

    if hash_value != init_data_hash:
        raise APIException(401, "Invalid initData")

    return InitData(init_data_dict)


HeaderInitParams = Annotated[InitData, Depends(parse_launch_params)]
