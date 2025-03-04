from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from app.models.database import get_db
from app.models.config import Config
from app.models.type import Type
from app.schemas.config import ConfigCreate, ConfigUpdate, Config as ConfigSchema, ConfigList, ConfigSearch
from app.api.deps import is_privilege_mode
# 添加缺少的导入
from app import schemas

router = APIRouter()

@router.post("", response_model=ConfigSchema)
async def create_config(
    config_data: ConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的配置项
    """
    # 查找或创建类型
    result = await db.execute(select(Type).where(Type.type_name == config_data.type_name))
    db_type = result.scalars().first()
    
    if not db_type:
        # 如果类型不存在，创建新类型
        db_type = Type(type_name=config_data.type_name, description=f"自动创建的类型: {config_data.type_name}")
        db.add(db_type)
        await db.flush()  # 获取新创建类型的ID
    
    # 检查同一类型下是否已存在相同key的配置
    result = await db.execute(
        select(Config).where(
            and_(
                Config.type_id == db_type.type_id,
                Config.key == config_data.key
            )
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail=f"类型 '{config_data.type_name}' 下已存在键 '{config_data.key}'")
    
    # 创建新配置
    db_config = Config(
        type_id=db_type.type_id,
        key=config_data.key,
        value=config_data.value,
        key_description=config_data.key_description
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    
    # 构建返回结果
    result = ConfigSchema(
        config_id=db_config.config_id,
        type_id=db_config.type_id,
        key=db_config.key,
        value=db_config.value,
        key_description=db_config.key_description,
        created_at=db_config.created_at,
        updated_at=db_config.updated_at,
        type_name=db_type.type_name
    )
    
    return result

@router.get("", response_model=ConfigList)
async def get_configs(
    skip: int = 0,
    limit: int = 100,
    type_name: Optional[str] = None,
    key: Optional[str] = None,
    value: Optional[str] = None,
    exact_match: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    获取配置列表，支持按类型、键、值筛选
    """
    # 构建查询条件
    conditions = []
    
    if type_name:
        # 按类型名称筛选
        result = await db.execute(select(Type).where(Type.type_name == type_name))
        db_type = result.scalars().first()
        if not db_type:
            # 如果类型不存在，返回空列表
            return {"configs": [], "total": 0}
        conditions.append(Config.type_id == db_type.type_id)
    
    if key:
        # 按键筛选
        if exact_match:
            conditions.append(Config.key == key)
        else:
            conditions.append(Config.key.like(f"%{key}%"))
    
    if value:
        # 按值筛选
        if exact_match:
            conditions.append(Config.value == value)
        else:
            conditions.append(Config.value.like(f"%{value}%"))
    
    # 构建查询
    query = select(Config, Type.type_name).join(Type)
    if conditions:
        query = query.where(and_(*conditions))
    
    # 查询总数
    count_query = select(func.count()).select_from(Config).join(Type)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 查询配置列表
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    # 构建返回结果
    configs = []
    for row in rows:
        config, type_name = row
        configs.append(
            ConfigSchema(
                config_id=config.config_id,
                type_id=config.type_id,
                key=config.key,
                value=config.value,
                key_description=config.key_description,
                created_at=config.created_at,
                updated_at=config.updated_at,
                type_name=type_name
            )
        )
    
    return {"configs": configs, "total": total}

@router.get("/{config_id}", response_model=ConfigSchema)
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定配置项的详细信息
    """
    result = await db.execute(
        select(Config, Type.type_name)
        .join(Type)
        .where(Config.config_id == config_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    
    config, type_name = row
    return ConfigSchema(
        config_id=config.config_id,
        type_id=config.type_id,
        key=config.key,
        value=config.value,
        key_description=config.key_description,
        created_at=config.created_at,
        updated_at=config.updated_at,
        type_name=type_name
    )

@router.put("/{config_id}", response_model=ConfigSchema)
async def update_config(
    config_id: int,
    config_data: ConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新配置项
    """
    result = await db.execute(
        select(Config, Type.type_name)
        .join(Type)
        .where(Config.config_id == config_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    
    config, type_name = row
    
    # 更新配置
    if config_data.value is not None:
        config.value = config_data.value
    if config_data.key_description is not None:
        config.key_description = config_data.key_description
    
    await db.commit()
    await db.refresh(config)
    
    return ConfigSchema(
        config_id=config.config_id,
        type_id=config.type_id,
        key=config.key,
        value=config.value,
        key_description=config.key_description,
        created_at=config.created_at,
        updated_at=config.updated_at,
        type_name=type_name
    )

@router.delete("/{config_id}", response_model=dict)
async def delete_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除配置项（仅管理员）
    """
    result = await db.execute(select(Config).where(Config.config_id == config_id))
    config = result.scalars().first()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    
    await db.delete(config)
    await db.commit()
    
    return {"message": f"配置ID {config_id} 已成功删除"}

@router.post("/search", response_model=ConfigList)
async def search_configs(
    search_data: ConfigSearch,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    高级搜索配置项
    """
    # 构建查询条件
    conditions = []
    
    if search_data.type_name:
        # 按类型名称筛选
        result = await db.execute(select(Type).where(Type.type_name == search_data.type_name))
        db_type = result.scalars().first()
        if not db_type:
            # 如果类型不存在，返回空列表
            return {"configs": [], "total": 0}
        conditions.append(Config.type_id == db_type.type_id)
    
    if search_data.key:
        # 按键筛选
        if search_data.exact_match:
            conditions.append(Config.key == search_data.key)
        else:
            conditions.append(Config.key.like(f"%{search_data.key}%"))
    
    if search_data.value:
        # 按值筛选
        if search_data.exact_match:
            conditions.append(Config.value == search_data.value)
        else:
            conditions.append(Config.value.like(f"%{search_data.value}%"))
    
    # 构建查询
    query = select(Config, Type.type_name).join(Type)
    if conditions:
        query = query.where(and_(*conditions))
    
    # 查询总数
    count_query = select(func.count()).select_from(Config).join(Type)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    result = await db.execute(count_query)
    total = result.scalar()
    
    # 查询配置列表
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    # 构建返回结果
    configs = []
    for row in rows:
        config, type_name = row
        configs.append(
            ConfigSchema(
                config_id=config.config_id,
                type_id=config.type_id,
                key=config.key,
                value=config.value,
                key_description=config.key_description,
                created_at=config.created_at,
                updated_at=config.updated_at,
                type_name=type_name
            )
        )
    
    return {"configs": configs, "total": total}

@router.get("/type/{type_name}/key/{key}", response_model=ConfigSchema)
async def get_config_by_type_and_key(
    type_name: str,
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    通过类型名称和键获取配置
    """
    # 查找类型
    result = await db.execute(select(Type).where(Type.type_name == type_name))
    db_type = result.scalars().first()
    
    if not db_type:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 不存在")
    
    # 查找配置
    result = await db.execute(
        select(Config)
        .where(
            and_(
                Config.type_id == db_type.type_id,
                Config.key == key
            )
        )
    )
    config = result.scalars().first()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 下不存在键 '{key}'")
    
    return ConfigSchema(
        config_id=config.config_id,
        type_id=config.type_id,
        key=config.key,
        value=config.value,
        key_description=config.key_description,
        created_at=config.created_at,
        updated_at=config.updated_at,
        type_name=type_name
    )

@router.delete("/type/{type_name}/key/{key}", response_model=dict)
async def delete_config_by_type_and_key(
    type_name: str,
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    通过类型名称和键删除配置（仅管理员）
    """
    # 查找类型
    result = await db.execute(select(Type).where(Type.type_name == type_name))
    db_type = result.scalars().first()
    
    if not db_type:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 不存在")
    
    # 查找配置
    result = await db.execute(
        select(Config)
        .where(
            and_(
                Config.type_id == db_type.type_id,
                Config.key == key
            )
        )
    )
    config = result.scalars().first()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"类型 '{type_name}' 下不存在键 '{key}'")
    
# 修改删除配置项的端点s
@router.delete("/{type_name}/{key}", response_model=dict)
async def delete_config(
        type_name: str,
        key: str,
        db: AsyncSession = Depends(get_db)
    ):
        """
        删除配置项
        """
        
        # 查询配置项
        result = await db.execute(
            select(Config).join(Type).where(
                Type.type_name == type_name,
                Config.key == key
            )
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail=f"找不到配置项: {type_name}.{key}")
        
        # 删除配置项
        await db.delete(config)
        await db.commit()
        
        # return config1212
        
        return {"message": "配置项已删除"}