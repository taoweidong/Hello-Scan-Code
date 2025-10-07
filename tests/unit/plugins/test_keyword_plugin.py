#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键字扫描插件测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.plugins.builtin.keyword_plugin import KeywordScanPlugin


class TestKeywordPlugin(unittest.TestCase):
    """关键字扫描插件测试类"""

    def setUp(self):
        """测试前准备"""
        self.plugin = KeywordScanPlugin()

    def test_plugin_properties(self):
        """测试插件属性"""
        self.assertEqual(self.plugin.plugin_id, "builtin.keyword")
        self.assertEqual(self.plugin.name, "Keyword Scanner")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.description, "基于关键字的代码扫描插件")
        self.assertEqual(self.plugin.author, "Hello-Scan-Code Team")

    def test_plugin_initialization(self):
        """测试插件初始化"""
        config = {
            "keywords": ["TODO", "FIXME", "BUG"],
            "case_sensitive": False
        }
        
        result = self.plugin.initialize(config)
        self.assertTrue(result)

    def test_scan_line(self):
        """测试行扫描功能"""
        # 初始化插件
        config = {
            "keywords": ["TODO", "FIXME", "BUG"],
            "case_sensitive": False
        }
        self.plugin.initialize(config)
        
        # 创建扫描上下文
        context = {}
        
        # 测试包含关键字的行
        results = self.plugin.scan_line("test.py", 10, "# TODO: 实现功能", context)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["plugin_id"], "builtin.keyword")
        self.assertEqual(results[0]["file_path"], "test.py")
        self.assertEqual(results[0]["line_number"], 10)
        self.assertEqual(results[0]["message"], "发现关键字: TODO")

    def test_get_grep_pattern(self):
        """测试获取grep模式"""
        # 初始化插件
        config = {
            "keywords": ["TODO", "FIXME", "BUG"],
            "case_sensitive": False
        }
        self.plugin.initialize(config)
        
        pattern = self.plugin.get_grep_pattern()
        self.assertIn("TODO", pattern)
        self.assertIn("FIXME", pattern)
        self.assertIn("BUG", pattern)


if __name__ == '__main__':
    unittest.main()