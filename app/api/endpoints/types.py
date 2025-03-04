from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.models.database import get_db
from app.models.type import Type
from app.models.config import Config
from app.schemas.type import TypeCreate, TypeUpdate, Type as TypeSchema, TypeList

router = APIRouter()

# 删除重复的路由，只保留一个获取所有类型的路由
@router.get("", response_model=TypeList)
async def get_types(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有配置类型
    """
    # 构建查询条件
    query = select(Type)
    if search:
        query = query.where(Type.type_name.contains(search) | Type.description.contains(search))
    
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 查询类型列表
    result = await db.execute(query.offset(skip).limit(limit))
    types = result.scalars().all()
    
    return {"types": types, "total": total}

@router.post("", response_model=TypeSchema)
async def create_type(
    type_data: TypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的配置类型
    """
    
    # 检查类型名是否已存在
    result = await db.execute(select(Type).where(Type.type_name == type_data.type_name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="类型名已存在")
    
    # 创建新类型
    db_type = Type(**type_data.dict())
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type

@router.get("/{type_name}", response_model=TypeSchema)
async def get_type(
    type_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定类型的详细信息
    """
    result = await db.execute(select(Type).where(Type.type_name == type_name))
    db_type = result.scalars().first()
    
    if not db_type:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 不存在")
    
    return db_type

@router.put("/{type_name}", response_model=TypeSchema)
async def update_type(
    type_name: str,
    type_data: TypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新配置类型
    """
    
    # 查找类型
    result = await db.execute(select(Type).where(Type.type_name == type_name))
    db_type = result.scalars().first()
    
    if not db_type:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 不存在")
    
    # 更新类型
    if type_data.description is not None:
        db_type.description = type_data.description
    
    await db.commit()
    await db.refresh(db_type)
    return db_type

@router.delete("/{type_name}", response_model=TypeSchema)
async def delete_type(
    type_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除配置类型
    """
    
    # 查询类型
    result = await db.execute(
        select(Type).where(Type.type_name == type_name)
    )
    type_obj = result.scalar_one_or_none()
    
    if not type_obj:
        raise HTTPException(status_code=404, detail=f"找不到类型: {type_name}")
    
    # 检查是否有关联的配置项
    configs_result = await db.execute(
        select(Config).where(Config.type_id == type_obj.type_id)
    )
    configs = configs_result.scalars().all()
    
    if configs:
        raise HTTPException(status_code=400, detail=f"类型 {type_name} 下有 {len(configs)} 个配置项，请先删除这些配置项")
    
    # 删除类型
    await db.delete(type_obj)
    await db.commit()
    
    return type_obj