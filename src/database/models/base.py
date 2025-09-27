"""
基础数据模型类

提供所有数据模型的公共字段和方法
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    基础模型类，所有数据模型都应继承此类
    
    提供公共字段：
    - id: 主键ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    
    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        server_default=func.now()
    )
    
    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now()
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典
        
        Returns:
            包含所有字段的字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理datetime类型，转换为ISO格式字符串
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        从字典创建模型实例
        
        Args:
            data: 包含字段数据的字典
            
        Returns:
            模型实例
        """
        # 过滤出存在于模型中的字段
        filtered_data = {}
        for column in cls.__table__.columns:
            if column.name in data:
                filtered_data[column.name] = data[column.name]
        
        return cls(**filtered_data)
    
    def __repr__(self) -> str:
        """
        返回模型的字符串表示
        """
        return f"<{self.__class__.__name__}(id={self.id})>"