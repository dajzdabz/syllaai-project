# ===== BEGIN app/schemas/user.py =====
from pydantic import BaseModel
from uuid import UUID

class UserBase(BaseModel):
    email: str
    name: str | None

class UserCreate(UserBase):
    role: str
    auth_provider: str
    external_id: str

class User(UserBase):
    id: UUID
    role: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID
# ===== END app/schemas/user.py =====
