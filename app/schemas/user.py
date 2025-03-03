from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., description="用户名")

class UserCreate(UserBase):
    password: str = Field(..., description="密码")
    role: Optional[str] = Field("user", description="用户角色")

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, description="密码")
    role: Optional[str] = Field(None, description="用户角色")

class UserInDB(UserBase):
    user_id: int
    role: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class UserList(BaseModel):
    users: List[User]
    total: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None