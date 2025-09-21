import argparse
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class SearchConfig:
    repo_path: str = "/root/openstack"  # 默认为当前目录
    search_term: str = "test,helo,pwd"  # 默认搜索词
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    db_path: str = "db/results.db"
    excel_path: str = "report/results.xlsx"
    log_level: str = "INFO"

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