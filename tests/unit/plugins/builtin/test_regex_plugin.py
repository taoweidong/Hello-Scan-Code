#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内置正则表达式插件测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from src.plugins.builtin.regex_plugin import RegexScanPlugin


class TestRegexPlugin(unittest.TestCase):
    """内置正则表达式插件测试类"""

    def setUp(self):
        """测试前准备"""
        self.plugin = RegexScanPlugin()

    def test_plugin_properties(self):
        """测试插件属性"""
        self.assertEqual(self.plugin.plugin_id, "builtin.regex")
        self.assertEqual(self.plugin.name, "Regex Scanner")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.description, "基于自定义正则表达式的代码扫描插件")
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
        self.assertEqual(pattern, "")

    def test_initialize(self):
        """测试插件初始化"""
        config = {
            "patterns": [
                {
                    "pattern": r"TODO:.*",
                    "rule_id": "CUSTOM_TODO",
                    "message": "自定义TODO注释",
                    "severity": "medium",
                    "category": "comment",
                    "suggestion": "处理TODO注释"
                }
            ]
        }
        result = self.plugin.initialize(config)
        self.assertTrue(result)
        self.assertTrue(self.plugin.initialized)

    def test_scan_line_with_matches(self):
        """测试扫描匹配正则表达式的行"""
        # 初始化插件
        config = {
            "patterns": [
                {
                    "pattern": r"TODO:.*",
                    "rule_id": "CUSTOM_TODO",
                    "message": "自定义TODO注释",
                    "severity": "medium",
                    "category": "comment",
                    "suggestion": "处理TODO注释"
                }
            ]
        }
        self.plugin.initialize(config)
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "# TODO: 实现功能", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["rule_id"], "CUSTOM_TODO")
        self.assertEqual(results[0]["message"], "自定义TODO注释")

    def test_scan_line_without_matches(self):
        """测试扫描不匹配正则表达式的行"""
        # 初始化插件
        config = {
            "patterns": [
                {
                    "pattern": r"FIXME:.*",
                    "rule_id": "CUSTOM_FIXME",
                    "message": "自定义FIXME注释",
                    "severity": "high",
                    "category": "comment",
                    "suggestion": "处理FIXME注释"
                }
            ]
        }
        self.plugin.initialize(config)
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "# TODO: 实现功能", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_scan_line_with_invalid_regex(self):
        """测试扫描包含无效正则表达式的配置"""
        # 初始化插件
        config = {
            "patterns": [
                {
                    "pattern": r"[",  # 无效的正则表达式
                    "rule_id": "INVALID_REGEX",
                    "message": "无效正则表达式",
                    "severity": "high",
                    "category": "configuration",
                    "suggestion": "检查正则表达式语法"
                }
            ]
        }
        self.plugin.initialize(config)
        
        context = {}
        results = self.plugin.scan_line(
            "test.py", 
            10, 
            "some code", 
            context
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["rule_id"], "REGEX_SYNTAX_ERROR")

    def test_get_config_schema(self):
        """测试获取配置schema"""
        schema = self.plugin.get_config_schema()
        self.assertIsInstance(schema, dict)
        self.assertIn("type", schema)
        self.assertIn("properties", schema)


if __name__ == '__main__':
    unittest.main()