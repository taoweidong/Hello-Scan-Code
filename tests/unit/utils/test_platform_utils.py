#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台工具函数测试
"""

import unittest
import sys
import os
from unittest.mock import patch, Mock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.utils.platform_utils import (
    is_windows, is_unix, is_macos, get_platform, 
    check_command_exists, run_command, get_cpu_count, get_memory_info
)


class TestPlatformUtils(unittest.TestCase):
    """平台工具函数测试类"""

    def test_is_windows(self):
        """测试是否为Windows系统"""
        # 这个测试依赖于实际的运行环境
        result = is_windows()
        self.assertIsInstance(result, bool)

    def test_is_unix(self):
        """测试是否为Unix系统"""
        # 这个测试依赖于实际的运行环境
        result = is_unix()
        self.assertIsInstance(result, bool)

    def test_is_macos(self):
        """测试是否为macOS系统"""
        # 这个测试依赖于实际的运行环境
        result = is_macos()
        self.assertIsInstance(result, bool)

    def test_get_platform(self):
        """测试获取平台信息"""
        platform_name = get_platform()
        self.assertIsInstance(platform_name, str)
        self.assertTrue(len(platform_name) > 0)

    def test_get_cpu_count(self):
        """测试获取CPU核心数"""
        cpu_count = get_cpu_count()
        self.assertIsInstance(cpu_count, int)
        self.assertGreater(cpu_count, 0)

    @patch('src.utils.platform_utils.subprocess.run')
    def test_check_command_exists_windows(self, mock_run):
        """测试检查Windows系统命令是否存在"""
        # 模拟Windows环境
        with patch('src.utils.platform_utils.is_windows', return_value=True):
            # 模拟命令存在
            mock_run.return_value = Mock(returncode=0, stdout="command.exe")
            result = check_command_exists("test_command")
            self.assertTrue(result)

    @patch('src.utils.platform_utils.subprocess.run')
    def test_check_command_exists_unix(self, mock_run):
        """测试检查Unix系统命令是否存在"""
        # 模拟Unix环境
        with patch('src.utils.platform_utils.is_windows', return_value=False):
            # 模拟命令存在
            mock_run.return_value = Mock(returncode=0, stdout="/usr/bin/command")
            result = check_command_exists("test_command")
            self.assertTrue(result)

    @patch('src.utils.platform_utils.subprocess.run')
    def test_run_command(self, mock_run):
        """测试运行命令"""
        # 模拟命令执行结果
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = run_command(["echo", "test"])
        if result is not None:
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "test output")

    @patch('src.utils.platform_utils.is_unix')
    def test_get_memory_info_unix(self, mock_is_unix):
        """测试获取Unix系统内存信息"""
        # 模拟Unix环境
        mock_is_unix.return_value = True
        
        # 模拟文件读取
        mock_file = Mock()
        mock_file.read.return_value = "MemTotal: 1000000 kB\nMemAvailable: 500000 kB"
        with patch('builtins.open', return_value=mock_file):
            memory_info = get_memory_info()
            self.assertIsInstance(memory_info, dict)
            self.assertIn("total", memory_info)
            self.assertIn("available", memory_info)
            self.assertIn("used", memory_info)

    def test_get_memory_info_windows(self):
        """测试获取Windows系统内存信息"""
        # 模拟Windows环境
        with patch('src.utils.platform_utils.is_unix', return_value=False):
            memory_info = get_memory_info()
            self.assertIsInstance(memory_info, dict)
            self.assertIn("total", memory_info)
            self.assertIn("available", memory_info)
            self.assertIn("used", memory_info)


if __name__ == '__main__':
    unittest.main()