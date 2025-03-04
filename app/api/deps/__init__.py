from app.core.config import settings

def is_privilege_mode():
    """检查是否处于特权模式"""
    return settings.PRIVILEGE_MODE