"""
数据库会话管理器

提供数据库会话的创建、管理和生命周期控制
"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from .config import DatabaseConfig, EngineFactory
from .models import BaseModel
from src.config import get_logger

logger = get_logger()


class SessionManager:
    """
    数据库会话管理器
    
    负责管理数据库连接和会话的生命周期，提供事务管理和错误处理
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化会话管理器
        
        Args:
            config: 数据库配置实例
        """
        self.config = config
        self.engine: Engine = EngineFactory.create_engine(config)
        
        # 创建会话工厂
        session_kwargs = config.get_session_kwargs()
        self._session_factory = sessionmaker(
            bind=self.engine,
            **session_kwargs
        )
        
        # 创建线程安全的会话
        self._scoped_session = scoped_session(self._session_factory)
        
        # 初始化数据库表结构
        self._init_database()
        
        logger.info("SessionManager初始化完成")
    
    def _init_database(self) -> None:
        """
        初始化数据库表结构
        """
        try:
            # 创建所有表
            BaseModel.metadata.create_all(self.engine)
            logger.info("数据库表结构初始化完成")
        except Exception as e:
            logger.error(f"数据库表结构初始化失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            数据库会话实例
        """
        return self._scoped_session()
    
    def close_session(self) -> None:
        """
        关闭当前线程的会话
        """
        try:
            self._scoped_session.remove()
        except Exception as e:
            logger.warning(f"关闭会话时出现警告: {e}")
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        会话上下文管理器，自动处理事务和会话关闭
        
        使用示例:
            with session_manager.session_scope() as session:
                # 数据库操作
                pass
        
        Yields:
            数据库会话实例
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败，已回滚事务: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def transaction_scope(self) -> Generator[Session, None, None]:
        """
        事务上下文管理器，提供更严格的事务控制
        
        与session_scope的区别是会显式开始事务
        
        Yields:
            数据库会话实例
        """
        session = self.get_session()
        transaction = session.begin()
        try:
            yield session
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            logger.error(f"事务执行失败，已回滚: {e}")
            raise
        finally:
            session.close()
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """
        在事务中执行函数
        
        Args:
            func: 要执行的函数，第一个参数必须是session
            *args: 函数的其他参数
            **kwargs: 函数的关键字参数
            
        Returns:
            函数的返回值
        """
        with self.session_scope() as session:
            return func(session, *args, **kwargs)
    
    def health_check(self) -> bool:
        """
        检查数据库连接健康状态
        
        Returns:
            连接是否正常
        """
        try:
            with self.session_scope() as session:
                # 执行简单查询测试连接
                session.execute("SELECT 1")
                return True
        except SQLAlchemyError as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    def get_engine_info(self) -> dict:
        """
        获取数据库引擎信息
        
        Returns:
            引擎信息字典
        """
        return {
            'url': str(self.engine.url),
            'driver': self.engine.driver,
            'pool_size': getattr(self.engine.pool, 'size', None),
            'checked_out': getattr(self.engine.pool, 'checkedout', None),
            'overflow': getattr(self.engine.pool, 'overflow', None),
        }
    
    def close(self) -> None:
        """
        关闭会话管理器，释放所有资源
        """
        try:
            # 移除所有scoped session
            self._scoped_session.remove()
            
            # 关闭引擎
            self.engine.dispose()
            
            logger.info("SessionManager已关闭")
        except Exception as e:
            logger.error(f"关闭SessionManager时出错: {e}")
    
    def __enter__(self):
        """
        支持with语句的上下文管理器
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时自动关闭
        """
        self.close()
    
    def __del__(self):
        """
        析构函数，确保资源正确释放
        """
        try:
            self.close()
        except:
            pass  # 避免析构时的异常