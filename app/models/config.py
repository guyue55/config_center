from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.database import Base

class Config(Base):
    __tablename__ = "configs"
    
    config_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey("types.type_id"), nullable=False)
    key = Column(String, index=True, nullable=False)
    value = Column(String, nullable=False)
    key_description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联类型
    type = relationship("Type", back_populates="configs")
    
    # 确保同一类型下的key唯一
    __table_args__ = (
        UniqueConstraint('type_id', 'key', name='uix_type_key'),
    )
    
    def __repr__(self):
        return f"<Config(config_id={self.config_id}, key='{self.key}', value='{self.value}')>"