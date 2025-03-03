from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from datetime import timedelta
from pathlib import Path

from app.models.database import get_db
from app.models.user import User
from app.api.deps import create_access_token, is_privilege_mode

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "templates"))

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    获取访问令牌
    """
    # 打印接收到的用户名，用于调试
    print(f"接收到的用户名: {form_data.username}")
    
    # 检查特权模式
    if await is_privilege_mode(db):
        # 特权模式下，返回管理员用户的令牌
        result = await db.execute(select(User).where(User.role == "admin").limit(1))
        admin_user = result.scalar_one_or_none()
        if admin_user:
            # 创建访问令牌
            access_token_expires = timedelta(minutes=60 * 24)  # 24小时
            access_token = create_access_token(
                data={"sub": admin_user.username}, expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "username": admin_user.username,
                "role": admin_user.role
            }
    
    # 查询用户
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    is_password_correct = bcrypt.checkpw(
        form_data.password.encode(), 
        user.hashed_password.encode()
    )
    
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=60 * 24)  # 24小时
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

# 添加一个直接接收表单数据的端点，以防OAuth2PasswordRequestForm不工作
@router.post("/login")
async def login_direct(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    直接接收表单数据的登录端点
    """
    # 查询用户
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    is_password_correct = bcrypt.checkpw(
        password.encode(), 
        user.hashed_password.encode()
    )
    
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=60 * 24)  # 24小时
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }
# 添加一个简单的登录处理函数
@router.post("/form-login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """处理表单登录"""
    try:
        # 查询用户
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "用户名或密码错误"}
            )
        
        # 验证密码
        is_password_correct = bcrypt.checkpw(
            password.encode(), 
            user.hashed_password.encode()
        )
        
        if not is_password_correct:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "用户名或密码错误"}
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=60 * 24)  # 24小时
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # 设置cookie
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=60 * 60 * 24,  # 24小时
            samesite="lax"
        )
        
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"登录失败: {str(e)}"}
        )
# 添加检查特权模式的端点
@router.get("/privilege-mode")
async def check_privilege_mode(db: AsyncSession = Depends(get_db)):
    """检查是否启用了特权模式"""
    privilege_mode = await is_privilege_mode(db)
    return {"privilege_mode": privilege_mode}