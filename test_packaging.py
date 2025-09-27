#!/usr/bin/env python3
"""
PyInstaller打包功能测试脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import importlib.util


def check_python_version():
    """检查Python版本"""
    print("=== 检查Python环境 ===")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 10):
        print("警告: Python版本过低，建议使用3.10+")
        return False
    else:
        print("Python版本检查: 通过")
        return True


def check_dependencies():
    """检查项目依赖"""
    print("\n=== 检查项目依赖 ===")
    
    required_packages = {
        'loguru': 'loguru',
        'pandas': 'pandas', 
        'openpyxl': 'openpyxl',
        'sqlalchemy': 'sqlalchemy',
        'alembic': 'alembic'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"✓ {package_name}: 已安装")
            else:
                print(f"✗ {package_name}: 未找到")
                missing_packages.append(package_name)
        except ImportError:
            print(f"✗ {package_name}: 导入失败")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请安装缺少的依赖包")
        return False
    else:
        print("\n所有依赖包检查: 通过")
        return True


def check_pyinstaller():
    """检查PyInstaller"""
    print("\n=== 检查PyInstaller ===")
    
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
        
        # 检查PyInstaller命令行工具
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("PyInstaller命令行工具: 可用")
            return True
        else:
            print("PyInstaller命令行工具: 不可用")
            return False
    except ImportError:
        print("PyInstaller: 未安装")
        print("请执行: pip install pyinstaller")
        return False


def test_project_structure():
    """测试项目结构"""
    print("\n=== 检查项目结构 ===")
    
    project_root = Path(__file__).parent
    
    required_files = [
        "src/main.py",
        "src/config/__init__.py",
        "src/config/config_loader.py",
        "src/config/config_validator.py", 
        "src/config/default_config.py",
        "src/packaging/__init__.py",
        "src/packaging/pyinstaller_hooks.py",
        "src/packaging/resource_bundler.py",
        "config/config.template.json",
        "config/default.json",
        "build/windows/hello-scan-code.spec",
        "build/linux/hello-scan-code.spec",
        "scripts/build_windows.py",
        "scripts/build_linux.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺少文件: {len(missing_files)}个")
        return False
    else:
        print("\n项目结构检查: 通过")
        return True


def test_import_modules():
    """测试模块导入"""
    print("\n=== 测试模块导入 ===")
    
    test_modules = [
        "src.config.default_config",
        "src.config.config_loader",
        "src.config.config_validator",
        "src.packaging.pyinstaller_hooks",
        "src.packaging.resource_bundler"
    ]
    
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    failed_imports = []
    
    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n导入失败: {len(failed_imports)}个模块")
        return False
    else:
        print("\n模块导入测试: 通过")
        return True


def test_resource_bundler():
    """测试资源打包器"""
    print("\n=== 测试资源打包器 ===")
    
    try:
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from src.packaging.resource_bundler import ResourceBundler
        
        bundler = ResourceBundler(str(project_root))
        
        # 测试资源收集
        config_files = bundler.collect_config_files()
        print(f"配置文件: {len(config_files)}个")
        
        all_resources = bundler.collect_all_resources()
        print(f"总资源文件: {len(all_resources)}个")
        
        # 测试资源验证
        validation = bundler.validate_resources()
        print(f"资源验证: {'通过' if validation['is_valid'] else '失败'}")
        if not validation['is_valid']:
            print(f"缺失文件: {validation['missing_files']}")
        
        return validation['is_valid']
        
    except Exception as e:
        print(f"资源打包器测试失败: {e}")
        return False


def test_pyinstaller_hooks():
    """测试PyInstaller钩子"""
    print("\n=== 测试PyInstaller钩子 ===")
    
    try:
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from src.packaging.pyinstaller_hooks import (
            get_hidden_imports, get_analysis_options, 
            get_exe_options, get_data_files
        )
        
        hidden_imports = get_hidden_imports()
        print(f"隐藏导入模块: {len(hidden_imports)}个")
        
        analysis_options = get_analysis_options()
        print(f"Analysis选项: {len(analysis_options)}个配置项")
        
        exe_options = get_exe_options()
        print(f"EXE选项: {len(exe_options)}个配置项")
        
        data_files = get_data_files()
        print(f"数据文件: {len(data_files)}个")
        
        print("PyInstaller钩子测试: 通过")
        return True
        
    except Exception as e:
        print(f"PyInstaller钩子测试失败: {e}")
        return False


def test_spec_files():
    """测试spec文件语法"""
    print("\n=== 测试spec文件语法 ===")
    
    project_root = Path(__file__).parent
    spec_files = [
        project_root / "build" / "windows" / "hello-scan-code.spec",
        project_root / "build" / "linux" / "hello-scan-code.spec"
    ]
    
    for spec_file in spec_files:
        if spec_file.exists():
            try:
                # 简单语法检查
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查关键字段
                required_keywords = ['Analysis', 'PYZ', 'EXE']
                missing_keywords = []
                
                for keyword in required_keywords:
                    if keyword not in content:
                        missing_keywords.append(keyword)
                
                if missing_keywords:
                    print(f"✗ {spec_file.name}: 缺少关键字段 {missing_keywords}")
                    return False
                else:
                    print(f"✓ {spec_file.name}: 语法检查通过")
            except Exception as e:
                print(f"✗ {spec_file.name}: 读取失败 {e}")
                return False
        else:
            print(f"✗ {spec_file.name}: 文件不存在")
            return False
    
    print("spec文件测试: 通过")
    return True


def main():
    """主函数"""
    print("开始PyInstaller打包功能测试\n")
    
    tests = [
        ("Python版本检查", check_python_version),
        ("依赖包检查", check_dependencies),
        ("PyInstaller检查", check_pyinstaller),
        ("项目结构检查", test_project_structure),
        ("模块导入测试", test_import_modules),
        ("资源打包器测试", test_resource_bundler),
        ("PyInstaller钩子测试", test_pyinstaller_hooks),
        ("spec文件测试", test_spec_files)
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
        print("\n所有测试通过！PyInstaller打包准备就绪。")
        return True
    else:
        print(f"\n{total-passed}个测试失败，请检查并修复问题。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)