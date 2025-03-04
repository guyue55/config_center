from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.models.database import get_db
from app.models.type import Type
from app.models.config import Config

# 将 router 改名为 page_router
page_router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@page_router.get("/", response_class=HTMLResponse)
async def index_page(request: Request, db: AsyncSession = Depends(get_db)):
    """首页"""
    # 查询类型数量
    result = await db.execute(select(func.count()).select_from(Type))
    type_count = result.scalar()
    
    # 查询配置项数量
    result = await db.execute(select(func.count()).select_from(Config))
    config_count = result.scalar()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "types_count": type_count,
            "configs_count": config_count
        }
    )



@page_router.get("/types", response_class=HTMLResponse)
async def types_page(
    request: Request, 
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """配置类型页面"""
    query = select(Type)
    if search:
        query = query.where(Type.type_name.contains(search) | Type.description.contains(search))
    
    result = await db.execute(query)
    types = result.scalars().all()
    
    return templates.TemplateResponse(
        "types.html", 
        {
            "request": request, 
            "types": types,
            "search": search
        }
    )

@page_router.get("/configs", response_class=HTMLResponse)
async def configs_page(
    request: Request,
    type_name: Optional[str] = None,
    key: Optional[str] = None,
    value: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """配置项页面"""
    # 构建查询
    query = select(Config, Type).join(Type)
    
    # 添加筛选条件
    if type_name:
        query = query.where(Type.type_name.contains(type_name))
    if key:
        query = query.where(Config.key.contains(key))
    if value:
        query = query.where(Config.value.contains(value))
    
    # 执行查询
    result = await db.execute(query)
    rows = result.all()
    
    # 处理查询结果，构建包含类型信息的配置数据
    configs = [{
        "config_id": row[0].config_id,
        "key": row[0].key,
        "value": row[0].value,
        "key_description": row[0].key_description,
        "created_at": row[0].created_at,
        "updated_at": row[0].updated_at,
        "type": {
            "type_name": row[1].type_name
        }
    } for row in rows]
    
    # 获取所有类型
    types_result = await db.execute(select(Type))
    types = types_result.scalars().all()
    
    return templates.TemplateResponse(
        "configs.html", 
        {
            "request": request, 
            "configs": configs,
            "types": types,
            "current_type": type_name
        }
    )