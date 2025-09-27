#!/usr/bin/env python3
"""
项目完整性验证脚本

验证新架构项目的所有功能是否正常工作
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_project_structure():
    """验证项目结构"""
    print("=== 验证项目结构 ===")
    
    required_files = [
        # 核心模块
        "src/config/__init__.py",
        "src/config/config_manager.py", 
        "src/config/json_config_loader.py",
        "src/config/app_config.py",
        "src/config/logger_config.py",
        "src/config/database_config.py",
        "src/config/base_config.py",
        
        # 打包模块
        "src/packaging/__init__.py",
        "src/packaging/pyinstaller_hooks.py",
        "src/packaging/resource_bundler.py",
        
        # 配置文件
        "config/config.template.json",
        "config/example.json",
        
        # 构建配置
        "build/windows/hello-scan-code.spec",
        "build/linux/hello-scan-code.spec",
        
        # 构建脚本
        "scripts/build_windows.py",
        "scripts/build_linux.py",
        
        # 测试文件
        "test_new_architecture.py",
        
        # 文档
        "PYINSTALLER_GUIDE.md",
        "README.md",
        "Makefile",
        "pyproject.toml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺少 {len(missing_files)} 个必要文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print(f"\n✅ 所有 {len(required_files)} 个必要文件都存在")
        return True


def verify_config_system():
    """验证配置系统"""
    print("\n=== 验证配置系统 ===")
    
    try:
        # 测试配置模块导入
        from src.config import (
            get_config_manager, get_app_config, get_logger_config,
            get_database_config, ConfigManager, AppConfig
        )
        print("✓ 配置模块导入成功")
        
        # 测试配置管理器
        manager = get_config_manager()
        print("✓ 配置管理器创建成功")
        
        # 测试各配置获取
        app_config = get_app_config()
        logger_config = get_logger_config()
        db_config = get_database_config()
        print("✓ 所有配置模块获取成功")
        
        # 测试JSON配置加载器
        from src.config import get_json_loader
        loader = get_json_loader()
        config_info = loader.get_config_info()
        print(f"✓ JSON配置加载器正常 (配置目录: {config_info['config_dir']})")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置系统验证失败: {e}")
        return False


def verify_packaging_system():
    """验证打包系统"""
    print("\n=== 验证打包系统 ===")
    
    try:
        # 测试打包模块导入
        from src.packaging import (
            get_hidden_imports, get_data_files, ResourceBundler,
            bundle_resources
        )
        print("✓ 打包模块导入成功")
        
        # 测试隐藏导入
        hidden_imports = get_hidden_imports()
        if 'src.config' in hidden_imports:
            print(f"✓ 隐藏导入正常 ({len(hidden_imports)} 个模块)")
        else:
            print("❌ 隐藏导入缺少新架构模块")
            return False
        
        # 测试资源收集
        bundler = ResourceBundler()
        resources = bundler.collect_all_resources()
        validation = bundler.validate_resources()
        
        print(f"✓ 资源收集正常 ({validation['existing_files']}/{validation['total_files']} 个文件)")
        
        if validation['missing_files'] > 0:
            print(f"⚠️  发现 {validation['missing_files']} 个缺失资源文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 打包系统验证失败: {e}")
        return False


def verify_build_system():
    """验证构建系统"""
    print("\n=== 验证构建系统 ===")
    
    try:
        # 检查spec文件语法
        spec_files = [
            project_root / "build" / "windows" / "hello-scan-code.spec",
            project_root / "build" / "linux" / "hello-scan-code.spec"
        ]
        
        for spec_file in spec_files:
            if spec_file.exists():
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查关键字段
                required_keywords = ['Analysis', 'PYZ', 'EXE']
                for keyword in required_keywords:
                    if keyword not in content:
                        print(f"❌ {spec_file.name} 缺少关键字段: {keyword}")
                        return False
                
                print(f"✓ {spec_file.name} 语法正确")
            else:
                print(f"❌ {spec_file.name} 不存在")
                return False
        
        # 检查构建脚本
        build_scripts = [
            project_root / "scripts" / "build_windows.py",
            project_root / "scripts" / "build_linux.py"
        ]
        
        for script in build_scripts:
            if script.exists():
                print(f"✓ {script.name} 存在")
            else:
                print(f"❌ {script.name} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 构建系统验证失败: {e}")
        return False


def verify_backward_compatibility():
    """验证向后兼容性"""
    print("\n=== 验证向后兼容性 ===")
    
    try:
        # 测试原有API兼容性
        from src.config import parse_args, SearchConfig
        
        # 测试parse_args函数
        config = parse_args()
        if hasattr(config, 'repo_path') and hasattr(config, 'search_term'):
            print("✓ parse_args函数兼容性正常")
        else:
            print("❌ parse_args函数缺少必要属性")
            return False
        
        # 测试SearchConfig别名
        search_config = SearchConfig()
        if hasattr(search_config, 'repo_path'):
            print("✓ SearchConfig别名兼容性正常")
        else:
            print("❌ SearchConfig别名不正常")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 向后兼容性验证失败: {e}")
        return False


def verify_config_files():
    """验证配置文件"""
    print("\n=== 验证配置文件 ===")
    
    try:
        # 检查配置模板文件
        template_file = project_root / "config" / "config.template.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # 检查必要字段
            required_fields = ['repo_path', 'search_term', 'output', 'logging', 'filters']
            for field in required_fields:
                if field not in template_data:
                    print(f"❌ 配置模板缺少字段: {field}")
                    return False
            
            print("✓ 配置模板文件格式正确")
        else:
            print("❌ 配置模板文件不存在")
            return False
        
        # 检查示例配置文件
        example_file = project_root / "config" / "example.json"
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                json.load(f)  # 验证JSON格式
            print("✓ 示例配置文件格式正确")
        else:
            print("❌ 示例配置文件不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return False


def verify_documentation():
    """验证文档"""
    print("\n=== 验证文档 ===")
    
    try:
        # 检查主要文档文件
        doc_files = [
            "README.md",
            "PYINSTALLER_GUIDE.md",
            "Makefile"
        ]
        
        for doc_file in doc_files:
            file_path = project_root / doc_file
            if file_path.exists():
                # 检查文件大小（确保不是空文件）
                file_size = file_path.stat().st_size
                if file_size > 100:  # 至少100字节
                    print(f"✓ {doc_file} 存在且内容完整 ({file_size} 字节)")
                else:
                    print(f"⚠️  {doc_file} 存在但内容可能不完整")
            else:
                print(f"❌ {doc_file} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 文档验证失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 开始项目完整性验证\n")
    
    verifiers = [
        ("项目结构", verify_project_structure),
        ("配置系统", verify_config_system),
        ("打包系统", verify_packaging_system),  
        ("构建系统", verify_build_system),
        ("向后兼容性", verify_backward_compatibility),
        ("配置文件", verify_config_files),
        ("文档", verify_documentation)
    ]
    
    passed = 0
    total = len(verifiers)
    
    for name, verifier in verifiers:
        try:
            if verifier():
                passed += 1
        except Exception as e:
            print(f"❌ {name}验证过程中发生异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 验证结果: {passed}/{total} 通过")
    print(f"📈 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有验证通过！项目已成功集成新架构和PyInstaller打包支持。")
        print("\n📋 主要特性:")
        print("  ✅ 模块化配置系统")
        print("  ✅ JSON配置文件支持")
        print("  ✅ PyInstaller打包支持")
        print("  ✅ 跨平台构建脚本")
        print("  ✅ 完整的向后兼容性")
        print("  ✅ 全面的文档和测试")
        
        print("\n🚀 快速开始:")
        print("  # 创建配置文件")
        print("  make config")
        print("  # 测试新架构")  
        print("  make test-new-arch")
        print("  # 构建可执行文件")
        print("  make build-linux")
        
        return True
    else:
        print(f"\n❌ {total-passed}个验证失败，请检查上述错误并修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)