#!/usr/bin/env python3
"""
新架构配置系统测试脚本

测试新架构的配置加载、JSON配置支持和PyInstaller集成
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试新架构的配置模块
try:
    from src.config import (
        get_config_manager, get_app_config, get_logger_config, 
        get_database_config, create_config_template,
        ConfigManager, AppConfig, LoggerConfig, DatabaseConfig,
        get_json_loader, load_config_from_json
    )
    print("✓ 新架构配置模块导入成功")
except ImportError as e:
    print(f"✗ 新架构配置模块导入失败: {e}")
    sys.exit(1)


def test_config_manager():
    """测试配置管理器"""
    print("\n=== 测试配置管理器 ===")
    
    try:
        # 获取配置管理器
        manager = get_config_manager()
        print("✓ 配置管理器获取成功")
        
        # 测试各个配置获取
        app_config = get_app_config()
        logger_config = get_logger_config()
        db_config = get_database_config()
        
        print(f"✓ 应用配置获取成功: repo_path={app_config.repo_path}")
        print(f"✓ 日志配置获取成功: level={logger_config.level}")
        print(f"✓ 数据库配置获取成功: pool_size={db_config.pool_size}")
        
        # 测试配置验证
        is_valid = manager.validate_all()
        print(f"✓ 配置验证结果: {'通过' if is_valid else '失败'}")
        
        return True
    except Exception as e:
        print(f"✗ 配置管理器测试失败: {e}")
        return False


def test_json_config_loader():
    """测试JSON配置加载器"""
    print("\n=== 测试JSON配置加载器 ===")
    
    try:
        # 创建临时配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 测试配置模板创建
            from src.config.json_config_loader import JsonConfigLoader
            loader = JsonConfigLoader(temp_dir)
            loader.save_config_template()
            
            template_path = temp_path / "config.template.json"
            if template_path.exists():
                print("✓ 配置模板创建成功")
            else:
                print("✗ 配置模板创建失败")
                return False
            
            # 创建自定义配置文件
            custom_config = {
                "repo_path": "/test/path",
                "search_term": "custom,test,terms",
                "is_regex": True,
                "validate": True,
                "validate_workers": 8,
                "output": {
                    "db_path": "custom.db",
                    "excel_path": "custom.xlsx"
                },
                "logging": {
                    "level": "DEBUG"
                },
                "filters": {
                    "ignore_dirs": [".git", "custom_ignore"],
                    "file_extensions": [".py", ".js"]
                }
            }
            
            config_file = temp_path / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(custom_config, f, indent=2)
            
            # 测试配置加载
            json_data = loader.load_json_config()
            if json_data:
                print("✓ JSON配置文件加载成功")
            else:
                print("✗ JSON配置文件加载失败")
                return False
            
            # 测试配置应用
            app_config = AppConfig()
            updated_config = loader.apply_json_to_config(app_config, json_data)
            
            if updated_config.repo_path == "/test/path":
                print("✓ JSON配置应用成功")
            else:
                print("✗ JSON配置应用失败")
                return False
        
        return True
    except Exception as e:
        print(f"✗ JSON配置加载器测试失败: {e}")
        return False


def test_config_integration():
    """测试配置集成"""
    print("\n=== 测试配置集成 ===")
    
    try:
        # 创建临时配置目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建配置文件
            config_data = {
                "repo_path": temp_dir,
                "search_term": "integration,test",
                "is_regex": False,
                "validate": True,
                "validate_workers": 4,
                "output": {
                    "db_path": f"{temp_dir}/test.db",
                    "excel_path": f"{temp_dir}/test.xlsx"
                },
                "logging": {
                    "level": "INFO"
                }
            }
            
            config_file = Path(temp_dir) / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            # 测试从JSON加载配置
            from src.config.json_config_loader import JsonConfigLoader
            loader = JsonConfigLoader(temp_dir)
            
            app_config = AppConfig()
            app_config = load_config_from_json(app_config)
            
            print(f"✓ 集成配置加载成功: search_term={app_config.search_term}")
            
            # 测试配置验证
            if app_config.validate():
                print("✓ 集成配置验证通过")
            else:
                print("✗ 集成配置验证失败")
                return False
        
        return True
    except Exception as e:
        print(f"✗ 配置集成测试失败: {e}")
        return False


def test_packaging_modules():
    """测试打包模块"""
    print("\n=== 测试打包模块 ===")
    
    try:
        # 测试PyInstaller钩子
        from src.packaging import (
            get_hidden_imports, get_data_files, get_exclude_modules,
            ResourceBundler, bundle_resources
        )
        
        # 测试隐藏导入
        hidden_imports = get_hidden_imports()
        if 'src.config' in hidden_imports:
            print("✓ 隐藏导入包含新架构配置模块")
        else:
            print("✗ 隐藏导入缺少新架构配置模块")
            return False
        
        # 测试数据文件
        data_files = get_data_files()
        print(f"✓ 数据文件收集: {len(data_files)} 个文件")
        
        # 测试资源打包器
        bundler = ResourceBundler()
        resources = bundler.collect_all_resources()
        print(f"✓ 资源文件收集: {len(resources)} 个资源")
        
        # 验证资源
        validation = bundler.validate_resources()
        if validation['is_valid']:
            print("✓ 资源文件验证通过")
        else:
            print(f"⚠ 资源文件验证: {validation['missing_files']} 个缺失文件")
        
        return True
    except Exception as e:
        print(f"✗ 打包模块测试失败: {e}")
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")
    
    try:
        # 测试原有的parse_args函数
        from src.config import parse_args, SearchConfig
        
        config = parse_args()
        if isinstance(config, (AppConfig, SearchConfig)):
            print("✓ parse_args向后兼容性测试通过")
        else:
            print("✗ parse_args向后兼容性测试失败")
            return False
        
        # 测试SearchConfig别名
        search_config = SearchConfig()
        if hasattr(search_config, 'repo_path'):
            print("✓ SearchConfig别名兼容性测试通过")
        else:
            print("✗ SearchConfig别名兼容性测试失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 向后兼容性测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 创建无效的JSON文件
            invalid_json_file = temp_path / "config.json"
            with open(invalid_json_file, 'w') as f:
                f.write("{ invalid json content }")
            
            from src.config.json_config_loader import JsonConfigLoader
            loader = JsonConfigLoader(temp_dir)
            
            # 应该返回None而不是抛出异常
            json_data = loader.load_json_config()
            if json_data is None:
                print("✓ 无效JSON处理正确")
            else:
                print("✗ 无效JSON处理错误")
                return False
            
            # 测试不存在配置文件的情况
            os.remove(invalid_json_file)
            json_data = loader.load_json_config()
            if json_data is None:
                print("✓ 不存在配置文件处理正确")
            else:
                print("✗ 不存在配置文件处理错误")
                return False
        
        return True
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        return False


def main():
    """主函数"""
    print("开始新架构配置系统测试\n")
    
    tests = [
        ("配置管理器测试", test_config_manager),
        ("JSON配置加载器测试", test_json_config_loader),
        ("配置集成测试", test_config_integration),
        ("打包模块测试", test_packaging_modules),
        ("向后兼容性测试", test_backward_compatibility),
        ("错误处理测试", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"{test_name} 执行失败: {e}")
    
    print(f"\n=== 测试总结 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！新架构配置系统运行正常。")
        return True
    else:
        print(f"\n❌ {total-passed}个测试失败，请检查并修复问题。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)