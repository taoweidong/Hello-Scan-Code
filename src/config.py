import argparse
from dataclasses import dataclass
from typing import Optional, List
import os

@dataclass
class SearchConfig:
    repo_path: str = "/root/CodeRootPath"  # 默认为当前目录
    search_term: str = "test,def,void"  # 默认搜索词
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    db_path: str = "db/results.db"
    excel_path: str = "report/results.xlsx"
    log_level: str = "INFO"
    # 默认忽略的目录
    ignore_dirs: List[str] = None
    # 默认搜索的文件后缀
    file_extensions: List[str] = None
    
    def __post_init__(self):
        # 设置默认忽略目录
        if self.ignore_dirs is None:
            self.ignore_dirs = [".git", "__pycache__", ".svn", ".hg", ".idea", ".vscode", "node_modules", ".tox"]
        
        # 设置默认文件后缀（None表示不限制）
        if self.file_extensions is None:
            self.file_extensions = None  # 不限制文件类型

def parse_args() -> SearchConfig:
    """
    创建配置对象，使用config文件中的默认值
    支持通过直接修改config参数来配置
    """
    config = SearchConfig()
    
    # 确保输出目录存在
    db_dir = os.path.dirname(config.db_path) or "."
    excel_dir = os.path.dirname(config.excel_path) or "."
    
    if db_dir != ".":
        os.makedirs(db_dir, exist_ok=True)
    if excel_dir != ".":
        os.makedirs(excel_dir, exist_ok=True)
    
    return config