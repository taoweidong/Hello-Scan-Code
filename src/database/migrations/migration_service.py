"""
数据库迁移服务

提供数据库结构版本控制和数据迁移功能
"""

import os
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime
from sqlalchemy import Engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from ..models.base import BaseModel
from src.config import get_logger

logger = get_logger()


class MigrationService:
    """
    数据库迁移服务
    
    提供数据库版本管理、结构升级和数据迁移功能
    """
    
    VERSION_TABLE = 'migration_versions'
    CURRENT_VERSION = '1.2.0'
    
    def __init__(self, engine: Engine):
        """
        初始化迁移服务
        
        Args:
            engine: 数据库引擎
        """
        self.engine = engine
        self.migrations: Dict[str, Callable] = {}
        self._register_migrations()
    
    def _register_migrations(self):
        """
        注册所有迁移脚本
        """
        self.migrations = {
            '1.0.0': self._migrate_to_1_0_0,
            '1.1.0': self._migrate_to_1_1_0,
            '1.2.0': self._migrate_to_1_2_0,
        }
    
    def _create_version_table(self):
        """
        创建版本记录表
        """
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.VERSION_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """))
            conn.commit()
    
    def _get_current_db_version(self) -> Optional[str]:
        """
        获取当前数据库版本
        
        Returns:
            当前版本号或None
        """
        try:
            with self.engine.connect() as conn:
                # 检查版本表是否存在
                inspector = inspect(self.engine)
                if self.VERSION_TABLE not in inspector.get_table_names():
                    return None
                
                # 获取最新版本
                result = conn.execute(text(f"""
                    SELECT version FROM {self.VERSION_TABLE} 
                    ORDER BY applied_at DESC LIMIT 1
                """))
                row = result.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.warning(f"获取数据库版本失败: {e}")
            return None
    
    def _set_db_version(self, version: str, description: str = ""):
        """
        设置数据库版本
        
        Args:
            version: 版本号
            description: 版本描述
        """
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                INSERT OR REPLACE INTO {self.VERSION_TABLE} 
                (version, applied_at, description) 
                VALUES (:version, CURRENT_TIMESTAMP, :description)
            """), {'version': version, 'description': description})
            conn.commit()
    
    def _table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            表是否存在
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def _column_exists(self, table_name: str, column_name: str) -> bool:
        """
        检查列是否存在
        
        Args:
            table_name: 表名
            column_name: 列名
            
        Returns:
            列是否存在
        """
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
        except Exception:
            return False
    
    def _migrate_to_1_0_0(self):
        """
        迁移到版本1.0.0 - 初始版本
        """
        logger.info("执行迁移到版本1.0.0 - 创建初始表结构")
        
        # 检查是否存在旧的search_results表
        if self._table_exists('search_results'):
            # 如果存在旧表，需要进行数据迁移
            self._migrate_old_table_structure()
        else:
            # 创建新的表结构
            BaseModel.metadata.create_all(self.engine)
        
        self._set_db_version('1.0.0', '初始表结构创建')
    
    def _migrate_to_1_1_0(self):
        """
        迁移到版本1.1.0 - 添加file_size字段
        """
        logger.info("执行迁移到版本1.1.0 - 添加file_size字段")
        
        if not self._column_exists('search_results', 'file_size'):
            with self.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE search_results 
                    ADD COLUMN file_size INTEGER
                """))
                conn.commit()
        
        self._set_db_version('1.1.0', '添加file_size字段')
    
    def _migrate_to_1_2_0(self):
        """
        迁移到版本1.2.0 - 添加编码和位置字段
        """
        logger.info("执行迁移到版本1.2.0 - 添加编码和位置字段")
        
        with self.engine.connect() as conn:
            # 添加encoding字段
            if not self._column_exists('search_results', 'encoding'):
                conn.execute(text("""
                    ALTER TABLE search_results 
                    ADD COLUMN encoding VARCHAR(20)
                """))
            
            # 添加match_position字段
            if not self._column_exists('search_results', 'match_position'):
                conn.execute(text("""
                    ALTER TABLE search_results 
                    ADD COLUMN match_position INTEGER
                """))
            
            # 添加时间戳字段
            if not self._column_exists('search_results', 'created_at'):
                conn.execute(text("""
                    ALTER TABLE search_results 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
            
            if not self._column_exists('search_results', 'updated_at'):
                conn.execute(text("""
                    ALTER TABLE search_results 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
            
            # 创建新的索引
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_file_path_search_term 
                    ON search_results(file_path, search_term)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON search_results(created_at)
                """))
            except SQLAlchemyError as e:
                logger.warning(f"创建索引时出现警告: {e}")
            
            conn.commit()
        
        self._set_db_version('1.2.0', '添加编码、位置字段和时间戳')
    
    def _migrate_old_table_structure(self):
        """
        迁移旧的表结构
        """
        logger.info("迁移旧的表结构数据")
        
        try:
            with self.engine.connect() as conn:
                # 检查旧表结构
                inspector = inspect(self.engine)
                old_columns = {col['name'] for col in inspector.get_columns('search_results')}
                
                # 如果旧表缺少必要的字段，先添加
                required_columns = {
                    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
                
                for col_name, col_def in required_columns.items():
                    if col_name not in old_columns:
                        conn.execute(text(f"""
                            ALTER TABLE search_results 
                            ADD COLUMN {col_name} {col_def}
                        """))
                
                conn.commit()
                logger.info("旧表结构迁移完成")
                
        except Exception as e:
            logger.error(f"迁移旧表结构失败: {e}")
            raise
    
    def _backup_database(self) -> str:
        """
        备份数据库
        
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.engine.url.database}_backup_{timestamp}"
        
        try:
            # 对于SQLite，直接复制文件
            if str(self.engine.url).startswith('sqlite'):
                import shutil
                db_path = self.engine.url.database
                if db_path and db_path != ':memory:':
                    shutil.copy2(db_path, backup_path)
                    logger.info(f"数据库备份完成: {backup_path}")
                    return backup_path
            
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            raise
        
        return ""
    
    def migrate(self) -> bool:
        """
        执行数据库迁移
        
        Returns:
            迁移是否成功
        """
        try:
            # 创建版本表
            self._create_version_table()
            
            # 获取当前数据库版本
            current_version = self._get_current_db_version()
            
            if current_version == self.CURRENT_VERSION:
                logger.info(f"数据库已是最新版本: {current_version}")
                return True
            
            # 备份数据库
            backup_path = self._backup_database()
            
            # 确定需要执行的迁移
            versions_to_migrate = self._get_migration_path(current_version)
            
            if not versions_to_migrate:
                logger.info("无需执行迁移")
                return True
            
            # 执行迁移
            for version in versions_to_migrate:
                logger.info(f"正在迁移到版本: {version}")
                
                try:
                    if version in self.migrations:
                        self.migrations[version]()
                        logger.info(f"版本 {version} 迁移完成")
                    else:
                        logger.warning(f"未找到版本 {version} 的迁移脚本")
                
                except Exception as e:
                    logger.error(f"版本 {version} 迁移失败: {e}")
                    # 可以在这里实现回滚逻辑
                    raise
            
            logger.info(f"数据库迁移完成，当前版本: {self.CURRENT_VERSION}")
            return True
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            return False
    
    def _get_migration_path(self, current_version: Optional[str]) -> List[str]:
        """
        获取迁移路径
        
        Args:
            current_version: 当前版本
            
        Returns:
            需要执行的迁移版本列表
        """
        all_versions = ['1.0.0', '1.1.0', '1.2.0']
        
        if current_version is None:
            # 全新安装
            return ['1.0.0', '1.1.0', '1.2.0']
        
        try:
            current_index = all_versions.index(current_version)
            return all_versions[current_index + 1:]
        except ValueError:
            # 未知版本，执行所有迁移
            logger.warning(f"未知的数据库版本: {current_version}")
            return all_versions
    
    def get_migration_info(self) -> Dict[str, any]:
        """
        获取迁移信息
        
        Returns:
            迁移信息字典
        """
        current_version = self._get_current_db_version()
        pending_migrations = self._get_migration_path(current_version)
        
        return {
            'current_version': current_version,
            'target_version': self.CURRENT_VERSION,
            'pending_migrations': pending_migrations,
            'migration_needed': len(pending_migrations) > 0
        }