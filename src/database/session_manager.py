"""
数据库会话管理器
"""
from typing import Optional
from contextlib import contextmanager
import sqlite3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseSessionManager:
    """数据库会话管理器"""
    
    def __init__(self, db_path: str = "db/scan_results.db"):
        self.db_path = db_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_session(self):
        """获取数据库会话"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """执行查询"""
        with self.get_session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    
    def execute_non_query(self, query: str, params: tuple = ()):
        """执行非查询语句"""
        with self.get_session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount