from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    info: str
