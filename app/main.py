from fastapi import FastAPI, Request  # 添加 Request 导入
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import uvicorn
import logging
from pathlib import Path
from app.api.api import api_router
from app.api.pages import page_router
from app.core.config import settings
from app.models.database import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# 设置模板目录
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
print("*"*100)
print("templates:", templates)
print(str(Path(__file__).parent / "templates"))

app = FastAPI(
    title=settings.APP_NAME,
    description="配置中心API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# 设置模板目录
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# 注册API路由
app.include_router(api_router, prefix="/api")

# 注册页面路由
app.include_router(page_router, prefix="/page")

# 根路径重定向到首页
@app.get("/")
async def root():
    # 将根路径重定向到页面路由的首页
    return RedirectResponse(url="/page/")

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("数据库初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭中...")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)