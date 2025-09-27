#!/usr/bin/env python3
"""
<<<<<<< HEAD
Linux平台构建脚本

使用PyInstaller构建Linux可执行文件
=======
Linux平台构建脚本 - 适配新架构

自动化执行PyInstaller打包流程
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
"""

import os
import sys
import shutil
import subprocess
<<<<<<< HEAD
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
=======
import platform
from pathlib import Path
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinuxBuilder:
    """Linux平台构建器 - 适配新架构"""
    
    def __init__(self, project_root: str = None):
        """
        初始化构建器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.build_dir = self.project_root / "build" / "linux"
        self.dist_dir = self.project_root / "dist" / "linux"
        self.spec_file = self.build_dir / "hello-scan-code.spec"
        
        # 添加项目路径到Python路径
        sys.path.insert(0, str(self.project_root))
    
    def check_requirements(self) -> bool:
        """
        检查构建要求
        
        Returns:
            bool: 是否满足构建要求
        """
        logger.info("检查构建要求...")
        
        # 检查操作系统
        if platform.system() != "Linux":
            logger.warning("当前不是Linux系统，但仍可尝试构建")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 10):
            logger.error(f"Python版本过低: {python_version}, 需要3.10+")
            return False
        
        # 检查PyInstaller
        try:
            import PyInstaller
            logger.info(f"PyInstaller版本: {PyInstaller.__version__}")
        except ImportError:
            logger.error("PyInstaller未安装，请执行: pip install pyinstaller")
            return False
        
        # 检查项目依赖
        required_packages = ['loguru', 'pandas', 'openpyxl', 'sqlalchemy', 'alembic']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.error("请执行: pip install -r requirements.txt")
            return False
        
        # 检查新架构的配置模块
        try:
            from src.config import ConfigManager, get_config_manager
            from src.packaging import ResourceBundler, get_hidden_imports
            logger.info("新架构模块检查通过")
        except ImportError as e:
            logger.error(f"新架构模块导入失败: {e}")
            return False
        
        # 检查spec文件
        if not self.spec_file.exists():
            logger.error(f"spec文件不存在: {self.spec_file}")
            return False
        
        logger.info("所有构建要求已满足")
        return True
    
    def clean_build(self):
        """清理构建目录"""
        logger.info("清理构建目录...")
        
        clean_dirs = [
            self.dist_dir,
            self.project_root / "build" / "__pycache__",
            self.project_root / "dist" / "__pycache__",
        ]
        
        for dir_path in clean_dirs:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"已清理: {dir_path}")
    
    def install_dependencies(self):
        """安装构建依赖"""
        logger.info("安装构建依赖...")
        
        try:
            # 升级PyInstaller到最新版本
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"
            ], check=True)
            
            logger.info("依赖安装完成")
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败: {e}")
            raise
    
    def prepare_config_template(self):
        """准备配置模板文件"""
        logger.info("准备配置模板文件...")
        
        try:
            from src.config import get_config_manager
            manager = get_config_manager()
            manager.create_config_template()
            logger.info("配置模板准备完成")
        except Exception as e:
            logger.warning(f"配置模板准备失败: {e}")
    
    def build_executable(self) -> bool:
        """
        构建可执行文件
        
        Returns:
            bool: 是否构建成功
        """
        logger.info("开始构建可执行文件...")
        
        try:
            # 切换到项目根目录
            os.chdir(self.project_root)
            
            # 执行PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(self.spec_file)
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("构建成功！")
                logger.info(f"构建输出: {result.stdout}")
                return True
            else:
                logger.error("构建失败！")
                logger.error(f"错误输出: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"构建过程中出现异常: {e}")
            return False
    
    def post_build_tasks(self):
        """构建后任务"""
        logger.info("执行构建后任务...")
        
        # 检查输出目录
        app_dir = self.dist_dir / "hello-scan-code"
        exe_file = app_dir / "hello-scan-code"
        
        if not exe_file.exists():
            logger.error("可执行文件未生成")
            return False
        
        # 设置可执行权限
        exe_file.chmod(0o755)
        logger.info("已设置可执行权限")
        
        # 计算目录大小
        total_size = sum(f.stat().st_size for f in app_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        logger.info(f"应用程序目录大小: {size_mb:.2f} MB")
        
        # 创建并复制配置模板到应用目录
        try:
            from src.config import get_json_loader
            loader = get_json_loader()
            
            # 检查是否存在配置模板
            if loader.template_path and os.path.exists(loader.template_path):
                shutil.copy2(loader.template_path, app_dir / "config.template.json")
                logger.info("已复制配置模板文件到应用目录")
            else:
                # 创建配置模板
                loader.save_config_template()
                if os.path.exists(loader.template_path):
                    shutil.copy2(loader.template_path, app_dir / "config.template.json")
                    logger.info("已创建并复制配置模板文件到应用目录")
        except Exception as e:
            logger.warning(f"配置模板处理失败: {e}")
        
        # 复制README和LICENSE到分发目录根部
        for doc_file in ["README.md", "LICENSE", "PYINSTALLER_GUIDE.md"]:
            src_file = self.project_root / doc_file
            if src_file.exists():
                shutil.copy2(src_file, self.dist_dir / doc_file)
                logger.info(f"已复制: {doc_file}")
        
        # 创建启动脚本
        self.create_launcher_script()
        
        return True
    
    def create_launcher_script(self):
        """创建启动脚本"""
        launcher_content = '''#!/bin/bash
# Hello-Scan-Code 启动脚本 (新架构版本)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/hello-scan-code"
EXECUTABLE="$APP_DIR/hello-scan-code"

# 检查可执行文件是否存在
if [ ! -f "$EXECUTABLE" ]; then
    echo "错误: 可执行文件不存在: $EXECUTABLE"
    exit 1
fi

# 检查配置模板
TEMPLATE_FILE="$APP_DIR/config.template.json"
CONFIG_FILE="$SCRIPT_DIR/config.json"

if [ ! -f "$CONFIG_FILE" ] && [ -f "$TEMPLATE_FILE" ]; then
    echo "提示: 首次运行，已为您复制配置模板文件"
    echo "配置文件位置: $CONFIG_FILE"
    echo "请根据需要修改配置文件，然后重新运行此脚本"
    cp "$TEMPLATE_FILE" "$CONFIG_FILE"
    exit 0
fi

# 切换到脚本目录（确保相对路径正确）
cd "$SCRIPT_DIR"

# 运行应用程序
echo "启动 Hello-Scan-Code (新架构版本)..."
echo "配置文件: $CONFIG_FILE"
"$EXECUTABLE" "$@"
'''
        
        launcher_path = self.dist_dir / "run-hello-scan-code.sh"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # 设置可执行权限
        launcher_path.chmod(0o755)
        logger.info(f"已创建启动脚本: {launcher_path}")
    
    def create_distribution_package(self):
        """创建分发包"""
        logger.info("创建分发包...")
        
        try:
            # 创建版本号
            version = "1.0.0"  # 可以从git或配置文件读取
            
            # 压缩包名称
            package_name = f"hello-scan-code-v{version}-linux"
            package_path = self.project_root / "dist" / f"{package_name}.tar.gz"
            
            # 创建tar.gz压缩包
            shutil.make_archive(
                str(package_path.with_suffix('').with_suffix('')),
                'gztar',
                self.dist_dir.parent,
                'linux'
            )
            
            logger.info(f"分发包已创建: {package_path}")
            
        except Exception as e:
            logger.error(f"创建分发包失败: {e}")
    
    def run_build(self, clean: bool = True, install_deps: bool = False) -> bool:
        """
        运行完整构建流程
        
        Args:
            clean: 是否清理构建目录
            install_deps: 是否安装依赖
            
        Returns:
            bool: 是否构建成功
        """
        logger.info("开始Linux平台构建...")
        
        try:
            # 检查要求
            if not self.check_requirements():
                return False
            
            # 清理构建目录
            if clean:
                self.clean_build()
            
            # 安装依赖
            if install_deps:
                self.install_dependencies()
            
            # 准备配置模板
            self.prepare_config_template()
            
            # 构建可执行文件
            if not self.build_executable():
                return False
            
            # 构建后任务
            if not self.post_build_tasks():
                return False
            
            # 创建分发包
            self.create_distribution_package()
            
            logger.info("Linux构建完成！")
            return True
            
        except Exception as e:
            logger.error(f"构建失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Linux平台构建脚本")
    parser.add_argument("--no-clean", action="store_true", help="不清理构建目录")
    parser.add_argument("--install-deps", action="store_true", help="安装构建依赖")
    parser.add_argument("--project-root", help="项目根目录路径")
    
    args = parser.parse_args()
    
    builder = LinuxBuilder(args.project_root)
    success = builder.run_build(
        clean=not args.no_clean,
        install_deps=args.install_deps
    )
    
    sys.exit(0 if success else 1)
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a


if __name__ == "__main__":
    main()