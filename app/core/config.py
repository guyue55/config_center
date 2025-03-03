import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    """应用配置"""
    # 应用名称
    APP_NAME: str = "配置中心"
    
    # 数据库URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./config_center.db")
    
    # 密钥
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # 特权模式
    PRIVILEGE_MODE: bool = os.getenv("PRIVILEGE_MODE", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        # 允许额外字段
        extra = "ignore"

settings = Settings()