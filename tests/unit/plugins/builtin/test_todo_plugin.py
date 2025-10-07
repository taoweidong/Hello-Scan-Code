#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内置TODO插件测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from src.plugins.builtin.todo_plugin import TodoScanPlugin


class TestTodoPlugin(unittest.TestCase):
    """内置TODO插件测试类"""

    def setUp(self):
        """测试前准备"""
        self.plugin = TodoScanPlugin()

    def test_plugin_properties(self):
        """测试插件属性"""
        self.assertEqual(self.plugin.plugin_id, "builtin.todo")
        self.assertEqual(self.plugin.name, "TODO Scanner")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.description, "检测代码中的TODO注释")
        self.assertEqual(self.plugin.author, "Hello-Scan-Code Team")

    def test_get_supported_extensions(self):
        """测试获取支持的文件扩展名"""
        extensions = self.plugin.get_supported_extensions()
        self.assertIsInstance(extensions, list)
        self.assertIn(".py", extensions)
        self.assertIn(".js", extensions)
        self.assertIn(".java", extensions)

    def test_get_grep_pattern(self):
        """测试获取grep模式"""
        pattern = self.plugin.get_grep_pattern()
        self.assertIsInstance(pattern, str)
        self.assertIn("TODO", pattern)
        self.assertIn("FIXME", pattern)
        self.assertIn("BUG", pattern)

    def test_initialize(self):
        """测试插件初始化"""
        config = {}
        result = self.plugin.initialize(config)
        self.assertTrue(result)
        self.assertTrue(self.plugin.initialized)

    def test_scan_line_with_todo(self):
        """测试扫描包含TODO的行"""
        # 初始化插件
        self.plugin.initialize({})
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "# TODO: 实现功能", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # 查找TODO相关的规则
        todo_results = [r for r in results if "TODO" in r["rule_id"]]
        self.assertEqual(len(todo_results), 1)
        self.assertEqual(todo_results[0]["message"], "发现TODO注释")

    def test_scan_line_with_fixme(self):
        """测试扫描包含FIXME的行"""
        # 初始化插件
        self.plugin.initialize({})
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            15, 
            "// FIXME: 修复bug", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # 查找FIXME相关的规则
        fixme_results = [r for r in results if "FIXME" in r["rule_id"]]
        self.assertEqual(len(fixme_results), 1)
        self.assertEqual(fixme_results[0]["message"], "发现FIXME注释")

    def test_scan_line_with_bug(self):
        """测试扫描包含BUG的行"""
        # 初始化插件
        self.plugin.initialize({})
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            20, 
            "# BUG: 这里有bug", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # 查找BUG相关的规则
        bug_results = [r for r in results if "BUG" in r["rule_id"]]
        self.assertEqual(len(bug_results), 1)
        self.assertEqual(bug_results[0]["message"], "发现BUG注释")

    def test_scan_line_without_matches(self):
        """测试扫描不包含TODO关键字的行"""
        # 初始化插件
        self.plugin.initialize({})
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "print('Hello World')", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_scan_line_uninitialized(self):
        """测试未初始化插件的扫描"""
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "# TODO: 实现功能", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_get_config_schema(self):
        """测试获取配置schema"""
        schema = self.plugin.get_config_schema()
        self.assertIsInstance(schema, dict)
        self.assertIn("type", schema)
        self.assertIn("properties", schema)


if __name__ == '__main__':
    unittest.main()