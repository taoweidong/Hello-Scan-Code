#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导出器测试
"""

import unittest
import sys
import os
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.exporters.excel_exporter import ExcelExporter


class TestExcelExporter(unittest.TestCase):
    """Excel导出器测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = ExcelExporter(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_excel_exporter_init(self):
        """测试Excel导出器初始化"""
        self.assertEqual(self.exporter.output_dir, self.temp_dir)

    def test_excel_exporter_export(self):
        """测试Excel导出功能"""
        # 创建测试数据
        results = [
            {
                "plugin_id": "keyword",
                "file_path": "test.py",
                "line_number": 10,
                "column": 0,
                "message": "发现待办事项",
                "severity": "medium",
                "rule_id": "TODO001",
                "category": "comment",
                "suggestion": "处理待办事项",
                "code_snippet": "TODO: 实现功能"
            }
        ]
        
        # 执行导出
        output_file = self.exporter.export(results, "test_results.xlsx")
        
        # 验证结果
        self.assertTrue(os.path.exists(output_file))


if __name__ == '__main__':
    unittest.main()