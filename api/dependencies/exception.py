from fastapi import HTTPException


class APIException(HTTPException):
    def __init__(self, error_code: int, msg: str):
        super(APIException, self).__init__(
            status_code=400,
            detail={"error_code": error_code, "msg": msg}
        )