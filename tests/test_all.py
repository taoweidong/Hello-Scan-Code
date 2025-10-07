#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试入口文件
运行所有单元测试并生成覆盖率报告
"""

import os
import sys
import unittest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_all_tests():
    """运行所有测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'unit')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("运行所有单元测试...")
    success = run_all_tests()
    if success:
        print("\n所有测试通过!")
        sys.exit(0)
    else:
        print("\n部分测试失败!")
        sys.exit(1)