from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import get_db
from app.api.deps import get_current_user_optional  # 修改这里，导入正确的函数
from app.models.user import User
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
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
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
            "current_user": current_user,
            "types": types,
            "search": search
        }
    )

@router.get("/configs", response_class=HTMLResponse)
async def configs_page(
    request: Request,
    type_name: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """配置项页面"""
    # 获取所有类型
    types_result = await db.execute(select(Type))
    types = types_result.scalars().all()
    
    # 构建查询
    query = select(Config)
    if type_name:
        # 获取类型ID
        type_result = await db.execute(select(Type).where(Type.type_name == type_name))
        selected_type = type_result.scalar_one_or_none()
        if selected_type:
            query = query.where(Config.type_id == selected_type.type_id)
    
    if search:
        query = query.where(Config.key.contains(search) | Config.value.contains(search) | Config.key_description.contains(search))
    
    # 执行查询
    result = await db.execute(query)
    configs = result.scalars().all()
    
    # 获取每个配置的类型信息
    for config in configs:
        if not hasattr(config, 'type') or config.type is None:
            type_result = await db.execute(select(Type).where(Type.type_id == config.type_id))
            config.type = type_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "configs.html",
        {
            "request": request,
            "current_user": current_user,
            "configs": configs,
            "types": types,
            "selected_type": selected_type if type_name else None,
            "search": search
        }
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """登录页面"""
    if current_user:
        # 如果用户已登录，重定向到首页
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )