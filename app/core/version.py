"""版本管理模块"""

import tomli
from pathlib import Path

# 读取pyproject.toml中的版本号
def _read_version_from_toml():
    try:
        project_root = Path(__file__).parent.parent.parent
        toml_path = project_root / "pyproject.toml"
        with open(toml_path, "rb") as f:
            data = tomli.load(f)
            return data["project"]["version"]
    except Exception:
        return "0.0.0"  # 默认版本号

# 项目版本号，采用语义化版本格式 (https://semver.org/)
VERSION = _read_version_from_toml()

# 解析版本号组件
try:
    MAJOR, MINOR, PATCH = map(int, VERSION.split("."))
except ValueError:
    MAJOR = MINOR = PATCH = 0

def get_version():
    """获取完整的版本号"""
    return VERSION