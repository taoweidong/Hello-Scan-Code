"""
应用配置管理

管理应用核心配置，包括搜索参数、路径配置等
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from .base_config import BaseConfig


@dataclass
class AppConfig(BaseConfig):
    """应用配置类"""
    
    # 搜索相关配置
    repo_path: str = "/root/CodeRootPath"
    search_term: str = "test,def,void"
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    
    # 输出路径配置
    db_path: str = "db/results.db"
    excel_path: str = "report/results.xlsx"
    
    # 搜索过滤配置
    ignore_dirs: List[str] = field(default_factory=lambda: [
        ".git", "__pycache__", ".svn", ".hg", ".idea", 
        ".vscode", "node_modules", ".tox"
    ])
    file_extensions: Optional[List[str]] = None
    
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        self.repo_path = self.get_env_var('REPO_PATH', self.repo_path)
        self.search_term = self.get_env_var('SEARCH_TERM', self.search_term)
        self.is_regex = self.get_env_var('IS_REGEX', self.is_regex, bool)
        self.validate = self.get_env_var('VALIDATE', self.validate, bool)
        self.validate_workers = self.get_env_var('VALIDATE_WORKERS', self.validate_workers, int)
        self.db_path = self.get_env_var('DB_PATH', self.db_path)
        self.excel_path = self.get_env_var('EXCEL_PATH', self.excel_path)
        
        # 处理列表类型的环境变量
        ignore_dirs_env = self.get_env_var('IGNORE_DIRS', None)
        if ignore_dirs_env:
            self.ignore_dirs = ignore_dirs_env.split(',')
            
        file_extensions_env = self.get_env_var('FILE_EXTENSIONS', None)
        if file_extensions_env:
            self.file_extensions = file_extensions_env.split(',')
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        # 检查必要的路径
        if not self.repo_path or not os.path.exists(self.repo_path):
            return False
            
        # 检查搜索词
        if not self.search_term:
            return False
            
        # 检查工作线程数
        if self.validate_workers <= 0:
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


def parse_args() -> AppConfig:
    """
    创建配置对象，使用默认值并支持环境变量覆盖
    保持向后兼容性
    """
    config = AppConfig()
    config.load_from_env()
    config.ensure_output_dirs()
    return config


# 向后兼容性别名
SearchConfig = AppConfig