#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描引擎测试
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.engine.scan_engine import OptimizedScanEngine


class TestScanEngine(unittest.TestCase):
    """扫描引擎测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟的配置管理器和插件管理器
        self.mock_config_manager = Mock()
        self.mock_plugin_manager = Mock()
        
        # 配置模拟对象的返回值
        self.mock_config_manager.get_repo_path.return_value = "."
        self.mock_config_manager.get_ignore_dirs.return_value = [".git", "__pycache__"]
        self.mock_config_manager.get_file_extensions.return_value = [".py", ".js"]
        
        # 创建扫描引擎实例
        self.engine = OptimizedScanEngine(self.mock_config_manager, self.mock_plugin_manager)

    def test_engine_init(self):
        """测试扫描引擎初始化"""
        self.assertIsInstance(self.engine, OptimizedScanEngine)
        self.assertEqual(self.engine.config_manager, self.mock_config_manager)
        self.assertEqual(self.engine.plugin_manager, self.mock_plugin_manager)

    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.engine.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_files', stats)
        self.assertIn('scanned_files', stats)
        self.assertIn('total_plugins', stats)
        self.assertIn('scan_time', stats)
        self.assertIn('results_count', stats)

    @patch('src.engine.scan_engine.GrepScanner')
    def test_scan_method(self, mock_grep_scanner):
        """测试扫描方法"""
        # 配置模拟对象
        mock_plugin = Mock()
        mock_plugin.get_grep_pattern.return_value = "TODO"
        self.mock_plugin_manager.get_enabled_plugins.return_value = [mock_plugin]
        
        # 执行扫描
        results = self.engine.scan()
        
        # 验证结果
        self.assertIsInstance(results, list)
        # 验证配置管理器的方法被调用
        self.mock_config_manager.get_repo_path.assert_called_once()
        # get_ignore_dirs可能被多次调用，所以我们检查至少被调用一次
        self.assertGreaterEqual(self.mock_config_manager.get_ignore_dirs.call_count, 1)
        self.mock_config_manager.get_file_extensions.assert_called_once()
        # 验证插件管理器的方法被调用
        self.mock_plugin_manager.get_enabled_plugins.assert_called_once()


if __name__ == '__main__':
    unittest.main()