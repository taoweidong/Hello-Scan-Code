"""
JSON配置适配器

将JSON配置转换为现有的AppConfig格式，提供向后兼容性
"""

import os
from typing import Dict, Any, Optional, List
from .app_config import AppConfig
from .json_config_loader import load_json_config
from loguru import logger


class JSONConfigAdapter:
    """JSON配置适配器"""
    
    @staticmethod
    def from_json_config(json_config: Dict[str, Any]) -> AppConfig:
        """
        从JSON配置创建AppConfig实例
        
        Args:
            json_config: JSON配置字典
            
        Returns:
            AppConfig实例
        """
        # 创建AppConfig实例
        config = AppConfig()
        
        # 基本配置映射
        config.repo_path = json_config.get('repo_path', config.repo_path)
        config.search_term = json_config.get('search_term', config.search_term)
        config.is_regex = json_config.get('is_regex', config.is_regex)
        config.enable_validate = json_config.get('validate', config.enable_validate)
        config.validate_workers = json_config.get('validate_workers', config.validate_workers)
        
        # 输出配置映射
        output_config = json_config.get('output', {})
        config.db_path = output_config.get('db_path', config.db_path)
        config.excel_path = output_config.get('excel_path', config.excel_path)
        
        # 过滤器配置映射
        filters_config = json_config.get('filters', {})
        config.ignore_dirs = filters_config.get('ignore_dirs', config.ignore_dirs)
        config.file_extensions = filters_config.get('file_extensions', config.file_extensions)
        
        return config
    
    @staticmethod
    def to_json_config(app_config: AppConfig) -> Dict[str, Any]:
        """
        将AppConfig转换为JSON配置格式
        
        Args:
            app_config: AppConfig实例
            
        Returns:
            JSON配置字典
        """
        return {
            "repo_path": app_config.repo_path,
            "search_term": app_config.search_term,
            "is_regex": app_config.is_regex,
            "validate": app_config.enable_validate,
            "validate_workers": app_config.validate_workers,
            "output": {
                "db_path": app_config.db_path,
                "excel_path": app_config.excel_path
            },
            "logging": {
                "level": "INFO"  # 默认日志级别
            },
            "filters": {
                "ignore_dirs": app_config.ignore_dirs,
                "file_extensions": app_config.file_extensions
            }
        }


def load_app_config_from_json(config_path: Optional[str] = None) -> AppConfig:
    """
    从JSON配置文件加载AppConfig
    
    Args:
        config_path: 配置文件路径，如果不指定则自动查找
        
    Returns:
        AppConfig实例
    """
    try:
        json_config = load_json_config(config_path)
        app_config = JSONConfigAdapter.from_json_config(json_config)
        
        # 确保输出目录存在
        app_config.ensure_output_dirs()
        
        logger.info("已成功从JSON配置加载应用配置")
        return app_config
        
    except Exception as e:
        logger.error(f"从JSON配置加载应用配置失败: {e}")
        logger.info("使用默认AppConfig配置")
        
        # 回退到默认配置
        config = AppConfig()
        config.load_from_env()
        config.ensure_output_dirs()
        return config


def parse_args_with_json_support() -> AppConfig:
    """
    支持JSON配置的parse_args替代函数
    保持向后兼容性，优先使用JSON配置
    
    Returns:
        AppConfig实例
    """
    return load_app_config_from_json()