#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具函数测试
"""

import unittest
import sys
import os
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.utils.file_utils import is_binary_file


class TestFileUtils(unittest.TestCase):
    """文件工具函数测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_is_binary_file_with_text_file(self):
        """测试文本文件识别"""
        # 创建文本文件
        text_file = os.path.join(self.temp_dir, "text.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("This is a text file.\nWith multiple lines.\n")
        
        result = is_binary_file(text_file)
        self.assertFalse(result)

    def test_is_binary_file_with_binary_file(self):
        """测试二进制文件识别"""
        # 创建二进制文件
        binary_file = os.path.join(self.temp_dir, "binary.bin")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')
        
        result = is_binary_file(binary_file)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()