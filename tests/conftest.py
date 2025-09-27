"""
pytest配置文件

提供测试运行的全局配置和夹具
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """项目根目录路径"""
    return project_root


@pytest.fixture(scope="function")
def temp_directory():
    """临时目录夹具"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def temp_db_path():
    """临时数据库路径"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    yield temp_path
    
    # 清理
    try:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    except:
        pass


@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置环境变量，跳过数据库迁移
    os.environ['SKIP_MIGRATION'] = '1'
    
    # 设置测试日志级别
    original_log_level = os.environ.get('LOG_LEVEL')
    os.environ['LOG_LEVEL'] = 'ERROR'  # 减少测试时的日志输出
    
    yield
    
    # 恢复环境变量
    if original_log_level:
        os.environ['LOG_LEVEL'] = original_log_level
    else:
        os.environ.pop('LOG_LEVEL', None)
    
    os.environ.pop('SKIP_MIGRATION', None)


@pytest.fixture(scope="function")
def sample_code_file():
    """示例代码文件夹具"""
    content = '''
def test_function():
    """测试函数"""
    print("Hello World")
    return "test_result"

class TestClass:
    def __init__(self):
        self.test_var = "test_value"
    
    def test_method(self):
        return self.test_var
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    # 清理
    try:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    except:
        pass


@pytest.fixture(scope="function")
def sample_search_data():
    """示例搜索结果数据"""
    return [
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
                    'content': '    return "test_result"',
                    'search_term': 'test'
                }
            ]
        },
        {
            'file_path': '/test/file2.py',
            'matches': [
                {
                    'line_number': '5',
                    'content': 'class TestClass:',
                    'search_term': 'test'
                }
            ]
        }
    ]