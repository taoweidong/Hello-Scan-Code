#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件发现服务测试
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.plugin.discovery import PluginDiscovery


class TestPluginDiscovery(unittest.TestCase):
    """插件发现服务测试类"""

    def setUp(self):
        """测试前准备"""
        self.discovery = PluginDiscovery()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_discovery_init(self):
        """测试插件发现服务初始化"""
        self.assertIsInstance(self.discovery, PluginDiscovery)
        self.assertEqual(len(self.discovery.get_discovered_plugins()), 0)

    def test_discover_plugins(self):
        """测试发现插件"""
        # 创建测试插件目录
        plugin_dirs = [self.temp_dir]
        
        # 执行插件发现
        discovered = self.discovery.discover_plugins(plugin_dirs)
        
        # 验证结果
        self.assertIsInstance(discovered, dict)

    def test_discover_from_directory(self):
        """测试从目录中发现插件"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test_plugin.py"
        test_file.write_text("# Test plugin file")
        
        # 执行目录发现
        discovered = self.discovery._discover_from_directory(Path(self.temp_dir))
        
        # 验证结果
        self.assertIsInstance(discovered, dict)

    def test_discover_from_file(self):
        """测试从文件中发现插件"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test_plugin.py"
        test_file.write_text("# Test plugin file")
        
        # 执行文件发现
        discovered = self.discovery._discover_from_file(test_file)
        
        # 验证结果
        self.assertIsInstance(discovered, dict)
        self.assertEqual(len(discovered), 0)  # 当前实现返回空字典

    def test_get_discovered_plugins(self):
        """测试获取已发现的插件"""
        # 获取已发现的插件
        plugins = self.discovery.get_discovered_plugins()
        
        # 验证结果
        self.assertIsInstance(plugins, dict)
        self.assertEqual(len(plugins), 0)


if __name__ == '__main__':
    unittest.main()