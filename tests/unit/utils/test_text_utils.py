#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本工具函数测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.utils.text_utils import (
    extract_code_snippets, highlight_text, truncate_text, 
    normalize_whitespace, count_lines, find_pattern_positions
)


class TestTextUtils(unittest.TestCase):
    """文本工具函数测试类"""

    def test_extract_code_snippets(self):
        """测试提取代码片段"""
        text = "line 1\nline 2\nline 3\nline 4\nline 5"
        line_numbers = [3]
        
        snippets = extract_code_snippets(text, line_numbers, context_lines=1)
        
        self.assertIsInstance(snippets, list)
        self.assertEqual(len(snippets), 1)
        self.assertIn("line_number", snippets[0])
        self.assertIn("snippet", snippets[0])

    def test_highlight_text(self):
        """测试高亮文本"""
        text = "This is a test text with TODO items"
        pattern = r"TODO"
        highlighted = highlight_text(text, pattern, "**", "**")
        
        self.assertIsInstance(highlighted, str)
        self.assertIn("**TODO**", highlighted)

    def test_truncate_text(self):
        """测试截断文本"""
        text = "This is a very long text that needs to be truncated"
        truncated = truncate_text(text, max_length=20, suffix="...")
        
        self.assertIsInstance(truncated, str)
        self.assertLessEqual(len(truncated), 20)
        self.assertIn("...", truncated)

    def test_truncate_text_no_truncation(self):
        """测试不截断的文本"""
        text = "Short text"
        truncated = truncate_text(text, max_length=20, suffix="...")
        
        self.assertEqual(truncated, text)

    def test_normalize_whitespace(self):
        """测试标准化空白字符"""
        text = "This   has    multiple     spaces"
        normalized = normalize_whitespace(text)
        
        self.assertIsInstance(normalized, str)
        self.assertNotIn("  ", normalized)  # 不应该有多个连续空格

    def test_count_lines(self):
        """测试计算文本行数"""
        text = "line 1\nline 2\nline 3"
        line_count = count_lines(text)
        
        self.assertIsInstance(line_count, int)
        self.assertEqual(line_count, 3)

    def test_find_pattern_positions(self):
        """测试查找模式位置"""
        text = "This is a test text with TODO items and TODO markers"
        pattern = r"TODO"
        positions = find_pattern_positions(text, pattern)
        
        self.assertIsInstance(positions, list)
        self.assertEqual(len(positions), 2)
        for position in positions:
            self.assertIn("start", position)
            self.assertIn("end", position)
            self.assertIn("line_number", position)


if __name__ == '__main__':
    unittest.main()