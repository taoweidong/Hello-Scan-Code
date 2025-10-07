#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件管理器测试
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.plugin.manager import PluginManager


class TestPluginManager(unittest.TestCase):
    """插件管理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟的配置管理器
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_plugin_dirs.return_value = []
        self.mock_config_manager.get_plugin_configs.return_value = {}
        
        # 创建插件管理器实例
        self.plugin_manager = PluginManager(self.mock_config_manager)

    def test_manager_init(self):
        """测试插件管理器初始化"""
        self.assertIsInstance(self.plugin_manager, PluginManager)
        self.assertEqual(self.plugin_manager.config_manager, self.mock_config_manager)
        self.assertFalse(self.plugin_manager._initialized)

    def test_initialize(self):
        """测试插件管理器初始化方法"""
        # 配置模拟对象
        self.mock_config_manager.get_plugin_dirs.return_value = []
        self.mock_config_manager.get_plugin_configs.return_value = {}
        
        # 执行初始化
        result = self.plugin_manager.initialize()
        
        # 验证结果
        self.assertTrue(result)
        self.assertTrue(self.plugin_manager._initialized)

    def test_get_enabled_plugins(self):
        """测试获取启用的插件"""
        # 初始化插件管理器
        self.plugin_manager.initialize()
        
        # 获取启用的插件
        plugins = self.plugin_manager.get_enabled_plugins()
        
        # 验证结果
        self.assertIsInstance(plugins, list)

    def test_get_plugin(self):
        """测试根据ID获取插件"""
        # 初始化插件管理器
        self.plugin_manager.initialize()
        
        # 获取不存在的插件
        plugin = self.plugin_manager.get_plugin("nonexistent")
        
        # 验证结果
        self.assertIsNone(plugin)

    def test_unload_plugin(self):
        """测试卸载插件"""
        # 初始化插件管理器
        self.plugin_manager.initialize()
        
        # 卸载不存在的插件
        result = self.plugin_manager.unload_plugin("nonexistent")
        
        # 验证结果
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()