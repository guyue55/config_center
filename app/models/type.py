from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.models.database import Base

class Type(Base):
    __tablename__ = "types"
    
    type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # 关联配置项
    configs = relationship("Config", back_populates="type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Type(type_id={self.type_id}, type_name='{self.type_name}')>"