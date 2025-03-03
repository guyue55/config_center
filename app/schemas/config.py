from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class ConfigBase(BaseModel):
    key: str = Field(..., description="配置键")
    value: str = Field(..., description="配置值")
    key_description: Optional[str] = Field(None, description="配置键描述")

class ConfigCreate(ConfigBase):
    type_name: Optional[str] = Field("default", description="配置类型名称")

class ConfigUpdate(BaseModel):
    value: Optional[str] = Field(None, description="配置值")
    key_description: Optional[str] = Field(None, description="配置键描述")

class ConfigInDB(ConfigBase):
    config_id: int
    type_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Config(ConfigInDB):
    type_name: str

class ConfigList(BaseModel):
    configs: List[Config]
    total: int

class ConfigSearch(BaseModel):
    type_name: Optional[str] = Field(None, description="配置类型名称")
    key: Optional[str] = Field(None, description="配置键")
    value: Optional[str] = Field(None, description="配置值")
    exact_match: bool = Field(False, description="是否精确匹配")