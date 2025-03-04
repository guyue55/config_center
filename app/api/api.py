from fastapi import APIRouter
from app.api.endpoints import types, configs

api_router = APIRouter()

# 页面路由已移至 app.api.pages.py

# API路由，不带前缀（因为前缀在main.py中添加）
api_router.include_router(types.router, prefix="/types", tags=["types"])
api_router.include_router(configs.router, prefix="/configs", tags=["configs"])