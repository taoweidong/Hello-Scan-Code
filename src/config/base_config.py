"""
基础配置类

为所有配置类提供通用的接口和功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import os


class BaseConfig(ABC):
    """配置基类"""
    
    @abstractmethod
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """验证配置是否有效"""
        pass
    
    def get_env_var(self, key: str, default: Any = None, var_type: type = str) -> Any:
        """
        安全地获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            var_type: 变量类型
            
        Returns:
            转换后的环境变量值
        """
        value = os.getenv(key, default)
        
        if value is None:
            return default
            
        if var_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            try:
                return int(value)
            except ValueError:
                return default
        elif var_type == list:
            return value.split(',') if isinstance(value, str) else value
        else:
            return value
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }