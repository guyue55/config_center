from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TypeBase(BaseModel):
    """配置类型基础模型"""
    type_name: str = Field(..., description="类型名称")
    description: Optional[str] = Field(None, description="类型描述")

class TypeCreate(TypeBase):
    """创建配置类型的请求模型"""
    pass

class TypeUpdate(BaseModel):
    """更新配置类型的请求模型"""
    type_name: Optional[str] = Field(None, description="类型名称")
    description: Optional[str] = Field(None, description="类型描述")

class TypeInDB(TypeBase):
    type_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class Type(TypeInDB):
    """配置类型响应模型"""
    type_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 替代旧版的 orm_mode = True

class TypeList(BaseModel):
    types: List[Type]
    total: int