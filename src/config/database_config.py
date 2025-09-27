"""
数据库配置管理

管理数据库相关的配置参数
"""

import os
from dataclasses import dataclass
from .base_config import BaseConfig


@dataclass  
class DatabaseConfig(BaseConfig):
    """数据库配置类"""
    
    # 数据库文件路径
    db_path: str = "db/results.db"
    
    # Excel导出路径
    excel_path: str = "report/results.xlsx"
    
    # 连接池配置
    connection_pool_size: int = 5
    connection_timeout: int = 30
    
    # 批量操作配置
    batch_size: int = 1000
    
    # 数据库引擎配置
    echo_sql: bool = False
    
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        self.db_path = self.get_env_var('DB_PATH', self.db_path)
        self.excel_path = self.get_env_var('EXCEL_PATH', self.excel_path)
        self.connection_pool_size = self.get_env_var('DB_POOL_SIZE', self.connection_pool_size, int)
        self.connection_timeout = self.get_env_var('DB_TIMEOUT', self.connection_timeout, int)
        self.batch_size = self.get_env_var('DB_BATCH_SIZE', self.batch_size, int)
        self.echo_sql = self.get_env_var('DB_ECHO_SQL', self.echo_sql, bool)
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        # 检查路径是否有效
        if not self.db_path:
            return False
            
        # 检查连接池大小
        if self.connection_pool_size <= 0:
            return False
            
        # 检查超时时间
        if self.connection_timeout <= 0:
            return False
            
        # 检查批量大小
        if self.batch_size <= 0:
            return False
            
        return True
    
    def ensure_output_dirs(self) -> None:
        """确保输出目录存在"""
        db_dir = os.path.dirname(self.db_path) or "."
        excel_dir = os.path.dirname(self.excel_path) or "."
        
        if db_dir != ".":
            os.makedirs(db_dir, exist_ok=True)
        if excel_dir != ".":
            os.makedirs(excel_dir, exist_ok=True)
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return f"sqlite:///{self.db_path}"