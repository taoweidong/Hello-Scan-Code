#!/usr/bin/env python3
"""
Linux平台构建脚本

使用PyInstaller构建Linux可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 直接导入模块
import src.packaging
from loguru import logger


def main():
    """主构建函数"""
    logger.info("开始Linux平台构建")
    
    # 获取打包辅助工具
    helper = src.packaging.PackagingHelper(str(project_root))
    
    # 准备构建环境
    if not helper.prepare_build_environment():
        logger.error("构建环境准备失败")
        sys.exit(1)
    
    # 创建spec文件
    spec_file = helper.create_spec_file(platform="linux", onefile=False)
    
    # 执行PyInstaller构建
    try:
        logger.info("执行PyInstaller构建...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            spec_file
        ]
        
        result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"PyInstaller构建失败: {result.stderr}")
            sys.exit(1)
        
        logger.info("PyInstaller构建完成")
        
    except Exception as e:
        logger.error(f"构建过程中发生错误: {e}")
        sys.exit(1)
    
    # 处理构建产物
    dist_dir = project_root / "dist"
    app_dir = dist_dir / "hello-scan-code"
    
    if not app_dir.exists():
        logger.error("未找到构建的应用目录")
        sys.exit(1)
    
    # 创建发布目录
    release_dir = project_root / "dist" / "hello-scan-code-v1.0.0-linux"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    # 复制应用目录
    shutil.copytree(app_dir, release_dir / "hello-scan-code")
    
    # 设置可执行权限
    exe_file = release_dir / "hello-scan-code" / "hello-scan-code"
    if exe_file.exists():
        exe_file.chmod(0o755)
    
    # 复制资源文件
    helper.copy_resources_to_dist(str(release_dir))
    
    # 创建打包信息
    helper.create_package_info(str(release_dir), "linux")
    
    # 创建启动脚本
    create_startup_script(release_dir)
    
    # 创建使用说明
    create_usage_instructions(release_dir)
    
    logger.info(f"Linux构建完成，输出目录: {release_dir}")


def create_startup_script(release_dir: Path):
    """创建启动脚本"""
    script_content = """#!/bin/bash
# Hello-Scan-Code 启动脚本

cd "$(dirname "$0")"
./hello-scan-code/hello-scan-code "$@"
"""
    
    script_file = release_dir / "run.sh"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置可执行权限
    script_file.chmod(0o755)


def create_usage_instructions(release_dir: Path):
    """创建使用说明文件"""
    usage_content = """# Hello-Scan-Code 使用说明 (Linux)

## 快速开始

1. 复制 `config.template.json` 为 `config.json`
2. 修改 `config.json` 中的配置参数：
   - `repo_path`: 设置要搜索的代码仓库路径
   - `search_term`: 设置搜索关键词
   - 其他配置根据需要调整
3. 运行 `./run.sh` 或 `./hello-scan-code/hello-scan-code`
4. 查看生成的结果文件

## 运行方式

方式一：使用启动脚本
```bash
./run.sh
```

方式二：直接运行
```bash
./hello-scan-code/hello-scan-code
```

## 配置文件说明

配置文件使用JSON格式，支持以下主要配置项：

- `repo_path`: 搜索目标路径
- `search_term`: 搜索关键词（逗号分隔多个关键词）
- `is_regex`: 是否使用正则表达式搜索
- `validate`: 是否启用结果验证
- `output`: 输出配置（数据库和Excel文件路径）
- `filters`: 过滤器配置（忽略目录、文件类型等）

## 输出文件

- 数据库文件: `db/results.db` (SQLite格式)
- Excel报告: `report/results.xlsx`

## 依赖要求

本程序已打包所有必要依赖，可以在大多数Linux系统上直接运行。
如果遇到问题，请确保系统已安装基础的C库。

更多详细信息请参考 README.md 文件。
"""
    
    with open(release_dir / "USAGE.md", 'w', encoding='utf-8') as f:
        f.write(usage_content)


if __name__ == "__main__":
    main()