import argparse
import os
from typing import Optional

# 向后兼容：重新导出新配置系统的类和函数
from .config.default_config import SearchConfig
from .config.config_loader import ConfigLoader, load_config_from_file


def parse_args() -> SearchConfig:
    """
    创建配置对象，优先加载JSON配置文件，回退到默认配置
    保持向后兼容性
    """
    try:
        # 尝试从JSON配置文件加载
        loader = ConfigLoader()
        config = loader.load_config()
        
        # 确保输出目录存在
        db_dir = os.path.dirname(config.db_path) or "."
        excel_dir = os.path.dirname(config.excel_path) or "."
        
        if db_dir != ".":
            os.makedirs(db_dir, exist_ok=True)
        if excel_dir != ".":
            os.makedirs(excel_dir, exist_ok=True)
        
        return config
    except Exception as e:
        # 如果加载失败，使用默认配置
        print(f"警告: 配置加载失败，使用默认配置: {e}")
        config = SearchConfig()
        
        # 确保输出目录存在
        db_dir = os.path.dirname(config.db_path) or "."
        excel_dir = os.path.dirname(config.excel_path) or "."
        
        if db_dir != ".":
            os.makedirs(db_dir, exist_ok=True)
        if excel_dir != ".":
            os.makedirs(excel_dir, exist_ok=True)
        
        return config


def load_json_config(config_path: Optional[str] = None) -> SearchConfig:
    """
    从JSON文件加载配置
    
    Args:
        config_path: 配置文件路径，为None时使用默认位置
        
    Returns:
        SearchConfig: 配置对象
    """
    return load_config_from_file(config_path)


def create_config_template(target_dir: Optional[str] = None) -> None:
    """
    创建配置模板文件
    
    Args:
        target_dir: 目标目录，为None时使用当前目录
    """
    from .config.config_loader import create_config_template
    create_config_template(target_dir)