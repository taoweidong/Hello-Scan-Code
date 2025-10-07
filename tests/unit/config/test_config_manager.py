#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器测试
"""

import unittest
import os
import tempfile
import json
from pathlib import Path

# 添加src目录到Python路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """配置管理器测试类"""

    def setUp(self):
        """测试前准备"""
        self.test_config = {
            "repo_path": ".",
            "ignore_dirs": [".git", "__pycache__", "node_modules"],
            "file_extensions": [".py", ".js", ".java"],
            "plugins": {
                "enabled": ["keyword", "todo", "security"],
                "dirs": ["src/plugins/custom/"]
            },
            "output": {
                "report_dir": "./report/",
                "export_formats": ["excel", "html"]
            },
            "scan": {
                "timeout": 300,
                "max_file_size": 10485760
            },
            "plugin_configs": {
                "keyword": {
                    "keywords": ["TODO", "FIXME", "BUG"],
                    "case_sensitive": False
                },
                "todo": {
                    "patterns": ["TODO:*", "FIXME:*"]
                },
                "security": {
                    "patterns": ["password\\s*=\\s*['\"].*['\"]", "secret\\s*=\\s*['\"].*['\"]"]
                }
            }
        }
        
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=2, ensure_ascii=False)
        
        # 创建ConfigManager实例
        self.config_manager = ConfigManager(self.config_file)

    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_get_repo_path(self):
        """测试获取仓库路径"""
        repo_path = self.config_manager.get_repo_path()
        self.assertEqual(repo_path, ".")

    def test_get_ignore_dirs(self):
        """测试获取忽略目录"""
        ignore_dirs = self.config_manager.get_ignore_dirs()
        expected = [".git", "__pycache__", "node_modules"]
        self.assertEqual(ignore_dirs, expected)

    def test_get_file_extensions(self):
        """测试获取文件扩展名"""
        file_extensions = self.config_manager.get_file_extensions()
        expected = [".py", ".js", ".java"]
        self.assertEqual(file_extensions, expected)

    def test_get_enabled_plugins(self):
        """测试获取启用插件"""
        enabled_plugins = self.config_manager.get_enabled_plugins()
        expected = ["keyword", "todo", "security"]
        self.assertEqual(enabled_plugins, expected)

    def test_get_plugin_config(self):
        """测试获取插件配置"""
        keyword_config = self.config_manager.get_plugin_config("keyword")
        expected = {
            "keywords": ["TODO", "FIXME", "BUG"],
            "case_sensitive": False
        }
        self.assertEqual(keyword_config, expected)

    def test_get_export_formats(self):
        """测试获取导出格式"""
        export_formats = self.config_manager.get_export_formats()
        expected = ["excel", "html"]
        self.assertEqual(export_formats, expected)

    def test_get_report_dir(self):
        """测试获取报告目录"""
        report_dir = self.config_manager.get_report_dir()
        self.assertEqual(report_dir, "./report/")


if __name__ == '__main__':
    unittest.main()