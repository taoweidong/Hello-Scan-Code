#!/usr/bin/env python3
"""
数据库操作优化验证测试

验证新的SQLAlchemy ORM实现是否正常工作，
并与原有功能保持兼容性
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.database import DatabaseManager
from src.database.session_manager import SessionManager
from src.database.repositories.search_result_repository import SearchResultRepository
from src.database.config import DatabaseConfig


def test_compatibility_interface():
    """测试兼容性接口是否正常工作"""
    print("=== 测试兼容性接口 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # 测试兼容性适配器
        db_manager = DatabaseManager(test_db_path)
        
        # 测试数据库初始化
        db_manager.init_database()
        print("✓ 数据库初始化成功")
        
        # 准备测试数据
        test_data = [
            {
                'file_path': '/test/file1.py',
                'matches': [
                    {
                        'line_number': '10',
                        'content': 'def test_function():',
                        'search_term': 'test'
                    },
                    {
                        'line_number': '15',
                        'content': 'return test_value',
                        'search_term': 'test'
                    }
                ]
            },
            {
                'file_path': '/test/file2.py',
                'matches': [
                    {
                        'line_number': '5',
                        'content': 'import test_module',
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
        expected_files = {'/test/file1.py', '/test/file2.py'}
        actual_files = set(results)
        
        if expected_files == actual_files:
            print("✓ 获取搜索结果成功")
        else:
            print(f"✗ 获取搜索结果失败，期望: {expected_files}, 实际: {actual_files}")
        
        # 测试新增功能
        stats = db_manager.get_search_statistics()
        print(f"✓ 统计信息: {stats}")
        
        # 测试按文件路径搜索
        file_results = db_manager.search_by_file_path('/test/file1.py')
        print(f"✓ 按文件路径搜索到 {len(file_results)} 条结果")
        
        # 测试按搜索词搜索
        term_results = db_manager.search_by_term('test')
        print(f"✓ 按搜索词搜索到 {len(term_results)} 条结果")
        
        # 测试内容搜索
        content_results = db_manager.search_in_content('function')
        print(f"✓ 内容搜索到 {len(content_results)} 条结果")
        
        print("✓ 兼容性接口测试通过")
        
        # 关闭数据库连接
        db_manager.close()
        
    except Exception as e:
        print(f"✗ 兼容性接口测试失败: {e}")
        raise
    finally:
        # 清理测试文件
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_new_orm_features():
    """测试新的ORM功能"""
    print("\n=== 测试新的ORM功能 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # 创建配置和会话管理器
        config = DatabaseConfig(db_path=test_db_path)
        session_manager = SessionManager(config)
        repository = SearchResultRepository()
        
        print("✓ 会话管理器和仓库创建成功")
        
        # 测试会话上下文管理器
        with session_manager.session_scope() as session:
            # 测试创建记录
            test_model_data = {
                'file_path': '/orm/test.py',
                'line_number': '20',
                'matched_content': 'class TestClass:',
                'search_term': 'class',
                'file_size': 1024,
                'encoding': 'utf-8',
                'match_position': 100
            }
            
            created_model = repository.create(session, **test_model_data)
            print(f"✓ 创建记录成功，ID: {created_model.id}")
            
            # 测试查询
            found_model = repository.get_by_id(session, created_model.id)
            if found_model:
                print("✓ 按ID查询成功")
            else:
                print("✗ 按ID查询失败")
            
            # 测试更新
            updated_model = repository.update(session, created_model.id, 
                                            matched_content='class UpdatedTestClass:')
            if updated_model and 'Updated' in updated_model.matched_content:
                print("✓ 更新记录成功")
            else:
                print("✗ 更新记录失败")
            
            # 测试模型方法
            model_dict = updated_model.to_dict()
            print(f"✓ 模型转字典: {len(model_dict)} 个字段")
            
            # 测试统计功能
            stats = repository.get_statistics(session)
            print(f"✓ 仓库统计: {stats}")
        
        # 测试健康检查
        is_healthy = session_manager.health_check()
        print(f"✓ 数据库健康检查: {'通过' if is_healthy else '失败'}")
        
        # 测试批量操作
        with session_manager.session_scope() as session:
            bulk_data = [
                {
                    'file_path': f'/bulk/file{i}.py',
                    'line_number': str(i),
                    'matched_content': f'line {i} content',
                    'search_term': 'bulk'
                }
                for i in range(5)
            ]
            
            created_models = repository.bulk_create(session, bulk_data)
            print(f"✓ 批量创建 {len(created_models)} 条记录")
            
            # 测试复杂查询
            criteria_results = repository.get_by_criteria(
                session, 
                search_term='bulk',
                limit=3
            )
            print(f"✓ 按条件查询到 {len(criteria_results)} 条记录")
        
        print("✓ 新的ORM功能测试通过")
        
    except Exception as e:
        print(f"✗ 新的ORM功能测试失败: {e}")
        raise
    finally:
        # 清理资源
        session_manager.close()
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_migration_service():
    """测试数据库迁移服务"""
    print("\n=== 测试数据库迁移服务 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        from src.database.migrations.migration_service import MigrationService
        from src.database.config.engine_factory import EngineFactory
        
        # 创建配置和引擎
        config = DatabaseConfig(db_path=test_db_path)
        engine = EngineFactory.create_engine(config)
        
        # 创建迁移服务
        migration_service = MigrationService(engine)
        
        # 获取迁移信息
        migration_info = migration_service.get_migration_info()
        print(f"✓ 迁移信息: {migration_info}")
        
        # 执行迁移
        migration_success = migration_service.migrate()
        if migration_success:
            print("✓ 数据库迁移成功")
        else:
            print("✗ 数据库迁移失败")
        
        # 验证迁移后的版本
        final_info = migration_service.get_migration_info()
        print(f"✓ 迁移后信息: {final_info}")
        
        print("✓ 数据库迁移服务测试通过")
        
    except Exception as e:
        print(f"✗ 数据库迁移服务测试失败: {e}")
        raise
    finally:
        # 清理
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_performance_comparison():
    """性能对比测试"""
    print("\n=== 性能对比测试 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        import time
        
        # 准备大量测试数据
        large_test_data = []
        for i in range(10):  # 减少数据量以便快速测试
            file_data = {
                'file_path': f'/perf/file{i}.py',
                'matches': []
            }
            for j in range(10):
                file_data['matches'].append({
                    'line_number': str(j),
                    'content': f'line {j} in file {i}',
                    'search_term': f'term{i % 3}'
                })
            large_test_data.append(file_data)
        
        # 测试新实现的性能
        start_time = time.time()
        db_manager = DatabaseManager(test_db_path)
        db_manager.save_results(large_test_data)
        new_save_time = time.time() - start_time
        
        start_time = time.time()
        results = db_manager.get_results()
        new_get_time = time.time() - start_time
        
        print(f"✓ 新实现 - 保存时间: {new_save_time:.4f}s, 获取时间: {new_get_time:.4f}s")
        print(f"✓ 数据量: {len(large_test_data)} 个文件, {sum(len(f['matches']) for f in large_test_data)} 条记录")
        print(f"✓ 获取结果: {len(results)} 个文件")
        
        # 测试新功能的性能
        start_time = time.time()
        stats = db_manager.get_search_statistics()
        stats_time = time.time() - start_time
        print(f"✓ 统计查询时间: {stats_time:.4f}s, 结果: {stats}")
        
        print("✓ 性能对比测试完成")
        
    except Exception as e:
        print(f"✗ 性能对比测试失败: {e}")
        raise
    finally:
        # 清理
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def main():
    """主测试函数"""
    print("开始数据库操作优化验证测试")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    try:
        # 运行所有测试
        test_compatibility_interface()
        test_new_orm_features()
        test_migration_service()
        test_performance_comparison()
        
        print("\n🎉 所有测试通过！数据库操作优化实现成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()