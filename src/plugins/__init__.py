#!/usr/bin/env python3
"""
插件系统包
"""

from . import builtin
from . import custom

__all__ = [
    "builtin",
    "custom"
]


# 插件注册表
_plugin_registry = {}


def register_plugin(cls):
    """
    插件装饰器，用于注册插件
    
    Args:
        cls: 插件类
        
    Returns:
        插件类
    """
    _plugin_registry[cls.__name__] = cls
    return cls


def get_plugin_registry():
    """
    获取插件注册表
    
    Returns:
        插件注册表字典
    """
    return _plugin_registry


def get_plugin(name):
    """
    根据名称获取插件类
    
    Args:
        name: 插件名称
        
    Returns:
        插件类或None
    """
    return _plugin_registry.get(name)