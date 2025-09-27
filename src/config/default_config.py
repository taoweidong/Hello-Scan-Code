"""
默认配置定义模块

定义系统的默认配置项和配置创建函数
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import os


@dataclass
class SearchConfig:
    """搜索配置数据类"""
    repo_path: str = "."
    search_term: str = "test,def,void" 
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    db_path: str = "results.db"
    excel_path: str = "results.xlsx"
    log_level: str = "INFO"
    ignore_dirs: List[str] = field(default_factory=lambda: [
        ".git", "__pycache__", ".svn", ".hg", ".idea", 
        ".vscode", "node_modules", ".tox", "dist", "build"
    ])
    file_extensions: Optional[List[str]] = None


# 默认配置字典，用于JSON序列化
DEFAULT_CONFIG: Dict[str, Any] = {
    "repo_path": ".",
    "search_term": "test,def,void",
    "is_regex": False,
    "validate": False,
    "validate_workers": 4,
    "output": {
        "db_path": "results.db",
        "excel_path": "results.xlsx"
    },
    "logging": {
        "level": "INFO"
    },
    "filters": {
        "ignore_dirs": [
            ".git", "__pycache__", ".svn", ".hg", ".idea",
            ".vscode", "node_modules", ".tox", "dist", "build"
        ],
        "file_extensions": None
    }
}


def create_default_config() -> SearchConfig:
    """
    创建默认配置对象
    
    Returns:
        SearchConfig: 默认配置实例
    """
    return SearchConfig()


def dict_to_search_config(config_dict: Dict[str, Any]) -> SearchConfig:
    """
    将配置字典转换为SearchConfig对象
    
    Args:
        config_dict: 配置字典
        
    Returns:
        SearchConfig: 配置对象
    """
    # 处理嵌套的output配置
    output_config = config_dict.get("output", {})
    db_path = output_config.get("db_path", DEFAULT_CONFIG["output"]["db_path"])
    excel_path = output_config.get("excel_path", DEFAULT_CONFIG["output"]["excel_path"])
    
    # 处理嵌套的logging配置
    logging_config = config_dict.get("logging", {})
    log_level = logging_config.get("level", DEFAULT_CONFIG["logging"]["level"])
    
    # 处理嵌套的filters配置
    filters_config = config_dict.get("filters", {})
    ignore_dirs = filters_config.get("ignore_dirs", DEFAULT_CONFIG["filters"]["ignore_dirs"])
    file_extensions = filters_config.get("file_extensions", DEFAULT_CONFIG["filters"]["file_extensions"])
    
    return SearchConfig(
        repo_path=config_dict.get("repo_path", DEFAULT_CONFIG["repo_path"]),
        search_term=config_dict.get("search_term", DEFAULT_CONFIG["search_term"]),
        is_regex=config_dict.get("is_regex", DEFAULT_CONFIG["is_regex"]),
        validate=config_dict.get("validate", DEFAULT_CONFIG["validate"]),
        validate_workers=config_dict.get("validate_workers", DEFAULT_CONFIG["validate_workers"]),
        db_path=db_path,
        excel_path=excel_path,
        log_level=log_level,
        ignore_dirs=ignore_dirs,
        file_extensions=file_extensions
    )


def search_config_to_dict(config: SearchConfig) -> Dict[str, Any]:
    """
    将SearchConfig对象转换为字典
    
    Args:
        config: SearchConfig对象
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    return {
        "repo_path": config.repo_path,
        "search_term": config.search_term,
        "is_regex": config.is_regex,
        "validate": config.validate,
        "validate_workers": config.validate_workers,
        "output": {
            "db_path": config.db_path,
            "excel_path": config.excel_path
        },
        "logging": {
            "level": config.log_level
        },
        "filters": {
            "ignore_dirs": config.ignore_dirs,
            "file_extensions": config.file_extensions
        }
    }