#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件基础接口测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.plugin.base import IScanPlugin


class TestPluginBase(unittest.TestCase):
    """插件基础接口测试类"""

    def test_plugin_interface_import(self):
        """测试插件接口导入"""
        # IScanPlugin是抽象基类，不能直接实例化
        # 这里只是测试导入是否成功
        self.assertTrue(IScanPlugin.__name__, "IScanPlugin")


if __name__ == '__main__':
    unittest.main()