from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import bcrypt
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, UserList
from app.api.deps import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("", response_model=UserList)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取所有用户（仅管理员）
    """
    # 查询总数
    result = await db.execute(select(func.count()).select_from(User))
    total = result.scalar()
    
    # 查询用户列表
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    
    return {"users": users, "total": total}

@router.post("", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    创建新用户（仅管理员）
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 哈希密码
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    
    # 创建新用户
    db_user = User(
        username=user_data.username,
        password=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户信息
    """
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取指定用户信息（仅管理员）
    """
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新用户信息（仅管理员）
    """
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
    
    # 更新用户信息
    if user_data.password:
        user.password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    if user_data.role:
        user.role = user_data.role
    
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    删除用户（仅管理员）
    """
    # 不允许删除自己
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的用户")
    
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")
    
    await db.delete(user)
    await db.commit()
    
    return {"message": f"用户ID {user_id} 已成功删除"}