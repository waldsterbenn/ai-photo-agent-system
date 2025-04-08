from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional


class UserModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    info: str
