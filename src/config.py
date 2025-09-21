import argparse
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class SearchConfig:
    repo_path: str = "/root/openstack"  # 默认为当前目录
    search_term: str = "test"  # 默认搜索词
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    db_path: str = "db/results.db"
    excel_path: str = "report/results.xlsx"
    log_level: str = "INFO"

def parse_args() -> SearchConfig:
    # --repo_path /path/to/repo --search_term "hello world"
    parser = argparse.ArgumentParser(description="高效代码搜索工具")
    parser.add_argument("repo_path", nargs="?", default="/root/openstack", help="代码仓库路径")
    parser.add_argument("search_term", nargs="?", default="test", help="要搜索的字符串或正则表达式")
    parser.add_argument("--regex", action="store_true", help="是否使用正则表达式搜索")
    parser.add_argument("--validate", action="store_true", help="是否启用二次校验")
    parser.add_argument("--validate_workers", type=int, default=4, help="二次校验的并发工作进程数")
    parser.add_argument("--db_path", default="db/results.db", help="SQLite数据库输出路径")
    parser.add_argument("--excel_path", default="report/results.xlsx", help="Excel文件输出路径")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    db_dir = os.path.dirname(args.db_path) or "."
    excel_dir = os.path.dirname(args.excel_path) or "."
    
    if db_dir != ".":
        os.makedirs(db_dir, exist_ok=True)
    if excel_dir != ".":
        os.makedirs(excel_dir, exist_ok=True)
    
    return SearchConfig(
        repo_path=args.repo_path,
        search_term=args.search_term,
        is_regex=args.regex,
        validate=args.validate,
        validate_workers=args.validate_workers,
        db_path=args.db_path,
        excel_path=args.excel_path,
        log_level=args.log_level
    )