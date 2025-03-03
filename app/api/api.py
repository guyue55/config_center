from fastapi import APIRouter
from app.api.endpoints import types, configs, users, auth, pages

api_router = APIRouter()

# 添加页面路由，不带前缀
api_router.include_router(pages.router, tags=["pages"])

# API路由，不带前缀（因为前缀在main.py中添加）
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(types.router, prefix="/types", tags=["types"])
api_router.include_router(configs.router, prefix="/configs", tags=["configs"])
api_router.include_router(users.router, prefix="/users", tags=["users"])