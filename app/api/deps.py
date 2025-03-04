from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.config import settings
from app.models.database import get_db
from app.models.config import Config

async def is_privilege_mode(db: AsyncSession) -> bool:
    """检查是否启用了特权模式"""
    # 首先检查环境变量中的特权模式设置
    if settings.PRIVILEGE_MODE:
        return True
        
    # 如果环境变量中没有启用特权模式，则检查数据库中的配置
    try:
        result = await db.execute(
            select(Config).where(
                Config.key == "privilege_mode"
            )
        )
        config = result.scalar_one_or_none()
        return config is not None and config.value.lower() == "true"
    except Exception as e:
        print(f"检查特权模式出错: {e}")
        return False

# 以下函数用于兼容性目的，返回None表示无用户
async def get_current_user_optional(db: AsyncSession = Depends(get_db)) -> None:
    """获取当前用户（可选，未登录返回None）"""
    return None

# 兼容性函数
async def get_current_active_user(db: AsyncSession = Depends(get_db)) -> None:
    """获取当前活跃用户（兼容性函数）"""
    return None

# 兼容性函数
async def get_current_admin_user(db: AsyncSession = Depends(get_db)) -> None:
    """获取当前管理员用户（兼容性函数）"""
    return None
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user