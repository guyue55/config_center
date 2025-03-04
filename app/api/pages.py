from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.type import Type
from app.models.config import Config

# 将 router 改名为 page_router
page_router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@page_router.get("/")
async def index_page(request: Request, db: AsyncSession = Depends(get_db)):
    """首页"""
    # 查询类型数量
    result = await db.execute(select(func.count()).select_from(Type))
    types_count = result.scalar()
    
    # 查询配置项数量
    result = await db.execute(select(func.count()).select_from(Config))
    configs_count = result.scalar()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request,
            "types_count": types_count,
            "configs_count": configs_count
        }
    )



@page_router.get("/types")
async def types_page(
    request: Request, 
    search: str = None,
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
            "types": types
        }
    )

@page_router.get("/configs")
async def configs_page(
    request: Request,
    type_name: str = None,
    search: str = None,
    db: AsyncSession = Depends(get_db)
):
    """配置项页面"""
    # 获取所有类型
    types_result = await db.execute(select(Type))
    types = types_result.scalars().all()
    
    # 构建查询
    query = select(Config).join(Type)
    
    if type_name:
        query = query.where(Type.type_name == type_name)
    
    if search:
        query = query.where(Config.key.contains(search) | Config.value.contains(search) | Config.key_description.contains(search))
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    return templates.TemplateResponse(
        "configs.html", 
        {
            "request": request, 
            "configs": configs, 
            "types": types,
            "current_type": type_name
        }
    )