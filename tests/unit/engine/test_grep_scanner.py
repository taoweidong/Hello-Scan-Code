#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grep扫描器测试
"""

import unittest
import sys
import os
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.engine.grep_scanner import GrepScanner


class TestGrepScanner(unittest.TestCase):
    """Grep扫描器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test.py")
        
        # 创建测试文件
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            f.write("# TODO: 实现功能\n")
            f.write("def test_function():\n")
            f.write("    # FIXME: 修复bug\n")
            f.write("    pass\n")
        
        # 创建GrepScanner实例
        self.scanner = GrepScanner(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_grep_scanner_init(self):
        """测试Grep扫描器初始化"""
        self.assertEqual(str(self.scanner.repo_path), os.path.abspath(self.temp_dir))

    def test_grep_scanner_scan(self):
        """测试Grep扫描器扫描功能"""
        # 在Windows上跳过这个测试，因为可能没有grep命令
        if os.name == 'nt':  # Windows
            self.skipTest("Windows系统可能没有grep命令")
            
        # 执行扫描
        results = list(self.scanner.scan("TODO|FIXME"))
        
        # 验证结果
        self.assertIsInstance(results, list)
        # 应该找到至少一个匹配项
        self.assertGreater(len(results), 0)


if __name__ == '__main__':
    unittest.main()