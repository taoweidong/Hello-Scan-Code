"""
配置管理器

提供统一的配置管理接口，集中管理所有配置类，支持JSON配置文件
"""

from typing import Optional, Dict, Any, TypeVar, Type
from .base_config import BaseConfig
from .app_config import AppConfig
from .logger_config import LoggerConfig, setup_logger
from .database_config import DatabaseConfig
from .json_config_loader import load_config_from_json, get_json_loader

T = TypeVar('T', bound=BaseConfig)


class ConfigManager:
    """配置管理器 - 统一管理所有配置"""
    
    def __init__(self):
        self._configs: Dict[str, BaseConfig] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """初始化所有配置"""
        if self._initialized:
            return
            
        # 初始化各个配置模块
        self.app = self.get_config(AppConfig)
        self.logger = self.get_config(LoggerConfig)
        self.database = self.get_config(DatabaseConfig)
        
        # 设置日志系统
        setup_logger(self.logger)
        
        # 确保输出目录存在
        self.app.ensure_output_dirs()
        self.database.ensure_output_dirs()
        
        self._initialized = True
    
    def get_config(self, config_class: Type[T]) -> T:
        """
        获取配置实例，支持JSON配置文件加载
        
        Args:
            config_class: 配置类
            
        Returns:
            配置实例
        """
        config_name = config_class.__name__
        
        if config_name not in self._configs:
            config_instance = config_class()
            
            # 先从环境变量加载
            config_instance.load_from_env()
            
            # 再从JSON文件加载（优先级更高）
            config_instance = load_config_from_json(config_instance)
            
            if not config_instance.validate():
                raise ValueError(f"配置验证失败: {config_name}")
                
            self._configs[config_name] = config_instance
        
        return self._configs[config_name]
    
    def reload_config(self, config_class: Type[T]) -> T:
        """
        重新加载配置
        
        Args:
            config_class: 配置类
            
        Returns:
            新的配置实例
        """
        config_name = config_class.__name__
        if config_name in self._configs:
            del self._configs[config_name]
        return self.get_config(config_class)
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置的字典表示
        
        Returns:
            所有配置的字典
        """
        if not self._initialized:
            self.initialize()
            
        return {
            name: config.to_dict() 
            for name, config in self._configs.items()
        }
    
    def validate_all(self) -> bool:
        """
        验证所有配置
        
        Returns:
            所有配置是否都有效
        """
        if not self._initialized:
            self.initialize()
            
        return all(config.validate() for config in self._configs.values())

    def create_config_template(self) -> None:
        """创建配置模板文件"""
        loader = get_json_loader()
        loader.save_config_template()
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息"""
        loader = get_json_loader()
        return loader.get_config_info()


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.initialize()
    return _config_manager


def get_app_config() -> AppConfig:
    """获取应用配置"""
    return get_config_manager().app


def get_logger_config() -> LoggerConfig:
    """获取日志配置"""
    return get_config_manager().logger


def get_database_config() -> DatabaseConfig:
    """获取数据库配置"""
    return get_config_manager().database