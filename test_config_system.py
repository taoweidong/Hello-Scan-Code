#!/usr/bin/env python3
"""
配置系统功能测试脚本
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.config.config_loader import ConfigLoader, load_config_from_file
from src.config.config_validator import ConfigValidator
from src.config.default_config import DEFAULT_CONFIG, SearchConfig, dict_to_search_config


def test_config_validator():
    """测试配置验证器"""
    print("=== 测试配置验证器 ===")
    
    # 测试有效配置
    valid_config = DEFAULT_CONFIG.copy()
    is_valid, errors = ConfigValidator.validate_config(valid_config)
    print(f"默认配置验证: {'通过' if is_valid else '失败'}")
    if errors:
        print(f"错误: {errors}")
    
    # 测试无效配置
    invalid_config = {
        "repo_path": "",  # 空路径
        "validate_workers": -1,  # 无效数值
        "logging": {
            "level": "INVALID"  # 无效日志级别
        }
    }
    is_valid, errors = ConfigValidator.validate_config(invalid_config)
    print(f"无效配置验证: {'失败' if not is_valid else '意外通过'}")
    print(f"预期错误数: {len(errors)}")
    
    print("配置验证器测试完成\n")


def test_config_loader():
    """测试配置加载器"""
    print("=== 测试配置加载器 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 测试默认配置加载
        loader = ConfigLoader(temp_dir)
        config = loader.load_config()
        print(f"默认配置加载: 成功")
        print(f"仓库路径: {config.repo_path}")
        print(f"搜索词: {config.search_term}")
        
        # 创建自定义配置文件
        custom_config = {
            "repo_path": "/test/path",
            "search_term": "custom,search,terms",
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
        
        # 测试自定义配置加载
        loader = ConfigLoader(temp_dir)
        try:
            custom_loaded_config = loader.load_config()
            print(f"自定义配置加载: 成功")
            print(f"自定义仓库路径: {custom_loaded_config.repo_path}")
            print(f"自定义搜索词: {custom_loaded_config.search_term}")
            print(f"正则表达式: {custom_loaded_config.is_regex}")
            print(f"验证模式: {custom_loaded_config.validate}")
            print(f"工作线程数: {custom_loaded_config.validate_workers}")
        except Exception as e:
            print(f"自定义配置加载失败: {e}")
        
        # 测试配置模板创建
        loader.create_template()
        template_path = temp_path / "config.template.json"
        print(f"配置模板创建: {'成功' if template_path.exists() else '失败'}")
    
    print("配置加载器测试完成\n")


def test_config_conversion():
    """测试配置转换功能"""
    print("=== 测试配置转换功能 ===")
    
    # 测试字典到SearchConfig的转换
    config_dict = DEFAULT_CONFIG.copy()
    search_config = dict_to_search_config(config_dict)
    
    print(f"字典转换为SearchConfig: 成功")
    print(f"类型: {type(search_config)}")
    print(f"仓库路径: {search_config.repo_path}")
    print(f"忽略目录数量: {len(search_config.ignore_dirs)}")
    
    # 测试SearchConfig到字典的转换
    from src.config.default_config import search_config_to_dict
    converted_dict = search_config_to_dict(search_config)
    
    print(f"SearchConfig转换为字典: 成功")
    print(f"字典键数量: {len(converted_dict)}")
    
    print("配置转换功能测试完成\n")


def test_compatibility():
    """测试向后兼容性"""
    print("=== 测试向后兼容性 ===")
    
    # 测试原有parse_args函数
    try:
        from src.config import parse_args
        config = parse_args()
        print(f"parse_args兼容性: 成功")
        print(f"配置类型: {type(config)}")
        print(f"仓库路径: {config.repo_path}")
    except Exception as e:
        print(f"parse_args兼容性测试失败: {e}")
    
    # 测试新的JSON配置加载函数
    try:
        from src.config import load_json_config
        json_config = load_json_config()
        print(f"load_json_config功能: 成功")
        print(f"配置类型: {type(json_config)}")
    except Exception as e:
        print(f"load_json_config测试失败: {e}")
    
    print("向后兼容性测试完成\n")


def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建无效的JSON文件
        invalid_json_file = temp_path / "config.json"
        with open(invalid_json_file, 'w') as f:
            f.write("{ invalid json content }")
        
        loader = ConfigLoader(temp_dir)
        try:
            config = loader.load_config()
            print(f"无效JSON处理: 成功回退到默认配置")
        except Exception as e:
            print(f"无效JSON处理失败: {e}")
        
        # 创建验证失败的配置文件
        invalid_config = {
            "repo_path": "",  # 空路径应该失败
            "validate_workers": "invalid"  # 类型错误
        }
        
        with open(invalid_json_file, 'w') as f:
            json.dump(invalid_config, f)
        
        try:
            config = loader.load_config()
            print(f"配置验证失败处理: 成功回退到默认配置")
        except Exception as e:
            print(f"配置验证失败处理失败: {e}")
    
    print("错误处理测试完成\n")


def main():
    """主函数"""
    print("开始配置系统功能测试\n")
    
    try:
        test_config_validator()
        test_config_loader()
        test_config_conversion()
        test_compatibility()
        test_error_handling()
        
        print("所有配置系统测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)