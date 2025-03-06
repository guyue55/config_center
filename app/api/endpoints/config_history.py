from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.config import Config
from app.models.config_history import ConfigHistory
from app.schemas.config import ConfigCreate, ConfigUpdate

router = APIRouter()

@router.get("/config/{config_id}/history", response_model=List[dict])
def get_config_history(config_id: int, db: Session = Depends(get_db)):
    """获取配置的修改历史"""
    history = db.query(ConfigHistory).filter(ConfigHistory.config_id == config_id).order_by(ConfigHistory.created_at.desc()).all()
    return [{
        "history_id": h.history_id,
        "config_id": h.config_id,
        "type_id": h.type_id,
        "key": h.key,
        "old_value": h.old_value,
        "new_value": h.new_value,
        "operator": h.operator,
        "operation_type": h.operation_type,
        "created_at": h.created_at
    } for h in history]

@router.post("/config/{config_id}/rollback/{history_id}")
def rollback_config(config_id: int, history_id: int, db: Session = Depends(get_db)):
    """回滚配置到指定的历史版本"""
    # 获取历史记录
    history = db.query(ConfigHistory).filter(ConfigHistory.history_id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    # 获取当前配置
    config = db.query(Config).filter(Config.config_id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    # 创建新的历史记录
    new_history = ConfigHistory(
        config_id=config_id,
        type_id=config.type_id,
        key=config.key,
        old_value=config.value,
        new_value=history.old_value,  # 回滚到历史版本的值
        operator="system",
        operation_type="rollback"
    )
    
    # 更新配置值
    config.value = history.old_value
    
    # 保存更改
    db.add(new_history)
    db.commit()
    
    return {"message": "Config rolled back successfully"}