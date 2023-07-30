from pydantic import BaseModel

from api.schemas import fields


class GetUserTgProfileRequest(BaseModel):
    user_id: int = fields.user_id
