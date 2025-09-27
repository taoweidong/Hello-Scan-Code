"""
配置加载器模块

提供JSON配置文件的加载和管理功能
"""

import json
import os
import sys
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from .default_config import DEFAULT_CONFIG, dict_to_search_config, SearchConfig
from .config_validator import ConfigValidator

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器类"""
    
    CONFIG_FILENAME = "config.json"
    TEMPLATE_FILENAME = "config.template.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置文件目录，默认为可执行文件所在目录
        """
        self.config_dir = config_dir or self._get_executable_dir()
        self.config_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
        self.template_path = os.path.join(self.config_dir, self.TEMPLATE_FILENAME)
    
    @staticmethod
    def _get_executable_dir() -> str:
        """
        获取可执行文件所在目录
        
        Returns:
            str: 可执行文件目录路径
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的可执行文件
            return os.path.dirname(sys.executable)
        else:
            # 开发环境
            return os.getcwd()
    
    def load_config(self) -> SearchConfig:
        """
        加载配置文件
        
        Returns:
            SearchConfig: 配置对象
        """
        # 首先尝试加载JSON配置文件
        if os.path.exists(self.config_path):
            try:
                config_dict = self._load_json_config()
                return dict_to_search_config(config_dict)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
                logger.info("使用默认配置")
                return dict_to_search_config(DEFAULT_CONFIG)
        else:
            logger.info("未找到配置文件，使用默认配置")
            # 如果有模板文件，建议用户复制
            if os.path.exists(self.template_path):
                logger.info(f"提示: 可以复制 {self.template_path} 为 {self.config_path} 来自定义配置")
            return dict_to_search_config(DEFAULT_CONFIG)
    
    def _load_json_config(self) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        Returns:
            Dict[str, Any]: 配置字典
            
        Raises:
            ValueError: 配置文件格式错误或验证失败
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件JSON格式错误: {e}")
        except FileNotFoundError:
            raise ValueError(f"配置文件不存在: {self.config_path}")
        except Exception as e:
            raise ValueError(f"读取配置文件失败: {e}")
        
        # 验证配置
        is_valid, errors = ConfigValidator.validate_full_config(config_dict)
        if not is_valid:
            error_msg = "配置文件验证失败:\\n" + "\\n".join(f"- {error}" for error in errors)
            raise ValueError(error_msg)
        
        # 合并默认配置
        merged_config = self._merge_with_defaults(config_dict)
        
        logger.info(f"成功加载配置文件: {self.config_path}")
        return merged_config
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将用户配置与默认配置合并
        
        Args:
            user_config: 用户配置字典
            
        Returns:
            Dict[str, Any]: 合并后的配置字典
        """
        merged_config = DEFAULT_CONFIG.copy()
        
        # 递归合并嵌套字典
        def merge_dict(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dict(merged_config, user_config)
    
    def save_config(self, config: SearchConfig) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置对象
        """
        from .default_config import search_config_to_dict
        
        config_dict = search_config_to_dict(config)
        
        try:
            # 确保配置目录存在
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def create_template(self) -> None:
        """
        创建配置模板文件
        """
        try:
            # 确保配置目录存在
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.template_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置模板已创建: {self.template_path}")
        except Exception as e:
            logger.error(f"创建配置模板失败: {e}")
            raise
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置文件信息
        
        Returns:
            Dict[str, Any]: 配置信息
        """
        return {
            "config_dir": self.config_dir,
            "config_path": self.config_path,
            "template_path": self.template_path,
            "config_exists": os.path.exists(self.config_path),
            "template_exists": os.path.exists(self.template_path),
            "is_executable": getattr(sys, 'frozen', False)
        }


def load_config_from_file(config_file_path: Optional[str] = None) -> SearchConfig:
    """
    便捷函数：从指定文件或默认位置加载配置
    
    Args:
        config_file_path: 配置文件路径，为None时使用默认位置
        
    Returns:
        SearchConfig: 配置对象
    """
    if config_file_path:
        config_dir = os.path.dirname(config_file_path)
        filename = os.path.basename(config_file_path)
        loader = ConfigLoader(config_dir)
        loader.CONFIG_FILENAME = filename
    else:
        loader = ConfigLoader()
    
    return loader.load_config()


def create_config_template(target_dir: Optional[str] = None) -> None:
    """
    便捷函数：创建配置模板文件
    
    Args:
        target_dir: 目标目录，为None时使用默认位置
    """
    loader = ConfigLoader(target_dir)
    loader.create_template()