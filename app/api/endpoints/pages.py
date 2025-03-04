from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import get_db
from app.models.type import Type
from app.models.config import Config
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parents[2] / "templates"))

# 修改根路径处理函数
@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
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
            "type_count": type_count,
            "config_count": config_count
        }
    )

@router.get("/types", response_class=HTMLResponse)
async def types_page(
    request: Request,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """配置类型页面"""
    # 构建查询
    query = select(Type)
    if search:
        query = query.where(Type.type_name.contains(search) | Type.description.contains(search))
    
    # 执行查询
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

@router.get("/configs", response_class=HTMLResponse)
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
    
    # 查询所有类型（用于筛选）
    types_result = await db.execute(select(Type))
    types = types_result.scalars().all()
    
    return templates.TemplateResponse(
        "configs.html",
        {
            "request": request,
            "configs": rows,
            "types": types,
            "type_name": type_name,
            "key": key,
            "value": value
        }
    )