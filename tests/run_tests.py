#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行入口文件
运行所有单元测试并生成覆盖率报告
"""

import os
import sys
import subprocess
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    try:
        # 使用coverage运行测试并生成覆盖率报告
        cmd = [
            sys.executable, "-m", "coverage", "run",
            "--source=src",
            "-m", "unittest", "discover",
            "-s", "tests/unit",
            "-p", "test_*.py",
            "-v"
        ]
        
        print("运行测试并生成覆盖率报告...")
        print("命令:", " ".join(cmd))
        
        result = subprocess.run(cmd, cwd=os.path.join(os.path.dirname(__file__), '..'))
        
        if result.returncode == 0:
            # 生成覆盖率报告
            print("\n生成覆盖率报告...")
            
            # 生成终端报告
            subprocess.run([
                sys.executable, "-m", "coverage", "report",
                "--show-missing"
            ], cwd=os.path.join(os.path.dirname(__file__), '..'))
            
            # 生成HTML报告
            subprocess.run([
                sys.executable, "-m", "coverage", "html",
                "-d", "report/coverage_html"
            ], cwd=os.path.join(os.path.dirname(__file__), '..'))
            
            # 生成XML报告
            subprocess.run([
                sys.executable, "-m", "coverage", "xml",
                "-o", "report/coverage.xml"
            ], cwd=os.path.join(os.path.dirname(__file__), '..'))
            
            return True
        else:
            return False
        
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


def run_tests_simple():
    """简单运行测试（不生成覆盖率报告）"""
    try:
        # 使用unittest发现并运行所有测试
        cmd = [
            sys.executable, "-m", "unittest", "discover",
            "-s", "tests/unit",
            "-p", "test_*.py",
            "-v"
        ]
        
        print("运行所有单元测试...")
        print("命令:", " ".join(cmd))
        
        result = subprocess.run(cmd, cwd=os.path.join(os.path.dirname(__file__), '..'))
        return result.returncode == 0
        
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行单元测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--html', action='store_true', help='生成HTML格式的覆盖率报告')
    
    args = parser.parse_args()
    
    print("Hello-Scan-Code 单元测试")
    print("=" * 50)
    
    if args.coverage:
        success = run_tests_with_coverage()
    else:
        success = run_tests_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 部分测试失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())