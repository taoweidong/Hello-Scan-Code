#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件注册表测试
"""

import unittest
import sys
import os
from unittest.mock import Mock
from typing import Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.plugin.registry import PluginRegistry
from src.plugin.base import IScanPlugin, ScanContext


class MockPlugin(IScanPlugin):
    """模拟插件类用于测试"""
    
    def __init__(self, plugin_id="test.plugin", name="Test Plugin"):
        self._plugin_id = plugin_id
        self._name = name
    
    @property
    def plugin_id(self) -> str:
        return self._plugin_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Test plugin for unit testing"
    
    @property
    def author(self) -> str:
        return "Test Author"
    
    def get_supported_extensions(self) -> list:
        return [".py", ".js"]
    
    def get_grep_pattern(self) -> str:
        return "test"
    
    def initialize(self, config: dict) -> bool:
        return True
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, context: ScanContext) -> list:
        return []


class TestPluginRegistry(unittest.TestCase):
    """插件注册表测试类"""

    def setUp(self):
        """测试前准备"""
        self.registry = PluginRegistry()
        self.mock_plugin = MockPlugin()

    def test_registry_init(self):
        """测试插件注册表初始化"""
        self.assertIsInstance(self.registry, PluginRegistry)
        self.assertEqual(len(self.registry.get_all_plugins()), 0)

    def test_register_plugin(self):
        """测试注册插件"""
        result = self.registry.register_plugin(self.mock_plugin)
        self.assertTrue(result)
        self.assertEqual(len(self.registry.get_all_plugins()), 1)

    def test_unregister_plugin(self):
        """测试注销插件"""
        # 先注册插件
        self.registry.register_plugin(self.mock_plugin)
        
        # 注销插件
        result = self.registry.unregister_plugin(self.mock_plugin.plugin_id)
        self.assertTrue(result)
        self.assertEqual(len(self.registry.get_all_plugins()), 0)
        
        # 注销不存在的插件
        result = self.registry.unregister_plugin("nonexistent")
        self.assertFalse(result)

    def test_get_plugin(self):
        """测试根据ID获取插件"""
        # 注册插件
        self.registry.register_plugin(self.mock_plugin)
        
        # 获取插件
        plugin = self.registry.get_plugin(self.mock_plugin.plugin_id)
        self.assertEqual(plugin, self.mock_plugin)
        
        # 获取不存在的插件
        plugin = self.registry.get_plugin("nonexistent")
        self.assertIsNone(plugin)

    def test_get_all_plugins(self):
        """测试获取所有插件"""
        # 注册多个插件
        plugin1 = MockPlugin("plugin.1")
        plugin2 = MockPlugin("plugin.2")
        
        self.registry.register_plugin(plugin1)
        self.registry.register_plugin(plugin2)
        
        # 获取所有插件
        plugins = self.registry.get_all_plugins()
        self.assertEqual(len(plugins), 2)
        self.assertIn(plugin1, plugins)
        self.assertIn(plugin2, plugins)

    def test_plugin_exists(self):
        """测试检查插件是否存在"""
        # 注册插件
        self.registry.register_plugin(self.mock_plugin)
        
        # 检查存在的插件
        exists = self.registry.plugin_exists(self.mock_plugin.plugin_id)
        self.assertTrue(exists)
        
        # 检查不存在的插件
        exists = self.registry.plugin_exists("nonexistent")
        self.assertFalse(exists)

    def test_add_plugin_to_category(self):
        """测试将插件添加到分类"""
        # 注册插件
        self.registry.register_plugin(self.mock_plugin)
        
        # 添加到分类
        self.registry.add_plugin_to_category(self.mock_plugin, "test_category")
        
        # 获取分类中的插件
        plugins = self.registry.get_plugins_by_category("test_category")
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0], self.mock_plugin)

    def test_get_plugins_by_category(self):
        """测试根据分类获取插件"""
        # 获取不存在分类中的插件
        plugins = self.registry.get_plugins_by_category("nonexistent")
        self.assertEqual(len(plugins), 0)


if __name__ == '__main__':
    unittest.main()