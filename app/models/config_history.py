from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.database import Base

class ConfigHistory(Base):
    __tablename__ = "config_history"
    
    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_id = Column(Integer, ForeignKey("configs.config_id"), nullable=False)
    type_id = Column(Integer, ForeignKey("types.type_id"), nullable=False)
    key = Column(String, nullable=False)
    old_value = Column(String, nullable=False)
    new_value = Column(String, nullable=False)
    operator = Column(String, nullable=True)  # 操作人
    operation_type = Column(String, nullable=False)  # 操作类型：create/update/delete
    created_at = Column(DateTime, default=func.now())
    
    # 关联配置
    config = relationship("Config")
    # 关联类型
    type = relationship("Type")
    
    def __repr__(self):
        return f"<ConfigHistory(history_id={self.history_id}, config_id={self.config_id}, operation_type='{self.operation_type}')>"