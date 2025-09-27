#!/usr/bin/env python3
"""
基础功能测试

测试数据库操作优化的核心功能
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager


def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # 简单测试，跳过迁移
        os.environ['SKIP_MIGRATION'] = '1'
        
        # 测试兼容性适配器
        db_manager = DatabaseManager(test_db_path)
        
        # 准备测试数据
        test_data = [
            {
                'file_path': '/test/file1.py',
                'matches': [
                    {
                        'line_number': '10',
                        'content': 'def test_function():',
                        'search_term': 'test'
                    }
                ]
            }
        ]
        
        # 测试保存结果
        db_manager.save_results(test_data)
        print("✓ 保存搜索结果成功")
        
        # 测试获取结果
        results = db_manager.get_results()
        print(f"✓ 获取到 {len(results)} 个文件路径")
        
        # 关闭数据库连接
        db_manager.close()
        print("✓ 基础功能测试通过")
        
    except Exception as e:
        print(f"✗ 基础功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
        except:
            pass


if __name__ == '__main__':
    test_basic_functionality()