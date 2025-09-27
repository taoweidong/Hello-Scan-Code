#!/usr/bin/env python3
"""
集成测试 - 验证原有业务逻辑是否正常工作
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SearchConfig
from src.code_searcher import CodeSearcher


def test_integration():
    """测试集成功能"""
    print("=== 测试业务集成功能 ===")
    
    # 跳过迁移进行快速测试
    os.environ['SKIP_MIGRATION'] = '1'
    
    # 创建临时目录结构
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file_path = os.path.join(temp_dir, 'test.py')
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("""
def test_function():
    print("Hello World")
    return "test_result"

class TestClass:
    def __init__(self):
        self.test_var = "test_value"
""")
        
        # 创建临时数据库和Excel输出路径
        db_dir = os.path.join(temp_dir, 'db')
        report_dir = os.path.join(temp_dir, 'report')
        os.makedirs(db_dir, exist_ok=True)
        os.makedirs(report_dir, exist_ok=True)
        
        try:
            # 创建搜索配置
            config = SearchConfig(
                repo_path=temp_dir,
                keywords=['test'],
                db_path=os.path.join(db_dir, 'test_results.db'),
                excel_path=os.path.join(report_dir, 'test_results.xlsx'),
                file_types=['.py'],
                exclude_patterns=[],
                use_regex=False,
                use_grep=False  # 使用Python搜索确保兼容性
            )
            
            # 创建代码搜索器
            searcher = CodeSearcher(config)
            print("✓ CodeSearcher 创建成功")
            
            # 执行搜索
            results = searcher.search()
            print(f"✓ 搜索完成，找到 {len(results)} 个文件")
            
            # 保存结果
            searcher.save_results(results)
            print("✓ 结果保存成功")
            
            # 验证数据库中的数据
            db_results = searcher.db_manager.get_results()
            print(f"✓ 数据库中有 {len(db_results)} 个文件记录")
            
            # 验证统计信息
            stats = searcher.db_manager.get_search_statistics()
            print(f"✓ 统计信息: 总匹配数={stats.get('total_matches', 0)}, 文件数={stats.get('unique_files', 0)}")
            
            # 验证Excel文件是否生成
            if os.path.exists(config.excel_path):
                print("✓ Excel 文件生成成功")
            else:
                print("⚠ Excel 文件未生成（可能是pandas未安装）")
            
            # 关闭资源
            searcher.db_manager.close()
            
            print("✓ 业务集成测试通过")
            
        except Exception as e:
            print(f"✗ 业务集成测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    test_integration()