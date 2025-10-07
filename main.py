#!/usr/bin/env python3
"""
Hello-Scan-Code 顶层入口
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    # 导入并运行主程序
    from src.main import main
    # 调用click命令
    main()