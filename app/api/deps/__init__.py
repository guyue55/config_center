# 从模块中导出所需的函数和类
from app.api.deps.auth import (
    create_access_token,
    get_current_user,
    get_current_user_optional,
    get_current_active_user,
    get_current_admin_user,
    is_privilege_mode
)

# 确保这些函数可以直接从 app.api.deps 导入
__all__ = [
    "create_access_token",
    "get_current_user",
    "get_current_user_optional",
    "get_current_active_user",
    "get_current_admin_user",
    "is_privilege_mode"
]