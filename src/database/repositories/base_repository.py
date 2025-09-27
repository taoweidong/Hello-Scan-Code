"""
基础仓库抽象类

定义数据访问层的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.base import BaseModel

# 定义泛型类型
ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseRepository(Generic[ModelType], ABC):
    """
    基础仓库抽象类
    
    定义了数据访问层的通用接口，所有具体仓库都应继承此类
    """
    
    def __init__(self, model_class: Type[ModelType]):
        """
        初始化基础仓库
        
        Args:
            model_class: 关联的模型类
        """
        self.model_class = model_class
    
    def create(self, session: Session, **kwargs) -> ModelType:
        """
        创建新记录
        
        Args:
            session: 数据库会话
            **kwargs: 模型字段参数
            
        Returns:
            创建的模型实例
        """
        instance = self.model_class(**kwargs)
        session.add(instance)
        session.flush()  # 获取ID但不提交事务
        return instance
    
    def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        """
        根据ID获取记录
        
        Args:
            session: 数据库会话
            id: 记录ID
            
        Returns:
            模型实例或None
        """
        return session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self, session: Session, 
                offset: int = 0, 
                limit: Optional[int] = None) -> List[ModelType]:
        """
        获取所有记录
        
        Args:
            session: 数据库会话
            offset: 偏移量
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        query = session.query(self.model_class)
        
        if offset > 0:
            query = query.offset(offset)
        
        if limit is not None:
            query = query.limit(limit)
        
        return query.all()
    
    def update(self, session: Session, id: int, **kwargs) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            session: 数据库会话
            id: 记录ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的模型实例或None
        """
        instance = self.get_by_id(session, id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            session.flush()
        return instance
    
    def delete(self, session: Session, id: int) -> bool:
        """
        删除记录
        
        Args:
            session: 数据库会话
            id: 记录ID
            
        Returns:
            删除是否成功
        """
        instance = self.get_by_id(session, id)
        if instance:
            session.delete(instance)
            session.flush()
            return True
        return False
    
    def count(self, session: Session) -> int:
        """
        获取记录总数
        
        Args:
            session: 数据库会话
            
        Returns:
            记录总数
        """
        return session.query(func.count(self.model_class.id)).scalar()
    
    def exists(self, session: Session, id: int) -> bool:
        """
        检查记录是否存在
        
        Args:
            session: 数据库会话
            id: 记录ID
            
        Returns:
            记录是否存在
        """
        return session.query(
            session.query(self.model_class).filter(
                self.model_class.id == id
            ).exists()
        ).scalar()
    
    def bulk_create(self, session: Session, instances: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            session: 数据库会话
            instances: 实例数据列表
            
        Returns:
            创建的模型实例列表
        """
        model_instances = [self.model_class(**data) for data in instances]
        session.add_all(model_instances)
        session.flush()
        return model_instances
    
    def bulk_update(self, session: Session, updates: List[Dict[str, Any]]) -> int:
        """
        批量更新记录
        
        Args:
            session: 数据库会话
            updates: 更新数据列表，每个字典必须包含'id'字段
            
        Returns:
            更新的记录数量
        """
        if not updates:
            return 0
        
        # 使用bulk_update_mappings进行批量更新
        session.bulk_update_mappings(self.model_class, updates)
        return len(updates)
    
    def bulk_delete(self, session: Session, ids: List[int]) -> int:
        """
        批量删除记录
        
        Args:
            session: 数据库会话
            ids: 要删除的记录ID列表
            
        Returns:
            删除的记录数量
        """
        if not ids:
            return 0
        
        deleted_count = session.query(self.model_class).filter(
            self.model_class.id.in_(ids)
        ).delete(synchronize_session=False)
        
        return deleted_count
    
    @abstractmethod
    def get_by_criteria(self, session: Session, **criteria) -> List[ModelType]:
        """
        根据条件查询记录（抽象方法，子类必须实现）
        
        Args:
            session: 数据库会话
            **criteria: 查询条件
            
        Returns:
            匹配的模型实例列表
        """
        pass