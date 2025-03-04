import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, inspect
from app.core.config import settings
from app.models.base import Base
from app.models.type import Type

# SQLite异步URL需要使用aiosqlite
DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """初始化数据库，创建所有表"""
    try:
        # 检查表是否存在
        async with engine.connect() as conn:
            # 检查types表是否存在
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='types'"))
            table_exists = result.scalar() is not None
            
            if not table_exists:
                # 如果表不存在，创建所有表
                async with engine.begin() as conn2:
                    await conn2.run_sync(Base.metadata.create_all)
                
                # 创建默认数据
                async with AsyncSessionLocal() as session:
                    # 创建默认配置类型
                    default_type = Type(
                        type_name="default",
                        description="默认配置类型"
                    )
                    session.add(default_type)
                    await session.commit()
                    
                    logging.info("数据库初始化成功，创建了默认配置类型")
            else:
                logging.info("数据库表已存在，跳过初始化")
            
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        raise

async def get_db():
    """获取数据库会话"""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()